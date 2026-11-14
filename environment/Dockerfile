# Agent container ("main"). It holds no simulator code or state: the lab lives in the "sim" service
# and is reachable only through its MCP tools at http://sim:8000/mcp.
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
