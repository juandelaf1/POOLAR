# Pending Risks — POOLAR

> Updated: 2026-11-10 (`fase0-gobernanza`). Status: **development/prototype, not production**. Risks are classified for prioritization; listing does not imply remediation unless explicitly evidenced.

## Critical / open

| Riesgo | Impacto | Estado | Mitigación / siguiente paso |
|---|---|---|---|
| **Cierre Fase 0 sin gates externos** | Falsa confianza en “cerrado” | Abierto | CI verde en HEAD, job PG con `POOLAR_TEST_POSTGRES_URL`+secrets, revalidación concurrencia/migraciones, E2E/fault-injection según criterio. |
| **Secretos/credenciales en entornos locales** | Exposición si se filtran | Parcial | `.env` gitignored; nunca commitear secretos. **Rotar** credenciales si fueron expuestas fuera de la máquina/entorno autorizado. Gestión/rotación formal pendiente. |
| **RGPD/PII y datos reales** | Cumplimiento/legal | Abierto | Mantener `synthetic_pilot`; consentimiento, minimización, retención, acceso por scope y procedencia antes de pilotos reales. |
| **Licencias/IP de repos/ecosistema** | Reutilización indebida | Abierto | No reutilizar/integrar código de repos sin derechos verificados (ver gobernanza/ecosistema). Mantener adaptadores/contratos propios. |

## Altos / medios

| Riesgo | Estado | Nota |
|---|---|---|
| Cobertura authz/HITL no exhaustiva en todos los endpoints/acciones | Parcial | Núcleo fuerte y probado; completar matriz y E2E por acción/rol/ámbito. |
| Diferencias SQLite vs PostgreSQL (concurrencia/locking) | Parcial | Guards y pruebas PG existen; ejecutar en PG real/CI para evidencia válida. |
| Integración con módulos/proveedores externos | Controlado (dev) | Solo contratos/adaptadores/mocks; sin autoridad de ejecución; degradación y procedencia explícitas. |
| Accesibilidad, observabilidad y UX operativa incompletas | Parcial | Mejoras incrementales; no bloquea invariantes HITL. |
| Documentación desalineada por iteraciones | Mitigándose | Índice/MkDocs, archivo legacy y pases de actualización en curso. |

## Históricos (contexto)

- Hallazgos previos P0/P1 en repos externos (p.ej. `Anexo_Risk`, `EnRuta`) tratados como referencias de auditoría; no integrados sin corrección/derechos/autorización.
- No declarar producción ni impacto verificado sin evidencia reproducible.
