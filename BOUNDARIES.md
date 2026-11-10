# BOUNDARIES.md — POOLAR

## Strict boundaries that must not be broken

### Architecture
- Modular monolith (FastAPI + SQLAlchemy + PostgreSQL target). No microservices by default.
- SQLite only for controlled local development and tests.
- Do not introduce CrewAI, LangGraph, distributed infrastructure, or mandatory AI systems without demonstrated need and justification.
- Migrations are managed with Alembic (not `create_all()` in production/target flows).

### Security
- `POOLAR_SECRET_KEY` is required from environment. Fail safely if missing.
- Authentication: JWT with PBKDF2-SHA256.
- Authorization by organization/role and by individual person context (`tipo` in token/actor context). No ambiguous tokens with conflicting contexts.
- Sensitive data (`email`, `contact`, `dni`, private locations, etc.) must never be exposed in public responses/DTOs, logs, or audit payloads.
- Apply rate limiting and input validation on endpoints as applicable.
- HITL/governed actions must be fail-closed; no self-approval and no authority transfer to external modules.

### Data
- `synthetic_pilot` labeling/provenance is required for dev/test data unless a documented consent process exists.
- No real personal data without documented consent, privacy, and operational controls.
- Preserve provenance (`DataProvenance`/`_provenance`) on records/exports where applicable.
- Do not confuse synthetic/estimated data with verified results.

### Code
- Strict Pydantic typing for contracts/DTOs.
- Passwords/secrets in request bodies or env vars only, never in URLs.
- `create_all()` only for SQLite/local dev as appropriate; PostgreSQL is initialized via Alembic migrations.
- Test PostgreSQL behavior in CI/target environments when required (do not substitute SQLite for migration/concurrency validation).

### Testing
- Do not accept error HTTP codes as success.
- No empty tests (`pass`).
- Negative authorization tests are required for sensitive flows.
- Do not claim green status without evidence; distinguish local/CI/PG/external-provider results.

### Documentation and claims
- Do not declare "production-ready".
- Do not claim verified real-world impact without evidence.
- Do not present AI agents/modules as executing authority in POOLAR context; modules propose, POOLAR governs/executes.
- Do not present deterministic matching as statistical probability.

### Language and conventions
- Repository default language is **English** (README bilingual, English default). See `docs/CONVENTIONS.md`. Keep contracts and behavior backward-compatible in dev where specified.