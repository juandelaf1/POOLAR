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


# Operaciones que el producto declara reanudables vía HITL (Fase 0). Mantener alineado con governance/endpoints.
EXPECTED_RESUMABLE_TOOLS = {
    "create_problema_colectivo",
    "create_iniciativa",
    "cambiar_estado_problema_colectivo",
    "create_decision",
    "create_decision_for_initiative",
}


def validate_resumable_handlers(expected=None) -> dict:
    """Valida registro determinista (F0-08). No lanza por defecto; devuelve informe."""
    expected = set(expected or EXPECTED_RESUMABLE_TOOLS)
    missing = sorted(t for t in expected if t not in RESUMABLE_HANDLERS)
    placeholders = sorted(
        t for t, fn in RESUMABLE_HANDLERS.items()
        if getattr(fn, "__name__", "") == "_not_impl"
    )
    return {"ok": not missing and not placeholders, "missing": missing, "placeholders": placeholders, "registered": sorted(RESUMABLE_HANDLERS)}
