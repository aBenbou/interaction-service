# app/services/bookmark_service.py
from typing import Dict, List, Tuple, Optional, Any
from uuid import UUID
from app import db
from app.models.bookmark import InteractionBookmark
from app.utils.event_publisher import publish_event

class BookmarkService:
    """Business logic for interaction bookmarks."""
    
    @staticmethod
    def create_bookmark(user_id: UUID, interaction_id: UUID, name: str, notes: str = None) -> InteractionBookmark:
        """Create a bookmark for an interaction."""
        # Check if bookmark already exists
        existing = InteractionBookmark.query.filter(
            InteractionBookmark.user_id == user_id,
            InteractionBookmark.interaction_id == interaction_id
        ).first()
        
        if existing:
            # Update existing bookmark
            existing.name = name
            existing.notes = notes
            db.session.commit()
            return existing
        
        # Create new bookmark
        bookmark = InteractionBookmark(
            user_id=user_id,
            interaction_id=interaction_id,
            name=name,
            notes=notes
        )
        
        db.session.add(bookmark)
        db.session.commit()
        
        # Publish event
        publish_event('interaction.bookmarked', {
            'bookmark_id': str(bookmark.id),
            'interaction_id': str(bookmark.interaction_id),
            'user_id': str(bookmark.user_id)
        })
        
        return bookmark
    
    @staticmethod
    def get_user_bookmarks(user_id: UUID, page: int = 1, per_page: int = 10) -> Tuple[List[InteractionBookmark], int]:
        """Get all bookmarks for a user with pagination."""
        query = InteractionBookmark.query.filter(
            InteractionBookmark.user_id == user_id
        ).order_by(InteractionBookmark.created_at.desc())
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        bookmarks = query.offset(offset).limit(per_page).all()
        
        return bookmarks, total
    
    @staticmethod
    def delete_bookmark(bookmark_id: UUID, user_id: UUID) -> bool:
        """Delete a bookmark."""
        bookmark = InteractionBookmark.query.filter(
            InteractionBookmark.id == bookmark_id,
            InteractionBookmark.user_id == user_id
        ).first()
        
        if not bookmark:
            return False
        
        db.session.delete(bookmark)
        db.session.commit()
        
        return True