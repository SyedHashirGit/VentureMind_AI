from __future__ import annotations
import json
import asyncio
from typing import Optional, Any
from app.core.config import get_settings

try:
    from glide import GlideClient, GlideClientConfiguration, NodeAddress
    _GLIDE_AVAILABLE = True
except ImportError:
    _GLIDE_AVAILABLE = False
    GlideClient = None  # type: ignore[assignment,misc]
    GlideClientConfiguration = None  # type: ignore[assignment,misc]
    NodeAddress = None  # type: ignore[assignment,misc]


class MockGlideClient:
    def __init__(self) -> None:
        self._db: dict[str, Any] = {}
        self._streams: dict[str, list[dict]] = {}
        self._pubsub_queues: dict[str, list[asyncio.Queue]] = {}

    async def custom_command(self, args: list[str]) -> Any:
        cmd = args[0].upper()
        if cmd == "HSET":
            key = args[1]
            if key not in self._db:
                self._db[key] = {}
            for i in range(2, len(args), 2):
                f = args[i]
                v = args[i+1]
                self._db[key][f] = v
            return len(args) // 2
        elif cmd == "HINCRBY":
            key = args[1]
            field = args[2]
            by = int(args[3])
            if key not in self._db:
                self._db[key] = {}
            val = int(self._db[key].get(field, 0)) + by
            self._db[key][field] = str(val)
            return val
        elif cmd == "HGETALL":
            key = args[1]
            return self._db.get(key, {})
        elif cmd == "PUBLISH":
            channel = args[1]
            message = args[2]
            queues = self._pubsub_queues.get(channel, [])
            for q in queues:
                q.put_nowait(message)
            return len(queues)
        elif cmd == "XADD":
            stream = args[1]
            fields = {}
            try:
                star_idx = args.index("*")
                start_idx = star_idx + 1
            except ValueError:
                start_idx = 2
            for i in range(start_idx, len(args), 2):
                k = args[i]
                v = args[i+1]
                fields[k] = v
            if stream not in self._streams:
                self._streams[stream] = []
            self._streams[stream].append(fields)
            return "1-0"
        return None

    async def set(self, key: str, value: str) -> None:
        self._db[key] = value

    async def get(self, key: str) -> str | None:
        return self._db.get(key)

    async def incr(self, key: str) -> int:
        val = int(self._db.get(key, 0)) + 1
        self._db[key] = str(val)
        return val

    async def expire(self, key: str, ttl: int) -> None:
        pass

    async def close(self) -> None:
        pass


_mock_client: Optional[MockGlideClient] = None


def get_mock_client() -> MockGlideClient:
    global _mock_client
    if _mock_client is None:
        _mock_client = MockGlideClient()
    return _mock_client


class ValkeyService:
    """Single backend-owned Valkey (GLIDE) connection.

    Generic ops + pub/sub publish are implemented here. Semantic cache and
    vector search (valkey-search FT.* commands) are layered in Phase 6 using
    `ft_command`, which already gives raw access to the module.
    """

    def __init__(self) -> None:
        self._client: Optional[GlideClient] = None

    async def connect(self) -> None:
        if not _GLIDE_AVAILABLE:
            print("[Valkey] valkey-glide not installed. Running in Mock/In-Memory mode.")
            self._client = None
            return
        s = get_settings()
        config = GlideClientConfiguration(
            addresses=[NodeAddress(host=s.valkey_host, port=s.valkey_port)],
            use_tls=s.valkey_use_tls,
        )
        try:
            self._client = await GlideClient.create(config)
            print("[Valkey] Successfully connected to Valkey server.")
        except Exception as exc:
            print(f"[Valkey] Failed to connect to Valkey at {s.valkey_host}:{s.valkey_port}. "
                  f"Falling back to Mock/In-Memory mode. Error: {exc}")
            self._client = None

    async def close(self) -> None:
        if self._client is not None:
            await self._client.close()

    @property
    def client(self) -> "GlideClient | MockGlideClient":
        if self._client is None:
            return get_mock_client()
        return self._client

    # --- generic key ops ---
    async def set(self, key: str, value: str, ttl: int | None = None) -> None:
        await self.client.set(key, value)
        if ttl:
            await self.client.expire(key, ttl)

    async def get(self, key: str):
        return await self.client.get(key)

    async def incr(self, key: str) -> int:
        return await self.client.incr(key)

    async def expire(self, key: str, ttl: int) -> None:
        await self.client.expire(key, ttl)

    # --- analytics counters ---
    async def bump(self, hash_key: str, field: str, by: int = 1) -> None:
        await self.client.custom_command(["HINCRBY", hash_key, field, str(by)])

    # --- pub/sub (publish side) ---
    async def publish(self, channel: str, message: dict) -> None:
        await self.client.custom_command(["PUBLISH", channel, json.dumps(message, default=str)])

    # --- event log stream (agent workflow replay) ---
    async def xadd(self, stream: str, fields: dict) -> None:
        args = ["XADD", stream, "MAXLEN", "~", "500", "*"]
        for k, v in fields.items():
            args += [k, v if isinstance(v, str) else str(v)]
        await self.client.custom_command(args)

    async def analytics(self) -> dict:
        raw = await self.client.custom_command(["HGETALL", "analytics:global"])
        out: dict[str, int] = {}
        if isinstance(raw, dict):
            for k, v in raw.items():
                kk = k.decode() if isinstance(k, (bytes, bytearray)) else k
                vv = v.decode() if isinstance(v, (bytes, bytearray)) else v
                try: out[kk] = int(vv)
                except (TypeError, ValueError): pass
        elif isinstance(raw, (list, tuple)):
            for i in range(0, len(raw) - 1, 2):
                k = raw[i].decode() if isinstance(raw[i], (bytes, bytearray)) else raw[i]
                v = raw[i + 1].decode() if isinstance(raw[i + 1], (bytes, bytearray)) else raw[i + 1]
                try: out[k] = int(v)
                except (TypeError, ValueError): pass
        return out

    # --- raw access for valkey-search FT.* (Phase 6) ---
    async def ft_command(self, args: list[str]):
        return await self.client.custom_command(args)


valkey = ValkeyService()
