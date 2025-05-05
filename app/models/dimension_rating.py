# app/models/dimension_rating.py
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app import db
from sqlalchemy.dialects.postgresql import JSONB

class DimensionRating(db.Model):
    """Rating for a specific dimension within feedback."""
    __tablename__ = 'dimension_ratings'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feedback_id = db.Column(UUID(as_uuid=True), db.ForeignKey('feedback.id'), nullable=False, index=True)
    dimension_id = db.Column(UUID(as_uuid=True), db.ForeignKey('evaluation_dimensions.id'), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)  # 1-5 rating
    justification = db.Column(db.Text, nullable=True)
    correct_response = db.Column(db.Text, nullable=True) 
    value = db.Column(JSONB, nullable=False)  # If user marked it incorrect
    
    # Relationships
    feedback = db.relationship('Feedback', back_populates='dimension_ratings')
    dimension = db.relationship('EvaluationDimension', back_populates='dimension_ratings')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('feedback_id', 'dimension_id', name='uq_feedback_dimension'),
        db.CheckConstraint('score >= 1 AND score <= 5', name='check_valid_score')
    )
    
    def to_dict(self):
        """Convert the dimension rating to a dictionary."""
        return {
            'id': str(self.id),
            'feedback_id': str(self.feedback_id),
            'dimension_id': str(self.dimension_id),
            'dimension_name': self.dimension.name if self.dimension else None,
            'score': self.score,
            'justification': self.justification,
            'correct_response': self.correct_response,
            'value': self.value
        }