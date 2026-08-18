from __future__ import annotations
import json
import asyncio
import random
from typing import Any, Type, TypeVar
from google import genai
from google.genai import types as genai_types
from pydantic import BaseModel, ValidationError
from app.core.config import get_settings
from app.core.errors import UpstreamError
from app.services import gemini_limiter

_client: genai.Client | None = None
T = TypeVar("T", bound=BaseModel)


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=get_settings().gemini_api_key)
    return _client


def _is_rate_limit(exc: Exception) -> bool:
    name = type(exc).__name__
    return name in ("ResourceExhausted", "TooManyRequests") or "429" in str(exc)


async def generate_json(
    system_prompt: str, user_prompt: str, temperature: float = 0.6, max_retries: int = 2
) -> dict[str, Any]:
    """Structured JSON generation with exponential backoff on rate limits."""
    s = get_settings()
    config = genai_types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json",
        temperature=temperature,
    )
    delay = 1.0
    for attempt in range(max_retries + 1):
        try:
            await gemini_limiter.acquire()
            resp = await _get_client().aio.models.generate_content(
                model=s.gemini_model,
                contents=user_prompt,
                config=config,
            )
            return json.loads(resp.text)
        except Exception as exc:  # noqa: BLE001
            if _is_rate_limit(exc) and attempt < max_retries:
                await asyncio.sleep(delay + random.random())
                delay *= 2
                continue
            raise UpstreamError(f"Gemini generation failed: {exc}") from exc
    raise UpstreamError("Gemini generation failed after retries")


async def generate_validated(
    system_prompt: str, user_prompt: str, model_cls: Type[T], *, temperature: float = 0.6, repair: bool = True
) -> T:
    """Generate, validate against a pydantic schema, and self-repair once on failure."""
    raw = await generate_json(system_prompt, user_prompt, temperature)
    try:
        return model_cls.model_validate(raw)
    except ValidationError as first:
        if not repair:
            raise UpstreamError(f"Model output failed schema validation: {first}") from first
        correction = (
            user_prompt
            + "\n\nYour previous response did not match the required schema. Errors: "
            + str(first)[:400]
            + "\nReturn corrected JSON only, matching the schema exactly."
        )
        raw2 = await generate_json(system_prompt, correction, temperature)
        try:
            return model_cls.model_validate(raw2)
        except ValidationError as second:
            raise UpstreamError(f"Model output failed schema validation after repair: {second}") from second


async def embed(text: str) -> list[float]:
    """Embedding used by the semantic cache and vector KB."""
    s = get_settings()
    try:
        resp = await _get_client().aio.models.embed_content(
            model=s.gemini_embedding_model,
            contents=text,
        )
        return resp.embeddings[0].values
    except Exception as exc:  # noqa: BLE001
        raise UpstreamError(f"Gemini embedding failed: {exc}") from exc
