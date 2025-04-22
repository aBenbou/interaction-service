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

logger = logging.getLogger(__name__)

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

@feedback_bp.route('', methods=['POST'])
@jwt_required_with_permissions()
def create_feedback():
    """Submit feedback for a model response."""
    user_id = str(g.current_user_id)
    data = request.get_json()
    
    # Validate required fields
    if not data.get('response_id') or not data.get('dimension_ratings'):
        return jsonify({'error': 'response_id and dimension_ratings are required'}), 400
    
    # Validate dimension ratings format
    for rating in data.get('dimension_ratings', []):
        if 'dimension_id' not in rating or 'score' not in rating:
            return jsonify({'error': 'Each dimension rating must include dimension_id and score'}), 400
    
    feedback = FeedbackService.create_feedback(
        response_id=data.get('response_id'),
        user_id=user_id,
        dimension_ratings=data.get('dimension_ratings'),
        overall_comment=data.get('overall_comment')
    )
    
    if isinstance(feedback, dict) and 'error' in feedback:
        return jsonify({'error': feedback['error']}), 400
    
    return jsonify(feedback.to_dict()), 201

@feedback_bp.route('/<uuid:feedback_id>', methods=['GET'])
@jwt_required_with_permissions()
def get_feedback(feedback_id):
    """Get details of a specific feedback entry."""
    user_id = str(g.current_user_id)
    
    feedback = FeedbackService.get_feedback(feedback_id)
    if not feedback:
        return jsonify({'error': 'Feedback not found'}), 404
    
    # Check authorization
    is_owner = feedback.user_id == user_id
    is_validator = has_role(user_id, 'validator')
    is_admin_user = has_permission(user_id, 'admin')
    
    if not (is_owner or is_validator or is_admin_user):
        return jsonify({'error': 'Not authorized to view this feedback'}), 403
    
    return jsonify(feedback.to_dict()), 200

@feedback_bp.route('/user', methods=['GET'])
@jwt_required_with_permissions()
def get_user_feedback():
    """Get feedback submitted by the current user."""
    user_id = str(g.current_user_id)
    
    # Parse pagination and filter parameters
    page, per_page = get_pagination_params(request)
    status = request.args.get('status')
    
    feedback_list, total = FeedbackService.get_user_feedback(
        user_id=user_id,
        page=page,
        per_page=per_page,
        status=status
    )
    
    return jsonify({
        'feedback': [f.to_dict() for f in feedback_list],
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

@feedback_bp.route('/pending', methods=['GET'])
@jwt_required_with_permissions(['validator:read'])
def get_pending_feedback():
    """Get pending feedback awaiting validation."""
    user_id = str(g.current_user_id)
    
    # Check if user is a validator
    if not has_role(user_id, 'validator'):
        return jsonify({'error': 'Not authorized to view pending feedback'}), 403
    
    # Parse pagination parameters
    page, per_page = get_pagination_params(request)
    model_id = request.args.get('model_id')
    
    feedback_list, total = FeedbackService.get_pending_feedback(
        page=page, 
        per_page=per_page,
        model_id=model_id
    )
    
    return jsonify({
        'feedback': [f.to_dict() for f in feedback_list],
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

@feedback_bp.route('/response/<uuid:response_id>', methods=['GET'])
@jwt_required_with_permissions()
def get_response_feedback(response_id):
    """Get all feedback for a specific response."""
    user_id = str(g.current_user_id)
    
    # Parse pagination parameters
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