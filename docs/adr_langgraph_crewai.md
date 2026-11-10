# ADR: LangGraph vs CrewAI

> Updated: 2026-11-10. Status: **proposed/preferred direction (not adopted by default)**. External orchestrators are evaluated only when a demonstrated need exists.

## Decision

Prefer **LangGraph** as the primary candidate for durable agent workflow orchestration if/when needed. Keep **CrewAI** as an alternative to evaluate only for specific requirements not well served by LangGraph. No mandatory adoption in current Phase 0.

## Rationale

- LangGraph can support persistent state, checkpoints, multi-step flows, and human review points.
- POOLAR requires deterministic steps, explicit HITL/governance, and re-validation of authorization at domain operations.
- Domain logic, tool contracts, and tests must remain framework-independent; POOLAR governance remains authoritative.

## Consequences

- Any orchestration integration must live outside/around the core domain and must not bypass HITL, scoping, or audit controls.
- Framework state is not the source of truth for POOLAR core entities.
- Re-evaluate alternatives only against concrete, evidenced needs.