# app/api/dataset.py
import logging
from flask import Blueprint, request, jsonify, make_response, g
from flask_jwt_extended import get_jwt_identity
from app.services.dataset_service import DatasetService
from app.utils.pagination import get_pagination_params
from app.utils.auth_client import AuthClient, has_permission
from app.utils.decorators import jwt_required_with_permissions

logger = logging.getLogger(__name__)

dataset_bp = Blueprint('dataset', __name__, url_prefix='/dataset')

@dataset_bp.route('/model/<string:model_id>', methods=['GET'])
@jwt_required_with_permissions(['admin'])
def get_model_dataset(model_id):
    """Get dataset entries for a model."""
    user_id = g.current_user_id
    
    # Check if user has admin permission
    if not has_permission(user_id, 'admin'):
        return jsonify({'error': 'Not authorized to view dataset entries'}), 403
    
    # Parse pagination parameters
    page, per_page = get_pagination_params(request)
    
    entries, total = DatasetService.get_model_dataset(model_id, page, per_page)
    
    return jsonify({
        'entries': [e.to_dict() for e in entries],
        'total': total,
        'page': page,
        'per_page': per_page
    }), 200

@dataset_bp.route('/model/<string:model_id>/export', methods=['GET'])
@jwt_required_with_permissions(['admin'])
def export_dataset(model_id):
    """Export dataset for a model."""
    user_id = g.current_user_id
    
    # Check if user has admin permission
    if not has_permission(user_id, 'admin'):
        return jsonify({'error': 'Not authorized to export dataset'}), 403
    
    format = request.args.get('format', 'json')
    if format not in ['json', 'csv']:
        return jsonify({'error': 'Unsupported format. Use "json" or "csv"'}), 400
    
    result = DatasetService.export_dataset(model_id, format)
    
    if isinstance(result, dict) and 'error' in result:
        return jsonify({'error': result['error']}), 400
    
    # Set appropriate content type and filename
    content_type = 'application/json' if format == 'json' else 'text/csv'
    filename = f'dataset_{model_id}.{format}'
    
    response = make_response(result)
    response.headers['Content-Type'] = content_type
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    
    return response

@dataset_bp.route('/entry/<uuid:entry_id>', methods=['GET'])
@jwt_required_with_permissions(['admin'])
def get_dataset_entry(entry_id):
    """Get a specific dataset entry."""
    user_id = g.current_user_id
    
    # Check if user has admin permission
    if not has_permission(user_id, 'admin'):
        return jsonify({'error': 'Not authorized to view dataset entries'}), 403
    
    entry = DatasetService.get_entry(entry_id)
    if not entry:
        return jsonify({'error': 'Dataset entry not found'}), 404
    
    return jsonify(entry.to_dict()), 200

@dataset_bp.route('/stats', methods=['GET'])
@jwt_required_with_permissions(['admin'])
def get_dataset_stats():
    """Get statistics about the dataset."""
    user_id = g.current_user_id
    
    # Check if user has admin permission
    if not has_permission(user_id, 'admin'):
        return jsonify({'error': 'Not authorized to view dataset statistics'}), 403
    
    stats = DatasetService.get_stats()
    
    return jsonify(stats), 200

# Additional method for DatasetService
def get_entry(entry_id):
    """
    Get a specific dataset entry by ID.
    
    Args:
        entry_id: ID of the dataset entry
        
    Returns:
        Dataset entry or None if not found
    """
    from app.models.dataset import DatasetEntry
    return DatasetEntry.query.get(entry_id)

# Additional method for DatasetService
def get_stats():
    """
    Get statistics about the dataset.
    
    Returns:
        Dictionary with dataset statistics
    """
    from app.models.dataset import DatasetEntry
    from sqlalchemy import func
    from app import db
    
    # Total entries
    total_entries = DatasetEntry.query.count()
    
    # Entries by model
    model_counts = db.session.query(
        DatasetEntry.model_id, 
        func.count(DatasetEntry.id)
    ).group_by(DatasetEntry.model_id).all()
    
    # Recent entries
    recent_entries = DatasetEntry.query.order_by(
        DatasetEntry.created_at.desc()
    ).limit(5).all()
    
    return {
        'total_entries': total_entries,
        'by_model': {model: count for model, count in model_counts},
        'recent_entries': [e.to_dict() for e in recent_entries]
    }

# Add these methods to DatasetService
DatasetService.get_entry = get_entry
DatasetService.get_stats = get_stats