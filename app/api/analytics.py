from flask import Blueprint, request, jsonify, g
from app.utils.decorators import jwt_required_with_permissions
from app.services.analytics_service import AnalyticsService
from datetime import datetime

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

@analytics_bp.route('/user', methods=['GET'])
@jwt_required_with_permissions(['analytics:read'])
def get_user_metrics():
    """Get engagement metrics for the current user."""
    user_id = str(g.current_user_id)
    
    start_date = None
    end_date = None
    
    if request.args.get('start_date'):
        try:
            start_date = datetime.fromisoformat(request.args['start_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)'
            }), 400
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.fromisoformat(request.args['end_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)'
            }), 400
    
    result = AnalyticsService.get_user_engagement_metrics(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return jsonify(result), 200

@analytics_bp.route('/model/<model_id>', methods=['GET'])
@jwt_required_with_permissions(['analytics:read'])
def get_model_metrics(model_id):
    """Get performance metrics for a specific model."""
    start_date = None
    end_date = None
    
    if request.args.get('start_date'):
        try:
            start_date = datetime.fromisoformat(request.args['start_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)'
            }), 400
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.fromisoformat(request.args['end_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)'
            }), 400
    
    result = AnalyticsService.get_model_performance_metrics(
        model_id=model_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return jsonify(result), 200

@analytics_bp.route('/system', methods=['GET'])
@jwt_required_with_permissions(['analytics:admin'])
def get_system_metrics():
    """Get system-wide metrics."""
    start_date = None
    end_date = None
    
    if request.args.get('start_date'):
        try:
            start_date = datetime.fromisoformat(request.args['start_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid start_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)'
            }), 400
    
    if request.args.get('end_date'):
        try:
            end_date = datetime.fromisoformat(request.args['end_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                'success': False,
                'message': 'Invalid end_date format. Use ISO format (YYYY-MM-DDTHH:MM:SSZ)'
            }), 400
    
    result = AnalyticsService.get_system_metrics(
        start_date=start_date,
        end_date=end_date
    )
    
    return jsonify(result), 200 