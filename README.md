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

## Project Structure

```
src/llm_mcp_server/
  __main__.py    # Entry-point
  config.py      # Settings via pydantic-settings / .env
  llm_client.py  # OpenAI / Anthropic client abstraction
  server.py      # FastMCP server & resource registration
  tools.py       # Tool implementations
```

## License

MIT
