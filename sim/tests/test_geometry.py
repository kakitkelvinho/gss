import math

import pytest

from sim import constants as K
from sim import vec as V
from sim.optics import Part, clip_transmission, trace

PUMP = (2250.0, 120.0, 300.0)
WEST = (-1.0, 0.0, 0.0)


def els(*parts, defocus=0.0):
    out = []
    for p in parts:
        out.extend(p.elements(defocus))
    return out


def test_mirror_45_turns_beam():
    m = Part("mirror-1", "mirror", (1500.0, 120.0, 300.0), math.radians(315))  # -x -> -z
    b = trace("pump", PUMP, WEST, els(m), [])
    assert b.hits[0].part_id == "mirror-1"
    a, c = b.segments[1]
    d = V.unit(V.sub(c, a))
    assert d == pytest.approx((0.0, 0.0, -1.0), abs=1e-9)
    assert b.end == "stray"  # leaves the table at z = 0


def test_back_of_mirror_absorbs():
    m = Part("mirror-1", "mirror", (1500.0, 120.0, 300.0), math.radians(135))  # faces away from the beam
    b = trace("pump", PUMP, WEST, els(m), [])
    assert b.end == "absorbed" and b.T == 0.0


def test_beam_beyond_edge_misses_and_clipping_rolls_off():
    m = Part("mirror-1", "mirror", (1500.0, 120.0, 314.0), math.radians(315))  # 14 mm off -> miss
    b = trace("pump", PUMP, WEST, els(m), [])
    assert not b.hits
    assert clip_transmission(9.9, 10.0, 12.7) == 1.0
    assert clip_transmission(11.35, 10.0, 12.7) == pytest.approx(0.5)
    assert clip_transmission(12.7, 10.0, 12.7) < 1e-3


def test_knob_yaw_deflects_twice():
    m = Part("mirror-1", "mirror", (1500.0, 120.0, 300.0), math.radians(315), knob_yaw=0.001)
    b = trace("pump", PUMP, WEST, els(m), [])
    a, c = b.segments[1]
    d = V.unit(V.sub(c, a))
    assert abs(math.atan2(d[0], -d[2])) == pytest.approx(0.002, abs=1e-9)


def test_retro_returns_antiparallel_and_adds_twice_the_travel():
    def run(pos):
        s = Part("stage", "stage", (800.0, 120.0, 312.0), math.pi, stage_pos=pos)
        return trace("pump", PUMP, WEST, els(s), [])

    b0, b1 = run(0.0), run(5.0)
    a, c = b0.segments[-1]
    assert V.unit(V.sub(c, a)) == pytest.approx((1.0, 0.0, 0.0), abs=1e-12)
    assert a[2] == pytest.approx(324.0)  # entered 12 mm off the apex line, leaves 12 mm on the other side
    # both end on the table edge at x = 2400; extra path is exactly 2 x 5 mm
    assert b1.opl - b0.opl == pytest.approx(10.0, abs=1e-9)


def test_periscope_changes_height_keeps_direction():
    p = Part("periscope-1", "periscope", (2050.0, 150.0, 300.0), math.pi, height_in=120.0)
    b = trace("pump", PUMP, WEST, els(p), [])
    a, c = b.segments[-1]
    assert a[1] == pytest.approx(150.0)
    assert V.unit(V.sub(c, a)) == pytest.approx(WEST, abs=1e-12)


def test_lens_spot_and_opl():
    lens = Part("sample", "sample", (1300.0, 120.0, 308.0), math.pi)
    th = 0.002
    d = (-math.cos(th), 0.0, -math.sin(th))  # yaw slightly toward -z
    b = trace("pump", (1500.0, 120.0, 300.0), d, els(lens, defocus=0.3), [])
    assert b.at_sample
    # lens axis -x; camera h axis = yaw(axis) - 90 deg = +z direction; ray tilts toward -z
    rho_h = b.lens_hit[0]
    expect = K.LENS_F * (-th) + 0.3 * (-th) - 0.3 * rho_h / K.LENS_F
    assert b.spot[0] == pytest.approx(expect, rel=1e-3)
    # OPL: wavefront through lens centre + f + dz
    assert b.opl == pytest.approx(200.0 / math.cos(th) - V.dot((0.0, 0.0, b.segments[-1][1][2] - 308.0), d)
                                  + K.LENS_F + 0.3, abs=1e-6)


def test_mount_plate_behind_mirror_blocks_a_passing_beam():
    # beam passes 10 mm beside the optic, on the side the mount plate sits (behind the mirror)
    m = Part("mirror-1", "mirror", (1500.0, 120.0, 310.0), math.radians(135))  # faces -x,+z
    b = trace("pump", PUMP, WEST, els(m), [])
    assert b.end == "absorbed" and "mount of mirror-1" in b.end_note
    # passing on the reflecting side, clear of the optic, is fine
    m2 = Part("mirror-1", "mirror", (1500.0, 120.0, 285.0), math.radians(135))
    b2 = trace("pump", PUMP, WEST, els(m2), [])
    assert b2.end == "stray" and not b2.hits


def test_post_blocks_a_low_beam():
    m = Part("mirror-1", "mirror", (1500.0, 200.0, 300.0), math.radians(135))  # 80 mm above the beam
    b = trace("pump", PUMP, WEST, els(m), [])
    assert b.end == "absorbed" and "mount of mirror-1" in b.end_note


def test_lens_mount_ring_absorbs():
    lens = Part("sample", "sample", (1300.0, 120.0, 318.0), math.pi)  # beam 18 mm off-axis
    b = trace("pump", PUMP, WEST, els(lens), [])
    assert b.end == "absorbed" and b.end_note == "lens mount"


def test_polarisation_planar_path_kept_and_out_of_plane_turn_rotates_it():
    lens_x = Part("sample", "sample", (1300.0, 120.0, 300.0), math.pi)
    b = trace("pump", PUMP, WEST, els(lens_x), [])
    assert b.pol == pytest.approx(1.0)
    # turn the beam up (-x -> +y), then sideways (+y -> -z): a 90 deg image rotation
    up = Part("periscope-1", "periscope", (2000.0, 220.0, 300.0), math.pi, height_in=120.0)
    # build the out-of-plane turn from two discs directly: lower mirror of the periscope + a mirror
    from sim.optics import Disc
    n2 = V.unit(V.sub((0.0, 0.0, -1.0), (0.0, 1.0, 0.0)))
    discs = [up.elements(0.0)[0], Disc("m", "mirror", (2000.0, 220.0, 300.0), n2, 12.7, 10.0)]
    lens_z = Part("sample", "sample", (2000.0, 220.0, 200.0), math.radians(270))
    b = trace("pump", PUMP, WEST, discs + els(lens_z), [])
    assert b.at_sample
    assert b.pol == pytest.approx(0.0, abs=1e-9)
