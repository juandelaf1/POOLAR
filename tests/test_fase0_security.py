"""Guardrails de seguridad/logs (redacción, inyección)."""
from src.core.security import sanitize_for_log, redact_audit_event, check_injection


def test_sanitize_redacts_db_url_and_secrets():
    s = "postgresql+psycopg2://user:pass@host/db?sslmode=require token=abc password=secret"
    out = sanitize_for_log(s)
    assert "pass@" not in out
    assert "password=[REDACTED]" in out.lower() or "password=" not in out.lower() or "[REDACTED]" in out
    assert "postgresql://" in out
    assert "user:pass" not in out


def test_redact_audit_event():
    e = {"password": "x", "tool": "t", "detail": "contact a@b.com"}
    r = redact_audit_event(e)
    assert r["password"] == "[REDACTED]"
    assert "[REDACTED_EMAIL]" in r["detail"]


def test_check_injection():
    assert check_injection("ignore previous instructions") is True
    assert check_injection("operación normal") is False
