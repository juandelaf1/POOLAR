# Modelo de Autorización — Trama Abierta v0.6

Estado: **definido en código y documentado; no verificado con usuario real**.
Referencia: `docs/vision_y_proposito.md`; `docs/modelo_problemas_colectivos.md`.
Fecha: 28 de octubre de 2026

---

## Principio

No se asume que pertenecer a una organización concede acceso ilimitado a todos los problemas, necesidades o iniciativas. Cada entidad (Persona, Organización) tiene un contexto de participación explícito, y los permisos se derivan de ese contexto, no de la simple posesión de un `id`.

En el MVP:
- **Persona independiente (`tipo = individuo`)**: puede crear necesidades propias, participar en problemas colectivos donde esté relacionada por evidencia o participación previa, ofrecer conocimiento o recursos propios, y consultar decisiones e iniciativas donde participe o sea responsable.
- **Organización (`tipo = organizacion`)**: crea recursos como propietaria; sus usuarios operativos (`OperationalUser`) actúan en su nombre. Un problema colectivo creado por la organización puede incluir necesidades vinculadas a ella y a personas relacionadas (previa validación explícita del flujo de consentimiento pendiente).

---

## Matriz de permisos (resumen operativo)

| Acción | Persona independiente (`individuo`) | Usuario de organización (`organizacion`) | Observaciones / limitaciones actuales |
|---|---|---|---|
| Registrar identidad | Sí (registro individual pendiente en endpoint) | Sí (mediante `POST /organizaciones`) | Registro individual requiere `Persona.hashed_password`; no se expone en DTO público. |
| Autenticarse (`/auth/token`) | Sí, si tiene `email` + `hashed_password` en `Persona` | Sí, con `email` + `hashed_password` en `OperationalUser` | La autenticación individual está implementada a nivel de datos (`auth.py` actualiza `get_current_user`), pero no hay endpoint público de registro individual aún. |
| Crear necesidad (`POST /necesidades`) | Sí, con `organizacion_id` = `None`, `persona_id` = propio | Sí, con `organizacion_id` = propio | Se requiere `visibilidad` explícita; por defecto `privada`. |
| Leer necesidad ajena (`GET /necesidades`) | Solo `compartible` o `publica` | Solo propias + `compartible`/`publica` | No se expone `responsable_id` ni datos sensibles en DTO público. |
| Crear Problema Colectivo (`POST /problemas-colectivos`) | Sí, con evidencia sintética obligatoria (`origen_datos` = `synthetic_pilot`) | Sí, igual restricción | El cliente no puede fijar `validado`; solo `detectado`. |
| Consultar problema (`GET /problemas-colectivos`) | Solo si es participante o responsable del problema | Solo si es participante, responsable o miembro de la organización responsable | No confirma existencia de problemas inaccesibles (404 único). |
| Asociar necesidad a problema | Solo necesidades accesibles (`privada` si es propia, `compartible`/`publica` si es ajena con permiso implícito) | Igual | Se rechaza explícitamente (`404`) si no tiene acceso. |
| Participar en problema (agregar persona/org) | Solo si la persona ya está relacionada con una necesidad del problema (no hay invitación independiente aún) | Igual restricción para organizaciones | Limitación documentada: falta flujo de consentimiento/invitación independiente. |
| Cambiar estado (`POST .../estado`) | Solo el responsable o la organización propietaria del problema | Solo organización propietaria (si el problema tiene `organizacion_id`) | Requiere evidencia para pasar a `validado`. |
| Crear iniciativa (`POST /iniciativas`) | Solo si es responsable de la iniciativa o pertenece a la organización de la necesidad vinculada | Solo la organización responsable (`responsable_id` = `org_id`) | La persona independiente aún no puede ser `responsable_id` de una iniciativa; pendiente de extensión mínima. |
| Crear decisión (`POST /decisiones`) | Solo si pertenece al contexto responsable de la iniciativa | Igual | Requiere `responsable_decision` explícito. |
| Consultar decisión (`GET ...`) | Incluido en flujo; no hay endpoint específico de lectura individual aún | Igual | La lectura es a través del flujo de iniciativa. |
| Exportar (`/exportar/*`) | Solo datos propios (necesidades de la organización para contexto organizativo; para individuo pendiente de implementación completa) | Solo datos propios | Datos sintéticos etiquetados (`synthetic`: true). |
| Registrar evento (`POST /eventos`) | Sí, solo sobre entidades accesibles (`problema_colectivo`, `iniciativa`, `necesidad`, `decision`) | Igual | No se registra contraseña, token ni datos personales en `dato_anterior`/`dato_nuevo`. |

---

## Notas sobre el flujo individual pendiente

- **Endpoint de registro individual** (`POST /personas/registro`): no implementado en esta iteración. El modelo de datos (`Persona.hashed_password`, `rol = individuo`, `email`) lo soporta; la limitación es de endpoint, no de dominio.
- **Responsable de iniciativa (`responsable_id`)**: actualmente se restringe a la organización (`org_id`). La persona independiente podría ser responsable si se extiende la validación de `responsable_tipo`; no se implementó para evitar ampliar el alcance sin pruebas de integración completas.
- **Invitación de participantes**: el modelo soporta la asociación N:M (`problema_participantes_persona`, `problema_participantes_organizacion`), pero la autorización requiere que la persona esté relacionada con una necesidad asociada al problema. Un flujo independiente de invitación (sin necesidad previa) está pendiente y documentado en `docs/riesgos_pendientes.md`.

---

## Riesgos documentados

- `docs/riesgos_pendientes.md` actualizado con:
  - P0 (`Anexo_Risk`): confirmado; no integrado.
  - P1 (`EnRuta`): confirmado; `SECRET_KEY` requiere entorno.
  - Autorización individual: implementada en datos (`Persona` con `hashed_password`) y en `auth.py`, pero pendiente de endpoint público completo (`POST /personas/registro`) y de flujo completo de iniciativa con `responsable_tipo = individuo`.
  - Migración PostgreSQL: pendiente (`tests/test_problema_colectivo.py` tiene `test_migracion_postgresql` con `skipif` si `TRAMA_TEST_POSTGRES_URL` no está configurada).
  - Datos sintéticos: obligatorio (`origen_datos = synthetic_pilot`). El piloto real requiere proceso de consentimiento y licencia verificada.
  - No producción: no se afirma impacto verificado ni impacto real.

---

## Pruebas y resultados

- Última ejecución: **30 passed, 1 skipped** (`tests/test_problema_colectivo.py`).
- `tests/test_auth_isolation.py`: 3 passed (token expiration, hash, synthetic tag).
- `tests/conftest.py`: configuración de base efímera con `TRAMA_ABIERTA_SECRET_KEY` y `DATABASE_URL` locales; sin credenciales reales.
- Nuevas pruebas de seguridad añadidas:
  - `test_rechaza_necesidad_inexistente`
  - `test_no_puede_ver_problema_de_otra_org`
  - `test_no_puede_incorporar_organizacion_sin_relacion`
  - `test_no_puede_cambiar_estado_de_problema_ajeno`
  - `test_sin_duplicados_en_relaciones`
  - `test_privacidad_necesidades_asociadas`
  - `test_flujo_completo_necesidad_problema_iniciativa`

---

## Estado de PostgreSQL

- Servicio PostgreSQL: **no disponible en esta iteración**.
- Prueba de integración (`test_migracion_postgresql`): marcada con `skipif` (`TRAMA_TEST_POSTGRES_URL`).
- Migración SQLite (`002_problemas_colectivos.sqlite.sql`) validada con `sqlite3` y `pytest`.
- Dependencias (`psycopg2-binary`) presentes en `requirements.txt`; no se ejecutan sin servicio.
- Recomendación: ejecutar `tests/` con `TRAMA_TEST_POSTGRES_URL=postgresql://...` cuando el servicio esté disponible para validar integridad N:M y restricciones (`ON DELETE CASCADE`, `CHECK`) en PostgreSQL.

---

## Pasos para reproducir el flujo individual completo (documentado)

Nota: el registro individual (`POST /personas/registro`) no está implementado como endpoint público en esta iteración, pero el flujo es reproducible manualmente con datos sintéticos a través de `Persona` en la base de datos y la autenticación con `email` + `hashed_password`. El diseño del modelo (`Persona.hashed_password`, `rol = individuo`, `email`) lo soporta.
