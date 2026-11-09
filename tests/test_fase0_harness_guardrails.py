"""Guardrails del harness (fail-closed): validación create/execute."""
import os
import pytest

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.core.agent_harness.approvals import approval_manager  # noqa: E402
from src.core.database import SessionLocal  # noqa: E402
from src.core.models import OperationalUser  # noqa: E402
from src.core.auth import hash_password  # noqa: E402


def _actor(org_id, user_id, rol="administrador"):
    return {"tipo": "organizacion", "user_id": user_id, "persona_id": None, "organizacion_id": org_id, "rol": rol}


def test_create_rejects_invalid_tool_name(org_a):
    actor = _actor(org_a["org_id"], org_a["user_id"])
    with pytest.raises(ValueError):
        approval_manager.create("e1", "", {}, proposed_by=org_a["user_id"], actor=actor)
    with pytest.raises(ValueError):
        approval_manager.create("e2", "   ", {}, proposed_by=org_a["user_id"], actor=actor)


def test_create_rejects_non_dict_inputs(org_a):
    actor = _actor(org_a["org_id"], org_a["user_id"])
    with pytest.raises(ValueError):
        approval_manager.create("e3", "test_tool", "nope", proposed_by=org_a["user_id"], actor=actor)  # type: ignore


def test_missing_handler_fails_closed_not_silent_executed(org_a, db_session):
    """Sin handler registrado, aprobar no debe marcar 'ejecutada' con efecto nulo."""
    actor = _actor(org_a["org_id"], org_a["user_id"])
    req = approval_manager.create("e4", "tool_sin_handler_registrado_xyz", {}, proposed_by=org_a["user_id"], actor=actor)
    approver = OperationalUser(email="gr-approver@a.org", hashed_password=hash_password("secret123"),
                               nombre="A", rol="administrador", organizacion_id=org_a["org_id"])
    db_session.add(approver); db_session.commit(); db_session.refresh(approver)
    aa = _actor(org_a["org_id"], approver.id)
    with pytest.raises(RuntimeError):
        approval_manager.approve(req.approval_id, approved_by=approver.id, actor=aa)
    row = approval_manager.get(req.approval_id)
    status = getattr(row.status, "value", row.status)
    assert status == "fallida_reintentable"
    assert row.executed_at is None
    assert row.approved_by == approver.id


def test_create_rejects_oversized_inputs(org_a):
    actor = _actor(org_a["org_id"], org_a["user_id"])
    with pytest.raises(ValueError):
        approval_manager.create("e5", "test_tool", {"x": "a" * 300000}, proposed_by=org_a["user_id"], actor=actor)


def test_failure_preserves_approver_audit(org_a, db_session):
    """Fallo de ejecución conserva trazabilidad del intento (approved_by)."""
    from src.core.agent_harness import handlers as _h
    tool = "test_audit_fail"
    prev = _h.RESUMABLE_HANDLERS.get(tool)
    _h.RESUMABLE_HANDLERS[tool] = lambda db, inputs: (_ for _ in ()).throw(RuntimeError("boom"))
    try:
        actor = _actor(org_a["org_id"], org_a["user_id"])
        req = approval_manager.create("e6", tool, {}, proposed_by=org_a["user_id"], actor=actor)
        approver = OperationalUser(email="auditfail@a.org", hashed_password=hash_password("secret123"),
                                   nombre="A", rol="administrador", organizacion_id=org_a["org_id"])
        db_session.add(approver); db_session.commit(); db_session.refresh(approver)
        aa = _actor(org_a["org_id"], approver.id)
        with pytest.raises(RuntimeError):
            approval_manager.approve(req.approval_id, approved_by=approver.id, actor=aa)
        row = approval_manager.get(req.approval_id)
        assert getattr(row.status, "value", row.status) == "fallida_reintentable"
        assert row.approved_by == approver.id
    finally:
        if prev is None:
            _h.RESUMABLE_HANDLERS.pop(tool, None)
        else:
            _h.RESUMABLE_HANDLERS[tool] = prev


def test_approval_lifecycle_emits_audit_events(org_a, db_session):
    """Gobernanza: transiciones HITL generan EventoAuditoria (entidad approval_request)."""
    from src.core.agent_harness import handlers as _h
    from src.core.models import EventoAuditoria, ApprovalRequest as AR
    tool = "test_audit_lc"
    prev = _h.RESUMABLE_HANDLERS.get(tool)
    _h.RESUMABLE_HANDLERS[tool] = lambda db, inputs: {"ok": True}
    try:
        actor = _actor(org_a["org_id"], org_a["user_id"])
        req = approval_manager.create("e7", tool, {}, proposed_by=org_a["user_id"], actor=actor)
        approver = OperationalUser(email="auditlc@a.org", hashed_password=hash_password("secret123"),
                                   nombre="A", rol="administrador", organizacion_id=org_a["org_id"])
        db_session.add(approver); db_session.commit(); db_session.refresh(approver)
        aa = _actor(org_a["org_id"], approver.id)
        approval_manager.approve(req.approval_id, approved_by=approver.id, actor=aa)
        with SessionLocal() as s:
            ar = s.query(AR).filter_by(approval_id=req.approval_id).first()
            evs = s.query(EventoAuditoria).filter_by(entidad_referencia="approval_request", entidad_id=ar.id).all()
        tipos = {e.tipo_evento for e in evs}
        assert "inicio" in tipos
        assert "resultado" in tipos
    finally:
        if prev is None:
            _h.RESUMABLE_HANDLERS.pop(tool, None)
        else:
            _h.RESUMABLE_HANDLERS[tool] = prev


def test_reject_emits_audit_event(org_a, db_session):
    from src.core.models import EventoAuditoria, ApprovalRequest as AR
    actor = _actor(org_a["org_id"], org_a["user_id"])
    req = approval_manager.create("e8", "tool_rej_audit", {}, proposed_by=org_a["user_id"], actor=actor)
    approver = OperationalUser(email="auditrej@a.org", hashed_password=hash_password("secret123"),
                               nombre="A", rol="administrador", organizacion_id=org_a["org_id"])
    db_session.add(approver); db_session.commit(); db_session.refresh(approver)
    aa = _actor(org_a["org_id"], approver.id)
    approval_manager.reject(req.approval_id, rejected_by=approver.id, reason="no", actor=aa)
    with SessionLocal() as s:
        ar = s.query(AR).filter_by(approval_id=req.approval_id).first()
        evs = s.query(EventoAuditoria).filter_by(entidad_referencia="approval_request", entidad_id=ar.id).all()
    assert any(e.tipo_evento == "cambio_estado" for e in evs)
