"""Grade final measured physics, then award efficiency only for a working setup."""

from __future__ import annotations

import math
from functools import lru_cache

from sim import catalogue as cat
from sim import constants as K
from sim import physics as P

# Cheapest design that can physically reach overlap: cheapest delay stage + the minimum number of
# mirrors + the cheapest diagnostic (with filter, if it is read by the signal camera) that can show the
# cross term at this OPA wavelength + an alignment camera that sees both beams.
# Mirrors: heights can be matched with pitch knobs or a vertical offset at the retroreflector, so no
# periscope is needed. L1: two turns (e.g. both beams turned once into a lens facing -z, or the 800 nm
# beam turned 180 deg while the OPA beam goes straight); blind playthroughs found both. L2: one turn
# (OPA beam straight into one lens along -x, the 800 nm return from the retroreflector turned once onto
# the other lens axis, +z).
N_MIN_MIRRORS = {1: 2, 2: 1}


def _of_slot(slot):
    return [k for k, p in cat.PARTS.items() if p["slot"] == slot]


def detection_routes(lam_o: float, level: int = 1) -> list[tuple[str, str | None, float]]:
    """All (diagnostic, filter or None, price) combinations that can show the cross term."""
    out = []
    for d in _of_slot("diagnostic"):
        pd = cat.PARTS[d]
        filters = [None] + (_of_slot("filter") if pd.get("readout") == "camera" else [])
        for f in filters:
            if P.detection_viable(pd, None if f is None else cat.filter_spec(f), lam_o, level):
                out.append((d, f, pd["price"] + (cat.PARTS[f]["price"] if f else 0)))
    return sorted(out, key=lambda r: r[2])


def needs_camera(lam_o: float) -> bool:
    return not P.sees(K.CAM_SI_RANGE, lam_o)


@lru_cache(maxsize=None)
def c_min(lam_o: float, level: int = 1) -> float:
    stage = min(cat.PARTS[k]["price"] for k in _of_slot("delay_stage"))
    det = detection_routes(lam_o, level)[0][2]
    cam = min(cat.PARTS[k]["price"] for k in _of_slot("camera")) if needs_camera(lam_o) else 0.0
    return float(stage + det + cam + N_MIN_MIRRORS[level] * cat.PARTS["MIR-1"]["price"])


def score(eta: float, overlap: float, t_800: float, t_opa: float,
          cost: float, time_frac: float, c_min_eur: float,
          dt_fs: float | None = None) -> dict[str, float | bool]:
    """Spatial credit requires two transmitted beams; timing credit requires overlap.

    The 0.3 efficiency bonus is gated by physical success, not purchases or tool use.
    Timing credit also falls with the absolute timing error (TAU_SCORE_FS), spend credit is the
    cheapest workable design's cost over the spend, and lab-time credit falls quadratically.
    """
    spatial = max(0.0, min(1.0, t_800 * t_opa * overlap))
    timed = max(0.0, min(1.0, eta))
    success = timed >= 0.9
    precision = 1.0 if dt_fs is None else math.exp(-(dt_fs / K.TAU_SCORE_FS) ** 2)
    cost_credit = 1.0 if cost <= 0 else max(0.0, min(1.0, c_min_eur / cost))
    time_frac = max(0.0, min(1.0, time_frac))
    spatial_score = 0.2 * spatial
    temporal_score = 0.5 * timed * precision
    efficiency_score = (K.ALPHA * cost_credit + K.BETA * (1.0 - time_frac) ** 2) if success else 0.0
    return {"reward": min(1.0, spatial_score + temporal_score + efficiency_score),
            "spatial_score": spatial_score, "temporal_score": temporal_score,
            "efficiency_score": efficiency_score, "success": success}


def design_viable(bought: dict[str, int], lam_o: float, level: int = 1) -> bool:
    owned = {k for k, n in bought.items() if n > 0}
    has_stage = any(cat.PARTS[p]["slot"] == "delay_stage" for p in owned)
    optics = bought.get("MIR-1", 0) + 2 * bought.get("PER-1", 0)
    det = any(d in owned and (f is None or f in owned) for d, f, _ in detection_routes(lam_o, level))
    cam = not needs_camera(lam_o) or any(cat.PARTS[p]["slot"] == "camera" for p in owned)
    return has_stage and optics >= N_MIN_MIRRORS[level] and det and cam
