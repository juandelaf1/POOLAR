"""Medallion raw->staging->marts con DuckDB (datos sintéticos)."""
import pytest
from pathlib import Path

pytest.importorskip("duckdb")


def test_medallion_duckdb_runs(tmp_path):
    from scripts.run_medallion_duckdb import run
    root = Path(__file__).resolve().parents[1]
    out = run(root / "analytics/sample/raw", tmp_path / "m.duckdb")
    assert out["ok"] is True
    assert len(out["mart_hitl_summary"]) >= 1
    statuses = {r["status"] for r in out["mart_hitl_summary"]}
    assert "ejecutada" in statuses or "pendiente" in statuses
