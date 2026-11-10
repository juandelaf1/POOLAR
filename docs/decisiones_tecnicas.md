# Technical Decisions — POOLAR

> Updated: 2026-11-10. Status: living record for **development/prototype (Phase 0)**, not production.

## Architecture and stack

- **Modular monolith:** FastAPI + SQLAlchemy + Pydantic v2. PostgreSQL is the target database; SQLite is used for controlled local dev/tests.
- **No microservices/shared DB:** ecosystem integrations are contract/adapter-based (no shared database, no cross-repo ORM/domain-model library).
- **Migrations:** Alembic (`src/core/alembic/`, `alembic.ini`).

## Security and governance

- **Secrets:** `POOLAR_SECRET_KEY` required from environment (fail-safe if missing); no hardcoded default key.
- **Auth:** PBKDF2-SHA256 + JWT; actor/context scoping (organization/person).
- **HITL / Agent Harness:** fail-closed, no self-approval, tenant/personal isolation, approval→execution via resumable handlers, idempotency/dedup, explicit states and audit trail. POOLAR retains execution authority.

## Contracts and data

- **In-repo contracts:** Pydantic domain/DTOs (`src/core/contracts.py`) and modular capability contracts (`src/core/contracts_modules.py`, `src/core/contracts_case.py`). HTTP contract exposed via FastAPI OpenAPI (`/docs`, `/openapi.json`) at runtime.
- **Ecosystem contracts:** versioned inter-repo schemas/envelopes live in `POOLAR_ECOSYSTEM_GOVERNANCE/18_contracts/` (outside this repo).
- **Provenance:** data labeled by origin/status (`synthetic_pilot` default); estimates vs verified outcomes must be distinguished. No verified impact claims without evidence.

## Analytics

- **Separated and read-only:** medallion exports/build (`scripts/export_medallion_raw.py`, `analytics/build_local_lakehouse.py`) with no HITL/domain side effects. Strategic managed lakehouse (Basin/Pipelines → R2/Iceberg) contemplated, not implemented.

## Integrations and boundaries

- External modules/providers **propose only** through adapters/mocks/contracts; no authority transfer. Reuse/integration of audited external repos requires verified rights, P0/P1 remediation where applicable, and explicit authorization.
- Prefer incremental, backward-compatible changes in development (dual-read/dual-write/progressive correlation where needed).

## Limitations

- Not production-ready; formal Phase 0 closure depends on external gates (CI green, PG job/secrets, exhaustive E2E/fault-injection as required).
- Advanced capabilities (pgvector/RAG, LangGraph, observability backends, PostGIS/OR-Tools, MCP) are adopted only when justified by demonstrated need.
