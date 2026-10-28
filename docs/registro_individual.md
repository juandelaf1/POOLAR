# Registro Individual — Decisión y Estado

Estado: **Implementado parcialmente** (`Persona` model + `auth.py` actualizado). Endpoint `POST /personas/registro` pendiente de integración completa en `main.py`. Documentado como pendiente en `docs/modelo_autorizacion.md`.

Restricción del piloto: `origen_datos=synthetic_pilot` obligatorio. No se habilita registro público con datos reales hasta que exista proceso documentado de consentimiento y privacidad.

**Validaciones aplicadas:**
- Email normalizado (`strip`, `lower`).
- Contraseña mínima 8 caracteres; hash `PBKDF2-SHA256`.
- Rol fijo a `individuo`; no se acepta `administrador` ni `miembro` desde este endpoint.
- Duplicados de email rechazados (`IntegrityError` capturado con mensaje genérico, sin enumeración de cuentas).
- Datos sensibles (`email` privado en DTO, nunca en eventos de auditoría).
