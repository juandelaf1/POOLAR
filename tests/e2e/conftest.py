"""Configuración de Playwright E2E para Trama Abierta."""
import os
import time
import sys
from pathlib import Path

import pytest
import httpx

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["TRAMA_ABIERTA_SECRET_KEY"] = (
    "test-only-secret-key-not-for-production-0123456789abcdef"
)
os.environ["DATABASE_URL"] = "sqlite:///./.pytest_e2e.db"
os.environ["TRAMA_DEMO_MODE"] = "true"


@pytest.fixture(scope="session")
def api_server():
    """Inicia el servidor API para las pruebas E2E."""
    import uvicorn
    import threading
    from src.main import app

    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=8002, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    # Health check with timeout instead of fixed sleep
    for _ in range(30):
        try:
            r = httpx.get("http://127.0.0.1:8002/health", timeout=1)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.5)
    else:
        raise RuntimeError("API server did not start")
    yield "http://127.0.0.1:8002"
    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture
def base_url(api_server):
    return api_server