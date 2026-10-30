# ADR: Agent Harness — Diseño y decisiones

## Estado
Aceptado (harness propio mínimo, con interfaces para LangGraph).

## Decisión
Implementar un Agent Harness propio y ligero en `src/core/agent_harness/`, con interfaces intercambiables para incorporar LangGraph cuando sea necesario. No instalar LangGraph, CrewAI ni Deep Agents en esta iteración.

## Razones
- Poolar necesita control explícito sobre permisos, autorización y aprobaciones.
- Un framework genérico no sustituye el modelo de autorización propio.
- El harness propio permite separar contexto, herramientas, políticas, aprobaciones y estado.
- LangGraph se evaluará cuando aparezcan flujos duraderos que realmente lo necesiten.
- CrewAI es una alternativa a comparar, no un segundo orquestador simultáneo.
- Deep Agents se evaluará si aporta valor frente al harness propio.

## Componentes implementados
- `ExecutionContext`: contexto estructurado (actor, permisos, presupuesto, herramientas).
- `ToolRegistry`: registro de herramientas tipadas con contratos, permisos, límites.
- `PolicyEngine`: verificación de autorización en tiempo de ejecución.
- `ApprovalManager`: aprobaciones humanas para operaciones sensibles.
- `ExecutionStateManager`: gestión de estado temporal de ejecuciones.
- `Security limits`: iteraciones, tool calls, timeout, presupuesto, rate limiting.

## Alternativas descartadas
- LangChain: útil para integración con modelos, pero no necesario para el harness básico.
- LangGraph: se evaluará cuando haya flujos duraderos que lo requieran.
- Deep Agents: se evaluará si aporta valor frente al harness propio.
- CrewAI: alternativa a comparar, no segundo orquestador simultáneo.