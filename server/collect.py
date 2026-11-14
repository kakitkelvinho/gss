"""Harbor collect hook (runs inside the sim container after the agent's container is stopped).

Reads the final result and the trajectory through the token-gated verifier route and writes them
to GSS_OUT_DIR (default /gss/out), which Harbor transfers to the separate verifier as artifacts.
Fetching /verifier/result auto-submits the episode, so nothing can act on the lab afterwards.
"""

from __future__ import annotations

import json
import os
import urllib.request

# Same default as server.app.TOKEN_FILE (not imported: importing the app would mint a new token).
TOKEN_FILE = "/run/gss/verifier_token"


def main():
    port = os.environ.get("GSS_PORT", "8000")
    out = os.environ.get("GSS_OUT_DIR", "/gss/out")
    tok = os.environ.get("GSS_VERIFIER_TOKEN") or open(os.environ.get("GSS_TOKEN_FILE", TOKEN_FILE)).read().strip()
    os.makedirs(out, exist_ok=True)
    for name, path in (("result", "/verifier/result"), ("trajectory", "/verifier/trajectory")):
        req = urllib.request.Request(f"http://127.0.0.1:{port}{path}", headers={"Authorization": f"Bearer {tok}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
        with open(os.path.join(out, f"{name}.json"), "w") as f:
            json.dump(data, f)
    print(open(os.path.join(out, "result.json")).read())


if __name__ == "__main__":
    main()
