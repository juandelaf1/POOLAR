# Analytics (Medallion) — POOLAR

> **Separado del núcleo transaccional/HITL (Fase 0).** La analítica lee/transforma; **nunca** aprueba ni ejecuta efectos de negocio.

## Capas
- `raw/` (bronze): ingesta con procedencia (exports, eventos, snapshots). Inmutable/append cuando sea posible.
- `staging/` (silver): limpieza, tipado, deduplicación, claves.
- `marts/` (gold): métricas/consumo (impacto, problemas resueltos, CO2e trazable). Read-only para serving/BI.

## Herramientas (plan)
- **DuckDB**: consulta/validación local de Parquet/CSV.
- **DBT**: modelado `raw→staging→marts` cuando haya destino estable (tests, docs, linaje).
- **DVC/Git LFS**: solo si aplica (datasets/modelos reproducibles / binarios de repo).

## Build local (DuckDB, medallion)
```bash
# Desde exports reales (read-only)
python scripts/export_medallion_raw.py --out analytics/local/raw

# Construir lakehouse local (raw/staging/marts) desde sample o exports
python analytics/build_local_lakehouse.py
python analytics/build_local_lakehouse.py --raw analytics/local/raw --db analytics/local/analytics.duckdb
```
Genera `analytics/local/analytics.duckdb` (ignorado por git) con vistas/tablas `raw.*`, `staging.*`, `marts.*`.

## Reglas
- Sin PII innecesaria; procedencia/versionado; idempotencia en ingesta.
- CO2e/capacidades externas como contratos auditables (p. ej. Devera), no acoplados al commit HITL.
- Pipeline estratégico: exports auditables → (Basin/Pipelines → R2/Iceberg) cuando se habilite. Ver `docs/ANALYTICS_LAKEHOUSE.md`.
