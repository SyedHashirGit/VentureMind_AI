from __future__ import annotations
import json
import time
from app.agents.base import AGENTS
from app.agents.validation import run_validation, to_score_map
from app.agents.synthesis import run_synthesis
from app.core.prompt_safety import sanitize_idea
from app.services.valkey_service import valkey
from app.services import firebase_service, gemini_service, semantic_cache
from app.services.memory_service import recall_summary, remember_run

ZERO_SCORES = {"viability": 0, "marketOpportunity": 0, "executionDifficulty": 0, "fundingAttractiveness": 0}
BOARD_COST = 1 + len(AGENTS) + 1  # validation + agents + synthesis


async def _emit(workspace_id: str, message: dict) -> None:
    await valkey.publish(f"boardroom:{workspace_id}", message)
    await valkey.bump("analytics:global", "pubsub_msgs")
    await valkey.xadd(f"boardroom:log:{workspace_id}", {
        "agent": message["agent"], "role": message["role"], "data": json.dumps(message["content"], default=str),
    })
    await firebase_service.db_push(f"workspaces/{workspace_id}/boardroom", message)


async def _replay_synthesis(workspace_id: str, synthesis: dict) -> None:
    for ch in synthesis.get("challenges", []):
        await _emit(workspace_id, {"agent": ch.get("fromAgent", "boardroom"), "role": "challenge",
                                   "content": {"toAgent": ch.get("toAgent"), "point": ch.get("point")}, "ts": time.time()})
    if synthesis.get("consensus"):
        await _emit(workspace_id, {"agent": "consensus", "role": "consensus",
                                   "content": synthesis["consensus"], "ts": time.time()})


async def run_boardroom(workspace_id: str, uid: str, raw_idea: str) -> dict:
    """Validation verdict + four scores, the seven-member board (round 1), then
    cross-examination + consensus (rounds 2-3, one synthesis call). Schema-validated,
    streamed over Valkey Pub/Sub, persisted to RTDB. A semantic cache short-circuits
    the whole run for a near-identical idea with zero Gemini calls. Founder memory
    (Breeth) personalizes the analysis and records the run."""
    idea = sanitize_idea(raw_idea)
    ctx_key = f"boardroom:ctx:{workspace_id}"

    founder_context = await recall_summary(uid, idea)

    embedding: list[float] | None = None
    try:
        embedding = await gemini_service.embed(idea)
    except Exception:
        embedding = None

    cached = await semantic_cache.lookup(embedding) if embedding else None
    if cached:
        scores = cached.get("scores", dict(ZERO_SCORES))
        await firebase_service.db_update(f"workspaces/{workspace_id}", {"scores": scores})
        if cached.get("validation"):
            await _emit(workspace_id, {"agent": "validation", "role": "verdict",
                                       "content": cached["validation"], "ts": time.time(), "cached": True})
        for agent_id, payload in cached.get("analyses", {}).items():
            await _emit(workspace_id, {"agent": agent_id, "role": "analysis",
                                       "content": payload, "ts": time.time(), "cached": True})
        if cached.get("synthesis"):
            await _replay_synthesis(workspace_id, cached["synthesis"])
        await valkey.bump("analytics:global", "gemini_saved", BOARD_COST)
        remember_run(uid, idea, (cached.get("validation") or {}).get("verdict"), scores)
        return {**cached, "cacheHit": True}

    await valkey.bump("analytics:global", "cache_misses")

    # 1) Validation -> scores + verdict
    validation = await run_validation(idea, founder_context)
    await valkey.bump("analytics:global", "gemini_calls")
    scores = to_score_map(validation) if validation else dict(ZERO_SCORES)
    await firebase_service.db_update(f"workspaces/{workspace_id}", {"scores": scores})
    if validation:
        await firebase_service.db_push(f"workspaces/{workspace_id}/analyses", {
            "type": "validation", "payload": validation.model_dump(),
            "model": "gemini", "cacheHit": False, "createdAt": time.time(),
        })
        await _emit(workspace_id, {"agent": "validation", "role": "verdict",
                                   "content": validation.model_dump(), "ts": time.time()})

    shared = {"idea": idea, "scores": scores,
              "verdict": validation.verdict if validation else None,
              "founder_context": founder_context}

    # 2) Round 1: independent analysis, streamed
    analyses: dict[str, dict] = {}
    for agent_id, agent in AGENTS.items():
        result = await agent.analyze(idea, shared)
        await valkey.bump("analytics:global", "gemini_calls")
        await valkey.bump("analytics:global", "agent_runs")
        payload = result.model_dump()
        analyses[agent_id] = payload
        await valkey.client.custom_command(["HSET", ctx_key, agent_id, json.dumps(payload)])
        await _emit(workspace_id, {"agent": agent_id, "role": "analysis", "content": payload, "ts": time.time()})

    # 3) Rounds 2-3: cross-examination + consensus
    synthesis = await run_synthesis(idea, analyses)
    synthesis_payload = None
    if synthesis:
        await valkey.bump("analytics:global", "gemini_calls")
        synthesis_payload = synthesis.model_dump()
        await _replay_synthesis(workspace_id, synthesis_payload)

    result_payload = {
        "scores": scores,
        "validation": validation.model_dump() if validation else None,
        "analyses": analyses,
        "synthesis": synthesis_payload,
    }
    await semantic_cache.store(idea, result_payload, embedding or [])
    remember_run(uid, idea, validation.verdict if validation else None, scores)
    return {**result_payload, "cacheHit": False}
