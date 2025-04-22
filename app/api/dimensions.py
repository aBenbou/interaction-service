# app/api/dimensions.py
import logging
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import get_jwt_identity
from app.services.dimension_service import DimensionService
from app.utils.auth_client import AuthClient
from app.utils.decorators import jwt_required_with_permissions

logger = logging.getLogger(__name__)

dimensions_bp = Blueprint('dimensions', __name__, url_prefix='/dimensions')

@dimensions_bp.route('', methods=['POST'])
@jwt_required_with_permissions(['admin'])
def create_dimension():
    """Create a new evaluation dimension."""
    user_id = g.current_user_id
    
    # Check if user has admin permission
    if not AuthClient.has_permission(user_id, 'admin'):
        return jsonify({'error': 'Not authorized to create dimensions'}), 403
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['model_id', 'name', 'description']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400
    
    dimension = DimensionService.create_dimension(
        model_id=data.get('model_id'),
        name=data.get('name'),
        description=data.get('description'),
        created_by=user_id
    )
    
    if isinstance(dimension, dict) and 'error' in dimension:
        return jsonify({'error': dimension['error']}), 400
    
    return jsonify(dimension.to_dict()), 201

@dimensions_bp.route('/model/<string:model_id>', methods=['GET'])
@jwt_required_with_permissions()
def get_model_dimensions(model_id):
    """Get all dimensions for a specific model."""
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    dimensions = DimensionService.get_model_dimensions(model_id, active_only)
    
    return jsonify({
        'dimensions': [d.to_dict() for d in dimensions]
    }), 200

@dimensions_bp.route('/<uuid:dimension_id>', methods=['PUT'])
@jwt_required_with_permissions(['admin'])
def update_dimension(dimension_id):
    """Update an evaluation dimension."""
    user_id = g.current_user_id
    
    # Check if user has admin permission
    if not AuthClient.has_permission(user_id, 'admin'):
        return jsonify({'error': 'Not authorized to update dimensions'}), 403
    
    data = request.get_json()
    
    dimension = DimensionService.update_dimension(
        dimension_id=dimension_id,
        name=data.get('name'),
        description=data.get('description'),
        is_active=data.get('is_active')
    )
    
    if isinstance(dimension, dict) and 'error' in dimension:
        return jsonify({'error': dimension['error']}), 400
    
    return jsonify(dimension.to_dict()), 200


