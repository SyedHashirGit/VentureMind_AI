import time
from fastapi import APIRouter, Depends
from app.core.security import get_current_uid
from app.core.errors import NotFoundError
from app.services import firebase_service
from app.services.valkey_service import valkey
from app.agents.sharktank import INVESTORS, generate_questions, score_answer, final_report
from app.schemas import SharkTankStartRequest, SharkTankAnswerRequest

router = APIRouter(prefix="/shark-tank", tags=["shark-tank"])


async def _owned_workspace(workspace_id: str, uid: str) -> dict:
    w = await firebase_service.db_get(f"workspaces/{workspace_id}")
    if not w or w.get("ownerUid") != uid:
        raise NotFoundError("Workspace not found")
    return w


async def _owned_session(session_id: str, uid: str) -> dict:
    s = await firebase_service.db_get(f"sharktankSessions/{session_id}")
    if not s or s.get("ownerUid") != uid:
        raise NotFoundError("Session not found")
    return s


@router.post("/start")
async def start(body: SharkTankStartRequest, uid: str = Depends(get_current_uid)):
    w = await _owned_workspace(body.workspaceId, uid)
    session = {"ownerUid": uid, "workspaceId": body.workspaceId, "status": "active", "createdAt": time.time()}
    sid = await firebase_service.db_push("sharktankSessions", session)
    for inv in INVESTORS:
        await firebase_service.db_set(f"sharktankSessions/{sid}/investors/{inv['id']}", inv)

    verdict = None
    qres = await generate_questions(w["ideaPrompt"], verdict)
    await valkey.bump("analytics:global", "gemini_calls")

    rounds = []
    for q in qres.questions:
        inv = next((i for i in INVESTORS if i["id"] == q.investorId), INVESTORS[0])
        rid = await firebase_service.db_push(f"sharktankSessions/{sid}/rounds", {
            "investorId": q.investorId, "persona": inv["persona"], "question": q.question, "createdAt": time.time(),
        })
        rounds.append({"roundId": rid, "investorId": q.investorId, "persona": inv["persona"], "question": q.question})

    return {"sessionId": sid, "investors": INVESTORS, "rounds": rounds}


@router.post("/answer")
async def answer(body: SharkTankAnswerRequest, uid: str = Depends(get_current_uid)):
    s = await _owned_session(body.sessionId, uid)
    w = await firebase_service.db_get(f"workspaces/{s['workspaceId']}")
    rnd = await firebase_service.db_get(f"sharktankSessions/{body.sessionId}/rounds/{body.roundId}")
    if not rnd:
        raise NotFoundError("Round not found")

    score = await score_answer(w["ideaPrompt"] if w else "", rnd.get("question", ""), body.answer)
    await valkey.bump("analytics:global", "gemini_calls")
    breakdown = score.model_dump()
    await firebase_service.db_update(f"sharktankSessions/{body.sessionId}/rounds/{body.roundId}",
                                     {"answer": body.answer, "scoreBreakdown": breakdown})
    return {"roundId": body.roundId, "scoreBreakdown": breakdown}


@router.post("/{session_id}/finish")
async def finish(session_id: str, uid: str = Depends(get_current_uid)):
    s = await _owned_session(session_id, uid)
    w = await firebase_service.db_get(f"workspaces/{s['workspaceId']}")
    rounds = await firebase_service.db_get(f"sharktankSessions/{session_id}/rounds") or {}
    answered = [r for r in rounds.values() if r.get("scoreBreakdown")]
    if not answered:
        raise NotFoundError("No answered rounds to score")

    avg = round(sum(r["scoreBreakdown"]["overall"] for r in answered) / len(answered))
    summary = "\n".join(f"- {r.get('persona')}: {r['scoreBreakdown']['overall']}/100" for r in answered)
    report = await final_report(w["ideaPrompt"] if w else "", summary, avg)
    await valkey.bump("analytics:global", "gemini_calls")
    result = report.model_dump()
    await firebase_service.db_update(f"sharktankSessions/{session_id}", {"status": "complete", "result": result, "endedAt": time.time()})
    return {"sessionId": session_id, "result": result}


@router.get("/{session_id}")
async def get_session(session_id: str, uid: str = Depends(get_current_uid)):
    s = await _owned_session(session_id, uid)
    rounds = await firebase_service.db_get(f"sharktankSessions/{session_id}/rounds") or {}
    items = []
    for rid, r in (rounds.items() if isinstance(rounds, dict) else []):
        items.append({"roundId": rid, **r})
    items.sort(key=lambda r: r.get("createdAt", 0))
    return {"sessionId": session_id, "status": s.get("status"), "rounds": items, "result": s.get("result")}
