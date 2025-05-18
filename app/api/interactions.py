# app/api/interactions.py
import logging
from flask import Blueprint, Response, request, jsonify, g
from app.utils.decorators import jwt_required_with_permissions
from app.services.interaction_service import InteractionService
from app.services.prompt_service import PromptService
from app.utils.pagination import get_pagination_params
from app.utils.auth_client import AuthClient
from app.models.feedback import Feedback  # Import Feedback model
from app.models.interaction import Interaction  # Import Interaction model
from app.models.prompt import Prompt  # Import Prompt model
from app import db  # Import the database object

logger = logging.getLogger(__name__)

interactions_bp = Blueprint('interactions', __name__, url_prefix='/interactions')

@interactions_bp.route('', methods=['POST'])
@jwt_required_with_permissions()  # No specific permissions required
def create_interaction():
    """Create a new interaction with an AI model."""
    user_id = str(g.current_user_id)  # Ensure user_id is a string
    data = request.get_json()
    
    # Validate required fields
    if not data.get('model_id') or not data.get('model_version'):
        return jsonify({'error': 'model_id and model_version are required'}), 400
    
    # Create interaction
    interaction = InteractionService.create_interaction(
        user_id=user_id,
        model_id=data.get('model_id'),
        model_version=data.get('model_version'),
        endpoint_name=data.get('endpoint_name'),
        metadata=data.get('metadata', {})
    )
    
    if isinstance(interaction, dict) and 'error' in interaction:
        return jsonify({'error': interaction['error']}), 400
    
    return jsonify(interaction.to_dict()), 201

@interactions_bp.route('/<uuid:interaction_id>', methods=['GET'])
@jwt_required_with_permissions(['admin'])  # Admin permission to view any interaction
def get_interaction(interaction_id):
    """Get details of a specific interaction."""
    user_id = str(g.current_user_id)  # Ensure user_id is a string
    
    interaction = InteractionService.get_interaction(interaction_id)
    if not interaction:
        return jsonify({'error': 'Interaction not found'}), 404
    
    # Check if user owns this interaction or has admin permission
    if interaction.user_id != user_id and not g.user_permissions.get('admin'):
        return jsonify({'error': 'Not authorized to access this interaction'}), 403
    
    return jsonify(interaction.to_dict()), 200

@interactions_bp.route('', methods=['GET'])
@jwt_required_with_permissions()  # No specific permissions required
def list_interactions():
    """Get a list of interactions for the current user."""
    user_id = str(g.current_user_id)  # Ensure user_id is a string
    
    # Parse query parameters
    page, per_page = get_pagination_params(request)
    status = request.args.get('status')
    model_id = request.args.get('model_id')
    
    interactions, total = InteractionService.get_user_interactions(
        user_id=user_id,
        page=page,
        per_page=per_page,
        status=status,
        model_id=model_id
    )
    
    return jsonify({
        'interactions': [i.to_dict() for i in interactions],
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

@interactions_bp.route('/<uuid:interaction_id>', methods=['PUT'])
@jwt_required_with_permissions()  # No specific permissions required
def update_interaction(interaction_id):
    """Update an interaction (end or change status)."""
    user_id = str(g.current_user_id)  # Ensure user_id is a string
    data = request.get_json()
    
    interaction = InteractionService.get_interaction(interaction_id)
    if not interaction:
        return jsonify({'error': 'Interaction not found'}), 404
    
    # Check if user owns this interaction
    if interaction.user_id != user_id:
        return jsonify({'error': 'Not authorized to update this interaction'}), 403
    
    # Update interaction (currently only supports ending)
    if data.get('status') in ('COMPLETED', 'ABANDONED'):
        updated_interaction = InteractionService.end_interaction(
            interaction_id=interaction_id,
            status=data.get('status')
        )
        return jsonify(updated_interaction.to_dict()), 200
    else:
        return jsonify({'error': 'Invalid status. Use COMPLETED or ABANDONED'}), 400

@interactions_bp.route('/interactions/<interaction_id>/prompts', methods=['POST'])
def submit_prompt(interaction_id):
    interaction = Interaction.query.get(interaction_id)
    if not interaction:
        return {"error": "Interaction not found"}, 404

    # Check if feedback is required for the last response
    last_response = Response.query.filter_by(prompt_id=interaction.prompts[-1].id).first()
    if last_response and not last_response.feedback_provided:
        return {"error": "Feedback required for the last response"}, 400

    # Create a new prompt
    data = request.json
    new_prompt = Prompt(
        interaction_id=interaction_id,
        content=data['content'],
        sequence_number=len(interaction.prompts) + 1
    )
    db.session.add(new_prompt)
    db.session.commit()

    # Generate a response
    new_response = Response(
        prompt_id=new_prompt.id,
        content="Generated response here",
        model_endpoint="default-model"
    )
    db.session.add(new_response)
    db.session.commit()

    # Update conversation history
    interaction.conversation_history.append({
        "prompt": new_prompt.content,
        "response": new_response.content
    })
    db.session.commit()

    return {"prompt": new_prompt.to_dict(), "response": new_response.to_dict()}, 201



@interactions_bp.route('/<uuid:interaction_id>/chat', methods=['POST'])
@jwt_required_with_permissions()  # No specific permissions required
def submit_chat_message(interaction_id):
    """Submit a chat message using the OpenAI-compatible chat format."""
    user_id = str(g.current_user_id)  # Ensure user_id is a string
    data = request.get_json()
    
    if not data.get('message'):
        return jsonify({'error': 'message is required'}), 400
    
    # Get interaction
    interaction = InteractionService.get_interaction(interaction_id)
    if not interaction:
        return jsonify({'error': 'Interaction not found'}), 404
    
    # Check if user owns this interaction
    if interaction.user_id != user_id:
        return jsonify({'error': 'Not authorized to access this interaction'}), 403
    
    # Submit chat message and get response
    prompt, response = PromptService.submit_chat_message(
        interaction_id=interaction_id,
        message=data.get('message'),
        system_prompt=data.get('system_prompt')
    )
    
    if isinstance(prompt, dict) and 'error' in prompt:
        return jsonify({'error': prompt['error']}), 400
    
    result = {
        'prompt': prompt.to_dict(),
        'response': response.to_dict() if response else None
    }
    
    return jsonify(result), 201

@interactions_bp.route('/<uuid:interaction_id>/history', methods=['GET'])
@jwt_required_with_permissions(['admin'])  # Admin permission to view any interaction history
def get_interaction_history(interaction_id):
    """Get conversation history for an interaction."""
    user_id = str(g.current_user_id)  # Ensure user_id is a string
    
    # Get interaction
    interaction = InteractionService.get_interaction(interaction_id)
    if not interaction:
        return jsonify({'error': 'Interaction not found'}), 404
    
    # Check if user owns this interaction or has admin permission
    if interaction.user_id != user_id and not g.user_permissions.get('admin'):
        return jsonify({'error': 'Not authorized to access this interaction'}), 403
    
    history = PromptService.get_interaction_history(interaction_id)
    
    return jsonify({
        'interaction_id': str(interaction_id),
        'history': history
    }), 200



@interactions_bp.route('/responses/<response_id>/feedback', methods=['POST'])
def provide_feedback(response_id):
    response = Response.query.get(response_id)
    if not response:
        return {"error": "Response not found"}, 404

    # Create feedback
    data = request.json
    new_feedback = Feedback(
        response_id=response_id,
        rating=data['rating'],
        comments=data.get('comments', '')
    )
    db.session.add(new_feedback)

    # Mark feedback as provided
    response.feedback_provided = True
    db.session.commit()

    return {"feedback": new_feedback.to_dict()}, 201