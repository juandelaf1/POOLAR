# Plan y parches aplicados — POOLAR Fase 0

## P0.2 — Fail-open en decisiones
- **Problema:** `execute_create_decision_for_initiative` capturaba `Exception` y hacía `pass`, permitiendo continuar tras denegación/error de autorización.
- **Causa raíz:** control defensivo mal implementado alrededor de una comprobación que puede lanzar `HTTPException`/errores.
- **Archivos afectados:** `src/services/decision_service.py`; prueba añadida `tests/test_fase0_decision_failclosed.py`.
- **Solución aplicada:** eliminación del `try/except Exception: pass`; revalidación fail-closed con `_puede_gestionar_iniciativa`; error de autorización => 404/no creación.
- **Decisión arquitectónica:** mantener 404 para no revelar existencia; revalidar en servicio (dominio) además de endpoint.
- **Migraciones:** ninguna.
- **Compatibilidad:** sin cambio de contrato público; comportamiento más seguro.
- **Pruebas de aceptación:** actor de otra org no crea decisión ni evento de auditoría (ejecutada, PASS).

## P0.1 — Ámbito y autorización de aprobaciones (parcial)
- **Problema:** aprobaciones sin tenant/ámbito persistido ni filtrado; endpoints sin autorización completa por rol/ámbito.
- **Archivos afectados:** `src/core/models.py`, `src/core/agent_harness/approvals.py`, `src/main.py` (`_handle_governance`, endpoints `/approvals/*`), migración `src/core/alembic/versions/0004_approval_scope_fase0.py`, tests `tests/test_fase0_approvals_scope.py`.
- **Solución aplicada:** campos de ámbito (`organizacion_id`, proponente, recurso/política/correlación/idempotency) en modelo y migración; `ApprovalManager.create/get/list_pending/approve/reject` aceptan `actor` y aplican checks de scope + rol + no autoaprobación en dominio; respuestas 404 cross-tenant; `_handle_governance` persiste scope desde usuario autenticado.
- **Decisiones:** fail-closed; no confiar en IDs del cuerpo; compatibilidad con llamadas legacy sin `actor` (checks básicos mantenidos) y filas sin `organizacion_id` (acceso limitado/denegado según evidencia).
- **Migraciones:** `0004_approval_scope_fase0` (nuevas columnas nullable + índices). Requiere aplicar en entornos con esquema migrado.
- **Riesgos:** roles de aprobación definidos de forma conservadora (`administrador/coordinador/gestor/responsable/aprobador` + individuo en ámbito personal) — puede requerir ajuste al modelo real de permisos; filas legacy sin scope.
- **Pruebas:** HTTP negativas cross-org y no autoaprobación (PASS). Falta batería completa de roles/casos persona.

## P0.3 — Atomicidad/ejecución/idempotencia (parcial)
- **Problema:** commits separados aprobada/efecto/ejecutada; servicios commit internos.
- **Archivos afectados:** `src/core/agent_harness/approvals.py`, `src/services/problema_colectivo_service.py`, `src/services/iniciativa_service.py`, `src/services/decision_service.py`, `src/main.py` (handlers), tests ajustados.
- **Solución aplicada:** `approve()` usa una transacción con lock: marca `ejecutando`, ejecuta handler, marca `ejecutada`+resultado y hace un commit; en fallo rollback + `fallida_reintentable` en paso separado. Servicios añaden `commit: bool = True`; handlers pasan `commit=False`. Idempotencia: si ya ejecutada/no-op de handler ausente devuelve estado resuelto.
- **Decisiones:** preservar `commit=True` por defecto para compatibilidad con endpoints AUTO_APPROVE existentes; no implementar outbox externo (sin efectos externos identificados).
- **Riesgos:** no todos los caminos están refactorizados; registro de fallo tras rollback es “best effort”; reintentos/recuperación tras reinicio no cubiertos completamente.
- **Pruebas:** reanudación/rechazo/idempotencia básica en SQLite (PASS). Faltan pruebas de fallo entre pasos, interrupción/reinicio, outbox.

## P1.4 — Concurrencia y cobertura de handlers (parcial)
- **Archivos afectados:** `tests/test_p04_resumption.py` (ajustes), `tests/test_p04_concurrency.py` (existente, no carrera real), nuevo `tests/test_fase0_p04_concurrency_pg.py`.
- **Solución aplicada:** prueba PG con barrera y 2 aprobadores simultáneos (skip sin PG); registro de handlers para las 5 operaciones.
- **Riesgos/Pendiente:** **no ejecutada en entorno con PostgreSQL**; falta cobertura de reanudación/fallo por cada handler.

## P1.5 — Handlers/puertos (parcial)
- **Archivos afectados:** `src/main.py`, `src/core/ports/{evidence,geo,semantic}.py`, `tests/test_governance_regresion.py`.
- **Solución aplicada:** ABCs implementados explícitamente; `or True` eliminado; registro de handlers más determinista (sin bloques try/except silenciosos en el reemplazo principal).
- **Pendiente:** validación de arranque para operaciones reanudables declaradas; persistencia real de evidencia; clasificación formal de prototipos en runtime/API.
