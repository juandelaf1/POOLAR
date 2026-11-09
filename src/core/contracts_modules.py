"""Contratos modulares genéricos POOLAR (versión 0).

Aplica a CASE y a cualquier otro módulo/proyecto integrado por capacidad.
Los módulos retornan propuestas/resultados; **POOLAR conserva autoridad** (HITL, tenant, permisos, ejecución).
Sin integración externa ni datos reales por defecto; usar mocks/sintético hasta F0-13 y puertas explícitas.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ModuleContractVersion(str, Enum):
    v0 = "module-contract/v0"


# Compatibilidad histórica
CaseContractVersion = ModuleContractVersion


class ModuleManifest(BaseModel):
    """Declaración de un módulo autoejecutable/componible (sin ejecución implícita)."""
    model_config = ConfigDict(extra="forbid")
    module_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    name: str = ""
    description: str = ""
    capabilities: List[str] = Field(default_factory=list)
    required_permissions: List[str] = Field(default_factory=list)
    contract_version: ModuleContractVersion = ModuleContractVersion.v0
    synthetic_safe: bool = True


class ActorContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    actor_type: str = Field(min_length=1)  # organizacion|individuo|sistema|modulo
    actor_id: Optional[str] = None
    tenant_id: Optional[str] = None
    roles: List[str] = Field(default_factory=list)
    trace_id: Optional[str] = None


class EvidenceEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    evidence_id: Optional[str] = None
    source: str = Field(min_length=1)
    kind: str = Field(min_length=1)
    payload: Dict[str, Any] = Field(default_factory=dict)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    synthetic: bool = True


class ExecutionRequest(BaseModel):
    """Solicitud gobernada a un módulo (POOLAR -> módulo). Sin autoridad de ejecución en el módulo."""
    model_config = ConfigDict(extra="forbid")
    request_id: str = Field(min_length=1)
    capability: str = Field(min_length=1)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    actor: Optional[ActorContext] = None
    trace_id: Optional[str] = None
    synthetic: bool = True


class DecisionProposal(BaseModel):
    """Propuesta emitida por un módulo; POOLAR puede aceptar, rechazar o escalar a HITL."""
    model_config = ConfigDict(extra="forbid")
    version: ModuleContractVersion = ModuleContractVersion.v0
    proposal_id: str = Field(min_length=1)
    module_id: Optional[str] = None
    action: str = Field(min_length=1)
    summary: str = ""
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    evidence: List[EvidenceEnvelope] = Field(default_factory=list)
    requested_effect: Dict[str, Any] = Field(default_factory=dict)
    requires_human_review: bool = True
    created_at: Optional[datetime] = None


class CapabilityResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    ok: bool
    capability: str = Field(min_length=1)
    module_id: Optional[str] = None
    output: Dict[str, Any] = Field(default_factory=dict)
    evidence: List[EvidenceEnvelope] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    trace_id: Optional[str] = None


class ApprovalRecord(BaseModel):
    """Referencia contractual (no sustituye el modelo operacional de POOLAR)."""
    model_config = ConfigDict(extra="forbid")
    approval_id: str = Field(min_length=1)
    proposal_id: Optional[str] = None
    status: str = Field(min_length=1)
    decided_by: Optional[str] = None
    decided_at: Optional[datetime] = None
    trace_id: Optional[str] = None
