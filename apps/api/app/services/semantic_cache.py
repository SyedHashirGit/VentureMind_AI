from __future__ import annotations
import json
import hashlib
import numpy as np
from app.services.valkey_service import valkey
from app.core.config import get_settings

CACHE_INDEX = "analysis_cache_idx"
KB_INDEX = "kb_idx"


def _vec_bytes(embedding: list[float]) -> bytes:
    return np.asarray(embedding, dtype=np.float32).tobytes()


async def ensure_indexes() -> None:
    """Create the HNSW vector indexes if the valkey-search module is present.
    Safe and idempotent; if the module is missing, caching simply no-ops later."""
    s = get_settings()
    dim = str(s.embedding_dim)
    for name, prefix in ((CACHE_INDEX, "cache:analysis:"), (KB_INDEX, "kb:")):
        try:
            await valkey.ft_command([
                "FT.CREATE", name, "ON", "HASH", "PREFIX", "1", prefix, "SCHEMA",
                "payload", "TEXT",
                "embedding", "VECTOR", "HNSW", "6",
                "TYPE", "FLOAT32", "DIM", dim, "DISTANCE_METRIC", "COSINE",
            ])
        except Exception:
            pass  # already exists, or module not loaded


async def lookup(embedding: list[float]) -> dict | None:
    """Return a cached analysis whose idea is semantically near, else None.
    Never raises: any failure (module missing, parse error) is treated as a miss."""
    if not embedding:
        return None
    s = get_settings()
    try:
        reply = await valkey.ft_command([
            "FT.SEARCH", CACHE_INDEX,
            "*=>[KNN 1 @embedding $vec AS dist]",
            "PARAMS", "2", "vec", _vec_bytes(embedding),
            "SORTBY", "dist", "RETURN", "2", "payload", "dist",
            "DIALECT", "2",
        ])
        payload, dist = _parse_first_hit(reply)
        if payload is None or dist is None:
            return None
        if dist <= s.semantic_cache_threshold:
            await valkey.bump("analytics:global", "cache_hits")
            return json.loads(payload)
        return None
    except Exception:
        return None


async def store(idea: str, payload: dict, embedding: list[float]) -> None:
    """Cache an analysis keyed by its semantic embedding. Never raises."""
    if not embedding:
        return
    s = get_settings()
    key = "cache:analysis:" + hashlib.sha256(idea.encode("utf-8")).hexdigest()[:24]
    try:
        await valkey.ft_command([
            "HSET", key, "payload", json.dumps(payload), "embedding", _vec_bytes(embedding),
        ])
        await valkey.expire(key, s.semantic_cache_ttl)
    except Exception:
        pass


def _decode(v):
    return v.decode() if isinstance(v, (bytes, bytearray)) else v


def _parse_first_hit(reply):
    """Tolerantly parse the first FT.SEARCH hit's payload + dist across reply shapes."""
    try:
        if isinstance(reply, dict):
            results = reply.get("results") or reply.get(b"results")
            if results:
                fields = results[0].get("extra_attributes") or results[0].get("fields") or {}
                fields = {_decode(k): _decode(v) for k, v in fields.items()}
                return fields.get("payload"), float(fields.get("dist"))
        if isinstance(reply, (list, tuple)) and len(reply) >= 3:
            field_array = reply[2]
            flat = {}
            for i in range(0, len(field_array) - 1, 2):
                flat[_decode(field_array[i])] = _decode(field_array[i + 1])
            return flat.get("payload"), float(flat.get("dist"))
    except Exception:
        return None, None
    return None, None
