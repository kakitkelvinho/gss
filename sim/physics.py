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


def spatial_overlap(pump: BeamResult, probe: BeamResult) -> float:
    """O = (2 w1 w2 / (w1^2 + w2^2)) exp(-2 d^2 / (w1^2 + w2^2)) of the two focal spots (Q9, Q15')."""
    if not (pump.at_sample and probe.at_sample):
        return 0.0
    w1, w2 = K.W0_PUMP, K.W0_PROBE
    d2 = (pump.spot[0] - probe.spot[0]) ** 2 + (pump.spot[1] - probe.spot[1]) ** 2
    s = w1 * w1 + w2 * w2
    return (2 * w1 * w2 / s) * math.exp(-2 * d2 / s)


def delay_fs(pump: BeamResult, probe: BeamResult, opa_path: float) -> float | None:
    """Delta t = t_pump - t_probe at the sample, fs. Both ports are path-matched at the amplifier
    split except for the OPA's internal path, which delays the probe."""
    if not (pump.at_sample and probe.at_sample):
        return None
    return (pump.opl - (probe.opl + opa_path)) / K.C_MM_PER_FS


def temporal_factor(dt_fs: float | None) -> float:
    if dt_fs is None:
        return 0.0
    return math.exp(-((dt_fs / K.TAU_C) ** 2))


def truth(pump: BeamResult, probe: BeamResult, opa_path: float) -> dict:
    O = spatial_overlap(pump, probe)
    dt = delay_fs(pump, probe, opa_path)
    g = temporal_factor(dt)
    return {
        "O": O,
        "dt_fs": dt,
        "T_pump": pump.T,
        "T_probe": probe.T,
        "eta": pump.T * probe.T * O * g,
        "pump_end": pump.end_note,
        "probe_end": probe.end_note,
    }


# ----------------------------------------------------------------------------------------------
# Instruments


def bbo_signal(model: str, pump: BeamResult | None, probe: BeamResult | None, opa_path: float,
               t_int: float, rng: random.Random) -> int:
    """S = A T O exp(-(dt/tau_c)^2) + b_pump T_p + b_probe T_q + N(0, sigma/sqrt(t_int)) (Q16).
    `pump` / `probe` are None when that arm is blocked."""
    p = K.BBO_GOOD if model == "bbo_good" else K.BBO_WRONG
    s = 0.0
    if pump is not None and pump.at_sample:
        s += p["b_pump"] * pump.T
    if probe is not None and probe.at_sample:
        s += p["b_probe"] * probe.T
    if pump is not None and probe is not None:
        O = spatial_overlap(pump, probe)
        if O > 0:
            s += p["A"] * pump.T * probe.T * O * temporal_factor(delay_fs(pump, probe, opa_path))
    s += rng.gauss(0.0, p["sigma"] / math.sqrt(t_int))
    return max(0, int(round(s)))


def photodiode(beams: dict[str, BeamResult | None], opa_path: float, rng: random.Random) -> dict:
    """Arrival time of each unblocked beam reaching the sample on the 1 GHz scope."""
    out = {}
    for arm, b in beams.items():
        if b is None or not b.at_sample or b.T < 0.01:
            continue
        opl = b.opl + (opa_path if arm == "probe" else 0.0)
        t = opl / C_MM_PER_PS - SCOPE_TRIGGER_PS + rng.gauss(0.0, K.SCOPE_JITTER_PS)
        out[f"{arm}_arrival_ps"] = round(t / K.SCOPE_QUANT_PS) * K.SCOPE_QUANT_PS
    return out


def camera_sample(beams: dict[str, BeamResult | None], rng: random.Random) -> list[dict]:
    spots = []
    for arm, b in beams.items():
        if b is None or not b.at_sample or b.T < 0.01:
            continue
        h, v = b.spot
        if abs(h) > K.CAM_HALF_FOV or abs(v) > K.CAM_HALF_FOV:
            continue
        w0 = K.W0_PUMP if arm == "pump" else K.W0_PROBE

        def px(val):
            q = val / K.CAM_PIXEL + rng.gauss(0.0, K.CAM_NOISE_PX)
            return round(round(q, 1) * K.CAM_PIXEL * 1000.0, 2)

        spots.append({"beam": arm, "h_um": px(h), "v_um": px(v),
                      "radius_um": round(w0 * 1000.0 * (1 + rng.gauss(0.0, 0.03)), 1)})
    return spots


def camera_lens(beams: dict[str, BeamResult | None], rng: random.Random) -> list[dict]:
    spots = []
    for arm, b in beams.items():
        if b is None or not b.at_sample or b.T < 0.01:
            continue
        h, v = b.lens_hit
        spots.append({"beam": arm, "h_mm": round(h + rng.gauss(0.0, 0.03), 2),
                      "v_mm": round(v + rng.gauss(0.0, 0.03), 2)})
    return spots
