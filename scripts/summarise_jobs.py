"""Summarise Harbor runs: one table of scores plus, per run, *why* it scored what it did.

Walks a jobs folder (the `-o` folder of `harbor run`) for the verifier's `diagnostics.json` and
`trajectory.json` (written by tests/score.py), and writes one Markdown file you can read or send on.

    python scripts/summarise_jobs.py jobs/            # writes jobs/summary.md and prints it
    python scripts/summarise_jobs.py jobs/ -o out.md

Stdlib only, reads files only (no simulator needed). The failure tags are heuristics over the
action log and the true state logged after every step; each says what it checked.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

C_MM_PER_FS = 2.99792458e-4
TAU_C_FS = {1: 70.0, 2: 186.0}  # overlap window (1/e half-width) per level
STAGE_TRAVEL = {"DL-M25": 25.0, "DL-C25": 25.0, "DL-C100": 100.0}


def _routes(lam, level=1):
    """Viable (diagnostic, filter) routes from the sim's own model, if the sim package is importable."""
    try:
        from sim import reward as RW
        return {(d, f) for d, f, _ in RW.detection_routes(lam, level)}
    except Exception:  # noqa: BLE001 - summariser must work without the sim
        return None


def find_runs(root):
    for dirpath, _, files in os.walk(root):
        if "diagnostics.json" in files:
            yield dirpath


def label(run_dir, root):
    rel = os.path.relpath(run_dir, root).split(os.sep)
    if rel and rel[-1] == "verifier":
        rel = rel[:-1]
    return "/".join(rel) or "."


def model_of(run_dir, root):
    """Best effort: look for a model name in Harbor's config/result files above the verifier dir."""
    d = run_dir
    while True:
        for name in ("config.json", "result.json"):
            p = os.path.join(d, name)
            if os.path.exists(p):
                try:
                    txt = json.load(open(p))
                except Exception:  # noqa: BLE001
                    continue
                m = _find_key(txt, ("model_name", "model"))
                if isinstance(m, str):
                    return m
        if os.path.abspath(d) == os.path.abspath(root) or os.path.dirname(d) == d:
            return "?"
        d = os.path.dirname(d)


def _find_key(x, keys):
    if isinstance(x, dict):
        for k in keys:
            if isinstance(x.get(k), str):
                return x[k]
        for v in x.values():
            r = _find_key(v, keys)
            if r:
                return r
    elif isinstance(x, list):
        for v in x:
            r = _find_key(v, keys)
            if r:
                return r
    return None


def analyse(res, traj):
    """Failure tags: (tag, explanation). Ordered roughly from design to execution."""
    tags = []
    tools = [s["tool"] for s in traj]
    level = res.get("level", 1)
    tau_fs = TAU_C_FS.get(level, 70.0)
    PEAK_STAGE_MM = tau_fs * C_MM_PER_FS / 2  # 1/e half-width of the peak in stage travel
    calls = lambda t: [s for s in traj if s["tool"] == t]  # noqa: E731
    lam = res.get("opa_lambda_nm")
    manuals = {s["args"].get("device") for s in calls("read_manual")}
    bought = {}
    for s in calls("buy"):
        if s["result"].get("outcome") == "delivered":
            for k, q in (s["args"].get("items") or {}).items() if isinstance(s["args"].get("items"), dict) else \
                    [(k, 1) for k in s["args"].get("items") or [] if isinstance(k, str)]:
                bought[k] = bought.get(k, 0) + q

    # --- design ---
    if "opa" not in manuals:
        tags.append(("no-opa-manual", "never read the OPA manual (internal path / wavelength route)"))
    if "table" not in manuals:
        tags.append(("no-table-manual", "never read the table manual (ports, OPA wavelength)"))
    if not res.get("design_viable"):
        why = []
        if not any(k in STAGE_TRAVEL for k in bought):
            why.append("no delay stage")
        routes = _routes(lam, level) if lam else None
        if routes is not None:
            owned = set(bought)
            if not any(d in owned and (f is None or f in owned) for d, f in routes):
                ok = ", ".join(sorted(f"{d}+{f}" if f else d for d, f in routes))
                why.append(f"no working detection route at {lam:.0f} nm (bought {sorted(bought) or 'nothing'}; "
                           f"working: {ok})")
        if lam and lam > 1000 and "CAM-VSWIR" not in bought:
            why.append("no camera that sees the 1300 nm beam")
        tags.append(("design-not-viable", "; ".join(why) or "parts list cannot reach overlap"))
    over = res.get("cost_eur", 0) - res.get("c_min_eur", 0)
    if over > 3000:
        tags.append(("overspent", f"EUR {over:.0f} above the cheapest workable design"))

    # --- detection practice ---
    reads = calls("read_signal") + calls("scan")
    if any(s["result"].get("saturated") for s in reads):
        n = sum(1 for s in reads if s["result"].get("saturated"))
        tags.append(("saturated-signal", f"{n} reading(s)/scan(s) saturated the signal camera (no or wrong filter)"))
    blocked_while_reading = False
    shut = {"800nm": False, "opa": False}
    for s in traj:
        if s["tool"] in ("block", "unblock") and "error" not in s["result"]:
            shut[s["args"].get("arm")] = s["tool"] == "unblock"
        if s["tool"] in ("read_signal", "scan") and "error" not in s["result"] and not all(shut.values()):
            blocked_while_reading = True
    if reads and not blocked_while_reading:
        tags.append(("no-single-beam-check", "never read the diagnostic with one arm blocked "
                                             "(can't tell the cross term from single-beam background)"))

    # --- scanning ---
    scans = [s for s in calls("scan") if "error" not in s["result"]]
    coarse = [s for s in scans if s["args"].get("step_mm", 0) > 2 * PEAK_STAGE_MM]
    if coarse and not any(s["args"].get("step_mm", 1) <= 2 * PEAK_STAGE_MM for s in scans):
        st = min(s["args"]["step_mm"] for s in coarse)
        tags.append(("steps-too-big", f"every scan stepped >= {st * 1000:.0f} um; the peak is ~{2 * PEAK_STAGE_MM * 1000:.0f} "
                                      f"um of stage travel wide (1/e full width), so it can be stepped over"))
    short = [s for s in scans if s["args"].get("t_int", 1) < 0.1]
    if short:
        tags.append(("short-integration", f"{len(short)} scan(s) at t_int < 0.1 s (noise x{(1 / 0.1) ** 0.5:.0f} vs 1 s)"))
    scan_time = sum(s["cost_s"] for s in scans) / 60
    if scan_time > 120:
        tags.append(("scan-heavy", f"{scan_time:.0f} min of the 240 spent scanning"))

    # --- reachability of time zero at the end ---
    dt = res.get("abs_dt_fs")
    stage = next((k for k in reversed(list(bought)) if k in STAGE_TRAVEL), None)
    last = traj[-1]["truth"] if traj else {}
    if stage and last.get("dt_fs") is not None:
        pos = None
        for s in reversed(traj):
            if "position_mm" in s["result"]:
                pos = s["result"]["position_mm"]
                break
        pos = 0.0 if pos is None else pos
        # moving the stage by x adds 2x of path to the 800 nm arm: dt(x) = dt_end + 2 (x - pos) / c
        lo = last["dt_fs"] + 2 * (0 - pos) / C_MM_PER_FS
        hi = last["dt_fs"] + 2 * (STAGE_TRAVEL[stage] - pos) / C_MM_PER_FS
        if not (lo <= 0 <= hi):
            miss = min(abs(lo), abs(hi)) * C_MM_PER_FS
            tags.append(("time-zero-unreachable", f"layout puts time zero {miss:.0f} mm of path outside the stage range "
                                                  "(coarse delay / OPA internal path not matched)"))
    if dt is not None and dt > 3 * tau_fs and not any(t[0] == "time-zero-unreachable" for t in tags):
        tags.append(("missed-time-zero", f"ended {dt:.0f} fs ({dt * C_MM_PER_FS * 1000:.0f} um of path) from time zero"))
    if dt is None:
        ends = [f"{k} -> {last.get('end_' + k.replace('nm', '')) or 'nothing placed / shutter closed'}" for k in ("800nm", "opa")]
        tags.append(("beam-not-at-sample", "at the end: " + ", ".join(ends)))
    elif res.get("O", 0) < 0.5:
        tags.append(("poor-spatial-overlap", f"spot overlap O = {res['O']:.2f} at the end"))
    if min(res.get("T_800", 1), res.get("T_opa", 1)) < 0.8 and dt is not None:
        tags.append(("clipping", f"transmission 800nm {res.get('T_800', 0):.2f}, opa {res.get('T_opa', 0):.2f}"))
    if res.get("stray_events", 0):
        tags.append(("stray-beams", f"{res['stray_events']} beam(s) left the table ({res.get('stray_time_min', 0)} min)"))
    if res.get("ended_by") == "timeout":
        tags.append(("timeout", "ran out of the 4 h lab time"))
    elif res.get("ended_by") == "verifier":
        tags.append(("never-submitted", "agent stopped without calling submit"))
    if res.get("malformed_calls", 0) > 10:
        tags.append(("malformed-calls", f"{res['malformed_calls']} rejected tool calls"))
    return tags, tools


def fmt(v, nd=3):
    if v is None:
        return "–"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jobs", help="Harbor jobs folder (or any folder containing verifier outputs)")
    ap.add_argument("-o", "--out", help="output Markdown file (default <jobs>/summary.md)")
    a = ap.parse_args()
    runs = []
    for d in sorted(find_runs(a.jobs)):
        res = json.load(open(os.path.join(d, "diagnostics.json")))
        tp = os.path.join(d, "trajectory.json")
        traj = []
        if os.path.exists(tp):
            t = json.load(open(tp))
            traj = t["trajectory"] if isinstance(t, dict) else t
        tags, _ = analyse(res, traj)
        runs.append((label(d, a.jobs), model_of(d, a.jobs), res, tags))
    if not runs:
        sys.exit(f"no diagnostics.json found under {a.jobs}")

    L = ["# GSS run summary", "",
         "R = reward; eta = overlap score before cost/time penalties; O = spot overlap; |dt| = timing error.",
         "", "| run | model | seed | level | OPA nm | R | eta | O | abs dt (fs) | EUR (C_min) | min | calls | ended | tags |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, model, r, tags in runs:
        L.append(f"| {name} | {model} | {r.get('seed')} | {r.get('level', 1)} | {fmt(r.get('opa_lambda_nm'), 0)} | {fmt(r.get('reward'))} | "
                 f"{fmt(r.get('eta'))} | {fmt(r.get('O'), 2)} | {fmt(r.get('abs_dt_fs'), 0)} | "
                 f"{r.get('cost_eur', 0):.0f} ({r.get('c_min_eur', 0):.0f}) | {fmt(r.get('lab_time_min'), 0)} | "
                 f"{r.get('tool_calls')} | {r.get('ended_by')} | {', '.join(t for t, _ in tags) or 'ok'} |")
    counts = {}
    for *_, tags in runs:
        for t, _ in tags:
            counts[t] = counts.get(t, 0) + 1
    if counts:
        L += ["", "## Failure modes across runs", ""]
        L += [f"- `{t}`: {n} of {len(runs)} runs" for t, n in sorted(counts.items(), key=lambda x: -x[1])]
    L += ["", "## Per run", ""]
    for name, model, r, tags in runs:
        L.append(f"### {name} ({model}, seed {r.get('seed')}, OPA {fmt(r.get('opa_lambda_nm'), 0)} nm): R = {fmt(r.get('reward'))}")
        L.append(f"- bought: {', '.join(r.get('diagnostics_bought') or []) or 'no diagnostics'}; "
                 f"design viable: {r.get('design_viable')}")
        L += [f"- **{t}**: {why}" for t, why in tags] or ["- no failure tags"]
        L.append("")
    text = "\n".join(L)
    out = a.out or os.path.join(a.jobs, "summary.md")
    with open(out, "w") as f:
        f.write(text + "\n")
    print(text)
    print(f"\nwritten to {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
