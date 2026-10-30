# Hoja de Ruta — Poolar MVP v0.6

Fecha: 29 octubre 2026
Estado: Entregado; no producción.

## Completado (esta iteración)

- [x] Diseño independiente (no copia de repos auditados)
- [x] Modelo `ProblemaColectivo` + `Persona` + relaciones N:M
- [x] Contratos versionados (`contracts.py`)
- [x] Auth PBKDF2-SHA256 + JWT con `tipo`
- [x] Registro individual (`POST /personas/registro`)
- [x] Endpoints problema colectivo (crear, consultar, estado)
- [x] Iniciativa con responsable individual
- [x] Autorización dual (org / persona) implementada
- [x] Invitación / participación mínima
- [x] Datos sintéticos obligatorios (`synthetic_pilot`)
- [x] Pruebas: 31 passed + flujo individual
- [x] Documentación: auditoría, entrega, cierre, autorización, decisiones técnicas, registro, visión
- [x] README actualizado
- [x] Dockerfile + docker-compose.yml
- [x] Alembic configurado con migración inicial
- [x] conftest.py actualizado para soportar PostgreSQL real
- [x] P0/P1 fixes aplicados (autorización individual, credenciales JSON)
- [x] Interfaz `interfaz/index.html` conectada a API
- [x] Catálogo de herramientas (`docs/cat_herramientas.md`)
- [x] Escenario de logística compartida (`docs/demo/escenario_logistica.md`)
- [x] CI workflow con PostgreSQL service (`.github/workflows/ci.yml`)
- [x] Capa de modelos (`src/core/model_provider.py`)
- [x] Seguridad transversal (`src/core/security.py`)
- [x] ADR LangGraph vs CrewAI (`docs/adr_langgraph_crewai.md`)
- [x] ADR LangSmith vs Langfuse (`docs/adr_langsmith_langfuse.md`)
- [x] Logo (`assets/logo_poolar.svg`) y badges en README

## Pendiente (documentado, no bloqueante para este MVP)

- [ ] PostgreSQL real (`POOLAR_TEST_POSTGRES_URL`)
- [ ] Integración con repos auditados (`P0`/`P1` corregidos)
- [ ] Proceso de consentimiento para datos reales
- [ ] Canal físico de invitación / consentimiento verificado
- [ ] Accesibilidad WCAG / adaptaciones
- [ ] Trazabilidad ética formal
- [ ] Perfil technic global automático
- [ ] Exportación completa verificada con datos sintéticos
- [x] Pruebas E2E con Playwright (5 passed en Chromium real)
- [x] Licencia formal (MIT)
- [x] EvidencePort (FitFamily) implementado con tests
- [x] GeoPort/OptimizationPort (EnRuta/DashLogistics) implementado con tests
- [x] Gobernanza (AutomationEvaluator) integrado en endpoints
- [x] Interfaz estática servida desde FastAPI
- [x] Matching determinista con filtros y explicación
- [x] Invitación persistente con consentimiento real
- [x] Accesibilidad WCAG básica (focus, ARIA, labels)
- [ ] LangGraph/CrewAI (documentado, pendiente de implementación)
- [ ] LangSmith/Langfuse (documentado, pendiente de implementación)
- [ ] PostGIS, OR-Tools, MCP (documentado, pendiente de necesidad demostrada)

## Próxima iteración sugerida

1. Confirmar PostgreSQL y ejecutar `test_migracion_postgresql`.
2. Completar trazabilidad ética + accesibilidad.
3. Cerrar integración solo tras `P0`/`P1` corregidos.