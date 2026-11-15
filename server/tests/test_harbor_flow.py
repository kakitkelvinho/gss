"""The Harbor flow without Docker: server mints its own token -> reference run over MCP ->
collect hook (as Harbor runs it in the sim container) -> separate grader writes the reward files."""

import json
import os
import socket
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "solution"))


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def test_reference_collect_grade(tmp_path):
    from reference import run

    port = _free_port()
    tok_file = tmp_path / "run" / "verifier_token"
    env = {k: v for k, v in os.environ.items() if k != "GSS_VERIFIER_TOKEN"}
    env.update(GSS_SEED="2", GSS_PORT=str(port), GSS_HOST="127.0.0.1", GSS_TOKEN_FILE=str(tok_file),
               GSS_OUT_DIR=str(tmp_path / "gss" / "out"), GSS_RESULT_DIR=str(tmp_path / "gss" / "out"),
               GSS_VERIFIER_DIR=str(tmp_path / "logs" / "verifier"))
    proc = subprocess.Popen([sys.executable, "-m", "server.app"], cwd=ROOT, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        assert tok_file.exists() and oct(tok_file.stat().st_mode & 0o777) == "0o600"
        run(f"http://127.0.0.1:{port}/mcp", "reference")
        subprocess.run([sys.executable, "-m", "server.collect"], cwd=ROOT, env=env, check=True,
                       stdout=subprocess.DEVNULL)
    finally:
        proc.terminate()
        proc.wait(5)
    subprocess.run([sys.executable, os.path.join(ROOT, "tests", "score.py")], env=env, check=True,
                   stdout=subprocess.DEVNULL)
    vdir = tmp_path / "logs" / "verifier"
    reward = float((vdir / "reward.txt").read_text())
    rj = json.loads((vdir / "reward.json").read_text())
    # The reference wins the physics (eta >= 0.9) but not every efficiency point under the tougher
    # grader (seed 2 spends EUR 4600 against C_min EUR 1700): its reward is about 0.80.
    assert reward >= 0.75 and rj["reward"] == reward and rj["success"] == 1
    assert all(isinstance(v, (int, float)) for v in rj.values())
    assert (vdir / "trajectory.json").exists()


def test_grader_without_collected_state_gives_zero(tmp_path):
    env = dict(os.environ, GSS_RESULT_DIR=str(tmp_path / "missing"), GSS_VERIFIER_DIR=str(tmp_path / "v"))
    subprocess.run([sys.executable, os.path.join(ROOT, "tests", "score.py")], env=env, check=True,
                   stdout=subprocess.DEVNULL)
    assert float((tmp_path / "v" / "reward.txt").read_text()) == 0.0
