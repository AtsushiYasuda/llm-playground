# llm-mcp-server

MCP (Model Context Protocol) server that exposes LLM integration as tools. Works with Claude Code and any MCP-compatible client.

## Setup

```bash
# Install dependencies
pip install -e .

# Copy and edit environment config
cp .env.example .env
```

Set `LLM_PROVIDER` to `openai` or `anthropic` and fill in the corresponding API key.

## Usage

### Run directly

```bash
python -m llm_mcp_server
```

### Claude Code (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "llm": {
      "command": "python",
      "args": ["-m", "llm_mcp_server"],
      "cwd": "/path/to/llm-playground"
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `llm_query` | Send a prompt to the configured LLM and return its response |
| `code_review` | LLM-powered code review with optional language and focus area |
| `calculator` | Basic arithmetic (add / sub / mul / div) |
| `echo` | Echo a message back (connectivity test) |

## Resources

| URI | Description |
|-----|-------------|
| `llm://status` | Current provider, model, and parameter settings |

## Context Optimization

This server implements several strategies to reduce token/context consumption by MCP clients:

| Strategy | Description | Config |
|----------|-------------|--------|
| Auto-summarization | Long LLM responses are automatically condensed via a second LLM call | `SUMMARIZE_THRESHOLD` |
| Hard truncation | Responses exceeding the char limit are truncated at a word boundary | `MAX_RESPONSE_CHARS` |
| TTL cache | Identical prompts return cached results without an API call | `CACHE_ENABLED`, `CACHE_TTL_SECONDS` |
| Compact JSON | Tool results use minimal JSON serialization (no whitespace) | Always on |
| Concise descriptions | Tool docstrings are kept short to minimize tool-definition tokens | Always on |
| Per-call `max_length` | Callers can request shorter responses on a per-tool-call basis | Tool parameter |

## Project Structure

```
src/llm_mcp_server/
  __main__.py    # Entry-point
  config.py      # Settings via pydantic-settings / .env
  context.py     # Token estimation, caching, truncation utilities
  llm_client.py  # OpenAI / Anthropic client with context optimization
  server.py      # FastMCP server & resource registration
  tools.py       # Tool implementations
```

## License

MIT
