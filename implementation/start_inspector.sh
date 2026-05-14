#!/usr/bin/env bash
# Run MCP Inspector against the SQLite Lab server
PYTHON="/home/quang_ai/miniconda3/envs/aip/bin/python3.10"
SERVER="$(dirname "$0")/mcp_server.py"

mkdir -p .npm-cache
NPM_CONFIG_CACHE="$PWD/.npm-cache" npx -y @modelcontextprotocol/inspector "$PYTHON" "$SERVER"
