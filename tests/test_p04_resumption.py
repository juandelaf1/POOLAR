"""P0.4 — Pruebas HTTP reales de reanudación de operaciones aprobadas.

Solo cubre create_problema_colectivo en esta iteración.
"""
import os
import pytest

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.main import app
from src.core.ports import AutomationRoute, automation_evaluator


@pytest.fixture
def necesidad_a(client, headers_a):
    resp = client.post("/necesidades", params={"titulo": "Necesidad test", "descripcion": "descripcion suficiente", "visibilidad": "privada"}, headers=headers_a)
    assert resp.status_code == 201
    return resp.json()["id"]


def test_resumption_creates_problem_after_approval(client, headers_a, necesidad_a, monkeypatch):
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
        json={"descripcion": "Problema resumption test", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    assert resp.status_code in (200, 201)
    approval_id = resp.json()["approval_id"]

    # Aun no debe existir el problema
    from src.core.database import SessionLocal
    from src.core.models import ProblemaColectivo
    with SessionLocal() as s:
        assert s.query(ProblemaColectivo).filter_by(descripcion="Problema resumption test").count() == 0

    # Aprobar (dispara reanudacion) con usuario autorizado distinto del proponente
    from src.core.agent_harness.approvals import approval_manager
    from src.core.models import OperationalUser
    from src.core.auth import hash_password
    with SessionLocal() as s:
        proposer = s.query(OperationalUser).filter_by(organizacion_id=1).first() or s.query(OperationalUser).first()
        approver = OperationalUser(email="approver-resume@a.org", hashed_password=hash_password("secret123"), nombre="Approver", rol="administrador", organizacion_id=proposer.organizacion_id)
        s.add(approver); s.commit(); s.refresh(approver)
        actor = {"tipo": "organizacion", "user_id": approver.id, "persona_id": None, "organizacion_id": approver.organizacion_id, "rol": approver.rol}
    approved = approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)
    st = approved.status.value if hasattr(approved.status, "value") else approved.status
    assert st in ("aprobada", "ejecutada")

    # Ahora debe existir el problema
    with SessionLocal() as s:
        from src.core.models import ProblemaColectivo
        count = s.query(ProblemaColectivo).filter_by(descripcion="Problema resumption test").count()
        assert count == 1, "La aprobacion debe reanudar y crear el problema"

    # Consultar via HTTP
    r = client.get(f"/approvals/{approval_id}", headers=headers_a)
    assert r.status_code == 200
    assert r.json()["executed_at"] is not None


def test_resumption_reject_does_not_execute(client, headers_a, necesidad_a, monkeypatch):
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
        json={"descripcion": "Problema reject test", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    approval_id = resp.json()["approval_id"]

    from src.core.agent_harness.approvals import approval_manager
    from src.core.database import SessionLocal
    from src.core.models import OperationalUser
    from src.core.auth import hash_password
    with SessionLocal() as s:
        proposer = s.query(OperationalUser).filter_by(organizacion_id=1).first() or s.query(OperationalUser).first()
        rejector = OperationalUser(email="rejector-resume2@a.org", hashed_password=hash_password("secret123"), nombre="Rejector", rol="administrador", organizacion_id=proposer.organizacion_id)
        s.add(rejector); s.commit(); s.refresh(rejector)
        actor = {"tipo": "organizacion", "user_id": rejector.id, "persona_id": None, "organizacion_id": rejector.organizacion_id, "rol": rejector.rol}
    approval_manager.reject(approval_id, rejected_by=rejector.id, reason="no", actor=actor)

    # No debe ejecutarse
    r = client.get(f"/approvals/{approval_id}", headers=headers_a)
    assert r.json()["status"] == "rechazada"
    assert r.json()["executed_at"] is None

    from src.core.models import ProblemaColectivo
    with SessionLocal() as s:
        assert s.query(ProblemaColectivo).filter_by(descripcion="Problema reject test").count() == 0


def test_resumption_repeat_approval_idempotent(client, headers_a, necesidad_a, monkeypatch):
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
        json={"descripcion": "Problema idempotent test", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    approval_id = resp.json()["approval_id"]

    from src.core.agent_harness.approvals import approval_manager
    from src.core.database import SessionLocal
    from src.core.models import OperationalUser
    from src.core.auth import hash_password
    with SessionLocal() as s:
        proposer = s.query(OperationalUser).filter_by(organizacion_id=1).first() or s.query(OperationalUser).first()
        approver = OperationalUser(email="approver-idem@a.org", hashed_password=hash_password("secret123"), nombre="Approver", rol="administrador", organizacion_id=proposer.organizacion_id)
        s.add(approver); s.commit(); s.refresh(approver)
        actor = {"tipo": "organizacion", "user_id": approver.id, "persona_id": None, "organizacion_id": approver.organizacion_id, "rol": approver.rol}
    approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)

    # Segunda aprobación: idempotente o error, pero sin duplicar efecto
    try:
        approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)
    except (ValueError, Exception):
        pass

    # Solo un problema creado
    with SessionLocal() as s:
        from src.core.models import ProblemaColectivo
        assert s.query(ProblemaColectivo).filter_by(descripcion="Problema idempotent test").count() == 1
