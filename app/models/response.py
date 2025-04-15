# app/models/response.py
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app import db

class Response(db.Model):
    """AI model response to a user prompt."""
    __tablename__ = 'responses'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id = db.Column(UUID(as_uuid=True), 
                         db.ForeignKey('prompts.id'), 
                         nullable=False, 
                         unique=True,
                         index=True)
    content = db.Column(db.Text, nullable=False)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processing_time_ms = db.Column(db.Integer, nullable=True)
    tokens_used = db.Column(db.Integer, nullable=True)
    model_confidence = db.Column(db.Float, nullable=True)
    error = db.Column(db.Text, nullable=True)
    
    # Relationship
    prompt = db.relationship('Prompt', back_populates='response')
    
    def to_dict(self):
        """Convert response to dictionary."""
        return {
            'id': str(self.id),
            'prompt_id': str(self.prompt_id),
            'content': self.content,
            'generated_at': self.generated_at.isoformat(),
            'processing_time_ms': self.processing_time_ms,
            'tokens_used': self.tokens_used,
            'model_confidence': self.model_confidence,
            'error': self.error
        }