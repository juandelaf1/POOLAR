"""Fase 0 P0.2: decisiones fail-closed ante denegación/error de autorización."""
import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.main import app  # noqa: E402
from src.core.database import SessionLocal  # noqa: E402
from src.core.models import Decision, EventoAuditoria  # noqa: E402
from src.services.decision_service import execute_create_decision_for_initiative  # noqa: E402


def test_cross_org_no_crea_decision_ni_auditoria(db_session, org_a, org_b):
    # Crear necesidad + iniciativa como org_a (usando DB directa para simplicidad controlada)
    from src.core.models import Necesidad, Iniciativa

    need = Necesidad(titulo="N", descripcion="d", visibilidad="privada", organizacion_id=org_a["org_id"])
    db_session.add(need)
    db_session.flush()
    ini = Iniciativa(
        necesidad_id=need.id, responsable_id=org_a["org_id"], responsable_tipo="organizacion",
        titulo="I", descripcion="d", criterios_decision="criterio valido", estado="propuesta",
    )
    db_session.add(ini)
    db_session.commit()
    db_session.refresh(ini)

    user_b = {"tipo": "organizacion", "user_id": org_b["user_id"], "persona_id": None,
              "organizacion_id": org_b["org_id"], "rol": "administrador"}
    data = {
        "iniciativa_id": ini.id, "tipo_decision": "aprobar", "alternativa_elegida": "x",
        "motivo": "m", "version_metodologia": "v1", "factors": None,
    }
    with pytest.raises(Exception):
        execute_create_decision_for_initiative(db_session, data, user_b, commit=True)

    # No debe haberse creado decisión ni evento
    with SessionLocal() as s:
        assert s.query(Decision).filter_by(iniciativa_id=ini.id).count() == 0
        assert s.query(EventoAuditoria).filter_by(entidad_referencia="decision").count() == 0
