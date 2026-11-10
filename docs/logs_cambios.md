# Change Log — POOLAR MVP v0.6 (Historical Record)

> Translated to English on 2026-11-10 for repository language convention. **Historical snapshot (2026-10-28)**; preserved as record. For current progress see git history, `docs/hoja_de_ruta.md`, and audit docs.

Format: brief date / file / change / rationale

- 2026-10-28 / `src/main.py` / Added `/personas/registro` endpoint / Controlled individual registration, synthetic data.
- 2026-10-28 / `src/main.py` / Dual auth (`tipo` in JWT) / Person/organization separation.
- 2026-10-28 / `src/main.py` / `/problemas-colectivos` accepts `tipo=individuo` / Independent flow.
- 2026-10-28 / `src/main.py` / Initiative allows `responsable_tipo=persona` / Individual responsibility.
- 2026-10-28 / `src/main.py` / `/invitaciones`, `/participaciones` endpoints / Basic consent/participation.
- 2026-10-28 / `docs/*` / Complete documentation / Audit, delivery, closure, authorization, registration.
- 2026-10-28 / `tests/test_flujo_individual.py` / End-to-end flow / Full individual verification.
- 2026-10-28 / `docs/hoja_de_ruta.md` / Roadmap / Progress and pending tracking.