"""add feedback table

Revision ID: add_feedback_table
Revises: previous_revision
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_feedback_table'
down_revision = 'previous_revision'  # Update this with your previous migration
branch_labels = None
depends_on = None

def upgrade():
    # Create feedback table
    op.create_table(
        'feedback',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('interaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prompt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('rating', sa.Integer, nullable=True),
        sa.Column('binary_evaluation', sa.Boolean, nullable=True),
        sa.Column('ranking', sa.Integer, nullable=True),
        sa.Column('justification', sa.Text, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('validator_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('validation_notes', sa.Text, nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['interaction_id'], ['interaction.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['prompt_id'], ['prompt.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['validator_id'], ['user.id'], ondelete='SET NULL')
    )
    
    # Create indexes
    op.create_index('ix_feedback_interaction_id', 'feedback', ['interaction_id'])
    op.create_index('ix_feedback_prompt_id', 'feedback', ['prompt_id'])
    op.create_index('ix_feedback_user_id', 'feedback', ['user_id'])
    op.create_index('ix_feedback_status', 'feedback', ['status'])
    op.create_index('ix_feedback_category', 'feedback', ['category'])
    op.create_index('ix_feedback_created_at', 'feedback', ['created_at'])

def downgrade():
    # Drop indexes
    op.drop_index('ix_feedback_created_at')
    op.drop_index('ix_feedback_category')
    op.drop_index('ix_feedback_status')
    op.drop_index('ix_feedback_user_id')
    op.drop_index('ix_feedback_prompt_id')
    op.drop_index('ix_feedback_interaction_id')
    
    # Drop table
    op.drop_table('feedback') 