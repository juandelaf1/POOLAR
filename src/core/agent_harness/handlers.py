"""Registro cerrado de handlers reanudables para P0.4.

No se permite ejecución dinámica ni imports arbitrarios. Solo las operaciones
registradas aquí pueden reanudarse tras una aprobación humana.
"""
from typing import Callable, Dict, Any, Optional
from sqlalchemy.orm import Session


# Registro cerrado: tool_name -> handler(db, inputs) -> dict
RESUMABLE_HANDLERS: Dict[str, Callable[[Session, dict], dict]] = {}


def register_handler(tool_name: str, handler: Callable[[Session, dict], dict]) -> None:
    if tool_name in RESUMABLE_HANDLERS:
        raise ValueError(f"Handler ya registrado para {tool_name}")
    RESUMABLE_HANDLERS[tool_name] = handler


def get_handler(tool_name: str) -> Optional[Callable[[Session, dict], dict]]:
    return RESUMABLE_HANDLERS.get(tool_name)


def is_resumable(tool_name: str) -> bool:
    return tool_name in RESUMABLE_HANDLERS
