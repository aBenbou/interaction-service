# app/models/feedback.py
import uuid
from datetime import datetime
from flask import g
from sqlalchemy.dialects.postgresql import UUID
from app import db

class Feedback(db.Model):
    """User feedback on a model response."""
    __tablename__ = 'feedback'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    response_id = db.Column(UUID(as_uuid=True), db.ForeignKey('responses.id'), nullable=False, index=True)
    user_id = db.Column(db.String(36), nullable=False, index=True, comment="String format to match Auth Service's public_id")
    overall_comment = db.Column(db.Text, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(
        db.Enum('PENDING', 'VALIDATED', 'REJECTED', name='feedback_status_enum'),
        default='PENDING',
        nullable=False,
        index=True
    )
    
    # Relationships
    response = db.relationship('Response', back_populates='feedback_entries')
    dimension_ratings = db.relationship('DimensionRating', back_populates='feedback',
                                      cascade='all, delete-orphan')
    validation_record = db.relationship('ValidationRecord', uselist=False, 
                                       back_populates='feedback',
                                       cascade='all, delete-orphan')
    dataset_entry = db.relationship('DatasetEntry', uselist=False,
                                   back_populates='feedback',
                                   cascade='all, delete-orphan')
    
    def to_dict(self, include_ratings=True):
        """
        Convert the feedback to a dictionary.
        
        Args:
            include_ratings: Whether to include dimension ratings
        """
        result = {
            'id': str(self.id),
            'response_id': str(self.response_id),
            'user_id': self.user_id,
            'overall_comment': self.overall_comment,
            'submitted_at': self.submitted_at.isoformat(),
            'status': self.status
        }
        
        # Add user profile information if available
        user_profiles = getattr(g, 'user_profiles', {})
        user_profile = user_profiles.get(str(self.user_id))
        if user_profile:
            result['user'] = {
                'username': user_profile.get('username'),
                'first_name': user_profile.get('first_name'),
                'last_name': user_profile.get('last_name')
            }
            
        # Add connection information if available
        user_connections = getattr(g, 'user_connections', {})
        connection = user_connections.get(str(self.user_id))
        if connection:
            if 'user' not in result:
                result['user'] = {}
            result['user']['connection'] = connection
        
        if include_ratings:
            result['dimension_ratings'] = [
                rating.to_dict() for rating in self.dimension_ratings
            ]
            
        return result

