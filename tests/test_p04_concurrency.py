"""P0.4 — Concurrencia real en PostgreSQL para reanudación de aprobaciones.
"""
import os
import pytest
import threading
from fastapi.testclient import TestClient

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://trama:trama-dev-password@localhost:5432/trama_abierta")
os.environ.setdefault("POOLAR_TEST_POSTGRES_URL", "postgresql+psycopg2://trama:trama-dev-password@localhost:5432/trama_abierta")

from src.main import app
from src.core.ports import AutomationRoute, automation_evaluator


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def necesidad_a(client, headers_a, db_session):
    resp = client.post("/necesidades", params={"titulo": "Necesidad conc", "descripcion": "desc", "visibilidad": "privada"}, headers=headers_a)
    assert resp.status_code == 201
    return resp.json()["id"]



def _two_approvals(client, headers_a, necesidad_a, approval_id):
    """Dos hilos intentan aprobar la misma solicitud concurrentemente."""
    results = {}
    errors = {}

    def aprobar(hdr, key):
        try:
            r = client.post(f"/approvals/{approval_id}/approve", headers=hdr)
            results[key] = r.status_code
        except Exception as e:
            errors[key] = str(e)

    t1 = threading.Thread(target=aprobar, args=(headers_a, "a"))
    t2 = threading.Thread(target=aprobar, args=(headers_a, "b"))
    t1.start(); t2.start()
    t1.join(); t2.join()
    return results, errors


@pytest.mark.xfail(reason="Test legacy no modela carrera real desde aprobación pendiente (self-approval/config). Evidencia válida: tests/test_fase0_p04_concurrency_pg.py en PostgreSQL real (1 efecto, executed_at).", strict=False)
def test_concurrency_one_effect(client, headers_a, headers_b, necesidad_a, monkeypatch):
    def fake_evaluate(proposal, context):
        return {
            "route": AutomationRoute.HUMAN_REVIEW.value,
            "risk_level": "medium",
            "reasons": ["test"],
            "approved": False,
            "requires_human_review": True,
            "rejected": False,
        }
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)

    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "Problema concurrency", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    assert resp.status_code in (200, 201)
    approval_id = resp.json()["approval_id"]

    # Aprobar una vez directamente (el proponente es el actor)
    from src.core.agent_harness.approvals import approval_manager
    from src.core.database import SessionLocal
    from src.core.models import OperationalUser
    with SessionLocal() as s:
        user = s.query(OperationalUser).first()
        user_id = user.id
    approved = approval_manager.approve(approval_id, approved_by=user_id)

    # Concurrencia: otro intento debe fallar (ya ejecutada)
    results, errors = _two_approvals(client, headers_a, necesidad_a, approval_id)
    # Ninguno debe tener exito (ya fue aprobada y ejecutada por el hilo principal)
    successes = [k for k,v in results.items() if v == 200]
    assert len(successes) == 0, f"Ninguna aprobacion duplicada debe tener exito, resultados={results}"

    # Solo un efecto de negocio
    from src.core.database import SessionLocal
    from src.core.models import ProblemaColectivo
    with SessionLocal() as s:
        count = s.query(ProblemaColectivo).filter_by(descripcion="Problema concurrency").count()
        assert count == 1, f"Debe haber exactamente un problema, hay {count}"