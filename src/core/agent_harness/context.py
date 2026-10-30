"""Contexto de ejecución para agentes de Trama Abierta."""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import uuid


@dataclass
class ExecutionContext:
    """Contexto estructurado para una ejecución de agente.

    Se construye en el backend a partir de la identidad autenticada
    y los permisos existentes. Nunca confía en que el modelo
    proporcione su identidad o permisos.
    """
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    actor_id: Optional[int] = None
    actor_type: str = "persona"  # persona | organizacion
    actor_rol: str = "individuo"
    scope: Optional[Dict[str, Any]] = None  # Entidades accesibles
    objective: str = ""
    available_tools: List[str] = field(default_factory=list)
    token_budget: int = 4096
    cost_budget: float = 0.10
    timeout_seconds: int = 300
    max_iterations: int = 10
    data_provenance: str = "synthetic_pilot"
    agent_version: str = "0.1.0"
    instructions_version: str = "0.1.0"
    tools_version: str = "0.1.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "actor_id": self.actor_id,
            "actor_type": self.actor_type,
            "actor_rol": self.actor_rol,
            "scope": self.scope,
            "objective": self.objective,
            "available_tools": self.available_tools,
            "token_budget": self.token_budget,
            "cost_budget": self.cost_budget,
            "timeout_seconds": self.timeout_seconds,
            "max_iterations": self.max_iterations,
            "data_provenance": self.data_provenance,
            "agent_version": self.agent_version,
            "created_at": self.created_at.isoformat(),
        }

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self.available_tools

    def check_budget(self, tokens_used: int, cost_used: float) -> bool:
        return tokens_used <= self.token_budget and cost_used <= self.cost_budget