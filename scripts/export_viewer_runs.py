"""Export finished Harbor runs as independent static replay files.

Replay is deterministic: every recorded action must reproduce its logged time, physics and
final diagnostics before a run is published. The export contains verifier geometry, never
OpenCode's database, credentials, or raw Harbor configuration.

    python3 scripts/export_viewer_runs.py jobs/
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.summarise_jobs import analyse  # noqa: E402
from scripts.build_run_index import build_index, file_for, save_run  # noqa: E402
from sim import reward as CURRENT_REWARD  # noqa: E402

early = argparse.ArgumentParser(add_help=False)
early.add_argument("--sim-root", type=Path)
source_root = early.parse_known_args()[0].sim_root
if source_root and source_root.resolve() != ROOT:
    if not (source_root / "sim/episode.py").exists():
        raise ValueError(f"no simulator at {source_root}")
    for name in list(sys.modules):
        if name == "sim" or name.startswith("sim."):
            del sys.modules[name]
    sys.path.insert(0, str(source_root.resolve()))

from sim import constants as K  # noqa: E402
from sim import vec as V  # noqa: E402
from sim.episode import Episode  # noqa: E402
from sim.optics import Lens  # noqa: E402

SCHEMA = "gss.viewer.v1"
PREFIX = "window.GSS_RUNS_BUNDLE = "


def xyz(v):
    if v is None:
        return None
    return {"x": round(v[0], 4), "z": round(v[2], 4), "h": round(v[1], 4)}


def part_snapshot(ep, item):
    p = item["part"]
    yaw = p.yaw + (p.knob_yaw + p.mount_err[0] if p.kind in ("mirror", "periscope") else 0.0)
    pitch = p.knob_pitch + p.mount_err[1] if p.kind in ("mirror", "periscope") else 0.0
    lenses = []
    if p.kind == "sample":
        for e in p.elements(ep.lab.defocus):
            if isinstance(e, Lens):
                sample_pt = e.sample_pt or V.add(e.center, V.mul(e.u, K.LENS_F))
                lenses.append({"role": e.role, "pos": xyz(e.center), "center": xyz(e.center),
                               "dir": xyz(e.u), "yaw_deg": round(math.degrees(math.atan2(e.u[2], e.u[0])), 4),
                               "f_mm": K.LENS_F, "radius_mm": K.LENS_R,
                               "mount_radius_mm": K.LENS_MOUNT_R, "sample_pos": xyz(sample_pt)})
    return {"id": p.id, "kind": p.kind, "catalogue_id": item["part_id"],
            "pos": xyz(p.pos), "yaw_deg": round(math.degrees(p.yaw), 4),
            "eff_yaw_deg": round(math.degrees(yaw), 4),
            "eff_pitch_deg": round(math.degrees(pitch), 4),
            "h_in": None if p.height_in is None else round(p.height_in, 4),
            "stage_pos_mm": round(p.stage_pos, 4) if p.kind == "stage" else None,
            "travel_mm": p.travel if p.kind == "stage" else None,
            "level": p.level if p.kind == "sample" else None, "lenses": lenses}


def beam_snapshot(ep, arm):
    b = ep._beams()[arm]
    return {"open": ep.shutter_open[arm], "end": b.end, "end_note": b.end_note,
            "T": round(b.T, 6), "opl_mm": round(b.opl, 4),
            "spot_mm": None if b.spot is None else [round(v, 4) for v in b.spot],
            "segments": [[xyz(a), xyz(z)] for a, z in b.segments],
            "hits": [{"part_id": h.part_id, "role": h.role, "T": round(h.T, 6)} for h in b.hits]}


def snapshot(ep, tool, response):
    parts = [part_snapshot(ep, item) for item in ep.inv.values() if item["part"] is not None]
    return {"you_mm": {"x": round(ep.pos[0], 4), "z": round(ep.pos[1], 4),
                       "at_desk": ep._you_at() == "desk"},
            "shutters_open": dict(ep.shutter_open), "cost_eur": ep.cost,
            "stage_cmd_mm": round(ep.stage_cmd, 4), "stage_true_mm": round(ep.stage_true, 4),
            "installed": {"diagnostic": ep.diag, "filter": ep.filter, "camera": ep.align_cam},
            "parts": parts, "beams": {arm: beam_snapshot(ep, arm) for arm in K.ARMS},
            "ir_probe": response if tool == "ir_card" and "error" not in response else None,
            "camera_frame": response if tool == "view_camera" and "error" not in response else None,
            "scan_data": response if tool == "scan" and "error" not in response else None}


def run_meta(ep):
    ports = {arm: {"pos": xyz(port["pos"]), "dir": xyz(port["dir"])}
             for arm, port in ep.lab.ports.items()}
    housings = [{"x0": x0, "x1": x1, "h0": h0, "h1": h1, "z0": z0, "z1": z1}
                for x0, x1, h0, h1, z0, z1 in ep.lab.housings]
    return {"schema_version": SCHEMA, "seed": ep.seed, "level": ep.level,
            "opa_lambda_nm": ep.lab.opa_lambda, "c_min_eur": ep.c_min,
            "spend_cap_eur": K.SPEND_CAP, "budget_s": K.BUDGET_S,
            "table_mm": {"x": K.TABLE_X, "z": K.TABLE_Z, "max_h": K.MAX_HEIGHT},
            "desk_mm": {"x": K.DESK[0], "z": K.DESK[2]},
            "walk_offset_mm": K.WALK_OFFSET, "ports": ports, "housings_mm": housings}


def harbor_usage(trial: Path) -> dict | None:
    """Copy only numeric usage and timing fields, never Harbor's config or rollout."""
    path = trial / "result.json"
    if not path.exists():
        return None
    result = json.loads(path.read_text())
    agent = result.get("agent_result") or {}
    usage = {key: agent[key] for key in ("n_input_tokens", "n_cache_tokens", "n_output_tokens", "cost_usd")
             if isinstance(agent.get(key), (int, float)) and not isinstance(agent[key], bool)}
    execution = result.get("agent_execution") or {}
    if execution.get("started_at") and execution.get("finished_at"):
        start = datetime.fromisoformat(execution["started_at"].replace("Z", "+00:00"))
        finish = datetime.fromisoformat(execution["finished_at"].replace("Z", "+00:00"))
        usage["wall_time_s"] = round((finish - start).total_seconds(), 3)
    return usage or None


def diagnostics_match(actual: dict, recorded: dict) -> bool:
    if actual.keys() != recorded.keys():
        return False
    for key, value in actual.items():
        expected = recorded[key]
        if isinstance(value, float) and isinstance(expected, (int, float)) and not isinstance(expected, bool):
            if not math.isclose(value, expected, rel_tol=1e-9, abs_tol=1e-9):
                return False
        elif value != expected:
            return False
    return True


def export_run(verifier_dir: Path, jobs_dir: Path):
    diagnostics = json.loads((verifier_dir / "diagnostics.json").read_text())
    recorded = json.loads((verifier_dir / "trajectory.json").read_text())["trajectory"]
    ep = Episode(diagnostics["seed"], diagnostics["level"])
    steps = []
    for step in recorded:
        response = ep.call(step["tool"], step["args"])
        replayed = ep.trajectory()[-1]
        if replayed["t_s"] != step["t_s"] or replayed["truth"] != step["truth"]:
            raise ValueError(f"simulator replay diverged at {verifier_dir}, step {step['i']}")
        truth = dict(step["truth"])
        truth.update(CURRENT_REWARD.score(truth["eta"], truth["O"], truth["T_800"], truth["T_opa"],
                              ep.cost, ep.t / K.BUDGET_S, ep.c_min))
        steps.append({**step, "truth": truth, "snapshot": snapshot(ep, step["tool"], response)})
    if not diagnostics_match(ep.result(), diagnostics):
        raise ValueError(f"final diagnostics differ at {verifier_dir}")

    trial = verifier_dir.parent
    config = json.loads((trial / "config.json").read_text())
    model = config["agent"].get("model_name") or config["agent"].get("name") or "unknown"  # the oracle agent has no model
    run_id = trial.relative_to(jobs_dir).as_posix()
    when = trial.parent.name.split("__", 1)[0]
    level = f"L{ep.level}" + (" (90°)" if ep.level == 2 else "")
    label = f"{model} · {when} — Seed {ep.seed} · {level} · {ep.lab.opa_lambda:.0f} nm · R = {diagnostics['reward']:.3f}"
    tags, _ = analyse(diagnostics, recorded)
    return {"id": run_id, "label": label, "model": model, "is_demo": False,
            "meta": run_meta(ep), "diagnostics": diagnostics,
            "failure_tags": tags, "agent_usage": harbor_usage(trial), "trajectory": steps}


def tag_scorer(run):
    """Mark runs whose verifier reward came from an earlier grader than today's sim/reward.py."""
    if not run["trajectory"]:
        run["old_scorer"] = False
        return run
    meta, last = run["meta"], run["trajectory"][-1]
    t = last["truth"]
    today = CURRENT_REWARD.score(t["eta"], t["O"], t["T_800"], t["T_opa"], last["snapshot"]["cost_eur"],
                     last["t_s"] / meta["budget_s"], meta["c_min_eur"])["reward"]
    run["today_reward"] = round(today, 6)
    run["old_scorer"] = abs(today - run["diagnostics"]["reward"]) > 0.005
    run["label"] = run["label"].removesuffix(" (old scorer)") + (" (old scorer)" if run["old_scorer"] else "")
    return run


def read_bundle(path: Path):
    content = path.read_text()
    if not content.startswith(PREFIX):
        raise ValueError(f"not a {SCHEMA} JavaScript bundle: {path}")
    bundle = json.loads(content[len(PREFIX):].rstrip(";\n"))
    if bundle.get("schema_version") != SCHEMA:
        raise ValueError(f"unsupported viewer schema in {path}")
    return bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jobs", type=Path, nargs="?", help="Harbor jobs directory")
    parser.add_argument("--runs", type=Path, default=ROOT / "viewer/runs")
    parser.add_argument("--import-bundle", type=Path, help="one-time import of the old bundle")
    parser.add_argument("--sim-root", type=Path, help="checkout with the simulator version used for replay")
    args = parser.parse_args()
    if not args.jobs and not args.import_bundle:
        parser.error("provide jobs or --import-bundle")
    count = 0
    if args.import_bundle:
        for run in read_bundle(args.import_bundle)["runs"]:
            save_run(tag_scorer(run), args.runs)
            count += 1
    if args.jobs:
        jobs_dir = args.jobs.resolve()
        files = sorted(jobs_dir.glob("*/**/verifier/diagnostics.json"))
        for path in files:
            if not (path.parent / "trajectory.json").exists():
                continue
            diagnostics = json.loads(path.read_text())
            trial = path.parent.parent
            run_id = trial.relative_to(jobs_dir).as_posix()
            archived = args.runs / file_for(run_id)
            if archived.exists():
                run = json.loads(archived.read_text())
                if run["id"] != run_id or run["diagnostics"] != diagnostics:
                    raise ValueError(f"archived run differs from verifier diagnostics: {run_id}")
                usage = harbor_usage(trial)
                if usage and run.get("agent_usage") != usage:
                    run["agent_usage"] = usage
                    archived.write_text(json.dumps(run, separators=(",", ":"), ensure_ascii=False) + "\n")
                    print(f"added Harbor usage to {run_id}")
                count += 1
                continue
            if not {"level", "T_800", "T_opa", "opa_lambda_nm"} <= diagnostics.keys():
                print(f"skipped unsupported old verifier format: {path}")
                continue
            try:
                run = tag_scorer(export_run(path.parent, jobs_dir))
            except ValueError as err:  # recorded under another simulator version: skip, don't block the rest
                print(f"skipped {run_id}: {err} (re-run with --sim-root <checkout of the commit it ran on>)")
                continue
            save_run(run, args.runs)
            count += 1
            print(f"exported {run['id']} ({len(run['trajectory'])} calls)")
    if not count:
        parser.error("no finished runs with verifier trajectories found")
    index = build_index(args.runs, ROOT / "viewer/runs_index.json")
    print(f"archived {count} runs; {index['summary']['count']} total")


if __name__ == "__main__":
    main()
