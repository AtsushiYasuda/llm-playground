"""MCP server definition and resource registration."""

from __future__ import annotations

import json
import logging

from mcp.server.fastmcp import FastMCP

from llm_mcp_server.config import Settings, load_settings
from llm_mcp_server.llm_client import LLMClient
from llm_mcp_server.tools import register_tools

logger = logging.getLogger(__name__)

_json = lambda obj: json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def create_server(settings: Settings | None = None) -> FastMCP:
    """Build and return a fully configured MCP server."""
    if settings is None:
        settings = load_settings()

    mcp = FastMCP("llm-mcp-server")
    llm = LLMClient(settings)

    # --- Resources -----------------------------------------------------------

    @mcp.resource("llm://status")
    def llm_status() -> str:
        """Current LLM configuration and context optimization settings."""
        return _json({
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "max_tokens": settings.max_tokens,
            "max_response_chars": settings.max_response_chars,
            "summarize_threshold": settings.summarize_threshold,
            "cache": llm.cache_info,
        })

    # --- Tools ---------------------------------------------------------------

    register_tools(mcp, llm)

    return mcp
