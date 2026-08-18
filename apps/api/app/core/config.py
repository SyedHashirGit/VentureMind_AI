from functools import lru_cache
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven configuration. No secret is ever hardcoded."""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    cors_origin_regex: str = ""  # e.g. https://.*\.vercel\.app to allow preview deploys

    # Firebase Realtime Database
    firebase_db_url: str = ""
    google_application_credentials: str = ""  # path to service-account JSON (local dev)
    firebase_service_account_json: str = ""    # raw JSON string (managed hosts: Render/Railway)

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_embedding_model: str = "text-embedding-004"
    embedding_dim: int = 768

    # Breeth (long-term founder memory)
    breeth_api_key: str = ""
    breeth_base_url: str = "https://api.thebreeth.com"

    # Valkey
    valkey_host: str = "localhost"
    valkey_port: int = 6379
    valkey_use_tls: bool = False
    valkey_password: str = ""

    # Cache / limits
    semantic_cache_ttl: int = 3600
    semantic_cache_threshold: float = 0.15
    rate_limit_per_min: int = 30

    # Gemini free-tier pacing (stay under the free RPM; cache absorbs the rest)
    gemini_max_rpm: int = 12
    gemini_min_interval_ms: int = 250

    # Breeth (graph memory) over its MCP endpoint
    breeth_mcp_url: str = "https://mcp.thebreeth.com/mcp"


@lru_cache
def get_settings() -> Settings:
    return Settings()
