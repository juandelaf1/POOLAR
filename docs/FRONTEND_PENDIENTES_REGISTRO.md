# Frontend Pending Tasks Log

> Created: 2026-11-09 (when `poolar/web/` scaffold started, React+Vite+TS). Updated: 2026-11-10. Frontend is thin; **POOLAR API retains authority**.

## Governance / Phase 0 (not blocking scaffold; relevant for formal closure)
- [ ] **F0-13 formal closure:** PR/merge `fase0-gobernanza`→`dev/main`, CI green, PG job with managed secrets, remaining E2E/fault-injection evidence.
- [ ] Revalidate real PG (0004/0005) in CI/target env when secrets available.

## API/contract for frontend (desirable)
- [x] Configurable dev/prod CORS (`POOLAR_CORS_ORIGINS`), Vite `/api` proxy.
- [x] Basic auth UX: login/token + `localStorage` storage (MVP; review secure refresh/storage for prod).
- [x] Initial TS types aligned to observed contracts (`web/src/api/types.ts`); OpenAPI→TS generation pending.
- [ ] Stable DTOs/OpenAPI export + client/type generation; normalize `pending_review`/error shapes.
- [ ] Normalized errors (`detail`/codes) without cross-tenant leakage.
- [ ] Pagination/filters for listings (needs, problems, initiatives, approvals).
- [ ] RBAC in UI (presentation only) aligned with backend roles/policies.

## Frontend MVP
- [ ] `npm install` and verify build; choose UI kit (MUI/Chakra/shadcn+Tailwind).
- [x] Login + HITL MVP wiring: `/auth/token`, `/approvals/pending`, approve/reject (reason). Missing proposer withdrawal UX, detail views, polling/refetch.
- [ ] Product screens: needs, problems, initiatives, decisions (end-to-end `pending_review` handling).
- [ ] Global handling of HITL states/errors/toasts/route guards.
- [ ] Secure token strategy (refresh/expiry/storage) for prod.
- [ ] Frontend tests (Vitest/RTL) for critical flows (optional MVP+).

## Parallel (not frontend)
- [ ] First non-CASE module via `ModuleManifest`+adapter (mock/synthetic first).
- [ ] Lightweight ops monitoring; analytics BI on stable marts.

## Recorded decision
- Frontend: **React + Vite + TypeScript** in `poolar/web/` (SPA), `/api` proxy to FastAPI, backend retains authority.
