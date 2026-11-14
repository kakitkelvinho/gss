"""True-state physics (overlap, delay) and the noisy instrument models.

Nothing here returns hidden truth to the agent directly: `Episode` only passes instrument
outputs (noisy, quantised) into tool results. `truth()` is for the verifier and trajectory log.
"""

from __future__ import annotations

import math
import random

from sim import constants as K
from sim.optics import BeamResult

C_MM_PER_PS = K.C_MM_PER_FS * 1000.0
SCOPE_TRIGGER_PS = 9000.0  # arbitrary fixed scope-trigger offset


HC_EV_NM = 1239.84


def photon_ev(lam_nm: float) -> float:
    return HC_EV_NM / lam_nm


def spatial_overlap(a: BeamResult, b: BeamResult) -> float:
    """O = (2 w1 w2 / (w1^2 + w2^2)) exp(-2 d^2 / (w1^2 + w2^2)) of the two focal spots (Q9, Q15')."""
    if not (a.at_sample and b.at_sample):
        return 0.0
    w1, w2 = K.W0_800, K.W0_OPA
    d2 = (a.spot[0] - b.spot[0]) ** 2 + (a.spot[1] - b.spot[1]) ** 2
    s = w1 * w1 + w2 * w2
    return (2 * w1 * w2 / s) * math.exp(-2 * d2 / s)


def delay_fs(b8: BeamResult, bo: BeamResult, opa_path: float) -> float | None:
    """Delta t = t_800 - t_opa at the sample, fs. Both ports are path-matched at the amplifier
    split except for the OPA's internal path, which delays the OPA pulse."""
    if not (b8.at_sample and bo.at_sample):
        return None
    return (b8.opl - (bo.opl + opa_path)) / K.C_MM_PER_FS


def temporal_factor(dt_fs: float | None) -> float:
    if dt_fs is None:
        return 0.0
    return math.exp(-((dt_fs / K.TAU_C) ** 2))


def truth(b8: BeamResult, bo: BeamResult, opa_path: float) -> dict:
    O = spatial_overlap(b8, bo)
    dt = delay_fs(b8, bo, opa_path)
    g = temporal_factor(dt)
    return {
        "O": O,
        "dt_fs": dt,
        "T_800": b8.T,
        "T_opa": bo.T,
        "eta": b8.T * bo.T * O * g,
        "end_800": b8.end_note,
        "end_opa": bo.end_note,
    }


# ----------------------------------------------------------------------------------------------
# Instruments
#
# Nonlinear diagnostics at the sample plane. Each produces a list of emission components
# (wavelength band, mean counts). Optical ones are read by the signal camera through the filter
# holder; electrical ones (photodiodes) are read directly. Wrong choices fail physically: the
# light is not generated, is generated where the camera is blind, is blocked by the filter, or is
# buried under a background (scatter, single-beam signals) and its fluctuations.


def sum_lambda(l1: float, l2: float) -> float:
    return 1.0 / (1.0 / l1 + 1.0 / l2)


def _bbo_pm(cut: tuple[float, float], pair: tuple[float, float]) -> float:
    """Phase matching: 1 for the pair the crystal is cut for, PM_MISMATCH otherwise."""
    return 1.0 if sorted(cut) == sorted(pair) else K.PM_MISMATCH


def components(d: dict, lam_o: float, T8: float, To: float, cross: float) -> list[tuple[str, tuple[float, float], float]]:
    """Mean emission components of diagnostic `d` (a catalogue part) for OPA wavelength lam_o.
    T8/To: transmission of each arm to the sample (0 if blocked); cross = T8 To O g."""
    out: list[tuple[str, tuple[float, float], float]] = []
    mdl = d["model"]
    if mdl == "bbo":
        cut = d["cut"]
        lx = sum_lambda(800.0, lam_o)
        out.append(("cross", (lx, lx), K.CROSS_A * _bbo_pm(cut, (800.0, lam_o)) * cross))
        for lam, T in ((800.0, T8), (lam_o, To)):
            if T > 0:
                pm = _bbo_pm(cut, (lam, lam))
                amp = K.BBO_SHG_MATCHED if pm == 1.0 else K.BBO_SHG_OTHER * pm
                out.append(("single", (lam / 2, lam / 2), amp * T * T))
    elif mdl in ("pl", "tpa_pd"):
        eg = d["eg_ev"]
        band = d.get("band_nm", (0.0, 0.0))
        e8, eo = photon_ev(800.0), photon_ev(lam_o)
        if e8 + eo > eg:
            out.append(("cross", band, K.CROSS_A * cross))
        self_amp = {"800": K.TPA_PD_SELF_800, "opa": K.TPA_PD_SELF_OPA} if mdl == "tpa_pd" else \
            {"800": K.GAN_TPA_SELF, "opa": K.GAN_TPA_SELF}
        for key, e, T in (("800", e8, T8), ("opa", eo, To)):
            if T <= 0:
                continue
            if e > eg:
                out.append(("single", band, K.LINEAR_ABS * T))
            elif 2 * e > eg:
                out.append(("single", band, self_amp[key] * T * T))
    return out


def filter_T(f: dict | None, band: tuple[float, float]) -> float:
    """Average transmission of filter f over an emission band (nm). None = empty holder."""
    if f is None:
        return 1.0
    lo, hi = band
    n = 1 if hi - lo < 1e-9 else 9
    tot = 0.0
    for i in range(n):
        lam = lo if n == 1 else lo + (hi - lo) * i / (n - 1)
        t = f["leak"]
        for a, b, tp in f["pass"]:
            if a <= lam <= b:
                t = tp
                break
        for a, b, tl in f.get("extra_leak", ()):
            if a <= lam <= b:
                t = max(t, tl)
        tot += t
    return tot / n


def cam_qe(band: tuple[float, float], rng_nm: tuple[float, float]) -> float:
    """Signal camera response: flat inside its specified range, zero outside (unspecified)."""
    lo, hi = band
    mid = 0.5 * (lo + hi)
    return 1.0 if rng_nm[0] <= mid <= rng_nm[1] else 0.0


def mean_and_sigma(d: dict, f: dict | None, lam_o: float, T8: float, To: float, cross: float,
                   t_int: float) -> tuple[float, float, float]:
    """(mean counts, noise sigma, cross-term counts) seen by the readout of diagnostic d."""
    comps = components(d, lam_o, T8, To, cross)
    if d["readout"] == "camera":
        gain = lambda band: cam_qe(band, K.CAM_SI_RANGE) * filter_T(f, band)  # noqa: E731
        # scattered fundamentals reach the signal camera too
        for lam, T in ((800.0, T8), (lam_o, To)):
            if T > 0:
                comps.append(("scatter", (lam, lam), K.SCATTER * T))
    else:
        gain = lambda band: 1.0  # noqa: E731
    S = sum(a * gain(b) for _, b, a in comps)
    C = sum(a * gain(b) for tag, b, a in comps if tag == "cross")
    # read-out floor plus source fluctuations (~3%), both averaging down as 1/sqrt(t_int)
    sigma = math.sqrt(K.NOISE_FLOOR ** 2 + (K.SOURCE_FLUCT * S) ** 2) / math.sqrt(t_int)
    return S, sigma, C


def nonlinear_signal(d: dict, f: dict | None, lam_o: float, b8: BeamResult | None, bo: BeamResult | None,
                     opa_path: float, t_int: float, rng: random.Random) -> dict:
    """Reading of a nonlinear diagnostic. b8 / bo are None when that arm is blocked."""
    T8 = b8.T if (b8 is not None and b8.at_sample) else 0.0
    To = bo.T if (bo is not None and bo.at_sample) else 0.0
    cross = 0.0
    if T8 > 0 and To > 0:
        cross = T8 * To * spatial_overlap(b8, bo) * temporal_factor(delay_fs(b8, bo, opa_path))
    S, sigma, _ = mean_and_sigma(d, f, lam_o, T8, To, cross, t_int)
    v = S + rng.gauss(0.0, sigma)
    if d["readout"] == "camera" and S > K.SIG_CAM_SAT:
        return {"counts": K.SIG_CAM_SAT, "saturated": True}
    return {"counts": max(0, int(round(v)))}


def detection_viable(d: dict, f: dict | None, lam_o: float) -> bool:
    """Can this diagnostic + filter show the cross term at all (reference alignment, both arms open,
    t_int = 1 s)? Peak must stand >= 5 sigma above the off-peak level and nothing may saturate."""
    if d["model"] not in ("bbo", "pl", "tpa_pd"):
        return False
    S0, sig0, _ = mean_and_sigma(d, f, lam_o, 1.0, 1.0, 0.0, 1.0)
    S1, _, C = mean_and_sigma(d, f, lam_o, 1.0, 1.0, 1.0, 1.0)
    if d["readout"] == "camera" and S1 > K.SIG_CAM_SAT:
        return False
    return C >= 5.0 * sig0


def sees(range_nm: tuple[float, float], lam: float) -> bool:
    return range_nm[0] <= lam <= range_nm[1]


def photodiode(beams: dict[str, BeamResult | None], lams: dict[str, float], range_nm: tuple[float, float],
               opa_path: float, rng: random.Random) -> dict:
    """Arrival time of each unblocked beam the photodiode is sensitive to, on the 1 GHz scope."""
    out = {}
    for arm, b in beams.items():
        if b is None or not b.at_sample or b.T < 0.01 or not sees(range_nm, lams[arm]):
            continue
        opl = b.opl + (opa_path if arm == "opa" else 0.0)
        t = opl / C_MM_PER_PS - SCOPE_TRIGGER_PS + rng.gauss(0.0, K.SCOPE_JITTER_PS)
        out[f"{arm}_arrival_ps"] = round(t / K.SCOPE_QUANT_PS) * K.SCOPE_QUANT_PS
    if not out:
        out["note"] = "no pulse on the scope"
    return out


def _power(T: float, rng: random.Random) -> float:
    """Fraction of the beam's output power reaching the sample, with ~2% reading noise."""
    return round(max(0.0, T * (1.0 + rng.gauss(0.0, 0.02))), 2)


def camera_sample(beams: dict[str, BeamResult | None], lams: dict[str, float], range_nm: tuple[float, float],
                  rng: random.Random) -> list[dict]:
    spots = []
    for arm, b in beams.items():
        if b is None or not b.at_sample or b.T < 0.01 or not sees(range_nm, lams[arm]):
            continue
        h, v = b.spot
        if abs(h) > K.CAM_HALF_FOV or abs(v) > K.CAM_HALF_FOV:
            continue
        w0 = K.W0_800 if arm == "800nm" else K.W0_OPA

        def px(val):
            q = val / K.CAM_PIXEL + rng.gauss(0.0, K.CAM_NOISE_PX)
            return round(round(q, 1) * K.CAM_PIXEL * 1000.0, 2)

        spots.append({"beam": arm, "h_um": px(h), "v_um": px(v),
                      "radius_um": round(w0 * 1000.0 * (1 + rng.gauss(0.0, 0.03)), 1),
                      "relative_power": _power(b.T, rng)})
    return spots


def camera_lens(beams: dict[str, BeamResult | None], lams: dict[str, float], range_nm: tuple[float, float],
                rng: random.Random) -> list[dict]:
    spots = []
    for arm, b in beams.items():
        if b is None or not b.at_sample or b.T < 0.01 or not sees(range_nm, lams[arm]):
            continue
        h, v = b.lens_hit
        spots.append({"beam": arm, "h_mm": round(h + rng.gauss(0.0, 0.03), 2),
                      "v_mm": round(v + rng.gauss(0.0, 0.03), 2), "relative_power": _power(b.T, rng)})
    return spots
