# app/api/bookmarks.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.bookmark_service import BookmarkService
from app.services.interaction_service import InteractionService
from uuid import UUID

bookmarks_bp = Blueprint('bookmarks', __name__)

@bookmarks_bp.route('/interactions/<uuid:interaction_id>/bookmark', methods=['POST'])
@jwt_required()
def bookmark_interaction(interaction_id):
    """Bookmark an interaction."""
    user_id = UUID(get_jwt_identity())
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'success': False, 'message': 'Bookmark name is required'}), 400
    
    # Check if interaction exists
    interaction = InteractionService.get_interaction(interaction_id)
    if not interaction:
        return jsonify({'success': False, 'message': 'Interaction not found'}), 404
    
    # Create bookmark
    bookmark = BookmarkService.create_bookmark(
        user_id=user_id,
        interaction_id=interaction_id,
        name=data.get('name'),
        notes=data.get('notes')
    )
    
    return jsonify({'success': True, 'bookmark': bookmark.to_dict()}), 201

@bookmarks_bp.route('/bookmarks', methods=['GET'])
@jwt_required()
def get_bookmarks():
    """Get all bookmarks for current user."""
    user_id = UUID(get_jwt_identity())
    
    # Parse pagination parameters
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 10)), 50)
    
    bookmarks, total = BookmarkService.get_user_bookmarks(
        user_id, page, per_page
    )
    
    return jsonify({
        'success': True,
        'bookmarks': [bookmark.to_dict() for bookmark in bookmarks],
        'pagination': {
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    }), 200

@bookmarks_bp.route('/bookmarks/<uuid:bookmark_id>', methods=['DELETE'])
@jwt_required()
def delete_bookmark(bookmark_id):
    """Delete a bookmark."""
    user_id = UUID(get_jwt_identity())
    
    result = BookmarkService.delete_bookmark(bookmark_id, user_id)
    if not result:
        return jsonify({'success': False, 'message': 'Bookmark not found or unauthorized'}), 404
    
    return jsonify({'success': True, 'message': 'Bookmark deleted successfully'}), 200

@bookmarks_bp.route('/bookmarks/<uuid:bookmark_id>', methods=['PUT'])
@jwt_required()
def update_bookmark(bookmark_id):
    """Update a bookmark's name or notes."""
    user_id = UUID(get_jwt_identity())
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name'):
        return jsonify({'success': False, 'message': 'Bookmark name is required'}), 400
    
    # Get the bookmark
    from app.models.bookmark import InteractionBookmark
    bookmark = InteractionBookmark.query.filter_by(id=bookmark_id, user_id=user_id).first()
    
    if not bookmark:
        return jsonify({'success': False, 'message': 'Bookmark not found or unauthorized'}), 404
    
    # Update bookmark
    bookmark.name = data.get('name')
    bookmark.notes = data.get('notes')
    
    from app import db
    db.session.commit()
    
    return jsonify({'success': True, 'bookmark': bookmark.to_dict()}), 200