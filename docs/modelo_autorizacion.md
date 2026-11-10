# Authorization Model — POOLAR

> Updated: 2026-11-10. Status: **partially implemented and evolving (dev/Phase 0), not verified with real users or production**.  
> References: `GOBERNANZA_POOLAR.md`, `docs/modelo_problemas_colectivos.md`, `BOUNDARIES.md`, `src/core/agent_harness/approvals.py`, `src/main.py`.

## Principles

- **Least privilege and fail-closed:** missing context/permission/scope/evidence ⇒ deny or do not execute.
- **Scope isolation:** organization (`organizacion_id`) and individual/personal (`persona_id`/personal actor), no cross-tenant or cross-person leakage.
- **Separation of duties:** proposers do not self-approve/execute; safe self-withdrawal without execution is allowed when policy permits.
- **POOLAR retains authority:** HITL/decision/governed execution stays in POOLAR; external modules/CASE only propose.
- **Data and privacy:** `synthetic_pilot` by default; no unnecessary PII in responses/logs/exports; consent/provenance required for real data.

## Actors and authentication

| Actor | Authentication | Typical context |
|---|---|---|
| Organization user | `POST /auth/token` (JWT, PBKDF2-SHA256) | `tipo=organizacion`, `organizacion_id`, operational role |
| Individual/person | `POST /personas/registro` + `POST /auth/token` | `tipo=individuo`, `persona_id`/personal scope |
| System/automation | Explicit policy | Only explicitly auto-approved and traceable routes |

`POOLAR_SECRET_KEY` is required (fail-safe if missing). No ambiguous token contexts.

## Summary matrix (domain and HITL)

| Capability | Individual (own/personal scope) | Org member/observer | Org manager/coordinator/responsible/approver/admin | Notes |
|---|---|---|---|---|
| Register/auth | Yes (registration and token) | Yes (per org onboarding/token) | Yes | Credentials in JSON body |
| Create/read needs | Own and accessible per visibility/scope | Own org + accessible (`shareable/public`) per rules | Within org scope | No sensitive data in public DTOs |
| Collective problem / initiative / decision | Per participation/responsibility and governance | Per membership/scope/role | Per role and scope | Some actions go through HITL evaluation |
| View HITL request | Yes, if in own/personal scope | Yes, if in scope (read) | Yes, in scope | Out of scope: hide/deny (404/403 per endpoint) |
| Approve/execute HITL | **No** self-approval; third parties **no** without explicit authority (fail-closed) | No | Yes, in scope, not own | Authorized `approve()` executes handler and records result |
| Reject HITL | Own withdrawal allowed (no execution) | No management action | Yes, in scope | Proposer cannot self-approve |
| Retry/close `failed_retryable` | Per policy (own withdrawal if applicable) | No | Yes, in scope, not own | Idempotent: no duplicated effect |

*The exact per-endpoint/action matrix is validated in code and tests (`tests/test_fase0_*`, `tests/test_p03_http_governance.py`, etc.); exhaustive coverage is part of formal Phase 0 closure.*

## HITL flow (implemented)

`pending` → (authorized approval) → `executing` → `executed`  
`pending` → (authorized reject/withdrawal) → `rejected`  
handler failure → rollback → `failed_retryable` → authorized retry/close  
`executed` → terminal (idempotent, no duplicated effect)  
`expired`/terminal → do not approve or execute.

## Evidence and verification

- Local without PG (2026-11-10): **171 passed, 7 skipped, 1 xfailed** (SQLite). Phase 0/governance and resumption suites covered.
- Prior disposable-PG evidence: migrations 0004+0005 and single-effect concurrency race; **revalidate** in target/CI environment with `POOLAR_TEST_POSTGRES_URL`.
- Known gaps: exhaustive matrix across all actions/endpoints, green CI/PG with managed secrets, operational consent/GDPR for real data.

## Constraints

- Not production; no verified impact without evidence.
- Do not relax isolation/HITL for convenience; do not grant execution authority to external modules.
