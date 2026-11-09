"""F0-08: registro determinista de handlers reanudables."""
import os

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")


def test_expected_handlers_registered():
    import src.main  # noqa: F401  # registra handlers
    from src.core.agent_harness.handlers import validate_resumable_handlers, EXPECTED_RESUMABLE_TOOLS

    report = validate_resumable_handlers()
    assert report["ok"], report
    for tool in EXPECTED_RESUMABLE_TOOLS:
        assert tool in report["registered"], tool
