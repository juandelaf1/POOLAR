"""Add execution tracking columns to approval_requests.

Revision ID: 0003_approval_exec
Revises: 7462b4e_approval
"""
from alembic import op
import sqlalchemy as sa

revision = '0003_approval_exec'
down_revision = '7462b4e_approval'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('approval_requests', sa.Column('executed_at', sa.DateTime(), nullable=True))
    op.add_column('approval_requests', sa.Column('execution_result', sa.Text(), nullable=True))
    op.add_column('approval_requests', sa.Column('execution_error', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('approval_requests', 'execution_error')
    op.drop_column('approval_requests', 'execution_result')
    op.drop_column('approval_requests', 'executed_at')