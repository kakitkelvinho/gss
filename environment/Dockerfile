# Agent container ("main"). It holds no simulator code or state: the lab lives in the "sim" service
# and is reachable only through its MCP tools at http://sim:8000/mcp.
FROM node:22-alpine

RUN apk add --no-cache bash coreutils curl git python3 \
    && npm install -g opencode-ai@1.19.5 \
    && opencode --version

WORKDIR /app
