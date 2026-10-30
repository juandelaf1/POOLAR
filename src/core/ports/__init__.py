"""Puertos (interfaces ABC) para la gobernanza y validación de riesgo de Poolar."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from enum import Enum

# Importar todos los puertos
from .evidence import Evidence, EvidencePort, EvidenceService, evidence_service
from .geo import GeoPort, OptimizationPort, SimpleGeoService, SimpleOptimizationService, geo_service, optimization_service
from .semantic import SemanticSearchPort, SemanticSearchResult, Embedding, LocalSemanticSearchService, semantic_search_service


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
        """Evalúa propuesta con precedencia estricta: REJECT > HUMAN_REVIEW > AUTO_APPROVE.
        Una regla posterior NUNCA puede rebajar una decisión más restrictiva."""
        # Precedencia estricta para rutas (más restrictiva = mayor valor)
        route_precedence = {
            AutomationRoute.REJECT: 3,
            AutomationRoute.HUMAN_REVIEW: 2,
            AutomationRoute.AUTO_APPROVE: 1,
        }
        # Precedencia para riesgo (más restrictivo = mayor valor)
        risk_precedence = {
            RiskLevel.CRITICAL: 4,
            RiskLevel.HIGH: 3,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 1,
        }
        route = AutomationRoute.AUTO_APPROVE
        risk_level = RiskLevel.LOW
        reasons = []

        for rule in self.rules:
            result = rule(proposal, context, risk_level)
            result_route = result.get("route")
            if isinstance(result_route, str):
                result_route = AutomationRoute(result_route)
            result_risk = result.get("risk_level")
            if isinstance(result_risk, str):
                result_risk = RiskLevel(result_risk)
            # Precedencia: nunca rebajar la restricción actual
            if result_route is not None and route_precedence[result_route] > route_precedence[route]:
                route = result_route
            if result_risk is not None and risk_precedence[result_risk] > risk_precedence[risk_level]:
                risk_level = result_risk
            reasons.extend(result.get("reasons", []))

        # Garantía final: datos reales o desconocidos nunca permiten AUTO_APPROVE
        origen = proposal.get("origen_datos")
        if origen is None or origen == "" or origen not in ("synthetic_pilot",):
            if route == AutomationRoute.AUTO_APPROVE:
                route = AutomationRoute.HUMAN_REVIEW
                reasons.append("Origen desconocido o no sintético requiere revisión humana")
            if risk_level == RiskLevel.LOW:
                risk_level = RiskLevel.MEDIUM
                reasons.append("Origen desconocido eleva riesgo mínimo")

        return {
            "route": route.value,
            "risk_level": risk_level.value,
            "reasons": reasons,
            "approved": route == AutomationRoute.AUTO_APPROVE,
            "requires_human_review": route == AutomationRoute.HUMAN_REVIEW,
            "rejected": route == AutomationRoute.REJECT,
        }

    def _rule_synthetic_data(self, proposal, context, risk_level):
        """Regla: datos sintéticos tienen menor riesgo; desconocidos se rechazan."""
        origen = proposal.get("origen_datos")
        if origen is None or origen == "" or origen not in ("synthetic_pilot", "real_pilot"):
            return {"risk_level": RiskLevel.HIGH, "route": AutomationRoute.REJECT, "reasons": ["origen de datos ausente o desconocido; no se permite aprobación automática"]}
        if origen == "synthetic_pilot":
            return {"risk_level": risk_level, "route": AutomationRoute.AUTO_APPROVE, "reasons": ["datos sintéticos etiquetados"]}
        # real_pilot sin consentimiento formal verificable
        return {"risk_level": RiskLevel.MEDIUM, "route": AutomationRoute.HUMAN_REVIEW, "reasons": ["datos reales requieren consentimiento formal verificable"]}

    def _rule_risk_level(self, proposal, context, risk_level):
        """Regla: operaciones sensibles requieren revisión humana."""
        action = proposal.get("action", "")
        sensitive_actions = {"change_state", "create_decision", "accept_invitation", "export_data"}
        if action in sensitive_actions:
            if risk_level == RiskLevel.LOW:
                return {"risk_level": RiskLevel.MEDIUM, "route": AutomationRoute.HUMAN_REVIEW, "reasons": [f"acción sensible: {action}"]}
        return {"risk_level": risk_level, "route": AutomationRoute.AUTO_APPROVE, "reasons": []}

    def _rule_authority(self, proposal, context, risk_level):
        """Regla: el actor debe tener autoridad explícita para la acción."""
        actor_type = context.get("actor_type", "")
        actor_rol = context.get("actor_rol", "")
        action = proposal.get("action", "")
        # Sin identidad o contexto suficiente: rechazo seguro
        if not actor_type or not actor_rol or actor_type == "desconocido":
            return {"risk_level": RiskLevel.HIGH, "route": AutomationRoute.REJECT, "reasons": ["Identidad o contexto insuficiente para autorización"]}
        # Datos reales sin consentimiento formal verificable: revisión humana
        origen = proposal.get("origen_datos", "synthetic_pilot")
        if origen != "synthetic_pilot":
            # Datos reales requieren verificación; nunca AUTO_APPROVE
            if actor_rol == "administrador" and actor_type == "organizacion":
                return {"risk_level": RiskLevel.MEDIUM, "route": AutomationRoute.HUMAN_REVIEW, "reasons": ["Datos reales requieren revisión humana (actor autorizado pero sin consentimiento verificado)"]}
            return {"risk_level": RiskLevel.HIGH, "route": AutomationRoute.REJECT, "reasons": ["Actor sin autoridad para datos reales sin consentimiento formal"]}
        # Actor organizativo con rol administrador: autorización pero sujeto a otras reglas
        if actor_type == "organizacion" and actor_rol == "administrador":
            return {"risk_level": risk_level, "route": AutomationRoute.AUTO_APPROVE, "reasons": ["Actor autorizado (admin org)"]}
        # Actor individual con rol definido: autorización pero sujeto a otras reglas
        if actor_type == "individuo" and actor_rol in ("individuo", "responsable"):
            return {"risk_level": risk_level, "route": AutomationRoute.AUTO_APPROVE, "reasons": ["Actor autorizado (individuo)"]}
        # Actor sin autoridad reconocida
        return {"risk_level": RiskLevel.HIGH, "route": AutomationRoute.REJECT, "reasons": ["Actor sin autoridad reconocida para la acción"]}

    def _rule_invitation_consent(self, proposal, context, risk_level):
        """Regla: las invitaciones requieren consentimiento del destinatario."""
        action = proposal.get("action", "")
        if action == "accept_invitation":
            # Solo el destinatario autenticado puede aceptar
            if not context.get("is_destinatario", False):
                return {"risk_level": RiskLevel.HIGH, "route": AutomationRoute.REJECT, "reasons": ["no es el destinatario de la invitación"]}
        return {"risk_level": risk_level, "route": AutomationRoute.AUTO_APPROVE, "reasons": []}

    def check_authority(self, actor_id: int, actor_type: str, action: str) -> bool:
        """Verifica si el actor tiene autoridad explícita para la acción."""
        if not actor_id or not actor_type:
            return False
        # Actor desconocido o sin rol definido: no autorizado
        if actor_type not in ("individuo", "organizacion"):
            return False
        # Para acciones sensibles, se requiere verificación adicional (no solo tipo)
        # Esta verificación básica garantiza que el actor exista y tenga tipo reconocido
        return True


# Instancia global
automation_evaluator = AutomationEvaluator()