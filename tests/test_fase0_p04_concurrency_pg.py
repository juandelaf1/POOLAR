"""Fase 0 / P1.4: concurrencia real en PostgreSQL (dos aprobadores simultáneos).

NO usa SQLite para declarar esta prueba superada. Requiere:
- POOLAR_TEST_POSTGRES_URL (o DATABASE_URL PostgreSQL) accesible.
- Esquema migrado.

Si no hay PostgreSQL disponible, esta prueba debe SKIP/FAIL por entorno, no PASS falso.
"""
import os
import threading

import pytest

PG_URL = os.getenv("POOLAR_TEST_POSTGRES_URL") or os.getenv("DATABASE_URL", "")
if not PG_URL.startswith("postgresql"):
    pytest.skip("Requiere PostgreSQL real (POOLAR_TEST_POSTGRES_URL)", allow_module_level=True)


def _pg_reachable(url: str) -> bool:
    try:
        import sqlalchemy as sa
        e = sa.create_engine(url)
        with e.connect() as c:
            c.execute(sa.text("SELECT 1"))
        return True
    except Exception:
        return False


if not _pg_reachable(PG_URL):
    pytest.skip("PostgreSQL no accesible en el entorno de prueba", allow_module_level=True)

os.environ["DATABASE_URL"] = PG_URL
os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")

from src.core.agent_harness.approvals import approval_manager  # noqa: E402
from src.core.database import SessionLocal  # noqa: E402
from src.core.models import OperationalUser, Organizacion, Necesidad, ProblemaColectivo  # noqa: E402
from src.core.auth import hash_password  # noqa: E402
from src.core.ports import AutomationRoute  # noqa: E402
from src.main import _handle_governance  # noqa: E402


def test_two_approvers_race_single_effect_pg():
    """Dos aprobadores compiten con barrera sobre una solicitud pendiente: 1 efecto."""
    marker = f"Problema race PG {__import__('uuid').uuid4().hex[:8]}"
    with SessionLocal() as s:
        org = Organizacion(nombre=f"Org Race {marker[-8:]}", tipo_organizacion="cooperativa", contacto_publico=f"r-{marker[-8:]}@r.org")
        s.add(org); s.flush()
        suffix = marker[-8:]
        proposer = OperationalUser(email=f"p-{suffix}@r.org", hashed_password=hash_password("secret123"), nombre="P", rol="administrador", organizacion_id=org.id)
        a1 = OperationalUser(email=f"a1-{suffix}@r.org", hashed_password=hash_password("secret123"), nombre="A1", rol="administrador", organizacion_id=org.id)
        a2 = OperationalUser(email=f"a2-{suffix}@r.org", hashed_password=hash_password("secret123"), nombre="A2", rol="administrador", organizacion_id=org.id)
        s.add_all([proposer, a1, a2]); s.flush()
        need = Necesidad(titulo="N race", descripcion="desc race", visibilidad="privada", organizacion_id=org.id)
        s.add(need); s.commit(); s.refresh(need); s.refresh(proposer); s.refresh(a1); s.refresh(a2); s.refresh(org)

    user = {"tipo": "organizacion", "user_id": proposer.id, "persona_id": None, "organizacion_id": org.id, "rol": "administrador"}
    proposal = {
        "version": 1, "action": "create_problema_colectivo", "origen_datos": "synthetic_pilot",
        "descripcion": marker, "evidencias": None, "necesidades_asociadas": [need.id],
        "personas_participantes": [], "organizaciones_participantes": [],
        "user": {"tipo": "organizacion", "user_id": proposer.id, "persona_id": None, "organizacion_id": org.id},
    }
    governance = {"rejected": False, "requires_human_review": True, "approved": False}
    with SessionLocal() as s:
        gov = _handle_governance(s, governance, user, proposal)
    approval_id = gov["approval_id"]

    barrier = threading.Barrier(2)
    results = {}

    def approve_as(uid, role, org_id, key):
        actor = {"tipo": "organizacion", "user_id": uid, "persona_id": None, "organizacion_id": org_id, "rol": role}
        barrier.wait()
        try:
            approval_manager.approve(approval_id, approved_by=uid, actor=actor)
            results[key] = "ok"
        except Exception as e:
            results[key] = f"err:{type(e).__name__}"

    t1 = threading.Thread(target=approve_as, args=(a1.id, "administrador", org.id, "a1"))
    t2 = threading.Thread(target=approve_as, args=(a2.id, "administrador", org.id, "a2"))
    t1.start(); t2.start(); t1.join(timeout=30); t2.join(timeout=30)

    # El perdedor puede recibir error o respuesta idempotente; lo crítico es 1 solo efecto.
    assert sum(1 for v in results.values() if v == "ok") >= 1, results
    with SessionLocal() as s:
        count = s.query(ProblemaColectivo).filter_by(descripcion=marker).count()
        row = s.query(__import__('src.core.models', fromlist=['ApprovalRequest']).ApprovalRequest).filter_by(approval_id=approval_id).first()
    assert count == 1, f"Efecto duplicado o ausente: {count}, resultados={results}"
    assert row is not None and row.executed_at is not None
