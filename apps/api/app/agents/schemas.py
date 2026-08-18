from __future__ import annotations
from typing import Any
from pydantic import BaseModel, Field


class AgentAnalysis(BaseModel):
    """Common, strictly-validated shape every board agent must return.
    Role-specific detail goes in role_output."""
    summary: str = Field(min_length=1)
    key_points: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    confidence: int = Field(ge=0, le=100, default=50)
    role_output: dict[str, Any] = Field(default_factory=dict)


class ScoreItem(BaseModel):
    score: int = Field(ge=0, le=100)
    rationale: str = Field(min_length=1)


class ValidationResult(BaseModel):
    viability: ScoreItem
    market_opportunity: ScoreItem
    execution_difficulty: ScoreItem
    funding_attractiveness: ScoreItem
    market_size: str
    demand: str
    competition: str
    feasibility: str
    risks: list[str] = Field(default_factory=list)
    verdict: str = Field(min_length=1)


# --- Shark Tank Live ---
class SharkQuestion(BaseModel):
    investorId: str
    question: str = Field(min_length=1)


class SharkQuestions(BaseModel):
    questions: list[SharkQuestion]


class AnswerScore(BaseModel):
    clarity: int = Field(ge=0, le=100)
    defensibility: int = Field(ge=0, le=100)
    market_understanding: int = Field(ge=0, le=100)
    traction: int = Field(ge=0, le=100)
    overall: int = Field(ge=0, le=100)
    feedback: str = Field(min_length=1)


class SharkResult(BaseModel):
    confidenceScore: int = Field(ge=0, le=100)
    fundingProbability: int = Field(ge=0, le=100)
    pitchQuality: int = Field(ge=0, le=100)
    weaknesses: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)


# --- Startup Time Machine ---
class TMStage(BaseModel):
    stage: str
    users: str
    revenue: str
    growth: str
    teamSize: str
    risks: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    fundingNeeds: str


class TMScenario(BaseModel):
    summary: str
    stages: list[TMStage]


class TimeMachineResult(BaseModel):
    optimistic: TMScenario
    realistic: TMScenario
    worstCase: TMScenario


# --- Boardroom rounds 2-3 (cross-examination + consensus) ---
class Challenge(BaseModel):
    fromAgent: str
    toAgent: str
    point: str = Field(min_length=1)


class Consensus(BaseModel):
    agreements: list[str] = Field(default_factory=list)
    tensions: list[str] = Field(default_factory=list)
    final_recommendation: str = Field(min_length=1)
    refined_verdict: str = Field(min_length=1)


class Synthesis(BaseModel):
    challenges: list[Challenge] = Field(default_factory=list)
    consensus: Consensus
