"""Servicio de dominio para creación de Problema Colectivo.

Compartido por el flujo AUTO_APPROVE y por la reanudación tras aprobación
humana (P0.4). Toda la validación y el efecto de negocio viven aquí.
"""
from typing import Any, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.contracts import ProblemaColectivoEstado
from src.core.models import (
    Necesidad, Persona, Organizacion, ProblemaColectivo,
)


def _need_accesible(need, user_ctx):
    from src.main import _need_accesible as _na
    return _na(need, user_ctx)


def _problema_dto(problema, user_ctx):
    from src.main import _problema_dto as _pd
    return _pd(problema, user_ctx)


def _registrar_evento(db, *args, **kwargs):
    from src.main import _registrar_evento as _re
    return _re(db, *args, **kwargs)


def execute_create_problema_colectivo(db: Session, data: Dict[str, Any], user: Dict[str, Any]) -> dict:
    """Valida y crea un Problema Colectivo. Idempotente a nivel de efecto.

    `data` debe contener las claves del payload original (descripcion, evidencias,
    necesidades_asociadas, personas_participantes, organizaciones_participantes,
    origen_datos) y `user` el contexto del actor (tipo, user_id, persona_id,
    organizacion_id).
    """
    tipo = user.get("tipo")
    if tipo == "individuo":
        org_id = None
    else:
        org_id = user.get("organizacion_id")
        if org_id is None:
            raise HTTPException(status_code=403, detail="No se identifico una organizacion valida")
        org = db.get(Organizacion, org_id)
        if org is None:
            raise HTTPException(status_code=404, detail="Organizacion no encontrada")

    origen = data.get("origen_datos", "synthetic_pilot")
    if origen != "synthetic_pilot":
        raise HTTPException(status_code=403, detail="Solo datos sinteticos etiquetados permitidos")

    necesidades = []
    for need_id in data.get("necesidades_asociadas", []):
        need = db.get(Necesidad, need_id)
        if need is None or (org_id is not None and not _need_accesible(need, org_id)) and not (tipo == "individuo" and need.persona_id is not None and need.persona_id == user.get("persona_id")):
            raise HTTPException(status_code=404, detail=f"Necesidad {need_id} no encontrada o no accesible")
        necesidades.append(need)

    personas_solicitadas = []
    for persona_id in data.get("personas_participantes", []):
        persona = db.get(Persona, persona_id)
        if persona is None:
            raise HTTPException(status_code=404, detail=f"Persona {persona_id} no encontrada")
        personas_solicitadas.append(persona)

    organizaciones_solicitadas = []
    for participante_id in data.get("organizaciones_participantes", []):
        participante = db.get(Organizacion, participante_id)
        if participante is None:
            raise HTTPException(status_code=404, detail=f"Organizacion {participante_id} no encontrada")
        organizaciones_solicitadas.append(participante)

    personas_derivadas = {need.persona_id for need in necesidades if need.persona_id is not None}
    organizaciones_derivadas = {need.organizacion_id for need in necesidades if need.organizacion_id is not None}
    if org_id is not None:
        organizaciones_derivadas.add(org_id)

    if any(p.id not in personas_derivadas for p in personas_solicitadas):
        raise HTTPException(status_code=403, detail="No se puede incorporar una persona sin relaci\u00f3n con las necesidades asociadas (falta flujo de consentimiento)")
    if any(o.id not in organizaciones_derivadas for o in organizaciones_solicitadas):
        raise HTTPException(status_code=403, detail="No se puede incorporar una organizaci\u00f3n sin relaci\u00f3n con las necesidades asociadas (falta flujo de invitaci\u00f3n)")

    personas_participantes = sorted(personas_derivadas)
    organizaciones_participantes = sorted(organizaciones_derivadas)

    problema = ProblemaColectivo(
        descripcion=data.get("descripcion"),
        evidencias=data.get("evidencias"),
        estado=ProblemaColectivoEstado.detectado.value,
        origen_datos=origen,
        organizacion_id=org_id,
        persona_id=user.get("persona_id") if tipo == "individuo" else None,
        creado_por_id=user.get("user_id") or user.get("persona_id"),
    )
    problema.necesidades_asociadas = necesidades
    problema.personas_participantes = [db.get(Persona, pid) for pid in personas_participantes]
    problema.organizaciones_participantes = [db.get(Organizacion, oid) for oid in organizaciones_participantes]
    db.add(problema)
    db.flush()
    _registrar_evento(db, "problema_colectivo", problema.id, "inicio", user, justificacion="Problema colectivo creado")
    db.commit()
    db.refresh(problema)
    return _problema_dto(problema, org_id)


def execute_cambiar_estado_problema(db, data, user):
    from src.core.contracts import ProblemaColectivoEstado, TRANSICIONES_PROBLEMA_COLECTIVO
    problema_id = data.get("problema_id")
    nuevo_estado_raw = data.get("nuevo_estado")
    nuevo_estado = ProblemaColectivoEstado(nuevo_estado_raw) if not isinstance(nuevo_estado_raw, ProblemaColectivoEstado) else nuevo_estado_raw

    problema = db.get(ProblemaColectivo, problema_id)
    if problema is None:
        raise HTTPException(status_code=404, detail="Problema colectivo no encontrado")
    # revalidar visibilidad
    if not _problema_visible(problema, user):
        raise HTTPException(status_code=404, detail="Problema colectivo no encontrado")

    estado_actual = ProblemaColectivoEstado(problema.estado)
    permitidos = TRANSICIONES_PROBLEMA_COLECTIVO[estado_actual]
    if nuevo_estado not in permitidos:
        raise HTTPException(status_code=409, detail=f"Transicion no permitida: {estado_actual.value} -> {nuevo_estado.value}")

    if nuevo_estado is ProblemaColectivoEstado.validado and not (problema.evidencias or "").strip():
        raise HTTPException(status_code=422, detail="Para validar el problema se requiere evidencia registrada")

    anterior = problema.estado
    problema.estado = nuevo_estado.value if hasattr(nuevo_estado, "value") else nuevo_estado
    _registrar_evento(db, "problema_colectivo", problema.id, "cambio_estado", user, justificacion="Cambio de estado reanudado", dato_anterior=anterior, dato_nuevo=problema.estado)
    db.commit()
    db.refresh(problema)
    return _problema_dto(problema, user.get("organizacion_id"))
