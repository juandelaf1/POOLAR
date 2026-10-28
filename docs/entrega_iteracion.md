1. `docs/modelo_autorizacion.md` (matriz, principios, riesgos)
2. `docs/modelo_problemas_colectivos.md` (entidad, reglas, estado código)
3. `src/core/auth.py` (PBKDF2-SHA256, `get_current_user` con contexto `tipo` individual/organización)
4. `src/core/contracts.py` (DTOs con `Persona`, `ProblemaColectivo`, `ProblemaColectivoEstadoUpdate`, `TRANSICIONES_PROBLEMA_COLECTIVO`)
5. `src/core/models.py` (entidad `Persona` con `hashed_password`, `Decision`, relaciones N:M, restricciones `CHECK` y `ON DELETE CASCADE`)
6. `src/main.py` (endpoints `/problemas-colectivos`, `/problemas-colectivos/{id}/estado`, `/iniciativas` con `problema_colectivo_id`, `/decisiones`, `/eventos`, `/exportar/*`, `/necesidades`, `/recursos`)
7. `tests/conftest.py` (base efímera, credenciales sintéticas, fixtures `org_a`, `org_b`, `headers_a`, `headers_b`)
8. `tests/test_problema_colectivo.py` (10+ casos con datos sintéticos etiquetados)
9. `tests/test_auth_isolation.py` (token, hash sintético, etiquetas)
10. `src/core/migrations/002_problemas_colectivos.sqlite.sql` (migración objetivo SQLite)
11. `docs/vision_y_proposito.md` (actualizado con contexto individual pendiente)
12. `README.md` (referencias actualizadas a `modelo_autorizacion.md` y `modelo_problemas_colectivos.md`)

Nota: los repositorios auditados (`Anexo_Risk`, `EnRuta`, `CASE`) no se modificaron; se mantienen como referencias bloqueadas (`P0`/`P1` no corregidos en ellos, pero `TRAMA_ABIERTA_SECRET_KEY` sin clave fija y `PBKDF2-SHA256` evitan heredar los problemas de seguridad de los candidatos).

---

## Estado de esta iteración (28 octubre 2026) — ENTREGADO
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
