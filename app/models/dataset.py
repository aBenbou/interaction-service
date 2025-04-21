# app/models/dataset.py
import uuid
import json
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app import db

class DatasetEntry(db.Model):
    """Validated feedback entry for model retraining."""
    __tablename__ = 'dataset_entries'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feedback_id = db.Column(UUID(as_uuid=True), db.ForeignKey('feedback.id'), nullable=False, unique=True)
    model_id = db.Column(db.String(100), nullable=False, index=True)
    prompt_text = db.Column(db.Text, nullable=False)
    response_text = db.Column(db.Text, nullable=False)
    correct_response = db.Column(db.Text, nullable=True)
    dataset_metadata = db.Column(JSONB, default={}, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    feedback = db.relationship('Feedback', back_populates='dataset_entry')
    
    def to_dict(self):
        """Convert the dataset entry to a dictionary."""
        return {
            'id': str(self.id),
            'feedback_id': str(self.feedback_id),
            'model_id': self.model_id,
            'prompt_text': self.prompt_text,
            'response_text': self.response_text,
            'correct_response': self.correct_response,
            'metadata': self.dataset_metadata,
            'created_at': self.created_at.isoformat()
        }
    
    def to_training_format(self):
        """
        Convert the dataset entry to a format suitable for model training.
        
        Returns:
            Dictionary in the format expected by training systems
        """
        return {
            'prompt': self.prompt_text,
            'response': self.correct_response or self.response_text,
            'original_response': self.response_text,
            'quality_ratings': {
                rating['dimension_name']: rating['score'] 
                for rating in self.dataset_metadata.get('dimension_ratings', [])
            },
            'source': {
                'type': 'feedback',
                'id': str(self.id),
                'created_at': self.created_at.isoformat()
            }
        }