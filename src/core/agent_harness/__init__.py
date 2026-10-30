"""Agent Harness para Poolar — capa de ejecución y control de agentes.

Diseñado para ser desacoplado del framework de IA. Proporciona:
- Contexto de ejecución estructurado
- Registro de herramientas tipadas
- Motor de políticas (autorización)
- Aprobaciones humanas
- Gestión de estado
- Límites de seguridad

Principios:
- El núcleo de Poolar es la autoridad del dominio.
- Los agentes proponen; el dominio valida; las personas autorizan.
- Sin LangGraph, CrewAI ni otros frameworks obligatorios.
- Sin LangSmith ni observabilidad externa por defecto.
- Sin microservicios ni infraestructura distribuida.
"""