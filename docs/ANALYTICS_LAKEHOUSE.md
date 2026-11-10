# Analytics and Lakehouse (Status and Roadmap)

> **Separated from the transactional/HITL core.** Analytics is **read-only/post-transactional**: it reads and transforms data; it **never** approves or executes business effects. No unnecessary PII; provenance, redaction, and idempotency are required.

## Current state (implemented/scaffolded, dev-stage)

| Component | Status | Evidence |
|---|---|---|
| Medallion architecture `raw → staging → marts` | **Scaffold** | `analytics/` (`raw/`, `staging/`, `marts/`, `sample/`, `dbt/`) |
| Idempotent raw export (JSONL) with provenance/redaction | **Implemented** | `scripts/export_medallion_raw.py` (read-only; HITL/problems/initiatives/decisions/needs entities; `_idempotency_key`, `_provenance`, `sanitize_for_log`) |
| Synthetic/redacted samples | **Present** | `analytics/sample/raw/*.jsonl` |
| dbt modeling (stubs/models) | **Implemented/scaffolded** | `analytics/dbt/dbt_project.yml`, models (`raw/staging/marts`), reproducible local profile (`analytics/dbt/profiles.yml`) |
| Local build/query (DuckDB) | **Implemented** | `analytics/build_local_lakehouse.py` (medallion in `analytics/local/analytics.duckdb`, gitignored) |
| dbt local run (DuckDB) | **Implemented** | `dbt run --project-dir analytics/dbt --profiles-dir analytics/dbt` → **PASS=3** (sample) |
| Export tests | **Present** | `tests/test_fase0_medallion_export.py` (idempotency, redaction) |

**Current scope:** local/dev analytics, synthetic or controlled exports, no coupling of HITL commits to external pipelines.

## Data lakehouse? (contemplated)

- **Today:** local medallion-style foundation (exports + layers + dbt + DuckDB). This is **lakehouse-style groundwork**, not a full production lakehouse (no managed object-lake storage, no transactional table format such as Iceberg/Delta, no unified catalog or distributed compute in operation).
- **Contemplated (strategic, when enabled):** evolution to a managed lakehouse: `auditable exports → (Basin/Pipelines → R2/Iceberg)` (see `analytics/README.md` and `docs/POOLAR_ECOSYSTEM_ARQUITECTURA_INTEGRACION.md`). Subject to authorization, privacy/retention controls, and no business effects executed from analytics.
- **Principles:** auditable contracts for external metrics (e.g. CO2e), provenance/versioning, idempotency, no unnecessary PII, no circular dependency with HITL.

## Usage (dev)

```bash
# Idempotent raw export (read-only)
python scripts/export_medallion_raw.py --out analytics/local/raw

# Build local DuckDB medallion (sample or exports)
python analytics/build_local_lakehouse.py

# dbt (reproducible local; DuckDB)
python -m pip install dbt-duckdb
dbt run --project-dir analytics/dbt --profiles-dir analytics/dbt
dbt run --project-dir analytics/dbt --profiles-dir analytics/dbt --vars '{"raw_path":"analytics/local/raw"}'
```

## Related

- `analytics/README.md` — rules and layers.
- `scripts/export_medallion_raw.py` — export.
- `analytics/build_local_lakehouse.py` — local build.
- `docs/POOLAR_ECOSYSTEM_ARQUITECTURA_INTEGRACION.md` — ecosystem (Basin/R2/Iceberg as strategic option).