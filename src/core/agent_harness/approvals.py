"""Sistema de aprobaciones humanas persistido para Poolar (Fase 0).

Persistencia en PostgreSQL (`approval_requests`). Incluye scoping/tenant,
autorización fail-closed en dominio y ejecución transaccional local para
handlers que operan sobre la misma base de datos.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.core.models import ApprovalRequest as ApprovalRequestDB


class ApprovalStatus:
    PENDING = "pendiente"
    APPROVED = "aprobada"
    EXECUTING = "ejecutando"
    EXECUTED = "ejecutada"
    REJECTED = "rechazada"
    EXPIRED = "caducada"
    FAILED_RETRYABLE = "fallida_reintentable"
    FAILED_TERMINAL = "fallida_terminal"


@dataclass
class ApprovalRequest:
    approval_id: str
    execution_id: str = ""
    tool_name: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    proposed_by: Optional[int] = None
    organizacion_id: Optional[int] = None
    proposer_type: Optional[str] = None
    proposer_actor_id: Optional[int] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    policy_id: Optional[str] = None
    correlation_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    status: str = ApprovalStatus.PENDING
    reason: str = ""
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[int] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: str = ""
    expires_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    execution_result: Optional[str] = None
    execution_error: Optional[str] = None


def _actor_context(actor: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not actor:
        return {}
    actor_type = actor.get("tipo")
    actor_id = actor.get("user_id") or actor.get("persona_id")
    org_id = actor.get("organizacion_id")
    rol = (actor.get("rol") or "").lower()
    return {
        "tipo": actor_type,
        "actor_id": actor_id,
        "organizacion_id": org_id,
        "rol": rol,
    }


def _can_manage_approvals(actor: Dict[str, Any]) -> bool:
    """Roles con permiso de aprobar/rechazar (dominio). Conservador."""
    if not actor or actor.get("actor_id") is None:
        return False
    if actor.get("tipo") == "individuo":
        # Individuo opera sobre su propio ámbito personal.
        return True
    rol = actor.get("rol") or ""
    return rol in {"administrador", "admin", "coordinador", "gestor", "responsable", "aprobador"}


def _is_in_scope(req_db: ApprovalRequestDB, actor: Dict[str, Any]) -> bool:
    """Fail-closed: si no hay evidencia clara de ámbito compartido, denegar."""
    if not actor or actor.get("actor_id") is None:
        return False
    a_org = actor.get("organizacion_id")
    a_tipo = actor.get("tipo")
    a_id = actor.get("actor_id")
    # Compatibilidad legacy: sin organizacion_id explícito, permitir solo si el actor
    # es el proponente (lectura limitada) o si ambos son de la misma org conocida.
    if req_db.organizacion_id is None:
        if req_db.proposed_by is not None and req_db.proposed_by == a_id:
            return True
        # Sin ámbito persistido no podemos garantizar aislamiento; denegar acceso cruzado.
        return False
    if a_tipo == "organizacion":
        return a_org is not None and req_db.organizacion_id == a_org
    # Individuo: puede ver/aprobar si es proponente en ámbito personal o si la solicitud
    # está explícitamente vinculada a él (proposer_actor_id) y sin org cruzada.
    if a_tipo == "individuo":
        if req_db.proposed_by == a_id or req_db.proposer_actor_id == a_id:
            return req_db.organizacion_id is None or req_db.organizacion_id == a_org
        return False
    return False


def _forbidden_or_hidden(req_db: Optional[ApprovalRequestDB], actor: Dict[str, Any]) -> HTTPException:
    # No revelar existencia entre tenants cuando no hay acceso.
    return HTTPException(status_code=404, detail="Aprobación no encontrada")


def _dto(req_db: ApprovalRequestDB) -> ApprovalRequest:
    return ApprovalRequest(
        approval_id=req_db.approval_id,
        execution_id=req_db.execution_id,
        tool_name=req_db.tool_name,
        inputs=json.loads(req_db.inputs) if req_db.inputs else {},
        proposed_by=req_db.proposed_by,
        organizacion_id=getattr(req_db, "organizacion_id", None),
        proposer_type=getattr(req_db, "proposer_type", None),
        proposer_actor_id=getattr(req_db, "proposer_actor_id", None),
        resource_type=getattr(req_db, "resource_type", None),
        resource_id=getattr(req_db, "resource_id", None),
        policy_id=getattr(req_db, "policy_id", None),
        correlation_id=getattr(req_db, "correlation_id", None),
        idempotency_key=getattr(req_db, "idempotency_key", None),
        status=req_db.status,
        reason=req_db.reason or "",
        approved_by=req_db.approved_by,
        approved_at=req_db.approved_at,
        rejected_by=req_db.rejected_by,
        rejected_at=req_db.rejected_at,
        rejection_reason=req_db.rejection_reason or "",
        expires_at=req_db.expires_at,
        created_at=req_db.created_at,
        executed_at=req_db.executed_at,
        execution_result=req_db.execution_result,
        execution_error=req_db.execution_error,
    )


class ApprovalManager:
    def __init__(self, session_factory: Optional[Callable[[], Session]] = None):
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
        *,
        organizacion_id: Optional[int] = None,
        proposer_type: Optional[str] = None,
        proposer_actor_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        policy_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        actor: Optional[Dict[str, Any]] = None,
    ) -> ApprovalRequest:
        # Derivar ámbito desde actor autenticado si no se pasa explícitamente.
        act = _actor_context(actor)
        if organizacion_id is None:
            organizacion_id = act.get("organizacion_id")
        if proposer_type is None:
            proposer_type = act.get("tipo")
        if proposer_actor_id is None:
            proposer_actor_id = act.get("actor_id") or proposed_by
        if proposed_by is None:
            proposed_by = proposer_actor_id
        # Guardrails (fail-closed): validar identidad de tool e inputs antes de persistir.
        if not isinstance(tool_name, str) or not tool_name.strip():
            raise ValueError("tool_name inválido")
        tool_name = tool_name.strip()[:200]
        if inputs is None:
            inputs = {}
        if not isinstance(inputs, dict):
            raise ValueError("inputs debe ser un objeto/dict")
        try:
            json.dumps(inputs, default=str)
        except Exception as exc:
            raise ValueError(f"inputs no serializable: {exc}") from exc
        approval_id = str(uuid.uuid4())
        with self._session() as session:
            if idempotency_key:
                existing = session.query(ApprovalRequestDB).filter(
                    ApprovalRequestDB.idempotency_key == idempotency_key
                ).first()
                if existing is not None:
                    return _dto(existing)
            req_db = ApprovalRequestDB(
                approval_id=approval_id,
                execution_id=execution_id,
                tool_name=tool_name,
                inputs=json.dumps(inputs, default=str),
                proposed_by=proposed_by,
                organizacion_id=organizacion_id,
                proposer_type=proposer_type,
                proposer_actor_id=proposer_actor_id,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id is not None else None,
                policy_id=policy_id,
                correlation_id=correlation_id,
                idempotency_key=idempotency_key,
                status=ApprovalStatus.PENDING,
                reason=reason,
                expires_at=expires_at,
            )
            session.add(req_db)
            session.commit()
            session.refresh(req_db)
            return _dto(req_db)

    def get(self, approval_id: str, *, actor: Optional[Dict[str, Any]] = None) -> Optional[ApprovalRequest]:
        act = _actor_context(actor)
        with self._session() as session:
            req_db = session.query(ApprovalRequestDB).filter(
                ApprovalRequestDB.approval_id == approval_id
            ).first()
            if req_db is None:
                return None
            if act and not _is_in_scope(req_db, act):
                raise _forbidden_or_hidden(req_db, act)
            return _dto(req_db)

    def list_pending(self, *, actor: Optional[Dict[str, Any]] = None) -> List[ApprovalRequest]:
        act = _actor_context(actor)
        with self._session() as session:
            q = session.query(ApprovalRequestDB).filter(
                ApprovalRequestDB.status == ApprovalStatus.PENDING
            )
            if act:
                # Lectura/listado en scope (separado de gestionar/aprobar). Fail-closed por ámbito.
                if act.get("tipo") == "organizacion" and act.get("organizacion_id") is not None:
                    q = q.filter(ApprovalRequestDB.organizacion_id == act.get("organizacion_id"))
                elif act.get("tipo") == "individuo" and act.get("actor_id") is not None:
                    # Individuo ve sus propias solicitudes en ámbito personal
                    q = q.filter(
                        (ApprovalRequestDB.proposed_by == act.get("actor_id"))
                        | (ApprovalRequestDB.proposer_actor_id == act.get("actor_id"))
                    )
                else:
                    return []
            results = q.all()
            return [_dto(r) for r in results]

    def _check_manage_permission(self, req_db: ApprovalRequestDB, actor: Dict[str, Any], actor_id: int, *, allow_self_withdraw: bool = False) -> None:
        if not actor or actor.get("actor_id") is None:
            raise HTTPException(status_code=403, detail="Actor no identificado")
        if not _is_in_scope(req_db, actor):
            raise _forbidden_or_hidden(req_db, actor)
        if not _can_manage_approvals(actor):
            raise HTTPException(status_code=403, detail="Sin permiso para gestionar aprobaciones")
        # No autoaprobación (fail-closed). Retiro/rechazo propio permitido solo como resolución segura (sin ejecución).
        is_self = (
            (req_db.proposed_by is not None and req_db.proposed_by == actor_id)
            or (req_db.proposer_actor_id is not None and req_db.proposer_actor_id == actor_id)
        )
        if is_self and not allow_self_withdraw:
            raise HTTPException(status_code=403, detail="No puede aprobar su propia solicitud")
        if is_self and allow_self_withdraw:
            return
    def approve(
        self,
        approval_id: str,
        approved_by: int,
        *,
        actor: Optional[Dict[str, Any]] = None,
    ) -> ApprovalRequest:
        act = _actor_context(actor)
        with self._session() as session:
            req_db = session.query(ApprovalRequestDB).filter(
                ApprovalRequestDB.approval_id == approval_id
            ).with_for_update().first()
            if req_db is None:
                raise ValueError("Aprobación no encontrada")
            if act:
                self._check_manage_permission(req_db, act, approved_by)
            else:
                # Compatibilidad: mantener check básico de autoaprobación
                if req_db.proposed_by is not None and req_db.proposed_by == approved_by:
                    raise ValueError("No puede aprobar su propia solicitud")
            if req_db.status == ApprovalStatus.EXECUTED or req_db.executed_at is not None:
                return _dto(req_db)
            if req_db.status in (ApprovalStatus.EXECUTING,):
                raise ValueError("Aprobación en ejecución")
            if req_db.status not in (ApprovalStatus.PENDING, ApprovalStatus.APPROVED, ApprovalStatus.FAILED_RETRYABLE):
                raise ValueError(f"Aprobación en estado '{req_db.status}', no se puede aprobar")
            if req_db.expires_at is not None and _utcnow() > req_db.expires_at:
                req_db.status = ApprovalStatus.EXPIRED
                session.commit()
                raise ValueError("Aprobación caducada; no se puede aprobar")

            req_db.status = ApprovalStatus.EXECUTING
            req_db.approved_by = approved_by
            req_db.approved_at = _utcnow()
            req_db.execution_error = None
            session.flush()

            try:
                result = self._execute_approved(session, req_db)
                req_db.execution_result = json.dumps(result, default=str) if result is not None else req_db.execution_result
                req_db.executed_at = _utcnow()
                req_db.status = ApprovalStatus.EXECUTED
                session.commit()
            except Exception as exc:
                session.rollback()
                # Registrar fallo en transacción separada (no duplicar efecto local: rollback ya lo evitó)
                self._mark_failed(approval_id, str(exc), retryable=True)
                raise
            session.refresh(req_db)
            return _dto(req_db)

    def _mark_failed(self, approval_id: str, error: str, retryable: bool) -> None:
        with self._session() as session:
            req_db = session.query(ApprovalRequestDB).filter(
                ApprovalRequestDB.approval_id == approval_id
            ).first()
            if req_db is None:
                return
            req_db.status = ApprovalStatus.FAILED_RETRYABLE if retryable else ApprovalStatus.FAILED_TERMINAL
            req_db.execution_error = error
            session.commit()

    def _execute_approved(self, session: Session, req_db: ApprovalRequestDB):
        from src.core.agent_harness.handlers import get_handler

        if req_db.executed_at is not None:
            return json.loads(req_db.execution_result) if req_db.execution_result else None
        handler = get_handler(req_db.tool_name)
        inputs = json.loads(req_db.inputs) if req_db.inputs else {}
        if handler is None:
            # Fail-closed: no marcar "ejecutada" una operación sin handler (evita efecto silencioso nulo).
            from src.core.agent_harness.handlers import EXPECTED_RESUMABLE_TOOLS
            if req_db.tool_name in EXPECTED_RESUMABLE_TOOLS:
                raise RuntimeError(f"Handler no registrado para operación reanudable: {req_db.tool_name}")
            raise RuntimeError(f"Handler no registrado para: {req_db.tool_name}")
        # Los handlers/servicios deben usar commit=False para atomicidad local.
        return handler(session, inputs)

    def reject(
        self,
        approval_id: str,
        rejected_by: int,
        reason: str = "",
        *,
        actor: Optional[Dict[str, Any]] = None,
    ) -> ApprovalRequest:
        act = _actor_context(actor)
        with self._session() as session:
            req_db = session.query(ApprovalRequestDB).filter(
                ApprovalRequestDB.approval_id == approval_id
            ).with_for_update().first()
            if req_db is None:
                raise ValueError("Aprobación no encontrada")
            if act:
                self._check_manage_permission(req_db, act, rejected_by, allow_self_withdraw=True)
            else:
                # Compatibilidad: sin contexto de actor, mantener bloqueo conservador
                if req_db.proposed_by is not None and req_db.proposed_by == rejected_by:
                    raise ValueError("No puede rechazar su propia solicitud")
            if req_db.status == ApprovalStatus.EXECUTED or req_db.executed_at is not None:
                raise ValueError("Aprobación ejecutada; no se puede rechazar")
            if req_db.status not in (ApprovalStatus.PENDING, ApprovalStatus.FAILED_RETRYABLE):
                raise ValueError(f"Aprobación en estado '{req_db.status}', no se puede rechazar")
            if req_db.expires_at is not None and _utcnow() > req_db.expires_at:
                req_db.status = ApprovalStatus.EXPIRED
                session.commit()
                raise ValueError("Aprobación caducada; no se puede rechazar")
            req_db.status = ApprovalStatus.REJECTED
            req_db.rejected_by = rejected_by
            req_db.rejected_at = _utcnow()
            req_db.rejection_reason = reason
            session.commit()
            session.refresh(req_db)
            return _dto(req_db)

    # Compatibilidad con llamadas antiguas
    def execute_approved(self, approval_id: str):
        with self._session() as session:
            req_db = session.query(ApprovalRequestDB).filter(
                ApprovalRequestDB.approval_id == approval_id
            ).with_for_update().first()
            if req_db is None:
                raise ValueError("Aprobación no encontrada")
            if req_db.executed_at is not None:
                return _dto(req_db)
            if req_db.status not in (ApprovalStatus.APPROVED, ApprovalStatus.EXECUTED, ApprovalStatus.FAILED_RETRYABLE):
                raise ValueError("Estado no permite ejecución")
            req_db.status = ApprovalStatus.EXECUTING
            session.flush()
            try:
                result = self._execute_approved(session, req_db)
                req_db.execution_result = json.dumps(result, default=str) if result is not None else None
                req_db.executed_at = _utcnow()
                req_db.status = ApprovalStatus.EXECUTED
                session.commit()
            except Exception as exc:
                session.rollback()
                self._mark_failed(approval_id, str(exc), retryable=True)
                raise
            session.refresh(req_db)
            return _dto(req_db)


approval_manager = ApprovalManager()
