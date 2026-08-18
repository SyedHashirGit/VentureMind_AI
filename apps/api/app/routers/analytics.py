from fastapi import APIRouter, Depends
from app.core.security import get_current_uid
from app.core.telemetry import compute_telemetry
from app.services.valkey_service import valkey

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/telemetry")
async def telemetry(uid: str = Depends(get_current_uid)):
    return compute_telemetry(await valkey.analytics())
