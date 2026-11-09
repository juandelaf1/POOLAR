"""CASE adapter mock: solo propuesta, sin autoridad."""
from src.core.adapters.case_mock import propose
from src.core.contracts_case import CaseContractVersion


def test_case_mock_proposes_only():
    p = propose("create_iniciativa", {"inputs": {"x": 1}}, evidence=[{"a": 1}])
    assert p.version == CaseContractVersion.v0
    assert p.action == "create_iniciativa"
    assert p.requires_human_review is True
    assert p.confidence == 0.0
    assert p.evidence[0].synthetic is True
