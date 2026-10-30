"""Registro de herramientas tipadas para el Agent Harness de Trama Abierta."""
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class ToolType(str, Enum):
    READ = "read"
    PROPOSAL = "proposal"
    CONTROLLED = "controlled"
    SENSITIVE = "sensitive"


@dataclass
class ToolDefinition:
    """Definición de una herramienta del harness."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    tool_type: ToolType
    required_permissions: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    requires_approval: bool = False
    idempotent: bool = False
    max_calls: int = 10
    timeout_seconds: int = 30
    errors: List[str] = field(default_factory=list)
    audit_events: List[str] = field(default_factory=list)
    handler: Optional[Callable] = None


class ToolRegistry:
    """Registro central de herramientas del harness."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Herramienta '{tool.name}' ya registrada")
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def list_by_type(self, tool_type: ToolType) -> List[ToolDefinition]:
        return [t for t in self._tools.values() if t.tool_type == tool_type]

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    def get_handler(self, name: str) -> Optional[Callable]:
        tool = self._tools.get(name)
        return tool.handler if tool else None


# Registro global del harness
harness_registry = ToolRegistry()


def register_tool(tool: ToolDefinition) -> None:
    """Registra una herramienta en el harness global."""
    harness_registry.register(tool)