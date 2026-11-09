"""Registro declarativo de módulos/capacidades (sin ejecución implícita).

POOLAR selecciona por capacidad; los módulos son autoejecutables aislados y se componen vía adaptadores/contratos.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from src.core.contracts_modules import ModuleManifest


class ModuleRegistry:
    def __init__(self) -> None:
        self._modules: Dict[str, ModuleManifest] = {}

    def register(self, manifest: ModuleManifest) -> None:
        self._modules[manifest.module_id] = manifest

    def get(self, module_id: str) -> Optional[ModuleManifest]:
        return self._modules.get(module_id)

    def list(self) -> List[ModuleManifest]:
        return list(self._modules.values())

    def find_by_capability(self, capability: str) -> List[ModuleManifest]:
        cap = (capability or "").strip()
        return [m for m in self._modules.values() if cap in (m.capabilities or [])]

    def validate(self) -> List[str]:
        issues: List[str] = []
        seen = set()
        for m in self._modules.values():
            if m.module_id in seen:
                issues.append(f"module_id duplicado: {m.module_id}")
            seen.add(m.module_id)
            if not m.capabilities:
                issues.append(f"módulo sin capacidades: {m.module_id}")
        return issues

    def catalog(self) -> List[dict]:
        """Catálogo read-only para descubrimiento (sin ejecución)."""
        return [m.model_dump() for m in self.list()]


module_registry = ModuleRegistry()
