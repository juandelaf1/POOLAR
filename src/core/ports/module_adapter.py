"""Puerto/protocolo para adaptadores de módulos (C1, sin autoridad en módulo)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from src.core.contracts_modules import CapabilityResult, DecisionProposal, ExecutionRequest, ModuleManifest


class ModuleAdapterPort(ABC):
    """Interfaz: módulos autoejecutables aislados, componibles vía POOLAR. No ejecutan efectos gobernados."""

    @abstractmethod
    def manifest(self) -> ModuleManifest:
        raise NotImplementedError

    @abstractmethod
    def execute(self, req: ExecutionRequest) -> CapabilityResult:
        raise NotImplementedError

    def propose(self, action: str, context: Dict[str, Any], evidence: Optional[list] = None) -> DecisionProposal:
        """Opcional: propuesta HITL (por defecto requiere revisión)."""
        return DecisionProposal(proposal_id=f"p-{action}", action=action, summary="propuesta", requires_human_review=True)
