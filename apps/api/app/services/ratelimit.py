import time
from app.services.valkey_service import valkey
from app.core.errors import RateLimitedError


async def enforce_rate_limit(uid: str, limit: int, window_seconds: int = 60) -> None:
    """Fixed-window limiter on Valkey. Caps Gemini spend and abuse per user."""
    window = int(time.time()) // window_seconds
    key = f"ratelimit:{uid}:{window}"
    count = await valkey.incr(key)
    if count == 1:
        await valkey.expire(key, window_seconds)
    if count > limit:
        raise RateLimitedError("Rate limit exceeded, please slow down")
