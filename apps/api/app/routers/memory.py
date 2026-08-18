from fastapi import APIRouter, Depends, Query
from app.core.security import get_current_uid
from app.services.memory_service import memory

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/profile")
async def profile(uid: str = Depends(get_current_uid)):
    try:
        return {"profile": await memory.profile(uid)}
    except Exception:
        return {"profile": ""}


@router.get("/search")
async def search(q: str = Query(..., min_length=1), uid: str = Depends(get_current_uid)):
    try:
        return {"results": await memory.search(uid, q, limit=8)}
    except Exception:
        return {"results": ""}
