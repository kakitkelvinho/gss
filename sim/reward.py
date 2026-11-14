"""Reward: eta = T_p T_q O exp(-(dt/tau_c)^2) from true state;
R = eta (1 - alpha (C - C_min)/(C_cap - C_min) - beta t_lab/t_budget)."""

from __future__ import annotations

from sim import catalogue as cat
from sim import constants as K

# Cheapest design that can physically reach overlap: cheapest delay stage + the correct-cut BBO +
# 2 mirrors. Two turns are the minimum (e.g. both beams turned once into a lens facing -z, or the
# pump turned 180 deg while the probe goes straight); heights can be matched with pitch knobs or a
# vertical offset at the retroreflector, so no periscope is needed. Blind playthroughs found both.
N_MIN_MIRRORS = 2


def c_min() -> float:
    stage = min(p["price"] for p in cat.PARTS.values() if p["slot"] == "delay_stage")
    bbo = cat.PARTS["BBO-SFG-1300"]["price"]
    mirror = cat.PARTS["MIR-1"]["price"]
    return float(stage + bbo + N_MIN_MIRRORS * mirror)


C_MIN = c_min()


def reward(eta: float, cost: float, time_frac: float = 0.0) -> float:
    pen = K.ALPHA * max(0.0, cost - C_MIN) / (K.SPEND_CAP - C_MIN) + K.BETA * min(1.0, max(0.0, time_frac))
    return max(0.0, min(1.0, eta * (1.0 - pen)))


def design_viable(bought: dict[str, int]) -> bool:
    has_stage = any(cat.PARTS[p]["slot"] == "delay_stage" and n > 0 for p, n in bought.items())
    optics = bought.get("MIR-1", 0) + 2 * bought.get("PER-1", 0)
    return has_stage and bought.get("BBO-SFG-1300", 0) > 0 and optics >= N_MIN_MIRRORS
