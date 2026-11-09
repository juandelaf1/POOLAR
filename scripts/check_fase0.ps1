# Verificación reproducible Fase 0 (Poolar) - SQLite
# Uso: powershell -ExecutionPolicy Bypass -File scripts\check_fase0.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "== compileall =="
python -m compileall -q src tests

Write-Host "== Fase 0 / gobernanza =="
Remove-Item .pytest_poolar.db,.pytest_poolar.db-shm,.pytest_poolar.db-wal -ErrorAction SilentlyContinue
python -m pytest tests/test_fase0_action_policies.py tests/test_fase0_contracts_case.py tests/test_fase0_case_adapter_mock.py tests/test_fase0_security.py tests/test_fase0_harness_guardrails.py tests/test_fase0_role_matrix.py tests/test_fase0_approvals_scope.py tests/test_fase0_decision_failclosed.py tests/test_fase0_resumption_handlers.py tests/test_fase0_handlers_registry.py tests/test_governance_regresion.py tests/test_p03_http_governance.py tests/test_p04_resumption.py tests/test_fase0_medallion_export.py tests/test_fase0_medallion_duckdb.py tests/test_e2e_flujo_core_capacidad.py tests/test_fase0_approvals_http_matrix.py -q --rootdir=.

Write-Host "== suite completa (SQLite) =="
python -m pytest -q --rootdir=.

Write-Host "OK. PG real: configurar POOLAR_TEST_POSTGRES_URL localmente y ejecutar alembic upgrade head + test_fase0_p04_concurrency_pg.py (no compartir secretos)."
