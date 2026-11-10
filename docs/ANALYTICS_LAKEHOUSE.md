# Analytics y Lakehouse (estado y hoja de ruta)

> **Separado del núcleo transaccional/HITL.** La analítica es **read-only/post-transaccional**: lee y transforma; **nunca** aprueba ni ejecuta efectos de negocio. Sin PII innecesaria; procedencia, redacción e idempotencia obligatorias.

## Estado actual (implementado/scaffolded, dev-stage)

| Componente | Estado | Evidencia |
|---|---|---|
| Arquitectura medallion `raw → staging → marts` | **Scaffold** | `analytics/` (`raw/`, `staging/`, `marts/`, `sample/`, `dbt/`) |
| Export idempotente raw (JSONL) con procedencia/redacción | **Implementado** | `scripts/export_medallion_raw.py` (read-only; entidades HITL/problemas/iniciativas/decisiones/necesidades; `_idempotency_key`, `_provenance`, `sanitize_for_log`) |
| Muestras sintéticas/redactadas | **Presente** | `analytics/sample/raw/*.jsonl` |
| Modelado dbt (stubs) | **Scaffold** | `analytics/dbt/dbt_project.yml`, `models/raw|staging|marts` (views/tables, p.ej. `stg_approval_requests`, `mart_hitl_summary`) |
| Consulta/validación local | **Previsto** | DuckDB sobre exports/Parquet-CSV (local) |
| Pruebas de export | **Presentes** | `tests/test_fase0_medallion_export.py` (idempotencia, redacción) |

**Alcance actual:** analítica local/dev, datos sintéticos o exports controlados, sin acoplar commits HITL a pipelines externos.

## ¿Data lakehouse? (contemplado)

- **Hoy:** base tipo *medallion* local (exports + capas + dbt stubs + DuckDB previsto). Esto es un **fundamento lakehouse-style**, no un lakehouse productivo completo (no hay storage de objetos gestionado como lake, formato de tabla transaccional tipo Iceberg/Delta, catálogo unificado ni cómputo distribuido en operación).
- **Contemplado (estratégico, cuando se habilite):** evolución a lakehouse gestionado: `exports auditables → (Basin/Pipelines → R2/Iceberg)` según `analytics/README.md` y la arquitectura de ecosistema (`docs/POOLAR_ECOSYSTEM_ARQUITECTURA_INTEGRACION.md`). Sujeto a autorización, controles de privacidad/retención, y sin ejecutar efectos de negocio desde analítica.
- **Principios:** contratos auditables para métricas externas (p.ej. CO2e), procedencia/versionado, idempotencia, sin PII innecesaria, sin dependencia circular con HITL.

## Uso (dev)
```bash
# Export raw idempotente (read-only)
python scripts/export_medallion_raw.py --out analytics/local/raw

# dbt (stubs; requiere perfil/engine configurado, p.ej. DuckDB)
# dbt run --project-dir analytics/dbt --profiles-dir analytics/dbt
```

## Relación
- `analytics/README.md` — reglas y capas.
- `scripts/export_medallion_raw.py` — export.
- `docs/POOLAR_ECOSYSTEM_ARQUITECTURA_INTEGRACION.md` — ecosistema (Basin/R2/Iceberg como opción estratégica).