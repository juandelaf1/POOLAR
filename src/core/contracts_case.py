"""Compatibilidad: contratos CASE = caso de contratos modulares genéricos.

Preferir `src.core.contracts_modules` para integraciones nuevas (CASE u otros módulos).
POOLAR conserva autoridad; módulos solo proponen/resultan.
"""
from src.core.contracts_modules import (  # noqa: F401
    ModuleContractVersion as CaseContractVersion,
    ModuleManifest,
    ActorContext,
    EvidenceEnvelope,
    ExecutionRequest,
    DecisionProposal,
    CapabilityResult,
    ApprovalRecord,
)

__all__ = [
    "CaseContractVersion",
    "ModuleManifest",
    "ActorContext",
    "EvidenceEnvelope",
    "ExecutionRequest",
    "DecisionProposal",
    "CapabilityResult",
    "ApprovalRecord",
]
