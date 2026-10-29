# Accesibilidad — Trama Abierta (WCAG 2.1 AA)

## Estado
Guía base; no implementado completamente.

## Principios (POUR)
- **Perceptible**: contraste mínimo 4.5:1 para texto normal, 3:1 para texto grande.
- **Operable**: navegación por teclado completa, sin trampas de foco.
- **Comprensible**: etiquetas claras, mensajes de error descriptivos.
- **Robusto**: HTML semántico, ARIA cuando sea necesario.

## Requisitos mínimos
1. Todos los formularios tienen `label` asociado con `for`.
2. Los botones tienen texto descriptivo o `aria-label`.
3. Los estados de carga/error se anuncian con `aria-live`.
4. La navegación por teclado cubre todos los elementos interactivos.
5. El foco visible (outline) no se elimina.
6. Las imágenes tienen `alt` descriptivo.
7. Los mensajes de error son específicos y legibles.

## Estado actual de la interfaz
- `interfaz/index.html`: formularios con labels, botones con texto, estados de error visibles.
- Pendiente: navegación por teclado completa, ARIA live regions, contraste verificado.

## Referencias
- WCAG 2.1 (W3C).
- `docs/modelo_autorizacion.md` — matriz de permisos.
- `interfaz/index.html` — interfaz funcional.