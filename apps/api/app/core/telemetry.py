def compute_telemetry(stats: dict) -> dict:
    """Pure aggregation of the analytics:global counters into the telemetry payload."""
    hits = stats.get("cache_hits", 0)
    misses = stats.get("cache_misses", 0)
    total = hits + misses
    return {
        "cacheHits": hits,
        "cacheMisses": misses,
        "cacheHitRate": round(hits / total, 3) if total else 0.0,
        "geminiCalls": stats.get("gemini_calls", 0),
        "geminiSaved": stats.get("gemini_saved", 0),
        "pubsubMsgs": stats.get("pubsub_msgs", 0),
        "agentRuns": stats.get("agent_runs", 0),
    }
