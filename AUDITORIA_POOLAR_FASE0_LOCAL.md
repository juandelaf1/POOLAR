# Auditoría local Fase 0 — POOLAR

**Fecha:** 2026-11-08 (auditoría/implementación local)  
**Workspace:** `C:\Users\JUAN\Desktop\Proyectos\Trama_Abierta\poolar` (la ruta indicada en el prompt, `C:\Users\JUAN\Desktop\Proyectos\poolar\`, **no existe** en este equipo; se documenta la discrepancia).  
**Alcance:** inspección de código local, contraste con remoto, verificación P0.1–P0.3 y P1.4–P1.5, correcciones parciales, pruebas ejecutadas. **No se integró CASE.**

## 1. Estado real encontrado

| Elemento | Valor |
|---|---|
| Rama local | `main` |
| HEAD local | `18119b1826f89838a12d82e7323a42955ef68087` |
| Remoto | `origin https://github.com/juandelaf1/POOLAR.git` |
| `origin/main` (HEAD remoto observado por `git ls-remote`) | `18119b1826f89838a12d82e7323a42955ef68087` (mismo commit) |
| Estado inicial `git status --short --branch` | `## main...origin/main` + `?? fix_regresion.py` (único sin seguimiento preexistente) |
| Diferencia HEAD local vs `origin/main` | Ninguna en nombres (`git diff --name-status HEAD..origin/main` sin salida) |
| Últimos 5 commits | `18119b1 feat(p0.4) reanudacion...`; `e95d5c5 P0.1 ENDPOINTS _handle_governance...`; `7af06aa`; `95ec5b4`; `848db5b` |
| Cambios preexistentes preservados | `fix_regresion.py` (sin seguimiento) **no modificado ni eliminado** |
| Estado final Git | Ver sección “Resumen de cambios” (modificados + nuevos de esta fase; sin commit/push) |

**Nota sobre referencia del prompt:** el commit público conocido `18119b1` coincide con el HEAD local actual. El informe local anterior (`INFORME_CIERRE_P0.md`, 2026-11-02, en `Trama_Abierta`) mencionaba `e95d5c5` con otros sin seguimiento; el estado real actual difiere.

## 2. Auditoría de hallazgos (código local inspeccionado)

| ID | Hallazgo | Estado inicial (local) | Evidencia (archivos/líneas, base HEAD 18119b1) | Estado tras cambios | Riesgo residual |
|---|---|---|---|---|---|
| P0.1 | Aislamiento/ámbito de aprobaciones | **Confirmado** | `src/core/models.py` `ApprovalRequest` sin `organizacion_id`/ámbito (líneas ~259-280). `src/core/agent_harness/approvals.py`: `create()` no persistía ámbito; `get()` sin tenant (109-133); `list_pending()` global (135-157); `approve/reject` sin scope/rol, solo lock+estado (159-205). `src/main.py` endpoints approvals sin filtro por org/rol (1589-1668). | **Parcialmente corregido** | Campos de ámbito añadidos (modelo + migración `0004_approval_scope_fase0`); manager acepta/deriva/persiste ámbito y filtra `get/list_pending/approve/reject` con actor (fail-closed, 404 para ocultar cross-tenant); endpoints pasan `actor=user`; `_handle_governance` propaga scope. **Pendiente**: modelo de roles/aprobadores por tenant más fino, políticas por recurso, lectura de detalle con todos los campos de DTO coherentes, pruebas negativas para *todos* los casos (persona compartida, lectura vs aprobación vs admin), compatibilidad completa con filas legacy sin `organizacion_id`. |
| P0.2 | Fail-open en decisiones | **Confirmado** | `src/services/decision_service.py` `execute_create_decision_for_initiative` (antes): `try: ... raise HTTPException(404)... except Exception: pass` (53-58 aprox. en HEAD). | **Corregido (objetivo principal)** | Eliminado `except Exception: pass`; denegación/errores de autorización ya no se tragan; revalida con `_puede_gestionar_iniciativa` fail-closed. Test HTTP/servicio negativo añadido (`tests/test_fase0_decision_failclosed.py`). **Pendiente**: revisión exhaustiva de controles similares en todo `src/` (grep no halló `except Exception` con pass en `src/services`, pero existen `except Exception: pass` en `src/main.py` en otros contextos no relacionados con autorización de decisiones; no todos evaluados). |
| P0.3 | Atomicidad + idempotencia de aprobaciones/efecto | **Confirmado (parcial en diseño)** | `approvals.py` (HEAD): `approve()` hacía `session.commit()` al marcar aprobada (175) antes de ejecutar handler (178-183); `_execute_approved` commiteaba (230); servicios (`problema_colectivo_service` 103,132; `iniciativa_service` 75; `decision_service` 37,74) hacían `commit()` internos. | **Parcialmente corregido** | Manager reescrito: flujo con lock, validación, estado `ejecutando`, ejecución del handler en la misma sesión, `ejecutado`+`executed_at`+resultado y **un commit final**; rollback + marcado `fallida_reintentable` en transacción separada ante excepción. Servicios aceptan `commit=False` (por defecto `True` para compatibilidad); handlers registrados pasan `commit=False`. Estados añadidos (`ejecutando`, `ejecutada`, `fallida_reintentable/terminal`). Idempotencia básica: si ya ejecutada devuelve registro. **Pendiente**: refactor transaccional completo y consistente en *todos* los caminos; outbox + idempotency key efectiva + recuperación para efectos externos (no implementado; no se identificaron efectos externos en esta pasada); pruebas de fallo entre pasos con control fino, reinicio de proceso, `failed_retryable` reintentable con semántica completa. |
| P1.4 | Concurrencia real + cobertura de reanudación | **Confirmado** | `tests/test_p04_concurrency.py`: aprobaba primero en hilo principal y luego lanzaba 2 hilos que reintentaban (no carrera real simultánea desde pendiente). `tests/test_p04_resumption.py`: declaraba cubrir solo `create_problema_colectivo`. | **Parcialmente corregido** | Tests p04 existentes ajustados a reglas de no autoaprobación/actor (siguen sin ser carrera real PG). Añadido `tests/test_fase0_p04_concurrency_pg.py` con **barrera + 2 aprobadores simultáneos + sesiones/conexiones independientes + PostgreSQL real** (skip si no hay PG). Handlers registrados para las 5 operaciones nombradas (`create_problema_colectivo`, `create_iniciativa`, `cambiar_estado_problema_colectivo`, `create_decision`, `create_decision_for_initiative`). **Pendiente**: ejecutar prueba PG real y demostrar 1 efecto/1 resultado; cubrir reanudación/fallo/reintento para *cada* handler con evidencia; interrupción entre commits. **No validado en este entorno (sin PostgreSQL accesible).** |
| P1.5 | Handlers/puertos/adaptadores prototipo | **Confirmado (parcial)** | `main.py`: registros con `try/except Exception: pass` y mutación directa de `RESUMABLE_HANDLERS`, placeholders sobrescritos (1569-1745 aprox.). `src/core/ports/evidence.py`: `EvidenceService` no heredaba `EvidencePort`, persistencia en memoria. `geo.py`: `SimpleGeoService`/`SimpleOptimizationService` sin herencia ABC explícita; heurísticas. `semantic.py`: `LocalSemanticSearchService` sin herencia explícita; hash (no embeddings productivos). `tests/test_governance_regresion.py:144`: `assert isinstance(EvidenceService(), EvidencePort) or True`. | **Parcialmente corregido** | Eliminado `or True`; servicios heredan explícitamente de sus ABC (`EvidencePort`, `GeoPort`, `OptimizationPort`, `SemanticSearchPort`). Registro de handlers en `main.py` consolidado de forma determinista para las operaciones principales (sin silenciamiento en el bloque nuevo; asignación explícita). **Pendiente**: registro centralizado completo con validación al arranque de operaciones declaradas reanudables vs handlers reales; detección estricta de duplicados/sobrescrituras accidentales en toda la app; persistencia/procedencia real de evidencias; pruebas de contratos exhaustivas; no presentar prototipos como productivos (documentado). |

## 3. Hallazgos adicionales observados
- `src/services/problema_colectivo_service.py` llamaba `_problema_visible` sin definición local (riesgo `NameError`); añadido wrapper.
- `test_p03_http_governance.py` y `test_p04_*` contenían flujos de aprobación con el mismo actor proponente (incompatibles con no autoaprobación, ahora reforzada); corregidos para usar aprobadores autorizados distintos.
- `conftest.py` (PostgreSQL) no trunca `approval_requests` en su lista de `TRUNCATE`; puede afectar pruebas PG si se ejecutan con ese conftest (pendiente de ajuste).

## 4. Cumplimiento de restricciones
- Sin `git reset --hard`, sin `git clean`, sin eliminar `fix_regresion.py`, sin sobrescribir cambios locales no relacionados, sin checkout destructivo, sin commit, sin push, sin modificación de BD real/datos de usuario, sin exponer secretos.

## 5. Estado de Fase 0
**ABIERTA.** Se han cerrado/corregido de forma demostrable: P0.2 (fail-open principal) y parte de P1.5 (ABCs/`or True`, registro más determinista) y se han implementado mejoras parciales de P0.1/P0.3/P1.4. No se cumplen todos los criterios de cierre (especialmente autorización/roles multi-tenant completos, atomicidad+outbox+recuperación completa, y **concurrencia PG real ejecutada**).

## 6. Actualizaci�n de avance (misma sesi�n, verificaci�n posterior)
- **Tests focales Fase 0:** 41 passed (SQLite) � ver RESULTADOS_TESTS_POOLAR_FASE0.md.
- **Correcciones adicionales:** cambiar_estado endpoint sin esponse_model r�gido y delega al servicio (auto-approve); datetime.utcnow() reemplazado por helper UTC-naive en approvals; deduplicaci�n por idempotency_key en ApprovalManager.create().
- **Cobertura a�adida:** resumption �xito 5 handlers; rechazo sin efecto (iniciativa/decisi�n); fallo inyectado sin efecto parcial + allida_reintentable; reintento exitoso; idempotencia post-ejecuci�n; roles observador/miembro denegados y coordinador/gestor/responsable/aprobador/admin permitidos (casos b�sicos org); validaci�n alidate_resumable_handlers().
- **Sigue abierto:** F0-10 concurrencia PG real (sin PG), matriz completa roles/persona/legacy, outbox/recuperaci�n externa, cobertura fallo/reinicio por todos los caminos, aplicaci�n migraci�n 0004 en PG.

## 7. Evidencia PostgreSQL real (2026-11-08)
- **Entorno:** Neon Postgres desechable; migraciones lembic upgrade head hasta  004_approval_scope_fase0 aplicadas.
- **Comando:** python -m pytest tests/test_fase0_p04_concurrency_pg.py -q --rootdir=.
- **Resultado:** **1 passed (11.07s)**. Bajo carrera real (2 aprobadores, barrera, sesiones independientes), se verific� **1 �nico efecto** (ProblemaColectivo) y executed_at registrado, sin duplicado.
- **Acci�n de seguridad:** rotar/eliminar credencial y BD de prueba (la conexi�n fue expuesta en el chat).
- **Impacto:** F0-10/F0-12 cuentan con evidencia; Fase 0 **sigue abierta** por �tems pendientes (F0-04 matriz completa/persona/legacy, cobertura total F0-09, F0-07 outbox/recuperaci�n si aplica, cierres residuales).
