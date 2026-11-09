# Registro: tareas pendientes antes/durante el frontend

> Creado 2026-11-09 al iniciar scaffold `poolar/web/` (React+Vite+TS). El frontend es fino; **POOLAR API conserva autoridad**.

## Pendientes (gobernanza/Fase 0 — no bloquean scaffold, sí producción formal)
- [ ] **F0-13 cierre formal:** PR/merge `fase0-gobernanza`→`dev/main`, CI verde, job PG con secrets gestionados, evidencia E2E/fault-injection restante.
- [ ] Revalidación PG real (0004/0005) en entorno CI/objetivo cuando haya secrets.

## Pendientes (API/contrato para front — deseables)
- [ ] **Auth UX:** flujo login/token documentado para UI (CORS, refresh si aplica, manejo 401/403 fail-closed).
- [ ] **DTOs estables:** respuestas consistentes para `pending_review` en todas las acciones gobernadas; tipado compartido (OpenAPI/TS client).
- [ ] **Errores normalizados:** mensajes/`detail` sin filtrar info cross-tenant; códigos para UI.
- [ ] **Paginación/filtros** en listados (necesidades, problemas, iniciativas, approvals).
- [ ] **RBAC en UI** (solo presentación) alineado a roles/políticas reales del backend.

## Pendientes (frontend MVP)
- [ ] `npm install` y verificar build; elegir kit UI (MUI/Chakra/shadcn+Tailwind).
- [ ] Login + almacenamiento seguro de token (definir estrategia).
- [ ] Pantallas: necesidades, problemas, iniciativas, decisiones, **approvals** (pending/approve/reject/retirar según permisos), módulos/capacidades.
- [ ] Manejo global de `pending_review` y estados HITL; toasts/errores.
- [ ] Tests front (Vitest/RTL) para flujos críticos (opcional MVP+).

## Pendientes (modular/otros — paralelos, no front)
- [ ] C1: primer módulo no-CASE real por `ModuleManifest`+adaptador (mock/sintético primero).
- [ ] Ops/monitoreo liviano separado; analytics BI sobre marts cuando estables.

## Decisión registrada
- Front: **React + Vite + TypeScript** en `poolar/web/` (SPA), proxy `/api`→FastAPI, backend conserva autoridad.
