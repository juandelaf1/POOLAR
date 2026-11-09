"""Matriz HTTP práctica (Fase 0): aislamiento y acciones sobre approvals."""
import os

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.core.agent_harness.approvals import approval_manager  # noqa: E402


def _actor_org(org):
    return {"tipo": "organizacion", "user_id": org.get("user_id"), "persona_id": None, "organizacion_id": org.get("org_id"), "rol": "administrador"}


def test_cross_org_cannot_read_or_manage_approval(client, headers_a, headers_b, org_a, org_b):
    actor_a = _actor_org(org_a)
    req = approval_manager.create("ex-matrix-1", "matrix_tool_noexec", {"x": 1}, proposed_by=org_a["user_id"], reason="r", actor=actor_a)
    # org B no debe ver/gestionar
    r = client.get(f"/approvals/{req.approval_id}", headers=headers_b)
    assert r.status_code in (403, 404), r.text
    r = client.post(f"/approvals/{req.approval_id}/reject", headers=headers_b)
    assert r.status_code in (403, 404, 422), r.text
    # org A puede ver
    r = client.get(f"/approvals/{req.approval_id}", headers=headers_a)
    assert r.status_code == 200, r.text
