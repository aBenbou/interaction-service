# app/models/interaction.py
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, ARRAY, JSONB
from app import db

class Interaction(db.Model):
    """User interaction with an AI model."""
    __tablename__ = 'interactions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), nullable=False, index=True)
    model_id = db.Column(db.String(100), nullable=False, index=True)
    model_version = db.Column(db.String(50), nullable=False)
    session_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(
        db.Enum('ACTIVE', 'COMPLETED', 'ABANDONED', name='interaction_status_enum'),
        default='ACTIVE',
        nullable=False
    )
    tags = db.Column(ARRAY(db.String), default=[], nullable=False)
    meta_data = db.Column(JSONB, default={}, nullable=False)  # Renamed from metadata to meta_data
    
    # Relationships
    prompts = db.relationship('Prompt', back_populates='interaction', 
                             cascade='all, delete-orphan')
    bookmarks = db.relationship('InteractionBookmark', back_populates='interaction',
                              cascade='all, delete-orphan')
    
    @property
    def duration_seconds(self):
        """Calculate interaction duration in seconds."""
        if not self.ended_at or self.status == 'ACTIVE':
            return None
        return (self.ended_at - self.started_at).total_seconds()
    
    def to_dict(self):
        """Convert interaction to dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'model_id': self.model_id,
            'model_version': self.model_version,
            'session_id': str(self.session_id),
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'status': self.status,
            'tags': self.tags,
            'metadata': self.meta_data,  # Still return as metadata in the API
            'duration_seconds': self.duration_seconds
        }