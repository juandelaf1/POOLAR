# ADR: LangSmith vs Langfuse for AI Observability

> Updated: 2026-11-10. Status: **proposed/preferred direction (not adopted by default)**. Adopt only when observability needs are demonstrated and privacy/ops constraints are met.

## Decision

Prefer **OpenTelemetry** as the instrumentation baseline and **self-hosted Langfuse** as the primary candidate platform for AI/LLM observability if adopted. **LangSmith** remains an optional development/evaluation tool where acceptable, not the default for sensitive environments.

## Rationale

- Self-hosted observability better aligns with data control, privacy, and autonomy goals.
- OpenTelemetry provides portable traces/metrics.
- External SaaS observability must be evaluated against data egress, redaction, and governance requirements.

## Consequences (if adopted)

- Telemetry must be environment-configurable and **disabled by default** in sensitive contexts.
- Traces/logs must not include secrets, tokens, or unnecessary PII; define redaction and data egress policies.
- Keep implementation optional and decoupled from core domain/HITL logic. Re-evaluate based on concrete needs.