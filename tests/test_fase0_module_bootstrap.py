"""Bootstrap opt-in de módulos demo (sintético)."""
import os
from src.core.module_bootstrap import load_demo_modules
from src.core.module_registry import ModuleRegistry, module_registry
from src.core.contracts_modules import ModuleManifest


def test_demo_modules_opt_in(monkeypatch):
    # aislar: limpiar registro global para test
    module_registry._modules.clear()
    monkeypatch.delenv("POOLAR_LOAD_DEMO_MODULES", raising=False)
    assert load_demo_modules() == 0
    monkeypatch.setenv("POOLAR_LOAD_DEMO_MODULES", "1")
    n = load_demo_modules()
    assert n >= 2
    module_registry._modules.clear()
