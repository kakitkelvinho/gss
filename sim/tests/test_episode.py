import json
import math

import pytest

from sim import Episode
from sim import constants as K
from sim.lab import Lab
from sim.optics import Part
from solution.expert import run_in_process

SEEDS = range(1, 11)


def test_rng_determinism_lab_independent_of_actions():
    a, b = Episode(5), Episode(5)
    a.call("buy", {"items": ["MIR-1"]})
    a.call("read_signal", {"t_int": 1.0})
    a.call("place", {"part": "mirror-1", "x": 1000, "z": 500, "height": 120, "yaw_deg": 45})
    assert a.lab.ports == b.lab.ports
    assert a.lab.opa_path == b.lab.opa_path and a.lab.defocus == b.lab.defocus
    assert Lab(5).mount_error("mirror-3") == Lab(5).mount_error("mirror-3")
    assert Lab(5).ports != Lab(6).ports


def perfect_layout(seed):
    """Hand-built expert layout with no placement errors and no defocus."""
    ep = Episode(seed)
    ep.lab.defocus = 0.0
    ep.call("buy", {"items": {"DL-C25": 1, "BBO-T236": 1, "MIR-1": 4, "PER-1": 1}})
    _, h_p, z_p = ep.lab.ports["pump"]["pos"]
    _, h_o, z_o = ep.lab.ports["probe"]["pos"]
    r = math.radians
    parts = {
        "sample": Part("sample", "sample", (1300.0, h_p, 600.0), r(180)),
        "periscope-1": Part("periscope-1", "periscope", (2050.0, h_p, z_o), r(180), height_in=h_o),
        "mirror-1": Part("mirror-1", "mirror", (1700.0, h_p, z_o), r(315)),
        "mirror-2": Part("mirror-2", "mirror", (1700.0, h_p, 608.0), r(135)),
        "stage": Part("stage", "stage", (900.0, h_p, z_p + 12), r(180), travel=25.0),
        "mirror-3": Part("mirror-3", "mirror", (1500.0, h_p, z_p + 24), r(135)),
        "mirror-4": Part("mirror-4", "mirror", (1500.0, h_p, 592.0), r(225)),
    }
    for k, p in parts.items():
        ep.inv[k]["part"] = p
    ep._invalidate()
    ep.call("unblock", {"arm": "pump"})
    ep.call("unblock", {"arm": "probe"})
    return ep


def test_hand_built_layout_reaches_sample_and_perfect_alignment_gives_eta_1():
    ep = perfect_layout(3)
    b = ep._beams()
    assert b["pump"].at_sample and b["probe"].at_sample
    assert b["pump"].T == 1.0 and b["probe"].T == 1.0
    # place the stage apex so that dt = 0: dt is linear in stage position (2 mm of path per mm)
    dt0 = ep._truth()["dt_fs"]
    stage = ep.inv["stage"]["part"]
    stage.pos = (stage.pos[0] + dt0 * K.C_MM_PER_FS / 2 + 12.5, stage.pos[1], stage.pos[2])
    ep._invalidate()
    ep.call("move_stage", {"position_mm": 12.5})
    t = ep._truth()
    assert abs(t["dt_fs"]) < 1.0
    assert t["O"] == pytest.approx(1.0, abs=1e-3)
    assert t["eta"] > 0.999


def test_time_and_cost_ledger():
    ep = Episode(1)
    r = ep.call("buy", {"items": ["MIR-1", "MIR-1", "DL-M25"]})
    assert r["spent_eur"] == 700
    assert ep.t == pytest.approx(900.0)
    assert r["lab_time_remaining_min"] == pytest.approx(225.0)
    r = ep.call("buy", {"items": {"DL-C100": 8}})
    assert "refused" in r["outcome"] and ep.cost == 700
    assert set(ep.inv) >= {"mirror-1", "mirror-2", "stage"}


def test_bad_arguments_cost_5s_and_change_nothing():
    ep = Episode(1)
    ep.call("buy", {"items": ["MIR-1", "DL-C25", "BBO-T236"]})
    t0 = ep.t
    bad = [
        ("place", {"part": "mirror-1", "x": float("nan"), "z": 1, "height": 100, "yaw_deg": 0}),
        ("place", {"part": "mirror-1", "x": float("inf"), "z": 1, "height": 100, "yaw_deg": 0}),
        ("place", {"part": "mirror-1", "x": "100", "z": 1, "height": 100, "yaw_deg": 0}),
        ("place", {"part": "mirror-1", "x": 1e300, "z": 1, "height": 100, "yaw_deg": 0}),
        ("place", {"part": "mirror-9", "x": 100, "z": 1, "height": 100, "yaw_deg": 0}),
        ("knob", {"part": "mirror-1", "axis": "roll", "delta_mrad": 1}),
        ("read_signal", {"t_int": -1}),
        ("read_signal", {"t_int": True}),
        ("scan", {"start_mm": 0, "end_mm": 25, "step_mm": 1e-6, "t_int": 0.1}),
        ("scan", {"start_mm": -5, "end_mm": 25, "step_mm": 0.1, "t_int": 0.1}),
        ("buy", {"items": ["NOPE"]}),
        ("buy", {"items": {"MIR-1": -3}}),
        ("hack", {}),
        ("status", {"extra": 1}),
    ]
    for tool, args in bad:
        r = ep.call(tool, args)
        assert "error" in r, (tool, args, r)
    assert ep.t == pytest.approx(t0 + 5.0 * len(bad))
    assert ep.inv["mirror-1"]["part"] is None and ep.cost == 3850
    assert ep.malformed == len(bad)


def test_every_action_costs_at_least_5s():
    ep = Episode(1)
    for _ in range(20):
        ep.call("status", {})
    assert ep.t == pytest.approx(100.0)


def test_timeout_auto_submits_and_locks():
    ep = Episode(2)
    n = 0
    while not ep.over:
        r = ep.call("read_signal", {"t_int": 10.0})
        n += 1
        assert n < 2000
    assert "auto-submitted" in r["error"]
    assert ep.t <= K.BUDGET_S
    assert ep.final["ended_by"] == "timeout"
    assert ep.call("status", {}) == {"error": "episode over"}


def test_post_submit_lock():
    ep = Episode(2)
    ep.call("submit", {})
    t = ep.t
    assert ep.call("unblock", {"arm": "pump"}) == {"error": "episode over"}
    assert ep.call("buy", {"items": ["MIR-1"]}) == {"error": "episode over"}
    assert ep.t == t and ep.shutter_open["pump"] is False
    assert ep.result()["ended_by"] == "agent"


FORBIDDEN = {"eta", "O", "dt_fs", "abs_dt_fs", "truth", "T_pump", "T_probe", "defocus", "opl", "reward"}


def _keys(x):
    if isinstance(x, dict):
        for k, v in x.items():
            yield k
            yield from _keys(v)
    elif isinstance(x, list):
        for v in x:
            yield from _keys(v)


def test_no_hidden_truth_in_tool_outputs():
    outputs = []
    ep_holder = {}

    def call(tool, **a):
        r = ep_holder["ep"].call(tool, a)
        outputs.append(r)
        return r

    from sim import Episode as E
    from solution.expert import Expert

    ep_holder["ep"] = ep = E(4)
    Expert(call).run()
    for r in outputs:
        assert not (set(_keys(r)) & FORBIDDEN), r
    text = json.dumps(outputs)
    assert f"{ep.lab.defocus}" not in text
    # tape measure is noisy: repeated reads differ
    ep3 = E(4)
    ep3.call("unblock", {"arm": "pump"})
    reads = {ep3.call("measure_path", {"arm": "pump"})["path_mm"] for _ in range(5)}
    assert len(reads) > 1


def test_do_nothing_scores_zero():
    for s in SEEDS:
        ep = Episode(s)
        ep.call("submit", {})
        r = ep.result()
        assert r["reward"] == 0.0 and r["stray_events"] == 0


@pytest.mark.parametrize("seed", SEEDS)
def test_expert_meets_pass_criteria(seed):
    ep, _ = run_in_process(seed)
    r = ep.result()
    assert r["eta"] >= 0.9
    assert r["lab_time_frac"] <= 0.65
    assert r["ended_by"] == "agent"


@pytest.mark.parametrize("seed", SEEDS)
def test_stop_early_scores_below_005(seed):
    ep, _ = run_in_process(seed, stop_early=True)
    r = ep.result()
    assert r["O"] > 0.9  # it did get spatial overlap
    assert r["reward"] < 0.05


def test_camera_shows_clipping_as_dim_spot():
    ep = perfect_layout(3)
    full = {s["beam"]: s["relative_power"] for s in ep.call("view_camera", {"plane": "sample"})["spots"]}
    assert full["probe"] == pytest.approx(1.0, abs=0.08)
    # slide mirror-2 in its own plane: the reflected beam is unchanged but now hits 11.3 mm off-centre
    m = ep.inv["mirror-2"]["part"]
    m.pos = (m.pos[0] + 8.0, m.pos[1], m.pos[2] + 8.0)
    ep._invalidate()
    spots = {s["beam"]: s for s in ep.call("view_camera", {"plane": "sample"})["spots"]}
    assert spots["probe"]["relative_power"] < 0.6
