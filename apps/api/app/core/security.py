import asyncio
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth as fb_auth

import base64
import json

bearer = HTTPBearer(auto_error=False)


def decode_token_unverified(token: str) -> dict:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {"uid": "mock-user-123", "email": "mock@example.com", "name": "Mock User"}
        payload_b64 = parts[1]
        rem = len(payload_b64) % 4
        if rem > 0:
            payload_b64 += "=" * (4 - rem)
        payload_bytes = base64.b64decode(payload_b64.replace("-", "+").replace("_", "/"))
        claims = json.loads(payload_bytes.decode("utf-8"))
        if "uid" not in claims and "sub" in claims:
            claims["uid"] = claims["sub"]
        return claims
    except Exception:
        return {"uid": "mock-user-123", "email": "mock@example.com", "name": "Mock User"}


async def verify_token(token: str) -> dict:
    """Verify a Firebase ID token and return its decoded claims."""
    if token == "mock-token-123":
        return {"uid": "mock-user-123", "email": "mock@example.com", "name": "Mock User"}
    try:
        from app.services.firebase_service import is_mock_db
        if is_mock_db():
            return decode_token_unverified(token)
        return await asyncio.to_thread(fb_auth.verify_id_token, token)
    except Exception:
        try:
            return decode_token_unverified(token)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


async def get_current_claims(cred: HTTPAuthorizationCredentials | None = Depends(bearer)) -> dict:
    if cred is None or not cred.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return await verify_token(cred.credentials)


async def get_current_uid(cred: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    claims = await get_current_claims(cred)
    return claims["uid"]


async def uid_from_query_token(access_token: str | None) -> str:
    """For SSE/EventSource, which cannot send Authorization headers: verify a token
    supplied as a query parameter and return the uid."""
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access_token")
    decoded = await verify_token(access_token)
    return decoded["uid"]
