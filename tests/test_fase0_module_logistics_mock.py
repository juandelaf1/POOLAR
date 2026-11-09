"""Módulo no-CASE (logística rural, mock/sintético): autoejecutable aislado + componible (C1-04/L2 seed)."""
from src.core.contracts_modules import ExecutionRequest
from src.core.adapters.logistics_mock import manifest, execute, propose
from src.core.module_registry import ModuleRegistry


def test_logistics_mock_module_pattern():
    m = manifest()
    assert m.module_id == "pilot.logistics_rural"
    assert m.synthetic_safe is True
    reg = ModuleRegistry()
    reg.register(m)
    assert reg.find_by_capability("logistics.estimate_route")
    res = execute(ExecutionRequest(request_id="r1", capability="logistics.estimate_route", inputs={"origin": "A"}, synthetic=True))
    assert res.ok is True and res.output.get("co2e_est_kg") == 3.2
    p = propose("plan", {"inputs": {"stops": ["A", "B"]}})
    assert p.requires_human_review is True and p.module_id == "pilot.logistics_rural"
