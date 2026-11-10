# Collective Problems Model — POOLAR

> Updated: 2026-11-10. Status: **defined in contracts/models and partially implemented (dev/prototype)**. Verify against current code/tests for exact fields and behavior.

References: `docs/vision_y_proposito.md`, `src/core/contracts.py`, `src/core/models.py`.

## Core entity: Collective Problem (`ProblemaColectivo`)

A Collective Problem is a domain entity representing a situation affecting multiple people or organizations that requires a coordinated response. It is not just a tag or an initiative type.

### Key distinctions

- **Individual need (`Necesidad`)**: a need/goal/problem declared by a person or organization.
- **Collective Problem (`ProblemaColectivo`)**: a validated grouping of related needs sharing context, cause, scope, or impact, potentially requiring a joint response.
- **Initiative (`Iniciativa`)**: a coordinated action proposed to address a problem (or part of it), not the problem itself.

This avoids conflating a potential match with a confirmed relationship.

## Fundamental relationships (conceptual)

```
Persona/Organizacion ── declares ──► Necesidad
Necesidad ── relates to (N:M, validatable/rejectable) ──► ProblemaColectivo
ProblemaColectivo ── involves ──► participating Personas/Organizaciones
ProblemaColectivo ── can generate ──► Iniciativa (1:N)
Iniciativa ── records ──► Decision / EventoAuditoria
```

## Domain rules (intent)

1. Not every group of similar needs is a Collective Problem; validation/state transitions are required (e.g. detected → analysis → validated/rejected).
2. A need may relate to more than one Collective Problem when contexts differ.
3. A Collective Problem does not require a prior organization; individuals can initiate and others can join under governance/consent rules.
4. Associated needs may not share the same solution; initiatives represent evaluated alternatives/actions.
5. Personal data remains separated; public DTOs must not expose sensitive personal fields.
6. Evidence/provenance is required before validation where applicable.
7. Incorrect matches/relations must be rejectable/correctable with audit traceability.

## Implementation notes

- Domain/contracts and persistence models define `ProblemaColectivo`, N:M linkage with needs, participants, initiatives, and state/evidence fields (see `src/core/contracts.py`, `src/core/models.py`, `src/main.py`).
- HITL/governance applies to sensitive transitions/actions as configured (Phase 0).
- Some pilot-readiness items (real-data validation, full methodology versioning, exhaustive audit/privacy guarantees) remain pending and evidence-dependent. See `docs/riesgos_pendientes.md` and `FASE0_CHECKLIST_CIERRE.md`.
