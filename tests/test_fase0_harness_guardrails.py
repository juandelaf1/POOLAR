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
