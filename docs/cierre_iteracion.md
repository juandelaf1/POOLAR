# Cierre de Iteración — Poolar MVP v0.6
Fecha: 28 octubre 2026
Estado: Entregado; no producción.
Repo independiente: poolar_mvp/ (sin modificar repos auditados).

## Código completado
- Registro individual (`POST /personas/registro`) funcional.
- Auth dual (`tipo` en JWT) funcional.
- Problema colectivo completo con integridad N:M.
- Iniciativa con responsabilidad individual (`responsable_tipo=persona`).
- Invitación/participación mínima insertada.
- Endpoints de problema aceptan `tipo=individuo` (org_id derivado de necesidad o persona).

## Pruebas
- Base: 30 passed, 1 skipped (PostgreSQL pendiente de servicio).
- Flujo individual (`tests/test_flujo_individual.py`): registro, auth, problema, iniciativa, descubrimiento, invitación pasados.
- Datos sintéticos (`synthetic_pilot`) obligatorios en todas las pruebas.

## Documentación
- `docs/auditoria_etapas.md`: etapas 1-10 documentadas.
- `docs/entrega_iteracion.md`: entregado con estado real.
- `docs/modelo_autorizacion.md`: matriz completa.
- `docs/registro_individual.md`: restricciones de registro individual.

## Bloqueos / pendientes
- PostgreSQL: código y migración listos; ejecución pendiente (`POOLAR_TEST_POSTGRES_URL` no disponible en este entorno).
- Integración con `Anexo_Risk`/`EnRuta`/`CASE`: bloqueada hasta `P0`/`P1` corregidos (no se intentó por diseño independiente).
- Datos reales: bloqueados hasta proceso de consentimiento documentado.

## Reproducibilidad del flujo individual (verificado)
1. `POST /personas/registro` → 201
2. `POST /auth/token` → 200 con `tipo=individuo`
3. `POST /necesidades` (persona_id) → creado
4. `POST /problemas-colectivos` (origen sintético) → 201
5. `POST /iniciativas` (responsable persona) → 201
6. `GET /problemas-colectivos` → descubre problema
7. `POST /invitaciones` / `participaciones` → documentado

No se declaró producción; no se expuso PII en DTOs ni eventos.
