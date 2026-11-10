# Checklist de cierre — Fase 0 (POOLAR)

> Fecha: 2026-11-08/10. Estado: **ABIERTA** (núcleo crítico con evidencia fuerte; cierre formal sujeto a gates externos/entorno). Rama activa: `fase0-gobernanza` (commits/push realizados).

## Evidencia base (reproducible)
```powershell
cd C:\Users\JUAN\Desktop\Proyectos\Trama_Abierta\poolar
python -m compileall -q src tests
Remove-Item .pytest_poolar.db,.pytest_poolar.db-shm,.pytest_poolar.db-wal -ErrorAction SilentlyContinue
python -m pytest -q --rootdir=.
# Esperado local sin PG (POOLAR_TEST_POSTGRES_URL no definido): 171 passed, 7 skipped, 7 warnings (SQLite). Tests PG-only quedan omitidos de forma determinista.
# PG real (solo con env local, no compartir secretos):
# $env:POOLAR_TEST_POSTGRES_URL="postgresql+psycopg2://..."
# python -m alembic -c alembic.ini upgrade head
# python -m pytest tests/test_p01_persistencia.py tests/test_fase0_p04_concurrency_pg.py -q --rootdir=.
```

## Criterios
| Criterio | Estado | Evidencia | Falta para cerrar |
|---|---|---|---|
| CI (local/remota) | **Parcial** | `.github/workflows/fase0-check.yml` (compileall + suite Fase 0 SQLite). Local (2026-11-10): **171 passed, 7 skipped, 1 xfailed** sin PG; guards PG-only deterministas (skip + reachability). | Ejecutar en CI/HEAD objetivo; job PG con secretos gestionados y evidencia verde |
| F0-01 Sin atajos inseguros | **Parcial→fuerte** | Scope/404 cross-tenant; no autoaprobación; fail-closed decisiones; aislamiento de handlers en tests corregido | Revisión final de excepciones silenciosas residuales + CI verde |
| F0-02 Fail-closed | **Hecho** | `decision_service` sin bypass; tests `test_fase0_decision_failclosed.py` | — |
| F0-03 Scoping/authz por tenant | **Parcial** | Modelo+migración 0004; filtrado; HTTP 404/403; individuo↔individuo/org↔personal; retiro propio | Matriz completa lectura/aprobación/admin; E2E por acciones gobernadas accesibles a individuo |
| F0-04 Roles/permisos + política HITL personal | **Parcial (política adoptada)** | Roles probados; **política profesional fail-closed**: HITL personal solo ver/retirar, sin autoaprobación ni terceros | Cobertura exhaustiva de matriz y casos legacy compartidos |
| F0-05 Commit único | **Hecho (núcleo)** | lock→ejecutando→handler(`commit=False`)→ejecutada; rollback→`fallida_reintentable` | Trazabilidad fina adicional si se requiere |
| F0-06 Fallo/reintento/estados | **Parcial fuerte** | `fallida_reintentable`, reintento, cierre por rechazo autorizado, idempotencia ejecutada, sin parcial; approve ejecuta handler (semántica actual) | Matriz exhaustiva por cada camino de fallo/recuperación |
| F0-07 Idempotencia/externos | **Parcial** | `idempotency_key`/dedup, **0005 aplicada en Neon** (revalidación); sin externos identificados | Outbox solo si hay externos |
| F0-08 Handlers deterministas | **Hecho (núcleo)** | 5/5 registrados, `validate_resumable_handlers()` OK | Validación startup en todos los entornos objetivo |
| F0-09 Reanudación | **Parcial fuerte** | Éxito 5 handlers; rechazo sin efecto; fallo→retry por cada tool reanudable; guards estado | Interrupción/crash real a mitad de camino (infra fault-injection) |
| F0-10 Carrera PG real | **Hecho (evidencia desechable previa)** | Neon desechable (2026-11-09): 0005 aplicada; `test_fase0_p04_concurrency_pg.py` **1 passed**, 1 efecto, `executed_at` | Revalidar en entorno PG objetivo/CI tras cambios relevantes |
| F0-11 Visibilidad | **Parcial** | `execution_status/result/error`, `executed_at`, estados | UI/observabilidad completa si aplica |
| F0-12 Migraciones/PG | **Hecho (evidencia desechable)** | 0004+**0005** aplicadas en Neon desechable; revalidación OK | Revalidar en entorno objetivo/CI cuando exista |

## Decisiones registradas
- HITL personal (individuo): **ver/retirar** permitido; **aprobar/ejecutar por terceros NO** sin autoridad de gobernanza explícita (fail-closed).
- Analítica separada (post Fase 0): DuckDB consulta/exports, DBT cuando haya marts estables, DVC solo para datasets/modelos reproducibles, Git LFS solo binarios de repo.

## No hacer antes de cerrar
- No integrar CASE/módulos externos reales sin autorización (solo contratos/mocks/adaptadores sintéticos según gobernanza).
- No usar datos reales/producción ni relajar aislamiento/HITL.
- Mantener cierre formal condicionado a gates externos (PR/CI verde, PG+secrets, evidencia E2E/fault-injection según criterio).
