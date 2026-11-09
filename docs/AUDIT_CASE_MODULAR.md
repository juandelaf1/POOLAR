# Auditoría inicial CASE (read-only) — integración modular con POOLAR

> **Fecha:** 2026-11-09. **Alcance:** inspección estática/read-only de `C:\Users\JUAN\Desktop\Proyectos\CASE` (no se modificó CASE; no se ejecutaron sus tests; no se expusieron secretos). **Objetivo:** decidir si CASE debe escalarse y/o exponerse como **módulo CASE-POOLAR** bajo la arquitectura modular gobernada.

## 1) Evidencia observada (CASE)
- **Identidad/madurez declarada:** `README.md` describe CASE v1.0.0 como “AI decision orchestration” (dominio/proveedor agnóstico), hexagonal, FastAPI + Streamlit, HITL/automatización por riesgo, auditoría. Declara 813 tests/93 archivos fuente (no verificado por ejecución en esta auditoría).
- **Stack:** Python >=3.11, FastAPI, Pydantic v2, httpx, python-dotenv; Alembic no visible en deps raíz pero sí persistencia SQLite (`case_audit.db` presente en repo local — **no inspeccionado**). `pyproject.toml` con ruff/mypy strict.
- **Estructura:** `src/case_core/{application,contracts,domain,evaluation,governance,hybrid,ml,ports,production,prompts,providers,react,reliability}`, `src/case_api`, `src/case_infra`, adaptadores `logistics_adapter`, `usgs_adapter`, `streamlit_app`, `tests/`, `docs/`.
- **Contratos/decisión (muestreados):** `contracts/automation.py` define `AutomationDecision` (`AUTO_APPROVE|HUMAN_REVIEW|ESCALATE`), `RiskAssessment`, HITL requerido; `contracts/lifecycle.py` define `ProcessingLifecycle` y `DecisionLifecycle` (`AI_PROPOSED/UNDER_REVIEW/APPROVED/REJECTED/ESCALATED/MODIFIED/OVERRIDDEN/ARCHIVED`). Conceptualmente alineado con HITL, pero **modelo de autoridad propio**.
- **Composición/autoridad:** `composition.py` construye `TriageEngine` con registry de dominios, providers (groq/ollama/mock/cloud) con circuit breaker, `SQLiteAuditAdapter`, `SQLiteDecisionRepository`, `automation_policy_fn`, `CostModel`. CASE **persiste decisiones/auditoría propias** y resuelve rutas de automatización internamente.

## 2) Encaje con POOLAR (arquitectura modular)
POOLAR ya definió (y tiene base implementada): contratos genéricos de módulo, `ModuleManifest`/registro, adaptadores mock (CASE mock + no-CASE), HTTP-safe, composer — todos **proposal/result only**, con **POOLAR como autoridad** (tenant, authz, HITL, ejecución, auditoría correlacionada). `docs/` y `BACKLOG_PRIORIZADO_POOLAR.md` establecen que módulos son **autoejecutables aislados + componibles** y que no se integra externo real antes de Fase 0/cierre+puertas.

## 3) Hallazgos (fit / riesgos)
| Área | Hallazgo | Implicación |
|---|---|---|
| Madurez/arquitectura | Hexagonal, contratos, HITL, multi-dominio, providers. | Buen candidato a **módulo por capacidades** (no reescribir desde cero). |
| Autoridad dual | CASE tiene HITL/automatización/auditoría/DB propios. | **No** embeber CASE como ejecutor/decisor dentro de POOLAR. Riesgo de doble autoridad/HITL/auditoría inconsistente. |
| Superficie de integración | Hay core/engine/API/policies; falta confirmar contrato estable “capability API” orientado a POOLAR (visto parcial). | Requiere **capa adaptadora** (anti-corruption/translation) y/o endpoints/capacidades explícitas. |
| Estado operativo | Presencia de `.env`, `case_audit.db`, logs en repo local. | Tratar como **externo/sensible**; no copiar datos/secretos; integrar solo con datos sintéticos/autorizados y configuración aislada. |
| Escalado | No evaluado rendimiento/carga/multi-tenant/SLO (fuera de alcance estático). | “Escalar CASE” es decisión separada; **no** prerrequisito para módulo proposal-only si se expone capacidad acotada. |
| Licencia/gobernanza | README badge MIT visible (verificar `LICENSE`/dependencias). | Verificar compatibilidad/licencia antes de redistribución/servicio conjunto. |

## 4) Recomendación
**No escalar/integrar CASE “en grande” ahora.** Crear un **módulo CASE-POOLAR (adapter boundary)**, *después* de Fase 0 formal y con datos sintéticos:

1. **Auditoría profunda (siguiente, verificable):** ejecutar/verificar tests de CASE en su entorno aislado, revisar `LICENSE` real, mapear capacidades exportables (p.ej. `case.triage.assess`, `case.risk.evaluate`, por dominio), confirmar API/SDK estable, revisar manejo PII/secrets.
2. **Diseño módulo (sin acoplar autoridad):** `ModuleManifest` para CASE; adaptador que invoca CASE **solo para obtener** `DecisionProposal`/`CapabilityResult`/evidencia (o `AUTO_APPROVE/HUMAN_REVIEW/ESCALATE` mapeado a propuesta); **POOLAR** valida tenant/actor, aplica HITL propio y ejecuta efectos. CASE no escribe en BD de POOLAR ni aprueba final.
3. **Integración por etapas:** mock (ya existe base) → adaptador HTTP/lib a CASE en entorno aislado con **synthetic** → pruebas contrato/timeout/fallo → piloto gobernado. Correlacionar `trace_id`/auditoría.
4. **Escalar/refactor CASE solo si el audit lo exige:** p.ej. extraer API de capacidades limpia, multi-tenant/aislamiento, idempotencia, observabilidad, o separar “motor de propuesta” de “persistencia/autoridad HITL propia” cuando se componga con POOLAR.

## 5) Criterios de decisión (go/no-go)
- **Go módulo (wrapper):** CASE expone capacidad estable; se puede forzar modo “propuesta”; timeouts/fallos controlables; licencia OK; datos sintéticos.
- **Refactor antes:** CASE no puede operar sin autoridad HITL/persistencia propia acoplada; sin API estable; sin aislamiento de datos; o rendimiento/integridad insuficiente para el caso de uso.
- **Escalar infraestructura CASE:** solo con evidencia de carga/SLO y tras definir boundary de módulo.

## 6) Próxima acción concreta
- [ ] Ejecutar checklist de auditoría profunda en `CASE` (aislado) y completar matriz de capacidades → `ModuleManifest`.
- [ ] Implementar `adapters/case_module.py` en POOLAR (extiende mock actual) con mapping `RiskAssessment/AutomationDecision` → `DecisionProposal` (siempre `requires_human_review` según política POOLAR) y config `synthetic_only` por defecto.
- [ ] Registrar manifest CASE demo cuando `POOLAR_LOAD_DEMO_MODULES=1` (ya hay patrón). **No** habilitar llamadas reales.
