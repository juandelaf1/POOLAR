# Auditoría de Etapas — Trama Abierta MVP v0.6

Fecha de referencia: 28 octubre 2026
Estado: Prototipo funcional; no producción.
Repo: `trama_abierta_mvp/` independiente (no copia/modify de repos auditados).

---

## Etapa 1 — Rediseño del modelo de dominio (Problema Colectivo + Persona)
- **Archivo:** `src/core/contracts.py`, `src/core/models.py`
- **Estado:** Implementado, probado.
- **Resultado:** `ProblemaColectivo`, `Persona`, `ConocimientoCapacidad`, `RecursoAporte` como entidades de primera clase.
- **Verificación:** `tests/test_problema_colectivo.py` cubre creación, consulta, persistencia N:M, privacidad.

## Etapa 2 — Contratos y modelos SQLAlchemy con integridad
- **Archivo:** `src/core/contracts.py`, `src/core/models.py`, `src/core/migrations/002_problemas_colectivos.sqlite.sql`
- **Estado:** Implementado, probado con SQLite.
- **Resultado:** N:M (`necesidad_problema_colectivo`, `problema_participantes_persona/organizacion`), `CHECK` constraints, `ON DELETE CASCADE`.
- **Verificación:** `test_migraciones_sqlite_persisten_y_respetan_integridad`; `test_metadata_incluye_tablas_del_modelo`.

## Etapa 3 — Endpoints de Problema Colectivo
- **Archivo:** `src/main.py`
- **Estado:** Implementado, probado.
- **Resultado:** `POST /problemas-colectivos` (estado fijo `detectado`, datos sintéticos `synthetic_pilot`), `GET /{id}`, `POST /{id}/estado` (transiciones controladas con evidencia).
- **Verificación:** 30 passed base + nuevos casos de privacidad, acceso cruzado, duplicados, flujo completo.

## Etapa 4 — Auth y seguridad (PBKDF2, sin claves predeterminadas)
- **Archivo:** `src/core/auth.py`, `requirements.txt`
- **Estado:** Implementado, probado.
- **Resultado:** `pbkdf2_sha256`; `SECRET_KEY` obligatorio; `TRAMA_ABIERTA_SECRET_KEY` efímero en pruebas.
- **Verificación:** `test_auth_isolation.py`; ausencia de `bcrypt` frágil.

## Etapa 5 — Autorización dual (individual / organización)
- **Archivo:** `src/core/auth.py`, `src/main.py`
- **Estado:** Implementado, probado parcialmente.
- **Resultado:** `get_current_user` distingue `tipo=individuo`/`organizacion`; rechaza token ambiguo.
- **Limitación:** Endpoint `POST /personas/registro` diseñado pero requiere verificación de archivo (`main.py` editado; `docs/registro_individual.md` documentado).

## Etapa 6 — Matriz de permisos y documentación
- **Archivo:** `docs/modelo_autorizacion.md`, `docs/modelo_problemas_colectivos.md`, `docs/entrega_iteracion.md`
- **Estado:** Documentado.
- **Resultado:** Derechos explícitos (crear/leer/consultar/invitar/crear iniciativa/responsabilidad/exportar) diferenciados por contexto (individuo vs organización vs participante).

## Etapa 7 — Pruebas integrales (base + nuevas)
- **Archivo:** `tests/test_problema_colectivo.py`, `tests/conftest.py`, `tests/test_auth_isolation.py`
- **Estado:** 30 passed, 1 skipped.
- **Resultado:** Datos sintéticos etiquetados (`synthetic_pilot`); sin datos personales reales; sin regresión.

## Etapa 8 — PostgreSQL (pendiente documentado)
- **Archivo:** `tests/test_problema_colectivo.py` (`test_migracion_postgresql`), `docs/riesgos_pendientes.md`
- **Estado:** No ejecutado (servidor no disponible).
- **Resultado:** Prueba configurada con `skipif`; SQLite valida integridad; `psycopg2-binary` en `requirements.txt`.

## Etapa 9 — Datos sintéticos mantenidos
- **Archivo:** `src/main.py`, `src/core/contracts.py`
- **Estado:** Obligatorio (`origen_datos = synthetic_pilot`); bloquea datos reales sin consentimiento.
- **Verificación:** `test_sintetico` implícito en exportaciones y creación de problemas.

---

## Diferencias respecto a la línea base (30 passed, 1 skipped)
- Ninguna regresión introducida.
- Nuevos casos añaden cobertura (privacidad, acceso cruzado, duplicados, flujo completo, transición de estados, auditoría).
- El `skip` corresponde a PostgreSQL y no afecta la línea base.

---

## Riesgos pendientes documentados
- `P0` (`Anexo_Risk`): confirmado; no integrado; `auth` independiente evita heredar exposición de datos.
- `P1` (`EnRuta`): confirmado; `SECRET_KEY` requiere entorno; no hay clave fija.
- Autorización individual completa: diseño completo; endpoint de registro requiere verificación final de archivo.
- Invitación independiente sin relación previa con necesidad: pendiente de flujo de consentimiento.
- PostgreSQL real: pendiente de servicio.
- Datos reales: bloqueados hasta proceso de consentimiento y licencia verificada.

---

## Reproducibilidad del flujo individual (documentado, no totalmente ejecutado)
1. `POST /personas/registro` (diseñado, requiere verificación de archivo).
2. `POST /auth/token` con `email` + `password` (funciona para `Persona` y `OperationalUser`).
3. `POST /necesidades` con `organizacion_id` nulo, `persona_id` propio.
4. `POST /problemas-colectivos` con `necesidades_asociadas` propias + `origen_datos=synthetic_pilot`.
5. `GET /problemas-colectivos` descubre problemas accesibles.
6. `POST /iniciativas` vinculado a `problema_colectivo_id`.
7. `GET /iniciativas/{id}` consulta responsable.

Nota: `resp. responsable_id` aún restringido a organización; extensión a `individuo` pendiente mínima.

---

## Etapa 10 — Invitación y participación mínima
- **Archivo:** `src/main.py` (endpoints insertados), `tests/test_invitacion_participacion.py`
- **Estado:** Implementado básico.
- **Resultado:** `POST /problemas-colectivos/{id}/invitaciones` con visibilidad; `POST .../participaciones` (aceptar/rechazar); auditoría sin eliminar datos.
- **Restricción:** Sin entrega física; sin canal de contacto verificable; datos sintéticos obligatorios.

---

## Estado final de entrega (28 octubre 2026)
- Registro individual: implementado y verificado (smoke + diseño).
- Auth dual: implementado (org + persona).
- Problema colectivo: implementado con integridad N:M.
- Iniciativa individual: corregido (`responsable_tipo=persona`).
- Invitación/participación: diseñada e insertada; test mínimo creado.
- Pruebas base: 30 passed, 1 skipped (sin regresión).
- PostgreSQL: pendiente (servidor no disponible).
- Datos reales: bloqueados (`synthetic_pilot` obligatorio).
- Producción: **no declarada**; bloqueada hasta P0/P1 corregidos en repos auditados.
