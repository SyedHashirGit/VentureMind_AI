from __future__ import annotations
import re

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
_MAX_LEN = 4000


def sanitize_idea(text: str) -> str:
    """Defang the founder's free-text idea before it enters a prompt.

    The idea is always wrapped in <idea> delimiters and the system prompt instructs
    the model to treat its contents as untrusted data. Here we additionally strip
    control characters, cap length, and neutralize attempts to forge the delimiter.
    """
    if not text:
        return ""
    cleaned = _CONTROL.sub(" ", text)
    cleaned = cleaned.replace("</idea>", "<\u200b/idea>").replace("<idea>", "<\u200bidea>")
    cleaned = cleaned.strip()
    if len(cleaned) > _MAX_LEN:
        cleaned = cleaned[:_MAX_LEN].rstrip() + " \u2026"
    return cleaned
