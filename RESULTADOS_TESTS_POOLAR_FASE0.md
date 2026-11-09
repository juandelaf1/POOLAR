# Resultados de pruebas — POOLAR Fase 0 (actualizado)

**Fecha:** 2026-11-08  
**Directorio:** `C:\Users\JUAN\Desktop\Proyectos\Trama_Abierta\poolar`  
**Python/pytest:** Python 3.13.12, pytest 9.0.3 (`--rootdir=.`)

## 1) Suites Fase 0 / gobernanza (SQLite, 1 corrida verde, harness estabilizado)

`tests/conftest.py` usa borrado de datos en SQLite (no `drop/create` por test) para estabilidad con imports a nivel módulo.

```powershell
cd C:\Users\JUAN\Desktop\Proyectos\Trama_Abierta\poolar
Remove-Item .pytest_poolar.db,.pytest_poolar.db-shm,.pytest_poolar.db-wal -ErrorAction SilentlyContinue
python -m pytest tests/test_fase0_approvals_scope.py tests/test_fase0_decision_failclosed.py tests/test_fase0_resumption_handlers.py tests/test_fase0_handlers_registry.py tests/test_governance_regresion.py tests/test_p03_http_governance.py tests/test_p04_resumption.py -q --rootdir=.
```

**Resultado:** **75 passed** (scope persona+retiro, aislamiento individuo↔individuo/org, guards, idempotencia, fallos/reintento por cada tool reanudable, cierre seguro de `fallida_reintentable`).

Incluye (además de lo previo): scope HTTP persona/individuo (lista/detalle, no autoaprobación, **retiro/rechazo propio** seguro), aislamiento org↔personal, y test de idempotencia `cambiar_estado`.

## 2) Suite focal previa (histórico, SQLite)

```powershell
python -m pytest tests/test_governance_regresion.py tests/test_p03_http_governance.py tests/test_p04_resumption.py tests/test_fase0_approvals_scope.py tests/test_fase0_decision_failclosed.py tests/test_fase0_resumption_handlers.py tests/test_fase0_handlers_registry.py -q --rootdir=.
```

**Resultado:** **41 passed in 14.99s** (antes de los incrementos de harness/scope/0005).

## 3) PostgreSQL real (Neon, BD desechable, 2026-11-08)

Migraciones aplicadas hasta `0004_approval_scope_fase0`. **Credenciales/BD de prueba deben mantenerse privadas y rotarse/eliminarse cuando no se usen.** `0005_approval_idempotency_unique` **aplicada en Neon (desechable, 2026-11-09)** al revalidar.

```powershell
$env:POOLAR_TEST_POSTGRES_URL="postgresql+psycopg2://...?...sslmode=require"  # solo local
$env:DATABASE_URL=$env:POOLAR_TEST_POSTGRES_URL
$env:POOLAR_SECRET_KEY="clave-local-solo-pruebas-no-produccion"
python -m alembic -c alembic.ini upgrade head
python -m pytest tests/test_fase0_p04_concurrency_pg.py -q --rootdir=.
```

**Resultado (revalidación 2026-11-09):** `alembic upgrade head` → `0004 -> 0005_approval_idempotency_unique` OK (salida redactada); concurrencia **1 passed in 10.15s**.  
**Invariante:** 2 aprobadores compiten (barrera, sesiones independientes, PG real) → **1 solo efecto** (`ProblemaColectivo`), **`executed_at`** registrado, sin duplicado. El perdedor puede recibir error o respuesta idempotente.

## 4) Cobertura demostrada (acumulada)

- P0.2 fail-closed decisiones cross-org.
- P0.1 parcial: scope/tenant en approvals, 404 cross-tenant, no autoaprobación, roles de gestión, dedup `idempotency_key`, **retiro propio** seguro, HTTP persona (scope/aislamiento).
- P0.3 parcial: commit único (lock→`ejecutando`→handler→`ejecutada`), rollback sin efecto parcial, `fallida_reintentable`/reintento, idempotencia ejecutada.
- F0-09 parcial: reanudación éxito 5 handlers; rechazo sin efecto (casos clave); fallo inyectado + reintento; idempotencia `cambiar_estado`.
- P1.5 parcial: ABCs explícitos, sin `or True`, registro/validación handlers.
- F0-10/F0-12: evidencia PG real de carrera (base 0004).

## 5) No ejecutado / pendiente

| Ítem | Estado |
|---|---|
| Aplicar `0005` en Neon / revalidar PG con 0005 | **Hecho (2026-11-09, Neon desechable, env local):** 0005 aplicada + `test_fase0_p04_concurrency_pg.py` 1 passed (10.15s). Revalidar de nuevo solo si cambian aprobaciones/concurrencia/PG. |
| Suite completa repo (SQLite) | **143 passed, 14 skipped, 1 xfailed** (57s). `test_p04_concurrency.py` marcado xfail (legacy; evidencia válida en `test_fase0_p04_concurrency_pg.py` PG real). Sin lint/typecheck configurados en repo. |
| Matriz completa F0-04 (lectura/aprobación/admin, política HITL personal para *aprobar/ejecutar* por tercero, E2E por acciones gobernadas para individuo) | Parcial |
| F0-09 completo (todos los caminos fallo/interrupción/reinicio por handler) | Parcial |
| F0-07 outbox/recuperación efectos externos | No aplica hasta identificar externos |
| `tests/test_p04_concurrency.py` original | No es carrera real desde pendiente; no usar como evidencia de cierre |

## 6) Limitación

No declarar Fase 0 cerrada hasta cumplir puertas F0-04, F0-09 y criterios de evidencia completa. No integrar CASE/módulos externos ni usar datos reales. Neon es recurso temporal; proteger/rotar credenciales.
