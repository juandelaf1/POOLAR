"""Add approval_requests table.

Revision ID: 7462b4e_approval
Revises: 8ad67c5
"""
from alembic import op
import sqlalchemy as sa

revision = '7462b4e_approval'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('approval_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('approval_id', sa.String(length=100), nullable=False),
        sa.Column('execution_id', sa.String(length=200), nullable=False),
        sa.Column('tool_name', sa.String(length=200), nullable=False),
        sa.Column('inputs', sa.Text(), nullable=False),
        sa.Column('proposed_by', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejected_by', sa.Integer(), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['proposed_by'], ['operational_users.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['operational_users.id'], ),
        sa.ForeignKeyConstraint(['rejected_by'], ['operational_users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('approval_id')
    )
    op.create_index(op.f('ix_approval_requests_approval_id'), 'approval_requests', ['approval_id'], unique=True)
    op.create_index(op.f('ix_approval_requests_execution_id'), 'approval_requests', ['execution_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_approval_requests_execution_id'), table_name='approval_requests')
    op.drop_index(op.f('ix_approval_requests_approval_id'), table_name='approval_requests')
    op.drop_table('approval_requests')
