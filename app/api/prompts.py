# app/api/prompts.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.interaction_service import InteractionService
from app.services.prompt_service import PromptService
from app.utils.auth_client import is_admin
from uuid import UUID

prompts_bp = Blueprint('prompts', __name__)

@prompts_bp.route('/interactions/<uuid:interaction_id>/prompts', methods=['POST'])
@jwt_required()
def submit_prompt(interaction_id):
    """Submit a new prompt to an AI model."""
    user_id = UUID(get_jwt_identity())
    data = request.get_json()
    
    # Validate required fields
    if not data.get('content'):
        return jsonify({'success': False, 'message': 'Prompt content is required'}), 400
    
    interaction = InteractionService.get_interaction(interaction_id)
    if not interaction:
        return jsonify({'success': False, 'message': 'Interaction not found'}), 404
    
    # Check authorization
    if interaction.user_id != user_id and not is_admin(user_id):
        return jsonify({'success': False, 'message': 'Not authorized to submit prompts to this interaction'}), 403
    
    # Check if interaction is active
    if interaction.status != 'ACTIVE':
        return jsonify({'success': False, 'message': 'Cannot submit prompts to a completed or abandoned interaction'}), 400
    
    # Submit prompt and get response
    prompt, response = PromptService.submit_prompt(
        interaction_id=interaction_id,
        content=data.get('content'),
        context=data.get('context', {}),
        client_metadata=data.get('client_metadata', {})
    )
    
    if not prompt:
        return jsonify({'success': False, 'message': 'Error submitting prompt'}), 500
    
    result = {
        'success': True,
        'prompt': prompt.to_dict(),
        'response': response.to_dict() if response else None
    }
    
    return jsonify(result), 201

@prompts_bp.route('/interactions/<uuid:interaction_id>/prompts/<uuid:prompt_id>', methods=['GET'])
@jwt_required()
def get_prompt(interaction_id, prompt_id):
    """Get a specific prompt and its response."""
    user_id = UUID(get_jwt_identity())
    
    from app.models.prompt import Prompt
    
    # Get the prompt
    prompt = Prompt.query.filter_by(id=prompt_id, interaction_id=interaction_id).first()
    if not prompt:
        return jsonify({'success': False, 'message': 'Prompt not found'}), 404
    
    # Check authorization
    interaction = InteractionService.get_interaction(interaction_id)
    if interaction.user_id != user_id and not is_admin(user_id):
        return jsonify({'success': False, 'message': 'Not authorized to view this prompt'}), 403
    
    result = {
        'success': True,
        'prompt': prompt.to_dict(),
        'response': prompt.response.to_dict() if prompt.response else None
    }
    
    return jsonify(result), 200