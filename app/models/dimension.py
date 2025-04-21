# app/models/dimension.py
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app import db

class EvaluationDimension(db.Model):
    """Dimension on which users evaluate model responses."""
    __tablename__ = 'evaluation_dimensions'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = db.Column(db.String(100), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_by = db.Column(UUID(as_uuid=True), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    dimension_ratings = db.relationship('DimensionRating', back_populates='dimension')
    
    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('model_id', 'name', name='uq_model_dimension'),
    )
    
    def to_dict(self):
        """Convert the dimension to a dictionary."""
        return {
            'id': str(self.id),
            'model_id': self.model_id,
            'name': self.name,
            'description': self.description,
            'created_by': str(self.created_by),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

