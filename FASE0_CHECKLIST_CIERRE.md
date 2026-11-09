# Checklist de cierre — Fase 0 (POOLAR)

> Fecha: 2026-11-08/09. Estado: **ABIERTA** (núcleo crítico con evidencia fuerte; faltan ítems de evidencia/exhaustividad/entorno). Sin commit/push.

## Evidencia base (reproducible)
```powershell
cd C:\Users\JUAN\Desktop\Proyectos\Trama_Abierta\poolar
python -m compileall -q src tests
Remove-Item .pytest_poolar.db,.pytest_poolar.db-shm,.pytest_poolar.db-wal -ErrorAction SilentlyContinue
python -m pytest tests/test_fase0_approvals_scope.py tests/test_fase0_decision_failclosed.py tests/test_fase0_resumption_handlers.py tests/test_fase0_handlers_registry.py tests/test_governance_regresion.py tests/test_p03_http_governance.py tests/test_p04_resumption.py -q --rootdir=.
python -m pytest -q --rootdir=.  # 119 passed, 14 skipped, 1 xfailed (legacy)
# PG real (solo con env local, no compartir secretos):
# python -m alembic -c alembic.ini upgrade head
# python -m pytest tests/test_fase0_p04_concurrency_pg.py -q --rootdir=.
```

## Criterios
| Criterio | Estado | Evidencia | Falta para cerrar |
| CI (local) | **Definido** | `.github/workflows/fase0-check.yml` (compileall + suite Fase 0 SQLite); **no push/ejecución remota** | Ejecutar en CI/HEAD objetivo; job PG con secretos gestionados |
|---|---|---|---|
| F0-01 Sin atajos inseguros | **Parcial→fuerte** | 104 passed Fase 0; scope/404 cross-tenant; no autoaprobación; fail-closed decisiones | Revisión final de excepciones silenciosas residuales + suite/CI en HEAD objetivo |
| F0-02 Fail-closed | **Hecho** | `decision_service` sin bypass; tests `test_fase0_decision_failclosed.py` | — |
| F0-03 Scoping/authz por tenant | **Parcial** | Modelo+migración 0004; filtrado; HTTP 404/403; individuo↔individuo/org↔personal; retiro propio | Matriz completa lectura/aprobación/admin; E2E por acciones gobernadas accesibles a individuo |
| F0-04 Roles/permisos + política HITL personal | **Parcial (política adoptada)** | Roles probados; **política profesional fail-closed**: HITL personal solo ver/retirar, sin autoaprobación ni terceros | Cobertura exhaustiva de matriz y casos legacy compartidos |
| F0-05 Commit único | **Hecho (núcleo)** | lock→ejecutando→handler(`commit=False`)→ejecutada; rollback→`fallida_reintentable` | Trazabilidad fina adicional si se requiere |
| F0-06 Fallo/reintento/estados | **Parcial fuerte** | fallida_reintentable, reintento, cierre por rechazo autorizado, idempotencia ejecutada, sin parcial | Matriz exhaustiva por cada camino de fallo/recuperación |
| F0-07 Idempotencia/externos | **Parcial** | `idempotency_key`/dedup, **0005 aplicada en Neon** (revalidación); sin externos identificados | Outbox solo si hay externos |
| F0-08 Handlers deterministas | **Hecho (núcleo)** | 5/5 registrados, `validate_resumable_handlers()` OK | Validación startup en todos los entornos objetivo |
| F0-09 Reanudación | **Parcial fuerte** | Éxito 5 handlers; rechazo sin efecto; fallo→retry por cada tool reanudable; guards estado | Interrupción/crash real a mitad de camino (infra fault-injection) |
| F0-10 Carrera PG real | **Hecho (0004+0005)** | Neon desechable (2026-11-09): 0005 aplicada; `test_fase0_p04_concurrency_pg.py` **1 passed (10.15s)**, 1 efecto, `executed_at` | Revalidar tras cambios relevantes |
| F0-11 Visibilidad | **Parcial** | `execution_status/result/error`, `executed_at`, estados | UI/observabilidad completa si aplica |
| F0-12 Migraciones/PG | **Hecho (evidencia desechable)** | 0004+**0005** aplicadas en Neon desechable; revalidación OK | Revalidar en entorno objetivo/CI cuando exista |

## Decisiones registradas
- HITL personal (individuo): **ver/retirar** permitido; **aprobar/ejecutar por terceros NO** sin autoridad de gobernanza explícita (fail-closed).
- Analítica separada (post Fase 0): DuckDB consulta/exports, DBT cuando haya marts estables, DVC solo para datasets/modelos reproducibles, Git LFS solo binarios de repo.

## No hacer antes de cerrar
- No integrar CASE/módulos externos (solo contratos/mocks después).
- No usar datos reales/producción.
- No commit/push. No relajar aislamiento.
