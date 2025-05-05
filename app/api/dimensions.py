# app/api/dimensions.py
import logging
from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import get_jwt_identity
from app.services.dimension_service import DimensionService
from app.utils.auth_client import AuthClient, has_permission
from app.utils.decorators import jwt_required_with_permissions

logger = logging.getLogger(__name__)

dimensions_bp = Blueprint('dimensions', __name__, url_prefix='/dimensions')

@dimensions_bp.route('', methods=['POST'])
@jwt_required_with_permissions(['admin'])
def create_dimension():
    """Create a new evaluation dimension."""
    user_id = g.current_user_id
    
    # Check if user has admin permission
    if not has_permission(user_id, 'admin'):
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
        created_by=user_id,
        scale_type=data.get('scale_type', 'numeric'),
        scale_options=data.get('scale_options'),
        evaluation_method=data.get('evaluation_method', 'rating'),
        ui_component=data.get('ui_component'),
        help_text=data.get('help_text'),
        placeholder=data.get('placeholder'),
        scale_labels=data.get('scale_labels'),
        weight=data.get('weight', 1.0),  # Default weight is 1.0
        is_required=data.get('is_required', False),  # Default is not required
        validation_rules=data.get('validation_rules') 
    )
    db.session.add(dimension)
    db.session.commit()
    
    
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
    data = request.get_json()
    dimension = EvaluationDimension.query.get(dimension_id)

    if not dimension:
        return jsonify({'error': 'Dimension not found'}), 404

    dimension.name = data.get('name', dimension.name)
    dimension.description = data.get('description', dimension.description)
    dimension.scale_type = data.get('scale_type', dimension.scale_type)
    dimension.scale_options = data.get('scale_options', dimension.scale_options)
    dimension.evaluation_method = data.get('evaluation_method', dimension.evaluation_method)
    dimension.ui_component = data.get('ui_component', dimension.ui_component)
    dimension.help_text = data.get('help_text', dimension.help_text)
    dimension.placeholder = data.get('placeholder', dimension.placeholder)
    dimension.scale_labels = data.get('scale_labels', dimension.scale_labels)
    dimension.weight = data.get('weight', dimension.weight)
    dimension.is_required = data.get('is_required', dimension.is_required)
    dimension.validation_rules = data.get('validation_rules', dimension.validation_rules)

    db.session.commit()

    return jsonify(dimension.to_dict()), 200
# def update_dimension(dimension_id):
#     """Update an evaluation dimension."""
#     user_id = g.current_user_id
    
#     # Check if user has admin permission
#     if not has_permission(user_id, 'admin'):
#         return jsonify({'error': 'Not authorized to update dimensions'}), 403
    
#     data = request.get_json()
    
#     dimension = DimensionService.update_dimension(
#         dimension_id=dimension_id,
#         name=data.get('name'),
#         description=data.get('description'),
#         is_active=data.get('is_active')
#     )
    
#     if isinstance(dimension, dict) and 'error' in dimension:
#         return jsonify({'error': dimension['error']}), 400
    
#     return jsonify(dimension.to_dict()), 200



from flask import Blueprint, request, jsonify
from app.models.dimension import EvaluationDimension
from app import db

dimensions_bp = Blueprint('dimensions', __name__, url_prefix='/dimensions')

@dimensions_bp.route('', methods=['POST'])
def create_dimension():
    """Create a new evaluation dimension."""
    data = request.get_json()

    dimension = EvaluationDimension(
        name=data['name'],
        description=data.get('description'),
        scale_type=data.get('scale_type', 'numeric'),
        scale_options=data.get('scale_options'),
        evaluation_method=data.get('evaluation_method', 'rating'),
        ui_component=data.get('ui_component'),
        help_text=data.get('help_text'),
        placeholder=data.get('placeholder'),
        scale_labels=data.get('scale_labels')
    )
    db.session.add(dimension)
    db.session.commit()

    return jsonify(dimension.to_dict()), 201

@dimensions_bp.route('', methods=['GET'])
def get_dimensions():
    """Get all evaluation dimensions."""
    dimensions = EvaluationDimension.query.all()
    return jsonify([dimension.to_dict() for dimension in dimensions]),
