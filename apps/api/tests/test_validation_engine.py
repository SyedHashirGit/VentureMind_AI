import pytest
from app.services import gemini_service
from app.agents.schemas import AgentAnalysis, ValidationResult
from app.agents.validation import to_score_map


def test_to_score_map():
    item = {"score": 0, "rationale": "x"}
    v = ValidationResult.model_validate({
        "viability": {"score": 72, "rationale": "x"},
        "market_opportunity": {"score": 65, "rationale": "x"},
        "execution_difficulty": {"score": 58, "rationale": "x"},
        "funding_attractiveness": {"score": 60, "rationale": "x"},
        "market_size": "a", "demand": "b", "competition": "c", "feasibility": "d",
        "risks": [], "verdict": "v",
    })
    assert to_score_map(v) == {
        "viability": 72, "marketOpportunity": 65, "executionDifficulty": 58, "fundingAttractiveness": 60,
    }


async def test_generate_validated_self_repairs(monkeypatch):
    calls = {"n": 0}

    async def fake_generate_json(system, user, temperature=0.6):
        calls["n"] += 1
        if calls["n"] == 1:
            return {"summary": ""}          # invalid: summary min_length=1 -> triggers repair
        return {"summary": "fixed", "confidence": 50}

    monkeypatch.setattr(gemini_service, "generate_json", fake_generate_json)
    result = await gemini_service.generate_validated("sys", "user", AgentAnalysis)
    assert result.summary == "fixed"
    assert calls["n"] == 2  # one bad attempt, one repair
