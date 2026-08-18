import time
from fastapi import APIRouter, Depends
from app.core.security import get_current_uid
from app.core.config import get_settings
from app.core.errors import NotFoundError
from app.services import firebase_service
from app.services.valkey_service import valkey
from app.services.ratelimit import enforce_rate_limit
from app.agents.timemachine import run_forecast

router = APIRouter(prefix="/time-machine", tags=["time-machine"])


@router.post("/{workspace_id}/run")
async def run(workspace_id: str, uid: str = Depends(get_current_uid)):
    await enforce_rate_limit(uid, get_settings().rate_limit_per_min)
    w = await firebase_service.db_get(f"workspaces/{workspace_id}")
    if not w or w.get("ownerUid") != uid:
        raise NotFoundError("Workspace not found")
    verdict = (w.get("scores") or {})
    forecast = await run_forecast(w["ideaPrompt"], str(verdict))
    await valkey.bump("analytics:global", "gemini_calls")
    payload = forecast.model_dump()
    await firebase_service.db_set(f"timemachineRuns/{workspace_id}", {
        "ownerUid": uid, "workspaceId": workspace_id, "scenarios": payload, "createdAt": time.time(),
    })
    return {"workspaceId": workspace_id, "scenarios": payload}


@router.get("/{workspace_id}")
async def get_latest(workspace_id: str, uid: str = Depends(get_current_uid)):
    run_doc = await firebase_service.db_get(f"timemachineRuns/{workspace_id}")
    if not run_doc or run_doc.get("ownerUid") != uid:
        return {"workspaceId": workspace_id, "scenarios": None}
    return {"workspaceId": workspace_id, "scenarios": run_doc.get("scenarios")}
