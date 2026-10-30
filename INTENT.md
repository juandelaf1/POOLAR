# INTENT.md — Poolar

## Propósito

Poolar es una plataforma modular y transaccional para conectar necesidades, optimizar capacidades y ejecutar soluciones colectivas de forma ágil.

No es una red social, ni un gestor de tareas, ni un portal de anuncios. Es infraestructura para organizar cooperación y hacerla comprensible, trazable y reutilizable.

## Objetivos de negocio

1. Permitir que personas y organizaciones registren necesidades, conocimientos y capacidades.
2. Descubrir problemas colectivos mediante coincidencias explicable.
3. Conectar recursos complementarios y calcular demanda compartida.
4. Comparar alternativas con criterios y supuestos explícitos.
5. Organizar iniciativas con decisiones documentadas y responsabilidades claras.
6. Coordinar ejecución y medir resultados verificables.
7. Conservar autonomía sobre datos y reducir dependencia de intermediarios.

## Flujo operativo principal

Necesidad → Descubrimiento → Problema Colectivo → Capacidades y recursos → Alternativas → Decisión → Ejecución → Resultados → Aprendizaje reutilizable.

## Reglas de dominio (intención)

- La unidad fundamental es el problema compartido y la capacidad colectiva.
- Personas y organizaciones son participantes de primera clase.
- Los datos sintéticos (`synthetic_pilot`) son obligatorios hasta que exista un proceso de consentimiento formal.
- Los agentes de IA asisten, no deciden.
- La autorización se verifica en cada operación del dominio.
- Las decisiones colectivas requieren aprobación humana.

## Contratos de API

- Todos los endpoints consumen y producen JSON tipado.
- La autenticación es JWT con secreto de entorno obligatorio.
- Las contraseñas se envían en cuerpo JSON, nunca en URL.
- Los datos personales nunca se exponen en DTOs públicos.

## Restricciones de diseño

- Monolito modular (FastAPI + SQLAlchemy + PostgreSQL).
- No microservicios ni infraestructura distribuida.
- PostgreSQL es la base objetivo; SQLite solo para desarrollo controlado.
- Migraciones reproducibles con Alembic.
- CI con PostgreSQL real y Playwright E2E.