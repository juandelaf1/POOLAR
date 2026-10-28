"""Servicio de invitaciones y consentimiento persistente."""
from sqlalchemy.orm import Session
from src.core.models import Persona, ProblemaColectivo, EventoAuditoria
from src.core.auth import hash_password


def invitations_create(db: Session, problema_id: int, persona_id: int, emisor_user_id: int, mensaje: str = "") -> dict:
    problema = db.get(ProblemaColectivo, problema_id)
    if problema is None:
        raise ValueError("Problema no encontrado")
    persona = db.get(Persona, persona_id)
    if persona is None or not persona.activo:
        raise ValueError("Persona no encontrada o inactiva")
    # Añadir a la ínter-participantes derivados
    already = [p for p in problema.personas_participantes if p.id == persona_id]
    if not already:
        problema.personas_participantes = [x for x in (problema.personas_participantes or []) if x.id != persona_id] + [persona]
        db.commit()
        _audit(db, "problema_colectivo", problema_id, "inicio", emisor_user_id, f"Invitación a persona {persona_id}")
    return {"problema_id": problema_id, "persona_id": persona_id, "estado": "pendiente_aceptacion"}


def participation_accept(db: Session, problema_id: int, persona_id: int, autentica_persona_id: int) -> dict:
    problema = db.get(ProblemaColectivo, problema_id)
    if problema is None or not (problema.persona_id is not None and problema.persona_id == persona_id) \
       and not any(p.id == persona_id for p in problema.personas_participantes):
        raise ValueError("No autorizado para participar en este problema")
    already = [p for p in problema.personas_participantes if p.id == persona_id]
    if not already:
        problema.personas_participantes = problema.personas_participantes or []
        problema.personas_participantes.append(db.get(Persona, persona_id))
        db.commit()
        _audit(db, "problema_colectivo", problema_id, "hito", autentica_persona_id, "Participación aceptada")
    return {"problema_id": problema_id, "persona_id": persona_id, "estado": "aceptada"}


def participation_retire(db: Session, problema_id: int, persona_id: int, autentica_persona_id: int) -> dict:
    problema = db.get(ProblemaColectivo, problema_id)
    problema.personas_participantes = [p for p in (problema.personas_participantes or []) if p.id != persona_id]
    db.commit()
    _audit(db, "problema_colectivo", problema_id, "cambio_estado", autentica_persona_id, "Retirada de participación")
    return {"problema_id": problema_id, "persona_id": persona_id, "estado": "rechazada"}


def _audit(db: Session, entidad: str, entidad_id: int, tipo_evento: str, user_id: int, justificacion: str):
    db.add(EventoAuditoria(
        entidad_referencia=entidad, entidad_id=entidad_id, tipo_evento=tipo_evento,
        usuario_o_sistema=f"user_{user_id}", justificacion=justificacion,
    ))
    db.commit()
