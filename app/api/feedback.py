# app/api/feedback.py
import logging
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import get_jwt_identity
from app.services.feedback_service import FeedbackService
from app.services.dimension_service import DimensionService
from app.utils.pagination import get_pagination_params
from app.utils.auth_client import AuthClient, is_admin, has_permission
from app.utils.user_client import UserClient, has_role
from app.utils.decorators import jwt_required_with_permissions
from datetime import datetime

logger = logging.getLogger(__name__)

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

@feedback_bp.route('', methods=['POST'])
@jwt_required_with_permissions(['feedback:write'])
def submit_feedback():
    """Submit feedback for a model response."""
    user_id = str(g.current_user_id)
    data = request.get_json()
    
    required_fields = ['interaction_id', 'prompt_id', 'category']
    if not all(field in data for field in required_fields):
        return jsonify({
            'success': False,
            'message': f'Missing required fields: {", ".join(required_fields)}'
        }), 400
    
    result = FeedbackService.submit_feedback(
        interaction_id=data['interaction_id'],
        prompt_id=data['prompt_id'],
        user_id=user_id,
        category=data['category'],
        rating=data.get('rating'),
        binary_evaluation=data.get('binary_evaluation'),
        ranking=data.get('ranking'),
        justification=data.get('justification'),
        metadata=data.get('metadata')
    )
    
    if result['success']:
        return jsonify(result), 201
    else:
        return jsonify(result), 400

@feedback_bp.route('/<uuid:feedback_id>', methods=['GET'])
@jwt_required_with_permissions(['feedback:read'])
def get_feedback(feedback_id):
    """Get feedback by ID."""
    result = FeedbackService.get_feedback(feedback_id)
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 404

@feedback_bp.route('/user', methods=['GET'])
@jwt_required_with_permissions(['feedback:read'])
def get_user_feedback():
    """Get feedback submitted by the current user."""
    user_id = str(g.current_user_id)
    
    page, per_page = get_pagination_params(request)
    status = request.args.get('status')
    category = request.args.get('category')
    
    result = FeedbackService.get_user_feedback(
        user_id=user_id,
        status=status,
        category=category,
        page=page,
        per_page=per_page
    )
    
    return jsonify(result), 200

@feedback_bp.route('/pending', methods=['GET'])
@jwt_required_with_permissions(['validation:read'])
def get_pending_validation():
    """Get feedback pending validation."""
    page, per_page = get_pagination_params(request)
    
    result = FeedbackService.get_pending_validation(
        page=page,
        per_page=per_page
    )
    
    return jsonify(result), 200

@feedback_bp.route('/<uuid:feedback_id>/validate', methods=['POST'])
@jwt_required_with_permissions(['validation:write'])
def validate_feedback(feedback_id):
    """Validate submitted feedback."""
    user_id = str(g.current_user_id)
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({
            'success': False,
            'message': 'Status is required'
        }), 400
    
    result = FeedbackService.validate_feedback(
        feedback_id=feedback_id,
        validator_id=user_id,
        status=data['status'],
        notes=data.get('notes')
    )
    
    if result['success']:
        return jsonify(result), 200
    else:
        return jsonify(result), 400

@feedback_bp.route('/response/<uuid:response_id>', methods=['GET'])
@jwt_required_with_permissions()
def get_response_feedback(response_id):
    """Get all feedback for a specific response."""
    user_id = str(g.current_user_id)
    
    page, per_page = get_pagination_params(request)
    
    feedback_list, total = FeedbackService.get_response_feedback(
        response_id=response_id,
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'feedback': [f.to_dict() for f in feedback_list],
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200