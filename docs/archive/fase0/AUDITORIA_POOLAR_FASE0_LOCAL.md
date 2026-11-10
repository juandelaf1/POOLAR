# AuditorÃ­a local Fase 0 â€” POOLAR

**Fecha:** 2026-11-08 (auditorÃ­a/implementaciÃ³n local)  
**Workspace:** `C:\Users\JUAN\Desktop\Proyectos\Trama_Abierta\poolar` (la ruta indicada en el prompt, `C:\Users\JUAN\Desktop\Proyectos\poolar\`, **no existe** en este equipo; se documenta la discrepancia).  
**Alcance:** inspecciÃ³n de cÃ³digo local, contraste con remoto, verificaciÃ³n P0.1â€“P0.3 y P1.4â€“P1.5, correcciones parciales, pruebas ejecutadas. **No se integrÃ³ CASE.**

## 1. Estado real encontrado

| Elemento | Valor |
|---|---|
| Rama local | `main` |
| HEAD local | `18119b1826f89838a12d82e7323a42955ef68087` |
| Remoto | `origin https://github.com/juandelaf1/POOLAR.git` |
| `origin/main` (HEAD remoto observado por `git ls-remote`) | `18119b1826f89838a12d82e7323a42955ef68087` (mismo commit) |
| Estado inicial `git status --short --branch` | `## main...origin/main` + `?? fix_regresion.py` (Ãºnico sin seguimiento preexistente) |
| Diferencia HEAD local vs `origin/main` | Ninguna en nombres (`git diff --name-status HEAD..origin/main` sin salida) |
| Ãšltimos 5 commits | `18119b1 feat(p0.4) reanudacion...`; `e95d5c5 P0.1 ENDPOINTS _handle_governance...`; `7af06aa`; `95ec5b4`; `848db5b` |
| Cambios preexistentes preservados | `fix_regresion.py` (sin seguimiento) **no modificado ni eliminado** |
| Estado final Git | Ver secciÃ³n â€œResumen de cambiosâ€� (modificados + nuevos de esta fase; sin commit/push) |

**Nota sobre referencia del prompt:** el commit pÃºblico conocido `18119b1` coincide con el HEAD local actual. El informe local anterior (`INFORME_CIERRE_P0.md`, 2026-11-02, en `Trama_Abierta`) mencionaba `e95d5c5` con otros sin seguimiento; el estado real actual difiere.

## 2. AuditorÃ­a de hallazgos (cÃ³digo local inspeccionado)

| ID | Hallazgo | Estado inicial (local) | Evidencia (archivos/lÃ­neas, base HEAD 18119b1) | Estado tras cambios | Riesgo residual |
|---|---|---|---|---|---|
| P0.1 | Aislamiento/Ã¡mbito de aprobaciones | **Confirmado** | `src/core/models.py` `ApprovalRequest` sin `organizacion_id`/Ã¡mbito (lÃ­neas ~259-280). `src/core/agent_harness/approvals.py`: `create()` no persistÃ­a Ã¡mbito; `get()` sin tenant (109-133); `list_pending()` global (135-157); `approve/reject` sin scope/rol, solo lock+estado (159-205). `src/main.py` endpoints approvals sin filtro por org/rol (1589-1668). | **Parcialmente corregido** | Campos de Ã¡mbito aÃ±adidos (modelo + migraciÃ³n `0004_approval_scope_fase0`); manager acepta/deriva/persiste Ã¡mbito y filtra `get/list_pending/approve/reject` con actor (fail-closed, 404 para ocultar cross-tenant); endpoints pasan `actor=user`; `_handle_governance` propaga scope. **Pendiente**: modelo de roles/aprobadores por tenant mÃ¡s fino, polÃ­ticas por recurso, lectura de detalle con todos los campos de DTO coherentes, pruebas negativas para *todos* los casos (persona compartida, lectura vs aprobaciÃ³n vs admin), compatibilidad completa con filas legacy sin `organizacion_id`. |
| P0.2 | Fail-open en decisiones | **Confirmado** | `src/services/decision_service.py` `execute_create_decision_for_initiative` (antes): `try: ... raise HTTPException(404)... except Exception: pass` (53-58 aprox. en HEAD). | **Corregido (objetivo principal)** | Eliminado `except Exception: pass`; denegaciÃ³n/errores de autorizaciÃ³n ya no se tragan; revalida con `_puede_gestionar_iniciativa` fail-closed. Test HTTP/servicio negativo aÃ±adido (`tests/test_fase0_decision_failclosed.py`). **Pendiente**: revisiÃ³n exhaustiva de controles similares en todo `src/` (grep no hallÃ³ `except Exception` con pass en `src/services`, pero existen `except Exception: pass` en `src/main.py` en otros contextos no relacionados con autorizaciÃ³n de decisiones; no todos evaluados). |
| P0.3 | Atomicidad + idempotencia de aprobaciones/efecto | **Confirmado (parcial en diseÃ±o)** | `approvals.py` (HEAD): `approve()` hacÃ­a `session.commit()` al marcar aprobada (175) antes de ejecutar handler (178-183); `_execute_approved` commiteaba (230); servicios (`problema_colectivo_service` 103,132; `iniciativa_service` 75; `decision_service` 37,74) hacÃ­an `commit()` internos. | **Parcialmente corregido** | Manager reescrito: flujo con lock, validaciÃ³n, estado `ejecutando`, ejecuciÃ³n del handler en la misma sesiÃ³n, `ejecutado`+`executed_at`+resultado y **un commit final**; rollback + marcado `fallida_reintentable` en transacciÃ³n separada ante excepciÃ³n. Servicios aceptan `commit=False` (por defecto `True` para compatibilidad); handlers registrados pasan `commit=False`. Estados aÃ±adidos (`ejecutando`, `ejecutada`, `fallida_reintentable/terminal`). Idempotencia bÃ¡sica: si ya ejecutada devuelve registro. **Pendiente**: refactor transaccional completo y consistente en *todos* los caminos; outbox + idempotency key efectiva + recuperaciÃ³n para efectos externos (no implementado; no se identificaron efectos externos en esta pasada); pruebas de fallo entre pasos con control fino, reinicio de proceso, `failed_retryable` reintentable con semÃ¡ntica completa. |
| P1.4 | Concurrencia real + cobertura de reanudaciÃ³n | **Confirmado** | `tests/test_p04_concurrency.py`: aprobaba primero en hilo principal y luego lanzaba 2 hilos que reintentaban (no carrera real simultÃ¡nea desde pendiente). `tests/test_p04_resumption.py`: declaraba cubrir solo `create_problema_colectivo`. | **Parcialmente corregido** | Tests p04 existentes ajustados a reglas de no autoaprobaciÃ³n/actor (siguen sin ser carrera real PG). AÃ±adido `tests/test_fase0_p04_concurrency_pg.py` con **barrera + 2 aprobadores simultÃ¡neos + sesiones/conexiones independientes + PostgreSQL real** (skip si no hay PG). Handlers registrados para las 5 operaciones nombradas (`create_problema_colectivo`, `create_iniciativa`, `cambiar_estado_problema_colectivo`, `create_decision`, `create_decision_for_initiative`). **Pendiente**: ejecutar prueba PG real y demostrar 1 efecto/1 resultado; cubrir reanudaciÃ³n/fallo/reintento para *cada* handler con evidencia; interrupciÃ³n entre commits. **No validado en este entorno (sin PostgreSQL accesible).** |
| P1.5 | Handlers/puertos/adaptadores prototipo | **Confirmado (parcial)** | `main.py`: registros con `try/except Exception: pass` y mutaciÃ³n directa de `RESUMABLE_HANDLERS`, placeholders sobrescritos (1569-1745 aprox.). `src/core/ports/evidence.py`: `EvidenceService` no heredaba `EvidencePort`, persistencia en memoria. `geo.py`: `SimpleGeoService`/`SimpleOptimizationService` sin herencia ABC explÃ­cita; heurÃ­sticas. `semantic.py`: `LocalSemanticSearchService` sin herencia explÃ­cita; hash (no embeddings productivos). `tests/test_governance_regresion.py:144`: `assert isinstance(EvidenceService(), EvidencePort) or True`. | **Parcialmente corregido** | Eliminado `or True`; servicios heredan explÃ­citamente de sus ABC (`EvidencePort`, `GeoPort`, `OptimizationPort`, `SemanticSearchPort`). Registro de handlers en `main.py` consolidado de forma determinista para las operaciones principales (sin silenciamiento en el bloque nuevo; asignaciÃ³n explÃ­cita). **Pendiente**: registro centralizado completo con validaciÃ³n al arranque de operaciones declaradas reanudables vs handlers reales; detecciÃ³n estricta de duplicados/sobrescrituras accidentales en toda la app; persistencia/procedencia real de evidencias; pruebas de contratos exhaustivas; no presentar prototipos como productivos (documentado). |

## 3. Hallazgos adicionales observados
- `src/services/problema_colectivo_service.py` llamaba `_problema_visible` sin definiciÃ³n local (riesgo `NameError`); aÃ±adido wrapper.
- `test_p03_http_governance.py` y `test_p04_*` contenÃ­an flujos de aprobaciÃ³n con el mismo actor proponente (incompatibles con no autoaprobaciÃ³n, ahora reforzada); corregidos para usar aprobadores autorizados distintos.
- `conftest.py` (PostgreSQL) no trunca `approval_requests` en su lista de `TRUNCATE`; puede afectar pruebas PG si se ejecutan con ese conftest (pendiente de ajuste).

## 4. Cumplimiento de restricciones
- Sin `git reset --hard`, sin `git clean`, sin eliminar `fix_regresion.py`, sin sobrescribir cambios locales no relacionados, sin checkout destructivo, sin commit, sin push, sin modificaciÃ³n de BD real/datos de usuario, sin exponer secretos.

## 5. Estado de Fase 0
**ABIERTA.** Se han cerrado/corregido de forma demostrable: P0.2 (fail-open principal) y parte de P1.5 (ABCs/`or True`, registro mÃ¡s determinista) y se han implementado mejoras parciales de P0.1/P0.3/P1.4. No se cumplen todos los criterios de cierre (especialmente autorizaciÃ³n/roles multi-tenant completos, atomicidad+outbox+recuperaciÃ³n completa, y **concurrencia PG real ejecutada**).

## 6. Actualización de avance (misma sesión, verificación posterior)
- **Tests focales Fase 0:** 41 passed (SQLite) — ver RESULTADOS_TESTS_POOLAR_FASE0.md.
- **Correcciones adicionales:** cambiar_estado endpoint sin 
esponse_model rígido y delega al servicio (auto-approve); datetime.utcnow() reemplazado por helper UTC-naive en approvals; deduplicación por idempotency_key en ApprovalManager.create().
- **Cobertura añadida:** resumption éxito 5 handlers; rechazo sin efecto (iniciativa/decisión); fallo inyectado sin efecto parcial + allida_reintentable; reintento exitoso; idempotencia post-ejecución; roles observador/miembro denegados y coordinador/gestor/responsable/aprobador/admin permitidos (casos básicos org); validación alidate_resumable_handlers().
- **Sigue abierto:** F0-10 concurrencia PG real (sin PG), matriz completa roles/persona/legacy, outbox/recuperación externa, cobertura fallo/reinicio por todos los caminos, aplicación migración 0004 en PG.

## 7. Evidencia PostgreSQL real (2026-11-08)
- **Entorno:** Neon Postgres desechable; migraciones lembic upgrade head hasta  004_approval_scope_fase0 aplicadas.
- **Comando:** python -m pytest tests/test_fase0_p04_concurrency_pg.py -q --rootdir=.
- **Resultado:** **1 passed (11.07s)**. Bajo carrera real (2 aprobadores, barrera, sesiones independientes), se verificó **1 único efecto** (ProblemaColectivo) y executed_at registrado, sin duplicado.
- **Acción de seguridad:** rotar/eliminar credencial y BD de prueba (la conexión fue expuesta en el chat).
- **Impacto:** F0-10/F0-12 cuentan con evidencia; Fase 0 **sigue abierta** por ítems pendientes (F0-04 matriz completa/persona/legacy, cobertura total F0-09, F0-07 outbox/recuperación si aplica, cierres residuales).
