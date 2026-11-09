"""Políticas declarativas por acción (guardrail)."""
import os

os.environ.setdefault("POOLAR_SECRET_KEY", "test-only-secret-key-not-for-production-0123456789abcdef")
os.environ.setdefault("DATABASE_URL", "sqlite:///./.pytest_poolar.db")

from src.core.agent_harness.action_policies import get_action_policy, validate_action_request, ACTION_POLICIES  # noqa: E402
from src.core.agent_harness.handlers import EXPECTED_RESUMABLE_TOOLS  # noqa: E402


def test_resumable_tools_have_policies():
    for tool in EXPECTED_RESUMABLE_TOOLS:
        p = get_action_policy(tool)
        assert p.resumable is True
        assert p.requires_human_review is True
        assert tool in ACTION_POLICIES


def test_validate_action_request():
    assert validate_action_request("create_iniciativa", {}) == []
    assert any("tool_name" in i for i in validate_action_request("", {}))
    assert any("inputs" in i for i in validate_action_request("x", "nope"))  # type: ignore
