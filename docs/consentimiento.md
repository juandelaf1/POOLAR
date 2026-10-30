# Consentimiento y Privacidad — Poolar

## Estado
Documentado; no implementado como flujo automatizado. Bloquea datos reales hasta definir proceso.

## Principios
1. Los datos sintéticos (`synthetic_pilot`) son obligatorios hasta que exista un proceso de consentimiento documentado.
2. Ningún dato personal real puede registrarse sin consentimiento explícito, registrado y revocable.
3. La minimización de datos es obligatoria: solo se recopila lo necesario para el caso de uso.
4. La separación entre información privada, compartible y pública debe ser explícita en cada entidad.

## Flujo de consentimiento (pendiente de implementación)
1. El usuario recibe información clara sobre qué datos se recopilan y para qué.
2. Acepta explícitamente (checkbox o firma digital).
3. El consentimiento se registra con fecha, versión y alcance.
4. El usuario puede revocar en cualquier momento.
5. Los datos se exportan/eliminan conforme a la revocación.

## Validación en API
- `origen_datos` debe ser `synthetic_pilot` en el MVP.
- Intentar registrar datos reales (`real_pilot`) sin metadato de consentimiento → HTTP 403.
- Cualquier endpoint que acepte datos debe validar `origen_datos`.

## Riesgos pendientes
- No hay proceso de consentimiento implementado.
- No hay política de retención definida.
- No hay derecho de acceso/portabilidad automatizado.
- No hay DPO (Data Protection Officer) asignado.
- **Estado P0 (commit `ad16c29`):** `ApprovalManager` (modelo `approval_requests`) creado y persistente en PostgreSQL (`7462b4e_approval`), pero **no integrado aún en `main.py`** para bloqueo de ejecución; la gobernanza opera en `evaluate()` (pre-acción) pero no impide la ejecución de la operación hasta aprobación humana en el flujo completo.
- **Estado repos auditados:** 11 repositorios (CASE, EnRuta, DashLogistics, FitFamily, etc.) permanecen bloqueados hasta que sus P0/P1 sean corregidos; Poolar es independiente.
- **Estado datos reales:** La API rechaza `real_pilot` (`HTTP 403`) cuando no hay consentimiento; la gobernanza (`AutomationEvaluator`) garantiza `REJECT` o `HUMAN_REVIEW` para datos reales sin contexto formal, pero no hay registro de consentimiento en base de datos aún.

## Referencias
- GDPR (Reglamento General de Protección de Datos).
- LOPDGDD (Ley Orgánica de Protección de Datos y Garantía de Derechos Digitales).
- `docs/modelo_autorizacion.md` — matriz de permisos.
- `docs/riesgos_pendientes.md` — riesgos P0/P1.