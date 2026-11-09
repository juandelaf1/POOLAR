"""E2E capacidad: decisión para iniciativa (endpoint /iniciativas/{id}/decisiones) con gobernanza/scope."""
import os
import pytest

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.core.ports import AutomationRoute  # noqa: E402


def _auto(monkeypatch):
    def fake_evaluate(proposal, context):
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [], "approved": True, "requires_human_review": False, "rejected": False}
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)


def _human(monkeypatch):
    def fake_evaluate(proposal, context):
        return {"route": AutomationRoute.HUMAN_REVIEW.value, "risk_level": "high", "reasons": [], "approved": False, "requires_human_review": True, "rejected": False}
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)


def _mk_iniciativa(client, headers_a, org_a, monkeypatch):
    _auto(monkeypatch)
    org_id = org_a["org_id"]
    r = client.post("/necesidades", params={"titulo": "N dec", "descripcion": "desc decision ok", "visibilidad": "privada"}, headers=headers_a)
    nid = r.json()["id"]
    r = client.post("/problemas-colectivos", json={"descripcion": "Problema decision ok", "necesidades_asociadas": [nid], "origen_datos": "synthetic_pilot", "personas_participantes": [], "organizaciones_participantes": []}, headers=headers_a)
    pj = r.json()
    if pj.get("status") == "pending_review":
        return None
    pid = pj.get("id") or pj.get("problema_id")
    r = client.post("/iniciativas", params={"necesidad_id": nid, "responsable_id": org_id, "criterios_decision": "criterio decision suficiente", "problema_colectivo_id": pid}, headers=headers_a)
    ij = r.json()
    if ij.get("status") == "pending_review":
        return None
    return ij.get("id") or ij.get("iniciativa_id")


def test_create_decision_for_initiative_auto(client, headers_a, org_a, monkeypatch):
    iid = _mk_iniciativa(client, headers_a, org_a, monkeypatch)
    if iid is None:
        pytest.skip("HITL en setup")
    _auto(monkeypatch)
    r = client.post(f"/iniciativas/{iid}/decisiones", params={"tipo_decision": "aprobacion", "alternativa_elegida": "A", "motivo": "motivo suficiente", "version_metodologia": "v1"}, headers=headers_a)
    assert r.status_code in (200, 201), r.text
    j = r.json()
    assert j.get("status") == "pending_review" or j.get("id") or j.get("decision_id")


def test_create_decision_for_initiative_hitl(client, headers_a, org_a, monkeypatch):
    iid = _mk_iniciativa(client, headers_a, org_a, monkeypatch)
    if iid is None:
        pytest.skip("HITL en setup")
    _human(monkeypatch)
    r = client.post(f"/iniciativas/{iid}/decisiones", params={"tipo_decision": "aprobacion", "alternativa_elegida": "A", "motivo": "motivo suficiente", "version_metodologia": "v1"}, headers=headers_a)
    assert r.status_code in (200, 201), r.text
    assert r.json().get("status") == "pending_review"


def test_create_decision_for_initiative_cross_org(client, headers_a, headers_b, org_a, monkeypatch):
    iid = _mk_iniciativa(client, headers_a, org_a, monkeypatch)
    if iid is None:
        pytest.skip("HITL en setup")
    _auto(monkeypatch)
    r = client.post(f"/iniciativas/{iid}/decisiones", params={"tipo_decision": "aprobacion", "alternativa_elegida": "A", "motivo": "motivo suficiente", "version_metodologia": "v1"}, headers=headers_b)
    assert r.status_code in (403, 404), r.text
