"""L2: beams cross at 90 deg at the sample, each through its own lens of the mount."""

import math

import pytest

from sim import Episode
from sim import catalogue as cat
from sim import constants as K
from sim import physics as P
from sim import reward as RW
from sim.optics import Part
from solution.expert import run_in_process

SEEDS = range(1, 11)


def perfect_l2(seed):
    """Error-free L2 layout: sample at (1200, 600) facing +x; 800 nm via lens A (yaw 135), OPA via lens B."""
    ep = Episode(seed, level=2)
    ep.lab.defocus = 0.0
    ep.call("buy", {"items": {"DL-C25": 1, "MIR-1": 4, "PER-1": 1}})
    _, h_p, z_p = ep.lab.ports["800nm"]["pos"]
    _, h_o, z_o = ep.lab.ports["opa"]["pos"]
    r = math.radians
    z2 = z_p + 100
    x2 = 1800 - z2
    zq = z_o - 100
    xp = zq + 600
    parts = {
        "sample": Part("sample", "sample", (1200.0, h_p, 600.0), r(0), level=2),
        "periscope-1": Part("periscope-1", "periscope", (2050.0, h_p, z_o), r(180), height_in=h_o),
        "mirror-1": Part("mirror-1", "mirror", (xp, h_p, z_o), r(315)),
        "mirror-2": Part("mirror-2", "mirror", (xp, h_p, zq), r(157.5)),
        "stage": Part("stage", "stage", (800.0, h_p, z_p + 12), r(180), travel=25.0),
        "mirror-3": Part("mirror-3", "mirror", (x2, h_p, z_p + 24), r(135)),
        "mirror-4": Part("mirror-4", "mirror", (x2, h_p, z2), r(202.5)),
    }
    for k, p in parts.items():
        ep.inv[k]["part"] = p
    ep._invalidate()
    ep.call("unblock", {"arm": "800nm"})
    ep.call("unblock", {"arm": "opa"})
    return ep


def zero_delay(ep):
    dt0 = ep._truth()["dt_fs"]
    st = ep.inv["stage"]["part"]
    st.pos = (st.pos[0] + dt0 * K.C_MM_PER_FS / 2 + 12.5, st.pos[1], st.pos[2])
    ep._invalidate()
    ep.call("move_stage", {"position_mm": 12.5})


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_perfect_l2_layout_gives_eta_1(seed):
    ep = perfect_l2(seed)
    b = ep._beams()
    assert b["800nm"].lens_role == "lens-A" and b["opa"].lens_role == "lens-B"
    assert b["800nm"].spot == pytest.approx((0.0, 0.0), abs=1e-6)
    assert b["opa"].spot == pytest.approx((0.0, 0.0), abs=1e-6)
    zero_delay(ep)
    t = ep._truth()
    assert abs(t["dt_fs"]) < 1.0 and t["eta"] > 0.999


def test_broadened_window_used_in_reward():
    assert K.TAU_C_L2 == pytest.approx(186.2, abs=0.5)
    assert K.L2_PEAK == pytest.approx(K.TAU_C / K.TAU_C_L2)
    assert P.temporal_factor(K.TAU_C_L2, level=2) == pytest.approx(math.exp(-1))
    assert P.temporal_factor(K.TAU_C_L2, level=1) < 1e-3


def test_same_lens_is_not_the_required_geometry():
    ep = perfect_l2(2)
    b = ep._beams()
    b["opa"].lens_role = "lens-A"  # pretend both came through lens A
    assert P.spatial_overlap(b["800nm"], b["opa"], level=2) == 0.0
    assert P.spatial_overlap(b["800nm"], b["opa"], level=1) > 0.99


def test_spot_is_stretched_on_the_tilted_sample():
    ep = perfect_l2(2)
    s = {x["beam"]: x for x in ep.call("view_camera", {"plane": "sample"})["spots"]}
    assert s["800nm"]["radius_h_um"] / s["800nm"]["radius_v_um"] == pytest.approx(math.sqrt(2), rel=0.1)
    # a horizontal angle error of the 800 nm beam moves its spot along h by ~ f theta / cos45
    m = ep.inv["mirror-4"]["part"]
    m.knob_yaw += 0.0005
    ep._invalidate()
    h = ep._beams()["800nm"].spot[0]
    assert abs(h) == pytest.approx(K.LENS_F * 0.001 * math.sqrt(2), rel=0.15)


def test_l2_routes():
    def viable(d, f, lam):
        return P.detection_viable(cat.PARTS[d], None if f is None else cat.filter_spec(f), lam, 2)
    assert not viable("BBO-SFG-1300", "F-BP495", 1300.0)  # no phase matching at 90 deg
    assert viable("GAP-TPA", None, 1300.0)
    assert not viable("GAP-TPA", None, 600.0)  # reduced peak vs two single-beam TPA backgrounds
    assert viable("GAN-1", "F-BP550", 600.0)
    assert viable("GAN-1", "F-VIS495", 450.0)
    assert RW.c_min(1300.0, 2) == 7750 and RW.c_min(600.0, 2) == 2000 and RW.c_min(450.0, 2) == 2000


def test_l2_manuals():
    ep = Episode(1, level=2)
    m = ep.call("read_manual", {"device": "sample_mount"})["manual"]
    assert "90-degree crossing" in m and f"{K.TAU_C_L2:.0f} fs" in m
    assert "phase-matched" in ep.call("read_manual", {"device": "nonlinear"})["manual"]
    with pytest.raises(ValueError):
        Episode(1, level=3)


@pytest.mark.parametrize("seed", SEEDS)
def test_expert_l2(seed):
    ep, _ = run_in_process(seed, level=2)
    r = ep.result()
    assert r["level"] == 2 and r["design_viable"]
    assert r["eta"] >= 0.9
    assert r["lab_time_frac"] <= 0.65


@pytest.mark.parametrize("seed", [1, 4, 7])
def test_stop_early_and_do_nothing_l2(seed):
    assert Episode(seed, level=2).result()["reward"] == 0.0
    ep, _ = run_in_process(seed, stop_early=True, level=2)
    assert ep.result()["reward"] < 0.05
