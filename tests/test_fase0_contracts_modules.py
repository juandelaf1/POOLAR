"""Contratos modulares genéricos (C1-01/C1-04 base, sin integración)."""
from src.core.contracts_modules import (
    ModuleContractVersion,
    ModuleManifest,
    ActorContext,
    ExecutionRequest,
    EvidenceEnvelope,
    DecisionProposal,
    CapabilityResult,
    ApprovalRecord,
)


def test_generic_module_contracts():
    m = ModuleManifest(module_id="m1", version="1.0.0", capabilities=["cap.a"])
    assert m.contract_version == ModuleContractVersion.v0
    req = ExecutionRequest(request_id="r1", capability="cap.a", inputs={"x": 1}, synthetic=True)
    res = CapabilityResult(ok=True, capability="cap.a", module_id="m1", output={"y": 2})
    p = DecisionProposal(proposal_id="p1", module_id="m1", action="cap.a", requires_human_review=True)
    assert p.requires_human_review is True
    ActorContext(actor_type="organizacion", tenant_id="t1")
    ApprovalRecord(approval_id="a1", status="pendiente")
    assert req.synthetic is True and res.ok is True
