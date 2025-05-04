# app/models/prompt.py
import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app import db

# class Prompt(db.Model):
#     """User prompt submitted to an AI model."""
#     __tablename__ = 'prompts'
    
#     id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     interaction_id = db.Column(UUID(as_uuid=True), 
#                               db.ForeignKey('interactions.id'), 
#                               nullable=False, 
#                               index=True)
#     content = db.Column(db.Text, nullable=False)
#     sequence_number = db.Column(db.Integer, nullable=False)
#     submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
#     context = db.Column(JSONB, default={}, nullable=False)
    
#     # Relationships
#     interaction = db.relationship('Interaction', back_populates='prompts')
#     response = db.relationship('Response', uselist=False, back_populates='prompt',
#                               cascade='all, delete-orphan')
    
#     # Unique constraint for sequence ordering within an interaction
#     __table_args__ = (
#         db.UniqueConstraint('interaction_id', 'sequence_number', 
#                            name='uq_prompt_sequence'),
#     )
    
#     def to_dict(self):
#         """Convert the prompt to a dictionary."""
#         return {
#             'id': str(self.id),
#             'interaction_id': str(self.interaction_id),
#             'content': self.content,
#             'sequence_number': self.sequence_number,
#             'submitted_at': self.submitted_at.isoformat(),
#             'context': self.context
#         }


class Prompt(db.Model):
    """User prompt submitted to an AI model."""
    __tablename__ = 'prompts'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    interaction_id = db.Column(UUID(as_uuid=True), db.ForeignKey('interactions.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    context = db.Column(JSONB, default={}, nullable=False)

    # Relationships
    interaction = db.relationship('Interaction', back_populates='prompts')
    response = db.relationship('Response', uselist=False, back_populates='prompt', cascade='all, delete-orphan')