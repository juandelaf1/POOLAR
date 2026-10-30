# BOUNDARIES.md — Poolar

## Límites estrictos que la IA nunca debe romper

### Arquitectura
- Monolito modular en FastAPI + SQLAlchemy + PostgreSQL. No microservicios.
- SQLite solo para desarrollo controlado y tests locales.
- No introducir CrewAI, LangGraph, microservicios ni sistemas de IA obligatorios sin justificación.
- Las migraciones se ejecutan con Alembic, no con `create_all()` en producción.

### Seguridad
- `POOLAR_SECRET_KEY` (antes `POOLAR_SECRET_KEY`) obligatoria de entorno. Falla segura si falta.
- Autenticación JWT con PBKDF2-SHA256.
- Autorización por organización y rol, y por persona individual (`tipo` en token).
- No tokens ambiguos con ambos `organizacion_id` y `persona_id`.
- Datos sensibles (`email`, `contacto`, `dni`, `ubicaciones_privadas`) nunca en respuestas públicas.
- Rate limiting y validación de entrada en todos los endpoints.

### Datos
- Etiqueta `synthetic_pilot` obligatoria en todos los datos de desarrollo/prueba.
- No datos personales reales sin proceso de consentimiento documentado.
- Procedencia de datos (`DataProvenance`) en cada registro.
- No confundir datos sintéticos con resultados verificados.

### Código
- Tipado Pydantic estricto en todos los contratos.
- Contraseñas en cuerpo JSON, nunca en URL.
- `create_all()` solo para SQLite en desarrollo.
- PostgreSQL se inicializa mediante migraciones Alembic.
- Tests contra PostgreSQL real en CI.

### Testing
- No aceptar códigos HTTP de error como si una operación hubiese tenido éxito.
- No tests vacíos (`pass`).
- Pruebas negativas de autorización obligatorias.
- No sustituir PostgreSQL por SQLite en validación de migraciones.

### Documentación
- No declarar "listo para producción".
- No afirmar impacto verificado sin evidencia.
- No presentar agentes de IA como funcionales si no lo están.
- No presentar matching determinista como probabilidad estadística.