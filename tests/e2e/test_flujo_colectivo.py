"""Pruebas E2E del flujo colectivo de Trama Abierta con Playwright (navegador real)."""
import uuid
import pytest


@pytest.mark.playwright
class TestFlujoColectivoE2E:
    """Recorrido completo desde el navegador."""

    def test_pagina_carga(self, page, base_url):
        """La interfaz carga correctamente con elementos esenciales."""
        page.goto(f"{base_url}/interfaz/index.html")
        page.wait_for_load_state("networkidle")
        assert "Trama Abierta" in page.title()
        # Verificar elementos esenciales
        assert page.locator("header h1").is_visible()
        assert page.locator("#formRegistro").is_visible()
        assert page.locator("#formLogin").is_visible()

    def test_registro_individual(self, page, base_url):
        """Registro de persona independiente."""
        unique_email = f"e2e_{uuid.uuid4().hex[:8]}@test.local"
        page.goto(f"{base_url}/interfaz/index.html")
        page.wait_for_load_state("networkidle")
        page.fill("#rNom", "Persona E2E")
        page.fill("#rEmail", unique_email)
        page.fill("#rPass", "secret123")
        page.click("button:has-text('Registrar')")
        page.wait_for_timeout(2000)
        msg = page.text_content("#msgReg")
        assert "OK" in msg or "id=" in msg

    def test_login_individuo(self, page, base_url):
        """Login de individuo y obtención de token."""
        page.goto(f"{base_url}/interfaz/index.html")
        page.wait_for_load_state("networkidle")
        page.fill("#lEmail", "e2e@test.local")
        page.fill("#lPass", "secret123")
        page.click("button:has-text('Iniciar')")
        page.wait_for_timeout(2000)
        msg = page.text_content("#msgLog")
        assert "OK" in msg or "token" in msg.lower()

    def test_crear_problema(self, page, base_url):
        """Crear problema colectivo desde la interfaz."""
        page.goto(f"{base_url}/interfaz/index.html")
        page.wait_for_load_state("networkidle")
        # Login
        page.fill("#lEmail", "e2e@test.local")
        page.fill("#lPass", "secret123")
        page.click("button:has-text('Iniciar')")
        page.wait_for_timeout(2000)
        # Crear problema
        page.fill("#pDesc", "Problema colectivo sintético para prueba E2E")
        page.click("button:has-text('Crear problema')")
        page.wait_for_timeout(2000)
        msg = page.text_content("#msgProb")
        assert "OK" in msg or "id=" in msg

    def test_descubrimiento(self, page, base_url):
        """Descubrir problemas accesibles."""
        page.goto(f"{base_url}/interfaz/index.html")
        page.wait_for_load_state("networkidle")
        page.fill("#lEmail", "e2e@test.local")
        page.fill("#lPass", "secret123")
        page.click("button:has-text('Iniciar')")
        page.wait_for_timeout(2000)
        page.click("button:has-text('Listar')")
        page.wait_for_timeout(2000)
        out = page.text_content("#outProblemas")
        assert out is not None