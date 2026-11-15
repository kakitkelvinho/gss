"""Add finished Harbor runs to the repo so they show up on the viewer site.

    python3 scripts/publish_runs.py <harbor jobs folder>
    git add runs viewer/runs && git commit -m "Add runs" && git push

1. Copies every finished job (a trial with verifier/reward.txt) into runs/harbor/, without
   OpenCode's internal database and file snapshots; refuses files that look like API keys.
2. Exports them into viewer/runs/ with scripts/export_viewer_runs.py (one file per run).
Jobs already in runs/harbor/ are skipped, so running it twice is harmless.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "runs" / "harbor"
SKIP_DIRS = {"opencode"}  # agent/opencode/: OpenCode's sqlite db, git snapshots, xdg data
KEY_PATTERNS = re.compile(rb"AIza[0-9A-Za-z_-]{30,}|sk-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{30,}")


def finished(job: Path) -> bool:
    return any(job.glob("*/verifier/reward.txt"))


def ignore(dirpath, names):
    return [n for n in names if n in SKIP_DIRS and Path(dirpath).name == "agent"]


def leaks(folder: Path) -> list[Path]:
    return [f for f in folder.rglob("*") if f.is_file() and KEY_PATTERNS.search(f.read_bytes())]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("jobs", type=Path, help="Harbor jobs folder (the one `harbor run` writes to)")
    args = parser.parse_args()
    sys.stdout.reconfigure(line_buffering=True)
    jobs = sorted(j for j in args.jobs.resolve().iterdir() if j.is_dir())
    DEST.mkdir(parents=True, exist_ok=True)
    added = []
    for job in jobs:
        if (DEST / job.name).exists():
            print(f"skip {job.name}: already published")
        elif not finished(job):
            print(f"skip {job.name}: no verifier score (run crashed or still going)")
        else:
            tmp = DEST / f".{job.name}.tmp"
            shutil.rmtree(tmp, ignore_errors=True)
            shutil.copytree(job, tmp, ignore=ignore)
            bad = leaks(tmp)
            if bad:
                shutil.rmtree(tmp)
                sys.exit(f"refusing {job.name}: possible API key in {', '.join(str(b.relative_to(tmp)) for b in bad)}")
            tmp.rename(DEST / job.name)
            added.append(job.name)
            print(f"added {job.name}")
    if not added:
        print("nothing new to copy; re-exporting anything not yet in viewer/runs/")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "export_viewer_runs.py"), str(DEST)], check=True)
    print(f"\n{len(added)} job(s) added. Now: git add runs viewer/runs && git commit -m 'Add runs' && git push")


if __name__ == "__main__":
    main()
