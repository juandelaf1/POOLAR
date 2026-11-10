# Authorization Model — POOLAR

> Updated: 2026-11-10. Status: **partially implemented and evolving (dev/Phase 0), not verified with real users or production**.  
> References: `GOBERNANZA_POOLAR.md`, `docs/modelo_problemas_colectivos.md`, `BOUNDARIES.md`, `src/core/agent_harness/approvals.py`, `src/main.py`.

## Principios

- **Mínimo privilegio y fail-closed:** falta contexto/permiso/scope/evidencia ⇒ denegar o no ejecutar.
- **Aislamiento por ámbito:** organización (`organizacion_id`), individuo/personal (`persona_id`/actor personal), sin fuga cross-tenant ni cross-persona.
- **Separación de funciones:** proponente no autoaprueba/ejecuta; retiro propio seguro permitido sin ejecución cuando la política lo autoriza.
- **POOLAR conserva autoridad:** HITL/decisión/ejecución gobernada en POOLAR; módulos externos/CASE solo proponen.
- **Datos y privacidad:** `synthetic_pilot` por defecto; sin PII innecesaria en respuestas/logs/exports; consentimiento/procedencia requeridos para datos reales.

## Actores y autenticación

| Actor | Autenticación | Contexto típico |
|---|---|---|
| Usuario de organización | `POST /auth/token` (JWT, PBKDF2-SHA256) | `tipo=organizacion`, `organizacion_id`, rol operativo |
| Persona/individuo | `POST /personas/registro` + `POST /auth/token` | `tipo=individuo`, `persona_id`/ámbito personal |
| Sistema/automatización | Política explícita | Solo rutas auto-aprobadas y trazables |

`POOLAR_SECRET_KEY` obligatoria (fail-safe si falta). Tokens sin contexto ambiguo.

## Matriz resumida (dominio y HITL)

| Capacidad | Individuo (ámbito propio/personal) | Miembro/observador org | Gestor/coordinador/responsable/aprobador/admin org | Notas |
|---|---|---|---|---|
| Registrar/auth | Sí (registro y token) | Sí (según alta/token org) | Sí | Credenciales en JSON body |
| Crear/leer necesidades | Propias y accesibles según visibilidad/scope | Propias org + accesibles (`compartible/publica`) según reglas | En scope org | No exponer datos sensibles en DTO público |
| Problema colectivo / iniciativa / decisión | Según participación/responsabilidad y gobernanza | Según pertenencia/scope/rol | Según rol y scope | Algunas acciones pasan por evaluación/HITL |
| Ver solicitud HITL | Sí, si está en su scope (propia/personal) | Sí, si está en scope (lectura) | Sí, en scope | Fuera de scope: ocultar/denegar (404/403 según endpoint) |
| Aprobar/ejecutar HITL | **No** autoaprobación; terceros **no** sin autoridad explícita (fail-closed) | No | Sí, en scope, no propia | `approve()` autorizado ejecuta handler y registra resultado |
| Rechazar HITL | Retiro propio permitido (sin ejecución) | No gestión | Sí, en scope | Proponente no autoaprueba |
| Reintento/cierre `fallida_reintentable` | Según política (retiro propio si aplica) | No | Sí, en scope, no propia | Idempotente: sin duplicar efecto |

*La matriz exacta por endpoint/acción se valida en código y tests (`tests/test_fase0_*`, `tests/test_p03_http_governance.py`, etc.); completar cobertura exhaustiva es parte del cierre Fase 0.*

## Flujo HITL (implementado)

`pendiente` → (aprobación autorizada) → `ejecutando` → `ejecutada`  
`pendiente` → (rechazo/retiro autorizado) → `rechazada`  
falla de handler → rollback → `fallida_reintentable` → reintento/cierre autorizado  
`ejecutada` → terminal (idempotente, sin duplicar efecto)  
`expirada`/terminal → no aprobar ni ejecutar.

## Evidencia y verificación

- Local sin PG (2026-11-10): **171 passed, 7 skipped, 1 xfailed** (SQLite). Suite Fase 0/gobernanza y resumption cubiertas.
- PG real (evidencia desechable previa): migraciones 0004+0005 y carrera de concurrencia 1 efecto; **revalidar** en entorno/CI objetivo con `POOLAR_TEST_POSTGRES_URL`.
- Gaps conocidos: matriz exhaustiva por todas las acciones/endpoints, PG/CI verde con secretos gestionados, consentimientos/RGPD operativo para datos reales.

## Restricciones

- No producción, no impacto verificado sin evidencia.
- No relajar aislamiento/HITL para conveniencia; no integrar módulos externos con autoridad de ejecución.
