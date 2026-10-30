"""Puertos (interfaces ABC) para la gobernanza y validación de riesgo de Poolar."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AutomationRoute(str, Enum):
    AUTO_APPROVE = "auto_approve"
    HUMAN_REVIEW = "human_review"
    REJECT = "reject"


class DecisionPort(ABC):
    """Puerto para validación y gobernanza de decisiones."""

    @abstractmethod
    def evaluate(self, proposal: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa una propuesta y retorna ruta, riesgo y justificación."""
        ...

    @abstractmethod
    def check_authority(self, actor_id: int, actor_type: str, action: str) -> bool:
        """Verifica si el actor tiene autoridad para la acción."""
        ...


class AutomationEvaluator:
    """Evaluador de reglas para determinar la ruta de automatización.

    Reglas:
    - Bajo riesgo + datos sintéticos + actor autorizado → AUTO_APPROVE
    - Riesgo medio o datos reales → HUMAN_REVIEW
    - Alto riesgo o falta de autorización → REJECT
    """

    def __init__(self):
        self.rules = [
            self._rule_synthetic_data,
            self._rule_risk_level,
            self._rule_authority,
            self._rule_invitation_consent,
        ]

    def evaluate(self, proposal: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evalúa una propuesta y retorna ruta, riesgo y justificación."""
        risk_level = RiskLevel.LOW
        route = AutomationRoute.AUTO_APPROVE
        reasons = []

        for rule in self.rules:
            result = rule(proposal, context, risk_level)
            if result["risk_level"] != risk_level:
                risk_level = result["risk_level"]
            if result["route"] != route:
                route = result["route"]
            reasons.extend(result.get("reasons", []))

        return {
            "route": route.value,
            "risk_level": risk_level.value,
            "reasons": reasons,
            "approved": route == AutomationRoute.AUTO_APPROVE,
            "requires_human_review": route == AutomationRoute.HUMAN_REVIEW,
            "rejected": route == AutomationRoute.REJECT,
        }

    def _rule_synthetic_data(self, proposal, context, risk_level):
        """Regla: datos sintéticos tienen menor riesgo."""
        origen = proposal.get("origen_datos", "synthetic_pilot")
        if origen == "synthetic_pilot":
            return {"risk_level": risk_level, "route": AutomationRoute.AUTO_APPROVE, "reasons": ["datos sintéticos"]}
        return {"risk_level": RiskLevel.MEDIUM, "route": AutomationRoute.HUMAN_REVIEW, "reasons": ["datos reales requieren consentimiento"]}

    def _rule_risk_level(self, proposal, context, risk_level):
        """Regla: operaciones sensibles requieren revisión humana."""
        action = proposal.get("action", "")
        sensitive_actions = {"change_state", "create_decision", "accept_invitation", "export_data"}
        if action in sensitive_actions:
            if risk_level == RiskLevel.LOW:
                return {"risk_level": RiskLevel.MEDIUM, "route": AutomationRoute.HUMAN_REVIEW, "reasons": [f"acción sensible: {action}"]}
        return {"risk_level": risk_level, "route": AutomationRoute.AUTO_APPROVE, "reasons": []}

    def _rule_authority(self, proposal, context, risk_level):
        """Regla: el actor debe tener autoridad para la acción."""
        actor_type = context.get("actor_type", "persona")
        actor_rol = context.get("actor_rol", "individuo")
        action = proposal.get("action", "")
        # Organizaciones con rol administrador tienen mayor autoridad
        if actor_type == "organizacion" and actor_rol == "administrador":
            return {"risk_level": risk_level, "route": AutomationRoute.AUTO_APPROVE, "reasons": ["actor autorizado (admin)"]}
        # Personas individuales tienen autoridad sobre sus propios recursos
        if actor_type == "individuo":
            return {"risk_level": risk_level, "route": AutomationRoute.AUTO_APPROVE, "reasons": ["actor autorizado (individuo)"]}
        return {"risk_level": RiskLevel.HIGH, "route": AutomationRoute.REJECT, "reasons": ["actor sin autoridad"]}

    def _rule_invitation_consent(self, proposal, context, risk_level):
        """Regla: las invitaciones requieren consentimiento del destinatario."""
        action = proposal.get("action", "")
        if action == "accept_invitation":
            # Solo el destinatario autenticado puede aceptar
            if not context.get("is_destinatario", False):
                return {"risk_level": RiskLevel.HIGH, "route": AutomationRoute.REJECT, "reasons": ["no es el destinatario de la invitación"]}
        return {"risk_level": risk_level, "route": AutomationRoute.AUTO_APPROVE, "reasons": []}

    def check_authority(self, actor_id: int, actor_type: str, action: str) -> bool:
        """Verifica si el actor tiene autoridad para la acción."""
        if actor_type == "individuo":
            return True  # Individuos tienen autoridad sobre sus propios recursos
        if actor_type == "organizacion":
            return True  # Organizaciones tienen autoridad sobre sus recursos
        return False


# Instancia global
automation_evaluator = AutomationEvaluator()