# Pending Risks — POOLAR

> Updated: 2026-11-10 (`fase0-gobernanza`). Status: **development/prototype, not production**. Risks are classified for prioritization; listing does not imply remediation unless explicitly evidenced.

## Critical / open

| Risk | Impact | Status | Mitigation / next step |
|---|---|---|---|
| **Phase 0 closure without external gates** | False confidence in “closed” | Open | Green CI on target HEAD, PG job with `POOLAR_TEST_POSTGRES_URL`+secrets, revalidate concurrency/migrations, E2E/fault-injection as required. |
| **Secrets/credentials in local environments** | Exposure if leaked | Partial | `.env` gitignored; never commit secrets. **Rotate** credentials if exposed outside the authorized machine/environment. Formal management/rotation pending. |
| **GDPR/PII and real data** | Compliance/legal | Open | Maintain `synthetic_pilot`; consent, minimization, retention, scope-based access, and provenance before real pilots. |
| **Licenses/IP of ecosystem repos** | Improper reuse | Open | Do not reuse/integrate code from repos without verified rights (see governance/ecosystem). Keep own adapters/contracts. |

## High / medium

| Risk | Status | Note |
|---|---|---|
| Incomplete authz/HITL coverage across all endpoints/actions | Partial | Strong and tested core; complete matrix and E2E by action/role/scope. |
| SQLite vs PostgreSQL differences (concurrency/locking) | Partial | PG-only guards and tests exist; run on real PG/CI for valid evidence. |
| Integration with external modules/providers | Controlled (dev) | Contracts/adapters/mocks only; no execution authority; explicit degradation and provenance. |
| Incomplete accessibility, observability, and operational UX | Partial | Incremental improvements; does not block HITL invariants. |
| Documentation drift across iterations | Mitigating | Index/MkDocs, legacy archive, and ongoing update passes. |

## Historical (context)

- Previous P0/P1 findings in external repos (e.g. `Anexo_Risk`, `EnRuta`) treated as audit references; not integrated without remediation/rights/authorization.
- Do not declare production or verified impact without reproducible evidence.
