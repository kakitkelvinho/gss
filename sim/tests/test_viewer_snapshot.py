"""Unit tests for `gss.viewer.v1` snapshots in `sim.Episode`, `server.app`, and `scripts.build_viewer`."""

from __future__ import annotations

import json
import os
import time

import pytest

from scripts import build_viewer as BV
from sim import Episode
from solution.expert import run_in_process


def _all_keys(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield k
            yield from _all_keys(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _all_keys(item)


def _assert_vec_mm(d: dict):
    assert isinstance(d, dict)
    assert set(d.keys()) >= {"x", "z", "h"}
    for k in ("x", "z", "h"):
        assert isinstance(d[k], (int, float)) and not isinstance(d[k], bool)


def test_call_never_contains_snapshot_and_meta_matches_schema():
    outputs = []
    ep = Episode(1, level=1)

    meta = ep.meta_snapshot()
    assert meta["schema_version"] == "gss.viewer.v1"
    assert meta["seed"] == 1 and meta["level"] == 1
    assert set(meta.keys()) == {
        "schema_version", "seed", "level", "opa_lambda_nm", "c_min_eur",
        "spend_cap_eur", "budget_s", "table_mm", "desk_mm", "walk_offset_mm",
        "ports", "housings_mm",
    }
    for arm in ("800nm", "opa"):
        p_raw = ep.lab.ports[arm]["pos"]
        p_snap = meta["ports"][arm]["pos"]
        _assert_vec_mm(p_snap)
        # Verify Vec = (x, height, z) -> {"x": v[0], "z": v[2], "h": v[1]}
        assert p_snap["x"] == pytest.approx(p_raw[0])
        assert p_snap["h"] == pytest.approx(p_raw[1])
        assert p_snap["z"] == pytest.approx(p_raw[2])

    def tracked_call(tool, **kwargs):
        res = ep.call(tool, kwargs)
        outputs.append(res)
        return res

    from solution.expert import Expert
    Expert(tracked_call).run()
    # Also check post-submit call
    outputs.append(ep.call("status", {}))

    for out in outputs:
        assert "snapshot" not in set(_all_keys(out))


def test_step_snapshots_l1_and_l2_lenses_camera_ir_and_scan_peak():
    # Run L1 expert (exercises ir_card, view_camera, >600-point coarse scan, fine scan, etc.)
    ep1, _ = run_in_process(1, level=1)
    traj1 = ep1.trajectory()
    assert len(traj1) > 20

    saw_ir = False
    saw_cam = False
    saw_long_scan = False
    saw_l1_lens = False

    for step in traj1:
        assert "reward" in step["truth"]
        snap = step["snapshot"]
        assert set(snap.keys()) == {
            "you_mm", "shutters_open", "cost_eur", "stage_cmd_mm", "stage_true_mm",
            "installed", "parts", "beams", "ir_probe", "camera_frame", "scan_data",
        }
        assert set(snap["beams"].keys()) == {"800nm", "opa"}
        for arm in ("800nm", "opa"):
            b = snap["beams"][arm]
            assert set(b.keys()) == {
                "open", "end", "end_note", "T", "opl_mm", "spot_mm", "segments", "hits",
            }
            for seg in b["segments"]:
                assert len(seg) == 2
                _assert_vec_mm(seg[0])
                _assert_vec_mm(seg[1])

        for p in snap["parts"]:
            _assert_vec_mm(p["pos"])
            if p["kind"] == "sample":
                assert p["level"] == 1
                assert len(p["lenses"]) == 1
                assert p["lenses"][0]["role"] == "lens"
                _assert_vec_mm(p["lenses"][0]["pos"])
                saw_l1_lens = True
            else:
                assert p["lenses"] == []

        if step["tool"] == "ir_card" and "point" in step["result"]:
            assert snap["ir_probe"] is not None
            _assert_vec_mm(snap["ir_probe"])
            assert isinstance(snap["ir_probe"]["beams"], list)
            saw_ir = True

        if step["tool"] == "view_camera":
            assert snap["camera_frame"] is not None
            assert snap["camera_frame"]["plane"] in ("sample", "lens")
            assert isinstance(snap["camera_frame"]["spots"], list)
            saw_cam = True

        if step["tool"] == "scan" and step["result"].get("n_points", 0) > 600:
            sd = snap["scan_data"]
            assert sd is not None
            assert sd["n_points"] > 600
            assert len(sd["points"]) <= 600
            # Verify endpoints and peak are preserved: replay just to check raw scan peak or check monotonic bounds
            xs = [pt[0] for pt in sd["points"]]
            assert xs == sorted(xs) or xs == sorted(xs, reverse=True)
            assert xs[0] == pytest.approx(step["args"]["start_mm"], abs=1e-4)
            saw_long_scan = True

    assert saw_ir and saw_cam and saw_long_scan and saw_l1_lens

    # Explicitly test scan downsampling preserves exact argmax & endpoints on a 2501-point scan
    ep_scan = Episode(1, level=1)
    ep_scan.call("buy", {"items": {"DL-C25": 1, "GAP-TPA": 1, "MIR-1": 1}})
    ep_scan.call("place", {"part": "sample", "x": 1300.0, "z": 600.0, "height": 120.0, "yaw_deg": 180.0})
    # Also check knob(..., watch=True) populates camera_frame when near desk
    ep_scan.call("place", {"part": "mirror-1", "x": 400.0, "z": 600.0, "height": 120.0, "yaw_deg": 0.0})
    knob_res = ep_scan.call("knob", {"part": "mirror-1", "axis": "yaw", "delta_mrad": 1.0, "watch": True})
    assert "snapshot" not in knob_res
    assert ep_scan.trajectory()[-1]["snapshot"]["camera_frame"] is not None

    raw_scan = ep_scan.call("scan", {"start_mm": 0.0, "end_mm": 25.0, "step_mm": 0.01, "t_int": 0.05})
    assert len(raw_scan["points"]) == 2501
    raw_peak = max(raw_scan["points"], key=lambda p: p[1])
    snap_scan = ep_scan.trajectory()[-1]["snapshot"]["scan_data"]
    assert snap_scan["n_points"] == 2501
    assert len(snap_scan["points"]) <= 600
    assert snap_scan["points"][0] == raw_scan["points"][0]
    assert snap_scan["points"][-1] == raw_scan["points"][-1]
    assert raw_peak in snap_scan["points"]

    # Verify L2 sample mount exposes two lenses (lens-A and lens-B)
    ep2 = Episode(1, level=2)
    ep2.call("place", {"part": "sample", "x": 1200.0, "z": 600.0, "height": 120.0, "yaw_deg": 0.0})
    sample_parts = [p for p in ep2.trajectory()[-1]["snapshot"]["parts"] if p["kind"] == "sample"]
    assert len(sample_parts) == 1
    lenses_l2 = sample_parts[0]["lenses"]
    assert sample_parts[0]["level"] == 2
    assert [l["role"] for l in lenses_l2] == ["lens-A", "lens-B"]
    for l in lenses_l2:
        _assert_vec_mm(l["pos"])
        assert l["f_mm"] == pytest.approx(100.0)


def test_build_viewer_retro_replays_stripped_legacy_trajectory(tmp_path):
    ep_orig, _ = run_in_process(2, level=2)
    orig_diag = ep_orig.result()
    orig_traj = ep_orig.trajectory()
    orig_last_truth = orig_traj[-1]["truth"]

    # Strip snapshots, meta, and reward from truth; also inject legacy 'pump'/'probe' arm names
    stripped_steps = []
    for s in orig_traj:
        args_copy = dict(s["args"])
        if args_copy.get("arm") == "800nm":
            args_copy["arm"] = "pump"
        elif args_copy.get("arm") == "opa":
            args_copy["arm"] = "probe"
        truth_copy = {k: v for k, v in s["truth"].items() if k != "reward"}
        stripped_steps.append({
            "i": s["i"],
            "tool": s["tool"],
            "args": args_copy,
            "cost_s": s["cost_s"],
            "t_s": s["t_s"],
            "result": s["result"],
            "truth": truth_copy,
        })

    run_dir = tmp_path / "jobs" / "trial_legacy" / "verifier"
    run_dir.mkdir(parents=True)
    (run_dir / "diagnostics.json").write_text(json.dumps(orig_diag), encoding="utf-8")
    (run_dir / "trajectory.json").write_text(
        json.dumps({"seed": 2, "trajectory": stripped_steps}),
        encoding="utf-8",
    )

    out_js = tmp_path / "runs_bundle.js"
    rc = BV.main([str(tmp_path / "jobs"), "--demos", "-o", str(out_js)])
    assert rc == 0

    raw_js = out_js.read_text(encoding="utf-8").strip()
    assert raw_js.startswith("window.GSS_RUNS_BUNDLE = ") and raw_js.endswith(";")
    bundle = json.loads(raw_js[len("window.GSS_RUNS_BUNDLE = "):-1])
    assert bundle["schema_version"] == "gss.viewer.v1"
    assert len(bundle["runs"]) == 3  # 1 replayed run + 2 demos

    replayed_run = next(r for r in bundle["runs"] if not r["is_demo"])
    assert replayed_run["meta"]["seed"] == 2 and replayed_run["meta"]["level"] == 2
    assert len(replayed_run["trajectory"]) == len(orig_traj)
    assert all("snapshot" in st and "reward" in st["truth"] for st in replayed_run["trajectory"])

    final_truth = replayed_run["trajectory"][-1]["truth"]
    assert final_truth["O"] == pytest.approx(orig_last_truth["O"], abs=1e-6)
    assert final_truth["T_800"] == pytest.approx(orig_last_truth["T_800"], abs=1e-6)
    assert final_truth["T_opa"] == pytest.approx(orig_last_truth["T_opa"], abs=1e-6)
    assert final_truth["dt_fs"] == pytest.approx(orig_last_truth["dt_fs"], abs=1e-6)

    # Verify the two synthetic demos and their speed (<0.2s total) + failure tags
    t_demo0 = time.perf_counter()
    demo_bundle = BV.build_bundle([], include_demos=True)
    demo_elapsed = time.perf_counter() - t_demo0
    assert demo_elapsed < 0.2

    d1, d2 = demo_bundle["runs"]
    d1_tags = {t for t, _ in d1["failure_tags"]}
    assert {"time-zero-unreachable", "saturated-signal"} <= d1_tags
    d1_scans = [s for s in d1["trajectory"] if s["tool"] == "scan"]
    assert d1_scans and d1_scans[0]["snapshot"]["scan_data"]["saturated"] is True
    assert max(p[1] for p in d1_scans[0]["snapshot"]["scan_data"]["points"]) == 60000

    d2_tags = {t for t, _ in d2["failure_tags"]}
    assert {"clipping", "missed-time-zero"} <= d2_tags
    assert d2["diagnostics"]["T_800"] < 0.80  # < 0.85 and triggers 'clipping'
    assert any("mount of mirror-4" in (s["truth"].get("end_opa") or "") for s in d2["trajectory"])


def test_real_jobs_directory_loads_gracefully_if_present():
    jobs_root = os.path.join(BV.ROOT, "jobs")
    if not os.path.isdir(jobs_root):
        pytest.skip("jobs/ directory not present")
    bundle = BV.build_bundle([jobs_root], include_demos=False)
    assert bundle["schema_version"] == "gss.viewer.v1"
    for r in bundle["runs"]:
        assert r["meta"]["schema_version"] == "gss.viewer.v1"
        for step in r["trajectory"]:
            assert "snapshot" in step and "reward" in step["truth"]
