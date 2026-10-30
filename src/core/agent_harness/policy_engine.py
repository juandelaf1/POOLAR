"""Motor de políticas del Agent Harness de Poolar.

Verifica permisos, autorización y reglas de dominio antes de ejecutar
cualquier herramienta. La autorización se comprueba en el momento de
ejecutar la herramienta, no solo al preparar el prompt.
"""
from typing import Optional, Dict, Any, List
from src.core.agent_harness.context import ExecutionContext
from src.core.agent_harness.tool_registry import ToolDefinition, ToolType


class PolicyEngine:
    """Motor de políticas para el harness."""

    def __init__(self):
        self._policies: List[Callable] = []

    def add_policy(self, policy: Callable) -> None:
        self._policies.append(policy)

    def check(self, ctx: ExecutionContext, tool: ToolDefinition, inputs: Dict[str, Any]) -> tuple:
        """Verifica si la ejecución está autorizada.

        Returns: (allowed: bool, reason: str)
        """
        # 1. Verificar que la herramienta está registrada
        if not ctx.has_tool(tool.name):
            return False, f"Herramienta '{tool.name}' no disponible en este contexto"

        # 2. Verificar tipo de operación vs rol
        if tool.tool_type == ToolType.SENSITIVE and ctx.actor_rol not in ("administrador",):
            return False, "Operación sensible requiere rol administrador"

        # 3. Verificar presupuesto
        if not ctx.check_budget(0, 0):
            return False, "Presupuesto de tokens o coste excedido"

        # 4. Ejecutar políticas registradas
        for policy in self._policies:
            allowed, reason = policy(ctx, tool, inputs)
            if not allowed:
                return False, reason

        # 5. Verificar permisos de la herramienta
        for perm in tool.required_permissions:
            if perm not in (ctx.scope or {}).get("permissions", []):
                return False, f"Permiso requerido no disponible: {perm}"

        return True, "Autorizado"


# Motor global de políticas
policy_engine = PolicyEngine()