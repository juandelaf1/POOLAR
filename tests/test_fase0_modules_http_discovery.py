"""C1-02: endpoint read-only de descubrimiento de módulos/capacidades (sin ejecución)."""
import os

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")


def test_modules_capabilities_requires_auth_and_readonly(client, headers_a):
    r = client.get("/modules/capabilities")
    assert r.status_code in (401, 403)
    r = client.get("/modules/capabilities", headers=headers_a)
    assert r.status_code == 200
    j = r.json()
    assert "modules" in j and isinstance(j["modules"], list)
    assert j["source"] == "declarative-registry"
