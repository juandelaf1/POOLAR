# Individual Registration — Status

> Updated: 2026-11-10. Status: **implemented (dev/prototype)**. Verify against current code/tests for exact behavior.

## Current state

- **Endpoint:** `POST /personas/registro` is implemented (individual/persona registration).
- **Authentication:** registered individuals authenticate via `POST /auth/token` with `tipo=individuo` context where applicable; passwords hashed with **PBKDF2-SHA256**.
- **Data default:** `synthetic_pilot` for MVP/dev flows. Real data requires documented consent and privacy controls (see `docs/consentimiento.md`).

## Applied validations (typical)

- Email normalized (trim/lowercase handling as implemented).
- Minimum password requirements and secure hashing (PBKDF2-SHA256).
- Fixed individual role for this registration path (no privileged/admin role granted by self-registration).
- Duplicate email handling without account enumeration (generic/conflict response).
- Sensitive data not exposed in public DTOs or audit events.

## References

- `docs/modelo_autorizacion.md` — authorization model and actor contexts.
- `src/main.py`, `src/core/auth.py`, `src/core/models.py`, `src/core/contracts.py` — source of truth.
- `docs/consentimiento.md`, `docs/riesgos_pendientes.md`.
