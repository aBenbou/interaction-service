# app/models/bookmark.py
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app import db

class InteractionBookmark(db.Model):
    """User bookmark for an interaction."""
    __tablename__ = 'interaction_bookmarks'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), nullable=False)
    interaction_id = db.Column(UUID(as_uuid=True), 
                              db.ForeignKey('interactions.id'), 
                              nullable=False)
    name = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    interaction = db.relationship('Interaction', back_populates='bookmarks')
    
    # Unique constraint to prevent duplicate bookmarks
    __table_args__ = (
        db.UniqueConstraint('user_id', 'interaction_id', name='uq_user_bookmark'),
    )
    
    def to_dict(self):
        """Convert bookmark to dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'interaction_id': str(self.interaction_id),
            'name': self.name,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }