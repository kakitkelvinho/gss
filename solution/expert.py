"""Scripted expert (reference run). Standalone: driven only by a `call(tool, **args) -> dict` function,
so the same code runs in-process (`sim.Episode`) and over MCP (step 3).

Every per-seed fact comes from manuals and measurements (tool outputs), never from the sim's state.
Layout geometry (mm; x along the table, z across, height = y; yaw from +x toward +z):

  probe: port -> periscope (2050, z_o) raises/lowers to h_p -> M_p1 (1700, z_o) -> M_p2 (1700, 592)
         -> lens at (1300, 600, h_p), hitting it at z = 592
  pump:  port -> delay stage (yaw 180, apex line z_p + 15) -> returns +x at z_p + 30
         -> M_q1 (1500, z_p + 30) -> M_q2 (1500, 608) -> lens, hitting it at z = 608
  The probe passes M_q2 on its reflecting side, clear of the mount plate behind it.
  The stage is placed so time zero sits near mid-travel:
  apex A_x = (4528 - z_p - probe_total) / 2, reference point P_x = A_x + 90 + x_mid.
"""

from __future__ import annotations

import math
import re
import statistics
from typing import Callable

LENS = (1300.0, 600.0)
PUMP_LENS_Z, PROBE_LENS_Z = 608.0, 592.0
X_PERI, X_P, X_Q = 2050.0, 1700.0, 1500.0
STAGE_OFF = 15.0
TAU_STAGE_MM = 0.0105  # 1/e half-width of the cross-correlation in stage travel (~70 fs)


class EpisodeOver(Exception):
    pass


class Expert:
    def __init__(self, call: Callable[..., dict], verbose: bool = False):
        self._call = call
        self.verbose = verbose
        self.notes: list[str] = []

    # -- plumbing ---------------------------------------------------------------------------
    def c(self, tool, **args):
        r = self._call(tool, **args)
        if self.verbose:
            short = {k: v for k, v in r.items() if k != "points"}
            print(f"{tool} {args} -> {short}")
        if r.get("error") == "episode over" or "auto-submitted" in str(r.get("error", "")):
            raise EpisodeOver(r["error"])
        return r

    def note(self, s):
        self.notes.append(s)
        if self.verbose:
            print("#", s)

    # -- facts from the manuals ----------------------------------------------------------------
    def read_facts(self):
        t = self.c("read_manual", device="table")["manual"]
        o = self.c("read_manual", device="opa")["manual"]
        self.c("read_manual", device="delay_stage")
        self.c("read_manual", device="sample_mount")
        ports = {}
        for arm, key in (("pump", "Pump output port"), ("probe", "Probe output port")):
            m = re.search(key + r"[^:]*:\s*x=([\d.]+),\s*z=([\d.]+),\s*height=([\d.]+)", t)
            ports[arm] = tuple(float(v) for v in m.groups())
        opa_internal = float(re.search(r"this unit:\s*([\d.]+)\s*mm", o).group(1))
        s_pump = float(re.search(r"pump port \(([\d.]+) mm of path from the split\)", t).group(1))
        s_opa = float(re.search(r"OPA\s+input \(([\d.]+) mm of path from the split\)", t).group(1))
        # extra path the probe has before its port, relative to the pump
        self.L_opa = s_opa + opa_internal - s_pump
        _, self.z_p, self.h_p = ports["pump"]
        _, self.z_o, self.h_o = ports["probe"]
        self.port_x = ports["pump"][0]
        self.note(f"ports pump z={self.z_p} h={self.h_p}, probe z={self.z_o} h={self.h_o}; L_opa={self.L_opa}")

    # -- small helpers -----------------------------------------------------------------------
    def knob(self, part, axis, mrad):
        if abs(mrad) < 0.005:
            return
        self.c("knob", part=part, axis=axis, delta_mrad=round(mrad, 4))

    def ir_point(self, arm, x, z, h, along):
        r = self.c("ir_card", x=x, z=z, height=h)
        for b in r["beams"]:
            if b["beam"] == arm:
                return (b["dz_mm"], b["dheight_mm"]) if along == "x" else (b["dx_mm"], b["dheight_mm"])
        return None

    def ir_part(self, arm, part):
        r = self.c("ir_card", part=part)
        for b in r["beams"]:
            if b["beam"] == arm:
                return (b["dx_mm"], b["dz_mm"], b["dheight_mm"])
        return None

    @staticmethod
    def _solve(J, e):
        det = J[0][0] * J[1][1] - J[0][1] * J[1][0]
        if abs(det) < 1e-12:
            return (0.0, 0.0)
        return ((-e[0] * J[1][1] + e[1] * J[0][1]) / det, (-e[1] * J[0][0] + e[0] * J[1][0]) / det)

    def steer(self, part, read, tol, dk, max_iter=6, J=None):
        """Drive the 2-vector read() to zero with the mirror's yaw/pitch knobs (finite-difference
        Jacobian, then Newton steps). Returns (ok, J)."""
        e = read()
        if e is None:
            return False, J
        if math.hypot(*e) < tol:
            return True, J
        if J is None:
            self.knob(part, "yaw", dk)
            e1 = read()
            self.knob(part, "pitch", dk)
            e2 = read()
            if e1 is None or e2 is None:
                return False, None
            J = [[(e1[0] - e[0]) / dk, (e2[0] - e1[0]) / dk], [(e1[1] - e[1]) / dk, (e2[1] - e1[1]) / dk]]
            e = e2
        for _ in range(max_iter):
            if math.hypot(*e) < tol:
                return True, J
            d = self._solve(J, e)
            d = tuple(max(-20.0, min(20.0, v)) for v in d)
            self.knob(part, "yaw", d[0])
            self.knob(part, "pitch", d[1])
            e = read()
            if e is None:
                return False, J
        return math.hypot(*e) < tol, J

    def aim_at_point(self, part, arm, src, tgt, along, tol=0.5):
        """Steer `part` so the beam leaving it passes through point tgt (x, z, h)."""
        L = math.dist((src[0], src[1]), (tgt[0], tgt[1]))
        for frac in (1.0, 0.5, 0.25):
            p = tuple(src[i] + frac * (tgt[i] - src[i]) for i in range(3))
            if self.ir_point(arm, *p, along) is not None:
                break
        else:
            raise RuntimeError(f"lost the {arm} beam after {part}")
        if frac < 1.0:
            self.note(f"{part}: beam not on the card at the target, aligning at {frac}x first")
            self.steer(part, lambda: self.ir_point(arm, *p, along), 1.0, 3000.0 / (L * frac))
        ok, _ = self.steer(part, lambda: self.ir_point(arm, *tgt, along), tol, 3000.0 / L)
        if not ok:
            self.note(f"{part}: did not converge to {tol} mm")

    # -- camera overlap ----------------------------------------------------------------------
    def find_probe_spot(self):
        """The camera doesn't label beams: block the pump to see where the probe focuses. Only the
        pump is steered afterwards, so the probe spot stays put."""
        self.c("block", arm="pump")
        spots = self.c("view_camera", plane="sample")["spots"]
        self.c("unblock", arm="pump")
        self.probe_spot = (spots[0]["h_um"], spots[0]["v_um"]) if spots else None

    def cam_diff(self, frames=2):
        acc = []
        for _ in range(frames):
            spots = self.c("view_camera", plane="sample")["spots"]
            if len(spots) < 2 or self.probe_spot is None:
                return None
            pts = [(s["h_um"], s["v_um"]) for s in spots[:2]]
            if math.dist(*pts) < 5.0:
                # on top of each other: which is which is ambiguous and doesn't matter
                acc.append((0.0, 0.0))
                continue
            pts.sort(key=lambda p: math.dist(p, self.probe_spot))
            probe, pump = pts
            acc.append((pump[0] - probe[0], pump[1] - probe[1]))
        return (statistics.fmean(a[0] for a in acc), statistics.fmean(a[1] for a in acc))

    # -- the procedure -----------------------------------------------------------------------
    def run(self, stop_early: bool = False):
        try:
            self._run(stop_early)
        except EpisodeOver as e:
            self.note(f"episode over: {e}")
            return
        self.c("submit")

    def _run(self, stop_early):
        self.read_facts()
        zp, hp, zo, ho = self.z_p, self.h_p, self.z_o, self.h_o
        self.c("buy", items={"DL-C25": 1, "BBO-T236": 1, "MIR-1": 4, "PER-1": 1})
        travel, x_mid = 25.0, 12.5

        # Probe arm, in beam order
        self.c("place", part="sample", x=LENS[0], z=LENS[1], height=hp, yaw_deg=180.0)
        self.c("unblock", arm="probe")
        self.c("place", part="periscope-1", x=X_PERI, z=zo, height=hp, yaw_deg=180.0, height_in=ho)
        self.aim_at_point("periscope-1", "probe", (X_PERI, zo, hp), (X_P, zo, hp), "x")
        yaw_p1 = -45.0 if PROBE_LENS_Z < zo else 45.0
        self.c("place", part="mirror-1", x=X_P, z=zo, height=hp, yaw_deg=yaw_p1)
        self.aim_at_point("mirror-1", "probe", (X_P, zo, hp), (X_P, PROBE_LENS_Z, hp), "z")
        self.c("place", part="mirror-2", x=X_P, z=PROBE_LENS_Z, height=hp, yaw_deg=135.0)
        self.aim_at_point("mirror-2", "probe", (X_P, PROBE_LENS_Z, hp), (LENS[0], PROBE_LENS_Z, hp), "x")

        # Pump arm: stage placed so time zero is near mid-travel (the stage itself stays at 0)
        probe_total = self.port_x - X_PERI + abs(hp - ho) + (X_PERI - X_P) + abs(zo - PROBE_LENS_Z) \
            + (X_P - LENS[0]) + self.L_opa
        # pump path to the lens = (port - entrance) + 80 inside the retro + (M_q1 - entrance)
        #   + (M_q2 - M_q1 in z) + (M_q2 - lens) = 3750 - 2 A_x + (PUMP_LENS_Z - 2 * 12 - z_p) + 200
        #   (retro entrance face 40 mm before the apex; 80 mm in and out of the retro)
        pump_const = (self.port_x - 40.0) + 80.0 + (X_Q - 40.0) + (X_Q - LENS[0])
        a_x = (pump_const + PUMP_LENS_Z - 2 * STAGE_OFF - zp - probe_total) / 2.0
        p_x = a_x + 90.0 + x_mid
        self.note(f"probe table+OPA path {probe_total:.0f} mm, stage apex {a_x:.0f}, reference x {p_x:.0f}")
        self.c("unblock", arm="pump")
        self.c("place", part="stage", x=p_x, z=zp + STAGE_OFF, height=hp, yaw_deg=180.0)
        ret = self.ir_point("pump", X_Q, zp + 2 * STAGE_OFF, hp, "x")
        z_ret, h_ret = (zp + 2 * STAGE_OFF, hp) if ret is None else (zp + 2 * STAGE_OFF + ret[0], hp + ret[1])
        self.c("place", part="mirror-3", x=X_Q, z=z_ret, height=h_ret, yaw_deg=135.0)
        self.aim_at_point("mirror-3", "pump", (X_Q, z_ret, h_ret), (X_Q, PUMP_LENS_Z, hp), "z")
        self.c("place", part="mirror-4", x=X_Q, z=PUMP_LENS_Z, height=hp, yaw_deg=225.0)
        self.aim_at_point("mirror-4", "pump", (X_Q, PUMP_LENS_Z, hp), (LENS[0], PUMP_LENS_Z, hp), "x")

        # Spatial overlap at the focus: steer the pump (mirror-4) onto the probe
        self.find_probe_spot()
        ok, self.J_cam = self.steer("mirror-4", self.cam_diff, 3.0, 0.3)
        if not ok:
            self.note("camera overlap did not converge")
        if stop_early:
            return

        # Time zero: predict from tape measurements, coarse scan, fine scan
        lp = self.c("measure_path", arm="pump")["path_mm"]
        lq = self.c("measure_path", arm="probe")["path_mm"]
        st = self.c("status")["inventory"]["stage"]["position_mm"]
        x0 = st + (lq + self.L_opa - lp) / 2.0
        self.note(f"predicted time zero at stage {x0:.3f} mm")
        lo, hi = max(0.0, x0 - 6.0), min(travel, x0 + 6.0)
        coarse = self.c("scan", start_mm=round(lo, 4), end_mm=round(hi, 4), step_mm=0.005, t_int=0.4)["points"]
        xs = [p[0] for p in coarse]
        ys = [p[1] for p in coarse]
        base = statistics.median(ys)
        k = [math.exp(-((i * 0.005) / TAU_STAGE_MM) ** 2) for i in range(-6, 7)]
        best_i, best_v = 0, -math.inf
        for i in range(len(ys)):
            v = sum(k[j + 6] * (ys[i + j] - base) for j in range(-6, 7) if 0 <= i + j < len(ys))
            if v > best_v:
                best_i, best_v = i, v
        xc = xs[best_i]
        self.note(f"coarse peak at {xc:.4f} mm")
        lo, hi = max(0.0, xc - 0.04), min(travel, xc + 0.04)
        fine = self.c("scan", start_mm=round(lo, 4), end_mm=round(hi, 4), step_mm=0.001, t_int=2.0)["points"]
        fx = [p[0] for p in fine]
        fy = [p[1] - base for p in fine]
        sm = [statistics.fmean(fy[max(0, i - 2):i + 3]) for i in range(len(fy))]
        imax = max(range(len(sm)), key=lambda i: sm[i])
        sel = [i for i in range(len(fy)) if abs(fx[i] - fx[imax]) <= 0.015 and fy[i] > 0]
        w = sum(fy[i] for i in sel)
        x_peak = sum(fx[i] * fy[i] for i in sel) / w if w > 0 else fx[imax]
        self.note(f"fine peak at {x_peak:.5f} mm")
        self.c("move_stage", position_mm=round(x_peak, 5))
        # Re-check the overlap
        ok, _ = self.steer("mirror-4", self.cam_diff, 3.0, 0.3, max_iter=2, J=self.J_cam)


def run_in_process(seed: int, stop_early: bool = False, verbose: bool = False):
    from sim import Episode

    ep = Episode(seed)
    ex = Expert(lambda tool, **a: ep.call(tool, a), verbose=verbose)
    ex.run(stop_early=stop_early)
    return ep, ex


if __name__ == "__main__":
    import sys

    seeds = [int(s) for s in sys.argv[1:]] or list(range(1, 11))
    for s in seeds:
        ep, ex = run_in_process(s)
        r = ep.result()
        print(s, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
