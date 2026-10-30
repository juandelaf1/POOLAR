# ADR: LangSmith vs Langfuse para observabilidad de IA

## Estado
Aceptado (OpenTelemetry como base, Langfuse autogestionado como plataforma principal).

## Decisión
Utilizar OpenTelemetry como base de instrumentación y Langfuse autogestionado como plataforma principal de observabilidad de IA.

## Razones
- Langfuse autogestionado favorece la autonomía, la inspección y el control de los datos (alineado con la visión de Poolar).
- OpenTelemetry proporciona trazas y métricas estándar, intercambiables.
- LangSmith facilita el desarrollo y evaluación de flujos, pero depende de un proveedor externo.
- La privacidad y el control de datos son prioritarios para un proyecto de cooperación abierta.

## Consecuencias
- Traces y métricas se envían a Langfuse autogestionado (configurable por entorno).
- El envío a LangSmith se desactiva por defecto.
- Las trazas de desarrollo no contienen contraseñas, tokens ni datos personales innecesarios.
- Se define qué datos pueden salir del entorno, qué se redacta y cómo se desactiva la telemetría.

## Alternativas descartadas
- LangSmith: descartado como principal por dependencia de proveedor externo.
- Solo OpenTelemetry sin plataforma: insuficiente para evaluación de prompts y costes.