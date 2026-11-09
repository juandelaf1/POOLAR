"""Add approval scoping/authorization fields for Fase 0.

Revision ID: 0004_approval_scope_fase0
Revises: 0003_approval_exec
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_approval_scope_fase0"
down_revision = "0003_approval_exec"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("approval_requests", sa.Column("organizacion_id", sa.Integer(), nullable=True))
    op.add_column("approval_requests", sa.Column("proposer_type", sa.String(length=30), nullable=True))
    op.add_column("approval_requests", sa.Column("proposer_actor_id", sa.Integer(), nullable=True))
    op.add_column("approval_requests", sa.Column("resource_type", sa.String(length=100), nullable=True))
    op.add_column("approval_requests", sa.Column("resource_id", sa.String(length=100), nullable=True))
    op.add_column("approval_requests", sa.Column("policy_id", sa.String(length=100), nullable=True))
    op.add_column("approval_requests", sa.Column("correlation_id", sa.String(length=200), nullable=True))
    op.add_column("approval_requests", sa.Column("idempotency_key", sa.String(length=200), nullable=True))
    op.create_index("ix_approval_requests_organizacion_id", "approval_requests", ["organizacion_id"], unique=False)
    op.create_index("ix_approval_requests_idempotency_key", "approval_requests", ["idempotency_key"], unique=False)


def downgrade():
    op.drop_index("ix_approval_requests_idempotency_key", table_name="approval_requests")
    op.drop_index("ix_approval_requests_organizacion_id", table_name="approval_requests")
    for col in [
        "idempotency_key", "correlation_id", "policy_id", "resource_id",
        "resource_type", "proposer_actor_id", "proposer_type", "organizacion_id",
    ]:
        op.drop_column("approval_requests", col)
