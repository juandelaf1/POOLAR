"""Export idempotente raw (medallion) - read-only, sin HITL."""
import os
import json
from pathlib import Path

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from scripts.export_medallion_raw import export_all  # noqa: E402
from src.core.database import SessionLocal  # noqa: E402
from src.core.models import EventoAuditoria  # noqa: E402
from src.core.agent_harness.approvals import approval_manager  # noqa: E402


def test_export_is_idempotent(tmp_path):
    # seed minimal audit row
    with SessionLocal() as s:
        s.add(EventoAuditoria(entidad_referencia="test", entidad_id=1, tipo_evento="inicio", usuario_o_sistema="t", justificacion="x"))
        s.commit()
    out = tmp_path / "raw"
    s1 = export_all(out)
    s2 = export_all(out)
    assert s1["eventos_auditoria"] >= 1
    assert s2["eventos_auditoria"] == 0  # idempotente
    lines = [json.loads(l) for l in (out / "eventos_auditoria.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    assert all("_idempotency_key" in r and "_provenance" in r for r in lines)


def test_export_redacts_sensitive_fields(tmp_path, org_a):
    actor = {"tipo": "organizacion", "user_id": org_a["user_id"], "persona_id": None, "organizacion_id": org_a["org_id"], "rol": "administrador"}
    approval_manager.create("ex-red", "tool_x", {}, proposed_by=org_a["user_id"], reason="contact a@b.com postgresql://u:p@h/db", actor=actor)
    out = tmp_path / "raw"
    export_all(out)
    text = (out / "approval_requests.jsonl").read_text(encoding="utf-8")
    assert "a@b.com" not in text
    assert "u:p@" not in text
