"""Contratos POOLAR↔CASE (stubs, sin integración)."""
from src.core.contracts_case import (
    CaseContractVersion,
    ActorContext,
    EvidenceEnvelope,
    DecisionProposal,
    CapabilityResult,
)


def test_case_contracts_roundtrip():
    p = DecisionProposal(
        proposal_id="p1",
        action="create_iniciativa",
        summary="propuesta",
        evidence=[EvidenceEnvelope(source="case", kind="analysis", payload={"x": 1}, synthetic=True)],
        requires_human_review=True,
    )
    assert p.version == CaseContractVersion.v0
    assert p.requires_human_review is True
    ActorContext(actor_type="sistema", roles=["case"])
    CapabilityResult(ok=True, capability="case.analyze", output={"k": "v"})
