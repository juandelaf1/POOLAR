"""Export idempotente (read-only) a capa raw (medallion).

Genera JSONL con procedencia. No modifica datos operacionales ni ejecuta HITL.
Uso: python scripts/export_medallion_raw.py [--out analytics/local/raw]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _bootstrap_env():
    """Carga .env local solo bajo demanda (CLI); evita efectos secundarios en imports/tests."""
    _env = ROOT / ".env"
    if _env.exists():
        for line in _env.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip().lstrip("\ufeff")
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and not os.getenv(k):
                os.environ[k] = v
    os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
    if not os.getenv("DATABASE_URL") and not os.getenv("POOLAR_TEST_POSTGRES_URL"):
        os.environ["DATABASE_URL"] = "sqlite:///./poolar.db"


def _lazy_imports():
    from src.core.database import SessionLocal  # noqa: E402
    from src.core.models import ApprovalRequest, Decision, EventoAuditoria, Iniciativa, Necesidad, ProblemaColectivo  # noqa: E402
    from src.core.security import sanitize_for_log  # noqa: E402
    return SessionLocal, (ApprovalRequest, Decision, EventoAuditoria, Iniciativa, Necesidad, ProblemaColectivo), sanitize_for_log


def _provenance(entity: str) -> dict:
    return {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "entity": entity,
        "source": "poolar.operational",
        "format": "jsonl",
        "synthetic_safe": True,
    }


def _idempotency_key(row: dict) -> str:
    blob = json.dumps(row, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _write_jsonl(path: Path, rows: list[dict], entity: str) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                seen.add(json.loads(line).get("_idempotency_key"))
            except Exception:
                pass
    written = 0
    with path.open("a", encoding="utf-8") as f:
        for r in rows:
            k = _idempotency_key(r)
            if k in seen:
                continue
            rec = {"_idempotency_key": k, "_provenance": _provenance(entity), **r}
            f.write(json.dumps(rec, default=str, ensure_ascii=False) + "\n")
            seen.add(k)
            written += 1
    return written


def export_all(out_dir: Path) -> dict:
    if not os.getenv("DATABASE_URL") and not os.getenv("POOLAR_TEST_POSTGRES_URL"):
        _bootstrap_env()
    SessionLocal, models, sanitize_for_log = _lazy_imports()
    ApprovalRequest, Decision, EventoAuditoria, Iniciativa, Necesidad, ProblemaColectivo = models
    stats = {}
    with SessionLocal() as s:
        approvals = []
        for a in s.query(ApprovalRequest).all():
            approvals.append({
                "approval_id": a.approval_id,
                "execution_id": a.execution_id,
                "tool_name": a.tool_name,
                "status": a.status,
                "organizacion_id": a.organizacion_id,
                "proposer_type": a.proposer_type,
                "proposer_actor_id": a.proposer_actor_id,
                "correlation_id": a.correlation_id,
                "idempotency_key": a.idempotency_key,
                "created_at": a.created_at,
                "approved_at": a.approved_at,
                "executed_at": a.executed_at,
                "rejected_at": a.rejected_at,
                "reason": sanitize_for_log(a.reason) if a.reason else None,
                "execution_error": sanitize_for_log(a.execution_error) if a.execution_error else None,
            })
        stats["approval_requests"] = _write_jsonl(out_dir / "approval_requests.jsonl", approvals, "approval_request")

        events = []
        for e in s.query(EventoAuditoria).all():
            events.append({
                "id": e.id,
                "entidad_referencia": e.entidad_referencia,
                "entidad_id": e.entidad_id,
                "tipo_evento": e.tipo_evento,
                "usuario_o_sistema": e.usuario_o_sistema,
                "fecha": e.fecha,
                "justificacion": sanitize_for_log(e.justificacion) if e.justificacion else None,
            })
        stats["eventos_auditoria"] = _write_jsonl(out_dir / "eventos_auditoria.jsonl", events, "evento_auditoria")

        problemas = []
        for p in s.query(ProblemaColectivo).all():
            problemas.append({
                "id": p.id,
                "estado": p.estado,
                "organizacion_id": getattr(p, "organizacion_id", None),
                "origen_datos": getattr(p, "origen_datos", None),
                "fecha_creacion": getattr(p, "fecha_creacion", None),
                "descripcion": sanitize_for_log(p.descripcion) if getattr(p, "descripcion", None) else None,
            })
        stats["problemas_colectivos"] = _write_jsonl(out_dir / "problemas_colectivos.jsonl", problemas, "problema_colectivo")

        iniciativas = []
        for i in s.query(Iniciativa).all():
            iniciativas.append({
                "id": i.id,
                "estado": i.estado,
                "organizacion_id": getattr(i, "organizacion_id", None),
                "problema_colectivo_id": getattr(i, "problema_colectivo_id", None),
                "titulo": sanitize_for_log(i.titulo) if getattr(i, "titulo", None) else None,
            })
        stats["iniciativas"] = _write_jsonl(out_dir / "iniciativas.jsonl", iniciativas, "iniciativa")

        decisiones = []
        for d in s.query(Decision).all():
            decisiones.append({
                "id": d.id,
                "iniciativa_id": d.iniciativa_id,
                "tipo_decision": getattr(d, "tipo_decision", None),
                "fecha": getattr(d, "fecha", None),
                "motivo": sanitize_for_log(d.motivo) if getattr(d, "motivo", None) else None,
            })
        stats["decisiones"] = _write_jsonl(out_dir / "decisiones.jsonl", decisiones, "decision")

        necesidades = []
        for n in s.query(Necesidad).all():
            necesidades.append({
                "id": n.id,
                "organizacion_id": getattr(n, "organizacion_id", None),
                "estado": getattr(n, "estado", None),
                "visibilidad": getattr(n, "visibilidad", None),
                "fecha_creacion": getattr(n, "fecha_creacion", None),
                "titulo": sanitize_for_log(n.titulo) if getattr(n, "titulo", None) else None,
                "descripcion": sanitize_for_log(n.descripcion) if getattr(n, "descripcion", None) else None,
            })
        stats["necesidades"] = _write_jsonl(out_dir / "necesidades.jsonl", necesidades, "necesidad")
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "analytics/local/raw"))
    args = ap.parse_args()
    _bootstrap_env()
    stats = export_all(Path(args.out))
    print(json.dumps({"ok": True, "out": args.out, "written": stats}, ensure_ascii=False))


if __name__ == "__main__":
    main()
