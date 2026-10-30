# Flujo end-to-end individual — Poolar MVP v0.6
# Datos sintéticos obligatorios (synthetic_pilot); sin datos reales.
from fastapi.testclient import TestClient


def test_flujo_completo_individual(client: TestClient):
    # 1. Registro individual controlado.
    r = client.post(
        "/personas/registro",
        json={
            "nombre": "Persona Sintética Flujo",
            "email": "flujo@test.local",
            "password": "secret123",
            "experiencia": "logistica",
        },
    )
    assert r.status_code == 201
    data = r.json()
    assert data["rol"] == "individuo"
    assert "syntético" in data["nota"].lower() or "synthetic_pilot" in data.get("nota", "")
    persona_id = data["id"]

    # 2. Auth como individuo (no organización).
    r2 = client.post(
        "/auth/token",
        json={"email": "flujo@test.local", "password": "secret123"},
    )
    assert r2.status_code == 200
    token = r2.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Creación de necesidad individual (persona_id, org nulo) via API.
    r_nec = client.post(
        "/necesidades",
        params={
            "titulo": "Necesidad sintética flujo",
            "descripcion": "Synthetic pilot need",
            "persona_id": persona_id,
            "visibilidad": "privada",
        },
        headers=headers,
    )
    assert r_nec.status_code == 201
    necesidad_id = r_nec.json()["id"]

    # 4. Creación de problema colectivo con origen sintético.
    r3 = client.post(
        "/problemas-colectivos",
        json={
            "descripcion": "Problema sintético flujo para prueba de flujo completo individual",
            "necesidades_asociadas": [necesidad_id],
            "origen_datos": "synthetic_pilot",
        },
        headers=headers,
    )
    assert r3.status_code == 201
    problema_id = r3.json()["id"]

    # 5. Creación de iniciativa con responsable persona (individuo autorizado).
    r4 = client.post(
        "/iniciativas",
        params={
            "necesidad_id": necesidad_id,
            "problema_colectivo_id": problema_id,
            "titulo": "Iniciativa flujo individual",
            "descripcion": "Initiative with individual responsibility",
            "criterios_decision": "Criterio sintético mínimo",
            "responsable_id": persona_id,
        },
        headers=headers,
    )
    assert r4.status_code == 201
    ini = r4.json()
    assert ini["responsable_tipo"] == "persona"
    assert ini["responsable_id"] == persona_id

    # 6. Descubrimiento de problemas accesibles.
    r5 = client.get("/problemas-colectivos", headers=headers)
    assert r5.status_code == 200
    resp = r5.json()
    if isinstance(resp, list):
        ids = [p.get("id") for p in resp]
    else:
        ids = [p.get("id") for p in resp.get("items", [])]
    assert problema_id in ids

    # 7. Invitación (pendiente de consentimiento).
    r6 = client.post(
        f"/problemas-colectivos/{problema_id}/invitaciones",
        json={"persona_id": persona_id, "mensaje": "Invitación sintética"},
        headers=headers,
    )
    assert r6.status_code == 201
    assert r6.json()["estado"] == "pendiente"

    # 8. Aceptación de participación.
    r7 = client.post(
        f"/problemas-colectivos/{problema_id}/participaciones",
        json={"persona_id": persona_id, "aceptar": True},
        headers=headers,
    )
    assert r7.status_code == 201
    assert r7.json()["estado"] == "aceptada"

    # 9. Registrar decisión.
    r8 = client.post(
        f"/iniciativas/{ini['id']}/decisiones",
        params={
            "tipo_decision": "aprobacion",
            "alternativa_elegida": "Compartir ruta",
            "motivo": "Mejor eficiencia",
            "version_metodologia": "v1",
        },
        headers=headers,
    )
    assert r8.status_code == 201
    assert r8.json()["tipo_decision"] == "aprobacion"

    # 10. Registrar hito.
    r9 = client.post(
        f"/iniciativas/{ini['id']}/actividades",
        params={
            "tipo_actividad": "hito",
            "descripcion": "Primer hito de ejecución sintética",
        },
        headers=headers,
    )
    assert r9.status_code == 201

    # 11. Consultar historial.
    r10 = client.get(f"/iniciativas/{ini['id']}/historial", headers=headers)
    assert r10.status_code == 200
    assert r10.json()["total"] >= 1

    # 12. Exportar expediente completo.
    r11 = client.get(f"/exportar/iniciativa/{ini['id']}", headers=headers)
    assert r11.status_code == 200
    assert r11.json()["synthetic"] is True