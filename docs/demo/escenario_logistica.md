# Shared Logistics Demo Scenario — POOLAR

> Updated: 2026-11-10. Status: **synthetic example (`synthetic_pilot`)**, not real operations or verified impact.

## Context

Several people and small businesses need access to suitable logistics services. No real route, savings, or outcomes are claimed; this is a documented synthetic example.

## Participants (synthetic IDs)

- **P1 (Persona):** needs regular transport (Seville).
- **P2 (Persona/small business):** needs deliveries (Seville).
- **C3 (Capability/knowledge):** logistics availability (example).
- **O4 (Organization):** can contribute capacity or negotiate providers.

## Synthetic data requirement

All records are labeled with `origen_datos = synthetic_pilot`. The flow is exercised through POOLAR APIs (product flow, not bypassed).

## Illustrative operational flow

1. Register needs for P1, P2, O4.
2. `matching.find_related_needs` → match P1↔P2 (transport/deliveries/logistics).
3. Review match; reject for documented differences (scale/schedule), then accept.
4. Create a Collective Problem linking P1+P2 needs (`synthetic_pilot`).
5. `aggregation.calculate_shared_demand` → shared demand (units/month) with explicit assumptions.
6. `resources.search` → find logistics capability/knowledge (C3).
7. Identify gaps (missing capacity).
8. `feasibility.compare_alternatives` → compare options (share resources, aggregate demand, shared route) with explicit assumptions.
9. `initiatives.create_from_problem` → initiative to evaluate shared route (responsible org O4).
10. Record commitments and activities.
11. Record milestones and define outcome metrics.
12. Review history and export JSON/CSV.
13. Repeat from a clean state (reproducible).

## Local reproduction (if demo script/mode is available)

```
POOLAR_SECRET_KEY=demo-key POOLAR_DEMO_MODE=true python docs/demo/escenario_logistica.py
```

> Verify script availability and current behavior in this repository; demo mode uses predefined synthetic accounts.

## Notes

This scenario is illustrative. Pending items (accessibility, persistent invitations/consent flows, full WCAG, real PostgreSQL validation in target env, etc.) are tracked in `docs/hoja_de_ruta.md` and `BACKLOG_PRIORIZADO_POOLAR.md`.
