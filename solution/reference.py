"""Reference (oracle) run over MCP: drives the scripted expert through the same tools the agent gets.

Usage: python reference.py [--url http://sim:8000/mcp] [--stop-early] [--do-nothing]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from expert import Expert  # noqa: E402


class SyncMCP:
    """Minimal synchronous wrapper around fastmcp's async Client."""

    def __init__(self, url: str):
        from fastmcp import Client

        self.loop = asyncio.new_event_loop()
        self.client = Client(url, timeout=600)
        self.loop.run_until_complete(self.client.__aenter__())
        self.calls = 0

    def call(self, tool: str, **args) -> dict:
        self.calls += 1
        r = self.loop.run_until_complete(self.client.call_tool(tool, args, raise_on_error=False))
        if r.structured_content is not None:
            return r.structured_content
        return json.loads(r.content[0].text)

    def close(self):
        self.loop.run_until_complete(self.client.__aexit__(None, None, None))
        self.loop.close()


def run(url: str, policy: str = "reference", verbose: bool = False) -> list[str]:
    m = SyncMCP(url)
    try:
        if policy == "do-nothing":
            m.call("submit")
            return []
        ex = Expert(m.call, verbose=verbose)
        ex.run(stop_early=(policy == "stop-early"))
        return ex.notes
    finally:
        m.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=os.environ.get("GSS_MCP_URL", "http://sim:8000/mcp"))
    ap.add_argument("--policy", choices=["reference", "stop-early", "do-nothing"], default="reference")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()
    for n in run(a.url, a.policy, a.verbose):
        print("#", n)


if __name__ == "__main__":
    main()
