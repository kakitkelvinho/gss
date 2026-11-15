"""Serve the run viewer locally and keep it up to date by itself.

    uv run python scripts/serve_viewer.py            # then leave it running; Ctrl+C stops it

It serves viewer/ at http://localhost:8766/ and opens it in your browser. Every few seconds it
looks for Harbor runs that have finished since the last check (in jobs/, or the folders passed
with --jobs) and exports them with scripts/export_viewer_runs.py, which replays each run and
skips any that don't reproduce. It also rebuilds viewer/runs_index.json whenever viewer/runs/
changes (for example after a git pull). An open viewer page picks up new runs on its own.

New runs are written to viewer/runs/ like `export_viewer_runs.py jobs` does. They stay local
until you commit them, so nothing reaches GitHub unless you choose to.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "viewer"
RUNS = VIEWER / "runs"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def finished_runs(jobs_dirs: list[Path]) -> dict[str, float]:
    """Finished Harbor trials (verifier wrote diagnostics + trajectory), keyed by path, with mtime."""
    found = {}
    for jobs in jobs_dirs:
        for diag in jobs.glob("*/*/verifier/diagnostics.json"):
            if (diag.parent / "trajectory.json").exists():
                found[str(diag)] = diag.stat().st_mtime
    return found


def run_files() -> dict[str, float]:
    return {p.name: p.stat().st_mtime for p in RUNS.glob("*.json")}


class Updater:
    def __init__(self, jobs_dirs: list[Path]):
        self.jobs_dirs = jobs_dirs
        self.seen_runs: dict[str, float] = {}
        self.seen_files: dict[str, float] = {}
        self.reported: set[str] = set()  # skip messages already shown, so they don't repeat

    def export(self) -> None:
        for jobs in self.jobs_dirs:
            if not any(jobs.glob("*/*/verifier/diagnostics.json")):
                continue
            proc = subprocess.run([sys.executable, str(ROOT / "scripts/export_viewer_runs.py"), str(jobs)],
                                  cwd=ROOT, capture_output=True, text=True)
            for line in (proc.stdout + proc.stderr).splitlines():
                line = line.strip()
                if line.startswith("exported "):
                    log("new run in the viewer: " + line.removeprefix("exported "))
                elif line.startswith("skipped ") and line not in self.reported:
                    self.reported.add(line)
                    log("not shown: " + line.removeprefix("skipped "))
            if proc.returncode not in (0, 2):  # 2 = "no finished runs", harmless
                tail = (proc.stderr or proc.stdout).strip().splitlines()[-1:] or ["unknown error"]
                log(f"export problem in {jobs}: {tail[0]}")

    def index(self) -> None:
        proc = subprocess.run([sys.executable, str(ROOT / "scripts/build_run_index.py")],
                              cwd=ROOT, capture_output=True, text=True)
        if proc.returncode:
            tail = (proc.stderr or proc.stdout).strip().splitlines()[-1:] or ["unknown error"]
            log(f"could not rebuild the run list: {tail[0]}")
        else:
            log(proc.stdout.strip().replace(str(ROOT) + "/", ""))

    def check(self) -> None:
        runs = finished_runs(self.jobs_dirs)
        if runs != self.seen_runs:
            self.seen_runs = runs
            self.export()  # also rebuilds the index when it exports anything
        files = run_files()
        if files != self.seen_files:
            self.seen_files = files
            self.index()

    def loop(self, interval: float, stop: threading.Event) -> None:
        while not stop.wait(interval):
            try:
                self.check()
            except Exception as err:  # keep serving even if one check fails
                log(f"update check failed: {err}")


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        if self.path.split("?")[0].endswith(".json"):
            self.send_header("Cache-Control", "no-store")  # so the page always sees new runs
        super().end_headers()

    def log_message(self, *args):  # keep the terminal for update messages
        pass


def open_browser(url: str) -> None:
    if shutil.which("explorer.exe"):  # WSL: open in the Windows browser
        subprocess.Popen(["explorer.exe", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        webbrowser.open(url)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--jobs", type=Path, action="append",
                   help="Harbor jobs folder to watch (repeatable; default: jobs/)")
    p.add_argument("--port", type=int, default=8766)
    p.add_argument("--interval", type=float, default=10.0, help="seconds between checks (default 10)")
    p.add_argument("--no-browser", action="store_true", help="don't open the browser")
    a = p.parse_args()
    jobs_dirs = [j.expanduser().resolve() for j in (a.jobs or [ROOT / "jobs"])]
    RUNS.mkdir(parents=True, exist_ok=True)

    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", a.port),
                                                 functools.partial(Handler, directory=str(VIEWER)))
    except OSError:
        sys.exit(f"Port {a.port} is busy: is the viewer already running? "
                 f"Use that one, or start this with --port {a.port + 1}.")

    url = f"http://localhost:{a.port}/"
    log("checking for finished runs…")
    updater = Updater(jobs_dirs)
    updater.check()
    stop = threading.Event()
    threading.Thread(target=updater.loop, args=(a.interval, stop), daemon=True).start()

    log(f"viewer running at {url}")
    log(f"watching {', '.join(os.path.relpath(j, ROOT) if j.is_relative_to(ROOT) else str(j) for j in jobs_dirs)}"
        f" every {a.interval:g}s; new runs appear in the open page by themselves. Ctrl+C to stop.")
    if not a.no_browser:
        open_browser(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        stop.set()
        server.server_close()
        log("viewer stopped")


if __name__ == "__main__":
    main()
