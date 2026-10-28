# Modelo de Problemas Colectivos — Trama Abierta v0.6

Referencia: `docs/vision_y_proposito.md`; `trama_abierta_mvp/src/core/contracts.py`; `trama_abierta_mvp/src/core/models.py`.
Estado: Definido en contratos y modelos; pendiente verificación completa con datos de piloto.

---

## Entidad central: Problema Colectivo

No es una etiqueta ni un tipo de iniciativa. Es una entidad de dominio que representa una situación que afecta a varias personas u organizaciones y que requiere una respuesta coordinada.

### Diferencia clave

- **Necesidad individual** (`Necesidad`): algo que una persona o organización declara como carencia, objetivo o problema.
- **Problema Colectivo** (`ProblemaColectivo`): agrupación validada de necesidades relacionadas que comparten contexto, causa, alcance territorial o impacto, y que pueden requerir una respuesta conjunta.
- **Iniciativa** (`Iniciativa`): acción coordinada propuesta para abordar un problema (o parte de él), no el problema en sí.

Esto evita confundir una coincidencia potencial con una relación confirmada.

---

## Relaciones fundamentales

```
Persona ── puede declarar ──► Necesidad
Organizacion ── puede declarar ──► Necesidad
Necesidad ── se relaciona con ──► ProblemaColectivo (N:M, validable/rechazable)
ProblemaColectivo ── reúne ──► Personas participantes (lista de IDs)
ProblemaColectivo ── reúne ──► Organizaciones participantes (lista de IDs)
ProblemaColectivo ── puede generar ──► Iniciativa (1:N)
Iniciativa ── utiliza ──► Recurso / RecursoAporte (N:M por contexto)
Iniciativa ── toma ──► Decision (1:N, con version_metodologia)
Iniciativa ── genera ──► EventoAuditoria (1:N, con trazabilidad)
```

---

## Reglas de dominio (verificables en código y pruebas)

1. **No todo grupo de necesidades iguales es un Problema Colectivo**. Se requiere un paso de validación (`estado: detectado → en_analisis → validado`).
2. **Una necesidad puede pertenecer a más de un Problema Colectivo** cuando aplica a contextos distintos (ej: transporte rural y logística ambiental).
3. **Un Problema Colectivo no requiere una organización previa**. Una persona puede iniciar; otras pueden unirse; una organización puede participar posteriormente sin ser obligatoria.
4. **No se asume que todas las necesidades asociadas tengan la misma solución**. La Iniciativa puede ser una de varias alternativas evaluadas (`alternativas_evaluadas`).
5. **Los datos personales permanecen separados**. El `ProblemaColectivo` describe el problema; no expone datos de personas (`Contacto`/`DNI` no en DTO público).
6. **La evidencia es necesaria antes de validar** (`evidencias` como campo obligatorio o recomendado; `calidad_reportada` en `ProcedenciaDatos`).
7. **Las coincidencias erróneas deben poder rechazarse** (`estado: rechazado` o `corregido`; registro de `EventoAuditoria` cuando se rechaza o modifica una relación).

---

## Estado en el código (verificado)

- `ProblemaColectivo` está definido en `src/core/contracts.py` (`BaseModel`) con campos `descripcion`, `necesidades_asociadas`, `organizaciones_participantes`, `personas_participantes`, `descripcion_problema`, `evidencias`, `estado`, `fecha_detecion`, `fecha_actualizacion`.
- `ProblemaColectivo` está definido en `src/core/models.py` (`SQLAlchemy`) con relación `N:M` (`necesidad_problema_colectivo`) a `Necesidad`, y campo `iniciativas` vinculadas.
- La relación `Necesidad ↔ ProblemaColectivo` permite agregar y quitar sin perder la `Necesidad` individual.
- La `Iniciativa` incorpora `problema_colectivo_id` opcional, permitiendo que una iniciativa se cree desde un problema validado.
- La `Persona` permite iniciar sin `Organizacion`; `Organizacion` amplifica posibilidades pero no es obligatoria.

---

## Qué falta antes de usarlo en piloto

- Validación de la relación `N:M` con datos reales o sintéticos etiquetados.
- Prueba de que una `Necesidad` puede existir sin `organizacion_id` (solo con `persona_id` o sin ser de organización).
- Confirmación de que `EventoAuditoria` registra cambios de relación sin exponer datos personales.
- Definición de `version_metodologia` para decisiones vinculadas al problema y no solo a la iniciativa.

---

## Por qué esto diferencia a Trama Abierta

No se trata solo de "agrupar necesidades similares" por categoría o ubicación. Se trata de permitre que varias personas u organizaciones **validen que comparten un problema** antes de decidir actuar juntos, y de conservar evidencia de cómo llegó esa validación (evidencias, criterios, decisiones de rechazo o corrección, resultados). Esto es lo que convierte una coincidencia potencial en una acción colectiva informada.
