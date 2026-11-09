"""Adaptador mock no-CASE (piloto logística rural, C1-04/L2): autoejecutable aislado + componible.

SOLO sintético/mock, sin datos reales, sin autoridad. POOLAR conserva HITL/tenant/ejecución.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.core.contracts_modules import (
    CapabilityResult,
    DecisionProposal,
    EvidenceEnvelope,
    ExecutionRequest,
    ModuleManifest,
)

MODULE_ID = "pilot.logistics_rural"


def manifest() -> ModuleManifest:
    return ModuleManifest(
        module_id=MODULE_ID,
        version="0.1.0-mock",
        name="Piloto Logística Rural (mock)",
        description="Capacidades mock de rutas/costos/participación territorial (sintético).",
        capabilities=["logistics.estimate_route", "logistics.propose_plan"],
        required_permissions=["logistics:read"],
        synthetic_safe=True,
    )


def execute(req: ExecutionRequest) -> CapabilityResult:
    if not req.synthetic:
        return CapabilityResult(ok=False, capability=req.capability, module_id=MODULE_ID, errors=["solo synthetic en mock"], trace_id=req.trace_id)
    if req.capability == "logistics.estimate_route":
        out = {"distance_km_est": 12.5, "cost_est": 100.0, "co2e_est_kg": 3.2, "methodology": "mock/synthetic"}
        return CapabilityResult(ok=True, capability=req.capability, module_id=MODULE_ID, output=out, evidence=[EvidenceEnvelope(source=MODULE_ID, kind="synthetic-estimate", payload=out, synthetic=True)], trace_id=req.trace_id)
    if req.capability == "logistics.propose_plan":
        return propose_plan(req.inputs, req.trace_id)
    return CapabilityResult(ok=False, capability=req.capability, module_id=MODULE_ID, errors=["capacidad no soportada"], trace_id=req.trace_id)


def propose_plan(inputs: Dict[str, Any], trace_id: Optional[str] = None) -> CapabilityResult:
    """Resultado/propuesta de planificación (mock) — no ejecuta efectos."""
    plan = {"stops": inputs.get("stops", []), "synthetic": True}
    return CapabilityResult(ok=True, capability="logistics.propose_plan", module_id=MODULE_ID, output={"plan": plan}, trace_id=trace_id)


def propose(action: str, context: Dict[str, Any], evidence: Optional[List[Dict[str, Any]]] = None) -> DecisionProposal:
    envs = [EvidenceEnvelope(source=MODULE_ID, kind="synthetic", payload=e, synthetic=True) for e in (evidence or [])]
    return DecisionProposal(
        proposal_id=f"mock-{MODULE_ID}-{action}",
        module_id=MODULE_ID,
        action=action,
        summary="Propuesta logística rural (mock/sintética): requiere validación y HITL en POOLAR",
        confidence=0.0,
        evidence=envs,
        requested_effect={"module_id": MODULE_ID, "action": action, "inputs": context.get("inputs", {})},
        requires_human_review=True,
    )
