"""Registro opt-in de módulos mock/demo (sintético). Nunca en producción con datos reales sin revisión."""
from __future__ import annotations
import os

from src.core.module_registry import module_registry
from src.core.adapters import logistics_mock, co2e_mock, module_mock


def load_demo_modules() -> int:
    if os.getenv("POOLAR_LOAD_DEMO_MODULES", "").lower() not in ("1", "true", "yes"):
        return 0
    for m in [logistics_mock.manifest(), co2e_mock.manifest(), module_mock.manifest()]:
        if module_registry.get(m.module_id) is None:
            module_registry.register(m)
    return len(module_registry.list())
