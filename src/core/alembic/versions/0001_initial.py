"""Initial schema with PostgreSQL-ready constraints."""
from alembic import op
import sqlalchemy as sa


def upgrade() -> None:
    op.create_table(
        'persona',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('nombre', sa.String(200), nullable=False),
        sa.Column('email', sa.String(254), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=True),
        sa.Column('activo', sa.Boolean, default=True),
        sa.Column('fecha_creacion', sa.DateTime, nullable=True),
        sa.Column('fecha_actualizacion', sa.DateTime, nullable=True)
    )


def downgrade() -> None:
    op.drop_table('persona')