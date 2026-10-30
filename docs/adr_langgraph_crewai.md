# ADR: LangGraph vs CrewAI

## Estado
Aceptado (LangGraph como primera opción, CrewAI como alternativa a evaluar).

## Decisión
Utilizar LangGraph como orquestador principal para flujos de agentes. Mantener CrewAI como alternativa a evaluar únicamente si un requisito concreto no se resuelve con LangGraph.

## Razones
- LangGraph proporciona estado persistente, recuperación después de fallos, ejecución de varios pasos y aprobaciones humanas (checkpoints).
- Poolar necesita estado, pasos deterministas, checkpoints y puntos explícitos de revisión humana.
- CrewAI es útil para equipos de agentes, pero no sustituye las herramientas operativas del dominio.
- La lógica de dominio, los contratos de herramientas y las pruebas deben ser independientes del framework.

## Consecuencias
- Los flujos de LangGraph se implementarán como módulos separados (no en el núcleo de dominio).
- El estado de LangGraph no es la autoridad definitiva sobre las entidades de Poolar Core.
- La autorización se verifica de nuevo en cada operación del dominio.
- Reevaluar CrewAI solo si un requisito específico no se resuelve con LangGraph.

## Alternativas descartadas
- CrewAI: descartado para la primera iteración por redundancia con LangGraph y mayor complejidad de agentes.
- Framework propio: descartado por complejidad y falta de soporte de persistencia.