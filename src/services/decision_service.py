"""Servicio de dominio para creacion de Decision."""
from typing import Any, Dict
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.models import Decision, Iniciativa


def _puede_gestionar_iniciativa(iniciativa, user):
    from src.main import _puede_gestionar_iniciativa as _pgi
    return _pgi(iniciativa, user)


def _registrar_evento(db, *args, **kwargs):
    from src.main import _registrar_evento as _re
    return _re(db, *args, **kwargs)


def execute_create_decision(db: Session, data: Dict[str, Any], user: Dict[str, Any], *, commit: bool = True) -> dict:
    iniciativa_id = data.get("iniciativa_id")
    iniciativa = db.get(Iniciativa, iniciativa_id)
    if iniciativa is None or not _puede_gestionar_iniciativa(iniciativa, user):
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")

    decision = Decision(
        iniciativa_id=iniciativa_id,
        tipo_decision=data.get("tipo_decision"),
        alternativa_elegida=data.get("alternativa_elegida"),
        motivo=data.get("motivo"),
        responsable_decision=data.get("responsable_decision"),
        version_metodologia=data.get("version_metodologia"),
        factors=data.get("factors"),
    )
    db.add(decision)
    db.flush()
    _registrar_evento(db, "decision", decision.id, "resultado", user, justificacion=data.get("motivo"), dato_nuevo=data.get("alternativa_elegida"))
    if commit:
        db.commit()
        db.refresh(decision)
    else:
        db.flush()
    return {
        "id": decision.id,
        "iniciativa_id": decision.iniciativa_id,
        "version_metodologia": decision.version_metodologia,
        "alternativa_elegida": decision.alternativa_elegida,
    }

def execute_create_decision_for_initiative(db, data, user, *, commit: bool = True):
    iniciativa_id = data.get("iniciativa_id")
    iniciativa = db.get(Iniciativa, iniciativa_id)
    if iniciativa is None or not _puede_gestionar_iniciativa(iniciativa, user):
        raise HTTPException(status_code=404, detail="Iniciativa no encontrada")

    tipo = user.get("tipo")
    responsable = user.get("persona_id") if tipo == "individuo" else user.get("organizacion_id")
    decision = Decision(
        iniciativa_id=iniciativa_id,
        tipo_decision=data.get("tipo_decision"),
        alternativa_elegida=data.get("alternativa_elegida"),
        motivo=data.get("motivo"),
        responsable_decision=responsable,
        version_metodologia=data.get("version_metodologia"),
        factors=data.get("factors"),
    )
    db.add(decision)
    db.flush()
    _registrar_evento(db, "decision", decision.id, "resultado", user, justificacion=data.get("motivo"))
    if commit:
        db.commit()
        db.refresh(decision)
    else:
        db.flush()
    return {
        "id": decision.id,
        "iniciativa_id": decision.iniciativa_id,
        "tipo_decision": decision.tipo_decision,
        "alternativa_elegida": decision.alternativa_elegida,
        "motivo": decision.motivo,
        "responsable_decision": decision.responsable_decision,
        "version_metodologia": decision.version_metodologia,
        "fecha": decision.fecha,
    }
