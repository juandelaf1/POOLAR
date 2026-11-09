"""Políticas declarativas por acción/tool (guardrail, fail-closed cuando aplique).

Define metadatos de gobernanza por operación. No reemplaza la evaluación de riesgo
ni la autorización de dominio; las complementa con reglas explícitas y auditables.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from src.core.agent_harness.handlers import EXPECTED_RESUMABLE_TOOLS


@dataclass(frozen=True)
class ActionPolicy:
    tool_name: str
    requires_human_review: bool = True
    resumable: bool = False
    allowed_manager_roles: Set[str] = field(default_factory=lambda: {
        "coordinador", "gestor", "responsable", "aprobador", "administrador", "admin", "owner",
    })
    max_inputs_bytes: int = 262144
    description: str = ""


_DEFAULT = ActionPolicy(tool_name="*", requires_human_review=True, resumable=False)


# Registro explícito (extender según catálogo de acciones gobernadas)
ACTION_POLICIES: Dict[str, ActionPolicy] = {
    name: ActionPolicy(
        tool_name=name,
        requires_human_review=True,
        resumable=True,
        description="Acción crítica reanudable: requiere HITL y handler determinista.",
    )
    for name in EXPECTED_RESUMABLE_TOOLS
}

# Acciones gobernadas conocidas (HITL/política según evaluación de riesgo; registro declarativo)
for _name, _res in [
    ("create_necesidad", False),
    ("create_problema_colectivo", True),
    ("create_iniciativa", True),
    ("create_decision", True),
    ("create_decision_for_initiative", True),
    ("cambiar_estado_problema_colectivo", True),
    ("accept_invitation", False),
]:
    if _name not in ACTION_POLICIES:
        ACTION_POLICIES[_name] = ActionPolicy(
            tool_name=_name, requires_human_review=_res, resumable=_res and _name in EXPECTED_RESUMABLE_TOOLS,
            description="Acción gobernada declarada.",
        )


def get_action_policy(tool_name: str) -> ActionPolicy:
    return ACTION_POLICIES.get((tool_name or "").strip(), _DEFAULT)


def validate_action_request(tool_name: str, inputs: dict, *, actor: Optional[dict] = None) -> List[str]:
    """Retorna violaciones de política (vacío = OK). Fail-closed para checks duros."""
    issues: List[str] = []
    name = (tool_name or "").strip()
    if not name:
        issues.append("tool_name requerido")
        return issues
    policy = get_action_policy(name)
    if policy.resumable and name in EXPECTED_RESUMABLE_TOOLS:
        # handler existence se valida en ejecución/registro; aquí solo consistencia declarativa
        pass
    # inputs shape validado en approvals.create; aquí política adicional
    if inputs is not None and not isinstance(inputs, dict):
        issues.append("inputs debe ser dict")
    return issues


def policy_warnings(tool_name: str) -> List[str]:
    """Advertencias declarativas (no bloqueantes) para gobernanza/observabilidad."""
    w: List[str] = []
    name = (tool_name or "").strip()
    if not name:
        return w
    if name not in ACTION_POLICIES:
        w.append(f"acción '{name}' sin política declarativa explícita")
    p = get_action_policy(name)
    if p.requires_human_review and not p.resumable and name in EXPECTED_RESUMABLE_TOOLS:
        w.append(f"acción '{name}' crítica esperada como reanudable")
    return w
