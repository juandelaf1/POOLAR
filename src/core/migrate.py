"""Módulo de migraciones para Poolar."""
import sys
import os

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from alembic.config import Config
from alembic import command


def _alembic_config():
    cfg = Config("alembic.ini")
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        cfg.set_main_option("sqlalchemy.url", db_url)
    return cfg


def upgrade(revision: str = "head"):
    cfg = _alembic_config()
    command.upgrade(cfg, revision)


def downgrade(revision: str = "-1"):
    cfg = _alembic_config()
    command.downgrade(cfg, revision)


def current():
    cfg = _alembic_config()
    command.current(cfg)


def main():
    if len(sys.argv) < 2:
        print("Uso: python -m src.core.migrate [upgrade|downgrade|current] [revision]")
        sys.exit(1)
    action = sys.argv[1]
    revision = sys.argv[2] if len(sys.argv) > 2 else ("head" if action == "upgrade" else "-1")
    if action == "upgrade":
        upgrade(revision)
    elif action == "downgrade":
        downgrade(revision)
    elif action == "current":
        current()
    else:
        print(f"Acción desconocida: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()