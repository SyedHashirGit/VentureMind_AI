from __future__ import annotations
import json
from app.services import gemini_service
from app.agents.schemas import Synthesis
from app.agents.prompts import SAFETY_PREAMBLE

SYN_SYSTEM = SAFETY_PREAMBLE + (
    " You are the board chair. Given seven advisor analyses (ceo, cto, pm, investor, marketing, "
    "competitor, legal), surface the sharpest cross-examinations where one advisor's view challenges "
    "another, then a final consensus. Use the agent ids for fromAgent/toAgent. JSON only."
)


async def run_synthesis(idea: str, analyses: dict) -> Synthesis | None:
    compact = {k: {"summary": v.get("summary"), "risks": v.get("risks")} for k, v in analyses.items()}
    prompt = (
        f"<idea>\n{idea}\n</idea>\n"
        f"Advisor analyses: {json.dumps(compact, default=str)[:6000]}\n\n"
        'Return JSON only: {"challenges":[{"fromAgent","toAgent","point"}],'
        '"consensus":{"agreements":[],"tensions":[],"final_recommendation":"","refined_verdict":""}}'
    )
    try:
        return await gemini_service.generate_validated(SYN_SYSTEM, prompt, Synthesis)
    except Exception:
        return None
