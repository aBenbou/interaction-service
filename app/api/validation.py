# app/api/validation.py
import logging
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import get_jwt_identity
from app.services.validation_service import ValidationService
from app.utils.user_client import UserClient, has_role
from app.utils.decorators import jwt_required_with_permissions

logger = logging.getLogger(__name__)

validation_bp = Blueprint('validation', __name__, url_prefix='/validation')

@validation_bp.route('/feedback/<uuid:feedback_id>', methods=['POST'])
@jwt_required_with_permissions(['validator:write'])
def validate_feedback(feedback_id):
    """Validate a feedback submission."""
    validator_id = str(g.current_user_id)
    
    # Check if user is a validator
    if not has_role(validator_id, 'validator'):
        return jsonify({'error': 'Not authorized to validate feedback'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    if 'is_valid' not in data:
        return jsonify({'error': 'is_valid field is required'}), 400
    
    validation = ValidationService.validate_feedback(
        feedback_id=feedback_id,
        validator_id=validator_id,
        is_valid=data.get('is_valid'),
        notes=data.get('notes')
    )
    
    if isinstance(validation, dict) and 'error' in validation:
        return jsonify({'error': validation['error']}), 400
    
    return jsonify(validation.to_dict()), 201

@validation_bp.route('/stats', methods=['GET'])
@jwt_required_with_permissions(['validator:read'])
def get_validation_stats():
    """Get validation statistics for current user."""
    validator_id = str(g.current_user_id)
    
    # Check if user is a validator
    if not has_role(validator_id, 'validator'):
        return jsonify({'error': 'Not authorized to view validation stats'}), 403
    
    stats = ValidationService.get_validator_stats(validator_id)
    
    return jsonify(stats), 200