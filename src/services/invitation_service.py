"""Servicio de invitaciones y consentimiento persistente."""
from sqlalchemy.orm import Session
from src.core.models import Persona, ProblemaColectivo, Invitacion, EventoAuditoria


def invitations_create(
    db: Session,
    problema_id: int,
    emisor_id: int,
    emisor_tipo: str,
    destinatario_id: int,
    mensaje: str = "",
) -> dict:
    problema = db.get(ProblemaColectivo, problema_id)
    if problema is None:
        raise ValueError("Problema no encontrado")
    persona = db.get(Persona, destinatario_id)
    if persona is None or not persona.activo:
        raise ValueError("Persona no encontrada o inactiva")
    # No duplicados: verificar invitación pendiente existente
    existente = db.query(Invitacion).filter(
        Invitacion.problema_colectivo_id == problema_id,
        Invitacion.destinatario_id == destinatario_id,
        Invitacion.estado == "pendiente",
    ).first()
    if existente:
        raise ValueError("Ya existe una invitación pendiente para esta persona")
    invitacion = Invitacion(
        problema_colectivo_id=problema_id,
        emisor_id=emisor_id,
        emisor_tipo=emisor_tipo,
        destinatario_id=destinatario_id,
        estado="pendiente",
        mensaje=mensaje,
    )
    db.add(invitacion)
    db.commit()
    db.refresh(invitacion)
    _audit(db, "problema_colectivo", problema_id, "inicio", emisor_id, f"Invitación creada para persona {destinatario_id}")
    return {
        "id": invitacion.id,
        "problema_id": problema_id,
        "destinatario_id": destinatario_id,
        "estado": invitacion.estado,
        "fecha_creacion": str(invitacion.fecha_creacion),
    }


def invitations_accept(
    db: Session,
    invitacion_id: int,
    autentica_persona_id: int,
) -> dict:
    invitacion = db.get(Invitacion, invitacion_id)
    if invitacion is None:
        raise ValueError("Invitación no encontrada")
    if invitacion.destinatario_id != autentica_persona_id:
        raise ValueError("No autorizado para aceptar esta invitación")
    if invitacion.estado != "pendiente":
        raise ValueError(f"Invitación en estado '{invitacion.estado}', no se puede aceptar")
    invitacion.estado = "aceptada"
    invitacion.fecha_respuesta = invitacion.fecha_respuesta or invitacion.fecha_respuesta
    from sqlalchemy.sql import func
    invitacion.fecha_respuesta = func.now()
    db.commit()
    problema = db.get(ProblemaColectivo, invitacion.problema_colectivo_id)
    persona = db.get(Persona, invitacion.destinatario_id)
    if persona not in (problema.personas_participantes or []):
        problema.personas_participantes = (problema.personas_participantes or []) + [persona]
        db.commit()
    _audit(db, "problema_colectivo", invitacion.problema_colectivo_id, "hito", autentica_persona_id, "Participación aceptada")
    return {"id": invitacion.id, "estado": invitacion.estado}


def invitations_reject(
    db: Session,
    invitacion_id: int,
    autentica_persona_id: int,
) -> dict:
    invitacion = db.get(Invitacion, invitacion_id)
    if invitacion is None:
        raise ValueError("Invitación no encontrada")
    if invitacion.destinatario_id != autentica_persona_id:
        raise ValueError("No autorizado para rechazar esta invitación")
    if invitacion.estado != "pendiente":
        raise ValueError(f"Invitación en estado '{invitacion.estado}', no se puede rechazar")
    invitacion.estado = "rechazada"
    invitacion.fecha_respuesta = func.now()
    db.commit()
    _audit(db, "problema_colectivo", invitacion.problema_colectivo_id, "cambio_estado", autentica_persona_id, "Invitación rechazada")
    return {"id": invitacion.id, "estado": invitacion.estado}


def invitations_retire(
    db: Session,
    invitacion_id: int,
    autentica_persona_id: int,
) -> dict:
    invitacion = db.get(Invitacion, invitacion_id)
    if invitacion is None:
        raise ValueError("Invitación no encontrada")
    if invitacion.destinatario_id != autentica_persona_id:
        raise ValueError("No autorizado para retirar esta participación")
    if invitacion.estado not in ("aceptada", "pendiente"):
        raise ValueError(f"Invitación en estado '{invitacion.estado}', no se puede retirar")
    invitacion.estado = "retirada"
    invitacion.fecha_retirada = func.now()
    problema = db.get(ProblemaColectivo, invitacion.problema_colectivo_id)
    problema.personas_participantes = [p for p in (problema.personas_participantes or []) if p.id != invitacion.destinatario_id]
    db.commit()
    _audit(db, "problema_colectivo", invitacion.problema_colectivo_id, "cambio_estado", autentica_persona_id, "Participación retirada")
    return {"id": invitacion.id, "estado": invitacion.estado}


def _audit(db: Session, entidad: str, entidad_id: int, tipo_evento: str, user_id: int, justificacion: str):
    db.add(EventoAuditoria(
        entidad_referencia=entidad, entidad_id=entidad_id, tipo_evento=tipo_evento,
        usuario_o_sistema=f"user_{user_id}", justificacion=justificacion,
    ))
    db.commit()