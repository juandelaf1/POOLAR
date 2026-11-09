# POOLAR — Benchmark estratégico, arquitectura de bien común, accesibilidad, seguridad y sostenibilidad

**Fecha de consulta de fuentes externas:** 2026-11-09.  
**Estado del documento:** registrado en repo a solicitud del usuario. Análisis de arquitectura/estrategia (no implementación).  
**Restricciones aplicadas en la sesión de origen:** no se modificó el repositorio durante el análisis; no se ejecutaron commits/PR; no se reejecutaron pruebas.

## Verificación del estado POOLAR (referencia, 2026-11-09)

| Elemento | Estado observado |
|---|---|
| Repo local | `C:\Users\JUAN\Desktop\Proyectos\Trama_Abierta\poolar` |
| Rama / HEAD | `fase0-gobernanza` / `9ddc834096d1bd86e39f9ef32d6ffbf61452f32f` |
| CI definido | `ci.yml` (PG16, migraciones, backend sin e2e, e2e Playwright) y `fase0-check.yml` (SQLite; `fase0-pg-real` `if:false`) — **ejecución verde remota no verificada** |
| Evidencia histórica (no reejecutada) | Núcleo HITL/gobernanza con avances; suite canónica Fase 0+capacidad 104 passed; backend sin E2E 174 passed / 1 xfailed / 7 failed por sensibilidad PG; Fase 0 no cerrada formalmente |

## 1. Resumen ejecutivo
Existe un espacio potencial, pero **no validado empíricamente**, para una infraestructura abierta de cooperación que conecte *necesidad → capacidades/recursos → iniciativa → decisión HITL → compromiso → ejecución → aprendizaje* con gobernanza humana fuerte, portabilidad y diseño para comunidades con pocos recursos. El hueco plausible no es “tener más objetos”, sino combinar: núcleo común interoperable + gobernanza/autorización humana verificable + privacidad/consentimiento + portabilidad real + uso esencial gratuito orientado a comunidades sin presupuesto + operación progresiva en baja conectividad + módulos especializados conectables sin doble autoridad.

## 2. Mapa competitivo (resumen)

| Tipo | Proyecto | Relación | Evidencia (2026-11-09) |
|---|---|---|---|
| Competidor conceptual directo | **Armillaria / Innovation Exchange** | People/Projects/Organisations/Opportunities/Issues/Needs/Offers; matching, procedencia/fork, permisos/revisión/scoring/reporting/export declarados; precios publicados; **open source/self-host no verificado** | https://armillaria.io/, https://armillaria.io/exchange — DECLARADA/VERIFICADA en web |
| Referente organizativo | **Commonhood** | Sitio público insuficiente para verificar plataforma software comparable | https://www.commonhood.org/ — NO VERIFICADO |
| Gobernanza/participación | **Decidim** | Procesos participativos; AGPL; autoalojable | decidim.org, GitHub decidim/decidim — VERIFICADA |
| Decisión deliberativa | **Loomio** | Discusiones/decisiones; AGPL; SaaS + self-host | loomio.com/pricing, GitHub loomio/loomio — VERIFICADA |
| Estándar/ontología | **ValueFlows** | Vocabulario agentes/recursos/compromisos/eventos/flujos | valueflo.ws — VERIFICADA |
| Framework | **hREA** | Implementación Holochain alineada con ValueFlows/REA | GitHub h-REA/hREA — PARCIAL |
| Vertical alimentación | **Open Food Network** | Marketplace cadena corta; AGPL; instancias locales | openfoodnetwork.org, GitHub — VERIFICADA |
| Vertical logística | **CoopCycle** | Logística cooperativa; licencia Coopyleft (uso condicionado) | coopcycle.org, GitHub — VERIFICADA con restricción |
| Finanzas/fiscal hosting | **Open Collective** | Gestión financiera colaborativa/transparencia; ecosistema OFiCo | opencollective.com, GitHub — PARCIAL |
| Campo/offline | **KoboToolbox** | Recolección datos/terreno; componentes AGPL | kobotoolbox.org, GitHub kpi — PARCIAL/VERIFICADA |
| Crisis/crowdsourcing | **Ushahidi** | Reportes/mapas/API; AGPL | ushahidi.com, GitHub platform — VERIFICADA |
| Verticales compras | **Karakolas, WeGrocery** | Búsqueda rápida sin evidencia verificable suficiente | NO VERIFICADO |

## 3. Lecciones clave
- **Armillaria:** modelo de dominio/matching/procedencia/configuración útil; diferenciarse por apertura, HITL verificable, soberanía de datos y diseño low-resource.
- **Decidim/Loomio:** integrar deliberación/decisión madura, no reconstruir.
- **ValueFlows:** referencia semántica para recursos/compromisos/eventos.
- **OFN/CoopCycle/Open Collective:** verticales/finanzas a integrar cuando aplique.
- **Kobo/Ushahidi:** patrones de captura en campo/offline parcial y riesgos Do No Harm.

## 4. Matriz CORE / MODULE / CONNECTOR / SEPARATE (síntesis)
| Capacidad | Decisión |
|---|---|
| Identidad, orgs, membresías, roles/permisos, HITL/políticas | **CORE** |
| Necesidades, ofertas, capacidades, recursos, problemas, oportunidades, iniciativas, propuestas/decisiones/approvals | **CORE** |
| Compromisos/ejecución (modelo) | **CORE** + operativa específica en **MODULE** |
| Auditoría, procedencia, consentimiento, export, aprendizaje base | **CORE** (+ analytics separado) |
| Matching/scoring explicable | **MODULE** inicial interno/servicio; posibles conectores |
| Compras, logística, banco recursos, ayuda mutua, emergencias (operativa) | **MODULE** o **CONNECTOR** según vertical |
| Finanzas/fiscal hosting, deliberación ciudadana compleja, logística/marketplaces maduros | **CONNECTOR / SEPARATE** |

## 5. Seguridad, accesibilidad y offline (requisitos de diseño)
- **Seguridad:** identidad progresiva y proporcional al riesgo (sin KYC universal excluyente), RBAC/ABAC, aislamiento org/tenant, rate limiting, moderación/reporte/apelación, protección de vulnerables/menores, auditoría sin sobre-recolección, módulos/adaptadores *proposal-only* sin autoridad de ejecución sensible.
- **Accesibilidad:** objetivo WCAG 2.2 AA, móvil, teclado/lector, lectura fácil, i18n, participación asistida.
- **Offline progresivo:** borradores/cola local idempotente para acciones de bajo riesgo; sync explícita y resolución de conflictos; **nunca** offline para approvals/decisiones vinculantes, cambios de permisos o acciones sensibles.
- **Do No Harm / DPG:** referencias de diseño; no reclamar certificación sin evaluación.

## 6. Sostenibilidad (misión de bien común)
Modelo recomendado: **híbrido** (subvenciones/fondos públicos/filantropía + pagos institucionales por hosting/soporte/implantación + nodos comunitarios). Esenciales gratuitos (código, uso, APIs base, export). **Prohibido como modelo principal:** venta de datos, publicidad conductual, pay-per-seat en esenciales, lock-in.

## 7. Decisiones estratégicas (resumen)
1. Cerrar Fase 0 y hardening authz/PG/CI/RGPD. 2. Licencia open source clara + export/self-host. 3. Dominio canónico Core (alineable con ValueFlows/Armillaria). 4. Un piloto acotado con comunidad real. 5. Sostenibilidad/gobernanza anticaptura + identidad progresiva.

## 8. Limitaciones de evidencia
Mezcla de **VERIFICADA** (repos/licencias públicas consultadas, estado local POOLAR), **DECLARADA** (claims de producto/precios/casos), **HISTÓRICA** (tests POOLAR previos no reejecutados), e **HIPÓTESIS/DESCONOCIDA** (nicho, costes, licencias no confirmadas, Karakolas/WeGrocery). Armillaria: open source/self-host **no verificado**.
