# INTENT.md — Poolar

## Propósito

Poolar es una plataforma modular y transaccional para conectar necesidades, optimizar capacidades y ejecutar soluciones colectivas de forma ágil.

No es una red social, ni un gestor de tareas, ni un portal de anuncios. Es infraestructura para organizar cooperación y hacerla comprensible, trazable y reutilizable.

## Objetivos de negocio

1. Permitir que personas y organizaciones registren necesidades, conocimientos y capacidades.
2. Descubrir problemas colectivos mediante coincidencias explicable.
3. Conectar recursos complementarios y calcular demanda compartida.
4. Comparar alternativas con criterios y supuestos explícitos.
5. Organizar iniciativas con decisiones documentadas y responsabilidades claras.
6. Coordinar ejecución y medir resultados verificables.
7. Conservar autonomía sobre datos y reducir dependencia de intermediarios.

## Flujo operativo principal

Necesidad → Descubrimiento → Problema Colectivo → Capacidades y recursos → Alternativas → Decisión → Ejecución → Resultados → Aprendizaje reutilizable.

## Reglas de dominio (intención)

- La unidad fundamental es el problema compartido y la capacidad colectiva.
- Personas y organizaciones son participantes de primera clase.
- Los datos sintéticos (`synthetic_pilot`) son obligatorios hasta que exista un proceso de consentimiento formal.
- Los agentes de IA asisten, no deciden.
- La autorización se verifica en cada operación del dominio.
- Las decisiones colectivas requieren aprobación humana.

## Contratos de API

- Todos los endpoints consumen y producen JSON tipado.
- La autenticación es JWT con secreto de entorno obligatorio.
- Las contraseñas se envían en cuerpo JSON, nunca en URL.
- Los datos personales nunca se exponen en DTOs públicos.

## Restricciones de diseño

- Monolito modular (FastAPI + SQLAlchemy + PostgreSQL).
- No microservicios ni infraestructura distribuida.
- PostgreSQL es la base objetivo; SQLite solo para desarrollo controlado.
- Migraciones reproducibles con Alembic.
- CI con PostgreSQL real y Playwright E2E.

## Auditoría de Estado y Hoja de Ruta

### Hito alcanzado
- MVP funcional con tests backend (41 passed) y E2E con Playwright (5 passed) en SQLite.
- Rebranding a Poolar completado (INTENT.md, BOUNDARIES.md, assets, env vars).
- P0/P1 corregidos (autorización individual, credenciales JSON tipado).
- Invitación persistente con consentimiento real.
- Matching determinista con filtros y explicación.
- Interfaz funcional conectada a API.
- Dockerfile, docker-compose, Alembic, CI workflow.
- Seguridad transversal (rate limiting, validación, redacción, detección de inyección).
- Capa de modelos desacoplada (NullProvider por defecto).
- ADRs (LangGraph vs CrewAI, LangSmith vs Langfuse).
- Catálogo de herramientas operativas.
- Escenario de logística compartida documentado.
- PostgreSQL 16 verificado localmente (suite completa 29/29 tests pasando contra PostgreSQL real).
- Capa de búsqueda semántica (SemanticSearchPort) implementada con servicio local y tests unitarios.
- **P0 Gobernanza y Human-in-the-Loop COMPLETADO** (commit `ad16c29`):
  - Precedencia estricta: `REJECT > HUMAN_REVIEW > AUTO_APPROVE`
  - Modelo `approval_requests` persistente (SQLAlchemy + Alembic `7462b4e_approval`)
  - 10 tests de regresión (`tests/test_governance_regresion.py`) — todos passing
  - Datos reales (`real_pilot`) nunca permiten `AUTO_APPROVE`; riesgo mínimo elevado a `MEDIUM`
  - Actor sin rol reconocido (`actor_rol` vacío/desconocido) → `REJECT`
  - Operaciones sensibles (`create_decision`, `export_data`, `accept_invitation`, `change_state`) → `HUMAN_REVIEW`
  - `ApprovalManager` con contrato de persistencia y no reutilización (`approve` requiere `PENDING`)

### Siguiente intención principal (Sprint actual)
Pulido de UI/UX en `interfaz/index.html` y accesibilidad WCAG.

### Backlog priorizado
1. Activación de PostgreSQL local y ejecución de suite de pruebas sobre Postgres. (COMPLETADO)
2. Pulido de UI/UX en `interfaz/index.html` y accesibilidad WCAG.
3. Renombrado del repositorio en GitHub y CI/CD en GitHub Actions.

### Pendiente (documentado)
- PostgreSQL real (`POOLAR_TEST_POSTGRES_URL`)
- Playwright E2E ejecución real
- Consentimiento formal para datos reales
- Accesibilidad WCAG completa
- Licencia formal (MIT ya agregada)
- Integración con repos auditados (`P0`/`P1` corregidos)
- RAG + búsqueda semántica (pgvector)
- LangGraph (orquestación de flujos)
- LangSmith/Langfuse (observabilidad)
- PostGIS, OR-Tools, MCP (pendiente de necesidad demostrada)