"""Configuration via environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Server settings loaded from environment variables / .env file."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    # LLM provider: "openai" or "anthropic"
    llm_provider: str = "openai"

    # Model identifier (e.g. "gpt-4o", "claude-sonnet-4-20250514")
    llm_model: str = "gpt-4o"

    # API keys — at least one must be set depending on the provider
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Request parameters
    timeout_seconds: int = 60
    max_tokens: int = 4096
    temperature: float = 0.7

    # --- Context optimization ------------------------------------------------
    # Maximum characters in a single tool response (truncated beyond this)
    max_response_chars: int = 3000
    # When a response exceeds this char count, auto-summarize via LLM
    summarize_threshold: int = 2000
    # Enable in-memory TTL cache for identical LLM calls
    cache_enabled: bool = True
    # Cache TTL in seconds
    cache_ttl_seconds: int = 300


def load_settings() -> Settings:
    """Create a validated Settings instance."""
    return Settings()
