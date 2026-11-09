# Resumen de cambios — Fase 0 (local, sin publicar)

## Actualización 2026-11-08 (incremento)
- `tests/conftest.py` — `reset_db` SQLite: `create_all` + borrado de datos por tabla (FK off/on, `sqlite_sequence`) para estabilidad en corridas multi-suite.
- `src/core/agent_harness/approvals.py` — **retiro propio** permitido en `reject()` (`allow_self_withdraw`, solo resolución segura sin ejecución); **autoaprobación sigue bloqueada**.
- `tests/test_fase0_approvals_scope.py` — casos individuo/persona (dominio + HTTP: lista/detalle, no autoaprobar, retiro propio, aislamiento org↔personal), legacy scope, roles, dedup idempotency key.
- `tests/test_fase0_resumption_handlers.py` — idempotencia `cambiar_estado` sin duplicado.
- `tests/test_p03_http_governance.py`, `tests/test_p04_resumption.py` — compatibilidad con conftest/harness.
- `src/core/alembic/versions/0005_approval_idempotency_unique.py` — **nuevo (local)**: unicidad parcial `idempotency_key`; **no aplicado a Neon** (aplicar al revalidar PG).
- Docs: `CAPAS_Y_AVANCE_POOLAR.md` (nuevo), `BACKLOG_PRIORIZADO_POOLAR.md`, `RESULTADOS_TESTS_POOLAR_FASE0.md`, `CAMBIOS_POOLAR_FASE0.md` actualizados.
- **Evidencia:** suites Fase 0/gobernanza → **49 passed (16.05s)** en 1 corrida; PG carrera real previa → **1 passed (11.07s)** (0004).

## Archivos modificados (acumulado)
- `src/core/models.py` — `ApprovalRequest` con campos de ámbito/ejecución (Fase 0).
- `src/core/agent_harness/approvals.py` — scoping/actor, autorización dominio fail-closed, estados ejecución, approve transaccional (lock + handler + commit único), idempotencia/dedup, **retiro propio seguro**.
- `src/main.py` — `_handle_governance` propaga scope/actor; endpoints `/approvals/*` pasan `actor=user`; registro determinista de handlers reanudables (5) con `commit=False`.
- `src/services/decision_service.py` — **P0.2 fail-closed**, `commit` opcional.
- `src/services/iniciativa_service.py` — `commit` opcional.
- `src/services/problema_colectivo_service.py` — `commit` opcional, `_problema_visible`.
- `src/core/ports/evidence.py`, `geo.py`, `semantic.py` — ABCs explícitos.
- `tests/test_governance_regresion.py`, `tests/test_p03_http_governance.py`, `tests/test_p04_resumption.py` — ajustes de autorización/harness.
- `tests/conftest.py` — reset SQLite estable + TRUNCATE PG incluye `approval_requests`.

## Archivos creados (acumulado)
- `src/core/alembic/versions/0004_approval_scope_fase0.py` — aplicada en PG desechable.
- `src/core/alembic/versions/0005_approval_idempotency_unique.py` — local, pendiente en PG al revalidar.
- `tests/test_fase0_approvals_scope.py`, `test_fase0_decision_failclosed.py`, `test_fase0_p04_concurrency_pg.py`, `test_fase0_resumption_handlers.py`, `test_fase0_handlers_registry.py`.
- `AUDITORIA_POOLAR_FASE0_LOCAL.md`, `PLAN_PARCHES_POOLAR_FASE0.md`, `RESULTADOS_TESTS_POOLAR_FASE0.md`, `CAMBIOS_POOLAR_FASE0.md`, `AMPLIACION_ESTRATEGICA_POOLAR.md`, `BACKLOG_PRIORIZADO_POOLAR.md`, `CAPAS_Y_AVANCE_POOLAR.md`.

## Preservado
- `fix_regresion.py` (sin seguimiento, preexistente).

- `.github/workflows/fase0-check.yml` — workflow local Fase 0 (SQLite, sin secretos PG).
- `scripts/check_fase0.ps1`, `FASE0_CHECKLIST_CIERRE.md`.

- `pyproject.toml` — config mínima `ruff`/`mypy` compatible con estado actual (errores graves en `src`).
- Fix preexistente (seguro): `Callable` en `src/core/agent_harness/policy_engine.py`; `func` top-level en `src/services/invitation_service.py`. `ruff check src` (E9,F63,F7,F82) OK.

## Confirmación
**Sin `git commit` ni `git push`. Sin operaciones destructivas de git. Sin modificación de bases de datos reales/producción. Neon es desechable; credenciales solo locales.**
