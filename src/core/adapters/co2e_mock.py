"""Adaptador mock no-CASE (CO2e/S3 seed): autoejecutable aislado + componible.

SOLO sintético/mock. No cifra opaca en producción real; aquí valores mock etiquetados.
POOLAR conserva autoridad.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from src.core.contracts_modules import CapabilityResult, DecisionProposal, EvidenceEnvelope, ExecutionRequest, ModuleManifest

MODULE_ID = "service.co2e_estimator"


def manifest() -> ModuleManifest:
    return ModuleManifest(
        module_id=MODULE_ID,
        version="0.1.0-mock",
        name="CO2e Estimator (mock)",
        description="Estimaciones CO2e sintéticas/versionadas (seed S3).",
        capabilities=["co2e.estimate", "co2e.compare"],
        required_permissions=["co2e:read"],
        synthetic_safe=True,
    )


def execute(req: ExecutionRequest) -> CapabilityResult:
    if not req.synthetic:
        return CapabilityResult(ok=False, capability=req.capability, module_id=MODULE_ID, errors=["solo synthetic"], trace_id=req.trace_id)
    if req.capability in ("co2e.estimate", "co2e.compare"):
        out = {"co2e_kg": 1.23, "unit": "kgCO2e", "methodology": "mock-v0", "uncertainty": "high-mock", "synthetic": True}
        return CapabilityResult(ok=True, capability=req.capability, module_id=MODULE_ID, output=out, evidence=[EvidenceEnvelope(source=MODULE_ID, kind="synthetic-co2e", payload=out, synthetic=True)], trace_id=req.trace_id)
    return CapabilityResult(ok=False, capability=req.capability, module_id=MODULE_ID, errors=["capacidad no soportada"], trace_id=req.trace_id)


def propose(action: str, context: Dict[str, Any]) -> DecisionProposal:
    return DecisionProposal(
        proposal_id=f"mock-{MODULE_ID}-{action}", module_id=MODULE_ID, action=action,
        summary="Estimación CO2e sintética (mock): POOLAR debe validar antes de usar en decisión",
        confidence=0.0, evidence=[], requested_effect={"module_id": MODULE_ID, "action": action, "inputs": context.get("inputs", {})},
        requires_human_review=True,
    )
