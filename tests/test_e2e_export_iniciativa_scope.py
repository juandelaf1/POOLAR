"""E2E producto+gobernanza: export de iniciativa respeta scope (fail-closed cross-org)."""
import os
import pytest

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.core.ports import AutomationRoute  # noqa: E402


def _auto(monkeypatch):
    def fake_evaluate(proposal, context):
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [], "approved": True, "requires_human_review": False, "rejected": False}
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)


def test_export_iniciativa_cross_org_failclosed(client, headers_a, headers_b, org_a, monkeypatch):
    _auto(monkeypatch)
    org_id = org_a["org_id"]
    r = client.post("/necesidades", params={"titulo": "N exp", "descripcion": "desc export ok", "visibilidad": "privada"}, headers=headers_a)
    assert r.status_code == 201
    nid = r.json()["id"]
    r = client.post("/problemas-colectivos", json={"descripcion": "Problema export ok", "necesidades_asociadas": [nid], "origen_datos": "synthetic_pilot", "personas_participantes": [], "organizaciones_participantes": []}, headers=headers_a)
    assert r.status_code in (200, 201)
    pj = r.json()
    if pj.get("status") == "pending_review":
        pytest.skip("HITL")
    pid = pj.get("id") or pj.get("problema_id")
    r = client.post("/iniciativas", params={"necesidad_id": nid, "responsable_id": org_id, "criterios_decision": "criterio export suficiente", "problema_colectivo_id": pid}, headers=headers_a)
    assert r.status_code in (200, 201)
    ij = r.json()
    if ij.get("status") == "pending_review":
        pytest.skip("HITL")
    iid = ij.get("id") or ij.get("iniciativa_id")
    r = client.get(f"/exportar/iniciativa/{iid}", headers=headers_a)
    assert r.status_code == 200, r.text
    assert "iniciativa" in r.json()
    r = client.get(f"/exportar/iniciativa/{iid}", headers=headers_b)
    assert r.status_code in (403, 404), r.text
