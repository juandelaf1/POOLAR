# POOLAR Documentation

Navigable index of **current** documentation and historical references. POOLAR is in **development (prototype/Phase 0)**: no production or verified-impact claims without evidence.

> Language: repository convention is **English** (README bilingual, English default). Some linked docs may still be in Spanish and are migrated progressively. See [CONVENTIONS](CONVENTIONS.md).

## Quick start
- [Repository README](../README.md) — overview, architecture, API, execution (English default, Spanish in collapsible section).
- [CONVENTIONS](CONVENTIONS.md) — language policy and contract locations.
- [AUDIT_READY_POOLAR.md](../AUDIT_READY_POOLAR.md) — auditable status (formal closure subject to external gates).
- [BACKLOG_PRIORIZADO_POOLAR.md](../BACKLOG_PRIORIZADO_POOLAR.md) — priorities and pending work.
- [FASE0_CHECKLIST_CIERRE.md](../FASE0_CHECKLIST_CIERRE.md) — Phase 0 closure checklist.

## Gobernanza y límites
- [INTENT.md](../INTENT.md) — intención y flujo operativo.
- [BOUNDARIES.md](../BOUNDARIES.md) — límites estrictos (seguridad, datos, testing, claims).
- [GOBERNANZA_POOLAR.md](../GOBERNANZA_POOLAR.md) — HITL, ámbitos, matriz de permisos.
- [CAPAS_Y_AVANCE_POOLAR.md](../CAPAS_Y_AVANCE_POOLAR.md) — capas y avance.

## Arquitectura y ecosistema
- [docs/POOLAR_ECOSYSTEM_ARQUITECTURA_INTEGRACION.md](POOLAR_ECOSYSTEM_ARQUITECTURA_INTEGRACION.md) — ecosistema, dominios, contratos, L1 propuesto.
- [docs/POOLAR_BENCHMARK_ARQUITECTURA_BIEN_COMUN.md](POOLAR_BENCHMARK_ARQUITECTURA_BIEN_COMUN.md) — benchmark CORE/MODULE/CONNECTOR.
- [docs/FRONTEND_MONITOREO_ARQUITECTURA.md](FRONTEND_MONITOREO_ARQUITECTURA.md) · [FRONTEND_PENDIENTES_REGISTRO.md](FRONTEND_PENDIENTES_REGISTRO.md)
- ADRs: [agent harness](adr_agent_harness.md), [LangGraph/CrewAI](adr_langgraph_crewai.md), [LangSmith/Langfuse](adr_langsmith_langfuse.md), [CI PG/secrets](CI_PG_SECRETS.md).

## Dominio y operación
- [modelo_autorizacion.md](modelo_autorizacion.md) · [modelo_problemas_colectivos.md](modelo_problemas_colectivos.md) · [registro_individual.md](registro_individual.md)
- [vision_y_proposito.md](vision_y_proposito.md) · [hoja_de_ruta.md](hoja_de_ruta.md) · [riesgos_pendientes.md](riesgos_pendientes.md)
- [cat_herramientas.md](cat_herramientas.md) · [decisiones_tecnicas.md](decisiones_tecnicas.md) · [consentimiento.md](consentimiento.md) · [accesibilidad_wcag.md](accesibilidad_wcag.md)
- [ANALYTICS_LAKEHOUSE.md](ANALYTICS_LAKEHOUSE.md) — medallion/raw-staging-marts, DuckDB/dbt stubs, lakehouse estratégico (Basin/R2/Iceberg)
- Demo: [escenario_logistica.md](demo/escenario_logistica.md)

## Archivo (histórico)
Informes de iteración/Fase 0 movidos a [`docs/archive/`](archive/README.md) para evitar ruido en la raíz; conservados por trazabilidad. No usarlos como estado actual sin verificar.