from __future__ import annotations
from dataclasses import dataclass
from app.services import gemini_service
from app.agents.schemas import AgentAnalysis
from app.agents.prompts import AGENT_BRIEFS, build_analysis_prompt


@dataclass(frozen=True)
class Agent:
    id: str
    name: str
    brief: str

    async def analyze(self, idea: str, shared_context: dict) -> AgentAnalysis:
        try:
            return await gemini_service.generate_validated(
                self.brief, build_analysis_prompt(idea, shared_context), AgentAnalysis
            )
        except Exception as exc:
            # Graceful degradation: one agent failing must not sink the whole board.
            err_str = str(exc)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                summary = (
                    f"{self.name}: Gemini API quota exceeded. "
                    "The free-tier daily limit has been reached. "
                    "Wait until quota resets (usually midnight Pacific) or upgrade your Google AI Studio plan."
                )
            elif "API_KEY" in err_str or "401" in err_str or "403" in err_str:
                summary = f"{self.name}: Gemini API key is invalid or missing. Check GEMINI_API_KEY in .env."
            else:
                summary = f"{self.name} could not complete analysis right now. Error: {err_str[:120]}"
            return AgentAnalysis(summary=summary, confidence=0)


AGENTS: dict[str, Agent] = {
    aid: Agent(aid, name, brief) for aid, (name, brief) in AGENT_BRIEFS.items()
}
