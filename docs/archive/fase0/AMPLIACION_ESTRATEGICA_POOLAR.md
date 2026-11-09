# Ampliación estratégica — Visión completa del producto POOLAR

**Fecha:** 2026-11-08  
**Origen:** visión aportada por el responsable del producto (prompt estratégico).  
**Relación con Fase 0:** esta visión **no sustituye** el cierre de Fase 0; **depende** de un núcleo POOLAR fiable (multi-tenant, fail-closed, atomicidad/idempotencia, concurrencia demostrada).

## 1. Resumen ejecutivo
POOLAR evoluciona hacia una **plataforma abierta, modular y profesional** para resolución de problemas colectivos y gestión inteligente de recursos compartidos. No es red social ni app vecinal: es infraestructura para identificar necesidades, agregar demandas, encontrar/evaluar/asignar recursos, organizar iniciativas, ejecutar soluciones y **medir resultados** (necesidades satisfechas, viabilidad, costes, aprovechamiento, impacto ambiental).

## 2. POOLAR ↔ CASE (decisión arquitectónica)
- **CASE** = motor modular de evaluación/decisión (escenarios, políticas, fiabilidad IA, propuestas justificadas). **No duplicar** con otro motor.
- **POOLAR** = contexto operativo, actores, evidencias, restricciones, **permisos, consentimiento, gobernanza/HITL, aprobación y control de ejecución** (autoridad final).
- Flujo objetivo: `POOLAR recibe → authz/permisos → invoca capacidades → CASE evalúa (cuando corresponda) → propuesta tipada → POOLAR aplica gobernanza → aprobación humana si procede → POOLAR ejecuta → POOLAR registra/audita`.
- Integración futura: estudiar conexión con módulos/contratos existentes de CASE **sin romper invariantes**; primera iteración con **provider mock + datos sintéticos** (solo tras Fase 0).

## 3. Dominios y capacidades objetivo (integración por capacidad, no por repo)
| Área | Ejemplos de capacidades | Candidatos de referencia (auditar antes) |
|---|---|---|
| Núcleo | identidad, multi-tenant, permisos, consentimiento, HITL, auditoría, evidencias/procedencia | POOLAR |
| Decisión | evaluación de casos, políticas, fiabilidad, rutas | CASE |
| Recursos compartidos/escasos | catálogo, titularidad, disponibilidad, inventario, reservas, asignación, priorización, trazabilidad; diferenciar consumibles/activos/capacidades | (dominio POOLAR + módulos especializados) |
| Sostenibilidad/CO2e | estimación/comparación de escenarios, factores versionados, unidades/límites, incertidumbre, medido vs estimado (base auditable) | Devera_DS (candidato; verificar metodología/licencia/procedencia) |
| Logística | matching, rutas, costes, operaciones | EnRuta, DashLogistics, Parada-Viva |
| Clima/ambiente/riesgo | ingesta climática, coste/ambiente, riesgo geoespacial, emergencias | SkyCast, SANDAM, GeoRisk_Finder, Anexo_Risk |
| Conocimiento/ingesta | RAG con citas/procedencia, extracción estructurada | AsesorIA, RASPAL_SCRAPER |
| Evidencia/informes | patrones de revisión versionada/HITL | FitFamily |
| Otros (especializados) | analítica/datos, inmobiliario, etc. | DataScope, PropIntel (aislado; revisar derechos/PII) |

**Regla:** evaluar cada capacidad por funcionalidad demostrada, arquitectura, calidad, tests, seguridad, licencias/PI, procedencia de datos, mantenibilidad, coste y compatibilidad contractual. Estados sugeridos: `candidate` → `experimental` → `validated` → `production-ready`. **No producción** sin criterios superados.

## 4. Ecosistema abierto de desarrolladores (futuro)
- API pública versionada, SDK, contratos tipados, `ModuleManifest`, registro/descubrimiento, versionado/compatibilidad, sandbox, tests de conformidad, permisos limitados por módulo, revisión de seguridad, licencias/atribución.
- **Aislamiento:** módulos externos **sin acceso directo a BD** y **sin autoridad** sobre aprobaciones/decisiones de POOLAR.

## 5. Experiencias y capacidades transversales de producto
Actores: ciudadanía, organizaciones/cooperativas, proveedores, administraciones/gestores (dentro de sus competencias), desarrolladores, operadores. Transversales: identidad/multi-tenancy, seguridad/privacidad, consentimiento, auditoría, gestión documental, notificaciones, observabilidad, rendimiento/resiliencia, backup/recuperación, CI/CD, accesibilidad, DX/documentación, licencias/gobernanza, medición de impacto.

## 6. Métrica principal de éxito
Priorizar: necesidades satisfechas, problemas resueltos, servicios ahora viables, costes reducidos, recursos compartidos/aprovechados, ahorro de tiempo, impacto ambiental (CO2e con base auditable), participación efectiva, calidad/permanencia de soluciones, módulos externos útiles y mantenidos. **No** optimizar principalmente por usuarios/publicaciones/interacciones.

## 7. Estrategia de evolución (orden recomendado)
1. **Cerrar P0/P1 de seguridad y ejecución del núcleo POOLAR** (Fase 0 abierta; ver `AUDITORIA_POOLAR_FASE0_LOCAL.md`).
2. **Definir contratos POOLAR↔CASE** (`ModuleManifest`, `ActorContext`, `ExecutionRequest`, `EvidenceEnvelope`, `CapabilityResult`, `DecisionProposal`, `ApprovalRecord`), manteniendo autoridad en POOLAR.
3. **Validar mecanismo común** de necesidades, capacidades, recursos y soluciones.
4. **Primer piloto integral:** logística rural (tras puertas de seguridad/licencia/datos).
5. **Sostenibilidad/CO2e** con Devera como candidato (metodología auditable, versionada, medido vs estimado).
6. **Recursos compartidos** progresivos (caso concreto inicial: agua o energía), sin modelo único forzado ni suplantar competencias de operadores/autoridades.
7. **Capacidades para módulos externos** (SDK/contratos/sandbox/conformidad/aislamiento).
8. **Integrar progresivamente proyectos propios** que superen evaluación de calidad/seguridad/licencia/datos.

**Objetivo final:** un producto único, coherente, extensible y profesional; no maximizar repos conectados.
