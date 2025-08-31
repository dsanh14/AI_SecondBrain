"""Initial database schema

Revision ID: 001
Revises: 
Create Date: 2023-09-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notes table
    op.create_table('notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    
    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('owner', sa.String(255), nullable=True),
        sa.Column('source_note_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('notes.id'), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # Create links table
    op.create_table('links',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_note_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('notes.id'), nullable=False),
        sa.Column('target_note_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('notes.id'), nullable=False),
        sa.Column('similarity', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # Create indexes
    op.create_index('idx_tasks_source_note_id', 'tasks', ['source_note_id'])
    op.create_index('idx_links_source_note_id', 'links', ['source_note_id'])
    op.create_index('idx_links_target_note_id', 'links', ['target_note_id'])


def downgrade() -> None:
    op.drop_table('links')
    op.drop_table('tasks')
    op.drop_table('notes')
