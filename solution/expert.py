"""Scripted expert (reference run). Standalone: driven only by a `call(tool, **args) -> dict` function,
so the same code runs in-process (`sim.Episode`) and over MCP (step 3).

Every per-seed fact comes from manuals and measurements (tool outputs), never from the sim's state.
Layout geometry (mm; x along the table, z across, height = y; yaw from +x toward +z):

Level 1:
  opa:   port -> periscope (2050, z_o) raises/lowers to h_p -> M_p1 (1700, z_o) -> M_p2 (1700, 592)
         -> lens at (1300, 600, h_p), hitting it at z = 592
  800nm: port -> delay stage (yaw 180, apex line z_p + 15) -> returns +x at z_p + 30
         -> M_q1 (1500, z_p + 30) -> M_q2 (1500, 608) -> lens, hitting it at z = 608
  The OPA beam passes M_q2 on its reflecting side, clear of the mount plate behind it.
  The stage is placed so time zero sits near mid-travel.
Level 2 (90 deg crossing): see layout_l2.
"""

from __future__ import annotations

import math
import re
import statistics
from typing import Callable

LENS = (1300.0, 600.0)
P800_LENS_Z, OPA_LENS_Z = 608.0, 592.0
X_PERI, X_P, X_Q = 2050.0, 1700.0, 1500.0
STAGE_OFF = 15.0


class EpisodeOver(Exception):
    pass


class Expert:
    def __init__(self, call: Callable[..., dict], verbose: bool = False, manual_l2: bool = True,
                 tape: bool = False):
        self.manual_l2, self.tape = manual_l2, tape
        self.cstep_frac, self.ct_int, self.snr_min = 0.45, 0.4, 8.0
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
        sm = self.c("read_manual", device="sample_mount")["manual"]
        self.level = 2 if "90-degree crossing" in sm else 1
        # 1/e half-width of the cross-correlation: sqrt(100^2 + 60^2) / (2 sqrt(ln 2)) = 70 fs; at 90 deg
        # crossing the arrival-time smear across the ~50 um spot (stretched by 1/cos45) broadens it to
        # sqrt(70^2 + (2 a sin45 / c)^2) with a = sqrt2 * 52 um / 2, i.e. ~186 fs.
        tau_fs = 186.0 if self.level == 2 else 70.0
        self.tau_stage = tau_fs * 2.99792458e-4 / 2.0  # 1/e half-width of the peak in stage travel
        ports = {}
        for arm, key in (("800nm", "800 nm output port"), ("opa", "OPA output port")):
            m = re.search(key + r".*?:\s*x=([\d.]+),\s*z=([\d.]+),\s*height=([\d.]+)", t)
            ports[arm] = tuple(float(v) for v in m.groups())
        self.lam_o = float(re.search(r"OPA output port \(arm 'opa'; OPA, ([\d.]+) nm", t).group(1))
        opa_internal = float(re.search(r"this unit:\s*([\d.]+)\s*mm", o).group(1))
        s_800 = float(re.search(r"800 nm port \(([\d.]+) mm of path from the split\)", t).group(1))
        s_opa = float(re.search(r"OPA\s+input \(([\d.]+) mm of path from the split\)", t).group(1))
        # extra path the OPA pulse has before its port, relative to the 800 nm pulse
        self.L_opa = s_opa + opa_internal - s_800
        _, self.z_p, self.h_p = ports["800nm"]
        _, self.z_o, self.h_o = ports["opa"]
        self.port_x = ports["800nm"][0]
        self.note(f"ports 800nm z={self.z_p} h={self.h_p}, opa z={self.z_o} h={self.h_o}; "
                  f"OPA {self.lam_o:.0f} nm, L_opa={self.L_opa}")

    # -- small helpers -----------------------------------------------------------------------
    def knob(self, part, axis, mrad):
        if abs(mrad) < 0.005:
            return
        self.c("knob", part=part, axis=axis, delta_mrad=round(mrad, 4))

    def ir_point(self, arm, x, z, h, along):
        r = self.c("ir_card", x=x, z=z, height=h)
        for b in r["beams"]:
            if b["beam"] == arm:
                if along == "x":
                    return (b["dz_mm"], b["dheight_mm"])
                if along == "z":
                    return (b["dx_mm"], b["dheight_mm"])
                a = math.radians(along)  # travel yaw in degrees: horizontal offset across the beam
                return (-math.sin(a) * b["dx_mm"] + math.cos(a) * b["dz_mm"], b["dheight_mm"])
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
            e = self.ir_point(arm, *p, along)
            if e is not None and (frac < 1.0 or math.hypot(*e) <= 20.0):
                break
        else:
            raise RuntimeError(f"lost the {arm} beam after {part}")
        if frac < 1.0:
            self.note(f"{part}: beam not on the card at the target, aligning at {frac}x first")
            self.steer(part, lambda: self.ir_point(arm, *p, along), 1.0, 3000.0 / (L * frac))
        ok, _ = self.steer(part, lambda: self.ir_point(arm, *tgt, along), tol, 3000.0 / L)
        if not ok:
            self.note(f"{part}: did not converge to {tol} mm")

    def detection_parts(self) -> dict:
        """Experimentalist's choice from photon energies (E = 1239.84 / lambda): the cross term needs
        E_800 + E_opa above the gap while a single 800 nm beam stays below it (or the background is
        tolerable); scattered laser light must be filtered away from the emission band."""
        e8, eo = 1239.84 / 800.0, 1239.84 / self.lam_o
        parts = {}
        # GaP two-photon photodiode: cheap, no filter. At 90 deg crossing the cross term drops to ~0.37,
        # which at 600 nm no longer stands well above the two single-beam TPA backgrounds.
        if eo < 2.26 and e8 + eo > 2.26 and (self.level == 1 or 2 * eo < 2.26):
            parts["GAP-TPA"] = 1
        else:  # GaN two-photon yellow luminescence through a bandpass inside the yellow band
            parts.update({"GAN-1": 1, "F-BP550": 1})
        if self.lam_o > 1000.0:  # Si alignment camera is blind here
            parts["CAM-VSWIR"] = 1
        self.note(f"photon energies {e8:.2f} + {eo:.2f} eV; buying {sorted(parts)}")
        return parts

    # -- camera overlap ----------------------------------------------------------------------
    def find_opa_spot(self):
        """The camera doesn't label beams: block the 800 nm arm to see where the OPA beam focuses. Only
        the 800 nm beam is steered afterwards, so the OPA spot stays put."""
        self.c("block", arm="800nm")
        spots = self.c("view_camera", plane="sample")["spots"]
        self.c("unblock", arm="800nm")
        self.opa_spot = (spots[0]["h_um"], spots[0]["v_um"]) if spots else None

    def cam_diff(self, frames=2):
        acc = []
        for _ in range(frames):
            spots = self.c("view_camera", plane="sample")["spots"]
            if len(spots) < 2 or self.opa_spot is None:
                return None
            pts = [(s["h_um"], s["v_um"]) for s in spots[:2]]
            if math.dist(*pts) < 5.0:
                # on top of each other: which is which is ambiguous and doesn't matter
                acc.append((0.0, 0.0))
                continue
            pts.sort(key=lambda p: math.dist(p, self.opa_spot))
            opa, b8 = pts
            acc.append((b8[0] - opa[0], b8[1] - opa[1]))
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
        # L2's broadened peak (~28 um of stage, 1/e) needs only ~250 coarse points, so the EUR 400 manual
        # stage is fast enough there; L1's ~10 um peak needs the motorised stage's 0.3 s per point.
        self.stage = "DL-M25" if (self.level == 2 and self.manual_l2) else "DL-C25"
        if self.stage == "DL-M25":  # ~3 s per hand-turned point: fewer, longer points (step ~0.9 of the 1/e half-width)
            self.cstep_frac, self.ct_int, self.snr_min = 0.9, 1.0, 6.0
        self.c("buy", items={self.stage: 1, "MIR-1": 4, "PER-1": 1, **self.detection_parts()})
        travel, x_mid = 25.0, 12.5
        if self.level == 2:
            self.layout_l2(x_mid)
        else:
            self.layout_l1(x_mid)

        # Spatial overlap at the focus: steer the 800 nm beam (mirror-4) onto the OPA beam
        self.find_opa_spot()
        ok, self.J_cam = self.steer("mirror-4", self.cam_diff, 3.0, 0.3)
        if not ok:
            self.note("camera overlap did not converge")
        if stop_early:
            return
        self.find_time_zero(travel)

    def layout_l2(self, x_mid):
        """90 deg crossing. Sample point S = (1200, 600), front normal +x. Lens A (800 nm) takes beams
        travelling at yaw 135, lens B (OPA) at yaw 225; each lens sits 100 mm before S on its axis.
        The last mirror of each arm sits L = 300-480 mm from S on that axis (a long lever arm keeps the
        angle error from placement small), and the mirror before it turns the beam onto that point:
          opa:   port -> periscope (2050, z_o) -> M1 (x_m, z_o) turns +/-z -> M2 on the yaw-225 axis
          800nm: port -> stage (yaw 180) -> back +x at z_p + 24 -> M3 (x_m, z_p + 24) turns +/-z
                 -> M4 on the yaw-135 axis
        """
        zp, hp, zo, ho = self.z_p, self.h_p, self.z_o, self.h_o
        S = (1200.0, 600.0)
        r2 = math.sqrt(2.0)
        lens_a = (S[0] + 100 / r2, S[1] - 100 / r2)
        lens_b = (S[0] + 100 / r2, S[1] + 100 / r2)
        z_ret0 = zp + 2 * STAGE_OFF

        def pick(z_from, sgn):
            # closest to 400 mm with the turning mirror >= 70 mm from the last one
            for L in sorted(range(300, 581, 10), key=lambda v: abs(v - 400)):
                if abs(z_from - (S[1] + sgn * L / r2)) >= 70.0:
                    return float(L)
            return 400.0
        Lo, L8 = pick(zo, 1.0), pick(z_ret0, -1.0)
        xo, zq = S[0] + Lo / r2, S[1] + Lo / r2  # M2
        x8, z8 = S[0] + L8 / r2, S[1] - L8 / r2  # M4
        so = 1.0 if zq > zo else -1.0  # direction M1 sends the OPA beam along z
        s8 = 1.0 if z8 > z_ret0 else -1.0

        self.c("place", part="sample", x=S[0], z=S[1], height=hp, yaw_deg=0.0)
        self.c("unblock", arm="opa")
        self.c("place", part="periscope-1", x=X_PERI, z=zo, height=hp, yaw_deg=180.0, height_in=ho)
        self.aim_at_point("periscope-1", "opa", (X_PERI, zo, hp), (xo, zo, hp), "x")
        self.c("place", part="mirror-1", x=xo, z=zo, height=hp, yaw_deg=math.degrees(math.atan2(so, 1.0)))
        self.aim_at_point("mirror-1", "opa", (xo, zo, hp), (xo, zq, hp), "z")
        self.c("place", part="mirror-2", x=xo, z=zq, height=hp,
               yaw_deg=math.degrees(math.atan2(-1 / r2 - so, -1 / r2)) % 360)
        self.aim_at_point("mirror-2", "opa", (xo, zq, hp), (lens_b[0], lens_b[1], hp), 225.0)

        opa_total = (self.port_x - X_PERI) + abs(hp - ho) + (X_PERI - xo) + abs(zq - zo) + Lo + self.L_opa
        a_x = (self.port_x + x8 + abs(z8 - z_ret0) + L8 - opa_total) / 2.0
        p_x = a_x + 90.0 + x_mid
        self.note(f"OPA arm table+internal path {opa_total:.0f} mm, stage apex {a_x:.0f}, reference x {p_x:.0f}")
        self.c("unblock", arm="800nm")
        self.c("place", part="stage", x=p_x, z=zp + STAGE_OFF, height=hp, yaw_deg=180.0)
        ret = self.ir_point("800nm", x8, z_ret0, hp, "x")
        z_ret, h_ret = (z_ret0, hp) if ret is None else (z_ret0 + ret[0], hp + ret[1])
        self.c("place", part="mirror-3", x=x8, z=z_ret, height=h_ret, yaw_deg=math.degrees(math.atan2(s8, -1.0)) % 360)
        self.aim_at_point("mirror-3", "800nm", (x8, z_ret, h_ret), (x8, z8, hp), "z")
        self.c("place", part="mirror-4", x=x8, z=z8, height=hp,
               yaw_deg=math.degrees(math.atan2(1 / r2 - s8, -1 / r2)) % 360)
        self.aim_at_point("mirror-4", "800nm", (x8, z8, hp), (lens_a[0], lens_a[1], hp), 135.0)

    def layout_l1(self, x_mid):
        zp, hp, zo, ho = self.z_p, self.h_p, self.z_o, self.h_o
        # OPA arm, in beam order
        self.c("place", part="sample", x=LENS[0], z=LENS[1], height=hp, yaw_deg=180.0)
        self.c("unblock", arm="opa")
        self.c("place", part="periscope-1", x=X_PERI, z=zo, height=hp, yaw_deg=180.0, height_in=ho)
        self.aim_at_point("periscope-1", "opa", (X_PERI, zo, hp), (X_P, zo, hp), "x")
        yaw_p1 = -45.0 if OPA_LENS_Z < zo else 45.0
        self.c("place", part="mirror-1", x=X_P, z=zo, height=hp, yaw_deg=yaw_p1)
        self.aim_at_point("mirror-1", "opa", (X_P, zo, hp), (X_P, OPA_LENS_Z, hp), "z")
        self.c("place", part="mirror-2", x=X_P, z=OPA_LENS_Z, height=hp, yaw_deg=135.0)
        self.aim_at_point("mirror-2", "opa", (X_P, OPA_LENS_Z, hp), (LENS[0], OPA_LENS_Z, hp), "x")

        # 800 nm arm: stage placed so time zero is near mid-travel (the stage itself stays at 0)
        opa_total = self.port_x - X_PERI + abs(hp - ho) + (X_PERI - X_P) + abs(zo - OPA_LENS_Z) \
            + (X_P - LENS[0]) + self.L_opa
        # 800 nm path to the lens = (port - entrance) + 80 inside the retro + (M_q1 - entrance)
        #   + (M_q2 - M_q1 in z) + (M_q2 - lens); retro entrance face 40 mm before the apex A_x
        p800_const = (self.port_x - 40.0) + 80.0 + (X_Q - 40.0) + (X_Q - LENS[0])
        a_x = (p800_const + P800_LENS_Z - 2 * STAGE_OFF - zp - opa_total) / 2.0
        p_x = a_x + 90.0 + x_mid
        self.note(f"OPA arm table+internal path {opa_total:.0f} mm, stage apex {a_x:.0f}, reference x {p_x:.0f}")
        self.c("unblock", arm="800nm")
        self.c("place", part="stage", x=p_x, z=zp + STAGE_OFF, height=hp, yaw_deg=180.0)
        ret = self.ir_point("800nm", X_Q, zp + 2 * STAGE_OFF, hp, "x")
        z_ret, h_ret = (zp + 2 * STAGE_OFF, hp) if ret is None else (zp + 2 * STAGE_OFF + ret[0], hp + ret[1])
        self.c("place", part="mirror-3", x=X_Q, z=z_ret, height=h_ret, yaw_deg=135.0)
        self.aim_at_point("mirror-3", "800nm", (X_Q, z_ret, h_ret), (X_Q, P800_LENS_Z, hp), "z")
        self.c("place", part="mirror-4", x=X_Q, z=P800_LENS_Z, height=hp, yaw_deg=225.0)
        self.aim_at_point("mirror-4", "800nm", (X_Q, P800_LENS_Z, hp), (LENS[0], P800_LENS_Z, hp), "x")

    def find_time_zero(self, travel):
        # Time zero: predict, coarse scan, fine scan. The layout put time zero at mid-travel; the tape
        # measure (+/-5 mm per arm, 3 min a reading) adds nothing to that, so it's off by default.
        if self.tape:
            lp = self.c("measure_path", arm="800nm")["path_mm"]
            lq = self.c("measure_path", arm="opa")["path_mm"]
            st = self.c("status")["inventory"]["stage"]["position_mm"]
            x0 = st + (lq + self.L_opa - lp) / 2.0
        else:
            x0 = travel / 2.0
        self.note(f"predicted time zero at stage {x0:.3f} mm")
        # Coarse search outward from the prediction (placement errors can put time zero a few mm of stage
        # away): scan the middle first and stop as soon as a peak stands clearly above the noise. Step
        # 0.45 of the peak's 1/e half-width on the motorised stage, 0.9 on the manual one.
        tau = self.tau_stage
        cstep = round(max(0.005, self.cstep_frac * tau), 3)
        n = max(3, round(1.2 * tau / cstep))
        k = [math.exp(-((i * cstep) / tau) ** 2) for i in range(-n, n + 1)]
        pts: dict[float, float] = {}

        def scan(a, b):
            a, b = max(0.0, a), min(travel, b)
            if b - a >= cstep:
                for x, y in self.c("scan", start_mm=round(a, 4), end_mm=round(b, 4), step_mm=cstep, t_int=self.ct_int)["points"]:
                    pts[round(x, 4)] = y

        def best():
            xs = sorted(pts)
            ys = [pts[x] for x in xs]
            base = statistics.median(ys)
            f = [sum(k[j + n] * (ys[i + j] - base) for j in range(-n, n + 1) if 0 <= i + j < len(ys))
                 for i in range(len(ys))]
            mad = statistics.median(abs(v - statistics.median(f)) for v in f) or 1e-9
            i = max(range(len(f)), key=lambda i: f[i])
            return xs[i], f[i] / (1.4826 * mad), base

        edges = [1.5, 3.5, 6.0]
        scan(x0 - edges[0], x0 + edges[0])
        xc, snr, base = best()
        for inner, outer in zip(edges, edges[1:]):
            if snr >= self.snr_min:
                break
            scan(x0 - outer, x0 - inner)
            scan(x0 + inner, x0 + outer)
            xc, snr, base = best()
        self.note(f"coarse peak at {xc:.4f} mm")
        half = 4 * tau
        step = 0.001 if tau < 0.015 else 0.002
        lo, hi = max(0.0, xc - half), min(travel, xc + half)
        fine = self.c("scan", start_mm=round(lo, 4), end_mm=round(hi, 4), step_mm=step, t_int=2.0)["points"]
        fx = [p[0] for p in fine]
        fy = [p[1] - base for p in fine]
        sm = [statistics.fmean(fy[max(0, i - 2):i + 3]) for i in range(len(fy))]
        imax = max(range(len(sm)), key=lambda i: sm[i])
        sel = [i for i in range(len(fy)) if abs(fx[i] - fx[imax]) <= 1.5 * tau and fy[i] > 0]
        w = sum(fy[i] for i in sel)
        x_peak = sum(fx[i] * fy[i] for i in sel) / w if w > 0 else fx[imax]
        self.note(f"fine peak at {x_peak:.5f} mm")
        # Approach from below, like the scans, so a manual stage's backlash is the same as during the scans
        self.c("move_stage", position_mm=round(max(0.0, x_peak - 0.05), 5))
        self.c("move_stage", position_mm=round(x_peak, 5))
        # Re-check the overlap
        ok, _ = self.steer("mirror-4", self.cam_diff, 3.0, 0.3, max_iter=2, J=self.J_cam)


def run_in_process(seed: int, stop_early: bool = False, verbose: bool = False, level: int = 1):
    from sim import Episode

    ep = Episode(seed, level)
    ex = Expert(lambda tool, **a: ep.call(tool, a), verbose=verbose)
    ex.run(stop_early=stop_early)
    return ep, ex


if __name__ == "__main__":
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root, for `sim`

    seeds = [int(s) for s in sys.argv[1:]] or list(range(1, 11))
    for s in seeds:
        ep, ex = run_in_process(s)
        r = ep.result()
        print(s, {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items()})
