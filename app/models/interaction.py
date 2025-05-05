# app/models/interaction.py
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app import db

class Interaction(db.Model):
    """User interaction with an AI model."""
    __tablename__ = 'interactions'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.String(36), nullable=False, index=True, comment="String format to match Auth Service's public_id")
    model_id = db.Column(db.String(100), nullable=False, index=True)
    model_version = db.Column(db.String(50), nullable=False)
    endpoint_name = db.Column(db.String(100), nullable=False, index=True)
    session_id = db.Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ended_at = db.Column(db.DateTime, nullable=True)
    status = db.Column(
        db.Enum('ACTIVE', 'COMPLETED', 'ABANDONED', name='interaction_status_enum'),
        default='ACTIVE',
        nullable=False
    )
    # Rename 'metadata' to 'interaction_metadata' to avoid SQLAlchemy reserved name conflict
    interaction_metadata = db.Column(JSONB, default={}, nullable=False)
    
    # Relationships
    prompts = db.relationship('Prompt', back_populates='interaction', 
                             cascade='all, delete-orphan')
    conversation_history = db.Column(JSONB, default=[], nullable=False)  # New field

    
    def to_dict(self):
        """Convert the interaction to a dictionary."""
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'model_id': self.model_id,
            'model_version': self.model_version,
            'endpoint_name': self.endpoint_name,
            'session_id': str(self.session_id),
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'status': self.status,
            'metadata': self.interaction_metadata  # Keep the API response consistent
        }