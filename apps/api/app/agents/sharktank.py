from __future__ import annotations
from app.services import gemini_service
from app.agents.schemas import SharkQuestions, AnswerScore, SharkResult
from app.agents.prompts import SAFETY_PREAMBLE

INVESTORS = [
    {"id": "yc", "persona": "Y Combinator Partner", "riskProfile": "high-conviction, fast", "style": "first-principles, blunt"},
    {"id": "sequoia", "persona": "Sequoia Partner", "riskProfile": "market-size obsessed", "style": "probes TAM and moat"},
    {"id": "a16z", "persona": "a16z Partner", "riskProfile": "founder-and-tech driven", "style": "technical defensibility"},
    {"id": "angel", "persona": "Angel Investor", "riskProfile": "early, relationship-led", "style": "why you, why now"},
    {"id": "cvc", "persona": "Corporate VC", "riskProfile": "strategic fit", "style": "distribution and integration"},
]


def _personas() -> str:
    return "\n".join(f"- {i['id']}: {i['persona']} — {i['style']}, {i['riskProfile']}" for i in INVESTORS)


QUESTIONS_SYSTEM = SAFETY_PREAMBLE + (
    " You are a panel of five distinct venture investors at a live pitch. Each asks ONE sharp, "
    "persona-true opening question that exposes a real weakness. Vary the angle across investors. JSON only."
)

SCORE_SYSTEM = SAFETY_PREAMBLE + (
    " You are a rigorous pitch coach scoring a founder's answer to an investor question. Score each "
    "rubric 0-100, calibrated and specific. Reserve high scores for genuinely strong answers. JSON only."
)

REPORT_SYSTEM = SAFETY_PREAMBLE + (
    " You are the lead investor turning a pitch session into a funding-decision brief. Be honest and "
    "actionable. JSON only."
)


async def generate_questions(idea: str, verdict: str | None = None) -> SharkQuestions:
    prompt = (
        f"<idea>\n{idea}\n</idea>\n"
        f"Boardroom verdict (context): {verdict or 'n/a'}\n\n"
        f"Investors:\n{_personas()}\n\n"
        'Return JSON only: {"questions":[{"investorId":"<id>","question":"<one question>"}]} '
        "with exactly one entry per investor id above."
    )
    return await gemini_service.generate_validated(QUESTIONS_SYSTEM, prompt, SharkQuestions)


async def score_answer(idea: str, question: str, answer: str) -> AnswerScore:
    prompt = (
        f"<idea>\n{idea}\n</idea>\n"
        f"Investor question: {question}\n"
        f"Founder answer: {answer}\n\n"
        'Return JSON only: {"clarity":0-100,"defensibility":0-100,"market_understanding":0-100,'
        '"traction":0-100,"overall":0-100,"feedback":"<two sentences>"}'
    )
    return await gemini_service.generate_validated(SCORE_SYSTEM, prompt, AnswerScore)


async def final_report(idea: str, answers_summary: str, avg: int) -> SharkResult:
    prompt = (
        f"<idea>\n{idea}\n</idea>\n"
        f"Average answer score: {avg}. Round-by-round:\n{answers_summary}\n\n"
        'Return JSON only: {"confidenceScore":0-100,"fundingProbability":0-100,"pitchQuality":0-100,'
        '"weaknesses":["..."],"improvements":["..."]}'
    )
    return await gemini_service.generate_validated(REPORT_SYSTEM, prompt, SharkResult)
