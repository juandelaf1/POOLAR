# Vision and Purpose — POOLAR

> Updated: 2026-11-10. Status: **prototype / development (Phase 0), not production**. No verified impact claims without evidence.

## What is POOLAR

POOLAR is an **open, modular, interoperable infrastructure** that enables people, communities, associations, small businesses, cooperatives, and institutions to:

1. **Identify shared problems** — even when those affected do not know each other.
2. **Gather needs and capabilities** — aggregate demands, discover available resources, and understand the real scale of a problem.
3. **Coordinate collective solutions** — compare alternatives, make traceable decisions, assign responsibilities, and execute coordinated actions.
4. **Measure and learn** — record observed outcomes, distinguish estimates from real data, and export reusable learning.

It is not a single monolithic application but an **ecosystem**:

- **POOLAR Core** — reusable common nucleus (organizations, needs, collective problems, resources, initiatives, decisions, audit, provenance, export, HITL governance).
- **POOLAR Initiatives / applications** — user-facing applications for end-to-end collective processes.
- **Specialized modules/providers** — domain capabilities (e.g. logistics, climate, evaluation) integrated via versioned contracts/adapters without transferring execution authority to POOLAR.

## Problem addressed

Individual needs often lack sufficient demand, negotiation power, or resources for a viable solution (e.g. shared logistics, community services, shared equipment, underused resources). The challenge is moving from **fragmented needs** to a **shared understanding** and then to **coordinated, measurable action**.

## Design principles

1. **Utility before novelty** — technology is justified by the problem it solves.
2. **Open and reusable** — open licenses, sufficient documentation to understand, deploy, and improve.
3. **People over metrics** — affected people must understand and participate in relevant decisions.
4. **Data with context** — results explain source, date, coverage, assumptions, quality, and limits.
5. **Privacy by design** — collect the minimum necessary; no personal data exposed by default.
6. **Transparency and accountability** — prioritization criteria, conflicts of interest, spending decisions, and results documented.
7. **Autonomy and federation** — communities keep identity and choose what to share.
8. **Fair value distribution** — contributions, costs, risks, and benefits visible and governed by prior rules.
9. **Accessibility and inclusion** — support diverse digital literacy, languages, devices, disabilities, connectivity.
10. **Interoperability and exit** — open formats, export, documentation that reduce lock-in.
11. **Experimental prudence** — test at small scale; define criteria to continue, correct, or stop.
12. **Learn in public** — document relevant mistakes and learnings without blame.
13. **Human sustainability** — maintenance, moderation, and care are recognized work.
14. **Partisan neutrality, not ethical neutrality** — defend rights, safety, dignity, non-discrimination, transparency.
15. **No unmeasured impact claims** — distinguish estimates vs. achieved results, intent vs. outcome, pilot vs. proven at scale.

## Long-term vision

An ecosystem where people and organizations can collaborate through open, reusable tools, retain control over data and decisions, organize activities more transparently and efficiently, and measure impact by real-world improvement.

**North star:** *Does this initiative increase people's ability to solve a real problem through means they can understand, govern, and maintain?*

## What POOLAR is not

- A promise that technology/AI/data alone solve political or social problems.
- A single global cooperative controlling all initiatives or data.
- A substitute for professional, legal, tax, or financial advice.
- A platform to collect personal data without limits or trade it.
- A system where all activity must be unpaid.
- A perfect democracy solved by votes or algorithms alone.

## Current state (evidence-based)

- **Phase 0 (governance/HITL):** core controls implemented (fail-closed, scoping, approvals, resumable handlers, idempotency/concurrency handling, audit). Formal closure gated by external CI/PG/E2E/fault-injection evidence.
- **Local test evidence (2026-11-10, non-PG):** 171 passed, 7 skipped, 1 xfailed.
- **Data:** `synthetic_pilot` by default; real data requires consent, privacy, and operational controls.
- **Integrations:** modular contracts/adapters in dev stage; external modules/providers propose only (POOLAR retains HITL/execution authority). Ecosystem inter-repo contracts live in `POOLAR_ECOSYSTEM_GOVERNANCE/18_contracts/`.
- **Analytics:** separated read-only medallion/lakehouse foundation (exports → raw/staging/marts, DuckDB/dbt stubs). No HITL or domain side effects.
- **Repository:** this repo (`fase0-gobernanza`); independent, governed by `GOBERNANZA_POOLAR.md`, `BOUNDARIES.md`, `INTENT.md`. See [README](../README.md) and [index](index.md).