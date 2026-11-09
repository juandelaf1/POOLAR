# AUDIT READY — POOLAR (`fase0-gobernanza`)

> **Fecha:** 2026-11-09 (generado automáticamente). **Rama:** `fase0-gobernanza` (pusheada). **Objetivo:** estado localmente completo/verificable para auditoría; Fase 0 con controles críticos implementados y evidenciados; **cierre formal pendiente de gates externos**.

## 1) Qué está completo (local, verificable)
- **Fase 0 (núcleo):** fail-closed decisiones, scoping/aislamiento tenant (org/individuo/personal/legacy), HITL personal fail-closed (ver/retirar; sin autoaprobación; sin terceros sin autoridad explícita), atomicidad local (lock→ejecutando→handler `commit=False`→commit único), rollback→`fallida_reintentable`, reintento/cierre por rechazo autorizado, idempotencia/dedup + `0005` (único), auditoría ciclo de vida (`EventoAuditoria` sanitizado), 5 handlers reanudables registrados/validados, guardrails (inputs/serialización/límites, handler faltante fail-closed), políticas declarativas + `policy_warnings` observables.
- **Concurrencia PG real (evidencia previa, desechable):** `alembic upgrade head` hasta 0004+0005 en Neon desechable; `test_fase0_p04_concurrency_pg.py` → **1 passed** (2 aprobadores, 1 efecto, `executed_at`). Requiere `POOLAR_TEST_POSTGRES_URL`/`DATABASE_URL` PostgreSQL local (no en repo).
- **Capacidad core (“lo importante”, gobernada):** E2E `necesidad→problema colectivo→iniciativa→decisión` (auto/HITL, cross-org fail-closed), actividades/historial, export iniciativa con scope, decisión por iniciativa, lecturas fail-closed.
- **Arquitectura modular (CASE + otros proyectos individuales):** contratos genéricos `ModuleManifest/ActorContext/ExecutionRequest/EvidenceEnvelope/CapabilityResult/DecisionProposal/ApprovalRecord` (`src/core/contracts_modules.py`), `contracts_case.py` compat; registro declarativo sin ejecución (`module_registry.py`); `GET /modules/capabilities` (auth, read-only); adaptadores mock/sintéticos no-CASE: `module_mock`, `pilot.logistics_rural`, `service.co2e_estimator`; puerto `ModuleAdapterPort`. **Módulos autoejecutables aislados + componibles**; POOLAR conserva autoridad; sin integración externa/real.
- **Analytics (post-transaccional, sin HITL):** medallion `raw→staging→marts`, export idempotente read-only redactado (`scripts/export_medallion_raw.py`), DuckDB marts (HITL/problemas/iniciativas/decisiones), muestras sintéticas, dbt stubs. Sin PII en exports de muestra; `necesidades` sin vínculo personal.

## 2) Comandos de verificación (auditoría)
```powershell
cd C:\Users\JUAN\Desktop\Proyectos\Trama_Abierta\poolar
python -m compileall -q src tests
python -m ruff check src --select=E9,F63,F7,F82
.\scripts\check_fase0.ps1   # suite canónica ampliada
python -m pytest -q --rootdir=.   # repo completo (ver notas PG)
```
**Evidencia local (2026-11-09):** suite canónica ampliada **98 passed**. Repo completo en entorno sin PG: **173 passed, 1 xfailed, 24 skipped** esperables (tests PG-only skip); sin fallos funcionales en lógica no-PG. (Si aparecen fallos en p01/PG race, confirmar que no hay `POOLAR_TEST_POSTGRES_URL` y que la DB es SQLite de prueba.)

**PG real (solo con env local, sin compartir secretos):**
```powershell
# $env:POOLAR_TEST_POSTGRES_URL, $env:DATABASE_URL, $env:POOLAR_SECRET_KEY
python -m alembic -c alembic.ini upgrade head   # hasta 0005
python -m pytest tests/test_fase0_p04_concurrency_pg.py -q --rootdir=.
```

## 3) Fase 0 — estado honesto
| Área | Estado | Nota |
|---|---|---|
| Controles críticos (scope/authz/fail-closed, HITL, atomicidad/idempotencia, handlers, concurrencia PG evidenciada) | **Fuerte** | Evidencia en tests/código/migraciones 0004-0005. |
| Cierre formal F0-13 | **ABIERTO (bloqueos externos)** | Falta PR/merge + CI verde, job PG con **secrets gestionados** (`docs/CI_PG_SECRETS.md`), matriz E2E exhaustiva por *todas* las acciones/producto donde falte, fault-injection real mid-handler si se exige. |

## 4) Restricciones respetadas
- Sin commit a `main`/merge automático; trabajo en `fase0-gobernanza`. Sin secrets en repo (`.env` gitignored). `fix_regresion.py` preservado sin trackear.
- Sin integración CASE/módulos externos reales; sin datos reales/producción; sin autoridad fuera de POOLAR.
- Cambios aditivos/compatibles donde fue posible (p01 compat Fase 0, shim `contracts_case`).

## 5) Mapa de evidencia clave
- Gobernanza/HITL: `src/core/agent_harness/approvals.py`, `handlers.py`, `action_policies.py`, `src/main.py`, migraciones `0004`/`0005`.
- Tests Fase 0/capacidad: `tests/test_fase0_*`, `tests/test_e2e_*`, `tests/test_p03_http_governance.py`, `tests/test_p04_resumption.py`.
- Modular: `src/core/contracts_modules.py`, `src/core/module_registry.py`, `src/core/adapters/*_mock.py`, `src/core/ports/module_adapter.py`, `tests/test_fase0_module_*`, `tests/test_fase0_contracts_modules.py`.
- Backlog/docs: `BACKLOG_PRIORIZADO_POOLAR.md`, `FASE0_CHECKLIST_CIERRE.md`, `GOBERNANZA_POOLAR.md`, `CAPAS_Y_AVANCE_POOLAR.md`.

## 6) Próximos pasos (cuando haya decisión humana/infra)
1. Abrir PR `fase0-gobernanza` → `dev`/`main`, CI verde, habilitar PG CI con secrets.
2. Integrar primer módulo individual no-CASE por `ModuleManifest`+adaptador mock/sintético (capability-first).
3. Post F0-13: adaptadores HTTP/lib con timeouts/fallos seguros; CASE solo proposal-only; pilotos con datos sintéticos/autorizados.
