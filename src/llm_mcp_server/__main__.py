"""Entry-point: ``python -m llm_mcp_server`` or ``llm-mcp-server`` CLI."""

from __future__ import annotations

import logging
import sys


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,  # MCP stdio transport uses stdout — logs must go to stderr
    )

    from llm_mcp_server.server import create_server

    server = create_server()

    logger = logging.getLogger(__name__)
    logger.info("Starting llm-mcp-server (stdio)")

    server.run(transport="stdio")


if __name__ == "__main__":
    main()
