"""LLM client abstraction supporting OpenAI and Anthropic."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from llm_mcp_server.context import ResponseCache, estimate_tokens, truncate

if TYPE_CHECKING:
    from llm_mcp_server.config import Settings

logger = logging.getLogger(__name__)

_SUMMARIZE_SYSTEM = (
    "Condense the following text into a concise summary. "
    "Keep all key facts, code snippets, and actionable items. "
    "Remove filler, repetition, and verbose explanations. "
    "Output the summary only — no preamble."
)


class LLMClient:
    """Unified async client for OpenAI / Anthropic APIs with context optimization."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._provider = settings.llm_provider
        self._model = settings.llm_model

        self._cache: ResponseCache | None = None
        if settings.cache_enabled:
            self._cache = ResponseCache(ttl=settings.cache_ttl_seconds)

        if self._provider == "openai":
            self._openai = AsyncOpenAI(
                api_key=settings.openai_api_key,
                timeout=settings.timeout_seconds,
            )
        elif self._provider == "openrouter":
            self._openai = AsyncOpenAI(
                api_key=settings.openrouter_api_key,
                base_url="https://openrouter.ai/api/v1",
                timeout=settings.timeout_seconds,
            )
        elif self._provider == "anthropic":
            self._anthropic = AsyncAnthropic(
                api_key=settings.anthropic_api_key,
                timeout=settings.timeout_seconds,
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self._provider!r}")

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    @property
    def cache_info(self) -> dict:
        if self._cache is None:
            return {"enabled": False}
        return {"enabled": True, "size": self._cache.size, "ttl": self._cache.ttl}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
        auto_summarize: bool = True,
        max_response_chars: int | None = None,
    ) -> str:
        """Send a prompt and return an optimised response.

        Context-saving pipeline:
        1. Check cache → return cached result if hit
        2. Call LLM API
        3. If response > summarize_threshold, auto-summarize via a second LLM call
        4. Truncate to max_response_chars as a hard safety net
        5. Store in cache
        """
        # 1. Cache lookup
        if self._cache is not None:
            cached = self._cache.get(prompt, system_prompt, self._model)
            if cached is not None:
                return cached

        # 2. Raw LLM call
        temp = temperature if temperature is not None else self._settings.temperature
        tokens = max_tokens if max_tokens is not None else self._settings.max_tokens

        if self._provider in ("openai", "openrouter"):
            raw = await self._chat_openai(prompt, system_prompt, temp, tokens)
        else:
            raw = await self._chat_anthropic(prompt, system_prompt, temp, tokens)

        result = raw
        threshold = self._settings.summarize_threshold
        cap = max_response_chars or self._settings.max_response_chars

        # 3. Auto-summarize long responses
        if auto_summarize and len(result) > threshold:
            logger.info(
                "Response too long (%d chars > %d threshold), auto-summarizing",
                len(result), threshold,
            )
            result = await self._summarize(result)

        # 4. Hard truncation
        result = truncate(result, cap)

        # 5. Cache store
        if self._cache is not None:
            self._cache.put(prompt, system_prompt, self._model, result)

        est = estimate_tokens(result)
        logger.info("Response: %d chars, ~%d tokens", len(result), est)
        return result

    # ------------------------------------------------------------------
    # Provider-specific calls
    # ------------------------------------------------------------------

    async def _chat_openai(
        self, prompt: str, system_prompt: str, temperature: float, max_tokens: int
    ) -> str:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await self._openai.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""

    async def _chat_anthropic(
        self, prompt: str, system_prompt: str, temperature: float, max_tokens: int
    ) -> str:
        kwargs: dict = {
            "model": self._model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = await self._anthropic.messages.create(**kwargs)
        return response.content[0].text

    # ------------------------------------------------------------------
    # Auto-summarization
    # ------------------------------------------------------------------

    async def _summarize(self, text: str) -> str:
        """Ask the LLM to condense *text* into a shorter summary."""
        # Use lower temperature and fewer tokens for deterministic, compact output
        if self._provider in ("openai", "openrouter"):
            return await self._chat_openai(text, _SUMMARIZE_SYSTEM, 0.2, 1024)
        return await self._chat_anthropic(text, _SUMMARIZE_SYSTEM, 0.2, 1024)
