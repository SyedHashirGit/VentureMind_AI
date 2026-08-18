import pytest
from pydantic import ValidationError
from app.agents.schemas import (
    AgentAnalysis, ValidationResult, SharkQuestions, AnswerScore,
    SharkResult, TimeMachineResult, Synthesis,
)


def test_agent_analysis_defaults():
    a = AgentAnalysis.model_validate({"summary": "x", "confidence": 80})
    assert a.key_points == [] and a.risks == [] and a.confidence == 80


def test_agent_analysis_rejects_out_of_range_confidence():
    with pytest.raises(ValidationError):
        AgentAnalysis.model_validate({"summary": "x", "confidence": 150})


def test_validation_result_score_bounds():
    base = {"score": 50, "rationale": "ok"}
    payload = {
        "viability": base, "market_opportunity": base,
        "execution_difficulty": base, "funding_attractiveness": base,
        "market_size": "a", "demand": "b", "competition": "c", "feasibility": "d",
        "risks": [], "verdict": "v",
    }
    assert ValidationResult.model_validate(payload).viability.score == 50
    bad = {**payload, "viability": {"score": 120, "rationale": "x"}}
    with pytest.raises(ValidationError):
        ValidationResult.model_validate(bad)


def test_shark_and_timemachine_and_synthesis():
    SharkQuestions.model_validate({"questions": [{"investorId": "yc", "question": "moat?"}]})
    AnswerScore.model_validate({"clarity": 1, "defensibility": 1, "market_understanding": 1, "traction": 1, "overall": 1, "feedback": "f"})
    SharkResult.model_validate({"confidenceScore": 1, "fundingProbability": 1, "pitchQuality": 1, "weaknesses": [], "improvements": []})
    stage = {"stage": "Month 1", "users": "0", "revenue": "0", "growth": "0", "teamSize": "2",
             "risks": [], "opportunities": [], "fundingNeeds": "boot"}
    scen = {"summary": "s", "stages": [stage]}
    TimeMachineResult.model_validate({"optimistic": scen, "realistic": scen, "worstCase": scen})
    Synthesis.model_validate({"challenges": [{"fromAgent": "investor", "toAgent": "cto", "point": "p"}],
                              "consensus": {"agreements": [], "tensions": [], "final_recommendation": "r", "refined_verdict": "v"}})
