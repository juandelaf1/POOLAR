"""Módulo no-CASE CO2e (mock/sintético, S3 seed)."""
from src.core.contracts_modules import ExecutionRequest
from src.core.adapters.co2e_mock import manifest, execute, propose


def test_co2e_mock_synthetic_and_proposal():
    m = manifest()
    assert m.synthetic_safe and "co2e.estimate" in m.capabilities
    r = execute(ExecutionRequest(request_id="r", capability="co2e.estimate", synthetic=True, inputs={"km": 10}))
    assert r.ok and r.output["synthetic"] is True and r.output["methodology"] == "mock-v0"
    p = propose("estimate", {"inputs": {}})
    assert p.requires_human_review and p.module_id == "service.co2e_estimator"
