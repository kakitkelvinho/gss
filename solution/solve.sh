#!/bin/bash
# Reference (oracle) run: the scripted expert plays the episode through the MCP server.
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/0.9.7/install.sh | sh
  source "$HOME/.local/bin/env"
fi

uv run --no-project --python 3.12 --with fastmcp==4.2.0 \
  python /solution/reference.py --url "${GSS_MCP_URL:-http://sim:8000/mcp}"
