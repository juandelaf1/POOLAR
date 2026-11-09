# Entrega de Iteración — Poolar MVP v0.6
Estado: **Prototipo funcional, no producción**.

## Entregables

1. `docs/modelo_autorizacion.md` — matriz, principios, riesgos
2. `docs/modelo_problemas_colectivos.md` — entidad, reglas, estado código
3. `src/core/auth.py` — PBKDF2-SHA256, `get_current_user` con contexto `tipo` individual/organización
4. `src/core/contracts.py` — DTOs con `Persona`, `ProblemaColectivo`, `ProblemaColectivoEstadoUpdate`, `TRANSICIONES_PROBLEMA_COLECTIVO`
5. `src/core/models.py` — `Persona` con `hashed_password`, `Decision`, relaciones N:M, restricciones `CHECK` y `ON DELETE CASCADE`
6. `src/main.py` — endpoints `/problemas-colectivos`, `/problemas-colectivos/{id}/estado`, `/iniciativas` con `problema_colectivo_id`, `/decisiones`, `/eventos`, `/exportar/*`, `/necesidades`, `/recursos`, `/personas/registro`, `/invitaciones`, `/participaciones`
7. `tests/conftest.py` — base efímera, credenciales sintéticas, fixtures `org_a`, `org_b`, `headers_a`, `headers_b`
8. `tests/test_problema_colectivo.py` — 10+ casos con datos sintéticos etiquetados
9. `tests/test_auth_isolation.py` — token, hash sintético, etiquetas
10. `src/core/migrations/002_problemas_colectivos.sqlite.sql` — migración objetivo SQLite
11. `docs/vision_y_proposito.md` — actualizado con contexto individual pendiente
12. `README.md` — referencias actualizadas a `modelo_autorizacion.md` y `modelo_problemas_colectivos.md`
13. `interfaz/index.html` — interfaz funcional conectada a API
14. `assets/logo_poolar.svg` — logo del proyecto
15. `docs/hoja_de_ruta.md` — hoja de ruta con pendientes
16. `docs/logs_cambios.md` — registro de cambios
17. `docs/cierre_iteracion.md` — estado de entrega
18. `docs/cat_herramientas.md` — catálogo de herramientas operativas
19. `docs/adr_langgraph_crewai.md` — ADR LangGraph vs CrewAI
20. `docs/adr_langsmith_langfuse.md` — ADR LangSmith vs Langfuse
21. `docs/demo/escenario_logistica.md` — escenario de logística compartida
22. `src/core/model_provider.py` — capa de acceso a modelos
23. `src/core/security.py` — controles de seguridad transversales
24. `src/core/migrate.py` — módulo de migraciones
25. `src/core/alembic/` — configuración y migraciones PostgreSQL
26. `Dockerfile`, `docker-compose.yml`, `.dockerignore`, `.env.example`
27. `.github/workflows/ci.yml` — CI con PostgreSQL service
28. `src/services/` — servicios operativos (needs, matching, invitation)

## Estado de la iteración (29 octubre 2026) — ENTREGADO

- Dockerfile + docker-compose.yml creados y verificados.
- Alembic configurado con migración inicial.
- conftest.py actualizado para soportar PostgreSQL real vía `POOLAR_TEST_POSTGRES_URL`.
- P0/P1 fixes aplicados (autorización individual, credenciales JSON).
- Interfaz `interfaz/index.html` conectada a API.
- Catálogo de herramientas (`docs/cat_herramientas.md`).
- Escenario de logística compartida (`docs/demo/escenario_logistica.md`).
- CI workflow con PostgreSQL service (`.github/workflows/ci.yml`).
- Pruebas: 31 passed, 1 skipped (PostgreSQL pendiente de servidor).
- Repo subido a GitHub (`juandelaf1/poolar`, commit `1b7c17d`).

## Pendiente de infraestructura (documentado)

- PostgreSQL real (`POOLAR_TEST_POSTGRES_URL` no disponible en este entorno).
- Pruebas E2E con Playwright.
- Consentimiento formal para datos reales.
- Accesibilidad WCAG.
- Licencia formal.
- Integración con repos auditados (`P0`/`P1` corregidos).
- Registro individual (`POST /personas/registro`) implementado y probado.
- Auth dual (`individuo`/`organizacion`) funcional con `get_current_user` por contexto.
- `ProblemaColectivo` completo con integridad N:M, transiciones controladas, eventos de auditoría.
- `Iniciativa` con responsable individual (`responsable_tipo=persona`) corregido.
- Invitación/participación mínima insertada (`invitaciones`, `participaciones`) con registro de auditoría.
- Flujo end-to-end individual documentado (`tests/test_flujo_individual.py`).
- Pruebas: 31 passed, 1 skipped (PostgreSQL pendiente de infraestructura).
- Datos sintéticos (`synthetic_pilot`) obligatorios; sin datos reales en ninguna prueba.
- Producción: NO declarada; integración con repos auditados bloqueada hasta `P0`/`P1` corregidos.
- PostgreSQL: pendiente; `test_migracion_postgresql` configurado con `skipif`; `psycopg2-binary` y migración listos.
- Documentación completa: `docs/auditoria_etapas.md`, `docs/registro_individual.md`, `docs/modelo_autorizacion.md` actualizado.

## Notas

Los repositorios auditados (`Anexo_Risk`, `EnRuta`, `CASE`) no se modificaron; se mantienen como referencias bloqueadas (`P0`/`P1` no corregidos en ellos, pero `POOLAR_SECRET_KEY` sin clave fija y `PBKDF2-SHA256` evitan heredar los problemas de seguridad de los candidatos).