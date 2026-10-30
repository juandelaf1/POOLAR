# Pruebas de autorización negativa — aislamiento individual vs organizacional
from fastapi.testclient import TestClient


def test_persona_no_accede_a_problema_de_otra_persona(client: TestClient):
    """Verifica que una persona no puede ver el problema de otra persona."""
    # Registrar persona A
    r_a = client.post("/personas/registro", json={
        "nombre": "Persona A", "email": "persona_a@test.local",
        "password": "secret123", "experiencia": "logistica",
    })
    assert r_a.status_code == 201
    persona_a_id = r_a.json()["id"]
    # Login persona A
    r_login_a = client.post("/auth/token", json={"email": "persona_a@test.local", "password": "secret123"})
    assert r_login_a.status_code == 200
    token_a = r_login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    # Registrar persona B
    r_b = client.post("/personas/registro", json={
        "nombre": "Persona B", "email": "persona_b@test.local",
        "password": "secret123", "experiencia": "logistica",
    })
    assert r_b.status_code == 201
    persona_b_id = r_b.json()["id"]
    # Login persona B
    r_login_b = client.post("/auth/token", json={"email": "persona_b@test.local", "password": "secret123"})
    assert r_login_b.status_code == 200
    token_b = r_login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    # Persona A crea necesidad y problema
    from src.core.models import Necesidad
    from src.core.database import SessionLocal
    db = SessionLocal()
    nec = Necesidad(titulo="Necesidad A", descripcion="Desc A", persona_id=persona_a_id, visibilidad="privada", estado="propuesta")
    db.add(nec)
    db.commit()
    db.refresh(nec)
    r_prob = client.post("/problemas-colectivos", json={
        "descripcion": "Problema de persona A para prueba de aislamiento",
        "necesidades_asociadas": [nec.id],
        "origen_datos": "synthetic_pilot",
    }, headers=headers_a)
    assert r_prob.status_code == 201
    problema_id = r_prob.json()["id"]
    db.close()
    # Persona B intenta ver el problema de A → 404 (no existe para B)
    r_get = client.get(f"/problemas-colectivos/{problema_id}", headers=headers_b)
    assert r_get.status_code == 404


def test_org_no_accede_a_problema_de_persona(client: TestClient, org_a, headers_a):
    """Verifica que una organización no puede ver el problema de una persona."""
    # Registrar persona
    r_p = client.post("/personas/registro", json={
        "nombre": "Persona Test", "email": "persona_test@test.local",
        "password": "secret123", "experiencia": "logistica",
    })
    assert r_p.status_code == 201
    persona_id = r_p.json()["id"]
    # Login persona
    r_login = client.post("/auth/token", json={"email": "persona_test@test.local", "password": "secret123"})
    assert r_login.status_code == 200
    token_p = r_login.json()["access_token"]
    headers_p = {"Authorization": f"Bearer {token_p}"}
    # Persona crea necesidad y problema
    from src.core.models import Necesidad
    from src.core.database import SessionLocal
    db = SessionLocal()
    nec = Necesidad(titulo="Necesidad Persona", descripcion="Desc", persona_id=persona_id, visibilidad="privada", estado="propuesta")
    db.add(nec)
    db.commit()
    db.refresh(nec)
    r_prob = client.post("/problemas-colectivos", json={
        "descripcion": "Problema de persona para prueba de aislamiento con org",
        "necesidades_asociadas": [nec.id],
        "origen_datos": "synthetic_pilot",
    }, headers=headers_p)
    assert r_prob.status_code == 201
    problema_id = r_prob.json()["id"]
    db.close()
    # Org A intenta ver el problema de la persona → 404
    r_get = client.get(f"/problemas-colectivos/{problema_id}", headers=headers_a)
    assert r_get.status_code == 404


def test_persona_no_puede_crear_iniciativa_para_necesidad_ajena(client: TestClient):
    """Verifica que una persona no puede crear iniciativa para necesidad de otra."""
    # Registrar persona A
    r_a = client.post("/personas/registro", json={
        "nombre": "Persona A2", "email": "persona_a2@test.local",
        "password": "secret123", "experiencia": "logistica",
    })
    persona_a_id = r_a.json()["id"]
    # Registrar persona B
    r_b = client.post("/personas/registro", json={
        "nombre": "Persona B2", "email": "persona_b2@test.local",
        "password": "secret123", "experiencia": "logistica",
    })
    persona_b_id = r_b.json()["id"]
    # Login persona A
    r_login_a = client.post("/auth/token", json={"email": "persona_a2@test.local", "password": "secret123"})
    token_a = r_login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    # Login persona B
    r_login_b = client.post("/auth/token", json={"email": "persona_b2@test.local", "password": "secret123"})
    token_b = r_login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}
    # Persona A crea necesidad
    from src.core.models import Necesidad
    from src.core.database import SessionLocal
    db = SessionLocal()
    nec = Necesidad(titulo="Necesidad A2", descripcion="Desc", persona_id=persona_a_id, visibilidad="privada", estado="propuesta")
    db.add(nec)
    db.commit()
    db.refresh(nec)
    necesidad_id = nec.id
    db.close()
    # Persona B intenta crear iniciativa para necesidad de A → 404
    r = client.post("/iniciativas", params={
        "necesidad_id": necesidad_id,
        "titulo": "Iniciativa ajena",
        "descripcion": "No debería funcionar",
        "criterios_decision": "Criterio sintético mínimo",
        "responsable_id": persona_b_id,
    }, headers=headers_b)
    assert r.status_code == 404