# POOLAR — Strategic Benchmark, Common-Good Architecture, Accessibility, Security, and Sustainability

> Updated: 2026-11-10 (English translation/progressive alignment). Original analysis date/reference: **2026-11-09**.  
> **Status:** strategy/architecture analysis recorded in repo (not implementation). Claims are labeled by evidence type where applicable.

## POOLAR status snapshot (reference, 2026-11-09)

| Item | Observed state |
|---|---|
| Local repo | `C:\Users\JUAN\Desktop\Proyectos\Trama_Abierta\poolar` |
| Branch / HEAD (at analysis time) | `fase0-gobernanza` / `9ddc834...` |
| CI defined | `ci.yml` (PG16, migrations, backend excluding e2e, Playwright e2e) and `fase0-check.yml` (SQLite; `fase0-pg-real` `if:false`) — **remote green run not verified** |
| Historical evidence (not rerun) | HITL/governance core advanced; canonical Phase 0+capability suite 104 passed (historical); Phase 0 not formally closed |

## 1. Executive summary

There is a potential, but **not empirically validated**, space for an open cooperation infrastructure connecting *need → capabilities/resources → initiative → HITL decision → commitment → execution → learning* with strong human governance, portability, and design for low-resource communities. The plausible gap is not “more objects”, but combining: interoperable common core + verifiable human governance/authorization + privacy/consent + real portability + essential free use for communities without budget + progressive operation in low-connectivity contexts + connectable specialized modules without dual authority.

## 2. Competitive map (summary)

| Type | Project | Relation | Evidence (2026-11-09) |
|---|---|---|---|
| Direct conceptual competitor | **Armillaria / Innovation Exchange** | People/Projects/Organisations/Opportunities/Issues/Needs/Offers; matching, provenance/fork, permissions/review/scoring/reporting/export declared; pricing published; **open source/self-host not verified** | armillaria.io — declared/verified on web |
| Organizational reference | **Commonhood** | Insufficient public evidence to verify comparable software platform | commonhood.org — not verified |
| Governance/participation | **Decidim** | Participatory processes; AGPL; self-hostable | decidim.org, GitHub — verified |
| Deliberative decision | **Loomio** | Discussions/decisions; AGPL; SaaS + self-host | loomio.com, GitHub — verified |
| Standard/ontology | **ValueFlows** | Vocabulary for agents/resources/commitments/events/flows | valueflo.ws — verified |
| Framework | **hREA** | Holochain implementation aligned with ValueFlows/REA | GitHub — partial |
| Food vertical | **Open Food Network** | Short supply-chain marketplace; AGPL; local instances | openfoodnetwork.org — verified |
| Logistics vertical | **CoopCycle** | Cooperative logistics; Coopyleft license (conditional use) | coopcycle.org — verified with restriction |
| Finance/fiscal hosting | **Open Collective** | Collaborative finance/transparency; OFiCo ecosystem | opencollective.com — partial |
| Field/offline data | **KoboToolbox** | Data/field collection; AGPL components | kobotoolbox.org — partial/verified |
| Crisis/crowdsourcing | **Ushahidi** | Reports/maps/API; AGPL | ushahidi.com — verified |
| Purchasing verticals | **Karakolas, WeGrocery** | Quick search, insufficient verifiable evidence | not verified |

## 3. Key lessons

- **Armillaria:** useful domain/matching/provenance/configuration model; differentiate through openness, verifiable HITL, data sovereignty, and low-resource design.
- **Decidim/Loomio:** integrate mature deliberation/decision tools rather than rebuild.
- **ValueFlows:** semantic reference for resources/commitments/events.
- **OFN/CoopCycle/Open Collective:** integrate verticals/finance where applicable.
- **Kobo/Ushahidi:** field capture/partial-offline patterns and Do No Harm risks.

## 4. CORE / MODULE / CONNECTOR / SEPARATE matrix (summary)

| Capability | Decision |
|---|---|
| Identity, orgs, memberships, roles/permissions, HITL/policies | **CORE** |
| Needs, offers, capabilities, resources, problems, opportunities, initiatives, proposals/decisions/approvals | **CORE** |
| Commitments/execution (model) | **CORE** + specific operations in **MODULE** |
| Audit, provenance, consent, export, base learning | **CORE** (+ separated analytics) |
| Explainable matching/scoring | **MODULE** initially (internal/service); possible connectors |
| Procurement, logistics, resource bank, mutual aid, emergencies (operations) | **MODULE** or **CONNECTOR** by vertical |
| Finance/fiscal hosting, complex civic deliberation, mature logistics/marketplaces | **CONNECTOR / SEPARATE** |

## 5. Security, accessibility, and offline (design requirements)

- **Security:** progressive identity proportional to risk (no universally exclusionary KYC), RBAC/ABAC, org/tenant isolation, rate limiting, moderation/report/appeal, protection for vulnerable groups/minors, audit without over-collection, modules/adapters *proposal-only* with no sensitive execution authority.
- **Accessibility:** target WCAG 2.2 AA, mobile, keyboard/screen reader, plain language, i18n, assisted participation.
- **Progressive offline:** drafts/local idempotent queue for low-risk actions; explicit sync/conflict resolution; **never** offline for approvals/binding decisions, permission changes, or sensitive actions.
- **Do No Harm / DPG:** design references; do not claim certification without evaluation.

## 6. Sustainability (common-good mission)

Recommended: **hybrid** model (grants/public/philanthropic funds + institutional payments for hosting/support/implementation + community nodes). Essentials free (code, use, base APIs, export). **Not allowed as primary model:** data sales, behavioral advertising, pay-per-seat for essentials, lock-in.

## 7. Strategic decisions (summary)

1. Close Phase 0 and harden authz/PG/CI/GDPR controls. 2. Clear open-source license + export/self-host. 3. Canonical Core domain (alignable with ValueFlows/Armillaria). 4. One scoped pilot with a real community. 5. Sustainability/anti-capture governance + progressive identity.

## 8. Evidence limitations

Mix of **VERIFIED** (public repos/licenses consulted, local POOLAR state), **DECLARED** (product/pricing/case claims), **HISTORICAL** (prior POOLAR tests not rerun), and **HYPOTHESIS/UNKNOWN** (niche, costs, unconfirmed licenses, Karakolas/WeGrocery). Armillaria open source/self-host **not verified**.
