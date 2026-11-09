"""Adaptador mock genérico para módulos (no-CASE incluido) — SOLO propuesta/resultado, sin autoridad.

Demuestra el patrón repetible C1-04: módulo autoejecutable aislado (lógica local/mock) + componible vía contratos.
POOLAR conserva autoridad (HITL/tenant/ejecución). Datos sintéticos.
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


def manifest(module_id: str = "sample.module", capabilities: Optional[List[str]] = None) -> ModuleManifest:
    caps = capabilities or ["sample.analyze", "sample.propose"]
    return ModuleManifest(
        module_id=module_id,
        version="0.1.0-mock",
        name=f"Mock {module_id}",
        description="Módulo mock autoejecutable/componible (sin autoridad, sintético).",
        capabilities=caps,
        required_permissions=[],
        synthetic_safe=True,
    )


def execute(req: ExecutionRequest) -> CapabilityResult:
    """Ejecuta una capacidad en modo mock/sintético. No realiza efectos gobernados."""
    if not req.synthetic:
        return CapabilityResult(
            ok=False,
            capability=req.capability,
            module_id="sample.module",
            errors=["solo se permite modo synthetic en mock"],
            trace_id=req.trace_id,
        )
    env = EvidenceEnvelope(source="module-mock", kind="synthetic", payload={"capability": req.capability, "inputs": req.inputs}, synthetic=True)
    return CapabilityResult(
        ok=True,
        capability=req.capability,
        module_id="sample.module",
        output={"status": "mock_ok", "echo_inputs": req.inputs},
        evidence=[env],
        trace_id=req.trace_id,
    )


def propose(module_id: str, action: str, context: Dict[str, Any], evidence: Optional[List[Dict[str, Any]]] = None) -> DecisionProposal:
    envs = [EvidenceEnvelope(source=f"{module_id}-mock", kind="synthetic", payload=e, synthetic=True) for e in (evidence or [])]
    return DecisionProposal(
        proposal_id=f"mock-{module_id}-{action}",
        module_id=module_id,
        action=action,
        summary="Propuesta sintética de módulo (mock): requiere revisión humana en POOLAR",
        confidence=0.0,
        evidence=envs,
        requested_effect={"module_id": module_id, "action": action, "inputs": context.get("inputs", {})},
        requires_human_review=True,
    )
