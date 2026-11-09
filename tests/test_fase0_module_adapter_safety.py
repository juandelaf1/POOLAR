"""Seguridad de adaptadores modulares: fail-safe en modo no sintético / entradas inválidas."""
from src.core.contracts_modules import ExecutionRequest
from src.core.adapters.module_mock import execute as mock_execute
from src.core.adapters.logistics_mock import execute as log_execute


def test_mocks_fail_safe_non_synthetic():
    r = mock_execute(ExecutionRequest(request_id="r", capability="x", synthetic=False))
    assert r.ok is False
    r = log_execute(ExecutionRequest(request_id="r", capability="logistics.estimate_route", synthetic=False))
    assert r.ok is False
