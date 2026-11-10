# CASE Initial Audit (read-only) — Modular Integration with POOLAR (Historical Record)

> Translated to English on 2026-11-10 for repository language convention. **Historical audit snapshot (2026-11-09)**; preserved as record. Static/read-only inspection of `C:\Users\JUAN\Desktop\Proyectos\CASE` (CASE not modified; its tests not executed in that audit; no secrets exposed). **Goal:** assess whether CASE should be exposed as a **CASE-POOLAR module** under governed modular architecture.

## 1) Observed evidence (CASE, at time)

- **Identity/maturity (declared):** CASE described as domain/provider-agnostic AI decision orchestration (hexagonal, FastAPI + Streamlit, HITL/risk-based automation, audit). Test counts declared in README were **not verified by execution** in that audit.
- **Stack:** Python >=3.11, FastAPI, Pydantic v2, httpx, python-dotenv; SQLite persistence present locally (not inspected).
- **Structure:** `case_core`, `case_api`, `case_infra`, adapters (`logistics_adapter`, `usgs_adapter`), `streamlit_app`, `tests/`, `docs/`.
- **Contracts/decision (sampled):** `AutomationDecision` (`AUTO_APPROVE|HUMAN_REVIEW|ESCALATE`), risk assessment, HITL required; processing/decision lifecycles defined. Conceptually aligned with HITL but with **its own authority model**.
- **Composition/authority:** engine built with domain registry, providers, audit adapter, decision repository, automation policy, cost model. CASE **persists its own decisions/audit** and resolves automation paths internally.

## 2) Fit with POOLAR modular architecture

POOLAR defines/implements generic module contracts, `ModuleManifest`/registry, mock adapters (including CASE mock), HTTP-safe composer — all **proposal/result only**, with **POOLAR as authority** (tenant, authz, HITL, execution, correlated audit). External real integrations are gated by Phase 0 closure/explicit gates.

## 3) Findings (fit / risks)

| Area | Finding | Implication |
|---|---|---|
| Maturity/architecture | Hexagonal, contracts, HITL, multi-domain, providers. | Good candidate as **capability module** (do not rewrite from scratch). |
| Dual authority | CASE has its own HITL/automation/audit/DB. | **Do not** embed CASE as executor/decider inside POOLAR. Risk of dual authority/inconsistent HITL/audit. |
| Integration surface | Stable POOLAR-oriented capability API/contract needed. | Requires **adapter/anti-corruption layer** and explicit capabilities. |
| Operational state | `.env`, `case_audit.db`, logs may exist locally. | Treat as **external/sensitive**; no secret/data copying; synthetic/authorized data only in isolated config. |
| Scaling | Performance/load/multi-tenant/SLO not assessed. | "Scale CASE" is separate; not a prerequisite for proposal-only module if capability is scoped. |
| License/governance | Verify LICENSE/dependencies before joint distribution/service. | IP/license review required. |

## 4) Recommendation (historical)

**Do not scale/integrate CASE "at large" immediately.** Create a **CASE-POOLAR adapter boundary module** after Phase 0 gates and with synthetic data:
1. Deep audit (isolated): verify tests, license, exportable capabilities, stable API/SDK, PII/secrets handling.
2. Module design (no authority coupling): manifest + adapter invoking CASE only for `DecisionProposal`/`CapabilityResult`/evidence; **POOLAR** validates tenant/actor, applies its HITL, executes effects.
3. Staged integration: mock → isolated HTTP/lib adapter with synthetic data → contract/timeout/failure tests → governed pilot.
4. Refactor/scale CASE only if audit requires (clean capability API, isolation, idempotency, observability, separation of proposal engine from own HITL persistence/authority in composed mode).

## 5) Decision criteria

- **Go (wrapper module):** stable capability, proposal-only mode possible, controllable timeouts/failures, license OK, synthetic data.
- **Refactor before:** cannot operate without coupled own HITL/persistence authority, no stable API, no data isolation, or insufficient integrity/performance.
- **Scale CASE infra:** only with load/SLO evidence and defined module boundary.

## 6) Subsequent progress (outside this historical snapshot)

- Ecosystem contract work and CASE `/api/v1/evaluate` envelope adapter (dev-stage, additive, recommendation-only) implemented later; baseline revalidated (**804 passed, 2 failed external Groq-live, 7 skipped** in 2026-11 run). See governance `18_contracts/case-evaluate.*` and current CASE repo state.