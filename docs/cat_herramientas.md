# Catálogo de Herramientas Operativas — Poolar v0.6
Estado: MVP independiente; no producción; datos sintéticos (`synthetic_pilot`).

## 1. Descubrimiento de posibilidades (`matching`)
- `find_related_needs` (determinista: categoría, ámbito, restricciones, escala, recursos necesarios)
- `explain_match` (criterios compartidos, diferencias, faltantes)
- `propose_relationship` / `accept` / `reject`
- Persistencia de propuesta y decisión.

## 2. Capacidad colectiva (`aggregation`, `resources`)
- `calculate_shared_demand` (unidades, supuestos explícitos)
- `identify_gaps` (faltantes: recursos, conocimientos, capacidades)
- `search_capabilities` / `offer_capability`
- `search_resources` / `reserve` / `release` / `record_use`

## 3. Motor de soluciones (`feasibility`, `initiatives`)
- `compare_alternatives` (criterios documentados, supuestos explícitos)
- `define_alternative` / `estimate_requirements`
- `initiatives.create_from_problem` / `get` / `update`
- `commitments.create` / `accept` / `update_status`
- `activities.record`

## 4. Ejecución y medición (`execution`, `outcomes`, `audit`)
- `record_event` / `record_milestone`
- `define_metric` / `record_observation`
- `compare_with_baseline`
- `generate_summary`
- `audit.get_history`

## 5. Autonomía, consentimiento y trazabilidad (`audit`, `provenance`, `exports`)
- `provenance.register` / `get`
- `exports.generate_json` / `generate_csv`
- `data.validate_import`
- `contracts.get_schema`
- `needs.create/get/search/update` con visibilidad (`privada`/`compartible`/`publica`)
- Registro de invitaciones y participación con consentimiento efectivo (`invitation_service`).

Requisitos generales:
- Cada herramienta: entrada tipada, salida tipada, permisos, errores definidos, eventos de auditoría, idempotencia verificada cuando corresponda.
- Contratos versionados (`src/core/contracts.py`).
- Datos sintéticos obligatorios (`synthetic_pilot`).
- Datos personales no expuestos en DTOs públicos.
- No producción; integración con repos auditados (`Anexo_Risk`, `EnRuta`, `CASE`) bloqueada hasta `P0`/`P1` corregidos.
