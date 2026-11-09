"""Configuración de pruebas de Poolar MVP.

Define un entorno efímero y aislado:
- Secreto JWT solo para pruebas (nunca se usa en producción).
- Base SQLite local de pruebas; PostgreSQL opcional vía `POOLAR_TEST_POSTGRES_URL`.
- Limpieza de tablas antes y después de cada prueba.
"""
import os
import sys
from pathlib import Path
from sqlalchemy import text

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Soporte PostgreSQL real si está disponible, si no SQLite.
pg_url = os.getenv("POOLAR_TEST_POSTGRES_URL")
if pg_url:
    os.environ["DATABASE_URL"] = pg_url
else:
    os.environ["DATABASE_URL"] = "sqlite:///./.pytest_poolar.db"

os.environ["POOLAR_SECRET_KEY"] = (
    "test-only-secret-key-not-for-production-0123456789abcdef"
)


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    from src.main import app
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db_session():
    from src.core.database import SessionLocal
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


_SQLITE_TABLES_DELETE_ORDER = [
    "approval_requests", "eventos_auditoria", "decisiones", "actividades",
    "recursos_aportes", "recursos", "conocimiento_capacidad", "invitaciones",
    "necesidad_problema_colectivo", "problema_participantes_persona",
    "problema_participantes_organizacion", "iniciativa_participantes_organizacion",
    "iniciativa_participantes_persona", "iniciativas", "problemas_colectivos",
    "necesidades", "operational_users", "personas", "organizaciones",
]


@pytest.fixture(autouse=True)
def reset_db():
    from src.core.database import engine
    from src.core.models import Base
    is_sqlite = str(engine.url).startswith("sqlite")
    if is_sqlite:
        # SQLite: esquema estable + limpieza de datos (más robusto que drop/create por test
        # cuando hay imports a nivel módulo / múltiples suites en una corrida).
        Base.metadata.create_all(bind=engine)
        with engine.begin() as conn:
            conn.execute(text("PRAGMA foreign_keys=OFF"))
            for t in _SQLITE_TABLES_DELETE_ORDER:
                try:
                    conn.execute(text(f"DELETE FROM {t}"))
                except Exception:
                    pass
            try:
                conn.execute(text("DELETE FROM sqlite_sequence"))
            except Exception:
                pass
            conn.execute(text("PRAGMA foreign_keys=ON"))
        yield
    else:
        # PostgreSQL: solo limpiar datos, conservar esquema migrado
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE approval_requests, eventos_auditoria, decisiones, iniciativas, invitaciones, recursos, recursos_aportes, conocimiento_capacidad, necesidad_problema_colectivo, problema_participantes_persona, problema_participantes_organizacion, problemas_colectivos, necesidades, operational_users, personas, organizaciones CASCADE"))
            conn.commit()
        yield
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE approval_requests, eventos_auditoria, decisiones, iniciativas, invitaciones, recursos, recursos_aportes, conocimiento_capacidad, necesidad_problema_colectivo, problema_participantes_persona, problema_participantes_organizacion, problemas_colectivos, necesidades, operational_users, personas, organizaciones CASCADE"))
            conn.commit()


def _crear_organizacion(db_session, nombre: str, email: str):
    from src.core.auth import hash_password
    from src.core.models import OperationalUser, Organizacion
    existing = db_session.query(OperationalUser).filter_by(email=email).first()
    if existing:
        org = db_session.get(Organizacion, existing.organizacion_id)
        if org is None:
            org = db_session.query(Organizacion).first()
        return {"org_id": org.id if org else existing.organizacion_id, "user_id": existing.id, "email": email, "password": "secret123"}
    organizacion = db_session.query(Organizacion).filter_by(nombre=nombre).first()
    if organizacion is None:
        organizacion = Organizacion(
            nombre=nombre, tipo_organizacion="cooperativa", contacto_publico=email,
        )
        db_session.add(organizacion)
        db_session.flush()
    usuario = OperationalUser(
        email=email, hashed_password=hash_password("secret123"),
        nombre=f"Admin {nombre}", rol="administrador",
        organizacion_id=organizacion.id,
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(organizacion)
    db_session.refresh(usuario)
    return {
        "org_id": organizacion.id, "user_id": usuario.id,
        "email": email, "password": "secret123",
    }


@pytest.fixture
def org_a(db_session):
    return _crear_organizacion(db_session, "Organización A", "admin@a.org")


@pytest.fixture
def org_b(db_session):
    return _crear_organizacion(db_session, "Organización B", "admin@b.org")


def _token(client, org):
    response = client.post("/auth/token", json={"email": org["email"], "password": org["password"]})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def headers_a(client, org_a):
    return {"Authorization": f"Bearer {_token(client, org_a)}"}


@pytest.fixture
def headers_b(client, org_b):
    return {"Authorization": f"Bearer {_token(client, org_b)}"}