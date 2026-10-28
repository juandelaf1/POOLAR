# Visión y Propósito — Trama Abierta

**Fecha:** 28 de octubre de 2026  
**Versión:** 0.6 (MVP)

---

## Qué es Trama Abierta

Trama Abierta es una **infraestructura abierta, modular e interoperable** que permite a personas, comunidades, asociaciones, pequeñas empresas, cooperativas e instituciones:

1. **Identificar problemas compartidos** — incluso cuando quienes los sufren no se conocen entre sí.
2. **Reunir necesidades y capacidades** — agregar demandas, descubrir recursos disponibles y entender la escala real del problema.
3. **Coordinar soluciones colectivas** — comparar alternativas, tomar decisiones trazables, asignar responsabilidades y ejecutar acciones conjuntas.
4. **Medir y aprender** — registrar resultados observados, distinguir estimaciones de datos reales, exportar aprendizajes reutilizables.

No es una única aplicación monolítica, sino un **ecosistema de tres niveles**:

- **Trama Core** — núcleo común reutilizable (organizaciones, necesidades, problemas colectivos, recursos, iniciativas, decisiones, auditoría, procedencia, exportación).
- **Trama Iniciativas** — primera aplicación orientada al usuario para gestionar un proceso colectivo de extremo a extremo.
- **Aplicaciones especializadas** — módulos futuros para logística, infraestructura, compras, emergencias, análisis territorial, etc.

---

## Problema que aborda

Muchas necesidades individuales no generan por sí solas la demanda, la capacidad de negociación o los recursos necesarios para una solución viable. Ejemplos:

- Pequeños comercios sin volumen para una ruta logística eficiente.
- Barrios o pueblos con carencias compartidas de transporte, conectividad o servicios.
- Empresas que necesitan almacenamiento o equipamiento que no pueden financiar solas.
- Agricultores que podrían compartir maquinaria, instalaciones o comercialización.
- Asociaciones que requieren suministros o espacios accesibles conjuntamente.
- Comunidades que sufren el mismo problema pero carecen de información, organización o capacidad para formular una propuesta común.
- Recursos infrautilizados que podrían servir a otros.

La dificultad no es solo técnica: es **cómo pasar de necesidades dispersas a una comprensión compartida del problema y, después, a una solución coordinada y medible**.

---

## Usuarios y contextos iniciales

| Perfil | Qué aporta | Qué obtiene |
|---|---|---|
| Ciudadanos y comunidades | Necesidades, conocimiento del contexto, validación | Soluciones útiles, acceso a información, capacidad de decisión |
| Asociaciones y ONG | Conocimiento de beneficiarios, datos autorizados, validación | Mejor asignación de recursos, evaluación, infraestructura accesible |
| Autónomos y pymes | Necesidades operativas, experiencia, demanda | Ahorro, mejores procesos, herramientas, colaboración comercial |
| Cooperativas y redes productivas | Capacidad compartida, gobernanza, compras, logística | Coordinación, economías de escala, soluciones comunes |
| Instituciones y financiadores | Recursos, datos abiertos, retos, evaluación independiente | Resultados verificables, herramientas reutilizables, garantías de autonomía |

La participación no requiere saber programar, tener capital o tiempo libre ilimitado. Se valoran contribuciones de investigación, facilitación, traducción, pruebas, documentación, mentoría, cuidados, moderación y conocimiento local.

---

## Principios de diseño (del documento fundacional v0.5)

1. **Utilidad antes que novedad** — la tecnología se justifica por el problema que resuelve.
2. **Código abierto y reutilización** — licencias abiertas, documentación suficiente para entender, desplegar y mejorar.
3. **Personas por encima de métricas** — los afectados deben entender y participar en decisiones relevantes.
4. **Datos con contexto** — todo resultado explica fuente, fecha, cobertura, supuestos, calidad y límites.
5. **Privacidad por diseño** — se recopila lo mínimo necesario; no se publican datos personales por defecto.
6. **Transparencia y rendición de cuentas** — criterios de priorización, conflictos de interés, decisiones de gasto y resultados documentados.
7. **Autonomía y federación** — las comunidades conservan su identidad y eligen cuánto compartir.
8. **Distribución justa del valor** — contribuciones, costes, riesgos y beneficios visibles y distribuidos por reglas previas.
9. **Accesibilidad e inclusión** — distintos niveles de alfabetización digital, idiomas, dispositivos, discapacidad, conectividad.
10. **Interoperabilidad y salida** — formatos abiertos, exportación, documentación que reduzcan dependencia.
11. **Prudencia experimental** — hipótesis probadas a pequeña escala; criterios para continuar, corregir o detener.
12. **Aprender públicamente** — errores relevantes documentados sin humillar; compartir aprendizajes evita repetir fallos.
13. **Sostenibilidad humana** — el voluntariado no es la única base; mantenimiento, moderación y cuidados son trabajo reconocido.
14. **Neutralidad partidista, no neutralidad ética** — defiende derechos, seguridad, dignidad, no discriminación y transparencia.
15. **No prometer impactos no medidos** — ahorro estimado vs. conseguido; intención vs. resultado; piloto vs. probado a escala.

---

## Visión a largo plazo

Un ecosistema donde personas y organizaciones puedan:

- Colaborar a través de herramientas abiertas y reutilizables.
- Reutilizar soluciones confiables y adaptarlas a su contexto.
- Conservar control sobre sus datos y decisiones.
- Organizar actividades económicas de manera más transparente, eficiente y participativa.
- Medir el impacto por lo que mejora en la vida real, no por métricas de vanidad.

**Estrella polar:**  
> ¿Esta iniciativa aumenta la capacidad de las personas para resolver un problema real, por medios que puedan comprender, gobernar y mantener?

---

## Qué NO es Trama Abierta

- Una promesa de que la tecnología, la IA o los datos resuelvan solos problemas políticos o sociales.
- Una única cooperativa global que controle todas las iniciativas o todos los datos.
- Un sustituto de asesoría profesional, legal, fiscal o financiera.
- Una plataforma para recopilar datos personales sin límites o comerciar con ellos.
- Un sistema donde toda actividad deba ser gratuita ni una excusa para exigir trabajo no remunerado.
- Una democracia perfecta resuelta por votos o algoritmos; las decisiones requieren deliberación y responsabilidad.

---

## Estado actual

- **Fase:** MVP v0.6 — primer flujo funcional verificable (compra colaborativa).
- **Repositorio:** `trama_abierta_mvp/` (independiente, no integra código de proyectos auditados hasta resolver riesgos).
- **Documentación:** este archivo + `definicion_producto.md`, `modelo_problemas_colectivos.md`, `arquitectura.md`, `plan_mvp_y_piloto.md`, `decisiones_tecnicas.md`, `riesgos_pendientes.md`, `diferencial_y_analisis_mercado.md`.
- **Auditoría previa:** documentada en `../audit_trama_abierta/` (riesgos P0/P1 identificados, integración bloqueada hasta corrección verificada).