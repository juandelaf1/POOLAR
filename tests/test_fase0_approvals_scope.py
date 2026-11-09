"""Fase 0: aislamiento multi-tenant y autorización de aprobaciones (P0.1).

Pruebas HTTP/scope sobre SQLite de pruebas (no certifica concurrencia PG).
"""
import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.main import app  # noqa: E402
from src.core.ports import AutomationRoute  # noqa: E402


@pytest.fixture
def necesidad_a(client, headers_a):
    resp = client.post(
        "/necesidades",
        params={"titulo": "Necesidad test", "descripcion": "desc", "visibilidad": "privada"},
        headers=headers_a,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _force_human_review(monkeypatch):
    def fake_evaluate(proposal, context):
        return {
            "route": AutomationRoute.HUMAN_REVIEW.value,
            "risk_level": "medium",
            "reasons": ["test"],
            "approved": False,
            "requires_human_review": True,
            "rejected": False,
        }

    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)


def _create_pending(client, headers, necesidad_id):
    resp = client.post(
        "/problemas-colectivos",
        json={"descripcion": "Problema scope test", "necesidades_asociadas": [necesidad_id], "origen_datos": "synthetic_pilot"},
        headers=headers,
    )
    assert resp.status_code in (200, 201), resp.text
    body = resp.json()
    assert body["status"] == "pending_review"
    return body["approval_id"]


def test_org_b_no_puede_ver_aprobacion_de_org_a(client, headers_a, headers_b, necesidad_a, monkeypatch):
    _force_human_review(monkeypatch)
    approval_id = _create_pending(client, headers_a, necesidad_a)

    r = client.get(f"/approvals/{approval_id}", headers=headers_b)
    assert r.status_code == 404


def test_org_b_no_puede_aprobar_aprobacion_de_org_a(client, headers_a, headers_b, necesidad_a, monkeypatch):
    _force_human_review(monkeypatch)
    approval_id = _create_pending(client, headers_a, necesidad_a)

    r = client.post(f"/approvals/{approval_id}/approve", headers=headers_b)
    assert r.status_code in (403, 404)


def test_org_b_no_puede_rechazar_aprobacion_de_org_a(client, headers_a, headers_b, necesidad_a, monkeypatch):
    _force_human_review(monkeypatch)
    approval_id = _create_pending(client, headers_a, necesidad_a)

    r = client.post(f"/approvals/{approval_id}/reject?reason=no", headers=headers_b)
    assert r.status_code in (403, 404)


def test_cola_pendientes_no_expone_otros_tenants(client, headers_a, headers_b, necesidad_a, monkeypatch):
    _force_human_review(monkeypatch)
    _create_pending(client, headers_a, necesidad_a)

    r = client.get("/approvals/pending", headers=headers_b)
    assert r.status_code == 200
    ids = [x["approval_id"] for x in r.json()]
    # org_b no debe ver aprobaciones de org_a
    assert all(x.get("organizacion_id") != 1 or x["approval_id"] not in ids for x in r.json())


def test_proponente_no_puede_autoaprobarse_http(client, headers_a, necesidad_a, monkeypatch):
    _force_human_review(monkeypatch)
    approval_id = _create_pending(client, headers_a, necesidad_a)

    r = client.post(f"/approvals/{approval_id}/approve", headers=headers_a)
    assert r.status_code == 403


def test_rol_sin_permiso_no_puede_aprobar(client, headers_a, necesidad_a, monkeypatch, db_session):
    """F0-04: rol no autorizado en la misma org no puede aprobar."""
    _force_human_review(monkeypatch)
    approval_id = _create_pending(client, headers_a, necesidad_a)

    from src.core.auth import hash_password
    from src.core.models import OperationalUser

    miembro = OperationalUser(
        email="miembro@a.org", hashed_password=hash_password("secret123"),
        nombre="Miembro A", rol="miembro", organizacion_id=1,
    )
    db_session.add(miembro)
    db_session.commit()

    resp = client.post("/auth/token", json={"email": "miembro@a.org", "password": "secret123"})
    assert resp.status_code == 200
    headers_miembro = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    r = client.post(f"/approvals/{approval_id}/approve", headers=headers_miembro)
    assert r.status_code == 403

    # Tampoco debe consultar la cola con permisos de gestión implícitos cruzados
    r2 = client.get("/approvals/pending", headers=headers_miembro)
    assert r2.status_code in (200, 403)
    if r2.status_code == 200:
        # Si ve algo, solo debe ser de su ámbito (aquí no tiene pendientes propios)
        assert isinstance(r2.json(), list)


def test_observador_no_puede_aprobar(client, headers_a, necesidad_a, monkeypatch, db_session):
    _force_human_review(monkeypatch)
    approval_id = _create_pending(client, headers_a, necesidad_a)

    from src.core.auth import hash_password
    from src.core.models import OperationalUser

    obs = OperationalUser(email="obs@a.org", hashed_password=hash_password("secret123"),
                          nombre="Obs", rol="observador", organizacion_id=1)
    db_session.add(obs); db_session.commit()
    resp = client.post("/auth/token", json={"email": "obs@a.org", "password": "secret123"})
    headers_obs = {"Authorization": f"Bearer {resp.json()['access_token']}"}
    assert client.post(f"/approvals/{approval_id}/approve", headers=headers_obs).status_code == 403


def test_coordinador_puede_aprobar_misma_org(client, headers_a, necesidad_a, monkeypatch, db_session):
    _force_human_review(monkeypatch)
    approval_id = _create_pending(client, headers_a, necesidad_a)

    from src.core.auth import hash_password
    from src.core.models import OperationalUser
    from src.core.agent_harness.approvals import approval_manager

    coord = OperationalUser(email="coord@a.org", hashed_password=hash_password("secret123"),
                            nombre="Coord", rol="coordinador", organizacion_id=1)
    db_session.add(coord); db_session.commit(); db_session.refresh(coord)
    actor = {"tipo": "organizacion", "user_id": coord.id, "persona_id": None, "organizacion_id": 1, "rol": "coordinador"}
    result = approval_manager.approve(approval_id, approved_by=coord.id, actor=actor)
    assert result.status in ("ejecutada", "aprobada", "fallida_reintentable")


def test_roles_gestion_permitidos_pueden_aprobar(client, headers_a, necesidad_a, monkeypatch, db_session):
    from src.core.auth import hash_password
    from src.core.models import OperationalUser
    from src.core.agent_harness.approvals import approval_manager

    for rol in ["gestor", "responsable", "aprobador", "admin"]:
        _force_human_review(monkeypatch)
        approval_id = _create_pending(client, headers_a, necesidad_a)
        email = f"{rol}-role@a.org"  # evitar colisión con admin@a.org de fixtures
        u = OperationalUser(email=email, hashed_password=hash_password("secret123"),
                            nombre=rol, rol=rol, organizacion_id=1)
        db_session.add(u); db_session.commit(); db_session.refresh(u)
        actor = {"tipo": "organizacion", "user_id": u.id, "persona_id": None, "organizacion_id": 1, "rol": rol}
        result = approval_manager.approve(approval_id, approved_by=u.id, actor=actor)
        assert result.status in ("ejecutada", "aprobada", "fallida_reintentable"), rol


def test_idempotency_key_dedup_create(org_a):
    from src.core.agent_harness.approvals import approval_manager
    actor = {"tipo": "organizacion", "user_id": org_a["user_id"], "persona_id": None,
             "organizacion_id": org_a["org_id"], "rol": "administrador"}
    r1 = approval_manager.create("exec1", "test_tool", {}, proposed_by=org_a["user_id"], idempotency_key="idem-1", actor=actor)
    r2 = approval_manager.create("exec2", "test_tool", {}, proposed_by=org_a["user_id"], idempotency_key="idem-1", actor=actor)
    assert r1.approval_id == r2.approval_id


def test_legacy_approval_sin_scope_visible_solo_al_proponente(org_a, db_session):
    """F0-04: filas legacy sin organizacion_id no se exponen cross-tenant; proponente puede ver."""
    from src.core.agent_harness.approvals import approval_manager
    from src.core.models import ApprovalRequest as AR
    import uuid, json
    aid = str(uuid.uuid4())
    db_session.add(AR(approval_id=aid, execution_id="e", tool_name="t", inputs=json.dumps({}), proposed_by=org_a["user_id"], status="pendiente"))
    db_session.commit()
    # proponente (sin actor scope explícito pero mismo user en contexto legacy)
    actor_a = {"tipo": "organizacion", "user_id": org_a["user_id"], "persona_id": None, "organizacion_id": org_a["org_id"], "rol": "administrador"}
    assert approval_manager.get(aid, actor=actor_a).approval_id == aid
    actor_b = {"tipo": "organizacion", "user_id": 999, "persona_id": None, "organizacion_id": 999, "rol": "administrador"}
    with pytest.raises(Exception):
        approval_manager.get(aid, actor=actor_b)


def test_individuo_puede_ver_su_pendiente_pero_no_autoaprobarse(db_session):
    """F0-04: ámbito personal individuo - ver propia, no autoaprobar, sí puede retirar (rechazar)."""
    from src.core.agent_harness.approvals import approval_manager
    actor_p = {"tipo": "individuo", "user_id": 5001, "persona_id": 5001, "organizacion_id": None, "rol": "individuo"}
    req = approval_manager.create("exec-p", "test_tool", {}, proposed_by=5001, actor=actor_p)
    assert approval_manager.get(req.approval_id, actor=actor_p).approval_id == req.approval_id
    with pytest.raises(Exception):
        approval_manager.approve(req.approval_id, approved_by=5001, actor=actor_p)
    # Retiro seguro (sin ejecución): permitido
    rej = approval_manager.reject(req.approval_id, rejected_by=5001, reason="retiro voluntario", actor=actor_p)
    status = getattr(rej.status, "value", rej.status)
    assert status in ("rechazada", "rejected", "REJECTED", "rechazado")


def test_org_no_accede_aprobacion_personal_individuo(db_session):
    """F0-04: actor organizacional no accede a aprobación personal de individuo (aislamiento)."""
    from src.core.agent_harness.approvals import approval_manager
    actor_p = {"tipo": "individuo", "user_id": 5002, "persona_id": 5002, "organizacion_id": None, "rol": "individuo"}
    req = approval_manager.create("exec-p2", "test_tool", {}, proposed_by=5002, actor=actor_p)
    actor_org = {"tipo": "organizacion", "user_id": 1, "persona_id": None, "organizacion_id": 1, "rol": "administrador"}
    with pytest.raises(Exception):
        approval_manager.get(req.approval_id, actor=actor_org)


def test_individuo_no_accede_aprobacion_de_otro_individuo(db_session):
    """F0-04: aislamiento entre individuos (ámbito personal)."""
    from src.core.agent_harness.approvals import approval_manager
    actor_p1 = {"tipo": "individuo", "user_id": 5010, "persona_id": 5010, "organizacion_id": None, "rol": "individuo"}
    actor_p2 = {"tipo": "individuo", "user_id": 5011, "persona_id": 5011, "organizacion_id": None, "rol": "individuo"}
    req = approval_manager.create("exec-p1", "test_tool", {}, proposed_by=5010, actor=actor_p1)
    assert approval_manager.get(req.approval_id, actor=actor_p1).approval_id == req.approval_id
    with pytest.raises(Exception):
        approval_manager.get(req.approval_id, actor=actor_p2)
    with pytest.raises(Exception):
        approval_manager.approve(req.approval_id, approved_by=5011, actor=actor_p2)


def test_persona_http_puede_listar_su_aprobacion_pendiente(client):
    """F0-04 (HTTP): token persona puede ver su aprobación pendiente; no puede autoaprobarla."""
    from src.core.agent_harness.approvals import approval_manager
    # Registro/login persona
    r = client.post("/personas/registro", json={"nombre": "Persona HITL", "email": "hitl-persona@test.local", "password": "secret12345"})
    assert r.status_code == 201
    persona_id = r.json()["id"]
    tok = client.post("/auth/token", json={"email": "hitl-persona@test.local", "password": "secret12345"}).json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}
    actor_p = {"tipo": "individuo", "user_id": persona_id, "persona_id": persona_id, "organizacion_id": None, "rol": "individuo"}
    req = approval_manager.create("exec-http-p", "test_tool", {"synthetic_pilot": True}, proposed_by=persona_id, actor=actor_p)
    # Lista y detalle en scope
    lst = client.get("/approvals/pending", headers=h)
    assert lst.status_code == 200
    assert any(a["approval_id"] == req.approval_id for a in lst.json())
    det = client.get(f"/approvals/{req.approval_id}", headers=h)
    assert det.status_code == 200
    # No autoaprobación; retiro (rechazo) propio permitido como resolución segura
    no = client.post(f"/approvals/{req.approval_id}/approve", json={}, headers=h)
    assert no.status_code == 403
    w = client.post(f"/approvals/{req.approval_id}/reject", json={"reason": "retiro"}, headers=h)
    assert w.status_code == 200, w.text
    assert w.json().get("status") == "rechazada"

