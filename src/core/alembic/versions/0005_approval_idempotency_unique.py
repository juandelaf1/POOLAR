"""Unique idempotency key for approval requests (F0-07, partial).

Revision ID: 0005_approval_idempotency_unique
Revises: 0004_approval_scope_fase0
"""
from alembic import op
from sqlalchemy import text

revision = "0005_approval_idempotency_unique"
down_revision = "0004_approval_scope_fase0"
branch_labels = None
depends_on = None


def upgrade():
    # Único cuando hay key; múltiples NULL permitidos (SQL estándar / PG / SQLite moderno).
    bind = op.get_bind()
    op.drop_index("ix_approval_requests_idempotency_key", table_name="approval_requests")
    if bind.dialect.name == "postgresql":
        op.create_index(
            "ux_approval_requests_idempotency_key",
            "approval_requests",
            ["idempotency_key"],
            unique=True,
            postgresql_where=text("idempotency_key IS NOT NULL"),
        )
    else:
        op.execute(
            "CREATE UNIQUE INDEX ux_approval_requests_idempotency_key ON approval_requests (idempotency_key) WHERE idempotency_key IS NOT NULL"
        )


def downgrade():
    op.drop_index("ux_approval_requests_idempotency_key", table_name="approval_requests")
    op.create_index("ix_approval_requests_idempotency_key", "approval_requests", ["idempotency_key"], unique=False)

