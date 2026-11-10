# Governance — POOLAR (Operational Model)

> Updated: 2026-11-10 (English translation/alignment). Status: **proposed + partially implemented (Phase 0)**.  
> Principles: **fail-closed**, least privilege, separation of duties, traceability, scope isolation. **POOLAR decides; CASE/external modules only propose.**

## 1) Principles

- **Authority:** execution of sensitive business effects requires a valid decision in POOLAR (automatic under explicit policy or HITL).
- **Fail-closed:** missing context, permission, scope, handler, or sufficient evidence → block/do not execute.
- **Separation of duties:** proposers do not approve/execute their own requests (except safe withdrawal without execution, where policy allows).
- **Scope (tenant/personal):** minimum access to the corresponding scope; no cross-tenant or cross-person leakage.
- **Auditability:** relevant decisions leave a trace: actor, action, context, reason, state, result/error, timestamps, correlation.
- **Idempotency/recovery:** safe retries without duplicating effects; recoverable states.

## 2) Actors and scopes

| Actor | Typical scope | Notes |
|---|---|---|
| Organization (operational member) | `organizacion_id` | Permissions by role within the org. |
| Individual / person | personal (`persona_id`, no `organizacion_id`) | Current policy: view/withdraw own HITL; no self-approval and no third-party approval without explicit authority (fail-closed). |
| System / automation | per policy | Only explicitly auto-approved routes; traceable. |
| Governance authority (future, explicit) | defined by policy | For escalation/exceptions; must be nominated, auditable, and must not relax isolation by default. |

## 3) Permissions matrix (Phase 0 base, to be completed)

| Capability | `member`/`observer` | `coordinator`/`manager`/`responsible`/`approver`/`admin` | Proposer (same actor) | Individual (personal scope) |
|---|---:|---:|---:|---:|
| View request in scope | **Yes** (read in scope) | Yes (in scope) | Yes (in scope) | Yes (own) |
| Approve/execute | No | Yes, in scope, not own | **No** (self-approval blocked) | **No** (self); third parties **No** (fail-closed policy) |
| Reject | No | Yes, in scope | **Own withdrawal allowed** (no execution) | **Own withdrawal allowed** |
| Retry `failed_retryable` | No | Yes (via approve), in scope | No (if self-approval implied) | N/A per policy |
| Close `failed_retryable` by rejection | No | Yes, in scope | Withdrawal if policy applies | Own withdrawal |
| Manage policy/roles | No | Admin role only (as defined) | No | No |

*Partially implemented in `src/core/agent_harness/approvals.py` and Phase 0 tests; read vs manage coverage and all endpoints/actions must be fully formalized and tested.*

## 4) HITL flow (states)

`pending` → (authorized approval) → `executing` → `executed`  
`pending` → (authorized reject/withdrawal) → `rejected`  
handler failure → rollback → `failed_retryable` → (approve/retry) or (reject/close)  
`executed` → terminal (idempotent re-approval, no duplicated effect)  
`expired`/terminal → do not approve or execute.

## 5) Approval, execution, and resumption

- **Approval does not imply uncontrolled execution:** an authorized approval triggers the resumable handler transactionally and records result/error.
- **Idempotency:** duplicate actions/keys must not duplicate effects; terminal executed state remains idempotent.
- **Concurrency:** concurrent approve/execute attempts must produce a single effect (verified in disposable PG evidence; revalidate in CI/target).
- **Handler failure:** no silent success; fail-safe state (`failed_retryable`) with audit.

## 6) Evidence and open gates

- Local (non-PG, 2026-11-10): **171 passed, 7 skipped, 1 xfailed**.
- Formal Phase 0 closure remains gated by external evidence (CI green, PG job/secrets, exhaustive authz/E2E/fault-injection as required).
- Real data/consent/GDPR operations, license/IP clearance for blocked repos, and runtime L1-EVAL-SYNTH require explicit human/legal authorization.

## 7) References

- `BOUNDARIES.md`, `INTENT.md`, `FASE0_CHECKLIST_CIERRE.md`, `AUDIT_READY_POOLAR.md`
- `docs/modelo_autorizacion.md`, `docs/CONVENTIONS.md`
- `src/core/agent_harness/approvals.py`, `src/core/agent_harness/handlers.py`, `tests/test_fase0_*`