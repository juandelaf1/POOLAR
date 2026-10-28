"""Servicios operativos de Trama Abierta — herramientas de necesidades."""
from sqlalchemy.orm import Session
from src.core.models import Necesidad, Persona


def needs_create(db: Session, titulo: str, descripcion: str, persona_id: int, visibilidad: str = "privada") -> Necesidad:
    need = Necesidad(titulo=titulo, descripcion=descripcion, persona_id=persona_id, visibilidad=visibilidad, estado="propuesta")
    db.add(need)
    db.commit()
    db.refresh(need)
    return need


def needs_get(db: Session, need_id: int, persona_id: int = None) -> Necesidad:
    need = db.get(Necesidad, need_id)
    if need is None:
        raise ValueError("Necesidad no encontrada")
    if need.persona_id is not None and need.persona_id != persona_id and need.visibilidad not in ("compartible", "publica"):
        raise ValueError("No autoriza acceder a esta necesidad")
    return need
