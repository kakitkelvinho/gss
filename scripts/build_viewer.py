"""Build `viewer/runs_bundle.js` (`window.GSS_RUNS_BUNDLE`) from Harbor `jobs/` runs + synthetic demos.

Usage:
    python scripts/build_viewer.py [jobs_dir ...] [--no-demos] [--serve] [--port 8765]

Stdlib-only CLI. Discovers finished runs (`diagnostics.json` + `trajectory.json`), deterministically
retro-replays trajectories missing `gss.viewer.v1` snapshots through `sim.Episode`, attaches failure
tags from `scripts.summarise_jobs`, adds two fast in-process failure demo runs (unless `--no-demos`),
and writes `viewer/runs_bundle.js`.
"""

from __future__ import annotations

import argparse
import datetime as dt
import http.server
import json
import math
import os
import subprocess
import sys
import threading
from urllib.parse import urlsplit
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts import summarise_jobs as SJ  # noqa: E402
from sim import Episode  # noqa: E402
from sim import constants as K  # noqa: E402

SCHEMA_VERSION = "gss.viewer.v1"

LEGACY_ARMS = {
    "pump": "800nm",
    "probe": "opa",
}

LEGACY_PARTS = {
    "BBO-SFG-1300": "BBO-T236",
    "BBO-SFG-600": "BBO-T341",
    "BBO-SFG-450": "BBO-T408",
    "BBO-SHG-800": "BBO-T292",
}


def _map_legacy_args(tool: str, args: dict | None) -> dict:
    """Translate pre-PR-#9 legacy arm names and BBO part IDs where possible."""
    out = dict(args or {})
    if isinstance(out.get("arm"), str) and out["arm"] in LEGACY_ARMS:
        out["arm"] = LEGACY_ARMS[out["arm"]]
    if tool == "buy" and "items" in out:
        items = out["items"]
        if isinstance(items, dict):
            mapped: dict[str, int] = {}
            for k, v in items.items():
                mk = LEGACY_PARTS.get(k, k) if isinstance(k, str) else k
                mapped[mk] = mapped.get(mk, 0) + v
            out["items"] = mapped
        elif isinstance(items, list):
            new_list = []
            for entry in items:
                if isinstance(entry, str):
                    new_list.append(LEGACY_PARTS.get(entry, entry))
                elif isinstance(entry, dict) and isinstance(entry.get("part_id"), str):
                    d = dict(entry)
                    d["part_id"] = LEGACY_PARTS.get(d["part_id"], d["part_id"])
                    new_list.append(d)
                else:
                    new_list.append(entry)
            out["items"] = new_list
    if tool in ("install", "get_datasheet") and isinstance(out.get("part_id"), str):
        out["part_id"] = LEGACY_PARTS.get(out["part_id"], out["part_id"])
    return out


def _resolve_model(run_dir: str, root: str) -> str:
    """Use summarise_jobs.model_of first, falling back to Harbor agent name (e.g. 'oracle') if '?'."""
    m = SJ.model_of(run_dir, root)
    if m and m != "?":
        return m
    d = run_dir
    while True:
        for name in ("config.json", "result.json"):
            p = os.path.join(d, name)
            if os.path.exists(p):
                try:
                    with open(p, encoding="utf-8") as f:
                        obj = json.load(f)
                except Exception:  # noqa: BLE001
                    continue
                if isinstance(obj, dict):
                    for sec in ("agent", "agent_info"):
                        sub = obj.get(sec)
                        if isinstance(sub, dict) and isinstance(sub.get("name"), str) and sub["name"]:
                            return sub["name"]
                    cfg = obj.get("config")
                    if isinstance(cfg, dict) and isinstance(cfg.get("agent"), dict):
                        aname = cfg["agent"].get("name")
                        if isinstance(aname, str) and aname:
                            return aname
        if os.path.abspath(d) == os.path.abspath(root) or os.path.dirname(d) == d:
            break
        d = os.path.dirname(d)
    return m


def _has_snapshots(traj_obj: Any, steps: list[dict]) -> bool:
    if not isinstance(traj_obj, dict) or not isinstance(traj_obj.get("meta"), dict):
        return False
    if traj_obj["meta"].get("schema_version") != SCHEMA_VERSION:
        return False
    return all(
        isinstance(s, dict)
        and isinstance(s.get("snapshot"), dict)
        and isinstance(s.get("truth"), dict)
        and "reward" in s["truth"]
        for s in steps
    )


def retro_replay(
    seed: int,
    level: int,
    raw_steps: list[dict],
    diagnostics: dict | None = None,
    run_label: str = "",
) -> tuple[dict, list[dict], dict] | None:
    """Deterministically replay `(tool, args)` through `Episode(seed, level)`.

    Returns `(meta_snapshot, enriched_trajectory, replayed_result)` or `None` if an ancient
    pre-PR-#9 run is incompatible with current simulator physics.
    """
    is_legacy = bool(diagnostics and ("T_pump" in diagnostics or "T_probe" in diagnostics))
    try:
        ep = Episode(seed, level)
    except Exception as exc:  # noqa: BLE001
        print(f"[build_viewer] Skipping {run_label or seed}: Episode({seed}, {level}) failed: {exc}", file=sys.stderr)
        return None

    for idx, step in enumerate(raw_steps):
        if not isinstance(step, dict) or not isinstance(step.get("tool"), str):
            continue
        tool = step["tool"]
        mapped_args = _map_legacy_args(tool, step.get("args"))
        try:
            ep.call(tool, mapped_args)
        except Exception as exc:  # noqa: BLE001
            print(
                f"[build_viewer] Warning in {run_label or seed} at step {idx} ({tool}): {exc}",
                file=sys.stderr,
            )
            break

    if raw_steps and not ep.trajectory():
        print(f"[build_viewer] Skipping {run_label or seed}: zero steps replayed cleanly", file=sys.stderr)
        return None

    replayed_res = ep.result()
    if is_legacy and diagnostics is not None:
        diag_O = float(diagnostics.get("O") or 0.0)
        diag_eta = float(diagnostics.get("eta") or 0.0)
        if abs(replayed_res["O"] - diag_O) > 0.05 or abs(replayed_res["eta"] - diag_eta) > 0.05:
            print(
                f"[build_viewer] Skipping incompatible pre-PR-#9 run {run_label or seed}: "
                f"replayed O={replayed_res['O']:.3f}/eta={replayed_res['eta']:.3f} diverges from "
                f"legacy diagnostics O={diag_O:.3f}/eta={diag_eta:.3f}",
                file=sys.stderr,
            )
            return None

    return ep.meta_snapshot(), ep.trajectory(), replayed_res


def _format_label(model: str, seed: int, level: int, lam_nm: float, reward: float,
                  run_id: str = "") -> str:
    lvl_str = "L2 (90°)" if level == 2 else "L1"
    try:
        run_time = dt.datetime.strptime(run_id.split("/")[0], "%Y-%m-%d__%H-%M-%S").strftime("%d %b %H:%M")
    except ValueError:
        run_time = ""
    timestamp = f" · {run_time}" if run_time else ""
    return f"{model}{timestamp} — Seed {seed} · {lvl_str} · {lam_nm:.0f} nm · R = {reward:.3f}"


def load_run_dir(run_dir: str, root: str) -> dict | None:
    """Load one verifier run directory containing `diagnostics.json` and `trajectory.json`."""
    diag_path = os.path.join(run_dir, "diagnostics.json")
    traj_path = os.path.join(run_dir, "trajectory.json")
    if not (os.path.exists(diag_path) and os.path.exists(traj_path)):
        return None

    try:
        with open(diag_path, encoding="utf-8") as f:
            diag = json.load(f)
        with open(traj_path, encoding="utf-8") as f:
            traj_obj = json.load(f)
    except Exception as exc:  # noqa: BLE001
        print(f"[build_viewer] Skipping {run_dir}: failed to read JSON ({exc})", file=sys.stderr)
        return None

    run_id = SJ.label(run_dir, root)
    if run_id == ".":
        run_id = os.path.basename(os.path.abspath(run_dir))
    seed = int(diag.get("seed", traj_obj.get("seed", 1) if isinstance(traj_obj, dict) else 1))
    level = int(diag.get("level", traj_obj.get("level", 1) if isinstance(traj_obj, dict) else 1))
    raw_steps = traj_obj.get("trajectory", []) if isinstance(traj_obj, dict) else traj_obj
    if not isinstance(raw_steps, list):
        print(f"[build_viewer] Skipping {run_id}: invalid trajectory list", file=sys.stderr)
        return None

    if _has_snapshots(traj_obj, raw_steps):
        meta = traj_obj["meta"]
        steps = raw_steps
        eff_diag = dict(diag)
    else:
        replayed = retro_replay(seed, level, raw_steps, diagnostics=diag, run_label=run_id)
        if replayed is None:
            return None
        meta, steps, replayed_res = replayed
        # Preserve original diagnostics while filling any missing post-PR-#9 keys if needed
        eff_diag = dict(replayed_res)
        eff_diag.update(diag)

    tags, _ = SJ.analyse(eff_diag, steps)
    model = _resolve_model(run_dir, root)
    lam_nm = float(eff_diag.get("opa_lambda_nm") or meta.get("opa_lambda_nm", 1300.0))
    reward = float(eff_diag.get("reward") or 0.0)

    return {
        "id": run_id,
        "label": _format_label(model, seed, level, lam_nm, reward, run_id),
        "model": model,
        "is_demo": False,
        "meta": meta,
        "diagnostics": eff_diag,
        "failure_tags": [[t, why] for t, why in tags],
        "trajectory": steps,
    }


# ----------------------------------------------------------------------------------------------
# Fast in-process synthetic failure demos (<0.2s total)


def _steer_ir(ep: Episode, part: str, arm: str, src: tuple[float, float, float],
              tgt: tuple[float, float, float], along: str, max_iter: int = 3):
    """Compact fast 2-axis IR-card steering helper for synthetic demo runs."""
    def measure():
        r = ep.call("ir_card", {"x": tgt[0], "z": tgt[1], "height": tgt[2]})
        for b in r.get("beams", []):
            if b.get("beam") == arm:
                if along == "x":
                    return (b["dz_mm"], b["dheight_mm"])
                return (b["dx_mm"], b["dheight_mm"])
        return None

    L = max(100.0, math.dist((src[0], src[1]), (tgt[0], tgt[1])))
    dk = round(2500.0 / L, 4)
    e0 = measure()
    if e0 is None or math.hypot(*e0) < 0.8:
        return
    ep.call("knob", {"part": part, "axis": "yaw", "delta_mrad": dk})
    e1 = measure()
    ep.call("knob", {"part": part, "axis": "pitch", "delta_mrad": dk})
    e2 = measure()
    if e1 is None or e2 is None:
        return
    J = [
        [(e1[0] - e0[0]) / dk, (e2[0] - e1[0]) / dk],
        [(e1[1] - e0[1]) / dk, (e2[1] - e1[1]) / dk],
    ]
    det = J[0][0] * J[1][1] - J[0][1] * J[1][0]
    if abs(det) < 1e-12:
        return
    e = e2
    for _ in range(max_iter):
        if math.hypot(*e) < 0.8:
            break
        dyaw = (-e[0] * J[1][1] + e[1] * J[0][1]) / det
        dpitch = (-e[1] * J[0][0] + e[0] * J[1][0]) / det
        dyaw = max(-25.0, min(25.0, dyaw))
        dpitch = max(-25.0, min(25.0, dpitch))
        if abs(dyaw) >= 0.01:
            ep.call("knob", {"part": part, "axis": "yaw", "delta_mrad": round(dyaw, 4)})
        if abs(dpitch) >= 0.01:
            ep.call("knob", {"part": part, "axis": "pitch", "delta_mrad": round(dpitch, 4)})
        e = measure()
        if e is None:
            break


def _steer_cam_overlap(ep: Episode, part: str):
    """Overlap the 800nm focal spot onto the OPA focal spot using sample camera frames."""
    ep.call("block", {"arm": "800nm"})
    s_opa = ep.call("view_camera", {"plane": "sample"}).get("spots", [])
    ep.call("unblock", {"arm": "800nm"})
    if not s_opa:
        return
    opa_pt = (s_opa[0]["h_um"], s_opa[0]["v_um"])

    def diff():
        spots = ep.call("view_camera", {"plane": "sample"}).get("spots", [])
        if len(spots) < 2:
            return None
        pts = [(s["h_um"], s["v_um"]) for s in spots[:2]]
        if math.dist(pts[0], pts[1]) < 4.0:
            return (0.0, 0.0)
        pts.sort(key=lambda p: math.dist(p, opa_pt))
        return (pts[1][0] - pts[0][0], pts[1][1] - pts[0][1])

    e0 = diff()
    if e0 is None or math.hypot(*e0) < 4.0:
        return
    dk = 0.3
    ep.call("knob", {"part": part, "axis": "yaw", "delta_mrad": dk})
    e1 = diff()
    ep.call("knob", {"part": part, "axis": "pitch", "delta_mrad": dk})
    e2 = diff()
    if e1 is None or e2 is None:
        return
    J = [
        [(e1[0] - e0[0]) / dk, (e2[0] - e1[0]) / dk],
        [(e1[1] - e0[1]) / dk, (e2[1] - e1[1]) / dk],
    ]
    det = J[0][0] * J[1][1] - J[0][1] * J[1][0]
    if abs(det) < 1e-12:
        return
    e = e2
    for _ in range(3):
        if math.hypot(*e) < 4.0:
            break
        dyaw = max(-15.0, min(15.0, (-e[0] * J[1][1] + e[1] * J[0][1]) / det))
        dpitch = max(-15.0, min(15.0, (-e[1] * J[0][0] + e[0] * J[1][0]) / det))
        if abs(dyaw) >= 0.005:
            ep.call("knob", {"part": part, "axis": "yaw", "delta_mrad": round(dyaw, 4)})
        if abs(dpitch) >= 0.005:
            ep.call("knob", {"part": part, "axis": "pitch", "delta_mrad": round(dpitch, 4)})
        e = diff()
        if e is None:
            break


def _build_demo_1() -> dict:
    """Demo 1: Skipped OPA Manual & Saturated Camera (Seed 1, L1).
    Matches only table path (missing ~1527 mm OPA internal path), installs unfiltered BBO,
    saturates camera at 60,000 counts on coarse scan, submits -> time-zero-unreachable + saturated-signal.
    """
    seed, level = 1, 1
    ep = Episode(seed, level)
    # Reads table & sample_mount manuals, skipping the OPA manual!
    ep.call("read_manual", {"device": "table"})
    ep.call("read_manual", {"device": "sample_mount"})

    _, hp, zp = ep.lab.ports["800nm"]["pos"]
    _, ho, zo = ep.lab.ports["opa"]["pos"]

    # Buys unfiltered BBO-T236 (no bandpass filter!)
    ep.call("buy", {"items": {"DL-C25": 1, "BBO-T236": 1, "CAM-VSWIR": 1, "MIR-1": 4, "PER-1": 1}})
    ep.call("place", {"part": "sample", "x": 1300.0, "z": 600.0, "height": hp, "yaw_deg": 180.0})

    # Route OPA arm
    ep.call("unblock", {"arm": "opa"})
    ep.call("place", {"part": "periscope-1", "x": 2050.0, "z": zo, "height": hp, "yaw_deg": 180.0, "height_in": ho})
    _steer_ir(ep, "periscope-1", "opa", (2050.0, zo, hp), (1700.0, zo, hp), "x", max_iter=2)
    ep.call("place", {"part": "mirror-1", "x": 1700.0, "z": zo, "height": hp, "yaw_deg": -45.0})
    _steer_ir(ep, "mirror-1", "opa", (1700.0, zo, hp), (1700.0, 592.0, hp), "z", max_iter=2)
    ep.call("place", {"part": "mirror-2", "x": 1700.0, "z": 592.0, "height": hp, "yaw_deg": 135.0})
    _steer_ir(ep, "mirror-2", "opa", (1700.0, 592.0, hp), (1300.0, 592.0, hp), "x", max_iter=2)

    # Route 800nm arm matching ONLY table path (forgetting the ~1527 mm OPA internal path!)
    ep.call("unblock", {"arm": "800nm"})
    ep.call("place", {"part": "stage", "x": 1685.0, "z": zp + 15.0, "height": hp, "yaw_deg": 180.0})
    ep.call("place", {"part": "mirror-3", "x": 1780.0, "z": zp + 30.0, "height": hp, "yaw_deg": 135.0})
    _steer_ir(ep, "mirror-3", "800nm", (1780.0, zp + 30.0, hp), (1780.0, 608.0, hp), "z", max_iter=2)
    ep.call("place", {"part": "mirror-4", "x": 1780.0, "z": 608.0, "height": hp, "yaw_deg": 225.0})
    _steer_ir(ep, "mirror-4", "800nm", (1780.0, 608.0, hp), (1300.0, 608.0, hp), "x", max_iter=2)

    _steer_cam_overlap(ep, "mirror-4")

    # Coarse scan with unfiltered BBO -> saturates signal camera at 60,000 counts!
    ep.call("scan", {"start_mm": 0.0, "end_mm": 25.0, "step_mm": 0.25, "t_int": 0.2})
    ep.call("move_stage", {"position_mm": 12.5})
    ep.call("submit", {})

    res = ep.result()
    traj = ep.trajectory()
    tags, _ = SJ.analyse(res, traj)
    return {
        "id": "demo-skipped-opa-saturated-s1-l1",
        "label": "[Demo] Skipped OPA Manual & Saturated Camera · Seed 1 · L1",
        "model": "demo",
        "is_demo": True,
        "meta": ep.meta_snapshot(),
        "diagnostics": res,
        "failure_tags": [[t, why] for t, why in tags],
        "trajectory": traj,
    }


def _build_demo_2() -> dict:
    """Demo 2: Mount Block & Lens Clipping (Seed 3, L1).
    Places mirror-4 whose 38mm backing mount blocks the OPA beam mid-run, then shifts it slightly
    off-center on the lens so T_800 < 0.85 (and < 0.80) and submits slightly off time-zero ->
    clipping + missed-time-zero.
    """
    seed, level = 3, 1
    ep = Episode(seed, level)
    ep.call("read_manual", {"device": "table"})
    ep.call("read_manual", {"device": "opa"})
    ep.call("read_manual", {"device": "delay_stage"})
    ep.call("read_manual", {"device": "sample_mount"})

    port_x, hp, zp = ep.lab.ports["800nm"]["pos"]
    _, ho, zo = ep.lab.ports["opa"]["pos"]
    lam_o = ep.lab.opa_lambda
    L_opa = ep.lab.opa_extra_path

    det_items: dict[str, int] = {}
    eo = 1239.84 / lam_o
    if eo < 2.26 and (1239.84 / 800.0 + eo) > 2.26:
        det_items["GAP-TPA"] = 1
    else:
        det_items.update({"GAN-1": 1, "F-BP550": 1})
    if lam_o > 1000.0:
        det_items["CAM-VSWIR"] = 1

    ep.call("buy", {"items": {"DL-C25": 1, "MIR-1": 4, "PER-1": 1, **det_items}})
    ep.call("place", {"part": "sample", "x": 1300.0, "z": 600.0, "height": hp, "yaw_deg": 180.0})

    # Route OPA arm cleanly into z = 592 on the sample lens
    ep.call("unblock", {"arm": "opa"})
    ep.call("place", {"part": "periscope-1", "x": 2050.0, "z": zo, "height": hp, "yaw_deg": 180.0, "height_in": ho})
    _steer_ir(ep, "periscope-1", "opa", (2050.0, zo, hp), (1700.0, zo, hp), "x", max_iter=2)
    yaw_m1 = -45.0 if 592.0 < zo else 45.0
    ep.call("place", {"part": "mirror-1", "x": 1700.0, "z": zo, "height": hp, "yaw_deg": yaw_m1})
    _steer_ir(ep, "mirror-1", "opa", (1700.0, zo, hp), (1700.0, 592.0, hp), "z", max_iter=2)
    ep.call("place", {"part": "mirror-2", "x": 1700.0, "z": 592.0, "height": hp, "yaw_deg": 135.0})
    _steer_ir(ep, "mirror-2", "opa", (1700.0, 592.0, hp), (1300.0, 592.0, hp), "x", max_iter=2)

    # Place delay stage with proper coarse path so time-zero IS reachable near ~12.5 mm
    z_clip = 612.1  # ~11.6-12.1 mm off-center on the 12.7 mm lens -> T_800 ~ 0.50 (< 0.80)
    opa_total = (port_x - 2050.0) + abs(hp - ho) + 350.0 + abs(zo - 592.0) + 400.0 + L_opa
    p800_const = (port_x - 40.0) + 80.0 + (1500.0 - 40.0) + (1500.0 - 1300.0)
    a_x = (p800_const + z_clip - 30.0 - zp - opa_total) / 2.0
    p_x = round(a_x + 90.0 + 12.5, 2)

    ep.call("unblock", {"arm": "800nm"})
    ep.call("place", {"part": "stage", "x": p_x, "z": zp + 15.0, "height": hp, "yaw_deg": 180.0})
    ep.call("place", {"part": "mirror-3", "x": 1500.0, "z": zp + 30.0, "height": hp, "yaw_deg": 135.0})
    _steer_ir(ep, "mirror-3", "800nm", (1500.0, zp + 30.0, hp), (1500.0, 584.0, hp), "z", max_iter=2)

    # Mid-run mistake: place mirror-4 at z = 584 (yaw 225), where its 38mm backing mount blocks the OPA beam at z = 592!
    ep.call("place", {"part": "mirror-4", "x": 1500.0, "z": 584.0, "height": hp, "yaw_deg": 225.0})
    _steer_ir(ep, "mirror-4", "800nm", (1500.0, 584.0, hp), (1300.0, 596.0, hp), "x", max_iter=1)
    # Camera check reveals only 1 spot because OPA is absorbed on mount of mirror-4!
    ep.call("view_camera", {"plane": "sample"})

    # Fix mount block by shifting mirror-4 to z = 611.6, which clears OPA but clips 800nm on the lens edge!
    ep.call("move", {"part": "mirror-4", "x": 1500.0, "z": z_clip})
    _steer_ir(ep, "mirror-3", "800nm", (1500.0, zp + 30.0, hp), (1500.0, z_clip, hp), "z", max_iter=2)
    _steer_ir(ep, "mirror-4", "800nm", (1500.0, z_clip, hp), (1300.0, z_clip, hp), "x", max_iter=2)
    ep.call("view_camera", {"plane": "lens"})
    _steer_cam_overlap(ep, "mirror-4")

    # Single-beam background check
    ep.call("block", {"arm": "800nm"})
    ep.call("read_signal", {"t_int": 0.5})
    ep.call("unblock", {"arm": "800nm"})

    # Coarse scan with too-wide step misses the narrow ~20 um peak, submitting ~0.6 mm (~4000 fs) off time-zero!
    ep.call("scan", {"start_mm": 6.0, "end_mm": 19.0, "step_mm": 0.25, "t_int": 0.3})
    # Pick a stage position ~0.6 mm away from true time zero so |dt| >> 3 * tau_c while still reachable
    dt_cur = ep._truth()["dt_fs"] or 0.0
    x_zero = ep.stage_cmd - dt_cur * K.C_MM_PER_FS / 2.0
    x_off = max(0.5, min(24.5, round(x_zero + 0.6, 3)))
    ep.call("move_stage", {"position_mm": x_off})
    ep.call("submit", {})

    res = ep.result()
    traj = ep.trajectory()
    tags, _ = SJ.analyse(res, traj)
    return {
        "id": "demo-mount-block-clipping-s3-l1",
        "label": "[Demo] Mount Block & Lens Clipping · Seed 3 · L1",
        "model": "demo",
        "is_demo": True,
        "meta": ep.meta_snapshot(),
        "diagnostics": res,
        "failure_tags": [[t, why] for t, why in tags],
        "trajectory": traj,
    }


def build_bundle(jobs_dirs: list[str], include_demos: bool = False) -> dict:
    discovered: list[dict] = []
    seen_dirs: set[str] = set()
    for root in jobs_dirs:
        if not os.path.exists(root):
            print(f"[build_viewer] Note: {root} does not exist, skipping", file=sys.stderr)
            continue
        for run_dir in sorted(SJ.find_runs(root)):
            abs_dir = os.path.abspath(run_dir)
            if abs_dir in seen_dirs:
                continue
            seen_dirs.add(abs_dir)
            entry = load_run_dir(run_dir, root)
            if entry is not None:
                discovered.append(entry)

    # Sort non-empty real LLM runs first (newest first, e.g. Flash L1), then oracle runs, then empty runs
    def _sort_key(r: dict) -> tuple:
        has_steps = 0 if r["trajectory"] else 1
        is_oracle = 1 if r["model"] in ("oracle", "?", "demo") else 0
        return (has_steps, is_oracle, r["id"])

    discovered.sort(key=_sort_key)
    # Within non-empty LLM runs, prefer newest timestamp first
    non_empty_llm = [r for r in discovered if r["trajectory"] and r["model"] not in ("oracle", "?", "demo")]
    rest = [r for r in discovered if not (r["trajectory"] and r["model"] not in ("oracle", "?", "demo"))]
    non_empty_llm.sort(key=lambda r: r["id"], reverse=True)
    discovered = non_empty_llm + rest

    # Disambiguate any duplicate labels across distinct Harbor trials
    used_labels: set[str] = set()
    for r in discovered:
        lbl = r["label"]
        if lbl in used_labels:
            short = r["id"].split("/")[-1]
            lbl = f"{lbl} ({short})"
            r["label"] = lbl
        used_labels.add(lbl)

    runs = list(discovered)
    if include_demos:
        runs.append(_build_demo_1())
        runs.append(_build_demo_2())

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "runs": runs,
    }


def write_bundle(bundle: dict, out_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    payload = json.dumps(bundle, separators=(",", ":"), ensure_ascii=False)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"window.GSS_RUNS_BUNDLE = {payload};\n")


def default_jobs_dirs() -> list[str]:
    """Include jobs in this checkout and any registered worktrees with a jobs folder."""
    roots = [ROOT]
    try:
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        roots.extend(line.removeprefix("worktree ") for line in result.stdout.splitlines()
                     if line.startswith("worktree "))
    except (OSError, subprocess.CalledProcessError):
        pass
    return list(dict.fromkeys(os.path.join(root, "jobs") for root in roots
                              if os.path.isdir(os.path.join(root, "jobs"))))


def _jobs_fingerprint(jobs_dirs: list[str]) -> tuple:
    files = []
    for root in jobs_dirs:
        if not os.path.isdir(root):
            continue
        for run_dir in SJ.find_runs(root):
            for name in ("diagnostics.json", "trajectory.json"):
                path = os.path.join(run_dir, name)
                try:
                    stat = os.stat(path)
                    files.append((path, stat.st_mtime_ns, stat.st_size))
                except OSError:
                    files.append((path, None, None))
    return tuple(sorted(files))


def serve_viewer(viewer_dir: str, port: int, jobs_dirs: list[str],
                 include_demos: bool, out_path: str) -> None:
    cache: dict[str, Any] = {"fingerprint": None, "bundle": None}
    lock = threading.Lock()

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=viewer_dir, **kwargs)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def do_GET(self):
            if urlsplit(self.path).path != "/api/runs":
                if "If-Modified-Since" in self.headers:
                    del self.headers["If-Modified-Since"]
                return super().do_GET()
            with lock:
                fingerprint = _jobs_fingerprint(jobs_dirs)
                if cache["bundle"] is None or fingerprint != cache["fingerprint"]:
                    cache["bundle"] = build_bundle(jobs_dirs, include_demos=include_demos)
                    cache["fingerprint"] = fingerprint
                    write_bundle(cache["bundle"], out_path)
                payload = json.dumps(cache["bundle"], separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            try:
                self.wfile.write(payload)
            except BrokenPipeError:
                pass  # Browser navigated away while a large bundle was being sent.

    handler = Handler
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Serving {viewer_dir} at http://127.0.0.1:{port} (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("jobs_dir", nargs="*", help="Harbor jobs folder(s) to scan (defaults to jobs/ in all registered worktrees)")
    ap.add_argument("--demos", action="store_true", help="Include synthetic failure demo runs")
    ap.add_argument("--no-demos", action="store_true", help="Do not include synthetic failure demo runs (default)")
    ap.add_argument("--serve", action="store_true", help="Serve viewer/ over http.server after building")
    ap.add_argument("--port", type=int, default=8765, help="Port for --serve (default: 8765)")
    ap.add_argument(
        "-o",
        "--out",
        default=os.path.join(ROOT, "viewer", "runs_bundle.js"),
        help="Output JS bundle path (default: viewer/runs_bundle.js)",
    )
    args = ap.parse_args(argv)

    jobs_dirs = list(args.jobs_dir)
    if not jobs_dirs:
        jobs_dirs = default_jobs_dirs()

    bundle = build_bundle(jobs_dirs, include_demos=bool(args.demos and not args.no_demos))
    write_bundle(bundle, args.out)
    print(f"Wrote {len(bundle['runs'])} run(s) to {args.out}", file=sys.stderr)

    if args.serve:
        serve_viewer(os.path.join(ROOT, "viewer"), args.port, jobs_dirs,
                     bool(args.demos and not args.no_demos), args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
