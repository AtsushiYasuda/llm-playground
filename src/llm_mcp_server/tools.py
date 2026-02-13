"""Tool implementations registered on the MCP server."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from llm_mcp_server.llm_client import LLMClient
    from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def register_tools(mcp: FastMCP, llm: LLMClient) -> None:
    """Register all tools on the given MCP server instance."""

    # ------------------------------------------------------------------
    # llm_query: send an arbitrary prompt to the configured LLM
    # ------------------------------------------------------------------
    @mcp.tool()
    async def llm_query(prompt: str, system_prompt: str = "") -> str:
        """Send a prompt to the configured LLM and return its response.

        Args:
            prompt: The user prompt to send.
            system_prompt: Optional system prompt for context / instructions.
        """
        logger.info("llm_query called (model=%s)", llm.model)
        return await llm.chat(prompt, system_prompt=system_prompt)

    # ------------------------------------------------------------------
    # calculator: basic arithmetic
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
        result = ops[operation]()
        return json.dumps({"result": result, "expression": f"{a} {operation} {b}"})

    # ------------------------------------------------------------------
    # code_review: LLM-powered code review
    # ------------------------------------------------------------------
    @mcp.tool()
    async def code_review(
        code: str,
        language: str = "",
        focus: str = "",
    ) -> str:
        """Review code using the configured LLM and return feedback.

        Args:
            code: Source code to review.
            language: Programming language (e.g. "python", "typescript"). Auto-detected if omitted.
            focus: Optional review focus area (e.g. "security", "performance", "readability").
        """
        logger.info("code_review called (model=%s, language=%s)", llm.model, language or "auto")

        lang_hint = f"Language: {language}\n" if language else ""
        focus_hint = f"Focus especially on: {focus}\n" if focus else ""

        system = (
            "You are an expert code reviewer. "
            "Provide clear, actionable feedback organized into sections: "
            "Issues (bugs/errors), Suggestions (improvements), and Good Points (what's done well). "
            "Be concise. Use the same language as the code comments or default to the user's language."
        )
        prompt = f"""{lang_hint}{focus_hint}
Review the following code:

```
{code}
```"""

        return await llm.chat(prompt, system_prompt=system)

    # ------------------------------------------------------------------
    # echo: simple echo (useful for connectivity testing)
    # ------------------------------------------------------------------
    @mcp.tool()
    async def echo(message: str) -> str:
        """Return the provided message as-is (useful for testing connectivity).

        Args:
            message: Text to echo back.
        """
        return message
