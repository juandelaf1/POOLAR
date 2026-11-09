# Capas y avance — POOLAR (registro vivo)

> Actualizado: 2026-11-08 (local, sin commit/push). Complementa `BACKLOG_PRIORIZADO_POOLAR.md`, `CAMBIOS_POOLAR_FASE0.md`, `RESULTADOS_TESTS_POOLAR_FASE0.md`.

## 1) Mapa de capas (arquitectura modular en monolito)

| Capa | Ruta principal | Responsabilidad | Estado Fase 0 |
|---|---|---|---|
| **API / borde HTTP** | `src/main.py` | Endpoints FastAPI, auth/contexto actor, wiring de gobernanza HITL, rutas `/approvals/*`, registro de handlers reanudables. | Parcial: propaga contexto; falta matriz completa por rol/acción/persona en todos los flujos. |
| **Servicios de dominio** | `src/services/*.py` | Lógica de negocio ejecutable (problema colectivo, iniciativa, decisión, estado). Aceptan `commit` para control transaccional del harness. | Parcial: fail-closed P0.2; transacciones componibles. |
| **Núcleo de dominio/datos** | `src/core/models.py`, `src/core/database.py`, `src/core/auth.py`, `src/core/schemas` (si aplica) | Modelos SQLAlchemy, sesión/engine, identidad/roles, tokens. | Parcial: `ApprovalRequest` ampliado (scope/ejecución/idempotencia); migraciones 0004 (+0005 local). |
| **Agent harness / gobernanza** | `src/core/agent_harness/approvals.py`, `handlers.py`, `policy_engine.py`, `tool_registry.py`, `state.py`, `security.py` | Evaluación, HITL, persistencia de solicitudes, autorización/scope, ejecución transaccional, reanudación determinista, trazabilidad. | **Foco actual.** Aislamiento tenant, no autoaprobación, retiro propio seguro, idempotencia/dedup, estados de ejecución, handlers 5/5 registrados/validados. |
| **Puertos / contratos** | `src/core/ports/*`, `src/core/contracts.py` | Interfaces ABC para capacidades externas (evidencia/geo/semántico). | Parcial: ABCs explícitos (sin `or True`); contratos POOLAR↔CASE pendientes. |
| **Migraciones** | `src/core/alembic/`, `src/core/migrations/` | Evolución de esquema. | 0004 aplicada en PG real (Neon desechable). **0005 local** (unicidad parcial `idempotency_key`) pendiente de aplicar al revalidar PG. |
| **Pruebas** | `tests/` | Regresión, Fase 0, concurrencia PG, HITL HTTP. | Suites Fase 0/gobernanza verdes en 1 corrida (SQLite) + evidencia PG carrera. Harness SQLite estabilizado. |

## 2) Flujo HITL (capa de gobernanza)

1. API evalúa gobernanza (`_handle_governance` / evaluator) → si requiere humano, crea `ApprovalRequest` con **scope/actor/correlación/idempotency key**.
2. Dominio filtra visibilidad/gestión por **tenant/actor/proponente** (fail-closed, 404/403 según caso).
3. **Aprobar** (actor autorizado, distinto del proponente): lock → `ejecutando` → handler/servicio (`commit=False`) → `ejecutada` + `executed_at` + resultado → commit; error → rollback + `fallida_reintentable` (reintentable sin duplicar efecto local).
4. **Rechazar**: actor autorizado; **retiro propio** permitido (resolución segura, sin ejecución). Autoaprobación bloqueada.
5. **Reanudación**: handlers deterministas registrados/validados; sin placeholders.

## 3) Avance por hito (resumen)

| Fecha | Capa(s) | Cambio | Evidencia |
|---|---|---|---|
| 2026-11-08 | core/agent_harness, services, API, alembic, tests, docs | P0.2 fail-closed decisiones cross-org. P0.1 scope/tenant/roles/no autoaprobación/idempotency key (0004). P0.3 commit único + estados ejecución + handlers/servicios componibles. P1.4/P1.5 handlers 5/5 + validación + ABCs. | 41 passed (focal) en corridas controladas; docs auditoría/plan/resultados/cambios. |
| 2026-11-08 | PG real (Neon desechable) | `alembic upgrade head` hasta 0004; carrera 2 aprobadores, 1 efecto, `executed_at`. | `test_fase0_p04_concurrency_pg.py` → **1 passed (11.07s)**. F0-10/F0-12 DONE (base). |
| 2026-11-08 | tests/conftest, approvals, scope tests, backlog | Harness SQLite: `reset_db` por borrado de datos (estable). Persona HTTP scope + retiro propio seguro. 0005 unicidad parcial idempotency **aplicada en Neon (desechable, 2026-11-09)**; carrera PG **1 passed (10.15s)** revalidada. | **88 passed** en 1 corrida (suites Fase 0/gobernanza + guards F0-09 + retiro propio): `test_fase0_approvals_scope`, `test_fase0_decision_failclosed`, `test_fase0_resumption_handlers`, `test_fase0_handlers_registry`, `test_governance_regresion`, `test_p03_http_governance`, `test_p04_resumption`. |

## 4) Gobernanza / decisiones / gaps abiertos

> Ver `GOBERNANZA_POOLAR.md` (modelo operativo, matriz, HITL, POOLAR↔CASE).


- **HITL personal (individuo) — política profesional adoptada (fail-closed):** el proponente puede **ver y retirar** (sin ejecución). **Aprobación/ejecución por terceros no permitida** sin autoridad de gobernanza explícita diseñada; preserva autonomía, privacidad y aislamiento tenant/personal. Autoaprobación bloqueada.
- **Efectos externos:** no identificados; si aparecen → outbox + idempotencia receptora + recuperación (F0-07).
- **0005 en Neon:** aplicar solo al revalidar PG (`alembic upgrade head`).

## 5) Capa analítica (planificada, separada del núcleo transaccional)

> No integrar antes de cerrar Fase 0. La analítica consume datos; **no** ejecuta efectos de negocio ni aprueba HITL.

| Capa | Rol | Tecnologías candidatas | Regla |
|---|---|---|---|
| **Operacional / fuente de verdad** | Transacciones, HITL, auditoría, estado | PostgreSQL (prod) / SQLite (dev), modelos `src/core/models.py`, `eventos_auditoria` | Autoridad. Append-only/auditable donde aplique. |
| **Ingesta / lake** | Exportar eventos/snapshots con procedencia | Pipelines/Basin → R2/Iceberg (estratégico), exports Parquet/CSV | Idempotente, versionado, sin PII innecesaria. |
| **Transformación / modelado** | Métricas, agregados, CO2e, indicadores de impacto | **DBT** (cuando haya destino estable: warehouse/lakehouse/Postgres analytics schema); SQL versionado + tests + docs | Separar `raw` → `staging` → `marts`. No mutar operacional. |
| **Consulta analítica** | Ad-hoc, notebooks, validación, embebido | **DuckDB** (embebido/local/CI, lee Parquet/CSV; puede consultar exports o datasets analíticos) | Útil para exploración y pipelines ligeros; no reemplaza la fuente transaccional. |
| **Serving / BI** | Dashboards, API de métricas (read-only) | Read models/vistas materializadas, API específica, o herramienta BI | Métricas = problemas resueltos/impacto (no vanidad), con trazabilidad/procedencia. |

**Decisión profesional:** empezar simple y auditable (exportaciones + DuckDB/SQL verificable), introducir **dbt** cuando existan modelos analíticos repetibles y un destino claro; CO2e/módulos externos como **capacidades con contratos** (p. ej. Devera) y resultados trazables, nunca acoplados al commit transaccional de HITL.

| Herramienta | Úsala para | No la uses para | Cuándo en POOLAR |
|---|---|---|---|
| **DBT** | Transformar/modelar datos analíticos (SQL versionado, tests, docs, linaje) | Versionar binarios grandes; reemplazar la DB transaccional | Cuando haya `raw/staging/marts` repetibles y destino estable. |
| **DVC** | Versionar datasets/modelos grandes + pipelines reproducibles (remoto de datos, métricas/experimentos) | Código normal; archivos pequeños que caben bien en Git; auditoría transaccional HITL | Cuando existan datasets/modelos analíticos/ML que deban reproducirse con procedencia. |
| **Git LFS** | Binarios grandes *acoplados al repo* (assets, artefactos específicos) | Versionado/pipelines de datasets, reproducibilidad analítica, lakehouse | Solo si un binario grande debe vivir en Git; preferir almacenamiento de datos externo + referencias auditables. |

## 6) Cómo revalidar (local)

```powershell
cd C:\Users\JUAN\Desktop\Proyectos\Trama_Abierta\poolar
# SQLite (suites Fase 0/gobernanza)
Remove-Item .pytest_poolar.db,.pytest_poolar.db-shm,.pytest_poolar.db-wal -ErrorAction SilentlyContinue
python -m pytest tests/test_fase0_approvals_scope.py tests/test_fase0_decision_failclosed.py tests/test_fase0_resumption_handlers.py tests/test_fase0_handlers_registry.py tests/test_governance_regresion.py tests/test_p03_http_governance.py tests/test_p04_resumption.py -q --rootdir=.

# PostgreSQL real (solo si se revalida; credenciales locales, no compartir)
# $env:POOLAR_TEST_POSTGRES_URL="postgresql+psycopg2://...?...sslmode=require"; $env:DATABASE_URL=$env:POOLAR_TEST_POSTGRES_URL
# python -m alembic -c alembic.ini upgrade head
# python -m pytest tests/test_fase0_p04_concurrency_pg.py -q --rootdir=.
```
