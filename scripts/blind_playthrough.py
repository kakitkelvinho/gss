"""Blind playthrough by a fresh agent with no access to the code (no API key or Harbor needed).

The player gets a folder outside the repo with only instruction.md and a stdlib CLI for the MCP
tools; the episode runs on a local server and is scored through the token-gated verifier route.

    uv run python scripts/blind_playthrough.py setup ~/gss-blind/p1 --seed 1 --level 2 --port 8811
        -> starts the server in the background, prints the prompt to give the player
    uv run python scripts/blind_playthrough.py score ~/gss-blind/p1
        -> saves result.json + trajectory.json into the folder, prints the score, stops the server
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOKEN = "blind-token"

CLI = r'''"""Lab tools CLI.  ./gss tools | ./gss call <tool> '<json args>'"""
import json, os, sys, urllib.request
URL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "url")).read().strip()
HDR = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

def rpc(msg, sid=None):
    h = dict(HDR, **({"Mcp-Session-Id": sid} if sid else {}))
    with urllib.request.urlopen(urllib.request.Request(URL, json.dumps(msg).encode(), h), timeout=600) as r:
        sid = r.headers.get("Mcp-Session-Id") or sid
        body = r.read().decode()
    out = None
    for line in body.splitlines():
        if line.startswith("data:"):
            out = json.loads(line[5:])
    if out is None and body.strip():
        out = json.loads(body)
    return out, sid

_, sid = rpc({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18",
             "capabilities": {}, "clientInfo": {"name": "cli", "version": "1"}}})
rpc({"jsonrpc": "2.0", "method": "notifications/initialized"}, sid)
if sys.argv[1] == "tools":
    res, _ = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, sid)
    for t in res["result"]["tools"]:
        print(f"## {t['name']}\n{t.get('description', '')}\nargs: {json.dumps(t['inputSchema'].get('properties', {}))}\n")
else:
    args = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
    res, _ = rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": sys.argv[2], "arguments": args}}, sid)
    r = res.get("result", res)
    sc = r.get("structuredContent")
    print(json.dumps(sc, indent=1) if sc is not None else "\n".join(c.get("text", "") for c in r.get("content", [])))
'''

PROMPT = """You are playing a simulated optics-lab task as a test subject. Play it as well as you can, to the end.

Your working folder is {d}
- Read `instruction.md` there first: it is your whole task brief.
- You act on the lab ONLY through the CLI in that folder:
  - `{d}/gss tools` lists the tools and their arguments;
  - `{d}/gss call <tool> '<json args>'` calls one tool, e.g. `{d}/gss call read_manual '{{"device": "table"}}'`.
- Strict rules (this is a blind test, breaking them invalidates it):
  - Do NOT read, list, grep or open anything outside your working folder. Do not read gss.py beyond
    running it, and do not inspect or connect to the server any other way. Do not use the web.
- You may write your own notes/scripts inside your working folder if that helps.
- Keep going until you call `submit` or lab time runs out. Don't stop early to ask questions; nobody will answer.

When finished, reply with: lab time used and money spent, your layout and parts, what you measured,
whether you think you found time zero, and the 3 biggest difficulties (including anything about the
tools or docs that seemed confusing or wrong)."""


def get(port, path):
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", headers={"Authorization": f"Bearer {TOKEN}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def setup(a):
    d = a.dir.expanduser().resolve()
    if ROOT in d.parents or d == ROOT:
        sys.exit("put the player folder outside the repo, so the player can't see the code")
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "instruction.md", d / "instruction.md")
    (d / "gss.py").write_text(CLI)
    (d / "gss").write_text(f'#!/bin/sh\nexec {shutil.which("python3") or "python3"} "{d}/gss.py" "$@"\n')
    (d / "gss").chmod(0o755)
    (d / "url").write_text(f"http://127.0.0.1:{a.port}/mcp\n")
    env = dict(os.environ, GSS_SEED=str(a.seed), GSS_LEVEL=str(a.level), GSS_VERIFIER_TOKEN=TOKEN,
               GSS_PORT=str(a.port), GSS_HOST="127.0.0.1")
    log = open(d.parent / f".{d.name}.server.log", "w")
    proc = subprocess.Popen([sys.executable, "-m", "server.app"], cwd=ROOT, env=env, stdout=log, stderr=log,
                            start_new_session=True)
    (d.parent / f".{d.name}.server").write_text(json.dumps({"pid": proc.pid, "port": a.port, "seed": a.seed,
                                                            "level": a.level}))
    time.sleep(3)
    out = subprocess.run([str(d / "gss"), "call", "list_catalogue", "{}"], capture_output=True, text=True)
    if out.returncode:
        sys.exit(f"server did not answer:\n{out.stderr}")
    print(f"server up (seed {a.seed}, level {a.level}, port {a.port}). Give the player this prompt:\n")
    print(PROMPT.format(d=d))


def score(a):
    d = a.dir.expanduser().resolve()
    info = json.loads((d.parent / f".{d.name}.server").read_text())
    res = get(info["port"], "/verifier/result")
    (d / "result.json").write_text(json.dumps(res, indent=1))
    (d / "trajectory.json").write_text(json.dumps(get(info["port"], "/verifier/trajectory"), indent=1))
    keys = ["reward", "eta", "O", "abs_dt_fs", "cost_eur", "c_min_eur", "lab_time_frac", "tool_calls"]
    print(f"seed {info['seed']} level {info['level']}:", {k: res.get(k) for k in keys})
    try:
        os.killpg(info["pid"], signal.SIGTERM)
    except ProcessLookupError:
        pass


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("setup")
    s.add_argument("dir", type=Path)
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--level", type=int, default=1)
    s.add_argument("--port", type=int, default=8811)
    c = sub.add_parser("score")
    c.add_argument("dir", type=Path)
    a = p.parse_args()
    setup(a) if a.cmd == "setup" else score(a)


if __name__ == "__main__":
    main()
