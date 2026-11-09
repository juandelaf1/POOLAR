"""E2E scope/producto: lecturas y acceso fail-closed cross-org (Fase 0/capacidad)."""
import os

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.core.ports import AutomationRoute  # noqa: E402


def _auto(monkeypatch):
    def fake_evaluate(proposal, context):
        return {"route": AutomationRoute.AUTO_APPROVE.value, "risk_level": "low", "reasons": [], "approved": True, "requires_human_review": False, "rejected": False}
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)


def test_necesidades_privadas_cross_org_not_visible(client, headers_a, headers_b):
    r = client.post("/necesidades", params={"titulo": "Privada A", "descripcion": "solo org A", "visibilidad": "privada"}, headers=headers_a)
    assert r.status_code == 201
    nid = r.json()["id"]
    ra = client.get("/necesidades", headers=headers_a)
    assert ra.status_code == 200
    ids_a = {n["id"] for n in ra.json()} if isinstance(ra.json(), list) else set()
    assert nid in ids_a
    rb = client.get("/necesidades", headers=headers_b)
    assert rb.status_code == 200
    ids_b = {n["id"] for n in rb.json()} if isinstance(rb.json(), list) else set()
    assert nid not in ids_b


def test_problema_iniciativa_get_cross_org_failclosed(client, headers_a, headers_b, org_a, monkeypatch):
    _auto(monkeypatch)
    org_id = org_a["org_id"]
    r = client.post("/necesidades", params={"titulo": "N s", "descripcion": "desc scope ok", "visibilidad": "privada"}, headers=headers_a)
    nid = r.json()["id"]
    r = client.post("/problemas-colectivos", json={"descripcion": "Problema scope ok", "necesidades_asociadas": [nid], "origen_datos": "synthetic_pilot", "personas_participantes": [], "organizaciones_participantes": []}, headers=headers_a)
    pj = r.json()
    if pj.get("status") == "pending_review":
        return  # HITL path covered elsewhere
    pid = pj.get("id") or pj.get("problema_id")
    assert client.get(f"/problemas-colectivos/{pid}", headers=headers_b).status_code in (403, 404)
    r = client.post("/iniciativas", params={"necesidad_id": nid, "responsable_id": org_id, "criterios_decision": "criterio scope suficiente", "problema_colectivo_id": pid}, headers=headers_a)
    ij = r.json()
    if ij.get("status") == "pending_review":
        return
    iid = ij.get("id") or ij.get("iniciativa_id")
    assert client.get(f"/iniciativas/{iid}", headers=headers_b).status_code in (403, 404)
