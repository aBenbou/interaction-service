from flask import Blueprint, request, jsonify, g
from app.utils.decorators import jwt_required_with_permissions
from app.services.leaderboard_service import LeaderboardService

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')

@leaderboard_bp.route('/rankings', methods=['GET'])
@jwt_required_with_permissions(['leaderboard:read'])
def get_rankings():
    """Get user rankings."""
    time_period = request.args.get('time_period', 'all_time')
    category = request.args.get('category')
    limit = int(request.args.get('limit', 100))
    
    if time_period not in ['daily', 'weekly', 'monthly', 'all_time']:
        return jsonify({
            'success': False,
            'message': 'Invalid time period. Use: daily, weekly, monthly, or all_time'
        }), 400
        
    if limit < 1 or limit > 1000:
        return jsonify({
            'success': False,
            'message': 'Limit must be between 1 and 1000'
        }), 400
    
    result = LeaderboardService.get_user_rankings(
        time_period=time_period,
        category=category,
        limit=limit
    )
    
    return jsonify(result), 200

@leaderboard_bp.route('/achievements', methods=['GET'])
@jwt_required_with_permissions(['leaderboard:read'])
def get_achievements():
    """Get achievements for the current user."""
    user_id = str(g.current_user_id)
    
    result = LeaderboardService.get_user_achievements(user_id)
    
    return jsonify(result), 200

@leaderboard_bp.route('/achievements/<user_id>', methods=['GET'])
@jwt_required_with_permissions(['leaderboard:admin'])
def get_user_achievements(user_id):
    """Get achievements for a specific user (admin only)."""
    result = LeaderboardService.get_user_achievements(user_id)
    
    return jsonify(result), 200 