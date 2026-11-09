"""Adaptador mock no-CASE (patrón C1-04): autoejecutable aislado/componible, proposal-only/synthetic, sin autoridad."""
from src.core.contracts_modules import ExecutionRequest
from src.core.adapters.module_mock import manifest, execute, propose
from src.core.module_registry import ModuleRegistry


def test_non_case_module_mock_execute_and_propose():
    m = manifest("sample.logistics", ["logistics.route"])
    assert m.module_id != "case" and m.synthetic_safe is True
    reg = ModuleRegistry()
    reg.register(m)
    assert reg.find_by_capability("logistics.route")[0].module_id == "sample.logistics"
    res = execute(ExecutionRequest(request_id="r1", capability="logistics.route", inputs={"from": "A"}, synthetic=True))
    assert res.ok is True and res.module_id == "sample.module"
    prop = propose("sample.logistics", "plan_route", {"inputs": {"from": "A"}})
    assert prop.requires_human_review is True
    assert prop.module_id == "sample.logistics"
    assert "POOLAR" in prop.summary
