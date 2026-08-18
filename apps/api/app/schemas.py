from pydantic import BaseModel, Field
from typing import Optional


class CreateWorkspaceRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    ideaPrompt: str = Field(min_length=10, max_length=4000)
    industry: Optional[str] = None
    stage: Optional[str] = None


class Scores(BaseModel):
    viability: int = 0
    marketOpportunity: int = 0
    executionDifficulty: int = 0
    fundingAttractiveness: int = 0


class WorkspaceOut(BaseModel):
    id: str
    ownerUid: str
    title: str
    ideaPrompt: str
    status: str
    scores: Scores = Scores()


class SharkTankStartRequest(BaseModel):
    workspaceId: str


class SharkTankAnswerRequest(BaseModel):
    sessionId: str
    roundId: str
    answer: str = Field(min_length=1, max_length=4000)
