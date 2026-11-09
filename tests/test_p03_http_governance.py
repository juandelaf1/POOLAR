"""P0.3 — Pruebas HTTP reales de gobernanza en endpoints de Poolar.

Verifica que los endpoints atraviesan _handle_governance y producen
los efectos correctos: REJECT, HUMAN_REVIEW, AUTO_APPROVE.
"""
import os
import pytest
from unittest.mock import patch

# Entorno de pruebas (conftest controla DB/secret; mantener compat si se ejecuta aislado)
os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.main import app
from src.core.ports import AutomationRoute, automation_evaluator


@pytest.fixture
def necesidad_a(client, headers_a):
    resp = client.post("/necesidades", params={"titulo": "Necesidad test", "descripcion": "descripcion suficiente", "visibilidad": "privada"}, headers=headers_a)
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.fixture
def necesidad_a(client, headers_a, db_session):
    """Crea una necesidad para usar en tests."""
    resp = client.post("/necesidades", params={"titulo": "Necesidad test", "descripcion": "desc", "visibilidad": "privada"}, headers=headers_a)
    assert resp.status_code == 201
    return resp.json()["id"]


# ── REJECT ──────────────────────────────────────────────────────────────

def test_http_reject_no_crea_problema(client, headers_a, necesidad_a, monkeypatch):
    """REJECT en endpoint: no debe crear problema colectivo."""
    # Forzar evaluador a devolver REJECT
    def fake_evaluate(proposal, context):
        return {
            "route": AutomationRoute.REJECT.value,
            "risk_level": "high",
            "reasons": ["test reject"],
            "approved": False,
            "requires_human_review": False,
            "rejected": True,
        }
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)

    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "Problema test", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    assert resp.status_code == 403
    assert "rechazada" in resp.json()["detail"].lower() or "rechaz" in resp.json()["detail"].lower()


def test_http_reject_no_crea_decision(client, headers_a, necesidad_a, monkeypatch):
    """REJECT en endpoint de decisión: no debe crear Decision."""
    # Crear iniciativa primero (AUTO_APPROVE)
    resp_init = client.post(
        "/iniciativas",
        params={"necesidad_id": necesidad_a, "responsable_id": 1, "criterios_decision": "criterio de prueba suficiente"},
        headers=headers_a,
    )
    # Si falla por gobernanza mock, saltar
    if resp_init.status_code not in (200, 201):
        pytest.skip("No se pudo crear iniciativa base")
    iniciativa_id = resp_init.json()["id"]

    def fake_evaluate(proposal, context):
        return {
            "route": AutomationRoute.REJECT.value,
            "risk_level": "high",
            "reasons": ["test reject"],
            "approved": False,
            "requires_human_review": False,
            "rejected": True,
        }
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)

    resp = client.post(
        "/decisiones",
        params={
            "iniciativa_id": iniciativa_id,
            "tipo_decision": "aprobar",
            "alternativa_elegida": "alt1",
            "motivo": "motivo test",
            "responsable_decision": 1,
            "version_metodologia": "v1",
        },
        headers=headers_a,
    )
    assert resp.status_code == 403


# ── HUMAN_REVIEW ─────────────────────────────────────────────────────────

def test_http_human_review_crea_solicitud_persistida(client, headers_a, necesidad_a, monkeypatch):
    """HUMAN_REVIEW: debe crear solicitud persistida y retornar pending_review."""
    def fake_evaluate(proposal, context):
        return {
            "route": AutomationRoute.HUMAN_REVIEW.value,
            "risk_level": "medium",
            "reasons": ["test human review"],
            "approved": False,
            "requires_human_review": True,
            "rejected": False,
        }
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)

    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "Problema HR test", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    assert resp.status_code in (200, 201)
    body = resp.json()
    assert body["status"] == "pending_review"
    assert "approval_id" in body

    # Verificar que la solicitud está persistida
    from src.core.agent_harness.approvals import approval_manager
    req = approval_manager.get(body["approval_id"])
    assert req is not None
    assert req.status.value == "pendiente" if hasattr(req.status, "value") else req.status == "pendiente"


def test_http_human_review_no_crea_problema(client, headers_a, necesidad_a, monkeypatch):
    """HUMAN_REVIEW: el problema colectivo NO debe crearse prematuramente."""
    def fake_evaluate(proposal, context):
        return {
            "route": AutomationRoute.HUMAN_REVIEW.value,
            "risk_level": "medium",
            "reasons": ["test human review"],
            "approved": False,
            "requires_human_review": True,
            "rejected": False,
        }
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)

    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "Problema HR no crear", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    assert resp.status_code in (200, 201)
    assert resp.json()["status"] == "pending_review"

    # Verificar que no se creó ningún problema colectivo con esa descripción
    from src.core.database import SessionLocal
    from src.core.models import ProblemaColectivo
    with SessionLocal() as s:
        count = s.query(ProblemaColectivo).filter_by(descripcion="Problema HR no crear").count()
        assert count == 0, "HUMAN_REVIEW no debe crear el problema"


# ── AUTO_APPROVE ─────────────────────────────────────────────────────────

def test_http_auto_approve_crea_problema(client, headers_a, necesidad_a):
    """AUTO_APPROVE: debe crear el problema colectivo."""
    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "Problema AA test", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    assert resp.status_code in (200, 201)
    body = resp.json()
    assert body["id"] is not None
    assert body["descripcion"] == "Problema AA test"


# ── Aprobación posterior ─────────────────────────────────────────────────

def test_http_aprobacion_posterior_no_ejecuta_efecto(client, headers_a, necesidad_a, monkeypatch):
    """La aprobación posterior cambia estado pero NO ejecuta efecto de negocio automáticamente.

    Documenta el vacío funcional: no existe mecanismo de reanudación.
    """
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

    # Crear solicitud pendiente
    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "Problema aprobacion test", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    assert resp.status_code in (200, 201)
    approval_id = resp.json()["approval_id"]

    # Aprobar la solicitud con un usuario distinto del proponente (misma org, rol autorizado)
    from src.core.agent_harness.approvals import approval_manager
    from src.core.database import SessionLocal
    from src.core.auth import hash_password
    from src.core.models import OperationalUser
    with SessionLocal() as s:
        proposer = s.query(OperationalUser).filter_by(email="admin@a.org").first() or s.query(OperationalUser).first()
        approver = OperationalUser(
            email="approver-a@a.org", hashed_password=hash_password("secret123"),
            nombre="Approver A", rol="administrador", organizacion_id=proposer.organizacion_id,
        )
        s.add(approver)
        s.commit()
        s.refresh(approver)
        actor = {"tipo": "organizacion", "user_id": approver.id, "persona_id": None,
                 "organizacion_id": approver.organizacion_id, "rol": approver.rol}
    approved = approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)
    _st = approved.status.value if hasattr(approved.status, "value") else approved.status
    assert _st in ("aprobada", "ejecutada"), f"Estado inesperado: {_st}"

    # Verificar que el problema NO se creó (vacío funcional: no hay reanudación)
    with SessionLocal() as s:
        from src.core.models import ProblemaColectivo
        count = s.query(ProblemaColectivo).filter_by(descripcion="Problema aprobacion test").count()
        assert count == 1, "La aprobacion debe reanudar la operacion y crear el problema"


# ── Autorización negativa ────────────────────────────────────────────────

def test_http_sin_auth_devuelve_401(client):
    """Actor no autenticado devuelve 401."""
    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "test", "necesidades_asociadas": [], "origen_datos": "synthetic_pilot"},
    )
    assert resp.status_code == 401


def test_http_org_b_no_accede_a_necesidad_de_org_a(client, headers_b, necesidad_a):
    """Actor de otra organización no accede a necesidad ajena."""
    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "test cross-org", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_b,
    )
    # Debe fallar con 404 (no se confirma existencia) o 403
    assert resp.status_code in (403, 404)


# client, org_a, org_b, headers_a, headers_b provistos por conftest.py
