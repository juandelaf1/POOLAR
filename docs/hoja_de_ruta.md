# Roadmap — POOLAR

> Updated: 2026-11-10 (`fase0-gobernanza`). Status: **development/prototype, not production**. Phase 0 core is strong; formal closure is subject to external gates.

## Completed (foundation and Phase 0)

- [x] Modular monolith (FastAPI + SQLAlchemy); JWT/PBKDF2 auth, individual registration (`POST /personas/registro`), org/person authorization, `synthetic_pilot` data.
- [x] Domain model: Need, Collective Problem, Initiative, Decision, Invitation/Participation, audit, export.
- [x] Governance/HITL: fail-closed, tenant/personal scoping, no self-approval, safe self-withdrawal, authorized approval→transactional execution of resumable handlers, idempotency/dedup, states (`pending/executing/executed/failed_retryable/rejected/expired`), migrations 0004/0005.
- [x] Deterministic handlers registered/validated (Phase 0 core), declarative policies, lifecycle audit.
- [x] Local suite (2026-11-10, no PG): **171 passed, 7 skipped, 1 xfailed**; deterministic PG-only/reachability guards; `RESUMABLE_HANDLERS`/fixture isolation fixed.
- [x] Prior disposable-PG evidence: single-effect concurrency (`test_fase0_p04_concurrency_pg.py`), migrations 0004+0005 (revalidate in target/CI environment).
- [x] Modular contracts/adapters (manifests/ports, synthetic mocks, proposal-only); dev-stage ecosystem contract adapters in EnRuta/SkyCast (PRs merged), CASE `case.evaluate` boundary adapter (additive).
- [x] Documentation reorganized and buildable: `docs/index.md`, `mkdocs.yml`, `docs/archive/fase0/`, `docs/ANALYTICS_LAKEHOUSE.md`, aligned README/checklist/governance/layers; English default + bilingual README, conventions, progressive migration.
- [x] Analytics (separated, read-only): medallion raw/staging/marts, idempotent/redacted export `scripts/export_medallion_raw.py`, synthetic samples, dbt models/profile, `analytics/build_local_lakehouse.py` (local DuckDB), **`dbt run` PASS=3**.
- [x] Docker/Compose, Alembic, CI workflow defined; global correlation middleware + ops/HITL envelope enrichment (additive).

## Pending / open

- [ ] **Formal Phase 0 closure (external gates):** green CI on target HEAD, PG job with managed secrets, exhaustive E2E matrix where missing, real mid-handler fault injection if required.
- [ ] Revalidate PG concurrency/migrations in target environment after relevant changes.
- [ ] Consent process and operational GDPR/PII controls for real data; secret rotation/management in environments.
- [ ] Real external integrations (CASE/modules/providers) only by contract, with authorization, synthetic/authorized data, and without expanding execution authority.
- [ ] Full HITL state observability/UI; complete WCAG accessibility; expanded E2E (Playwright) as needed.
- [ ] Real semantic search (pgvector) and advanced capabilities (RAG, PostGIS, OR-Tools, MCP, LangGraph/LangSmith) only when justified by demonstrated need.
- [ ] Verified licenses/rights for blocked repos before reuse.

## Suggested next iterations

1. **Target CI/PG:** run PG suite with `POOLAR_TEST_POSTGRES_URL` + migrations and publish evidence.
2. **Analytics:** extend dbt models/tests over real exports; traceable impact marts.
3. **Contract adoption in POOLAR:** continue normalizing correlation/envelope/provenance in business/read APIs (backward-compatible) with contract tests.
4. **Docs:** keep remaining docs/ADRs aligned in English and current as they are touched.