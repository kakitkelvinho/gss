"""Reward: eta = T_800 T_opa O exp(-(dt/tau_c)^2) from true state;
R = eta (1 - alpha (C - C_min)/(C_cap - C_min) - beta t_lab/t_budget)."""

from __future__ import annotations

from functools import lru_cache

from sim import catalogue as cat
from sim import constants as K
from sim import physics as P

# Cheapest design that can physically reach overlap: cheapest delay stage + 4 mirrors (a beam can be
# sloped with pitch knobs, so a periscope is not strictly needed) + the cheapest diagnostic (with
# filter, if it is read by the signal camera) that can show the cross term at this OPA wavelength
# + an alignment camera that sees both beams.
N_MIN_MIRRORS = 4


def _of_slot(slot):
    return [k for k, p in cat.PARTS.items() if p["slot"] == slot]


def detection_routes(lam_o: float) -> list[tuple[str, str | None, float]]:
    """All (diagnostic, filter or None, price) combinations that can show the cross term."""
    out = []
    for d in _of_slot("diagnostic"):
        pd = cat.PARTS[d]
        filters = [None] + (_of_slot("filter") if pd.get("readout") == "camera" else [])
        for f in filters:
            if P.detection_viable(pd, None if f is None else cat.filter_spec(f), lam_o):
                out.append((d, f, pd["price"] + (cat.PARTS[f]["price"] if f else 0)))
    return sorted(out, key=lambda r: r[2])


def needs_camera(lam_o: float) -> bool:
    return not P.sees(K.CAM_SI_RANGE, lam_o)


@lru_cache(maxsize=None)
def c_min(lam_o: float) -> float:
    stage = min(cat.PARTS[k]["price"] for k in _of_slot("delay_stage"))
    det = detection_routes(lam_o)[0][2]
    cam = min(cat.PARTS[k]["price"] for k in _of_slot("camera")) if needs_camera(lam_o) else 0.0
    return float(stage + det + cam + N_MIN_MIRRORS * cat.PARTS["MIR-1"]["price"])


def reward(eta: float, cost: float, time_frac: float, c_min_eur: float) -> float:
    pen = K.ALPHA * max(0.0, cost - c_min_eur) / (K.SPEND_CAP - c_min_eur) + K.BETA * min(1.0, max(0.0, time_frac))
    return max(0.0, min(1.0, eta * (1.0 - pen)))


def design_viable(bought: dict[str, int], lam_o: float) -> bool:
    owned = {k for k, n in bought.items() if n > 0}
    has_stage = any(cat.PARTS[p]["slot"] == "delay_stage" for p in owned)
    optics = bought.get("MIR-1", 0) + 2 * bought.get("PER-1", 0)
    det = any(d in owned and (f is None or f in owned) for d, f, _ in detection_routes(lam_o))
    cam = not needs_camera(lam_o) or any(cat.PARTS[p]["slot"] == "camera" for p in owned)
    return has_stage and optics >= N_MIN_MIRRORS and det and cam
