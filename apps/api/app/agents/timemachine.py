from __future__ import annotations
from app.services import gemini_service
from app.agents.schemas import TimeMachineResult
from app.agents.prompts import SAFETY_PREAMBLE

TM_SYSTEM = SAFETY_PREAMBLE + (
    " You are a startup forecaster. Project realistic, idea-specific trajectories across three scenarios. "
    "Numbers should be plausible ranges, not fantasy. JSON only."
)

TM_CONTRACT = (
    "Return JSON only with keys optimistic, realistic, worstCase. Each is "
    '{"summary": str, "stages": [ {"stage","users","revenue","growth","teamSize",'
    '"risks":[],"opportunities":[],"fundingNeeds"} ]}. '
    'Provide exactly these six stages in order: "Month 1","Month 3","Month 6","Year 1","Year 3","Year 5".'
)


async def run_forecast(idea: str, verdict: str | None = None) -> TimeMachineResult:
    prompt = f"<idea>\n{idea}\n</idea>\nContext verdict: {verdict or 'n/a'}\n\n{TM_CONTRACT}"
    return await gemini_service.generate_validated(TM_SYSTEM, prompt, TimeMachineResult)
