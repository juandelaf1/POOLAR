"""Pruebas E2E del flujo colectivo de Trama Abierta (API-level)."""
import httpx
import pytest


class TestFlujoColectivoE2E:
    """Recorrido completo desde la API."""

    def test_registro_y_login(self, base_url):
        """Registro y login de usuario independiente."""
        r = httpx.post(f"{base_url}/personas/registro", json={
            "nombre": "Persona E2E",
            "email": "e2e@test.local",
            "password": "secret123",
            "experiencia": "logistica",
        })
        assert r.status_code == 201
        assert r.json()["rol"] == "individuo"
        assert "id" in r.json()

    def test_login_individuo(self, base_url):
        """Login de individuo."""
        r = httpx.post(f"{base_url}/auth/token", json={
            "email": "e2e@test.local",
            "password": "secret123",
        })
        assert r.status_code == 200
        assert "access_token" in r.json()
        token = r.json()["access_token"]
        assert len(token) > 10

    def test_descubrimiento_coincidencias(self, base_url):
        """Descubrir coincidencias de necesidades."""
        # Login
        r = httpx.post(f"{base_url}/auth/token", json={
            "email": "e2e@test.local",
            "password": "secret123",
        })
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        # Create need via API
        r2 = httpx.post(f"{base_url}/necesidades", params={
            "titulo": "Necesidad E2E",
            "descripcion": "Necesidad sintética para E2E",
            "persona_id": 1,
            "visibilidad": "compartible",
        }, headers=headers)
        # Matching
        r3 = httpx.get(f"{base_url}/matching/necesidades-relacionadas", headers=headers)
        assert r3.status_code == 200
        assert "matches" in r3.json()

    def test_crear_problema(self, base_url):
        """Crear problema colectivo."""
        r = httpx.post(f"{base_url}/auth/token", json={
            "email": "e2e@test.local",
            "password": "secret123",
        })
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        # Create need
        r2 = httpx.post(f"{base_url}/necesidades", params={
            "titulo": "Necesidad E2E Problema",
            "descripcion": "Necesidad para problema",
            "persona_id": 1,
            "visibilidad": "compartible",
        }, headers=headers)
        need_id = r2.json()["id"]
        # Create problem
        r3 = httpx.post(f"{base_url}/problemas-colectivos", json={
            "descripcion": "Problema colectivo sintético para E2E",
            "necesidades_asociadas": [need_id],
            "origen_datos": "synthetic_pilot",
        }, headers=headers)
        assert r3.status_code == 201
        assert "id" in r3.json()

    def test_exportacion_expediente(self, base_url):
        """Verificar exportación de expediente."""
        r = httpx.post(f"{base_url}/auth/token", json={
            "email": "e2e@test.local",
            "password": "secret123",
        })
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        # Just verify the endpoint exists and returns proper format
        r2 = httpx.get(f"{base_url}/exportar/necesidades", headers=headers)
        assert r2.status_code == 200
        assert "synthetic" in r2.json() or "export" in r2.json()