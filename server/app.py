"""Thin FastMCP server around one `sim.Episode` (one episode per process, seed from GSS_SEED, level from GSS_LEVEL).

Every MCP tool forwards to `Episode.call` and nothing else: no accounting, validation or state
lives here. Parameters are declared with JSON types for the agent's benefit but are NOT validated
by this layer (pydantic `Any`), so malformed calls still reach the sim and are charged there.

Verifier routes (same server): GET /verifier/result and GET /verifier/trajectory need
`Authorization: Bearer <token>` (GSS_VERIFIER_TOKEN, or a random token generated at start-up and
stored only inside this container); anything else gets 404. /verifier/result
auto-submits the episode before scoring, so no tool can act after it. No other routes exist.
"""

from __future__ import annotations

import hmac
import inspect
import os
import secrets
import threading
from typing import Annotated, Any

from fastmcp import FastMCP
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse

from sim import Episode
from sim.episode import TOOL_SPECS

SEED = int(os.environ.get("GSS_SEED", "1"))
LEVEL = int(os.environ.get("GSS_LEVEL", "1"))  # 1 or 2 (90 deg crossing)
TOKEN_FILE = os.environ.get("GSS_TOKEN_FILE", "/run/gss/verifier_token")


def _load_token() -> str:
    """Verifier token: from GSS_VERIFIER_TOKEN, else a fresh random one written to TOKEN_FILE
    (inside the sim container only; read by the collect hook, never visible to the agent)."""
    tok = os.environ.get("GSS_VERIFIER_TOKEN", "")
    if tok:
        return tok
    tok = secrets.token_hex(32)
    try:
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(tok)
    except OSError:
        return ""  # no token file -> verifier routes stay closed (404)
    return tok


TOKEN = _load_token()
EPISODE = Episode(SEED, LEVEL)
LOCK = threading.Lock()

mcp = FastMCP("gss")

JSON_TYPES = {
    "num": {"type": "number"},
    "str": {"type": "string"},
    "bool": {"type": "boolean"},
    "items": {"anyOf": [{"type": "array", "items": {"type": "string"}},
                        {"type": "object", "additionalProperties": {"type": "integer"}}]},
}


def _make_tool(name: str, spec: dict):
    params = []
    for pname, (typ, required) in spec["params"].items():
        ann = Annotated[Any, Field(json_schema_extra=JSON_TYPES[typ])]
        params.append(inspect.Parameter(pname, inspect.Parameter.KEYWORD_ONLY,
                                        default=inspect.Parameter.empty if required else None,
                                        annotation=ann))

    def tool(**kwargs) -> dict:
        args = {k: v for k, v in kwargs.items() if v is not None}
        with LOCK:
            return EPISODE.call(name, args)

    tool.__name__ = name
    tool.__doc__ = spec["desc"]
    tool.__signature__ = inspect.Signature(params, return_annotation=dict)
    tool.__annotations__ = {p.name: p.annotation for p in params} | {"return": dict}
    mcp.tool(tool, name=name, description=spec["desc"])


for _name, _spec in TOOL_SPECS.items():
    _make_tool(_name, _spec)


def _authorised(request: Request) -> bool:
    if not TOKEN:
        return False
    got = request.headers.get("authorization", "")
    return hmac.compare_digest(got.encode(), f"Bearer {TOKEN}".encode())


@mcp.custom_route("/verifier/result", methods=["GET"], include_in_schema=False)
async def verifier_result(request: Request):
    if not _authorised(request):
        return PlainTextResponse("Not Found", status_code=404)
    with LOCK:
        return JSONResponse(EPISODE.result())


@mcp.custom_route("/verifier/trajectory", methods=["GET"], include_in_schema=False)
async def verifier_trajectory(request: Request):
    if not _authorised(request):
        return PlainTextResponse("Not Found", status_code=404)
    with LOCK:
        return JSONResponse({"seed": SEED, "trajectory": EPISODE.trajectory()})


def main():
    mcp.run(transport="streamable-http", host=os.environ.get("GSS_HOST", "0.0.0.0"),
            port=int(os.environ.get("GSS_PORT", "8000")), show_banner=False)


if __name__ == "__main__":
    main()
