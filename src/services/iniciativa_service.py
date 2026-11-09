"""Servicio de dominio para creacion de Iniciativa."""
from typing import Any, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.models import Necesidad, Organizacion, ProblemaColectivo, Iniciativa


def _need_accesible(need, user_ctx):
    from src.main import _need_accesible as _na
    return _na(need, user_ctx)


def _problema_visible(problema, user_ctx):
    from src.main import _problema_visible as _pv
    return _pv(problema, user_ctx)


def _registrar_evento(db, *args, **kwargs):
    from src.main import _registrar_evento as _re
    return _re(db, *args, **kwargs)


def execute_create_iniciativa(db: Session, data: Dict[str, Any], user: Dict[str, Any], *, commit: bool = True) -> dict:
    tipo = user.get("tipo")
    if tipo == "individuo":
        org_id = None
    else:
        org_id = user.get("organizacion_id")
        if org_id is None:
            raise HTTPException(status_code=403, detail="No se identifico organizacion")

    necesidad_id = data.get("necesidad_id")
    necesidad = db.get(Necesidad, necesidad_id)
    if necesidad is None or (org_id is not None and not _need_accesible(necesidad, org_id)) or (tipo == "individuo" and (necesidad.persona_id is None or necesidad.persona_id != user.get("persona_id"))):
        raise HTTPException(status_code=404, detail="Necesidad no accesible")

    responsable_id = data.get("responsable_id")
    if tipo == "individuo":
        if responsable_id != user.get("persona_id"):
            raise HTTPException(status_code=403, detail="Responsable debe ser la persona autenticada")
    else:
        if responsable_id != org_id:
            raise HTTPException(status_code=403, detail="El responsable debe ser la organizacion autenticada")

    criterios = (data.get("criterios_decision") or "").strip()
    if len(criterios) < 5:
        raise HTTPException(status_code=422, detail="criterios_decision debe describir el criterio de decision")

    problema = None
    problema_colectivo_id = data.get("problema_colectivo_id")
    if problema_colectivo_id is not None:
        problema = db.get(ProblemaColectivo, problema_colectivo_id)
        if problema is None or not _problema_visible(problema, user if tipo == "individuo" else org_id):
            raise HTTPException(status_code=404, detail="Problema colectivo no encontrado")

    resp_tipo = "persona" if tipo == "individuo" else "organizacion"
    resp_id = user.get("persona_id") if tipo == "individuo" else org_id
    iniciativa = Iniciativa(
        necesidad_id=necesidad_id,
        problema_colectivo_id=problema_colectivo_id,
        responsable_id=resp_id,
        responsable_tipo=resp_tipo,
        titulo=data.get("titulo"),
        descripcion=data.get("descripcion", ""),
        alternativas_evaluadas=data.get("alternativas_evaluadas", ""),
        criterios_decision=data.get("criterios_decision", ""),
        presupuesto_estimate=data.get("presupuesto_estimate"),
        plazo=data.get("plazo"),
        estado="propuesta",
    )
    db.add(iniciativa)
    db.flush()
    _registrar_evento(db, "iniciativa", iniciativa.id, "inicio", user, justificacion="Iniciativa propuesta")
    if commit:
        db.commit()
        db.refresh(iniciativa)
    else:
        db.flush()
    return {"id": iniciativa.id, "necesidad_id": iniciativa.necesidad_id, "problema_colectivo_id": iniciativa.problema_colectivo_id, "responsable_id": iniciativa.responsable_id, "responsable_tipo": iniciativa.responsable_tipo, "titulo": iniciativa.titulo, "descripcion": iniciativa.descripcion, "alternativas_evaluadas": iniciativa.alternativas_evaluadas, "criterios_decision": iniciativa.criterios_decision, "presupuesto_estimate": iniciativa.presupuesto_estimate, "plazo": iniciativa.plazo, "estado": iniciativa.estado, "fecha_creacion": iniciativa.fecha_creacion, "fecha_actualizacion": iniciativa.fecha_actualizacion}
