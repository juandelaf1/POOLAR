"""Ejecuta medallion raw->staging->marts con DuckDB (local, read-only, sin HITL).

Usa datos sample (sintéticos) o exports en analytics/local/raw.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]


def run(raw_dir: Path, db_path: Path) -> dict:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    raw_glob = str(raw_dir / "approval_requests.jsonl").replace("\\", "/")
    con.execute(f"""
        create or replace view raw_approval_requests as
        select * from read_json_auto('{raw_glob}');
    """)
    con.execute("""
        create or replace view stg_approval_requests as
        select
          approval_id, execution_id, tool_name, lower(status) as status,
          cast(organizacion_id as integer) as organizacion_id, proposer_type,
          try_cast(created_at as timestamp) as created_at,
          try_cast(executed_at as timestamp) as executed_at,
          case when executed_at is not null then 1 else 0 end as is_executed,
          _idempotency_key
        from raw_approval_requests
        where _idempotency_key is not null;
    """)
    con.execute("""
        create or replace table mart_hitl_summary as
        select tool_name, status, count(*) as approvals, sum(is_executed) as executed_count
        from stg_approval_requests
        group by 1, 2;
    """)
    rows = con.execute("select * from mart_hitl_summary order by tool_name, status").fetchall()
    cols = [d[0] for d in con.description]
    con.close()
    return {"ok": True, "db": str(db_path), "mart_hitl_summary": [dict(zip(cols, r)) for r in rows]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", default=str(ROOT / "analytics/sample/raw"))
    ap.add_argument("--db", default=str(ROOT / "analytics/local/medallion.duckdb"))
    args = ap.parse_args()
    print(json.dumps(run(Path(args.raw), Path(args.db)), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
