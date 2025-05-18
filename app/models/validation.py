# app/models/validation.py
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app import db

class ValidationRecord(db.Model):
    """Validation of feedback by a validator."""
    __tablename__ = 'validation_records'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feedback_id = db.Column(UUID(as_uuid=True), db.ForeignKey('feedback.id'), nullable=False, unique=True, index=True)
    validator_id = db.Column(db.String(36), nullable=False, index=True, comment="String format to match Auth Service's public_id")
    is_valid = db.Column(db.Boolean, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    validated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    feedback = db.relationship('Feedback', back_populates='validation_record')

    def to_dict(self):
        """Convert the validation record to a dictionary."""
        return {
            'id': str(self.id),
            'feedback_id': str(self.feedback_id),
            'validator_id': self.validator_id,
            'is_valid': self.is_valid,
            'notes': self.notes,
            'validated_at': self.validated_at.isoformat()
        }

