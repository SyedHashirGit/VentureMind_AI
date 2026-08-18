import time
from fastapi import APIRouter, Depends
from app.core.security import get_current_claims
from app.services import firebase_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/bootstrap")
async def bootstrap(claims: dict = Depends(get_current_claims)):
    """Ensure a /users/{uid} record exists on first login; return the profile.
    Called by the client immediately after sign-in."""
    uid = claims["uid"]
    now = time.time()
    existing = await firebase_service.db_get(f"users/{uid}")
    if existing:
        await firebase_service.db_update(f"users/{uid}", {"lastActiveAt": now})
        return {"uid": uid, **existing, "lastActiveAt": now}

    email = claims.get("email") or ""
    profile = {
        "displayName": claims.get("name") or (email.split("@")[0] if email else "Founder"),
        "email": email or None,
        "photoURL": claims.get("picture"),
        "plan": "free",
        "createdAt": now,
        "lastActiveAt": now,
    }
    await firebase_service.db_set(f"users/{uid}", profile)
    return {"uid": uid, **profile}
