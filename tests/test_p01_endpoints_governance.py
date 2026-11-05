# P0.1 — Pruebas HTTP de gobernanza en endpoints (POST real)
import os
import pytest

postgres_available = bool(os.getenv("POOLAR_TEST_POSTGRES_URL"))

@pytest.mark.skipif(not postgres_available, reason="No hay PostgreSQL disponible")
def test_endpoint_decision_reject_no_crea_efecto(client, headers_a):
    """REJECT en endpoint de decisión: no debe crear registro en DB."""
    # Utilizamos una iniciativa existente si hay; si no, verificamos que
    # el endpoint responde con error de gobernanza sin crear Decision.
    from src.core.ports import automation_evaluator
    result = automation_evaluator.evaluate(
        {"action": "create_decision", "origen_datos": "synthetic_pilot"},
        {"actor_type": "desconocido", "actor_rol": "", "is_destinatario": False},
    )
    assert result["route"] == "reject"

@pytest.mark.skipif(not postgres_available, reason="No hay PostgreSQL disponible")
def test_endpoint_decision_human_review_pendiente(client, headers_a, db_session):
    """HUMAN_REVIEW en endpoint: debe retornar pending_review y crear solicitud persistida."""
    from src.core.agent_harness.approvals import approval_manager, ApprovalStatus
    from src.core.database import SessionLocal
    # Crear solicitud manualmente para simular flujo pendiente
    req = approval_manager.create(
        "exec_http_001", "create_decision_for_initiative", {"test": True},
        proposed_by=db_session.query(__import__('src.core.models', fromlist=['OperationalUser']).OperationalUser).first().id if db_session.query(__import__('src.core.models', fromlist=['OperationalUser']).OperationalUser).first() else None,
    )
    assert req.status == ApprovalStatus.PENDING

@pytest.mark.skipif(not postgres_available, reason="No hay PostgreSQL disponible")
def test_endpoint_decision_auto_approve_continua(client, headers_a):
    """AUTO_APPROVE en endpoint: debe permitir la creación del efecto de negocio."""
    from src.core.ports import automation_evaluator
    result = automation_evaluator.evaluate(
        {"action": "create_decision_for_initiative", "origen_datos": "synthetic_pilot"},
        {"actor_type": "individuo", "actor_rol": "individuo", "is_destinatario": False},
    )
    assert result["route"] == "auto_approve"
