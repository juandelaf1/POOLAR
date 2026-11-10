# INTENT.md — POOLAR

> Updated: 2026-11-10. Status: **prototype / development (Phase 0), not production**.

## Purpose

POOLAR is a modular, transactional infrastructure to connect needs, organize capabilities, and execute collective solutions in a governed, traceable, and reusable way.

It is not a social network, a task manager, or a listings portal. It is cooperation infrastructure.

## Business/product objectives

1. Enable people and organizations to register needs, knowledge, and capabilities.
2. Discover collective problems through explainable matching.
3. Connect complementary resources and calculate shared demand.
4. Compare alternatives with explicit criteria and assumptions.
5. Organize initiatives with documented decisions and clear responsibilities.
6. Coordinate execution and measure outcomes with evidence/provenance.
7. Preserve data autonomy and reduce dependency on intermediaries.

## Core operational flow

Need → Discovery → Collective Problem → Capabilities & resources → Alternatives → Decision → Execution → Results → Reusable learning.

## Domain intent (rules)

- The fundamental unit is the shared problem and collective capability.
- People and organizations are first-class participants.
- `synthetic_pilot` is the default until a documented consent process exists for real data.
- AI/modules assist and propose; they do not hold execution authority in POOLAR context.
- Authorization is verified per operation (fail-closed).
- Sensitive collective actions require governed human approval (HITL) per policy.

## API/contracts intent

- Endpoints consume/produce typed JSON; runtime OpenAPI available (`/docs`, `/openapi.json`).
- Authentication via JWT with required environment secret.
- Passwords/secrets in JSON body or environment, never in URLs.
- Sensitive personal data is not exposed in public DTOs.
- Additive correlation/envelope fields (`X-Correlation-Id`, `correlation_id`, `data_status`, etc.) are being normalized for ops/integration compatibility.

## Design constraints

- Modular monolith (FastAPI + SQLAlchemy), PostgreSQL target; SQLite for controlled dev/tests.
- Reproducible migrations with Alembic.
- CI includes SQLite checks; real PostgreSQL validation and managed secrets remain external closure gates.
- Analytics separated and read-only (medallion/raw→staging→marts, DuckDB/dbt); no HITL/domain side effects.

## Current state (evidence-based)

- **Phase 0 HITL/governance:** core controls implemented and evolving (fail-closed, scoping, approvals, resumable handlers, idempotency/concurrency handling, audit). Formal closure gated by external CI/PG/E2E/fault-injection evidence.
- **Local (non-PG, 2026-11-10):** `pytest -q --rootdir=.` → **171 passed, 7 skipped, 1 xfailed**.
- **Integrations:** modular contracts/adapters in dev stage; ecosystem S2 adapters merged (EnRuta/SkyCast), CASE evaluate boundary adapter added (recommendation-only). External integrations require verified contracts/licenses/security and explicit authorization.
- **Documentation:** English by default, README bilingual, MkDocs index/archives, conventions and key docs aligned progressively.

## Pending (documented)

- Formal Phase 0 closure gates (CI green, PG job/secrets, exhaustive E2E/fault-injection as required).
- Consent/GDPR operational process for real data/pilots.
- Complete WCAG/accessibility, stable DTO/OpenAPI client generation, frontend hardening.
- License/IP clearance for blocked repos; external integrations only with authorization and synthetic/authorized data.
- Advanced capabilities (pgvector/RAG, orchestration/observability backends, PostGIS/OR-Tools, MCP) only when justified.