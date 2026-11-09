"""Registro declarativo de módulos (C1-02)."""
from src.core.module_registry import ModuleRegistry
from src.core.contracts_modules import ModuleManifest


def test_registry_find_by_capability():
    r = ModuleRegistry()
    r.register(ModuleManifest(module_id="a", version="1", capabilities=["x", "y"]))
    r.register(ModuleManifest(module_id="b", version="1", capabilities=["y"]))
    assert set(m.module_id for m in r.find_by_capability("y")) == {"a", "b"}
    assert r.find_by_capability("z") == []
    assert r.validate() == []


def test_registry_catalog_readonly():
    r = ModuleRegistry()
    r.register(ModuleManifest(module_id="a", version="1", capabilities=["x"], synthetic_safe=True))
    cat = r.catalog()
    assert cat[0]["module_id"] == "a" and cat[0]["synthetic_safe"] is True
