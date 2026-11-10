# ADR: Agent Harness — Design and Decisions

> Updated: 2026-11-10. Status: **accepted/evolving** (POOLAR-owned minimal harness; external orchestration frameworks evaluated only when justified).

## Decision

Implement and evolve a lightweight, **POOLAR-owned Agent Harness** (`src/core/agent_harness/`) with explicit control over context, tools, policies, approvals, and execution state. External frameworks (LangGraph, CrewAI, Deep Agents, etc.) are not adopted by default and are evaluated only when durable workflow needs justify them.

## Rationale

- POOLAR requires explicit control over permissions, authorization, approvals, and HITL boundaries.
- Generic agent frameworks do not replace POOLAR's governance/authorization model.
- The harness separates concerns (context, tool registry/contracts, policy, approvals, state) and supports fail-closed behavior.

## Implemented/evolved components (current direction)

- **Execution context / actor scoping** (tenant/personal context propagation).
- **Approval lifecycle & persistence** (`ApprovalManager`, states, idempotency, concurrency controls, resumable handlers).
- **Policy/governance checks** (fail-closed, no self-approval, scope enforcement).
- **Tool/handler registry** for governed resumable actions.
- **Auditability and security limits** as applicable.

> Verify exact component names/APIs in `src/core/agent_harness/*` (implementation has evolved beyond the initial skeleton).

## Alternatives considered

- **LangGraph/CrewAI/Deep Agents:** evaluate later for concrete, demonstrated needs (durable workflows, multi-agent orchestration) without displacing POOLAR governance or adding unnecessary complexity. See related ADRs.