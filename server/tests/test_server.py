"""End-to-end tests of the MCP server: a real server process per test module."""

import asyncio
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOKEN = "test-token-123"


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


@pytest.fixture()
def server():
    port = _free_port()
    env = dict(os.environ, GSS_SEED="4", GSS_VERIFIER_TOKEN=TOKEN, GSS_PORT=str(port), GSS_HOST="127.0.0.1")
    proc = subprocess.Popen([sys.executable, "-m", "server.app"], cwd=ROOT, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        try:
            socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
            break
        except OSError:
            time.sleep(0.1)
    yield f"http://127.0.0.1:{port}"
    proc.terminate()
    proc.wait(5)


def get(url, token=None):
    req = urllib.request.Request(url)
    if token is not None:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None


def mcp_calls(base, calls):
    from fastmcp import Client

    async def run():
        out = []
        async with Client(f"{base}/mcp") as c:
            for tool, args in calls:
                if tool == "__list__":
                    out.append([t.name for t in await c.list_tools()])
                else:
                    r = await c.call_tool(tool, args, raise_on_error=False)
                    out.append(r.structured_content)
        return out

    return asyncio.run(run())


def raw_jsonrpc(base, tool, args):
    """Talk to /mcp with plain HTTP (what a curl-wielding agent would do)."""
    hdr = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

    def post(body, sid=None):
        h = dict(hdr)
        if sid:
            h["mcp-session-id"] = sid
        req = urllib.request.Request(f"{base}/mcp", data=json.dumps(body).encode(), headers=h, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.headers.get("mcp-session-id"), r.read().decode()

    sid, _ = post({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                   "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                              "clientInfo": {"name": "curl", "version": "0"}}})
    post({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
    _, body = post({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                    "params": {"name": tool, "arguments": args}}, sid)
    for line in body.splitlines():
        if line.startswith("data:"):
            body = line[5:]
    msg = json.loads(body)
    return json.loads(msg["result"]["content"][0]["text"])


def test_smoke_list_unblock_camera_submit(server):
    names, r1, r2, r3, r4 = mcp_calls(server, [("__list__", {}), ("unblock", {"arm": "opa"}),
                                               ("view_camera", {"plane": "sample"}), ("submit", {}),
                                               ("unblock", {"arm": "800nm"})])
    assert {"place", "knob", "scan", "submit", "ir_card"} <= set(names)
    assert not any("state" in n or "debug" in n or "verif" in n for n in names)
    assert r1["outcome"] == "opa shutter open"
    assert r2["spots"] == []
    assert r3["outcome"].startswith("submitted")
    assert r4 == {"error": "episode over"}  # tools after submit change nothing
    code, res = get(f"{server}/verifier/result", TOKEN)
    assert code == 200 and res["ended_by"] == "agent" and res["tool_calls"] == 3


def test_verifier_needs_token_and_autosubmits(server):
    assert get(f"{server}/verifier/result")[0] == 404
    assert get(f"{server}/verifier/result", "wrong")[0] == 404
    assert get(f"{server}/verifier/trajectory")[0] == 404
    for path in ("/state", "/debug", "/admin", "/verifier", "/"):
        assert get(server + path, TOKEN)[0] == 404
    mcp_calls(server, [("buy", {"items": ["MIR-1"]})])
    code, res = get(f"{server}/verifier/result", TOKEN)
    assert code == 200
    assert res["reward"] == 0.0 and res["cost_eur"] == 150 and res["ended_by"] == "verifier"
    assert mcp_calls(server, [("status", {})])[0] == {"error": "episode over"}
    code, tr = get(f"{server}/verifier/trajectory", TOKEN)
    assert code == 200 and [s["tool"] for s in tr["trajectory"]] == ["buy"]
    assert "truth" in tr["trajectory"][0]


def test_raw_http_goes_through_the_same_accounting(server):
    r = raw_jsonrpc(server, "read_signal", {"t_int": 10})
    assert r["lab_time_used_min"] == pytest.approx(11 / 60, abs=0.01)
    r = raw_jsonrpc(server, "status", {})
    assert r["lab_time_used_min"] == pytest.approx(16 / 60, abs=0.01)


def test_exploit_checklist(server):
    calls = [
        ("place", {"part": "sample", "x": 1e308, "z": 1, "height": 100, "yaw_deg": 0}),
        ("place", {"part": "sample", "x": -50, "z": -50, "height": 100, "yaw_deg": 0}),
        ("read_signal", {"t_int": 1e9}),
        ("read_signal", {"t_int": -1}),
        ("move_stage", {"position_mm": 5}),
        ("buy", {"items": {"MIR-1": 100000}}),
        ("scan", {"start_mm": 0, "end_mm": 25, "step_mm": 0.0001, "t_int": 0.01}),
    ] + [("status", {})] * 10
    res = mcp_calls(server, calls)
    assert "error" in res[0] and "error" in res[2] and "error" in res[3] and "error" in res[4]
    assert "doesn't fit" in res[1]["outcome"]
    assert "error" in res[5] or "refused" in res[5].get("outcome", "")
    assert "error" in res[6]
    # repeated reads are not free
    used = [r["lab_time_used_min"] for r in res[7:]]
    assert all(b > a for a, b in zip(used, used[1:]))
    code, final = get(f"{server}/verifier/result", TOKEN)
    assert final["reward"] == 0.0 and final["cost_eur"] == 0.0
