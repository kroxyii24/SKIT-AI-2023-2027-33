"""
Emergency detector tests.

Coverage philosophy: for a safety-critical module, false negatives (missing
a real emergency) are far worse than false positives (over-flagging). Tests
are weighted accordingly — every positive case below MUST be caught.
"""
import pytest
from app.services.emergency.detector import (
    check_emergency_keywords,
    run_emergency_check,
    build_emergency_response,
    EMERGENCY_HELPLINES,
)


class TestEmergencyDetection:
    @pytest.mark.parametrize("message", [
        "I have severe chest pain and can't breathe",
        "My father is unconscious after a fall",
        "I want to kill myself",
        "She took an overdose of pills",
        "My baby is not moving and I'm worried",
        "He is having a seizure and is unconscious",
        "I think I'm having a heart attack",
        "There was an accident and he is bleeding badly and not moving",
    ])
    def test_detects_true_emergencies(self, message):
        result = check_emergency_keywords(message)
        assert result.is_emergency is True

    @pytest.mark.parametrize("message", [
        "What are the symptoms of diabetes?",
        "How can I prevent dengue fever?",
        "What vaccines does my child need this year?",
        "Tell me about Ayushman Bharat scheme",
        "What foods are good for pregnant women?",
        "I have a mild headache, what could cause it?",
    ])
    def test_does_not_flag_normal_health_queries(self, message):
        result = check_emergency_keywords(message)
        assert result.is_emergency is False

    def test_emergency_response_includes_helpline_numbers(self):
        response = build_emergency_response()
        assert EMERGENCY_HELPLINES["national_emergency"] in response
        assert EMERGENCY_HELPLINES["ambulance"] in response

    def test_emergency_response_never_hedges_or_delays(self):
        response = build_emergency_response()
        # Should not contain soft hedging language that could delay action
        assert "maybe" not in response.lower()
        assert "i think" not in response.lower()

    def test_run_emergency_check_populates_response_message(self):
        result = run_emergency_check("I can't breathe")
        assert result.is_emergency is True
        assert result.response_message is not None
        assert "112" in result.response_message

    def test_run_emergency_check_normal_query_no_message(self):
        result = run_emergency_check("What is malaria?")
        assert result.is_emergency is False
        assert result.response_message is None

    def test_case_insensitivity(self):
        result = check_emergency_keywords("CHEST PAIN and can't BREATHE")
        assert result.is_emergency is True
