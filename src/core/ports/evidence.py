"""Puerto de evidencias y procedencia para Poolar.

Inspirado en FitFamily: evidencia con fuente, fechas, unidades, huella hash/versión.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json


@dataclass
class Evidence:
    """Evidencia verificable con procedencia."""
    id: Optional[int] = None
    source: str = ""  # Fuente (URL, documento, API)
    source_url: Optional[str] = None
    date_queried: Optional[datetime] = None
    reference_period: Optional[str] = None
    unit: Optional[str] = None
    value: Optional[Any] = None
    verification_status: str = "unverified"  # observed, declared_unverified, estimated, hypothesis
    limitations: Optional[str] = None
    license: Optional[str] = None
    entity_type: str = ""  # necesidad, problema, iniciativa, decision
    entity_id: Optional[int] = None
    created_by: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    hash_fingerprint: Optional[str] = None

    def compute_fingerprint(self) -> str:
        """Calcula huella hash del contenido para verificación."""
        content = json.dumps({
            "source": self.source,
            "value": self.value,
            "unit": self.unit,
            "reference_period": self.reference_period,
        }, sort_keys=True, default=str)
        self.hash_fingerprint = hashlib.sha256(content.encode()).hexdigest()
        return self.hash_fingerprint

    def validate(self) -> List[str]:
        """Valida la evidencia. Devuelve lista de errores."""
        errors = []
        if not self.source:
            errors.append("Fuente (source) es obligatoria")
        if self.value is None and self.verification_status == "observed":
            errors.append("Evidencia observada requiere valor")
        if not self.unit and self.value is not None:
            errors.append("Unidad (unit) es obligatoria cuando hay valor")
        if not self.entity_type:
            errors.append("Tipo de entidad (entity_type) es obligatorio")
        if self.entity_id is None:
            errors.append("ID de entidad (entity_id) es obligatorio")
        return errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "source_url": self.source_url,
            "date_queried": self.date_queried.isoformat() if self.date_queried else None,
            "reference_period": self.reference_period,
            "unit": self.unit,
            "value": self.value,
            "verification_status": self.verification_status,
            "limitations": self.limitations,
            "license": self.license,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "hash_fingerprint": self.hash_fingerprint,
            "created_at": self.created_at.isoformat(),
        }


class EvidencePort(ABC):
    """Puerto para gestión y validación de evidencias."""

    @abstractmethod
    def register(self, evidence: Evidence) -> Evidence:
        """Registra una evidencia. Valida antes de persistir."""
        ...

    @abstractmethod
    def get(self, evidence_id: int) -> Optional[Evidence]:
        """Obtiene una evidencia por ID."""
        ...

    @abstractmethod
    def get_by_entity(self, entity_type: str, entity_id: int) -> List[Evidence]:
        """Obtiene evidencias de una entidad."""
        ...

    @abstractmethod
    def validate(self, evidence: Evidence) -> List[str]:
        """Valida una evidencia."""
        ...


class EvidenceService:
    """Servicio de evidencias con validación."""

    def __init__(self):
        self._evidences: Dict[int, Evidence] = {}
        self._next_id = 1

    def register(self, evidence: Evidence) -> Evidence:
        errors = evidence.validate()
        if errors:
            raise ValueError(f"Evidencia inválida: {'; '.join(errors)}")
        evidence.id = self._next_id
        self._next_id += 1
        evidence.compute_fingerprint()
        self._evidences[evidence.id] = evidence
        return evidence

    def get(self, evidence_id: int) -> Optional[Evidence]:
        return self._evidences.get(evidence_id)

    def get_by_entity(self, entity_type: str, entity_id: int) -> List[Evidence]:
        return [e for e in self._evidences.values()
                if e.entity_type == entity_type and e.entity_id == entity_id]

    def validate(self, evidence: Evidence) -> List[str]:
        return evidence.validate()


# Instancia global
evidence_service = EvidenceService()