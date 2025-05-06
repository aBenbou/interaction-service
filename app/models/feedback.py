# app/models/feedback.py
import uuid
from datetime import datetime
from flask import g
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app import db

class Feedback(db.Model):
    """User feedback on model responses."""
    __tablename__ = 'feedback'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = db.Column(UUID(as_uuid=True), db.ForeignKey('interactions.id', ondelete='CASCADE'), nullable=False)
    prompt_id = db.Column(UUID(as_uuid=True), db.ForeignKey('prompts.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.String(36), nullable=False, index=True)
    model_id = db.Column(db.String(100), nullable=False, index=True)
    model_version = db.Column(db.String(50), nullable=False)
    
    category = db.Column(db.String(50), nullable=False, index=True)  
    rating = db.Column(db.Integer)  
    binary_evaluation = db.Column(db.Boolean)  
    ranking = db.Column(db.Integer) 
    justification = db.Column(db.Text)  
   
    validation_status = db.Column(
        db.Enum('PENDING', 'ACCEPTED', 'REJECTED', name='validation_status_enum'),
        default='PENDING',
        nullable=False
    )
    validator_id = db.Column(db.String(36), nullable=True)
    validation_notes = db.Column(db.Text)
    

    meta_data = db.Column(JSONB, default={})
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    interaction = db.relationship('Interaction', back_populates='feedback')
    prompt = db.relationship('Prompt', back_populates='feedback')

    response_id = db.Column(UUID(as_uuid=True), db.ForeignKey('responses.id'), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    claimed_by = db.Column(UUID(as_uuid=True), nullable=True, index=True)  # New field
    claimed_at = db.Column(db.DateTime, nullable=True)  # New field

    # Relationships
    response = db.relationship('Response', back_populates='feedback_entries')

    
    def to_dict(self):
        """Convert the feedback to a dictionary."""
        return {
            'id': str(self.id),
            'interaction_id': str(self.interaction_id),
            'prompt_id': str(self.prompt_id),
            'user_id': self.user_id,
            'model_id': self.model_id,
            'model_version': self.model_version,
            'category': self.category,
            'rating': self.rating,
            'binary_evaluation': self.binary_evaluation,
            'ranking': self.ranking,
            'justification': self.justification,
            'validation_status': self.validation_status,
            'validator_id': self.validator_id,
            'validation_notes': self.validation_notes,
            'metadata': self.meta_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'response_id': str(self.response_id),
            'rating': self.rating,
            'comments': self.comments,
            'created_at': self.created_at.isoformat(),
            'claimed_by': str(self.claimed_by) if self.claimed_by else None,
            'claimed_at': self.claimed_at.isoformat() if self.claimed_at else None
        }

