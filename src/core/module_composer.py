"""Composición gobernada de módulos (C1: "juntos", sin ceder autoridad a POOLAR).

Resuelve capacidad -> módulo registrado y ejecuta vía adaptador. Solo resultados/propuestas;
cualquier efecto gobernado debe pasar por HITL/política en POOLAR. Fail-closed.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from src.core.contracts_modules import CapabilityResult, DecisionProposal, ExecutionRequest
from src.core.module_registry import ModuleRegistry


class ModuleComposer:
    def __init__(self, registry: ModuleRegistry, adapters: Dict[str, Any]):
        self.registry = registry
        self.adapters = adapters  # module_id -> adapter (manifest/execute/propose)

    def resolve(self, capability: str):
        mods = self.registry.find_by_capability(capability)
        return mods[0] if mods else None

    def execute_capability(self, req: ExecutionRequest) -> CapabilityResult:
        m = self.resolve(req.capability)
        if not m:
            return CapabilityResult(ok=False, capability=req.capability, errors=["capacidad sin módulo registrado (fail-closed)"], trace_id=req.trace_id)
        adapter = self.adapters.get(m.module_id)
        if adapter is None:
            return CapabilityResult(ok=False, capability=req.capability, module_id=m.module_id, errors=["adaptador no disponible (fail-closed)"], trace_id=req.trace_id)
        fn = getattr(adapter, "execute", None)
        if not callable(fn):
            return CapabilityResult(ok=False, capability=req.capability, module_id=m.module_id, errors=["adaptador sin execute"], trace_id=req.trace_id)
        return fn(req)

    def propose_effect(self, capability: str, action: str, context: Dict[str, Any]) -> Optional[DecisionProposal]:
        """Siempre retorna propuesta HITL; no ejecuta efectos."""
        m = self.resolve(capability)
        if not m:
            return DecisionProposal(proposal_id=f"missing-{capability}", action=action, summary="Sin módulo (fail-closed); requiere revisión", requires_human_review=True)
        adapter = self.adapters.get(m.module_id)
        if adapter and callable(getattr(adapter, "propose", None)):
            return adapter.propose(action, context)
        return DecisionProposal(proposal_id=f"p-{m.module_id}-{action}", module_id=m.module_id, action=action, summary="Propuesta compuesta; requiere HITL en POOLAR", requires_human_review=True)
