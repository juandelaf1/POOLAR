"""Configuración de pruebas de Trama Abierta MVP.

Define un entorno efímero y aislado:
- Secreto JWT solo para pruebas (nunca se usa en producción).
- Base SQLite local de pruebas.
- Limpieza de tablas antes y después de cada prueba.
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Sobrescribe cualquier variable externa: las pruebas nunca deben usar
# credenciales ni bases de datos reales.
os.environ["TRAMA_ABIERTA_SECRET_KEY"] = (
    "test-only-secret-key-not-for-production-0123456789abcdef"
)
os.environ["DATABASE_URL"] = "sqlite:///./.pytest_trama_abierta.db"


@pytest.fixture(autouse=True)
def reset_db():
    from src.core.database import engine
    from src.core.models import Base

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


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


def _crear_organizacion(db_session, nombre: str, email: str):
    from src.core.auth import hash_password
    from src.core.models import OperationalUser, Organizacion

    organizacion = Organizacion(
        nombre=nombre,
        tipo_organizacion="cooperativa",
        contacto_publico=email,
    )
    db_session.add(organizacion)
    db_session.flush()
    usuario = OperationalUser(
        email=email,
        hashed_password=hash_password("secret123"),
        nombre=f"Admin {nombre}",
        rol="administrador",
        organizacion_id=organizacion.id,
    )
    db_session.add(usuario)
    db_session.commit()
    db_session.refresh(organizacion)
    db_session.refresh(usuario)
    return {
        "org_id": organizacion.id,
        "user_id": usuario.id,
        "email": email,
        "password": "secret123",
    }


@pytest.fixture
def org_a(db_session):
    return _crear_organizacion(db_session, "Organización A", "admin@a.org")


@pytest.fixture
def org_b(db_session):
    return _crear_organizacion(db_session, "Organización B", "admin@b.org")


def _token(client, org):
    response = client.post(
        "/auth/token",
        json={"email": org["email"], "password": org["password"]},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def headers_a(client, org_a):
    return {"Authorization": f"Bearer {_token(client, org_a)}"}


@pytest.fixture
def headers_b(client, org_b):
    return {"Authorization": f"Bearer {_token(client, org_b)}"}


def crear_necesidad(
    db_session,
    *,
    organizacion_id=None,
    persona_id=None,
    titulo="Necesidad de prueba",
    visibilidad="privada",
):
    from src.core.models import Necesidad

    necesidad = Necesidad(
        titulo=titulo,
        descripcion="Descripción sintética de prueba",
        organizacion_id=organizacion_id,
        persona_id=persona_id,
        visibilidad=visibilidad,
        estado="propuesta",
    )
    db_session.add(necesidad)
    db_session.commit()
    db_session.refresh(necesidad)
    return necesidad


def crear_persona(db_session, nombre="Persona Sintética", email=None):
    from src.core.models import Persona

    persona = Persona(nombre=nombre, email=email)
    db_session.add(persona)
    db_session.commit()
    db_session.refresh(persona)
    return persona