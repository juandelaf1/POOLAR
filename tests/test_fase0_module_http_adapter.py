"""Plantilla/adaptador HTTP-safe para módulos (C1-04): fail-closed, inyectable, sintético."""
from src.core.contracts_modules import ExecutionRequest, ModuleManifest
from src.core.adapters.http_module_adapter import HTTPAdapterConfig, SafeHTTPModuleAdapter


def _manifest():
    return ModuleManifest(module_id="ext.sample", version="1", capabilities=["cap.x"], synthetic_safe=True)


def test_http_adapter_success_with_mock_transport():
    def transport(method, url, body, timeout):
        return 200, {"output": {"ok": True, "echo": body["capability"]}}
    a = SafeHTTPModuleAdapter(_manifest(), HTTPAdapterConfig(module_id="ext.sample", base_url="mock://local", synthetic_only=True), transport)
    r = a.execute(ExecutionRequest(request_id="r1", capability="cap.x", synthetic=True))
    assert r.ok is True and r.output["echo"] == "cap.x"


def test_http_adapter_fail_closed_no_transport():
    a = SafeHTTPModuleAdapter(_manifest(), HTTPAdapterConfig(module_id="ext.sample"), transport=None)
    r = a.execute(ExecutionRequest(request_id="r1", capability="cap.x", synthetic=True))
    assert r.ok is False and any("fail-closed" in e or "transport" in e for e in r.errors)


def test_http_adapter_blocks_non_synthetic_when_configured():
    def transport(*a, **k): return 200, {"output": {}}
    a = SafeHTTPModuleAdapter(_manifest(), HTTPAdapterConfig(module_id="ext.sample", synthetic_only=True), transport)
    r = a.execute(ExecutionRequest(request_id="r1", capability="cap.x", synthetic=False))
    assert r.ok is False and any("synthetic_only" in e for e in r.errors)


def test_http_adapter_timeout_and_http_error_fail_closed():
    def boom(method, url, body, timeout): raise TimeoutError()
    a = SafeHTTPModuleAdapter(_manifest(), HTTPAdapterConfig(module_id="ext.sample"), boom)
    r = a.execute(ExecutionRequest(request_id="r1", capability="cap.x", synthetic=True))
    assert r.ok is False and "timeout" in r.errors
    def bad(method, url, body, timeout): return 503, {"error": "x"}
    a2 = SafeHTTPModuleAdapter(_manifest(), HTTPAdapterConfig(module_id="ext.sample"), bad)
    r2 = a2.execute(ExecutionRequest(request_id="r1", capability="cap.x", synthetic=True))
    assert r2.ok is False
    assert a.propose("cap.x", {"inputs": {}}).requires_human_review is True
