# Backlog priorizado — POOLAR (capability-based)

**Fecha:** 2026-11-08  
**Base:** `AUDITORIA_POOLAR_FASE0_LOCAL.md`, `RESULTADOS_TESTS_POOLAR_FASE0.md`, `AMPLIACION_ESTRATEGICA_POOLAR.md`.  
**Reglas:** unidad = **capacidad** (no repo); no integrar CASE ni dominios externos antes de Fase 0; no datos reales sin puertas de aceptación; evidencia verificable (código/líneas, tests, CI del HEAD, licencias/procedencia).

## Convenciones
- **Estado:** `OPEN` | `PARTIAL` | `DONE` | `BLOCKED` (entorno/evidencia externa)
- **Evidencia requerida:** archivo(s)+línea(s)/diff, comando, resultado, entorno/BD, HEAD/CI, o decisión documentada.
- **Prioridad:** P0 (bloquea núcleo/seguridad/ejecución), P1 (pre-piloto/contratos), P2 (dominio/piloto), P3 (ecosistema/escala).

---

## Fase 0 — Cierre del núcleo (P0) — **ABIERTA**

| ID | Capacidad / ítem | Dep. | Criterios de aceptación verificables | Evidencia requerida | Estado |
|---|---|---|---|---|---|
| F0-01 | Baseline reproducible | - | HEAD/rama/remoto, cambios locales preservados, comparación con remoto documentada. | `git` outputs; `AUDITORIA_POOLAR_FASE0_LOCAL.md`. | **DONE** |
| F0-02 | Decisiones fail-closed (P0.2) | F0-01 | Ningún `except Exception: pass` que trague denegación en controles de decisión; acceso cross-org no crea decisión ni auditoría. | `src/services/decision_service.py` diff; `tests/test_fase0_decision_failclosed.py` PASS. | **DONE** (alcance principal) |
| F0-03 | Ámbito tenant de aprobaciones (P0.1) | F0-01 | Cada aprobación persiste ámbito (tenant/org, proponente, recurso/política/correlación/idempotency); `get/list/approve/reject` filtran por ámbito; 404 cross-tenant. | Modelo + migración `0004_approval_scope_fase0`; manager/endpoints; tests scope PASS. | **PARTIAL** |
| F0-04 | Roles/permisos de aprobación | F0-03 | Roles que pueden aprobar/rechazar definidos y aplicados (lectura vs aprobación vs admin separados); individuo/persona y org cubiertos; no permisos implícitos. | Matriz rol→acción; pruebas HTTP negativas por rol/tenant/persona compartida. | **PARTIAL** (roles `miembro/observador` denegados; `coordinador/gestor/responsable/aprobador/admin` permitidos; legacy sin `organizacion_id` solo proponente; **HTTP persona/individuo**: lista/detalle OK, autoaprobación denegada, **retiro propio permitido** (sin ejecución), aislamiento org↔personal. **Política profesional adoptada (fail-closed):** HITL en ámbito personal **no es aprobable/ejecutable por terceros** sin autoridad de gobernanza explícita; solo vista/retiro por proponente. Pendiente: matriz completa lectura/aprobación/admin + E2E por acciones gobernadas accesibles a individuo.) |
| F0-05 | No autoaprobación en dominio | F0-03 | Proponente (y actor proponente equivalente) no puede aprobar/rechazar; enforced en dominio, no solo endpoint. | Tests dominio+HTTP; manager `actor`. | **PARTIAL** (implementado; reforzar casos equivalentes) |
| F0-06 | Atomicidad local aprobación+efecto (P0.3) | F0-03 | Efecto local y estado de ejecución en unidad transaccional verificable (sin ventana commit-separado para el caso local estándar); estados explícitos. | Manager/servicios/handlers; pruebas de fallo inyectado entre pasos. | **PARTIAL** (handler con `commit=False` + commit único en manager; test de fallo inyectado confirma rollback sin efecto parcial y estado `fallida_reintentable`. Falta: fallo en puntos intermedios finos, reintento completo, preservación total de trazabilidad en fallo separado) |
| F0-07 | Outbox + idempotencia efectos externos | F0-06 | Efectos externos usan outbox transaccional, idempotency key, estados recuperables; no "exactly once" sin idempotencia receptora. | Diseño + implementación + pruebas de reintento/duplicado/recuperación. | **PARTIAL** (campos `idempotency_key/correlation_id` + dedup; `0005_approval_idempotency_unique` **aplicada en Neon (desechable)** al revalidar; test idempotencia `cambiar_estado` OK; outbox/recuperación externos no implementado; sin efectos externos identificados aún) |
| F0-08 | Handlers reanudables deterministas (P1.5) | F0-01 | Registro determinista; sin `except Exception: pass` que oculte registro; sin placeholders que sobrescriban handlers reales; operaciones declaradas reanudables tienen handler válido o se marcan no soportadas al arranque. | `src/main.py`/handler registry; validación startup; pruebas. | **PARTIAL** (registro consolidado en `main.py`; `validate_resumable_handlers()` + `test_fase0_handlers_registry.py` PASS; falta validación estricta en arranque para todas las operaciones declaradas/no soportadas) |
| F0-09 | Cobertura reanudación por handler (P1.4) | F0-06,F0-08 | `create_problema_colectivo`, `create_iniciativa`, `cambiar_estado_problema_colectivo`, `create_decision`, `create_decision_for_initiative`: éxito, rechazo, fallo, reintento/idempotencia, sin duplicar efecto. | Tests por handler (HTTP/servicio) con resultados. | **PARTIAL** (éxito/reanudación PASS para los **5 handlers** en `test_p04_resumption.py` + `test_fase0_resumption_handlers.py`; rechazo/idempotencia básica en PC; fallos inyectados/reintentos/interrupción por handler pendientes) |
| F0-10 | Concurrencia PostgreSQL real (P1.4) | F0-06,F0-09 | 2 aprobadores compiten simultáneamente (barrera) desde **pendiente** sobre **PG real**, sesiones independientes: exactamente 1 aprobación válida, **1 efecto**, 1 resultado persistido, sin estado incoherente. | Ejecución de `tests/test_fase0_p04_concurrency_pg.py` con `POOLAR_TEST_POSTGRES_URL`, esquema migrado, log de resultado. | **DONE (evidencia 2026-11-08)**: Neon Postgres desechable, `alembic upgrade head` hasta `0004_approval_scope_fase0`, `python -m pytest tests/test_fase0_p04_concurrency_pg.py -q --rootdir=.` → **`1 passed`** (11.07s). Invariante verificado: **1 `ProblemaColectivo`**, `executed_at` registrado; sin duplicado bajo carrera (el perdedor puede recibir error/respuesta idempotente según implementación). *Rotar/eliminar credencial/BD de prueba.* |
| F0-11 | Contratos/adaptadores verificables (P1.5) | F0-01 | ABCs implementados/validados sin `or True`; prototipos etiquetados (no optimización matemática, no búsqueda semántica productiva, no persistencia real si no lo es). | `ports/*`, tests de contrato; docs. | **PARTIAL** (`or True` eliminado, herencia ABC; persistencia/evidencia y contratos exhaustivos pendientes) |
| F0-12 | Compatibilidad migraciones/PG | F0-03 | `0004_approval_scope_fase0` aplicada en PG de pruebas; conftest PG trunca tablas nuevas (`approval_requests`) según necesidad. | Comando migración + prueba PG. | **DONE (evidencia 2026-11-08/09)**: `alembic upgrade head` aplicado en Postgres real (Neon desechable) hasta **`0005_approval_idempotency_unique`**; `test_fase0_p04_concurrency_pg.py` → **1 passed (10.15s)** tras 0005. Conftest PG incluye `approval_requests`. |
| F0-13 | Puerta de salida Fase 0 | F0-04–F0-12 | Todos los criterios del prompt de Fase 0 cumplidos con evidencia; sin declaración por aproximación. | Checklist firmado + resultados tests PG + revisión. | **OPEN** |

---

## Principio de arquitectura modular (transversal)
- **POOLAR = núcleo gobernado/orquestador:** identidad/tenant, permisos, HITL/aprobaciones, auditoría, ejecución autorizada. Conserva **autoridad final**.
- **Módulos = productos separados y componibles** (CASE **y otros proyectos individuales/integraciones**): cada uno **autoejecutable** de forma independiente (propio ciclo de vida, config, tests, datos de prueba, interfaz/contrato) y **componible** con POOLAR (y entre sí solo vía contratos/orquestación gobernada).
- **Integración por capacidad, no por acoplamiento de repos:** unidad = capacidad; un módulo expone capacidades declaradas (`ModuleManifest`) y retorna resultados/propuestas (`CapabilityResult`/`DecisionProposal`/`EvidenceEnvelope`), **nunca** autoridad de ejecución ni acceso directo a BD de POOLAR.
- **Aislamiento:** sin acceso BD compartida, sin secretos cruzados, sin bypass de HITL/tenant; fallos/timeouts degradan seguro. Datos reales solo con puertas (consentimiento/procedencia/licencia).
- **Regla:** no integrar módulos externos antes de **F0-13**; primero contratos/mocks/sintético, luego adaptadores validados.

## Fase 1 - Contratos modulares, mecanismo común y adaptadores (P1)

| ID | Capacidad / Ítem | Dep. | Criterios de aceptación verificables | Evidencia requerida | Estado |
|---|---|---|---|---|---|
| C1-01 | Contratos versionados (genéricos de módulo) | F0-13 | `ModuleManifest`, `ActorContext`, `ExecutionRequest`, `EvidenceEnvelope`, `CapabilityResult`, `DecisionProposal`, `ApprovalRecord`; válidos para **cualquier** módulo (CASE u otros); tests. | Pydantic/JSON Schema + tests compat. | **PARTIAL** (stubs `contracts_case.py`; generalizar) |
| C1-02 | Registro/descubrimiento de módulos y capacidades | C1-01 | Catálogo declarativo (manifest), versiones, capacidades, permisos, health; selección por capacidad; sin ejecución implícita. | Contrato + tests. | OPEN |
| C1-03 | Adaptador CASE (primera integración, una vía) | C1-01 | Lib versionada o adaptador HTTP interno estable; timeouts/fallos recuperables; salida = **propuesta**. | Adaptador + tests. | **PARTIAL** (mock `case_mock.py`) |
| C1-04 | Adaptadores para otros proyectos/módulos (patrón repetible) | C1-01,C1-02 | Plantilla/SDK; cada módulo integrable por mismo patrón (**autoejecutable aislado + compuesto**); CASE no es caso especial. | Plantilla + ≥1 adaptador no-CASE mock/sintético. | OPEN |
| C1-05 | Autoridad conservada en POOLAR (todos los módulos) | C1-03,C1-04 | Salidas = propuestas/resultados; POOLAR valida actor/tenant/permiso/consentimiento; HITL/ejecución solo bajo política; auditoría correlacionada. | Tests: sin ejecución sin aprobación; no autoaprobación. | OPEN |
| C1-06 | Datos sintéticos + providers mock (por módulo) | C1-01 | Sin datos reales; providers mock por módulo; etiquetado explícito. | Fixtures + E2E controlados. | **PARTIAL** (CASE; generalizar) |
| C1-07 | Mecanismo común validado | C1-01,F0-13 | Flujo común **necesidades, capacidades, recursos y soluciones** con evidencia/procedencia/estados; multi-tenant/HITL/composición. | Diseño + API/servicios + tests. | OPEN |

---

## Fase 2 — Piloto integral: logística rural (P2)

| ID | Capacidad / ítem | Dep. | Criterios de aceptación verificables | Evidencia requerida | Estado |
|---|---|---|---|---|---|
| L2-01 | Selección de capacidades (no repos) | C1-05 | Mapa de capacidades necesarias (matching, rutas/costes, participación territorial, evidencia); candidatos evaluados con estado `candidate/experimental/validated`. | Matriz de evaluación por capacidad. | OPEN |
| L2-02 | Puertas de candidatos | L2-01 | Candidatos (p. ej. EnRuta/Parada-Viva/DashLogistics como referencia) superan seguridad, licencias/PI, procedencia datos, CI del HEAD, contratos, aislamiento; secretos fuera de código/historial. | Checklist por candidato + evidencia. | OPEN |
| L2-03 | Vertical logística rural controlado | L2-02,C1-03 | Caso de uso verificable, datos sintéticos o autorizados etiquetados, sin ejecución sin aprobación POOLAR, exportación/auditoría, métricas de resultado (no vanity). | Pruebas + informe de piloto + trazabilidad. | OPEN |

---

## Fase 3 — Sostenibilidad / CO2e auditable (P2)

| ID | Capacidad / ítem | Dep. | Criterios de aceptación verificables | Evidencia requerida | Estado |
|---|---|---|---|---|---|
| S3-01 | Auditoría Devera_DS (capacidad) | F0-13 | Metodología, factores, unidades, límites, licencia, procedencia, reproducibilidad y calidad verificados; solo reutilizar lo validado. | Informe de auditoría técnica+metodológica. | OPEN |
| S3-02 | Servicio CO2e transversal | S3-01,C1-01 | Estimaciones/comparaciones con factores versionados, incertidumbre, distinción medido vs estimado, resultados reproducibles; sin cifra opaca. | Contrato `EvidenceEnvelope/CapabilityResult` + tests + versionado metodología. | OPEN |
| S3-03 | Uso por CASE como factor | S3-02,C1-03 | CASE puede consumir CO2e como factor de evaluación vía propuesta; decisión/ejecución siguen bajo POOLAR. | Prueba de integración controlada. | OPEN |

---

## Fase 4 — Recursos compartidos / ecosistema (P2–P3)

| ID | Capacidad / ítem | Dep. | Criterios de aceptación verificables | Evidencia requerida | Estado |
|---|---|---|---|---|---|
| R4-01 | Modelo común de recursos | C1-05 | Catálogo, titularidad, disponibilidad, reservas, asignación, priorización, trazabilidad; tipos: consumible / activo reutilizable / capacidad limitada. | Diseño + tests + migraciones controladas. | OPEN |
| R4-02 | Caso concreto agua o energía | R4-01,S3-02 | Un caso acotado, sin modelo único forzado, sin suplantar competencias de operadores/autoridades; políticas/HITL. | Piloto controlado + evidencia. | OPEN |
| E4-01 | Ecosistema desarrolladores | C1-01,F0-13 | API versionada, SDK, `ModuleManifest`, sandbox, tests de conformidad, permisos limitados, revisión seguridad/licencias; módulos aislados, **sin acceso BD** y **sin autoridad de aprobación**. | Docs + plataforma + pruebas de aislamiento. | OPEN |

---

## Secuencia inmediata recomendada (actualizada, 2026-11-09)
> Detalle ampliado en `docs/POOLAR_ECOSYSTEM_ARQUITECTURA_INTEGRACION.md` (ADRs, backlog B-001..B-008, integración de referencia).

1. **F0-13 cierre formal (externo):** PR/merge + CI verde, habilitar job PG con secrets gestionados, evidencia E2E/fault-injection restante. (F0-10/F0-12 revalidados 0004+0005; suite Fase 0+capacidad **104 passed**).
2. **B-001/B-002/B-003/B-008:** envelope común + errores, `ModuleManifest` v0, matriz authz endpoint/adapter crítica, inventario licencias/IP. Sin integrar módulos externos reales.
3. **L1-EVAL-SYNTH (propuesto, requiere autorización):** evaluación logística gobernada sintética POOLAR→EnRuta (`logistics-l1/0.1`, `/matches/evaluate`)→SkyCast (`skycast-route-weather/0.1`), **sin ejecución operativa real**; idempotencia, correlación, procedencia, `data_status`, degradación segura.
4. **Producto core sobre gobernanza:** completar capacidades del flujo (`actividades`, participantes, historial/export, invitaciones/membresía) con actor+scope+HITL y E2E por capacidad.
5. **C1-01/C1-02/C1-03/C1-04/C1-05/C1-06 (post F0-13):** contratos modulares + registry; adaptadores CASE y ≥1 no-CASE **proposal-only**, mocks/sintético, autoridad siempre en POOLAR.
6. **L2/S3/R4:** pilotos por capacidad (logística rural, CO2e auditable, recursos), sin acoplamiento de repos y con puertas de datos/licencia.