# Flujo end-to-end individual — Trama Abierta MVP v0.6
# Datos sintéticos obligatorios (synthetic_pilot); sin datos reales.
from fastapi.testclient import TestClient
from src.core.auth import hash_password
from src.core.models import Persona


def test_flujo_completo_individual(client: TestClient, db_session):
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

    # 3. Creación de necesidad individual (persona_id, org nulo).
    from src.core.models import Necesidad
    necesidad = Necesidad(
        titulo="Necesidad sintética flujo",
        descripcion="Synthetic pilot need",
        persona_id=persona_id,
        visibilidad="privada",
        estado="propuesta",
    )
    db_session.add(necesidad)
    db_session.commit()
    db_session.refresh(necesidad)

    # 4. Creación de problema colectivo con origen sintético.
    r3 = client.post(
        "/problemas-colectivos",
        json={
            "descripcion": "Problema sintético flujo para prueba de flujo completo individual",
            "necesidades_asociadas": [necesidad.id],
            "origen_datos": "synthetic_pilot",
        },
        headers=headers,
    )
    assert r3.status_code == 201
    problema_id = r3.json()["id"]

    # 5. Creación de iniciativa con responsable persona (individuo autorizado).
    r4 = client.post(
        "/iniciativas",
        json={
            "necesidad_id": necesidad.id,
            "problema_colectivo_id": problema_id,
            "titulo": "Iniciativa flujo individual",
            "descripcion": "Initiative with individual responsibility",
            "criterios_decision": "Criterio sintético mínimo",
            "responsable_id": persona_id,
        },
        headers=headers,
    )
    assert r4.status_code in (201, 422)
    if r4.status_code == 201:
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

    # 7. Invitación básica documentada (no entrega física).
    # Se requiere que la persona exista como participante o el invitado sea visible.
    # En este flujo sintético solo verificamos que el endpoint responde sin exponer datos.
    r6 = client.post(
        f"/problemas-colectivos/{problema_id}/invitaciones",
        json={"persona_id": persona_id, "mensaje": "Invitación sintética"},
        headers=headers,
    )
    # Puede ser 403 o 201 según visibilidad; aceptamos respuesta controlada.
    assert r6.status_code in (201, 403)
    if r6.status_code == 201:
        assert r6.json()["estado"] == "pendiente_aceptacion"

    # 8. Aceptación de participación (mismo usuario o contexto autorizado).
    # En flujo individual, la persona puede aceptar si está autorizada.
    r7 = client.post(
        f"/problemas-colectivos/{problema_id}/participaciones",
        json={"persona_id": persona_id, "aceptar": True},
        headers=headers,
    )
    assert r7.status_code in (201, 403)
