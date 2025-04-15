# app/api/interactions.py
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.interaction_service import InteractionService
from app.utils.decorators import jwt_required_with_permissions
from app.utils.auth_client import is_admin, has_permission
from uuid import UUID

interactions_bp = Blueprint('interactions', __name__)

@interactions_bp.route('', methods=['POST'])
@jwt_required()
def create_interaction():
    """Create a new interaction with an AI model."""
    user_id = UUID(get_jwt_identity())
    data = request.get_json()
    
    # Validate required fields
    if not data.get('model_id') or not data.get('model_version'):
        return jsonify({'success': False, 'message': 'model_id and model_version are required'}), 400
    
    # Create interaction
    interaction = InteractionService.create_interaction(
        user_id=user_id,
        model_id=data.get('model_id'),
        model_version=data.get('model_version'),
        tags=data.get('tags', []),
        metadata=data.get('metadata', {})
    )
    
    return jsonify({'success': True, 'interaction': interaction.to_dict()}), 201

@interactions_bp.route('/<uuid:interaction_id>', methods=['GET'])
@jwt_required()
def get_interaction(interaction_id):
    """Get interaction details."""
    user_id = UUID(get_jwt_identity())
    
    interaction = InteractionService.get_interaction(interaction_id)
    if not interaction:
        return jsonify({'success': False, 'message': 'Interaction not found'}), 404
    
    # Check authorization
    if interaction.user_id != user_id and not is_admin(user_id):
        if not has_permission(user_id, 'interaction:view_any'):
            return jsonify({'success': False, 'message': 'Not authorized to view this interaction'}), 403
    
    return jsonify({'success': True, 'interaction': interaction.to_dict()}), 200

@interactions_bp.route('/user/<uuid:user_id>', methods=['GET'])
@jwt_required()
def get_user_interactions(user_id):
    """Get interactions for a specific user."""
    current_user_id = UUID(get_jwt_identity())
    
    # Check authorization
    if user_id != current_user_id and not is_admin(current_user_id):
        if not has_permission(current_user_id, 'interaction:view_any'):
            return jsonify({'success': False, 'message': 'Not authorized to view interactions for this user'}), 403
    
    # Parse pagination parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 10)), 50)
    status = request.args.get('status')
    model_id = request.args.get('model_id')
    
    interactions, total = InteractionService.get_user_interactions(
        user_id, page, per_page, status=status, model_id=model_id
    )
    
    return jsonify({
        'success': True,
        'interactions': [interaction.to_dict() for interaction in interactions],
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    }), 200

@interactions_bp.route('/<uuid:interaction_id>/end', methods=['PUT'])
@jwt_required()
def end_interaction(interaction_id):
    """End an active interaction."""
    user_id = UUID(get_jwt_identity())
    data = request.get_json()
    status = data.get('status', 'COMPLETED')
    
    if status not in ['COMPLETED', 'ABANDONED']:
        return jsonify({'success': False, 'message': 'Status must be COMPLETED or ABANDONED'}), 400
    
    interaction = InteractionService.get_interaction(interaction_id)
    if not interaction:
        return jsonify({'success': False, 'message': 'Interaction not found'}), 404
    
    # Check authorization
    if interaction.user_id != user_id and not is_admin(user_id):
        return jsonify({'success': False, 'message': 'Not authorized to end this interaction'}), 403
    
    updated_interaction = InteractionService.end_interaction(interaction_id, status)
    
    return jsonify({'success': True, 'interaction': updated_interaction.to_dict()}), 200

@interactions_bp.route('/<uuid:interaction_id>/history', methods=['GET'])
@jwt_required()
def get_interaction_history(interaction_id):
    """Get all prompts and responses for an interaction."""
    user_id = UUID(get_jwt_identity())
    
    interaction = InteractionService.get_interaction(interaction_id)
    if not interaction:
        return jsonify({'success': False, 'message': 'Interaction not found'}), 404
    
    # Check authorization
    if interaction.user_id != user_id and not is_admin(user_id):
        if not has_permission(user_id, 'interaction:view_any'):
            return jsonify({'success': False, 'message': 'Not authorized to view this interaction history'}), 403
    
    history = InteractionService.get_interaction_history(interaction_id)
    
    return jsonify({
        'success': True,
        'interaction_id': str(interaction_id),
        'history': history
    }), 200

@interactions_bp.route('/search', methods=['GET'])
@jwt_required()
def search_interactions():
    """Search for interactions based on criteria."""
    user_id = UUID(get_jwt_identity())
    
    # Parse search parameters
    query = request.args.get('q', '')
    model_id = request.args.get('model_id')
    status = request.args.get('status')
    tags = request.args.getlist('tag')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 10)), 50)
    
    # Check if user can search all interactions
    search_all = is_admin(user_id) or has_permission(user_id, 'interaction:view_any')
    
    interactions, total = InteractionService.search_interactions(
        user_id=user_id if not search_all else None,
        query=query,
        model_id=model_id,
        status=status,
        tags=tags,
        start_date=start_date,
        end_date=end_date,
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'success': True,
        'interactions': [interaction.to_dict() for interaction in interactions],
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    }), 200