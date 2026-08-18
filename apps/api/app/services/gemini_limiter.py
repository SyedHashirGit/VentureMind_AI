from __future__ import annotations
import asyncio
import time
from app.services.valkey_service import valkey
from app.core.config import get_settings

_last_call_ts = 0.0
_spacing_lock = asyncio.Lock()


async def acquire() -> None:
    """Block until it's safe to make a Gemini call under the free-tier budget.

    Two guards: a per-minute ceiling tracked in Valkey (shared across workers), and a
    small minimum spacing between calls so a burst of agent calls doesn't spike RPM.
    """
    s = get_settings()

    # 1) minimum spacing between consecutive calls
    async with _spacing_lock:
        global _last_call_ts
        gap = s.gemini_min_interval_ms / 1000.0
        wait = _last_call_ts + gap - time.monotonic()
        if wait > 0:
            await asyncio.sleep(wait)
        _last_call_ts = time.monotonic()

    # 2) per-minute ceiling in Valkey (best-effort; never blocks forever)
    try:
        for _ in range(60):
            minute = int(time.time()) // 60
            key = f"gemini:rpm:{minute}"
            count = await valkey.incr(key)
            if count == 1:
                await valkey.expire(key, 65)
            if count <= s.gemini_max_rpm:
                return
            # over budget: wait out the remainder of this minute window
            await asyncio.sleep(60 - (int(time.time()) % 60) + 0.05)
    except Exception:
        return  # if Valkey is unavailable, fall back to spacing-only
