"""Sistema de aprobaciones humanas persistido para Poolar.

Cada solicitud vive en PostgreSQL (`approval_requests`). No hay diccionario
como fuente de verdad. Una instancia del gestor debe poder recuperar lo
creado por otra instancia (persistencia real).
"""
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from src.core.models import ApprovalRequest as ApprovalRequestDB


class ApprovalStatus(str):
    PENDING = "pendiente"
    APPROVED = "aprobada"
    REJECTED = "rechazada"
    EXPIRED = "caducada"


class ApprovalRequest:
    """DTO de dominio para una solicitud de aprobación."""
    def __init__(
        self,
        approval_id: str,
        execution_id: str = "",
        tool_name: str = "",
        inputs: Optional[Dict[str, Any]] = None,
        proposed_by: Optional[int] = None,
        status: str = ApprovalStatus.PENDING,
        reason: str = "",
        approved_by: Optional[int] = None,
        approved_at: Optional[datetime] = None,
        rejected_by: Optional[int] = None,
        rejected_at: Optional[datetime] = None,
        rejection_reason: str = "",
        expires_at: Optional[datetime] = None,
    ):
        self.approval_id = approval_id
        self.execution_id = execution_id
        self.tool_name = tool_name
        self.inputs = inputs or {}
        self.proposed_by = proposed_by
        self.status = status
        self.reason = reason
        self.approved_by = approved_by
        self.approved_at = approved_at
        self.rejected_by = rejected_by
        self.rejected_at = rejected_at
        self.rejection_reason = rejection_reason
        self.expires_at = expires_at
        self.created_at = datetime.utcnow()


class ApprovalManager:
    """Gestor persistente de aprobaciones contra PostgreSQL."""

    def __init__(self, session_factory=None):
        # session_factory opcional para inyección; por defecto usa SessionLocal
        self.session_factory = session_factory

    def _session(self) -> Session:
        if self.session_factory is not None:
            return self.session_factory()
        from src.core.database import SessionLocal
        return SessionLocal()

    def create(
        self,
        execution_id: str,
        tool_name: str,
        inputs: Dict[str, Any],
        proposed_by: Optional[int] = None,
        reason: str = "",
    ) -> ApprovalRequest:
        approval_id = str(__import__("uuid").uuid4())
        req_db = ApprovalRequestDB(
            approval_id=approval_id,
            execution_id=execution_id,
            tool_name=tool_name,
            inputs=json.dumps(inputs, default=str),
            proposed_by=proposed_by,
            status=ApprovalStatus.PENDING,
            reason=reason,
        )
        with self._session() as session:
            session.add(req_db)
            session.commit()
            session.refresh(req_db)
        return ApprovalRequest(
            approval_id=req_db.approval_id,
            execution_id=req_db.execution_id,
            tool_name=req_db.tool_name,
            inputs=inputs,
            proposed_by=req_db.proposed_by,
            status=req_db.status,
            reason=req_db.reason,
            expires_at=req_db.expires_at,
        )

    def get(self, approval_id: str) -> Optional[ApprovalRequest]:
        with self._session() as session:
            req_db = session.query(ApprovalRequestDB).filter(
                ApprovalRequestDB.approval_id == approval_id
            ).first()
            if req_db is None:
                return None
            return ApprovalRequest(
                approval_id=req_db.approval_id,
                execution_id=req_db.execution_id,
                tool_name=req_db.tool_name,
                inputs=json.loads(req_db.inputs) if req_db.inputs else {},
                proposed_by=req_db.proposed_by,
                status=req_db.status,
                reason=req_db.reason,
                approved_by=req_db.approved_by,
                approved_at=req_db.approved_at,
                rejected_by=req_db.rejected_by,
                rejected_at=req_db.rejected_at,
                rejection_reason=req_db.rejection_reason,
                expires_at=req_db.expires_at,
            )

    def list_pending(self) -> List[ApprovalRequest]:
        with self._session() as session:
            results = session.query(ApprovalRequestDB).filter(
                ApprovalRequestDB.status == ApprovalStatus.PENDING
            ).all()
            return [
                ApprovalRequest(
                    approval_id=r.approval_id,
                    execution_id=r.execution_id,
                    tool_name=r.tool_name,
                    inputs=json.loads(r.inputs) if r.inputs else {},
                    proposed_by=r.proposed_by,
                    status=r.status,
                    reason=r.reason,
                    approved_by=r.approved_by,
                    approved_at=r.approved_at,
                    rejected_by=r.rejected_by,
                    rejected_at=r.rejected_at,
                    rejection_reason=r.rejection_reason,
                    expires_at=r.expires_at,
                )
                for r in results
            ]

    def approve(self, approval_id: str, approved_by: int) -> ApprovalRequest:
        with self._session() as session:
            req_db = session.query(ApprovalRequestDB).filter(
                ApprovalRequestDB.approval_id == approval_id
            ).with_for_update().first()
            if req_db is None:
                raise ValueError("Aprobación no encontrada")
            if req_db.status != ApprovalStatus.PENDING:
                raise ValueError(
                    f"Aprobación en estado '{req_db.status}', no se puede aprobar"
                )
            if req_db.expires_at is not None and datetime.utcnow() > req_db.expires_at:
                raise ValueError("Aprobación caducada; no se puede aprobar")
            req_db.status = ApprovalStatus.APPROVED
            req_db.approved_by = approved_by
            req_db.approved_at = datetime.utcnow()
            session.commit()
            session.refresh(req_db)
        return ApprovalRequest(
            approval_id=req_db.approval_id,
            execution_id=req_db.execution_id,
            tool_name=req_db.tool_name,
            inputs=json.loads(req_db.inputs) if req_db.inputs else {},
            proposed_by=req_db.proposed_by,
            status=req_db.status,
            reason=req_db.reason,
            approved_by=req_db.approved_by,
            approved_at=req_db.approved_at,
            rejected_by=req_db.rejected_by,
            rejected_at=req_db.rejected_at,
            rejection_reason=req_db.rejection_reason,
            expires_at=req_db.expires_at,
        )

    def reject(self, approval_id: str, rejected_by: int, reason: str = "") -> ApprovalRequest:
        with self._session() as session:
            req_db = session.query(ApprovalRequestDB).filter(
                ApprovalRequestDB.approval_id == approval_id
            ).with_for_update().first()
            if req_db is None:
                raise ValueError("Aprobación no encontrada")
            if req_db.status != ApprovalStatus.PENDING:
                raise ValueError(
                    f"Aprobación en estado '{req_db.status}', no se puede rechazar"
                )
            if req_db.expires_at is not None and datetime.utcnow() > req_db.expires_at:
                raise ValueError("Aprobación caducada; no se puede rechazar")
            req_db.status = ApprovalStatus.REJECTED
            req_db.rejected_by = rejected_by
            req_db.rejected_at = datetime.utcnow()
            req_db.rejection_reason = reason
            session.commit()
            session.refresh(req_db)
        return ApprovalRequest(
            approval_id=req_db.approval_id,
            execution_id=req_db.execution_id,
            tool_name=req_db.tool_name,
            inputs=json.loads(req_db.inputs) if req_db.inputs else {},
            proposed_by=req_db.proposed_by,
            status=req_db.status,
            reason=req_db.reason,
            approved_by=req_db.approved_by,
            approved_at=req_db.approved_at,
            rejected_by=req_db.rejected_by,
            rejected_at=req_db.rejected_at,
            rejection_reason=req_db.rejection_reason,
            expires_at=req_db.expires_at,
        )

    def is_expired(self, approval_id: str) -> bool:
        with self._session() as session:
            req_db = session.query(ApprovalRequestDB).filter(
                ApprovalRequestDB.approval_id == approval_id,
            ).first()
            if req_db is None or req_db.expires_at is None:
                return False
            return datetime.utcnow() > req_db.expires_at


# Gestor global de aprobaciones (persistente)
approval_manager = ApprovalManager()
