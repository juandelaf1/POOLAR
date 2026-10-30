"""Gestión de estado para el Agent Harness de Poolar.

Diferencia entre:
- Estado oficial del dominio (PostgreSQL).
- Estado temporal de una ejecución.
- Contexto de conversación.
- Memoria reutilizable de un agente.
- Historial de auditoría.

El estado del agente nunca prevalece sobre el estado actual del dominio.
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class ExecutionState:
    """Estado temporal de una ejecución de agente."""
    execution_id: str
    current_step: int = 0
    total_steps: int = 0
    status: str = "running"  # running, paused, completed, failed, cancelled
    steps_completed: List[str] = field(default_factory=list)
    steps_pending: List[str] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    checkpoint: Optional[Dict[str, Any]] = None

    def mark_step_complete(self, step_name: str, result: Any = None) -> None:
        if step_name not in self.steps_completed:
            self.steps_completed.append(step_name)
        if step_name in self.steps_pending:
            self.steps_pending.remove(step_name)
        if result is not None:
            self.results[step_name] = result
        self.last_updated = datetime.utcnow()

    def mark_step_pending(self, step_name: str) -> None:
        if step_name not in self.steps_pending:
            self.steps_pending.append(step_name)

    def is_complete(self) -> bool:
        return len(self.steps_pending) == 0 and len(self.steps_completed) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "status": self.status,
            "steps_completed": self.steps_completed,
            "steps_pending": self.steps_pending,
            "results": self.results,
            "errors": self.errors,
            "started_at": self.started_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class ExecutionStateManager:
    """Gestor de estado de ejecuciones."""

    def __init__(self):
        self._states: Dict[str, ExecutionState] = {}

    def create(self, execution_id: str, total_steps: int = 0) -> ExecutionState:
        state = ExecutionState(execution_id=execution_id, total_steps=total_steps)
        self._states[execution_id] = state
        return state

    def get(self, execution_id: str) -> Optional[ExecutionState]:
        return self._states.get(execution_id)

    def update(self, execution_id: str, **kwargs) -> Optional[ExecutionState]:
        state = self._states.get(execution_id)
        if state is None:
            return None
        for key, value in kwargs.items():
            if hasattr(state, key):
                setattr(state, key, value)
        state.last_updated = datetime.utcnow()
        return state

    def delete(self, execution_id: str) -> bool:
        return self._states.pop(execution_id, None) is not None

    def list_active(self) -> List[ExecutionState]:
        return [s for s in self._states.values() if s.status in ("running", "paused")]


# Gestor global de estado de ejecuciones
execution_state_manager = ExecutionStateManager()