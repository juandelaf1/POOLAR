"""Build local analytics lakehouse (medallion) with DuckDB — read-only, no HITL.

Reads raw JSONL exports/samples and materializes raw/staging/marts in a local DuckDB file.
Usage:
  python analytics/build_local_lakehouse.py
  python analytics/build_local_lakehouse.py --raw analytics/local/raw --db analytics/local/analytics.duckdb
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RAW = ROOT / "analytics" / "sample" / "raw"
DEFAULT_DB = ROOT / "analytics" / "local" / "analytics.duckdb"


ENTITIES = [
    "approval_requests",
    "eventos_auditoria",
    "problemas_colectivos",
    "iniciativas",
    "decisiones",
    "necesidades",
]


def _read_jsonl(path: Path):
    if not path.exists():
        return f"read_json_auto('{path.as_posix()}', ignore_errors=true)"  # will return empty if missing in some cases
    return f"read_json_auto('{path.as_posix()}', union_by_name=true, ignore_errors=true)"


def build(raw_dir: Path, db_path: Path) -> dict:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute("CREATE SCHEMA IF NOT EXISTS staging")
    con.execute("CREATE SCHEMA IF NOT EXISTS marts")

    stats = {}
    for ent in ENTITIES:
        p = raw_dir / f"{ent}.jsonl"
        if p.exists():
            con.execute(f"CREATE OR REPLACE VIEW raw.{ent} AS SELECT * FROM read_json_auto('{p.as_posix()}', union_by_name=true)")
            stats[ent] = con.execute(f"SELECT count(*) FROM raw.{ent}").fetchone()[0]
        else:
            con.execute(f"CREATE OR REPLACE VIEW raw.{ent} AS SELECT NULL WHERE false")
            stats[ent] = 0

    # staging: normalización HITL
    con.execute(
        """
        CREATE OR REPLACE VIEW staging.stg_approval_requests AS
        SELECT
          approval_id,
          execution_id,
          tool_name,
          lower(cast(status as varchar)) as status,
          try_cast(organizacion_id as integer) as organizacion_id,
          proposer_type,
          try_cast(created_at as timestamp) as created_at,
          try_cast(executed_at as timestamp) as executed_at,
          case when try_cast(executed_at as timestamp) is not null then 1 else 0 end as is_executed,
          _idempotency_key
        FROM raw.approval_requests
        WHERE _idempotency_key IS NOT NULL OR approval_id IS NOT NULL
        """
    )

    # marts
    con.execute(
        """
        CREATE OR REPLACE TABLE marts.mart_hitl_summary AS
        SELECT
          coalesce(tool_name, 'unknown') as tool_name,
          coalesce(status, 'unknown') as status,
          count(*) as approvals,
          sum(is_executed) as executed_count
        FROM staging.stg_approval_requests
        GROUP BY 1, 2
        """
    )

    con.execute(
        """
        CREATE OR REPLACE VIEW staging.stg_problemas_colectivos AS
        SELECT
          try_cast(id as integer) as id,
          lower(cast(estado as varchar)) as estado,
          try_cast(organizacion_id as integer) as organizacion_id,
          origen_datos,
          try_cast(fecha_creacion as timestamp) as fecha_creacion
        FROM raw.problemas_colectivos
        """
    )

    con.execute(
        """
        CREATE OR REPLACE TABLE marts.mart_problemas_summary AS
        SELECT coalesce(estado,'unknown') as estado, count(*) as problemas
        FROM staging.stg_problemas_colectivos
        GROUP BY 1
        """
    )

    summary = {
        "raw_counts": stats,
        "db": str(db_path),
        "marts": {
            "mart_hitl_summary": con.execute("SELECT count(*) FROM marts.mart_hitl_summary").fetchone()[0],
            "mart_problemas_summary": con.execute("SELECT count(*) FROM marts.mart_problemas_summary").fetchone()[0],
        },
    }
    con.close()
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(DEFAULT_RAW), help="Directorio con *.jsonl raw (default: analytics/sample/raw)")
    ap.add_argument("--db", default=str(DEFAULT_DB), help="Ruta DuckDB local (default: analytics/local/analytics.duckdb)")
    args = ap.parse_args()
    summary = build(Path(args.raw), Path(args.db))
    print(json.dumps({"ok": True, **summary}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
