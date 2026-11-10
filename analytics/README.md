# Analytics (Medallion) — POOLAR

> **Separado del núcleo transaccional/HITL (Fase 0).** La analítica lee/transforma; **nunca** aprueba ni ejecuta efectos de negocio.

## Capas
- `raw/` (bronze): ingesta con procedencia (exports, eventos, snapshots). Inmutable/append cuando sea posible.
- `staging/` (silver): limpieza, tipado, deduplicación, claves.
- `marts/` (gold): métricas/consumo (impacto, problemas resueltos, CO2e trazable). Read-only para serving/BI.

## Herramientas
- **DuckDB**: local medallion build/query (`analytics/build_local_lakehouse.py`).
- **dbt + duckdb**: models in `analytics/dbt/` (reproducible locally over JSONL exports/samples).
- **DVC/Git LFS**: only if needed for reproducible datasets/models or repo binaries.

## Build local (DuckDB, medallion)
```bash
# From real exports (read-only)
python scripts/export_medallion_raw.py --out analytics/local/raw

# Build local lakehouse (raw/staging/marts) from sample or exports
python analytics/build_local_lakehouse.py
python analytics/build_local_lakehouse.py --raw analytics/local/raw --db analytics/local/analytics.duckdb
```
Generates `analytics/local/analytics.duckdb` (gitignored) with `raw.*`, `staging.*`, `marts.*`.

## dbt (reproducible local)
```bash
# Install (once)
python -m pip install dbt-duckdb

# Run from repo root (uses sample data by default; writes analytics/local/dbt_analytics.duckdb)
python -m dbt run --project-dir analytics/dbt --profiles-dir analytics/dbt

# Use real exports
python -m dbt run --project-dir analytics/dbt --profiles-dir analytics/dbt --vars '{"raw_path":"analytics/local/raw"}'

# Tests (when added)
python -m dbt test --project-dir analytics/dbt --profiles-dir analytics/dbt
```
`analytics/dbt/profiles.yml` is committed for local reproducibility (no secrets). DuckDB files and `analytics/local/` are gitignored. Models read JSONL via `read_json_auto` (no HITL/domain side effects).

## Reglas
- Sin PII innecesaria; procedencia/versionado; idempotencia en ingesta.
- CO2e/capacidades externas como contratos auditables (p. ej. Devera), no acoplados al commit HITL.
- Pipeline estratégico: exports auditables → (Basin/Pipelines → R2/Iceberg) cuando se habilite. Ver `docs/ANALYTICS_LAKEHOUSE.md`.
