"""Sistema de aprobaciones humanas para el Agent Harness de Poolar."""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = "pendiente"
    APPROVED = "aprobada"
    REJECTED = "rechazada"
    EXPIRED = "caducada"


@dataclass
class ApprovalRequest:
    """Solicitud de aprobación para una operación sensible."""
    approval_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str = ""
    tool_name: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    proposed_by: Optional[int] = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    reason: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[int] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: str = ""


class ApprovalManager:
    """Gestor de aprobaciones humanas."""

    def __init__(self):
        self._approvals: Dict[str, ApprovalRequest] = {}

    def create(self, execution_id: str, tool_name: str, inputs: Dict[str, Any], proposed_by: Optional[int] = None) -> ApprovalRequest:
        req = ApprovalRequest(
            execution_id=execution_id,
            tool_name=tool_name,
            inputs=inputs,
            proposed_by=proposed_by,
        )
        self._approvals[req.approval_id] = req
        return req

    def approve(self, approval_id: str, approved_by: int) -> ApprovalRequest:
        req = self._approvals.get(approval_id)
        if req is None:
            raise ValueError("Aprobación no encontrada")
        if req.status != ApprovalStatus.PENDING:
            raise ValueError(f"Aprobación en estado '{req.status}', no se puede aprobar")
        req.status = ApprovalStatus.APPROVED
        req.approved_by = approved_by
        req.approved_at = datetime.utcnow()
        return req

    def reject(self, approval_id: str, rejected_by: int, reason: str = "") -> ApprovalRequest:
        req = self._approvals.get(approval_id)
        if req is None:
            raise ValueError("Aprobación no encontrada")
        if req.status != ApprovalStatus.PENDING:
            raise ValueError(f"Aprobación en estado '{req.status}', no se puede rechazar")
        req.status = ApprovalStatus.REJECTED
        req.rejected_by = rejected_by
        req.rejected_at = datetime.utcnow()
        req.rejection_reason = reason
        return req

    def get(self, approval_id: str) -> Optional[ApprovalRequest]:
        return self._approvals.get(approval_id)

    def list_pending(self) -> List[ApprovalRequest]:
        return [a for a in self._approvals.values() if a.status == ApprovalStatus.PENDING]

    def is_expired(self, approval_id: str) -> bool:
        req = self._approvals.get(approval_id)
        if req is None or req.expires_at is None:
            return False
        return datetime.utcnow() > req.expires_at


# Gestor global de aprobaciones
approval_manager = ApprovalManager()