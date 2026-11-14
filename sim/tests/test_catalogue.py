"""Detection routes: which diagnostic/filter/camera works at which OPA wavelength, and why."""

import pytest

from sim import Episode
from sim import catalogue as cat
from sim import constants as K
from sim import physics as P
from sim import reward as RW
from sim.lab import Lab


def viable(d, f, lam):
    return P.detection_viable(cat.PARTS[d], None if f is None else cat.filter_spec(f), lam)


def test_routes_per_wavelength():
    # 1300 nm: E_800 + E_1300 = 2.50 eV, below GaN's 3.4 eV gap; above GaP's 2.26 eV
    assert viable("GAP-TPA", None, 1300.0)
    assert viable("BBO-T236", "F-BP495", 1300.0)
    assert not viable("GAN-1", "F-BP550", 1300.0)
    assert not viable("BBO-T292", "F-BP495", 1300.0)  # wrong cut
    assert not viable("BBO-T236", None, 1300.0)  # unfiltered scatter saturates the camera
    assert not viable("BBO-T236", "F-SP775", 1300.0)  # 800 nm leaks through the shortpass edge
    # 450 nm: 2 x 1.55 = 3.10 < 3.4 < 1.55 + 2.76 = 4.31 eV
    assert viable("GAN-1", "F-VIS495", 450.0)
    assert not viable("GAN-1", "F-UV", 450.0)  # blocks the yellow band
    assert not viable("GAN-1", None, 450.0)
    assert not viable("BBO-T408", "F-UV", 450.0)  # 288 nm: signal camera is blind
    assert not viable("GAP-TPA", None, 450.0)  # 2.76 eV > 2.26 eV: linear absorption swamps it
    # 600 nm: the GaN band-pass must exclude 600 nm scatter; the broad VIS stack does not
    assert viable("GAN-1", "F-BP550", 600.0)
    assert not viable("GAN-1", "F-VIS495", 600.0)
    assert not viable("BBO-T341", "F-UV", 600.0)  # 343 nm: blind camera


def test_c_min_per_wavelength():
    stage, mirrors = 400, 2 * 150
    assert RW.c_min(1300.0) == stage + mirrors + 250 + 6500  # GaP + VIS-SWIR camera
    assert RW.c_min(600.0) == stage + mirrors + 250
    assert RW.c_min(450.0) == stage + mirrors + 800 + 200  # GaN + 550 nm band-pass


def test_design_viable_needs_camera_at_1300():
    base = {"DL-M25": 1, "MIR-1": 2, "GAP-TPA": 1}
    assert not RW.design_viable(base, 1300.0)
    assert RW.design_viable({**base, "CAM-VSWIR": 1}, 1300.0)
    assert RW.design_viable(base, 600.0)
    assert not RW.design_viable(base, 450.0)


def test_gan_single_beam_calibration_and_contrast_at_450():
    d, f = cat.PARTS["GAN-1"], cat.filter_spec("F-VIS495")
    only_opa, _, _ = P.mean_and_sigma(d, f, 450.0, 0.0, 1.0, 0.0, 1.0)
    only_800, _, _ = P.mean_and_sigma(d, f, 450.0, 1.0, 0.0, 0.0, 1.0)
    off, _, _ = P.mean_and_sigma(d, f, 450.0, 1.0, 1.0, 0.0, 1.0)
    peak, _, _ = P.mean_and_sigma(d, f, 450.0, 1.0, 1.0, 1.0, 1.0)
    assert only_800 < 50  # 800 nm alone cannot reach the gap with two photons
    assert only_opa > 250  # 450 nm alone does (5.5 eV): same yellow band, a filter can't remove it
    assert peak / off == pytest.approx(4.0, rel=0.15)


def test_alignment_camera_range():
    ep = Episode(1)
    assert ep.lab.opa_lambda == 1300.0
    from sim.tests.test_episode import perfect_layout
    ep = perfect_layout(1)
    assert len(ep.call("view_camera", {"plane": "sample"})["spots"]) == 1  # Si camera can't see 1300 nm
    ep.call("block", {"arm": "800nm"})
    assert ep.call("view_camera", {"plane": "sample"})["spots"] == []
    ep.call("buy", {"items": ["CAM-VSWIR"]})
    assert len(ep.call("view_camera", {"plane": "sample"})["spots"]) == 1
    ep.call("unblock", {"arm": "800nm"})
    spots = ep.call("view_camera", {"plane": "sample"})["spots"]
    assert len(spots) == 2 and all("beam" not in s for s in spots)


def test_filter_install_and_saturation():
    from sim.tests.test_episode import perfect_layout
    ep = perfect_layout(2)  # 450 nm
    assert ep.lab.opa_lambda == 450.0
    ep.call("buy", {"items": ["GAN-1"]})
    r = ep.call("read_signal", {"t_int": 1.0})
    assert r["counts"] == K.SIG_CAM_SAT and r["saturated"] and r["filter"] is None
    ep.call("buy", {"items": ["F-VIS495"]})
    r = ep.call("read_signal", {"t_int": 1.0})
    assert "saturated" not in r and r["counts"] < 1000
    assert ep.call("uninstall", {"what": "filter"})["outcome"] == "filter holder empty"
    assert ep.call("install", {"part_id": "F-VIS495"})["outcome"].startswith("F-VIS495")


def test_opa_route_sets_internal_path():
    for s in range(1, 30):
        lab = Lab(s)
        lo, hi = (1500, 1700) if lab.opa_lambda > 1000 else (2080, 2280)
        assert lo <= lab.opa_path <= hi
    assert {Lab(s).opa_lambda for s in range(1, 30)} == set(K.OPA_LAMBDAS_NM)


def test_photodiode_spectral_range():
    from sim.tests.test_episode import perfect_layout
    ep = perfect_layout(1)  # 1300 nm
    ep.call("buy", {"items": ["PD-SI"]})
    r = ep.call("read_signal", {"t_int": 1.0})
    assert "800nm_arrival_ps" in r and "opa_arrival_ps" not in r
    ep.call("buy", {"items": ["PD-FAST"]})
    r = ep.call("read_signal", {"t_int": 1.0})
    assert "800nm_arrival_ps" in r and "opa_arrival_ps" in r
