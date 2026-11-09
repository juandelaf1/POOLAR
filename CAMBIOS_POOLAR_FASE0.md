# Resumen de cambios — Fase 0 (local, sin publicar)

## Estado vigente (2026-11-09)
- **Evidencia:** 76 passed (Fase 0/gobernanza, 1 corrida) + 142 passed/14 skipped/1 xfailed (repo) + `compileall`/`ruff` (E9,F63,F7,F82) OK. **Neon (desechable):** migraciones 0004+0005 aplicadas, `test_fase0_p04_concurrency_pg.py` → 1 passed (10.15s), 1 efecto/`executed_at`.
- **Núcleo:** fail-closed, scope multi-tenant (org↔org, individuo↔individuo, org↔personal), no autoaprobación, lectura vs gestión, retiro propio HITL personal (política adoptada), atomicidad, `fallida_reintentable`/reintento/cierre seguro, idempotencia+dedup, caducidad, 5 handlers reanudables validados.
- **Seguridad/redacción:** `src/core/security.py` mejora `sanitize_for_log` (URLs DB/secretos) + `tests/test_fase0_security.py`.
- **Guardrails/harness:** validación `tool_name`/`inputs` (dict, serializable, ≤256KB), handler faltante no se marca ejecutado (fail-closed), auditoría de intento preservada en fallo, `EventoAuditoria` en ciclo de vida HITL, políticas declarativas por acción (`action_policies.py`).
- **Contratos/adapter (sin integración):** `src/core/contracts_case.py`, `src/core/adapters/case_mock.py` (solo propone), tests `test_fase0_contracts_case.py`, `test_fase0_case_adapter_mock.py`.
- **Proceso/docs:** `GOBERNANZA_POOLAR.md`, `CAPAS_Y_AVANCE_POOLAR.md` (analítica DVC/LFS/DBT), `FASE0_CHECKLIST_CIERRE.md`, scripts `check_fase0.ps1`/`set_neon_test_url.ps1`, `.github/workflows/fase0-check.yml` (SQLite + job PG `if:false`), `pyproject.toml`.
- **Fixes preexistentes seguros:** `Callable` en `policy_engine.py`, `func` top-level en `invitation_service.py`.

## Archivos clave (acumulado)
- Core: `src/core/agent_harness/{approvals,handlers,action_policies,policy_engine}.py`, `src/core/models.py`, `src/core/ports/*`, `src/core/contracts_case.py`, migraciones `0004`/`0005`.
- API/servicios: `src/main.py`, `src/services/{decision,iniciativa,problema_colectivo,invitation}_service.py`.
- Tests Fase 0: `tests/test_fase0_{action_policies,contracts_case,harness_guardrails,role_matrix,approvals_scope,decision_failclosed,resumption_handlers,handlers_registry,p04_concurrency_pg}.py` + ajustes `conftest/governance_regresion/p03/p04*`.
- Docs: auditoría/plan/resultados/cambios/capas/gobernanza/checklist/backlog/ampliación.

## Confirmación
**Sin `git commit` ni `git push` automáticos en este resumen; usar flujo Git acordado. Sin `.env`/db reales en commits. Neon desechable; credenciales locales.**
