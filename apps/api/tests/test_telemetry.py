from app.core.telemetry import compute_telemetry


def test_hit_rate_and_passthrough():
    out = compute_telemetry({"cache_hits": 7, "cache_misses": 3, "gemini_calls": 40, "gemini_saved": 56, "pubsub_msgs": 9, "agent_runs": 21})
    assert out["cacheHitRate"] == 0.7
    assert out["geminiSaved"] == 56 and out["pubsubMsgs"] == 9


def test_zero_total_is_safe():
    out = compute_telemetry({})
    assert out["cacheHitRate"] == 0.0 and out["cacheHits"] == 0
