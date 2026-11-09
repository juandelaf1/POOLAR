"""Adaptador HTTP-safe genérico para módulos (C1-04, plantilla).

- Autoejecutable/componible: inyectable (transport/mock) para tests y local.
- Fail-closed: timeouts/errores/shape inválido => CapabilityResult(ok=False), sin excepción no controlada al llamador.
- Sin autoridad: solo lee/propone según contrato; POOLAR gobierna HITL/ejecución.
- Por defecto sintético/mock; no integra endpoints reales sin configuración explícita.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple

from src.core.contracts_modules import CapabilityResult, DecisionProposal, EvidenceEnvelope, ExecutionRequest, ModuleManifest

# transport(method, url, json_body, timeout_s) -> (status_code, json_dict | None)
Transport = Callable[[str, str, Optional[Dict[str, Any]], float], Tuple[int, Optional[Dict[str, Any]]]]


@dataclass
class HTTPAdapterConfig:
    module_id: str
    base_url: str = ""
    timeout_s: float = 5.0
    synthetic_only: bool = True  # fail-closed: bloquea llamadas no sintéticas/reales por defecto
    capability_paths: Dict[str, str] = None  # capability -> path

    def path_for(self, capability: str) -> str:
        m = self.capability_paths or {}
        return m.get(capability, f"/capabilities/{capability}")


class SafeHTTPModuleAdapter:
    def __init__(self, manifest: ModuleManifest, config: HTTPAdapterConfig, transport: Optional[Transport] = None):
        self._manifest = manifest
        self._config = config
        self._transport = transport  # si None y no synthetic_only, execute falla (fail-closed)

    def manifest(self) -> ModuleManifest:
        return self._manifest

    def execute(self, req: ExecutionRequest) -> CapabilityResult:
        try:
            if req.capability not in (self._manifest.capabilities or []):
                return CapabilityResult(ok=False, capability=req.capability, module_id=self._config.module_id, errors=["capacidad no declarada"], trace_id=req.trace_id)
            if self._config.synthetic_only and not req.synthetic:
                return CapabilityResult(ok=False, capability=req.capability, module_id=self._config.module_id, errors=["synthetic_only: modo no sintético bloqueado"], trace_id=req.trace_id)
            if self._transport is None:
                return CapabilityResult(ok=False, capability=req.capability, module_id=self._config.module_id, errors=["transport no configurado (fail-closed)"], trace_id=req.trace_id)
            url = (self._config.base_url.rstrip("/") + self._config.path_for(req.capability)) if self._config.base_url else self._config.path_for(req.capability)
            status, body = self._transport("POST", url, req.model_dump(mode="json"), self._config.timeout_s)
            if status >= 400:
                return CapabilityResult(ok=False, capability=req.capability, module_id=self._config.module_id, errors=[f"http {status}"], output=body or {}, trace_id=req.trace_id)
            if not isinstance(body, dict):
                return CapabilityResult(ok=False, capability=req.capability, module_id=self._config.module_id, errors=["respuesta inválida"], trace_id=req.trace_id)
            ev = [EvidenceEnvelope(source=self._config.module_id, kind="http-adapter", payload={"url": url, "status": status}, synthetic=bool(req.synthetic))]
            return CapabilityResult(ok=True, capability=req.capability, module_id=self._config.module_id, output=body.get("output", body), evidence=ev, trace_id=req.trace_id)
        except TimeoutError:
            return CapabilityResult(ok=False, capability=req.capability, module_id=self._config.module_id, errors=["timeout"], trace_id=req.trace_id)
        except Exception as e:
            return CapabilityResult(ok=False, capability=req.capability, module_id=self._config.module_id, errors=[f"adapter_error:{type(e).__name__}"], trace_id=req.trace_id)

    def propose(self, action: str, context: Dict[str, Any]) -> DecisionProposal:
        return DecisionProposal(
            proposal_id=f"http-{self._config.module_id}-{action}", module_id=self._config.module_id, action=action,
            summary="Propuesta vía adaptador HTTP-safe (módulo externo/proxy): requiere HITL en POOLAR",
            requested_effect={"module_id": self._config.module_id, "action": action, "inputs": context.get("inputs", {})},
            requires_human_review=True,
        )
