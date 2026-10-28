# Escenario demostrativo de logística compartida — Trama Abierta v0.6
Fecha: 28 octubre 2026
Estado: Sintético; datos identificables como tales (`synthetic_pilot`).

## Contexto
Varias personas y pequeños comercios tienen dificultades para acceder a un servicio logístico adecuado.
No hay tal ruta creada ni realizado ahorro real. Todo es ejemplos documentables con datos sintéticos.

## Participantes (IDs ficticios / sintéticos)
- P1 — Persona: necesita transporte regular (Sevilla).
- P2 — Persona: pequeño comercio; necesita entregas (Sevilla).
- C3 — Conocimiento/capacidad logística (disponibilidad début-marzo).
- O4 — Organización: puede aportar capacidad o negociar proveedores.

## Datos sintéticos obligatorios
Todos los registros se etiquetan como `origen_datos = synthetic_pilot`.
El flujo se ejecuta mediante las API de Trama Abierta (no salte el producto).

## Flujo operativo ejecutado
1. Registrar necesidades P1, P2, O4.
2. `matching.find_related_needs` → coincidencia P1↔P2 por "transporte/entregas/logística".
3. Revisar coincidencia; rechazar por unterschiedes escala/horario (documentado); luego aceptar.
4. Crear Problema Colectivo con necesidad P1+P2, origen `synthetic_pilot`.
5. `aggregation.calculate_shared_demand` → demanda compartida (unidades/mes), supuestos territoriales.
6. `resources.search` → hallar conocimiento C3 para logística.
7. Identificar gaps (capacidad que falta).
8. `feasibility.compare_alternatives` → comparar: compartir recursos vs agrupar demanda vs compartir ruta. Supuestos explícitos.
9. `initiatives.create_from_problem` → iniciativa para evaluar ruta compartida, responsable O4 (organización).
10. `commitments.create` + `activities.record`.
11. `execution.record_milestone` y `outcomes.define_metric`.
12. Consultar historial + exportar JSON/CSV.
13. Repetición desde estado limpio (reproducible).

## Requisito de reproducción local
```
TRAMA_ABIERTA_SECRET_KEY=demo-key TRAMA_DEMO_MODE=true python docs/demo/escenario_logistica.py
```
El modo demo canaliza acccesos a cuentas predefinidas sintéticas.

## Documentación pendiente (ver en docs/hoja_de_ruta.md)
- Discovery por coincidencias explícitas (noIA).
- Invitación persistente efectiva con consignación.
- Accesibilidad WCAG.
- Licencia formal.
- PostgreSQL real.
