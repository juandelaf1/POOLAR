# Gobernanza — POOLAR (modelo operativo)

> Estado: **propuesto + parcialmente implementado (Fase 0)**. Principios: **fail-closed**, mínimo privilegio, separación de funciones, trazabilidad, aislamiento por ámbito. **POOLAR decide; CASE/módulos externos solo proponen.**

## 1) Principios
- **Autoridad:** la ejecución de efectos de negocio sensibles requiere decisión válida en POOLAR (automática bajo política explícita o HITL).
- **Fail-closed:** falta de contexto, permiso, scope, handler o evidencia suficiente ⇒ bloquear/no ejecutar.
- **Separación de funciones:** quien propone no aprueba/ejecuta su propia solicitud (salvo retiro seguro sin ejecución).
- **Ámbito (tenant/personal):** acceso mínimo al scope correspondiente; sin fuga cross-tenant ni cross-persona.
- **Auditabilidad:** cada decisión relevante deja rastro: actor, acción, contexto, motivo, estado, resultado/error, timestamps, correlación.
- **Idempotencia/recuperación:** reintentos seguros, sin duplicar efectos; estados recuperables.

## 2) Actores y ámbitos
| Actor | Ámbito típico | Notas |
|---|---|---|
| Organización (miembro operativo) | `organizacion_id` | Permisos por rol dentro de la org. |
| Individuo / persona | personal (`persona_id`, sin `organizacion_id`) | Política actual: ver/retirar HITL propio; sin autoaprobación ni aprobación por terceros sin autoridad explícita. |
| Sistema / automatización | según política | Solo rutas auto-aprobadas explícitas; trazable. |
| Autoridad de gobernanza (futuro, explícita) | definido por política | Para escalamiento/excepciones; debe ser nominada, auditable y no relajar aislamiento por defecto. |

## 3) Matriz de permisos (base Fase 0, a completar)

| Capacidad | `miembro`/`observador` | `coordinador`/`gestor`/`responsable`/`aprobador`/`admin` | Proponente (mismo actor) | Individuo (ámbito personal) |
|---|---:|---:|---:|---:|
| Ver solicitud en scope | **Sí** (lectura en scope, sin gestión) | Sí (en scope) | Sí (en scope) | Sí (propia) |
| Aprobar/ejecutar | No | Sí, en scope, no propia | **No** (self-approval bloqueado) | **No** (self); terceros **No** (política fail-closed) |
| Rechazar | No | Sí, en scope | **Retiro propio permitido** (sin ejecución) | **Retiro propio permitido** |
| Reintentar `fallida_reintentable` | No | Sí (vía aprobar), en scope | No (si implica autoaprobación) | N/A según política |
| Cerrar `fallida_reintentable` por rechazo | No | Sí, en scope | Retiro si aplica política | Retiro propio |
| Administrar política/roles | No | Solo rol admin definido | No | No |

*Implementado parcialmente en `src/core/agent_harness/approvals.py` y tests Fase 0; falta formalizar lectura vs gestión y cubrir todos los endpoints/acciones.*

## 4) Flujo HITL (estados)
`pendiente` → (aprobación autorizada) → `ejecutando` → `ejecutada`  
`pendiente` → (rechazo/retiro autorizado) → `rechazada`  
`ejecutando`/handler falla → rollback → `fallida_reintentable` → (aprobar/reintentar) o (rechazar/cerrar)  
`ejecutada` → terminal (re-aprobar idempotente, sin duplicar efecto).  
`expirada/caducada`/terminal → no aprobar ni ejecutar.

## 5) Políticas por riesgo (propuesto)
| Riesgo/acción | Ruta por defecto | Requisitos |
|---|---|---|
| Bajo riesgo, reversible, política explícita | Auto | Registro + auditoría |
| Medio/alto, efecto de negocio, datos sensibles | HITL | Scope + aprobador autorizado + no self |
| Excepcional / personal / escalamiento | HITL + autoridad explícita | Política nominada, evidencia, auditoría reforzada (diseñar antes de habilitar) |
| Ambiguo / sin contexto | **Bloquear** | Fail-closed |

## 6) POOLAR ↔ CASE / módulos externos
- **CASE propone** (DecisionProposal, EvidenceEnvelope, recomendaciones); **POOLAR valida, registra y decide**.
- Integración por **contratos versionados** (ModuleManifest, ActorContext, ExecutionRequest, CapabilityResult, ApprovalRecord), adapters y mocks/datos sintéticos.
- Ningún módulo externo recibe autoridad de aprobar/ejecutar HITL por defecto.

## 7) Auditoría y datos
- Registrar quién/cuándo/qué/por qué/resultado/correlación; preservar trazabilidad ante fallos.
- Datos personales/consentimientos: mínimo necesario, procedencia, acceso por scope, retención definida.
- Analítica separada del transaccional (exports auditables → DuckDB/DBT cuando aplique); sin acoplar a HITL.

## 8) Pendientes de gobernanza (backlog)
- Completar matriz lectura/aprobación/admin y aplicarla en todos los endpoints.
- Diseñar autoridad de escalamiento/excepciones (si se requiere) sin romper aislamiento.
- Definir expiración/SLA, notificaciones, y reglas de quórum/delegación (si aplica).
- Contratos POOLAR↔CASE y pruebas con mocks.
- Revalidación PG/CI en entorno objetivo cuando haya cambios o pipeline con secretos gestionados.
