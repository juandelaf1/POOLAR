"""Composición de múltiples módulos (CASE + no-CASE) vía contratos, sin ceder autoridad."""
from src.core.contracts_modules import ExecutionRequest
from src.core.module_registry import ModuleRegistry
from src.core.module_composer import ModuleComposer
from src.core.adapters import logistics_mock, co2e_mock, module_mock


class _FnAdapter:
    def __init__(self, mod):
        self.mod = mod
    def execute(self, req):
        return self.mod.execute(req)
    def propose(self, action, context, evidence=None):
        try:
            return self.mod.propose(action, context, evidence=evidence)
        except TypeError:
            return self.mod.propose(action, context)


def test_composer_resolves_and_executes_multiple_modules():
    reg = ModuleRegistry()
    reg.register(logistics_mock.manifest())
    reg.register(co2e_mock.manifest())
    reg.register(module_mock.manifest("sample.ext", ["ext.cap"]))
    comp = ModuleComposer(reg, {
        logistics_mock.MODULE_ID: _FnAdapter(logistics_mock),
        co2e_mock.MODULE_ID: _FnAdapter(co2e_mock),
        "sample.ext": _FnAdapter(module_mock),
    })
    r = comp.execute_capability(ExecutionRequest(request_id="1", capability="logistics.estimate_route", synthetic=True))
    assert r.ok and r.module_id == logistics_mock.MODULE_ID
    r = comp.execute_capability(ExecutionRequest(request_id="2", capability="co2e.estimate", synthetic=True))
    assert r.ok and r.module_id == co2e_mock.MODULE_ID
    r = comp.execute_capability(ExecutionRequest(request_id="3", capability="unknown.cap", synthetic=True))
    assert r.ok is False and "fail-closed" in (r.errors[0] if r.errors else "")
    p = comp.propose_effect("co2e.estimate", "apply", {"inputs": {}})
    assert p is not None and p.requires_human_review is True
