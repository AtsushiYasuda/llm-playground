"""LLM client abstraction supporting OpenAI and Anthropic."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

if TYPE_CHECKING:
    from llm_mcp_server.config import Settings

logger = logging.getLogger(__name__)


class LLMClient:
    """Unified async client for OpenAI / Anthropic APIs."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._provider = settings.llm_provider
        self._model = settings.llm_model

        if self._provider == "openai":
            self._openai = AsyncOpenAI(
                api_key=settings.openai_api_key,
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

    async def chat(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Send a prompt to the configured LLM and return the text response.

        Raises on API errors instead of silently returning error strings.
        """
        temp = temperature if temperature is not None else self._settings.temperature
        tokens = max_tokens if max_tokens is not None else self._settings.max_tokens

        if self._provider == "openai":
            return await self._chat_openai(prompt, system_prompt, temp, tokens)
        return await self._chat_anthropic(prompt, system_prompt, temp, tokens)

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
