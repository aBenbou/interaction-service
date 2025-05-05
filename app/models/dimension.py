# app/models/dimension.py
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from app import db
from sqlalchemy.dialects.postgresql import JSONB

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
    scale_type = db.Column(db.String(50), nullable=False, default='numeric')  # e.g., numeric, binary, custom
    scale_options = db.Column(JSONB, nullable=True)  # e.g., {"min": 1, "max": 5} or {"labels": ["Yes", "No"]}
    evaluation_method = db.Column(db.String(50), nullable=False, default='rating')  # e.g., rating, binary, ranking
    ui_component = db.Column(db.String(50), nullable=True)  # e.g., stars, slider, thumbs
    help_text = db.Column(db.Text, nullable=True)  # Help text or tooltips
    placeholder = db.Column(db.String(100), nullable=True)  # Placeholder text
    scale_labels = db.Column(JSONB, nullable=True)  # e.g., {"1": "Poor", "5": "Excellent"}
    weight = db.Column(db.Float, nullable=False, default=1.0)  # New field for weighting
    is_required = db.Column(db.Boolean, nullable=False, default=False)  # New field for required validation
    validation_rules = db.Column(JSONB, nullable=True)  # New field for custom validation rules

    
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
            'created_at': self.created_at.isoformat(),
            'scale_type': self.scale_type,
            'scale_options': self.scale_options,
            'evaluation_method': self.evaluation_method,
            'ui_component': self.ui_component,
            'help_text': self.help_text,
            'placeholder': self.placeholder,
            'scale_labels': self.scale_labels,
            'weight': self.weight,
            'is_required': self.is_required,
            'validation_rules': self.validation_rules
        }

