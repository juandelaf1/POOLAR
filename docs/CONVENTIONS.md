# Repository Conventions

> Established: 2026-11-10. Scope: POOLAR repository.

## Language

- **Default language: English.** All repository content should be in English: documentation, code comments, docstrings, commit messages, issue/PR descriptions, variable/domain naming where practical, and user-facing technical copy.
- **README:** bilingual, with **English as the default/primary content** and **Spanish available in a collapsible section** (`<details><summary>Español</summary>...</details>`).
- **Existing content:** some legacy/current documents may still be in Spanish. They should be migrated to English progressively when touched, while preserving meaning and evidence. Do not invent or lose information during translation.
- **Domain terminology:** Spanish domain terms may be kept in identifiers/APIs where already established for compatibility; document or map them when relevant.

## Contracts

Contracts are defined and exposed at multiple levels in this repo:

| Level | Location | Notes |
|---|---|---|
| Domain/DTO contracts (Pydantic) | `src/core/contracts.py` | Versioned domain entities and API DTOs; public DTOs must not expose sensitive personal/auth fields. Includes data provenance (`synthetic_pilot`/`real_pilot`). |
| Module/capability contracts (v0) | `src/core/contracts_modules.py`, `src/core/contracts_case.py` | `ModuleManifest`, `ActorContext`, `ExecutionRequest`, `EvidenceEnvelope`, `CapabilityResult`, `DecisionProposal`, `ApprovalRecord`. Modules propose; **POOLAR retains HITL/authority/execution control**. |
| HTTP/API contract (runtime) | FastAPI app (`src/main.py`, services/schemas) | OpenAPI generated at runtime: `/docs`, `/redoc`, `/openapi.json`. No separately committed canonical OpenAPI artifact unless explicitly added. |
| Persistence/schema contract | `src/core/models.py`, `src/core/alembic/`, `alembic.ini` | SQLAlchemy models and Alembic migrations. |
| Governance/HITL behavior | `GOBERNANZA_POOLAR.md`, `FASE0_CHECKLIST_CIERRE.md`, `docs/modelo_autorizacion.md`, `src/core/agent_harness/*` | States, permissions, fail-closed rules, idempotency/resumption (operational contract). |

**Ecosystem (outside this repo):** versioned inter-repo contracts (envelope, logistics/case/climate capabilities, error codes, JSON schemas) live in the governance workspace `POOLAR_ECOSYSTEM_GOVERNANCE/18_contracts/`.

## Contribution hygiene

- No secrets or PII in code/docs/commits. `.env` stays gitignored.
- Prefer backward-compatible, incremental changes in dev stage.
- Keep claims evidence-based (no production/verified-impact claims without evidence). Use labels like `synthetic_pilot`, `estimated`, and provenance where applicable.
