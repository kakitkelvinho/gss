"""Per-seed lab: the fixed facts of the room, drawn from a dedicated "lab" random stream.

Whatever the agent does, the same seed gives the same lab. Placement errors and measurement noise
come from separate streams (see `Episode`), and per-mount tilt errors are keyed by part id.
"""

from __future__ import annotations

import random

from sim import constants as K

PORT_X = 2250.0
VIS_BOX_PATH = 580.0


class Lab:
    def __init__(self, seed: int, level: int = 1):
        self.seed = int(seed)
        self.level = int(level)  # 1: one lens, any crossing angle; 2: 90 deg crossing, a lens per beam
        r = random.Random(f"gss-lab-{self.seed}")
        z_p = r.uniform(200.0, 400.0)
        h_p = r.uniform(90.0, 160.0)
        z_o = r.uniform(800.0, 1000.0)
        # Periscopes need >= 30 mm of height change, so keep the two port heights at least 30 mm apart.
        while True:
            h_o = r.uniform(90.0, 160.0)
            if abs(h_o - h_p) >= 30.0:
                break
        # Round to whole mm: these are stated to the agent in the table manual.
        z_p, h_p, z_o, h_o = (float(round(v)) for v in (z_p, h_p, z_o, h_o))
        self.ports = {
            "800nm": {"pos": (PORT_X, h_p, z_p), "dir": (-1.0, 0.0, 0.0)},
            "opa": {"pos": (PORT_X, h_o, z_o), "dir": (-1.0, 0.0, 0.0)},
        }
        signal_path = float(round(r.uniform(1500.0, 1700.0)))
        # OPA output wavelength: its own stream, so the table layout of a seed doesn't depend on it.
        self.opa_lambda = random.Random(f"gss-lambda-{self.seed}").choice(K.OPA_LAMBDAS_NM)
        # Visible outputs pass through the frequency-mixing extension box: +580 mm internal path.
        self.opa_route = "signal" if self.opa_lambda > 1000 else "visible"
        self.opa_path = signal_path + (0.0 if self.opa_route == "signal" else VIS_BOX_PATH)  # stated in the OPA manual
        self.defocus = r.uniform(-0.5, 0.5)  # hidden: sample sits delta_z behind the lens focal plane
        # Paths inside the laser housing from the amplifier's split to the 800 nm port and to the OPA
        # input (stated in the table manual). Drawn last so the earlier per-seed draws are unchanged.
        self.split_800 = float(round(r.uniform(300.0, 700.0)))
        self.split_opa = float(round(r.uniform(300.0, 700.0)))
        # Housings: absorbing boxes behind each port (x_lo, x_hi, y_lo, y_hi, z_lo, z_hi)
        self.housings = [
            (PORT_X, K.TABLE_X, 0.0, 400.0, p["pos"][2] - 150.0, p["pos"][2] + 150.0)
            for p in self.ports.values()
        ]

    @property
    def opa_extra_path(self) -> float:
        """Extra path the OPA pulse has before its port, relative to the 800 nm pulse before its port (mm)."""
        return self.split_opa + self.opa_path - self.split_800

    def mount_error(self, part_id: str) -> tuple[float, float]:
        """Intrinsic (yaw, pitch) tilt error of a kinematic mount, rad. Fixed per seed and part id."""
        r = random.Random(f"gss-mount-{self.seed}-{part_id}")
        return (r.gauss(0.0, 0.002), r.gauss(0.0, 0.002))
