# Hoja de Ruta — POOLAR

> Actualizado: 2026-11-10 (`fase0-gobernanza`). Estado: **desarrollo/prototipo, no producción**. Fase 0 con núcleo fuerte; cierre formal sujeto a gates externos.

## Completado (base y Fase 0)

- [x] Monolito modular FastAPI + SQLAlchemy; auth JWT/PBKDF2, registro individual (`POST /personas/registro`), autorización org/persona, datos sintéticos `synthetic_pilot`.
- [x] Modelo dominio: Necesidad, Problema Colectivo, Iniciativa, Decisión, Invitación/Participación, auditoría, exportación.
- [x] Gobernanza/HITL: fail-closed, scoping tenant/personal, no autoaprobación, retiro propio seguro, aprobación→ejecución transaccional de handlers reanudables, idempotencia/dedup, estados (`pendiente/ejecutando/ejecutada/fallida_reintentable/rechazada/expirada`), migraciones 0004/0005.
- [x] Handlers deterministas registrados/validados (núcleo Fase 0), políticas declarativas, auditoría de ciclo de vida.
- [x] Suite local (2026-11-10, sin PG): **171 passed, 7 skipped, 1 xfailed**; guards PG-only/reachability deterministas; aislamiento de `RESUMABLE_HANDLERS`/fixtures corregido.
- [x] Evidencia PG desechable previa: concurrencia 1 efecto (`test_fase0_p04_concurrency_pg.py`), migraciones 0004+0005 (revalidar en entorno/CI objetivo).
- [x] Contratos/adaptadores modulares (manifests/ports, mocks sintéticos, proposal-only); adapters dev-stage de contratos ecosistema en EnRuta/SkyCast (PRs mergeadas).
- [x] Documentación reorganizada y compilable: `docs/index.md`, `mkdocs.yml`, archivo `docs/archive/fase0/`, `docs/ANALYTICS_LAKEHOUSE.md`, README/checklist/gobernanza/capas alineados.
- [x] Analítica (separada, read-only): medallion raw/staging/marts, export idempotente/redactado `scripts/export_medallion_raw.py`, muestras sintéticas, stubs dbt, `analytics/build_local_lakehouse.py` (DuckDB local).
- [x] Docker/Compose, Alembic, CI workflow definido.

## Pendiente / abierto

- [ ] **Cierre formal Fase 0 (gates externos):** CI verde en HEAD objetivo, job PG con secretos gestionados, matriz E2E exhaustiva donde falte, fault-injection real mid-handler si se exige.
- [ ] Revalidar concurrencia/migraciones PG en entorno objetivo tras cambios relevantes.
- [ ] Proceso de consentimiento y controles RGPD/PII operativos para datos reales; rotación/gestión de secretos en entornos.
- [ ] Integraciones externas reales (CASE/módulos/proveedores) solo por contrato, con autorización, datos sintéticos/autorizados y sin ampliar autoridad de ejecución.
- [ ] Observabilidad/UI completa de estados HITL; accesibilidad WCAG completa; E2E ampliado (Playwright) según necesidad.
- [ ] Búsqueda semántica real (pgvector) y capacidades avanzadas (RAG, PostGIS, OR-Tools, MCP, LangGraph/LangSmith) solo cuando haya necesidad demostrada.
- [ ] Licencias/derechos verificados para repos bloqueados antes de reutilización.

## Próximas iteraciones sugeridas

1. **CI/PG objetivo:** ejecutar suite PG con `POOLAR_TEST_POSTGRES_URL` + migraciones y publicar evidencia.
2. **Analytics local:** perfil dbt DuckDB + `dbt run/test` sobre exports raw; marts de impacto trazable.
3. **Integración contratos en POOLAR:** correlation/envelope en APIs HITL/ops (backward-compatible).
4. **Docs contenido:** mantener `docs/modelo_autorizacion.md`, `docs/riesgos_pendientes.md`, `docs/decisiones_tecnicas.md` alineados con implementación.