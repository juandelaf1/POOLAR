"""Adapter CASE mock (SOLO propuesta, SIN integración/ejecución).

Usar con datos sintéticos. POOLAR valida/decide; este adapter nunca aprueba ni ejecuta.
"""
from __future__ import annotations

from typing import Any, Dict, List

from src.core.contracts_case import DecisionProposal, EvidenceEnvelope


def propose(action: str, context: Dict[str, Any], evidence: List[Dict[str, Any]] | None = None) -> DecisionProposal:
    envs = [EvidenceEnvelope(source="case-mock", kind="synthetic", payload=e, synthetic=True) for e in (evidence or [])]
    return DecisionProposal(
        proposal_id=f"mock-{action}",
        action=action,
        summary="Propuesta sintética CASE (mock): requiere revisión humana en POOLAR",
        confidence=0.0,
        evidence=envs,
        requested_effect={"action": action, "inputs": context.get("inputs", {})},
        requires_human_review=True,
    )
