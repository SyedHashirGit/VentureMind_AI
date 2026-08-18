from fastapi import APIRouter, Request, Query
from sse_starlette.sse import EventSourceResponse
from app.core.security import uid_from_query_token
from app.core.errors import NotFoundError
from app.services import firebase_service
from app.realtime.relay import boardroom_stream

router = APIRouter(prefix="/boardroom", tags=["boardroom"])


@router.get("/{workspace_id}/stream")
async def stream(workspace_id: str, request: Request, access_token: str | None = Query(default=None)):
    uid = await uid_from_query_token(access_token)
    workspace = await firebase_service.db_get(f"workspaces/{workspace_id}")
    if not workspace or workspace.get("ownerUid") != uid:
        raise NotFoundError("Workspace not found")
    return EventSourceResponse(boardroom_stream(workspace_id, request))
