import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Requerida por entorno: no hay URL por defecto para evitar usar una base
# de datos no prevista. SQLite solo debe usarse en desarrollo controlado.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL no configurada; definir la base de datos por entorno"
    )

engine = create_engine(
    DATABASE_URL,
    connect_args=(
        {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
    ),
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()