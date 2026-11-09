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


def test_known_governed_actions_declared():
    for name in ["create_iniciativa", "create_decision", "create_decision_for_initiative", "cambiar_estado_problema_colectivo", "create_problema_colectivo"]:
        p = get_action_policy(name)
        assert p.tool_name == name
        assert p.requires_human_review is True


def test_policy_warnings_non_blocking():
    from src.core.agent_harness.action_policies import policy_warnings
    assert any("sin política" in w for w in policy_warnings("accion_desconocida_xyz"))
    assert policy_warnings("create_iniciativa") == []

