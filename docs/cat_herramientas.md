# Operational Tools Catalog — POOLAR

> Updated: 2026-11-10. Status: **development/prototype, not production**. Capabilities are implemented incrementally; this catalog is a functional map (some items may be planned/partial). Use `synthetic_pilot` by default.

## 1. Discovery / matching
- Deterministic need matching (category, scope, constraints, scale, required resources).
- Match explanation (shared criteria, differences, gaps).
- Relationship proposal/accept/reject and persistence (where implemented).

## 2. Collective capacity (aggregation, resources)
- Shared demand calculation (explicit units/assumptions).
- Gap identification (resources, knowledge, capabilities).
- Capability/resource search, offers, reservation/release/use tracking (as implemented).

## 3. Solution design (feasibility, initiatives)
- Alternative comparison with documented criteria and assumptions.
- Initiative creation from validated problems, commitments, and activity records.

## 4. Execution and measurement (execution, outcomes, audit)
- Event/milestone recording.
- Metrics/observations and baseline comparison.
- Summary generation and audit history.

## 5. Autonomy, consent, and traceability (audit, provenance, exports)
- Provenance registration/retrieval.
- JSON/CSV exports (authorized/synthetic context).
- Import validation and schema/contract exposure.
- Visibility controls (`private`/`shareable`/`public` as implemented).
- Invitations/participation with effective consent.

## Cross-cutting requirements
- Typed inputs/outputs, permissions, defined errors, audit events, idempotency where applicable.
- Contracts/schemas: `src/core/contracts.py`, module contracts, runtime OpenAPI (`/docs`).
- No unnecessary PII in public DTOs/logs/exports.
- HITL/governance for sensitive actions (POOLAR retains authority; modules propose).
- External repo integrations only with verified rights/remediation and explicit authorization. Verify implementation status in code/tests.
