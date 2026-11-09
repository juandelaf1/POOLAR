"""Contratos propuestos POOLAR ↔ CASE (solo definición, SIN integración).

CASE propone; POOLAR valida, audita y decide. No otorgan autoridad de ejecución.
Usar con adapters/mocks y datos sintéticos hasta que Fase 0 esté cerrada y haya
decisión explícita de integración.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CaseContractVersion(str, Enum):
    v0 = "case-contract/v0"


class ActorContext(BaseModel):
    model_config = ConfigDict(extra="forbid")
    actor_type: str = Field(min_length=1)  # organizacion|individuo|sistema
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


class DecisionProposal(BaseModel):
    """Propuesta emitida por CASE; POOLAR puede aceptar, rechazar o escalar a HITL."""
    model_config = ConfigDict(extra="forbid")
    version: CaseContractVersion = CaseContractVersion.v0
    proposal_id: str = Field(min_length=1)
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
    capability: str
    output: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    trace_id: Optional[str] = None
