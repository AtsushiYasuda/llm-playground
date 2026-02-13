"""Tool implementations registered on the MCP server."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_mcp_server.llm_client import LLMClient
    from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

# Compact JSON: no extra whitespace → fewer tokens in context
_json = lambda obj: json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def register_tools(mcp: FastMCP, llm: LLMClient) -> None:
    """Register all tools on the given MCP server instance."""

    # ------------------------------------------------------------------
    # llm_query: send an arbitrary prompt to the configured LLM
    # ------------------------------------------------------------------
    @mcp.tool()
    async def llm_query(
        prompt: str,
        system_prompt: str = "",
        max_length: int = 0,
    ) -> str:
        """Send a prompt to the configured LLM and return its response.

        Args:
            prompt: The user prompt to send.
            system_prompt: Optional system prompt for context / instructions.
            max_length: Max response chars (0 = use server default).
        """
        logger.info("llm_query called (model=%s)", llm.model)
        kwargs: dict = {"system_prompt": system_prompt}
        if max_length > 0:
            kwargs["max_response_chars"] = max_length
        return await llm.chat(prompt, **kwargs)

    # ------------------------------------------------------------------
    # code_review: LLM-powered code review
    # ------------------------------------------------------------------
    @mcp.tool()
    async def code_review(
        code: str,
        language: str = "",
        focus: str = "",
        max_length: int = 0,
    ) -> str:
        """Review code using the configured LLM and return concise feedback.

        Args:
            code: Source code to review.
            language: Programming language (e.g. "python"). Auto-detected if omitted.
            focus: Review focus (e.g. "security", "performance", "readability").
            max_length: Max response chars (0 = use server default).
        """
        logger.info("code_review called (model=%s, lang=%s)", llm.model, language or "auto")

        parts = []
        if language:
            parts.append(f"Language: {language}")
        if focus:
            parts.append(f"Focus: {focus}")
        parts.append(f"Review this code:\n```\n{code}\n```")

        system = (
            "You are an expert code reviewer. "
            "Reply with short, actionable bullet points under: "
            "Issues, Suggestions, Good Points. "
            "Omit empty sections. Be concise."
        )

        kwargs: dict = {"system_prompt": system}
        if max_length > 0:
            kwargs["max_response_chars"] = max_length
        return await llm.chat("\n".join(parts), **kwargs)

    # ------------------------------------------------------------------
    # calculator: basic arithmetic (compact output)
    # ------------------------------------------------------------------
    @mcp.tool()
    async def calculator(a: float, b: float, operation: str) -> str:
        """Perform basic arithmetic (add, sub, mul, div).

        Args:
            a: First operand.
            b: Second operand.
            operation: One of "add", "sub", "mul", "div".
        """
        ops = {
            "add": lambda: a + b,
            "sub": lambda: a - b,
            "mul": lambda: a * b,
            "div": lambda: a / b,
        }
        if operation not in ops:
            raise ValueError(f"Unknown operation: {operation!r}. Use add/sub/mul/div.")
        if operation == "div" and b == 0:
            raise ValueError("Division by zero.")
        return _json({"result": ops[operation]()})

    # ------------------------------------------------------------------
    # echo: connectivity test (minimal output)
    # ------------------------------------------------------------------
    @mcp.tool()
    async def echo(message: str) -> str:
        """Echo a message back (connectivity test).

        Args:
            message: Text to echo back.
        """
        return message
