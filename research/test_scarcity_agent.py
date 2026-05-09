import pytest
from scarcity_agent import ScarcityAgent

def test_analyze_suitability():
    agent = ScarcityAgent(api_key="test_key")  # Mock key for testing
    score = agent.analyze_suitability({"price": 1000, "category": "luxury"})
    assert 0 <= score <= 1

def test_heuristic_scarcity_copy():
    agent = ScarcityAgent(api_key="test_key")
    copy = agent._heuristic_scarcity_copy("Test Product", "Great product", "medium")
    assert "Test Product" in copy
    assert "Great product" in copy

def test_calibrate_trust_level():
    agent = ScarcityAgent(api_key="test_key")
    result = agent.calibrate_trust_level("Normal copy")
    assert "status" in result
    assert "score" in result