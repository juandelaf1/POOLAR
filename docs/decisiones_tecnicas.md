# Decisiones técnicas — MVP Poolar v0.6

- Monolito modular (`FastAPI`, `PostgreSQL` objetivo, `SQLAlchemy`, `Pydantic v2`); no microservicios.
- Contratos (`contracts.py`) basados en `AGENTS.md` (`Organización`, `Necesidad`, `Recurso`, `Iniciativa`, `Decisión`, `EventoAuditoría`, `ProcedenciaDatos`) y `v0.5`.
- `SECRET_KEY` de entorno; `fail` si falta; sin clave predeterminada (corrección de `P1` `EnRuta`).
- Datos sintéticos etiquetados; no se confunden con resultados verificados (`AGENTS.md`; `v0.5`).
- `Anexo_Risk`/`EnRuta`/`CASE`: no integrados; referencia `D`/`C`; `A` descartado sin evidencia.
- Exportación `JSON`/`CSV` básica; no integración de pagos; no IA obligatoria.
- Limitación: no producción; no afirma impacto verificado.
