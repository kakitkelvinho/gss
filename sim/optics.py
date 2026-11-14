"""Beam-centre-line tracer (Q33'/Q35).

Each beam is a single ray: origin, unit direction, accumulated optical path length (OPL, mm) and
transmission T (clipping only). It travels straight until it meets an element:

* Mirror disc (1"): reflects off its ACTUAL normal (yaw by eye + placement error + mount error +
  knobs). Clipping rolls off with erfc from 10 mm to the 12.7 mm edge; beyond the edge the beam
  misses the mirror and carries on. Hitting the back of a mirror absorbs the beam.
* Periscope: two such discs (the top one has the knobs).
* Delay stage: hollow retroreflector. Entrance disc R = 19.05 mm, 40 mm in front of the apex A.
  Output = point reflection through the apex, direction -d. Bookkeeping: the output ray starts
  at Q' = 2A - Q with the OPL it had at the entrance point Q. Moving the apex by s along the rail
  therefore adds 2s of path, and the true exit point on the entrance plane is 80 mm further on.
* Sample lens (thin lens, f = 100 mm, sample at f + delta_z): focal-plane spot
  r = f*theta + delta_z*theta - delta_z*rho/f, with theta the ray angle to the lens axis and rho
  the hit point on the lens. OPL to the focus = OPL_H - (H - L).d + f + delta_z (equal-path
  wavefront through the lens centre). The beam ends there.
* Laser housings are absorbing boxes. Leaving the table volume, or hitting its surface, is stray.

Yaw is measured in the XZ table plane from +x toward +z; +y is height.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from sim import constants as K
from sim import vec as V
from sim.vec import Vec

EPS = 1e-6
MAX_BOUNCES = 40
TABLE_TOP = 600.0  # a beam going above this height has left the optics volume


def clip_transmission(r: float, r0: float, r_edge: float) -> float:
    """1 inside r0, erfc roll-off to ~1e-4 at the edge."""
    if r <= r0:
        return 1.0
    mid = 0.5 * (r0 + r_edge)
    s = (r_edge - r0) / 5.4
    return 0.5 * math.erfc((r - mid) / s)


def dir_from_angles(yaw: float, elev: float) -> Vec:
    return (math.cos(yaw) * math.cos(elev), math.sin(elev), math.sin(yaw) * math.cos(elev))


# ----------------------------------------------------------------------------------------------
# Parts (true state)


@dataclass
class Part:
    id: str
    kind: str  # "mirror" | "periscope" | "stage" | "sample"
    pos: Vec  # true reference position (x, height, z)
    yaw: float  # true base yaw, rad (by eye + placement error)
    knob_yaw: float = 0.0  # rad
    knob_pitch: float = 0.0  # rad
    mount_err: tuple[float, float] = (0.0, 0.0)
    height_in: float | None = None  # periscope input height (true)
    stage_pos: float = 0.0  # stage: true position along the rail, mm
    travel: float = 25.0

    # ------------------------------------------------------------------
    def elements(self, defocus: float) -> list["Element"]:
        x, y, z = self.pos
        if self.kind == "mirror":
            n = dir_from_angles(self.yaw + self.knob_yaw + self.mount_err[0],
                                self.knob_pitch + self.mount_err[1])
            return [Disc(self.id, "mirror", self.pos, n, K.MIRROR_R, K.CLIP_START),
                    MountBody(self.id, self.pos, n, post=True)]
        if self.kind == "periscope":
            a = V.yaw_dir(self.yaw)
            up = 1.0 if y > self.height_in else -1.0
            lower_c = (x, self.height_in, z)
            # lower mirror: normal horizontal part along -a, 45 deg toward the travel (up/down)
            n1 = dir_from_angles(self.yaw + math.pi, up * math.pi / 4)
            # top mirror: horizontal part along +a, 45 deg away from the vertical travel
            n2 = dir_from_angles(self.yaw + self.knob_yaw + self.mount_err[0],
                                 -up * math.pi / 4 + self.knob_pitch + self.mount_err[1])
            return [Disc(self.id, "lower", lower_c, n1, K.MIRROR_R, K.CLIP_START),
                    Disc(self.id, "upper", self.pos, n2, K.MIRROR_R, K.CLIP_START),
                    MountBody(self.id, lower_c, n1, post=False), MountBody(self.id, self.pos, n2, post=False)]
        if self.kind == "stage":
            u = V.yaw_dir(self.yaw)
            apex = V.add(self.pos, V.mul(u, K.STAGE_APEX_OFFSET + self.stage_pos))
            return [Retro(self.id, apex, u)]
        if self.kind == "sample":
            u = V.yaw_dir(self.yaw)
            return [Lens(self.id, self.pos, u, defocus)]
        raise ValueError(self.kind)


# ----------------------------------------------------------------------------------------------
# Elements


@dataclass
class Hit:
    t: float
    point: Vec
    elem: "Element"


@dataclass
class Disc:
    part_id: str
    role: str  # "mirror" | "lower" | "upper"
    center: Vec
    normal: Vec
    radius: float
    clip_start: float

    def intersect(self, p: Vec, d: Vec) -> Hit | None:
        den = V.dot(d, self.normal)
        if abs(den) < 1e-12:
            return None
        t = V.dot(V.sub(self.center, p), self.normal) / den
        if t <= EPS:
            return None
        h = V.add(p, V.mul(d, t))
        if V.norm(V.sub(h, self.center)) > self.radius:
            return None
        return Hit(t, h, self)


@dataclass
class Retro:
    part_id: str
    apex: Vec
    u: Vec  # rail direction = direction light travels into the retro
    role: str = "retro"

    @property
    def center(self) -> Vec:
        return V.sub(self.apex, V.mul(self.u, K.RETRO_FRONT))

    def intersect(self, p: Vec, d: Vec) -> Hit | None:
        n = self.u
        den = V.dot(d, n)
        if abs(den) < 1e-12:
            return None
        c = self.center
        t = V.dot(V.sub(c, p), n) / den
        if t <= EPS:
            return None
        h = V.add(p, V.mul(d, t))
        if V.norm(V.sub(h, c)) > K.RETRO_R:
            return None
        return Hit(t, h, self)


@dataclass
class Lens:
    part_id: str
    center: Vec
    u: Vec  # lens axis = direction light travels through the lens
    defocus: float
    role: str = "lens"

    def intersect(self, p: Vec, d: Vec) -> Hit | None:
        den = V.dot(d, self.u)
        if abs(den) < 1e-12:
            return None
        t = V.dot(V.sub(self.center, p), self.u) / den
        if t <= EPS:
            return None
        h = V.add(p, V.mul(d, t))
        if V.norm(V.sub(h, self.center)) > K.LENS_MOUNT_R:
            return None
        return Hit(t, h, self)


@dataclass
class MountBody:
    """Mount plate behind a mirror (oriented box) plus, optionally, its post (vertical cylinder).
    Absorbs any beam that hits it."""
    part_id: str
    center: Vec  # optic centre
    normal: Vec  # optic normal (reflecting side)
    post: bool
    role: str = "mount"

    def intersect(self, p: Vec, d: Vec) -> Hit | None:
        best = None
        n = self.normal
        es = V.unit(V.cross(V.Y, n)) if abs(n[1]) < 0.999 else (1.0, 0.0, 0.0)
        ev = V.cross(n, es)
        rel = V.sub(p, self.center)
        lo, hi = -math.inf, math.inf
        for axis, (a, b) in ((n, (-K.MOUNT_DEPTH[1], -K.MOUNT_DEPTH[0])), (es, (-K.MOUNT_HALF, K.MOUNT_HALF)),
                             (ev, (-K.MOUNT_HALF, K.MOUNT_HALF))):
            o, v = V.dot(rel, axis), V.dot(d, axis)
            if abs(v) < 1e-15:
                if o < a or o > b:
                    lo, hi = 1.0, 0.0
                    break
                continue
            t1, t2 = (a - o) / v, (b - o) / v
            if t1 > t2:
                t1, t2 = t2, t1
            lo, hi = max(lo, t1), min(hi, t2)
        if lo <= hi and lo > EPS:
            best = lo
        if self.post:
            # vertical cylinder below the plate
            nh = V.unit((n[0], 0.0, n[2])) if math.hypot(n[0], n[2]) > 1e-9 else (1.0, 0.0, 0.0)
            cx, cz = self.center[0] - K.POST_BEHIND * nh[0], self.center[2] - K.POST_BEHIND * nh[2]
            top = self.center[1] - K.MOUNT_HALF
            ox, oz = p[0] - cx, p[2] - cz
            A = d[0] ** 2 + d[2] ** 2
            if A > 1e-15:
                B = 2 * (ox * d[0] + oz * d[2])
                C = ox * ox + oz * oz - K.POST_R ** 2
                disc = B * B - 4 * A * C
                if disc >= 0:
                    for t in sorted(((-B - math.sqrt(disc)) / (2 * A), (-B + math.sqrt(disc)) / (2 * A))):
                        y = p[1] + t * d[1]
                        if t > EPS and 0.0 <= y <= top:
                            if best is None or t < best:
                                best = t
                            break
        if best is None:
            return None
        return Hit(best, V.add(p, V.mul(d, best)), self)


def _box_entry(p: Vec, d: Vec, box) -> float | None:
    """Entry t (> EPS) of a ray into an axis-aligned box (x0,x1,y0,y1,z0,z1), or None."""
    lo, hi = -math.inf, math.inf
    bounds = ((box[0], box[1]), (box[2], box[3]), (box[4], box[5]))
    for i in range(3):
        a, b = bounds[i]
        if abs(d[i]) < 1e-15:
            if p[i] < a or p[i] > b:
                return None
            continue
        t1, t2 = (a - p[i]) / d[i], (b - p[i]) / d[i]
        if t1 > t2:
            t1, t2 = t2, t1
        lo, hi = max(lo, t1), min(hi, t2)
    if lo > hi or lo <= EPS:
        return None
    return lo


def _table_exit(p: Vec, d: Vec) -> float:
    ts = []
    for i, (a, b) in enumerate(((0.0, K.TABLE_X), (0.0, TABLE_TOP), (0.0, K.TABLE_Z))):
        if d[i] > 1e-15:
            ts.append((b - p[i]) / d[i])
        elif d[i] < -1e-15:
            ts.append((a - p[i]) / d[i])
    return max(min(ts), 0.0) if ts else 0.0


# ----------------------------------------------------------------------------------------------
# Tracing


@dataclass
class HitRecord:
    part_id: str
    role: str
    offset: Vec  # hit point minus element centre (table coordinates)
    T: float  # transmission of this interaction


@dataclass
class BeamResult:
    arm: str
    segments: list[tuple[Vec, Vec]] = field(default_factory=list)
    hits: list[HitRecord] = field(default_factory=list)
    end: str = "stray"  # "sample" | "absorbed" | "stray"
    end_note: str = ""
    T: float = 1.0
    opl: float = 0.0  # OPL at the end point (focus if end == "sample")
    spot: tuple[float, float] | None = None  # focal-plane (h, v), mm, relative to lens axis
    lens_hit: tuple[float, float] | None = None  # (h, v) on the lens, mm
    path_geom: float = 0.0  # geometric length travelled on the table (tape measure)
    pol: float = 1.0  # cos^2 of the polarisation angle from horizontal at the sample (type-I SFG projection)

    @property
    def at_sample(self) -> bool:
        return self.end == "sample"


def trace(arm: str, origin: Vec, direction: Vec, elements: list, housings: list) -> BeamResult:
    res = BeamResult(arm)
    p, d = origin, V.unit(direction)
    opl = 0.0
    T = 1.0
    skip = None
    E = V.unit(V.cross(V.Y, d)) if abs(d[1]) < 0.999 else (1.0, 0.0, 0.0)  # horizontal polarisation
    for _ in range(MAX_BOUNCES):
        best: Hit | None = None
        for e in elements:
            if e is skip:
                continue
            h = e.intersect(p, d)
            if h is not None and (best is None or h.t < best.t):
                best = h
        t_exit = _table_exit(p, d)
        t_house = None
        for box in housings:
            tb = _box_entry(p, d, box)
            if tb is not None and (t_house is None or tb < t_house):
                t_house = tb
        if best is not None and best.t > t_exit + EPS:
            best = None
        if t_house is not None and t_house > t_exit + EPS:
            t_house = None
        if t_house is not None and (best is None or t_house < best.t):
            q = V.add(p, V.mul(d, t_house))
            res.segments.append((p, q))
            opl += t_house
            res.path_geom += t_house
            res.end, res.end_note = "absorbed", "laser housing"
            break
        if best is None:
            q = V.add(p, V.mul(d, t_exit))
            res.segments.append((p, q))
            opl += t_exit
            res.path_geom += t_exit
            res.end = "stray"
            res.end_note = "hits the table surface" if q[1] <= 1e-6 else "leaves the table"
            break
        q = best.point
        res.segments.append((p, q))
        opl += best.t
        res.path_geom += best.t
        e = best.elem
        skip = None
        if isinstance(e, Disc):
            off = V.sub(q, e.center)
            if V.dot(d, e.normal) > 0:
                res.hits.append(HitRecord(e.part_id, e.role, off, 0.0))
                res.end, res.end_note = "absorbed", f"back of {e.part_id}"
                T = 0.0
                break
            tr = clip_transmission(V.norm(off), e.clip_start, e.radius)
            T *= tr
            res.hits.append(HitRecord(e.part_id, e.role, off, tr))
            p, d = q, V.unit(V.reflect(d, e.normal))
            # perfect-conductor reflection of the field: tangential part flips, normal part kept
            E = V.sub(V.mul(e.normal, 2 * V.dot(E, e.normal)), E)
            E = V.unit(V.sub(E, V.mul(d, V.dot(E, d))))
            skip = e
            continue
        if isinstance(e, MountBody):
            res.hits.append(HitRecord(e.part_id, "mount", V.sub(q, e.center), 0.0))
            res.end, res.end_note = "absorbed", f"mount of {e.part_id}"
            T = 0.0
            break
        if isinstance(e, Retro):
            off = V.sub(q, e.center)
            if V.dot(d, e.u) <= 0:
                res.hits.append(HitRecord(e.part_id, e.role, off, 0.0))
                res.end, res.end_note = "absorbed", f"back of {e.part_id}"
                T = 0.0
                break
            tr = clip_transmission(V.norm(off), K.RETRO_CLIP_START, K.RETRO_R)
            T *= tr
            res.hits.append(HitRecord(e.part_id, e.role, off, tr))
            q2 = V.sub(V.mul(e.apex, 2.0), q)
            d2 = V.mul(d, -1.0)
            # The output ray starts at q2 with the OPL it had at q; move to the exit on the
            # entrance plane (80 mm on for normal incidence).
            den = V.dot(d2, V.mul(e.u, -1.0))
            t_out = V.dot(V.sub(e.center, q2), V.mul(e.u, -1.0)) / den
            p = V.add(q2, V.mul(d2, t_out))
            opl += t_out
            res.path_geom += t_out
            d = d2
            skip = e
            continue
        if isinstance(e, Lens):
            off = V.sub(q, e.center)
            if V.dot(d, e.u) <= 0:
                res.hits.append(HitRecord(e.part_id, e.role, off, 0.0))
                res.end, res.end_note = "absorbed", "back of the sample mount"
                T = 0.0
                break
            if V.norm(off) > K.LENS_R:
                res.hits.append(HitRecord(e.part_id, "mount", off, 0.0))
                res.end, res.end_note = "absorbed", "lens mount"
                T = 0.0
                break
            tr = clip_transmission(V.norm(off), K.LENS_CLIP_START, K.LENS_R)
            T *= tr
            res.hits.append(HitRecord(e.part_id, e.role, off, tr))
            e1, e2 = V.perp_basis(e.u)
            du = V.dot(d, e.u)
            th = (V.dot(d, e1) / du, V.dot(d, e2) / du)
            rho = (V.dot(off, e1), V.dot(off, e2))
            f, dz = K.LENS_F, e.defocus
            res.spot = tuple(f * th[i] + dz * th[i] - dz * rho[i] / f for i in range(2))
            res.lens_hit = rho
            res.pol = V.dot(E, e1) ** 2
            opl = opl - V.dot(off, d) + f + dz
            res.path_geom += f + dz
            res.end, res.end_note = "sample", "sample"
            break
    else:
        res.end, res.end_note = "stray", "lost (too many reflections)"
    res.T = T if res.end == "sample" else 0.0
    res.opl = opl
    return res


def closest_approach(res: BeamResult, pt: Vec) -> tuple[float, Vec] | None:
    """(distance, offset = closest point - pt) over all segments of a traced beam."""
    best = None
    for a, b in res.segments:
        ab = V.sub(b, a)
        L2 = V.dot(ab, ab)
        if L2 < 1e-12:
            continue
        s = max(0.0, min(1.0, V.dot(V.sub(pt, a), ab) / L2))
        c = V.add(a, V.mul(ab, s))
        off = V.sub(c, pt)
        dist = V.norm(off)
        if best is None or dist < best[0]:
            best = (dist, off)
    return best
