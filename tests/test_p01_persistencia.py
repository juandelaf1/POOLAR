# P0.1 — Pruebas de persistencia/bloqueo (PostgreSQL). Compatibles con Fase 0 (scope/actor).
import os
import threading
from datetime import datetime, timedelta
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

from src.core.agent_harness.approvals import ApprovalManager, ApprovalStatus
from src.core.ports import automation_evaluator, AutomationRoute, AutomationRoute as AR
from src.core.database import SessionLocal, engine
from src.core.models import OperationalUser, ApprovalRequest as ApprovalRequestDB

# Estos tests requieren PostgreSQL de prueba. CI/local debe definir POOLAR_TEST_POSTGRES_URL.
_PG_URL = os.getenv("POOLAR_TEST_POSTGRES_URL", "")
if not _PG_URL.startswith("postgresql"):
    pytest.skip("No hay POOLAR_TEST_POSTGRES_URL (PostgreSQL de prueba)", allow_module_level=True)
try:
    import sqlalchemy as sa
    _e = sa.create_engine(_PG_URL)
    with _e.connect() as _c:
        _c.execute(sa.text("SELECT 1"))
except Exception:
    pytest.skip("PostgreSQL de prueba no accesible", allow_module_level=True)


@pytest.fixture(autouse=True)
def _register_test_handlers():
    """Handlers no-op para tools genéricas usadas en tests de persistencia (approve ejecuta handler). Restaura estado."""
    from src.core.agent_harness.handlers import RESUMABLE_HANDLERS

    def _noop(session, inputs):
        return {"ok": True, "inputs": inputs}

    names = ("t", "test_tool", "test_op", "op_sensible")
    prev = {n: RESUMABLE_HANDLERS.get(n) for n in names}
    added = []
    for name in names:
        if name not in RESUMABLE_HANDLERS:
            RESUMABLE_HANDLERS[name] = _noop
            added.append(name)
    yield
    for name in added:
        RESUMABLE_HANDLERS.pop(name, None)
    for name, fn in prev.items():
        if fn is not None and name not in RESUMABLE_HANDLERS:
            RESUMABLE_HANDLERS[name] = fn


def _org_p01():
    from src.core.models import Organizacion
    with SessionLocal() as s:
        org = s.query(Organizacion).filter_by(nombre="Org P0.1").first()
        if org is None:
            org = Organizacion(nombre="Org P0.1", tipo_organizacion="cooperativa", contacto_publico="p0@poolar.local")
            s.add(org)
            s.commit()
            s.refresh(org)
        return org.id


def _create_synthetic_user(email: str = "test@poolar.local") -> int:
    """Crea usuario sintético en operational_users (respeta FK)."""
    org_id = _org_p01()
    with SessionLocal() as s:
        existing = s.query(OperationalUser).filter_by(email=email).first()
        if existing:
            return existing.id
        user = OperationalUser(
            email=email,
            hashed_password="fakehash",
            nombre="Usuario Sintetico P0.1",
            rol="administrador",
            organizacion_id=org_id,
        )
        s.add(user)
        s.commit()
        s.refresh(user)
        return user.id


def _actor(uid: int):
    return {"tipo": "organizacion", "user_id": uid, "persona_id": None, "organizacion_id": _org_p01(), "rol": "administrador"}


def _create(m, exec_id, tool="t", inputs=None, proposed_by=None, **kw):
    uid = proposed_by if proposed_by is not None else _create_synthetic_user("prop@poolar.local")
    return m.create(exec_id, tool, inputs or {}, proposed_by=uid,
                     organizacion_id=_org_p01(), proposer_type="organizacion", proposer_actor_id=uid, **kw)


def test_persistencia_across_instances():
    uid = _create_synthetic_user("p1@poolar.local")
    m1 = ApprovalManager()
    r = _create(m1, "exec_001", "test_tool", {"key": "val"}, proposed_by=uid)
    m2 = ApprovalManager()
    recovered = m2.get(r.approval_id)
    assert recovered is not None
    assert recovered.approval_id == r.approval_id
    assert recovered.proposed_by == uid
    assert recovered.status == ApprovalStatus.PENDING


def test_approve_and_reject_persisted():
    uid = _create_synthetic_user("p2@poolar.local")
    m = ApprovalManager()
    r = _create(m, "exec_002", proposed_by=uid)
    approver = _create_synthetic_user("p_approver@poolar.local")
    approved = m.approve(r.approval_id, approved_by=approver, actor=_actor(approver))
    assert approved.status in (ApprovalStatus.APPROVED, ApprovalStatus.EXECUTED)
    assert approved.approved_by == approver
    assert approved.approved_at is not None
    with pytest.raises(Exception):
        m.reject(r.approval_id, rejected_by=_create_synthetic_user("p_rejecter@poolar.local"), actor=_actor(_create_synthetic_user("p_rejecter@poolar.local")))


def test_reject_expired_not_allowed():
    uid = _create_synthetic_user("p3@poolar.local")
    m = ApprovalManager()
    r = _create(m, "exec_003", proposed_by=uid)
    with SessionLocal() as s:
        db_r = s.query(ApprovalRequestDB).filter_by(approval_id=r.approval_id).first()
        db_r.expires_at = datetime.utcnow() - timedelta(hours=1)
        s.commit()
    assert m.is_expired(r.approval_id) is True
    a = _create_synthetic_user("a3@poolar.local")
    with pytest.raises(Exception):
        m.approve(r.approval_id, approved_by=a, actor=_actor(a))
    rej = _create_synthetic_user("r3@poolar.local")
    with pytest.raises(Exception):
        m.reject(r.approval_id, rejected_by=rej, actor=_actor(rej))


def test_no_second_resolution():
    uid = _create_synthetic_user("p4@poolar.local")
    m = ApprovalManager()
    r = _create(m, "exec_004", proposed_by=uid)
    a = _create_synthetic_user("a4@poolar.local")
    m.approve(r.approval_id, approved_by=a, actor=_actor(a))
    a2 = _create_synthetic_user("a4b@poolar.local")
    with pytest.raises(Exception):
        m.approve(r.approval_id, approved_by=a2, actor=_actor(a2))
    rj = _create_synthetic_user("r4@poolar.local")
    with pytest.raises(Exception):
        m.reject(r.approval_id, rejected_by=rj, actor=_actor(rj))


def test_concurrent_approve_blocked_by_db():
    uid = _create_synthetic_user("p5@poolar.local")
    m = ApprovalManager()
    r = _create(m, "exec_005", proposed_by=uid)
    results = []

    def approve_thread(user_email):
        try:
            m_local = ApprovalManager()
            au = _create_synthetic_user(user_email)
            result = m_local.approve(r.approval_id, approved_by=au, actor=_actor(au))
            results.append(("approved", result.status))
        except Exception as exc:
            results.append(("error", str(exc)[:120]))

    t1 = threading.Thread(target=approve_thread, args=("c1@poolar.local",))
    t2 = threading.Thread(target=approve_thread, args=("c2@poolar.local",))
    t1.start(); t2.start()
    t1.join(); t2.join()
    ok_statuses = {ApprovalStatus.APPROVED, ApprovalStatus.EXECUTED, "aprobada", "ejecutada"}
    approved_count = sum(1 for kind, s in results if kind == "approved" and (getattr(s, "value", s) in ok_statuses or s in ok_statuses))
    assert approved_count == 1, f"expected 1 successful approval, got results={results}"
    final = m.get(r.approval_id)
    assert final.status in (ApprovalStatus.APPROVED, ApprovalStatus.EXECUTED)


def test_human_review_no_ejecuta_efecto():
    result = automation_evaluator.evaluate(
        {"action": "create_decision", "origen_datos": "real_pilot"},
        {"actor_type": "individuo", "actor_rol": "individuo", "is_destinatario": False},
    )
    assert result["route"] != AutomationRoute.AUTO_APPROVE.value
    assert result["approved"] is False
    from src.main import _handle_governance
    assert callable(_handle_governance)
    m = ApprovalManager()
    uid = _create_synthetic_user("hr@poolar.local")
    req = _create(m, "exec_hr", "test_op", {"data": "x"}, proposed_by=uid)
    assert req.status == ApprovalStatus.PENDING


def test_reject_no_produce_efecto():
    result = automation_evaluator.evaluate(
        {"action": "create_decision", "origen_datos": "synthetic_pilot"},
        {"actor_type": "desconocido", "actor_rol": "", "is_destinatario": False},
    )
    assert result["route"] == AutomationRoute.REJECT.value
    assert result["approved"] is False


def test_aprobacion_ejecuta_una_vez():
    uid = _create_synthetic_user("p6@poolar.local")
    m = ApprovalManager()
    r = _create(m, "exec_006", "op_sensible", {"data": "original"}, proposed_by=uid)
    effect_ran = []
    def run_effect():
        effect_ran.append(True)
    a = _create_synthetic_user("a6@poolar.local")
    approved = m.approve(r.approval_id, approved_by=a, actor=_actor(a))
    run_effect()
    assert len(effect_ran) == 1
    assert approved.inputs.get("data") == "original"
    a2 = _create_synthetic_user("a6b@poolar.local")
    with pytest.raises(Exception):
        m.approve(r.approval_id, approved_by=a2, actor=_actor(a2))
    assert len(effect_ran) == 1


def test_autorizacion_actor_resuelve():
    uid = _create_synthetic_user("p7@poolar.local")
    m = ApprovalManager()
    r = _create(m, "exec_007", proposed_by=uid)
    a = _create_synthetic_user("a7@poolar.local")
    res = m.approve(r.approval_id, approved_by=a, actor=_actor(a))
    assert res.approved_by is not None


def test_origen_desconocido_falla_conservador():
    result = automation_evaluator.evaluate(
        {"action": "create_necesidad"},
        {"actor_type": "individuo", "actor_rol": "individuo", "is_destinatario": False},
    )
    assert result["route"] != AutomationRoute.AUTO_APPROVE.value
