"""F0-04: matriz explícita de roles (gestión HITL en misma org, ámbito aislado)."""
import os
import pytest

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.core.agent_harness.approvals import approval_manager  # noqa: E402
from src.core.database import SessionLocal  # noqa: E402
from src.core.models import OperationalUser  # noqa: E402
from src.core.auth import hash_password  # noqa: E402


def _mk(org_id, user_id, rol, tipo="organizacion"):
    return {"tipo": tipo, "user_id": user_id, "persona_id": None, "organizacion_id": org_id, "rol": rol}


def test_role_matrix_same_org(db_session, org_a):
    proposer = org_a["user_id"]
    org = org_a["org_id"]
    actor_proposer = _mk(org, proposer, "administrador")
    req = approval_manager.create("exec-rm", "test_tool", {}, proposed_by=proposer, actor=actor_proposer)

    allowed = ["coordinador", "gestor", "responsable", "aprobador", "administrador", "admin", "owner"]
    denied = ["miembro", "observador", "viewer"]

    uid = 90000
    for rol in allowed:
        uid += 1
        aa = _mk(org, uid, rol)
        # lectura en scope + capacidad de gestionar (aprobación probada en otros tests)
        got = approval_manager.get(req.approval_id, actor=aa)
        assert got.approval_id == req.approval_id

    req2 = approval_manager.create("exec-rm2", "test_tool", {}, proposed_by=proposer, actor=actor_proposer)
    for rol in denied:
        uid += 1
        aa = _mk(org, uid, rol)
        # lectura en scope permitida; gestión/aprobación denegada
        got = approval_manager.get(req2.approval_id, actor=aa)
        assert got.approval_id == req2.approval_id
        with pytest.raises(Exception):
            approval_manager.approve(req2.approval_id, approved_by=uid, actor=aa)
        with pytest.raises(Exception):
            approval_manager.reject(req2.approval_id, rejected_by=uid, reason="x", actor=aa)
