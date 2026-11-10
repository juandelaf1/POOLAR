# Accessibility — POOLAR (WCAG 2.1 AA target)

> Updated: 2026-11-10. Status: **baseline guidance; not fully implemented/verified**.

## Principles (POUR)
- **Perceivable**: sufficient contrast (4.5:1 normal text, 3:1 large text).
- **Operable**: full keyboard navigation, no focus traps.
- **Understandable**: clear labels and descriptive error messages.
- **Robust**: semantic HTML, ARIA where necessary.

## Minimum requirements
1. All form inputs have associated `label`/`for`.
2. Buttons have descriptive text or `aria-label`.
3. Loading/error states announced with `aria-live` where appropriate.
4. Keyboard navigation covers all interactive elements.
5. Visible focus indicators are preserved.
6. Images have descriptive `alt` text.
7. Error messages are specific and readable.

## Current state (indicative)
- `interfaz/index.html` includes basic labels/buttons and visible error states.
- Pending: complete keyboard flow, ARIA live regions, verified contrast, and broader audit.

## References
- WCAG 2.1 (W3C).
- `docs/modelo_autorizacion.md` — authorization context.
- `interfaz/index.html`.