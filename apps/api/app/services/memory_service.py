from __future__ import annotations
import asyncio
from app.services.breeth_client import BreethClient


def _extract_text(result) -> str:
    """MCP tool results carry a content[] array of text blocks."""
    if not result:
        return ""
    content = result.get("content") if isinstance(result, dict) else None
    if not content:
        return ""
    parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    return "\n".join(p for p in parts if p).strip()


class MemoryService:
    """Per-founder graph memory. Each founder gets an isolated Breeth group."""

    def __init__(self) -> None:
        self._client = BreethClient()

    @staticmethod
    def _group(uid: str) -> str:
        return f"f_{uid[:16]}"

    async def remember(self, uid: str, content: str, extract_intent: bool = True) -> None:
        await self._client.call_tool("add_episode", {
            "content": content, "group_id": self._group(uid),
            "extract_intent": extract_intent, "source_description": "venturemind",
        })

    async def record_fact(self, uid: str, subject: str, predicate: str, obj: str) -> None:
        await self._client.call_tool("record_fact", {
            "subject": subject, "predicate": predicate, "object": obj, "group_id": self._group(uid),
        })

    async def search(self, uid: str, query: str, limit: int = 5) -> str:
        res = await self._client.call_tool("search_graph", {
            "query": query, "group_id": self._group(uid), "limit": limit,
        })
        return _extract_text(res)

    async def profile(self, uid: str) -> str:
        res = await self._client.call_tool("get_director_profile", {"group_id": self._group(uid)})
        return _extract_text(res)


memory = MemoryService()


# --- non-fatal helpers used by the orchestrator (memory must never block the product) ---

async def recall_summary(uid: str, idea: str, timeout: float = 6.0) -> str | None:
    try:
        text = await asyncio.wait_for(memory.search(uid, idea, limit=5), timeout)
        return text or None
    except Exception:
        return None


def remember_run(uid: str, idea: str, verdict: str | None, scores: dict) -> None:
    """Fire-and-forget: persist this run to the founder's long-term memory."""
    async def _task():
        try:
            content = (
                f"Founder explored a startup idea: {idea}. "
                f"Boardroom verdict: {verdict or 'n/a'}. Scores: {scores}."
            )
            await memory.remember(uid, content, extract_intent=True)
        except Exception:
            pass
    try:
        asyncio.create_task(_task())
    except RuntimeError:
        pass
