from __future__ import annotations
import asyncio
import json
import httpx
from app.core.config import get_settings

PROTOCOL_VERSION = "2025-06-18"


class BreethError(Exception):
    pass


class BreethClient:
    """Calls Breeth's graph-memory tools over its MCP streamable-HTTP endpoint.

    One bearer token per project (the ck_live_ key). The session is initialized
    lazily and the Mcp-Session-Id is reused across calls. All higher-level callers
    treat failures as non-fatal so memory never blocks the product.
    """

    def __init__(self) -> None:
        s = get_settings()
        self._url = s.breeth_mcp_url
        self._key = s.breeth_api_key
        self._session_id: str | None = None
        self._initialized = False
        self._lock = asyncio.Lock()
        self._id = 0

    def _headers(self) -> dict[str, str]:
        h = {
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": PROTOCOL_VERSION,
        }
        if self._session_id:
            h["Mcp-Session-Id"] = self._session_id
        return h

    def _next_id(self) -> int:
        self._id += 1
        return self._id

    async def _post(self, client: httpx.AsyncClient, payload: dict, expect_response: bool = True):
        resp = await client.post(self._url, headers=self._headers(), json=payload)
        sid = resp.headers.get("mcp-session-id")
        if sid:
            self._session_id = sid
        if not expect_response:
            return None
        if "text/event-stream" in resp.headers.get("content-type", ""):
            return self._parse_sse(resp.text, payload.get("id"))
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _parse_sse(text: str, want_id):
        found = None
        for line in text.splitlines():
            line = line.strip()
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if not data or data == "[DONE]":
                continue
            try:
                msg = json.loads(data)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == want_id:
                found = msg
        return found

    async def _ensure_initialized(self, client: httpx.AsyncClient) -> None:
        if self._initialized:
            return
        async with self._lock:
            if self._initialized:
                return
            await self._post(client, {
                "jsonrpc": "2.0", "id": self._next_id(), "method": "initialize",
                "params": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {"name": "venturemind-ai", "version": "0.7.0"},
                },
            })
            await self._post(client, {"jsonrpc": "2.0", "method": "notifications/initialized"}, expect_response=False)
            self._initialized = True

    async def call_tool(self, name: str, arguments: dict, timeout: float = 20.0):
        async with httpx.AsyncClient(timeout=timeout) as client:
            await self._ensure_initialized(client)
            msg = await self._post(client, {
                "jsonrpc": "2.0", "id": self._next_id(), "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            })
            if not msg:
                raise BreethError("No response from Breeth")
            if "error" in msg:
                self._initialized = False  # force re-init next time on protocol errors
                raise BreethError(str(msg["error"]))
            return msg.get("result")
