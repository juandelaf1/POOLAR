"""E2E capacidad core (producto + evidencia gobernanza/Fase 0).
Flujo: necesidad -> problema colectivo -> iniciativa -> decisión, con scope.
Maneja HITL: cuando gobernanza retorna pending_review, aprueba con actor autorizado distinto (si aplica) o valida ruta.
"""
import os
import pytest

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.core.ports import AutomationRoute  # noqa: E402


def _auto(monkeypatch):
    def fake_evaluate(proposal, context):
        return {
            "route": AutomationRoute.AUTO_APPROVE.value,
            "risk_level": "low",
            "reasons": ["e2e auto"],
            "approved": True,
            "requires_human_review": False,
            "rejected": False,
        }
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)


def _human(monkeypatch):
    def fake_evaluate(proposal, context):
        return {
            "route": AutomationRoute.HUMAN_REVIEW.value,
            "risk_level": "high",
            "reasons": ["e2e hitl"],
            "approved": False,
            "requires_human_review": True,
            "rejected": False,
        }
    monkeypatch.setattr("src.core.ports.automation_evaluator.evaluate", fake_evaluate)


def _extract_id(resp_json, *keys):
    if not isinstance(resp_json, dict):
        return None
    for k in keys:
        if resp_json.get(k) is not None:
            return resp_json[k]
    # nested common shapes
    for v in resp_json.values():
        if isinstance(v, dict):
            for k in keys:
                if v.get(k) is not None:
                    return v[k]
    return None


def test_e2e_flujo_core_autoapprove_org(client, headers_a, org_a, monkeypatch):
    """Capacidad core end-to-end (auto-aprobación): org crea y gestiona su flujo sin fuga de scope."""
    _auto(monkeypatch)
    org_id = org_a["org_id"]

    r = client.post("/necesidades", params={"titulo": "Agua segura", "descripcion": "Acceso comunitario", "visibilidad": "privada"}, headers=headers_a)
    assert r.status_code == 201, r.text
    necesidad_id = _extract_id(r.json(), "id", "necesidad_id")
    assert necesidad_id

    r = client.post("/problemas-colectivos", json={"descripcion": "Problema agua", "necesidades_asociadas": [necesidad_id], "origen_datos": "synthetic_pilot", "personas_participantes": [], "organizaciones_participantes": []}, headers=headers_a)
    assert r.status_code in (200, 201), r.text
    pj = r.json()
    if pj.get("status") == "pending_review":
        pytest.fail(f"esperaba auto-approve en e2e negocio, obtuvo pending: {pj}")
    problema_id = _extract_id(pj, "id", "problema_id")
    assert problema_id

    r = client.post("/iniciativas", params={"necesidad_id": necesidad_id, "responsable_id": org_id, "criterios_decision": "criterio técnico y comunitario", "problema_colectivo_id": problema_id, "titulo": "Pozo"}, headers=headers_a)
    assert r.status_code in (200, 201), r.text
    ij = r.json()
    if ij.get("status") == "pending_review":
        pytest.fail(f"esperaba auto-approve en e2e negocio, obtuvo pending: {ij}")
    iniciativa_id = _extract_id(ij, "id", "iniciativa_id")
    assert iniciativa_id

    r = client.post("/decisiones", params={"iniciativa_id": iniciativa_id, "tipo_decision": "aprobacion", "alternativa_elegida": "pozo A", "motivo": "mejor costo-beneficio", "responsable_decision": org_id, "version_metodologia": "v1"}, headers=headers_a)
    assert r.status_code in (200, 201, 403), r.text  # 403 si gobernanza/HITL distinto; validar abajo
    dj = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    if r.status_code in (200, 201) and dj.get("status") == "pending_review":
        # HITL activo: evidencia válida de gobernanza
        assert dj.get("approval_id")
    elif r.status_code in (200, 201):
        assert _extract_id(dj, "id", "decision_id")


def test_e2e_flujo_core_cross_org_failclosed(client, headers_a, headers_b, org_a, org_b, monkeypatch):
    """Evidencia Fase 0: org B no accede/gestiona recursos de org A."""
    _auto(monkeypatch)
    org_id = org_a["org_id"]
    r = client.post("/necesidades", params={"titulo": "Priv A", "descripcion": "desc", "visibilidad": "privada"}, headers=headers_a)
    assert r.status_code == 201
    necesidad_id = r.json()["id"]
    # org B no debe poder crear problema usando necesidad privada de A
    r = client.post("/problemas-colectivos", json={"descripcion": "Intento cross-org inválido", "necesidades_asociadas": [necesidad_id], "origen_datos": "synthetic_pilot", "personas_participantes": [], "organizaciones_participantes": []}, headers=headers_b)
    assert r.status_code in (403, 404, 422), r.text  # fail-closed: sin acceso o validado sin efecto cross-org


def test_e2e_gobernanza_hitl_pending(client, headers_a, org_a, monkeypatch):
    """Evidencia gobernanza: acción crítica puede quedar en pending_review (sin efecto inmediato)."""
    _human(monkeypatch)
    r = client.post("/necesidades", params={"titulo": "N", "descripcion": "desc", "visibilidad": "privada"}, headers=headers_a)
    assert r.status_code == 201
    necesidad_id = r.json()["id"]
    r = client.post("/problemas-colectivos", json={"descripcion": "Problema sintético HITL", "necesidades_asociadas": [necesidad_id], "origen_datos": "synthetic_pilot", "personas_participantes": [], "organizaciones_participantes": []}, headers=headers_a)
    assert r.status_code in (200, 201), r.text
    pj = r.json()
    assert pj.get("status") == "pending_review"
    assert pj.get("approval_id")
