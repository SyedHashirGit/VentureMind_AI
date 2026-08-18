from __future__ import annotations
from app.services import gemini_service
from app.agents.schemas import ValidationResult
from app.agents.prompts import VALIDATION_SYSTEM, build_validation_prompt


async def run_validation(idea: str, founder_context: str | None = None) -> ValidationResult | None:
    """Four scores (each with rationale) plus market/feasibility/risk analysis.
    Returns None on failure so the boardroom degrades gracefully."""
    try:
        return await gemini_service.generate_validated(
            VALIDATION_SYSTEM, build_validation_prompt(idea, founder_context), ValidationResult
        )
    except Exception:
        return None


def to_score_map(v: ValidationResult) -> dict[str, int]:
    return {
        "viability": v.viability.score,
        "marketOpportunity": v.market_opportunity.score,
        "executionDifficulty": v.execution_difficulty.score,
        "fundingAttractiveness": v.funding_attractiveness.score,
    }
