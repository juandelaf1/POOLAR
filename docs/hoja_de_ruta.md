# Hoja de Ruta — Trama Abierta MVP v0.6
Fecha: 28 octubre 2026
Estado: Entregado; no producción.

## Completado (esta iteración)
- [x] Diseño independiente (no copia de repos auditados)
- [x] Modelo `ProblemaColectivo` + `Persona` + relaciones N:M
- [x] Contratos versionados (`contracts.py`)
- [x] Auth PBKDF2-SHA256 + JWT con `tipo`
- [x] Registro individual (`POST /personas/registro`)
- [x] Endpoints problema colectivo (crear, consultar, estado)
- [x] Iniciativa con responsable individual
- [x] Autorización dual (org / persona) implementada
- [x] Invitación / participación mínima
- [x] Datos sintéticos obligatorios (`synthetic_pilot`)
- [x] Pruebas: 30 passed + flujo individual
- [x] Documentación: auditoría, entrega, cierre, autorización, decisiones técnicas, registro, visión
- [x] README actualizado

## Pendiente (documentado, no bloqueante para este MVP)
- [ ] PostgreSQL real (`TRAMA_TEST_POSTGRES_URL`)
- [ ] Integración con repos auditados (`P0`/`P1` corregidos)
- [ ] Proceso de consentimiento para datos reales
- [ ] Canal físico de invitación / consentimiento verificado
- [ ] Accesibilidad WCAG / adaptaciones
- [ ] Trazabilidad ética formal (cada decisión justificada con criterio ético)
- [ ] Perfil technic global automático (más allá de fixtures `org_a`/`org_b`)
- [ ] Exportación completa verificada con datos sintéticos

## Próxima iteración sugerida
1. Confirmar PostgreSQL y ejecutar `test_migracion_postgresql`.
2. Completar trazabilidad ética + accesibilidad.
3. Cerrar integración solo tras `P0`/`P1` corregidos.
