import time
from fastapi import APIRouter, Depends
from app.core.security import get_current_uid
from app.core.config import get_settings
from app.core.errors import NotFoundError
from app.services.ratelimit import enforce_rate_limit
from app.services import firebase_service
from app.agents.orchestrator import run_boardroom
from app.schemas import CreateWorkspaceRequest, WorkspaceOut

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceOut)
async def create_workspace(body: CreateWorkspaceRequest, uid: str = Depends(get_current_uid)):
    now = time.time()
    data = {
        "ownerUid": uid,
        "title": body.title,
        "ideaPrompt": body.ideaPrompt,
        "industry": body.industry,
        "stage": body.stage,
        "status": "draft",
        "createdAt": now,
        "updatedAt": now,
        "scores": {"viability": 0, "marketOpportunity": 0, "executionDifficulty": 0, "fundingAttractiveness": 0},
    }
    wid = await firebase_service.db_push("workspaces", data)
    await firebase_service.db_set(f"userWorkspaces/{uid}/{wid}", True)
    return WorkspaceOut(id=wid, ownerUid=uid, title=body.title, ideaPrompt=body.ideaPrompt, status="draft")


@router.get("", response_model=list[WorkspaceOut])
async def list_workspaces(uid: str = Depends(get_current_uid)):
    index = await firebase_service.db_get(f"userWorkspaces/{uid}") or {}
    out: list[WorkspaceOut] = []
    for wid in index.keys():
        w = await firebase_service.db_get(f"workspaces/{wid}")
        if w:
            out.append(WorkspaceOut(
                id=wid, ownerUid=w["ownerUid"], title=w["title"],
                ideaPrompt=w["ideaPrompt"], status=w["status"],
            ))
    return out


@router.post("/{workspace_id}/analyze")
async def analyze(workspace_id: str, uid: str = Depends(get_current_uid)):
    await enforce_rate_limit(uid, get_settings().rate_limit_per_min)
    w = await firebase_service.db_get(f"workspaces/{workspace_id}")
    if not w or w.get("ownerUid") != uid:
        raise NotFoundError("Workspace not found")
    await firebase_service.db_update(f"workspaces/{workspace_id}", {"status": "analyzing"})
    result = await run_boardroom(workspace_id, uid, w["ideaPrompt"])
    await firebase_service.db_update(f"workspaces/{workspace_id}", {"status": "complete"})
    return {"workspaceId": workspace_id, "result": result}


@router.get("/{workspace_id}", response_model=WorkspaceOut)
async def get_workspace(workspace_id: str, uid: str = Depends(get_current_uid)):
    w = await firebase_service.db_get(f"workspaces/{workspace_id}")
    if not w or w.get("ownerUid") != uid:
        raise NotFoundError("Workspace not found")
    from app.schemas import Scores
    return WorkspaceOut(
        id=workspace_id, ownerUid=w["ownerUid"], title=w["title"],
        ideaPrompt=w["ideaPrompt"], status=w["status"],
        scores=Scores(**(w.get("scores") or {})),
    )


@router.get("/{workspace_id}/boardroom")
async def get_boardroom(workspace_id: str, uid: str = Depends(get_current_uid)):
    w = await firebase_service.db_get(f"workspaces/{workspace_id}")
    if not w or w.get("ownerUid") != uid:
        raise NotFoundError("Workspace not found")
    raw = await firebase_service.db_get(f"workspaces/{workspace_id}/boardroom") or {}
    items = list(raw.values()) if isinstance(raw, dict) else []
    items.sort(key=lambda m: m.get("ts", 0))
    return {"messages": items}
