import pytest

from app.agent_loop import agent_loop
from app.tools import ration_entitlement


def test_aay_entitlement():
    result = ration_entitlement("AAY", 4)

    assert result["monthly_entitlement"] == 35
    assert result["card_type"] == "AAY"


def test_phh_entitlement():
    result = ration_entitlement("PHH", 3)

    assert result["monthly_entitlement"] == 15
    assert result["card_type"] == "PHH"


def test_invalid_family_size():
    with pytest.raises(ValueError):
        ration_entitlement("PHH", 0)


def test_invalid_card_type():
    with pytest.raises(ValueError):
        ration_entitlement("XYZ", 4)
        
        
def test_agent_uses_ration_entitlement_tool():
    result = agent_loop(
        question="How much ration will I get?",
        card_type="PHH",
        family_size=3
    )

    assert result["tool_used"] == "ration_entitlement"
    assert result["answer"]["monthly_entitlement"] == 15