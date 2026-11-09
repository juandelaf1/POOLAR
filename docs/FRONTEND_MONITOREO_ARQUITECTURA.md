# POOLAR — Frontend y Monitoreo (propuesta/diagrama)

> Borrador para decisión. Respeta gobernanza: **POOLAR conserva autoridad** (tenant, HITL, permisos, auditoría). Analytics/monitoreo **no** acoplan ni ejecutan efectos HITL.

## 1) Separar superficies (no mezclar)
| Superficie | Usuarios | Objetivo | Fuente de verdad |
|---|---|---|---|
| **Frontend producto** | organizaciones/individuos/gestores | flujo `necesidad→problema→iniciativa→decisión`, invitaciones, recursos, acciones gobernadas | API POOLAR (gobernada) |
| **Consola HITL/Gobernanza** | aprobadores/admins | ver/gestionar approvals, auditoría, estados, retiros (según política) | API `/approvals/*` + eventos auditoría |
| **Monitoreo ops** | equipo técnico | salud API, latencia, errores, colas/jobs, DB performance, alertas | métricas/logs/infra (fuera de lógica de negocio HITL) |
| **Analytics/BI** | decisión/seguimiento | KPIs, embudos HITL, problemas/iniciativas/CO2e (estimado vs medido) | exports/medallion `raw→staging→marts` (DuckDB/dbt), **read-only**, sin tocar transaccional |

## 2) Herramientas mencionadas — encaje recomendado
| Herramienta | ¿Encaja? | Uso recomendado / nota |
|---|---|---|
| **MLflow** | **No ahora** (salvo ML real) | Tracking de experimentos/modelos ML. Útil solo si hay modelos versionados (p.ej. scoring CASE) — **no** para monitoreo de app/DB ni UI de producto. |
| **SQL Server Perf Monitoring** | **No** | Específico de SQL Server; POOLAR usa **PostgreSQL** (y SQLite tests). Irrelevante. |
| **ParadeDB / pg_analytics / Hydra** | **Opcional, más adelante** | Extensiones/variantes analíticas sobre Postgres. Útiles si el volumen/consultas analíticas crecen *dentro* de PG. Hoy ya tenemos **DuckDB + exports medallion** (separado, simple, sin riesgo al OLTP). No adoptar antes de necesidad medida. |
| **DuckDB + dbt + exports** (actual) | **Sí (base)** | Analytics read-only post-Fase 0, reproducible, sin acoplar HITL. Mantener. |
| **Dashboard ops liviano** | **Sí** | `/health` + métricas (Prometheus/OpenTelemetry) + logs estructurados + consultas PG de performance (pg_stat_statements) o panel simple (Grafana/Metabase según stack). Separado del producto. |

**Recomendación práctica:** 1 frontend producto + 1 vista HITL (puede ser módulo del mismo front con permisos), 1 stack ops liviano, analytics vía medallion/DuckDB→BI cuando haya marts estables. Evitar tool sprawl.

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
