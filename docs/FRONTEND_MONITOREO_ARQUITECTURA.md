# POOLAR — Frontend and Monitoring (proposal/diagram)

> Updated: 2026-11-10. Draft for decision. Respects governance: **POOLAR retains authority** (tenant, HITL, permissions, audit). Analytics/monitoring **must not** couple to or execute HITL effects.

## 1) Separate surfaces (do not mix)

| Surface | Users | Goal | Source of truth |
|---|---|---|---|
| **Product frontend** | orgs/individuals/managers | `need→problem→initiative→decision`, invitations, resources, governed actions | POOLAR API (governed) |
| **HITL/Governance console** | approvers/admins | view/manage approvals, audit, states, withdrawals (per policy) | `/approvals/*` API + audit events |
| **Ops monitoring** | technical team | API health, latency, errors, jobs/queues, DB performance, alerts | metrics/logs/infra (outside HITL business logic) |
| **Analytics/BI** | decision/tracking | KPIs, HITL funnels, problems/initiatives/CO2e (estimated vs measured) | medallion exports `raw→staging→marts` (DuckDB/dbt), **read-only** |

## 2) Tool fit (recommended)

| Tool | Fit | Notes |
|---|---|---|
| **MLflow** | **Not now** (unless real ML) | For ML experiment/model tracking only (e.g. model scoring). Not for app/DB monitoring or product UI. |
| **SQL Server Perf Monitoring** | **No** | POOLAR targets PostgreSQL (SQLite in tests). |
| **ParadeDB / pg_analytics / Hydra** | **Optional, later** | Consider only if in-PG analytics pressure is demonstrated. Current base is separated DuckDB + medallion exports. |
| **DuckDB + dbt + exports** (current) | **Yes (base)** | Read-only, reproducible analytics without coupling HITL/OLTP. |
| **Lightweight ops dashboard** | **Yes** | `/health` + metrics (Prometheus/OpenTelemetry) + structured logs + PG stats (e.g. `pg_stat_statements`) / simple dashboard. |

**Practical recommendation:** 1 product frontend + 1 HITL view (can be RBAC module in same app), 1 lightweight ops stack, analytics via medallion/DuckDB→BI when marts are stable. Avoid tool sprawl.

## 3) Diagrama (objetivo)
```mermaid
flowchart LR
  subgraph Users[Usuarios]
    U1[Org/Individuo]
    U2[Aprobador/Admin]
    U3[Ops/Analista]
  end

  subgraph Front[Frontends]
    PUI[Frontend Producto\n(necesidades→decisiones)]
    HITLUI[Consola HITL/Gobernanza\n(rol/permisos)]
    OPSUI[Dashboard Ops/Monitoreo]
    BIUI[BI/Analytics\n(marts)]
  end

  subgraph Core[POOLAR Core - autoridad]
    API[API gobernada\nFastAPI]
    GOV[HITL/Approvals\nScope/AuthZ/Atomicidad]
    MOD[Composición módulos\nproposals/results\n(sintético/mock hoy)]
    AUD[(Eventos auditoría)]
    OLTP[(PostgreSQL OLTP)]
  end

  subgraph Analytics[Analytics separada - read-only]
    EXP[Export idempotente\nredactado]
    RAW[(raw JSONL/obj)]
    STG[(staging)]
    MART[(marts DuckDB/dbt)]
  end

  subgraph Ext[Módulos externos - futuros, aislados]
    CASE[CASE]
    LOG[Logística]
    CO2[CO2e]
    OTH[Otros proyectos]
  end

  U1 --> PUI --> API
  U2 --> HITLUI --> API
  API --> GOV --> OLTP
  API --> AUD --> OLTP
  API --> MOD --> CASE & LOG & CO2 & OTH
  MOD -.solo propuestas/resultados.-> GOV
  AUD --> EXP --> RAW --> STG --> MART --> BIUI
  U3 --> OPSUI
  OPSUI -.métricas/logs/pg stats.-> API
  OPSUI -.métricas.-> OLTP
```

## 4) Fases sugeridas
1. **Diagramar + contratos UI** (ahora): mapear pantallas/endpoints/roles (aprovecha 104 tests y `/modules/capabilities`), estados HITL, errores fail-closed.
2. **MVP Front producto+HITL**: app web (p.ej. React/Vite o Next, según preferencia) consumiendo API existente; auth; vistas: necesidades, problemas, iniciativas, decisiones, approvals pendientes/historial; manejo `pending_review`.
3. **Ops liviano**: health + métricas estructuradas + dashboard simple (sin acoplar a negocio).
4. **Analytics UI**: sobre marts DuckDB/dbt (read-only), cuando Fase 0 cerrada y marts definidos.
5. **MLflow/pg_analytics/etc.**: solo ante requisito concreto (modelos ML versionados o presión analítica en PG demostrada).

## 5) Decisiones abiertas (para elegir)
- Stack frontend (React+Vite SPA, Next.js, u otro) y dónde vive (mismo monorepo/carpeta `web/` o repo separado).
- Consola HITL: separada o módulo con RBAC en el mismo front.
- Ops: Prometheus+Grafana, o más liviano (logs + pg_stat_statements + panel mínimo).
- Multitenancy/branding en UI.
