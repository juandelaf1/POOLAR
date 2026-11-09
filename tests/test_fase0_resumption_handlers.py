"""Fase 0 (F0-09): reanudación tras aprobación para handlers registrados.

Cubre operaciones adicionales a create_problema_colectivo (SQLite).
"""
import os

import pytest

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.core.ports import AutomationRoute  # noqa: E402
from src.core.database import SessionLocal  # noqa: E402
from src.core.models import OperationalUser, ProblemaColectivo  # noqa: E402
from src.core.auth import hash_password  # noqa: E402
from src.core.agent_harness.approvals import approval_manager  # noqa: E402


@pytest.fixture
def necesidad_a(client, headers_a):
    resp = client.post(
        "/necesidades",
        params={"titulo": "N", "descripcion": "d", "visibilidad": "privada"},
        headers=headers_a,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _approver_actor_same_org(proposer_email="admin@a.org", approver_email="approver-h@a.org"):
    with SessionLocal() as s:
        proposer = s.query(OperationalUser).filter_by(email=proposer_email).first()
        if proposer is None:
            proposer = s.query(OperationalUser).first()
        approver = OperationalUser(
            email=approver_email, hashed_password=hash_password("secret123"),
            nombre="Approver", rol="administrador", organizacion_id=proposer.organizacion_id,
        )
        s.add(approver); s.commit(); s.refresh(approver)
        return approver, {"tipo": "organizacion", "user_id": approver.id, "persona_id": None,
                          "organizacion_id": approver.organizacion_id, "rol": approver.rol}


def test_resumption_cambiar_estado_problema(client, headers_a, necesidad_a, monkeypatch):
    # Crear problema (auto-approve normal)
    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "Problema colectivo para cambio estado", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    assert resp.status_code in (200, 201), resp.text
    problema_id = resp.json()["id"]

    def fake_review(proposal, context):
        return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                "approved": False, "requires_human_review": True, "rejected": False}

    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    r2 = client.post(f"/problemas-colectivos/{problema_id}/estado", json={"estado": "en_analisis"}, headers=headers_a)
    assert r2.status_code in (200, 201), r2.text
    body = r2.json()
    assert body["status"] == "pending_review"
    approval_id = body["approval_id"]

    approver, actor = _approver_actor_same_org(approver_email="approver-estado@a.org")
    approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)

    with SessionLocal() as s:
        p = s.get(ProblemaColectivo, problema_id)
        assert p is not None
        assert p.estado == "en_analisis"


def test_reject_create_iniciativa_no_effect(client, headers_a, necesidad_a, monkeypatch, org_a):
    from src.core.models import Iniciativa

    def fake_review(proposal, context):
        if proposal.get("action") == "create_iniciativa":
            return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                    "approved": False, "requires_human_review": True, "rejected": False}
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [],
                "approved": True, "requires_human_review": False, "rejected": False}

    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    resp = client.post(
        "/iniciativas",
        params={"necesidad_id": necesidad_a, "responsable_id": org_a["org_id"],
                "criterios_decision": "criterio valido suficiente", "titulo": "Ini rechazada"},
        headers=headers_a,
    )
    assert resp.json()["status"] == "pending_review"
    approval_id = resp.json()["approval_id"]
    approver, actor = _approver_actor_same_org(approver_email="rejector-ini@a.org")
    approval_manager.reject(approval_id, rejected_by=approver.id, reason="no", actor=actor)
    with SessionLocal() as s:
        assert s.query(Iniciativa).filter_by(titulo="Ini rechazada").count() == 0


def test_reject_create_decision_no_effect(client, headers_a, necesidad_a, monkeypatch, org_a):
    from src.core.models import Decision

    resp_i = client.post(
        "/iniciativas",
        params={"necesidad_id": necesidad_a, "responsable_id": org_a["org_id"],
                "criterios_decision": "criterio valido suficiente", "titulo": "Ini rej dec"},
        headers=headers_a,
    )
    iniciativa_id = resp_i.json()["id"]

    def fake_review(proposal, context):
        if proposal.get("action") == "create_decision":
            return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                    "approved": False, "requires_human_review": True, "rejected": False}
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [],
                "approved": True, "requires_human_review": False, "rejected": False}

    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    resp = client.post(
        "/decisiones",
        params={"iniciativa_id": iniciativa_id, "tipo_decision": "aprobar", "alternativa_elegida": "x",
                "motivo": "motivo suficiente", "responsable_decision": org_a["user_id"], "version_metodologia": "v1"},
        headers=headers_a,
    )
    approval_id = resp.json()["approval_id"]
    approver, actor = _approver_actor_same_org(approver_email="rejector-dec@a.org")
    approval_manager.reject(approval_id, rejected_by=approver.id, reason="no", actor=actor)
    with SessionLocal() as s:
        assert s.query(Decision).filter_by(iniciativa_id=iniciativa_id).count() == 0


def test_idempotent_cambiar_estado_no_duplicate(client, headers_a, necesidad_a, monkeypatch, org_a):
    from src.core.models import ProblemaColectivo
    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "Problema colectivo para idempotencia estado", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    problema_id = resp.json()["id"]

    def fake_review(proposal, context):
        if proposal.get("action") == "cambiar_estado_problema_colectivo":
            return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                    "approved": False, "requires_human_review": True, "rejected": False}
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [],
                "approved": True, "requires_human_review": False, "rejected": False}

    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    r2 = client.post(f"/problemas-colectivos/{problema_id}/estado", json={"estado": "en_analisis"}, headers=headers_a)
    approval_id = r2.json()["approval_id"]
    approver, actor = _approver_actor_same_org(approver_email="approver-idem-estado@a.org")
    approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)
    approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)  # idempotente
    with SessionLocal() as s:
        p = s.get(ProblemaColectivo, problema_id)
        assert p.estado == "en_analisis"


def test_reject_cambiar_estado_no_effect(client, headers_a, necesidad_a, monkeypatch):
    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "Problema colectivo para rechazo estado", "necesidades_asociadas": [necesidad_a], "origen_datos": "synthetic_pilot"},
        headers=headers_a,
    )
    problema_id = resp.json()["id"]

    def fake_review(proposal, context):
        if proposal.get("action") == "cambiar_estado_problema_colectivo":
            return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                    "approved": False, "requires_human_review": True, "rejected": False}
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [],
                "approved": True, "requires_human_review": False, "rejected": False}

    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    r2 = client.post(f"/problemas-colectivos/{problema_id}/estado", json={"estado": "en_analisis"}, headers=headers_a)
    approval_id = r2.json()["approval_id"]
    approver, actor = _approver_actor_same_org(approver_email="rejector-estado@a.org")
    approval_manager.reject(approval_id, rejected_by=approver.id, reason="no", actor=actor)
    with SessionLocal() as s:
        p = s.get(ProblemaColectivo, problema_id)
        assert p.estado == "detectado"


def test_reject_create_decision_for_initiative_no_effect(client, headers_a, necesidad_a, monkeypatch):
    from src.core.models import Decision, Organizacion
    with SessionLocal() as s:
        org_id = s.query(Organizacion).first().id
    resp_i = client.post(
        "/iniciativas",
        params={"necesidad_id": necesidad_a, "responsable_id": org_id,
                "criterios_decision": "criterio valido suficiente", "titulo": "Ini rej dec2"},
        headers=headers_a,
    )
    iniciativa_id = resp_i.json()["id"]

    def fake_review(proposal, context):
        if proposal.get("action") == "create_decision_for_initiative":
            return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                    "approved": False, "requires_human_review": True, "rejected": False}
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [],
                "approved": True, "requires_human_review": False, "rejected": False}

    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    resp = client.post(f"/iniciativas/{iniciativa_id}/decisiones",
                       params={"tipo_decision": "aprobar", "alternativa_elegida": "x", "motivo": "motivo suficiente", "version_metodologia": "v1"},
                       headers=headers_a)
    approval_id = resp.json()["approval_id"]
    approver, actor = _approver_actor_same_org(approver_email="rejector-dec2@a.org")
    approval_manager.reject(approval_id, rejected_by=approver.id, reason="no", actor=actor)
    with SessionLocal() as s:
        assert s.query(Decision).filter_by(iniciativa_id=iniciativa_id).count() == 0


def test_resumption_create_iniciativa(client, headers_a, necesidad_a, monkeypatch, org_a):
    from src.core.models import Iniciativa

    def fake_review(proposal, context):
        return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                "approved": False, "requires_human_review": True, "rejected": False}

    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    resp = client.post(
        "/iniciativas",
        params={
            "necesidad_id": necesidad_a,
            "responsable_id": org_a["org_id"],
            "criterios_decision": "criterio valido suficiente",
            "titulo": "Iniciativa HR",
            "descripcion": "desc",
        },
        headers=headers_a,
    )
    assert resp.status_code in (200, 201), resp.text
    body = resp.json()
    assert body["status"] == "pending_review"
    approval_id = body["approval_id"]

    approver, actor = _approver_actor_same_org(approver_email="approver-ini@a.org")
    approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)

    with SessionLocal() as s:
        assert s.query(Iniciativa).filter_by(titulo="Iniciativa HR").count() == 1


def test_resumption_create_decision(client, headers_a, necesidad_a, monkeypatch, org_a):
    from src.core.models import Decision

    # Crear iniciativa (auto-approve)
    resp_i = client.post(
        "/iniciativas",
        params={
            "necesidad_id": necesidad_a,
            "responsable_id": org_a["org_id"],
            "criterios_decision": "criterio valido suficiente",
            "titulo": "Ini para decision",
        },
        headers=headers_a,
    )
    assert resp_i.status_code in (200, 201), resp_i.text
    iniciativa_id = resp_i.json()["id"]

    def fake_review(proposal, context):
        if proposal.get("action") == "create_decision":
            return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                    "approved": False, "requires_human_review": True, "rejected": False}
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [],
                "approved": True, "requires_human_review": False, "rejected": False}

    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    resp = client.post(
        "/decisiones",
        params={
            "iniciativa_id": iniciativa_id,
            "tipo_decision": "aprobar",
            "alternativa_elegida": "alt1",
            "motivo": "motivo suficiente",
            "responsable_decision": org_a["user_id"],
            "version_metodologia": "v1",
        },
        headers=headers_a,
    )
    assert resp.status_code in (200, 201), resp.text
    body = resp.json()
    assert body["status"] == "pending_review"
    approval_id = body["approval_id"]

    approver, actor = _approver_actor_same_org(approver_email="approver-dec@a.org")
    approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)

    with SessionLocal() as s:
        assert s.query(Decision).filter_by(iniciativa_id=iniciativa_id).count() == 1


def test_resumption_create_decision_for_initiative(client, headers_a, necesidad_a, monkeypatch, org_a):
    from src.core.models import Decision

    resp_i = client.post(
        "/iniciativas",
        params={
            "necesidad_id": necesidad_a,
            "responsable_id": org_a["org_id"],
            "criterios_decision": "criterio valido suficiente",
            "titulo": "Ini para decision2",
        },
        headers=headers_a,
    )
    assert resp_i.status_code in (200, 201), resp_i.text
    iniciativa_id = resp_i.json()["id"]

    def fake_review(proposal, context):
        if proposal.get("action") == "create_decision_for_initiative":
            return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                    "approved": False, "requires_human_review": True, "rejected": False}
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [],
                "approved": True, "requires_human_review": False, "rejected": False}

    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    resp = client.post(
        f"/iniciativas/{iniciativa_id}/decisiones",
        params={
            "tipo_decision": "aprobar",
            "alternativa_elegida": "alt2",
            "motivo": "motivo suficiente",
            "version_metodologia": "v1",
        },
        headers=headers_a,
    )
    assert resp.status_code in (200, 201), resp.text
    body = resp.json()
    assert body["status"] == "pending_review"
    approval_id = body["approval_id"]

    approver, actor = _approver_actor_same_org(approver_email="approver-dec2@a.org")
    approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)

    with SessionLocal() as s:
        assert s.query(Decision).filter_by(iniciativa_id=iniciativa_id).count() == 1


def test_handler_failure_no_partial_effect_and_marks_failed(org_a, db_session):
    """F0-06/F0-09: fallo en handler => rollback del efecto, estado failed_retryable."""
    from src.core.agent_harness import handlers as _h
    from src.core.models import EventoAuditoria

    tool = "test_fail_atomic"
    marker = "marker_fail_atomic_xyz"

    def failing_handler(db, inputs):
        db.add(EventoAuditoria(entidad_referencia="test", entidad_id=1, tipo_evento="inicio", justificacion=marker))
        db.flush()
        raise RuntimeError("boom")

    prev = _h.RESUMABLE_HANDLERS.get(tool)
    _h.RESUMABLE_HANDLERS[tool] = failing_handler
    try:
        actor = {"tipo": "organizacion", "user_id": org_a["user_id"], "persona_id": None,
                 "organizacion_id": org_a["org_id"], "rol": "administrador"}
        req = approval_manager.create("exec-fail", tool, {"x": 1}, proposed_by=org_a["user_id"], actor=actor)
        approver = OperationalUser(email="approver-fail@a.org", hashed_password=hash_password("secret123"),
                                   nombre="Approver", rol="administrador", organizacion_id=org_a["org_id"])
        db_session.add(approver); db_session.commit(); db_session.refresh(approver)
        approver_actor = {"tipo": "organizacion", "user_id": approver.id, "persona_id": None,
                          "organizacion_id": org_a["org_id"], "rol": "administrador"}
        with pytest.raises(RuntimeError):
            approval_manager.approve(req.approval_id, approved_by=approver.id, actor=approver_actor)

        with SessionLocal() as s:
            assert s.query(EventoAuditoria).filter_by(justificacion=marker).count() == 0
            row = approval_manager.get(req.approval_id)  # no actor: legacy read ok; or use actor
            assert row is not None
            assert row.status == "fallida_reintentable"
            assert row.executed_at is None
            assert "boom" in (row.execution_error or "")
    finally:
        if prev is None:
            _h.RESUMABLE_HANDLERS.pop(tool, None)
        else:
            _h.RESUMABLE_HANDLERS[tool] = prev


def test_retry_failed_retryable_succeeds(org_a, db_session):
    """F0-06: reintento tras fallida_reintentable ejecuta sin duplicar."""
    from src.core.agent_harness import handlers as _h
    from src.core.models import EventoAuditoria

    tool = "test_retry_ok"
    marker = "marker_retry_ok"
    state = {"fail": True}

    def flaky(db, inputs):
        if state["fail"]:
            raise RuntimeError("transient")
        db.add(EventoAuditoria(entidad_referencia="test", entidad_id=1, tipo_evento="inicio", justificacion=marker))
        db.flush()
        return {"ok": True}

    prev = _h.RESUMABLE_HANDLERS.get(tool)
    _h.RESUMABLE_HANDLERS[tool] = flaky
    try:
        actor = {"tipo": "organizacion", "user_id": org_a["user_id"], "persona_id": None,
                 "organizacion_id": org_a["org_id"], "rol": "administrador"}
        req = approval_manager.create("exec-retry", tool, {}, proposed_by=org_a["user_id"], actor=actor)
        approver = OperationalUser(email="approver-retry@a.org", hashed_password=hash_password("secret123"),
                                   nombre="Approver", rol="administrador", organizacion_id=org_a["org_id"])
        db_session.add(approver); db_session.commit(); db_session.refresh(approver)
        aa = {"tipo": "organizacion", "user_id": approver.id, "persona_id": None,
              "organizacion_id": org_a["org_id"], "rol": "administrador"}
        with pytest.raises(RuntimeError):
            approval_manager.approve(req.approval_id, approved_by=approver.id, actor=aa)
        state["fail"] = False
        result = approval_manager.approve(req.approval_id, approved_by=approver.id, actor=aa)
        assert result.status == "ejecutada"
        with SessionLocal() as s:
            assert s.query(EventoAuditoria).filter_by(justificacion=marker).count() == 1
    finally:
        if prev is None:
            _h.RESUMABLE_HANDLERS.pop(tool, None)
        else:
            _h.RESUMABLE_HANDLERS[tool] = prev


def test_executed_approval_idempotent_no_duplicate(client, headers_a, necesidad_a, monkeypatch, org_a):
    """F0-09: aprobar de nuevo una solicitud ejecutada no duplica efecto."""
    from src.core.models import Iniciativa

    def fake_review(proposal, context):
        if proposal.get("action") == "create_iniciativa":
            return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                    "approved": False, "requires_human_review": True, "rejected": False}
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [],
                "approved": True, "requires_human_review": False, "rejected": False}

    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    resp = client.post(
        "/iniciativas",
        params={"necesidad_id": necesidad_a, "responsable_id": org_a["org_id"],
                "criterios_decision": "criterio valido suficiente", "titulo": "Ini idem"},
        headers=headers_a,
    )
    approval_id = resp.json()["approval_id"]
    approver, actor = _approver_actor_same_org(approver_email="approver-idem2@a.org")
    approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)
    # segunda llamada idempotente
    approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)
    with SessionLocal() as s:
        assert s.query(Iniciativa).filter_by(titulo="Ini idem").count() == 1


def test_cannot_approve_rejected_request(client, headers_a, necesidad_a, monkeypatch, org_a):
    """F0-09: solicitud rechazada no puede aprobarse."""
    def fake_review(proposal, context):
        if proposal.get("action") == "create_iniciativa":
            return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                    "approved": False, "requires_human_review": True, "rejected": False}
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [],
                "approved": True, "requires_human_review": False, "rejected": False}
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    resp = client.post("/iniciativas", params={"necesidad_id": necesidad_a, "responsable_id": org_a["org_id"],
            "criterios_decision": "criterio valido suficiente", "titulo": "Ini rej2"}, headers=headers_a)
    approval_id = resp.json()["approval_id"]
    approver, actor = _approver_actor_same_org(approver_email="approver-rejstate@a.org")
    approval_manager.reject(approval_id, rejected_by=approver.id, reason="no", actor=actor)
    with pytest.raises(Exception):
        approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)


def test_cannot_reject_executed_request(client, headers_a, necesidad_a, monkeypatch, org_a):
    """F0-09: solicitud ejecutada no puede rechazarse."""
    def fake_review(proposal, context):
        if proposal.get("action") == "create_iniciativa":
            return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "medium", "reasons": ["t"],
                    "approved": False, "requires_human_review": True, "rejected": False}
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [],
                "approved": True, "requires_human_review": False, "rejected": False}
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_review)
    resp = client.post("/iniciativas", params={"necesidad_id": necesidad_a, "responsable_id": org_a["org_id"],
            "criterios_decision": "criterio valido suficiente", "titulo": "Ini exec-rej"}, headers=headers_a)
    approval_id = resp.json()["approval_id"]
    approver, actor = _approver_actor_same_org(approver_email="approver-execrej@a.org")
    approval_manager.approve(approval_id, approved_by=approver.id, actor=actor)
    with pytest.raises(Exception):
        approval_manager.reject(approval_id, rejected_by=approver.id, reason="tarde", actor=actor)


def test_can_reject_failed_retryable(org_a, db_session):
    """F0-09: fallida_reintentable puede cerrarse por rechazo autorizado (sin ejecución)."""
    from src.core.agent_harness import handlers as _h
    tool = "test_reject_retryable"
    prev = _h.RESUMABLE_HANDLERS.get(tool)
    _h.RESUMABLE_HANDLERS[tool] = lambda db, inputs: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        actor = {"tipo": "organizacion", "user_id": org_a["user_id"], "persona_id": None,
                 "organizacion_id": org_a["org_id"], "rol": "administrador"}
        req = approval_manager.create("exec-rej-retry", tool, {}, proposed_by=org_a["user_id"], actor=actor)
        approver = OperationalUser(email="approver-rejretry@a.org", hashed_password=hash_password("secret123"),
                                   nombre="Approver", rol="administrador", organizacion_id=org_a["org_id"])
        db_session.add(approver); db_session.commit(); db_session.refresh(approver)
        aa = {"tipo": "organizacion", "user_id": approver.id, "persona_id": None,
              "organizacion_id": org_a["org_id"], "rol": "administrador"}
        with pytest.raises(RuntimeError):
            approval_manager.approve(req.approval_id, approved_by=approver.id, actor=aa)
        row = approval_manager.get(req.approval_id)
        assert row.status == "fallida_reintentable"
        rej = approval_manager.reject(req.approval_id, rejected_by=approver.id, reason="no reintentar", actor=aa)
        assert getattr(rej.status, "value", rej.status) == "rechazada"
    finally:
        if prev is None:
            _h.RESUMABLE_HANDLERS.pop(tool, None)
        else:
            _h.RESUMABLE_HANDLERS[tool] = prev


@pytest.mark.parametrize("tool_name", [
    "create_problema_colectivo",
    "create_iniciativa",
    "create_decision",
    "create_decision_for_initiative",
    "cambiar_estado_problema_colectivo",
])
def test_failure_then_retry_semantics_per_resumable_tool(client, org_a, db_session, tool_name):
    """F0-09: por cada tool reanudable registrada, fallo => fallida_reintentable + executed_at null; reintento OK."""
    from src.core.agent_harness import handlers as _h
    if tool_name not in _h.RESUMABLE_HANDLERS:
        pytest.skip(f"handler {tool_name} no registrado")
    prev = _h.RESUMABLE_HANDLERS[tool_name]
    state = {"fail": True}

    def flaky(db, inputs):
        if state["fail"]:
            raise RuntimeError(f"fallo inyectado {tool_name}")
        return {"ok": True, "tool": tool_name}

    _h.RESUMABLE_HANDLERS[tool_name] = flaky
    try:
        actor = {"tipo": "organizacion", "user_id": org_a["user_id"], "persona_id": None,
                 "organizacion_id": org_a["org_id"], "rol": "administrador"}
        req = approval_manager.create(f"exec-{tool_name}", tool_name, {"synthetic_pilot": True}, proposed_by=org_a["user_id"], actor=actor)
        approver = OperationalUser(email=f"retry-{tool_name[:20]}@a.org", hashed_password=hash_password("secret123"),
                                   nombre="Approver", rol="administrador", organizacion_id=org_a["org_id"])
        db_session.add(approver); db_session.commit(); db_session.refresh(approver)
        aa = {"tipo": "organizacion", "user_id": approver.id, "persona_id": None,
              "organizacion_id": org_a["org_id"], "rol": "administrador"}
        with pytest.raises(RuntimeError):
            approval_manager.approve(req.approval_id, approved_by=approver.id, actor=aa)
        row = approval_manager.get(req.approval_id)
        assert row.status == "fallida_reintentable"
        assert row.executed_at is None
        state["fail"] = False
        row2 = approval_manager.approve(req.approval_id, approved_by=approver.id, actor=aa)
        assert getattr(row2.status, "value", row2.status) == "ejecutada"
    finally:
        _h.RESUMABLE_HANDLERS[tool_name] = prev
