"""Render the v2 video in parallel and assemble it with the score, within a hard time budget.

    uv run --no-project --with playwright --with pillow --with imageio-ffmpeg python video/v2/make_video.py [--workers 5]

Each worker is a separate process with its own headless browser, rendering a balanced set of shots into
separate clips; the clips are then joined without re-encoding and the score is added.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import render as R  # noqa: E402

BUDGET_S = 20 * 60


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    a = ap.parse_args()
    start = time.time()
    seg = os.path.join(HERE, "_segments")
    shutil.rmtree(seg, ignore_errors=True)
    os.makedirs(seg)

    # balance shots across workers by frame count (longest first)
    frames = []
    for i, (kind, bar0, bars, spec) in enumerate(R.SHOTS, 1):
        t0, dur = R.tb(bar0), bars * R.BAR
        frames.append((int(round((t0 + dur) * R.FPS)) - int(round(t0 * R.FPS)), i))
    loads = [[0, []] for _ in range(a.workers)]
    for n, i in sorted(frames, reverse=True):
        w = min(loads, key=lambda x: x[0])
        w[0] += n
        w[1].append(i)
    print("frames per worker:", [w[0] for w in loads], flush=True)

    env = dict(os.environ)
    procs = []
    for k, (_, shots) in enumerate(loads):
        if not shots:
            continue
        log = open(os.path.join(seg, f"worker{k}.log"), "w")
        procs.append((subprocess.Popen([sys.executable, os.path.join(HERE, "render.py"), "--shots", ",".join(map(str, sorted(shots))),
                                        "--segments", seg], stdout=log, stderr=subprocess.STDOUT, env=env), log, k))
    failed = False
    for p, log, k in procs:
        remaining = BUDGET_S - (time.time() - start)
        try:
            p.wait(timeout=max(1, remaining))
        except subprocess.TimeoutExpired:
            for q, _, _ in procs:
                q.kill()
            sys.exit(f"over the {BUDGET_S // 60}-minute budget; stopped")
        log.close()
        if p.returncode:
            failed = True
            print(f"worker {k} failed; see {log.name}", flush=True)
    if failed:
        sys.exit(1)
    print(f"all shots rendered in {time.time() - start:.0f} s", flush=True)

    import imageio_ffmpeg
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    listing = os.path.join(seg, "list.txt")
    with open(listing, "w") as f:
        for i in range(1, len(R.SHOTS) + 1):
            f.write(f"file 'shot_{i:02d}.mp4'\n")
    joined = os.path.join(seg, "joined.mp4")
    subprocess.run([exe, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", listing, "-c", "copy", joined], check=True)
    out = os.path.join(HERE, "gss_pitch_v2.mp4")
    subprocess.run([exe, "-y", "-loglevel", "error", "-i", joined, "-i", os.path.join(HERE, "score.wav"), "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    shutil.rmtree(seg)
    print(f"wrote {out} in {time.time() - start:.0f} s total (budget {BUDGET_S // 60} min)")


if __name__ == "__main__":
    main()
