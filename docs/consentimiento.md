# Consent and Privacy — POOLAR

> Updated: 2026-11-10. Status: **documented; not implemented as an automated end-to-end flow**. Real data is blocked/controlled until a documented process exists.

## Principles

1. **Synthetic by default:** `synthetic_pilot` data is required unless/until a documented consent process exists for real data.
2. **Explicit consent:** no real personal data may be recorded without explicit, recorded, and revocable consent.
3. **Data minimization:** collect only what is necessary for the use case.
4. **Visibility boundaries:** separation between private, shareable, and public information must be explicit per entity.

## Consent flow (pending implementation)

1. User receives clear information about what data is collected and for what purpose.
2. User gives explicit consent (and scope/version).
3. Consent is recorded with date, version, and scope.
4. User can revoke at any time.
5. Data is exported/deleted according to revocation and retention rules.

## API and governance controls (current intent/behavior)

- `origen_datos` should be `synthetic_pilot` in MVP/dev flows.
- Attempts to register/use real data (`real_pilot`) without valid consent context must be denied by policy/API validation (e.g. HTTP 403) and/or routed to human review as applicable.
- HITL/governance must fail closed for sensitive or insufficiently evidenced actions; POOLAR does not execute effects without authorized approval where required.

> **Note:** implementation details evolve; verify against current code/tests (`src/main.py`, `src/core/contracts.py`, agent harness, Fase 0 tests). Prior statements about components "not integrated" may be outdated — rely on `FASE0_CHECKLIST_CIERRE.md` and test evidence.

## Pending risks

- No automated consent capture/registry/ revocation workflow.
- No formal retention/deletion/access/portability process.
- No assigned DPO/operational privacy ownership (project-dependent).
- Real-user pilots require legal/privacy review and environment controls.

## References

- GDPR / applicable local data protection regulations.
- `docs/modelo_autorizacion.md` — authorization model.
- `docs/riesgos_pendientes.md` — risk register.
- `BOUNDARIES.md`, `GOBERNANZA_POOLAR.md`.