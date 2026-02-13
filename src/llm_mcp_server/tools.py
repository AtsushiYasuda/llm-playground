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
    # echo: simple echo (useful for connectivity testing)
    # ------------------------------------------------------------------
    @mcp.tool()
    async def echo(message: str) -> str:
        """Return the provided message as-is (useful for testing connectivity).

        Args:
            message: Text to echo back.
        """
        return message
