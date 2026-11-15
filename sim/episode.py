"""One lab episode. `Episode.call(tool, args)` is the ONLY entry point for agent actions.

It validates arguments, walks the person around the table for physical actions, charges lab time,
applies the action,
and logs the true state after every step. The MCP layer forwards calls here and nothing else.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Callable

from sim import catalogue as cat
from sim import constants as K
from sim import physics as P
from sim import reward as RW
from sim import vec as V
from sim.lab import Lab
from sim.optics import Part, closest_approach, trace


class BadArgs(Exception):
    pass


# ----------------------------------------------------------------------------------------------
# Tool specs: the single source of truth for the MCP layer (names, goal-neutral descriptions,
# parameters). Types: num, str, bool, items.

TOOL_SPECS: dict[str, dict] = {
    "status": dict(desc="Your position, lab time, money spent, inventory (with the poses you requested), "
                        "stage position, installed diagnostic and filter, alignment camera and shutter states.", params={}),
    "list_catalogue": dict(desc="List catalogue items, optionally for one slot (delay_stage, diagnostic, filter, "
                                "camera, mounting).",
                           params={"slot": ("str", False)}),
    "get_datasheet": dict(desc="Datasheet of one catalogue item.", params={"part_id": ("str", True)}),
    "read_manual": dict(desc="Read a device manual: table, opa, delay_stage, sample_mount, signal_camera, mirror, "
                             "periscope, photodiode, nonlinear, ir_card.", params={"device": ("str", True)}),
    "buy": dict(desc="Place one buy order (~15 min of lab time at the desk per order). items: list of catalogue part ids (repeat an id to buy several), "
                     "or an object {part_id: quantity}.", params={"items": ("items", True)}),
    "place": dict(desc="Place an inventory part on the table. x, z, height in mm; yaw_deg in degrees "
                       "(see the part's manual for what yaw means). Periscopes also take height_in.",
                  params={"part": ("str", True), "x": ("num", True), "z": ("num", True), "height": ("num", True),
                          "yaw_deg": ("num", True), "height_in": ("num", False)}),
    "rotate": dict(desc="Loosen a placed part's base, turn it by delta_deg and re-tighten.",
                   params={"part": ("str", True), "delta_deg": ("num", True)}),
    "move": dict(desc="Move a placed part to a new x, z (mm), keeping its yaw and height.",
                 params={"part": ("str", True), "x": ("num", True), "z": ("num", True)}),
    "remove": dict(desc="Take a part off the table back into the inventory.", params={"part": ("str", True)}),
    "knob": dict(desc="Turn a kinematic knob (axis 'yaw' or 'pitch') by delta_mrad. watch=true also returns a "
                      "camera frame if the monitor is within reach of view.",
                 params={"part": ("str", True), "axis": ("str", True), "delta_mrad": ("num", True),
                         "watch": ("bool", False)}),
    "ir_card": dict(desc="Look with the IR card: either at a placed part (part=...) or at a point (x, z, height).",
                    params={"part": ("str", False), "x": ("num", False), "z": ("num", False), "height": ("num", False)}),
    "install": dict(desc="Install an owned diagnostic in the sample mount, or an owned filter in the signal "
                         "camera's filter holder.", params={"part_id": ("str", True)}),
    "uninstall": dict(desc="Empty the signal camera's filter holder ('filter') or the sample mount ('diagnostic').",
                      params={"what": ("str", True)}),
    "measure_path": dict(desc="Tape-measure the beam path of one arm ('800nm' or 'opa') from its output port (good to about +/-5 mm).",
                         params={"arm": ("str", True)}),
    "view_camera": dict(desc="Camera frame at the sample mount: plane 'sample' (focal plane) or 'lens'. Each spot gives its position and relative_power.",
                        params={"plane": ("str", True)}),
    "block": dict(desc="Close the shutter of one arm ('800nm' or 'opa').", params={"arm": ("str", True)}),
    "unblock": dict(desc="Open the shutter of one arm ('800nm' or 'opa').", params={"arm": ("str", True)}),
    "move_stage": dict(desc="Move the delay stage to position_mm.", params={"position_mm": ("num", True)}),
    "read_signal": dict(desc="Read the installed diagnostic, integrating for t_int seconds (0.01-10).",
                        params={"t_int": ("num", True)}),
    "scan": dict(desc="Step the delay stage from start_mm to end_mm in steps of step_mm, reading the diagnostic "
                      "for t_int seconds at each point (max 5000 points).",
                 params={"start_mm": ("num", True), "end_mm": ("num", True), "step_mm": ("num", True),
                         "t_int": ("num", True)}),
    "submit": dict(desc="Submit: you are done. Ends the episode.", params={}),
}

FREE_INFO_TOOLS = frozenset({"status", "list_catalogue", "get_datasheet", "read_manual"})

COORD_LIMIT = 1.0e5
KNOB_S = 30.0  # tuned from 60 s (DECISIONS Q32') so the expert fits in 65% of the budget
FOOTPRINT = {"mirror": 25.0, "periscope": 40.0, "sample": 40.0, "stage": 40.0}

# Ring the person walks on (300 mm outside the table edge), parametrised by arc length s.
RX0, RX1 = -K.WALK_OFFSET, K.TABLE_X + K.WALK_OFFSET
RZ0, RZ1 = -K.WALK_OFFSET, K.TABLE_Z + K.WALK_OFFSET
RING_LEN = 2 * (RX1 - RX0) + 2 * (RZ1 - RZ0)
DESK_XZ = (K.DESK[0], K.DESK[2])


def _ring_s(x: float, z: float) -> float:
    if abs(z - RZ0) < 1e-6:
        return x - RX0
    if abs(x - RX1) < 1e-6:
        return (RX1 - RX0) + (z - RZ0)
    if abs(z - RZ1) < 1e-6:
        return (RX1 - RX0) + (RZ1 - RZ0) + (RX1 - x)
    return 2 * (RX1 - RX0) + (RZ1 - RZ0) + (RZ1 - z)


def _ring_dist(a: tuple[float, float], b: tuple[float, float]) -> float:
    d = abs(_ring_s(*a) - _ring_s(*b))
    return min(d, RING_LEN - d)


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


@dataclass
class Plan:
    loc: Any  # None (stay), "desk", or (x, z) table point to stand next to
    cost_s: float
    run: Callable[[], dict]


class Episode:
    def __init__(self, seed: int, level: int = 1):
        if level not in (1, 2):
            raise ValueError("level must be 1 or 2")
        self.seed = int(seed)
        self.level = int(level)
        self.lab = Lab(self.seed, self.level)
        self.rng_place = random.Random(f"gss-place-{self.seed}")
        self.rng_noise = random.Random(f"gss-noise-{self.seed}")
        self.t = 0.0
        self.pos = DESK_XZ
        self.over = False
        self.ended_by: str | None = None
        self.cost = 0.0
        self.bought: dict[str, int] = {}
        # inventory: id -> {"part_id", "kind", "part": Part|None, "req": dict|None}
        self.inv: dict[str, dict] = {"sample": {"part_id": None, "kind": "sample", "part": None, "req": None}}
        self.n_mirror = 0
        self.n_periscope = 0
        self.stage_cmd = 0.0
        self.stage_true = 0.0
        self.stage_last_dir = 0
        self.diag_owned: list[str] = []
        self.diag: str | None = None
        self.filters_owned: list[str] = []
        self.filter: str | None = None
        self.align_cam: str | None = None  # None = the free Si camera
        self.lams = {"800nm": 800.0, "opa": self.lab.opa_lambda}
        self.c_min = RW.c_min(self.lab.opa_lambda, self.level)
        self.shutter_open = {"800nm": False, "opa": False}
        self.tool_calls = 0
        self.malformed = 0
        self.stray_s = 0.0
        self.stray_events = 0
        self._stray_now = False
        self.log: list[dict] = []
        self._cache = None
        self.final: dict | None = None

    # ------------------------------------------------------------------------------------------
    # Public API

    def call(self, tool: str, args: dict | None = None) -> dict:
        if self.over:
            return {"error": "episode over"}
        self.tool_calls += 1
        args = dict(args or {})
        try:
            if not isinstance(tool, str) or tool not in TOOL_SPECS:
                raise BadArgs(f"unknown tool {tool!r}")
            a = self._validate(tool, args)
            plan = getattr(self, f"_t_{tool}")(**a)
        except BadArgs as e:
            self.malformed += 1
            return self._charge_and_respond(tool, args, K.MIN_ACTION_S, None, {"error": str(e)})
        walk_s, new_pos = self._walk(plan.loc)
        total = 0.0 if tool in FREE_INFO_TOOLS else max(K.MIN_ACTION_S, walk_s + plan.cost_s)
        if self.t + total > K.BUDGET_S:
            self._end("timeout")
            res = {"error": "not enough lab time left for this action; the episode is over (auto-submitted)"}
            self._log(tool, args, 0.0, res)
            return res
        self.pos = new_pos
        return self._charge_and_respond(tool, args, total, plan.run, None)

    def result(self) -> dict:
        """Final score and diagnostics. Auto-submits if the episode is still running (verifier)."""
        if not self.over:
            self._end("verifier")
        return dict(self.final)

    def trajectory(self) -> list[dict]:
        return list(self.log)

    # ------------------------------------------------------------------------------------------
    # Core machinery

    def _charge_and_respond(self, tool, args, cost_s, run, res):
        if self._stray_now:
            self.stray_s += cost_s
        self.t += cost_s
        if run is not None:
            res = run()
        if tool == "submit" and not self.over:
            self._end("agent")
        self._update_stray()
        out = dict(res)
        out["lab_time_used_min"] = round(self.t / 60.0, 2)
        out["lab_time_remaining_min"] = round((K.BUDGET_S - self.t) / 60.0, 2)
        out["you_at"] = self._you_at()
        self._log(tool, args, cost_s, out)
        return out

    def _you_at(self):
        if _ring_dist(self.pos, DESK_XZ) < 1.0:
            return "desk"
        return {"x_mm": round(self.pos[0]), "z_mm": round(self.pos[1])}

    def _end(self, by: str):
        self.over = True
        self.ended_by = by
        tr = self._truth()
        dt = tr["dt_fs"]
        xs = [p["part"].pos for p in self.inv.values() if p["part"] is not None]
        area = 0.0
        if len(xs) >= 2:
            area = (max(x[0] for x in xs) - min(x[0] for x in xs)) * (max(x[2] for x in xs) - min(x[2] for x in xs)) / 1e6
        self.final = {
            **RW.score(tr["eta"], tr["O"], tr["T_800"], tr["T_opa"],
                       self.cost, self.t / K.BUDGET_S, self.c_min),
            "eta": tr["eta"],
            "O": tr["O"],
            "abs_dt_fs": None if dt is None else abs(dt),
            "T_800": tr["T_800"],
            "T_opa": tr["T_opa"],
            "opa_lambda_nm": self.lab.opa_lambda,
            "design_viable": RW.design_viable(self.bought, self.lab.opa_lambda, self.level),
            "level": self.level,
            "diagnostics_bought": sorted(k for k in self.bought if cat.PARTS[k]["slot"] in ("diagnostic", "filter", "camera")),
            "cost_eur": self.cost,
            "c_min_eur": self.c_min,
            "lab_time_min": round(self.t / 60.0, 2),
            "lab_time_frac": round(self.t / K.BUDGET_S, 4),
            "tool_calls": self.tool_calls,
            "malformed_calls": self.malformed,
            "stray_events": self.stray_events,
            "stray_time_min": round(self.stray_s / 60.0, 2),
            "parts_placed": len(xs),
            "footprint_m2": round(area, 4),
            "ended_by": by,
            "seed": self.seed,
        }

    def _log(self, tool, args, cost_s, res):
        tr = self._truth()
        small = {k: v for k, v in res.items() if k != "points"}
        if "points" in res:
            small["n_points"] = len(res["points"])
        self.log.append({
            "i": len(self.log), "tool": tool, "args": _jsonable(args), "cost_s": round(cost_s, 3),
            "t_s": round(self.t, 3), "result": small,
            "truth": {k: (round(v, 6) if isinstance(v, float) else v) for k, v in tr.items()},
        })

    def _walk(self, loc):
        if loc is None:
            return 0.0, self.pos
        if loc == "desk":
            target = DESK_XZ
        else:
            tx, tz = loc
            tx = _clamp(tx, RX0, RX1)
            tz = _clamp(tz, RZ0, RZ1)
            cands = []
            if tz <= K.REACH:
                cands.append((tx, RZ0))
            if tz >= K.TABLE_Z - K.REACH:
                cands.append((tx, RZ1))
            if tx <= K.REACH:
                cands.append((RX0, tz))
            if tx >= K.TABLE_X - K.REACH:
                cands.append((RX1, tz))
            if not cands:
                cands.append((tx, RZ0))
            target = min(cands, key=lambda c: _ring_dist(self.pos, c))
        return _ring_dist(self.pos, target) / K.WALK_SPEED, target

    def _invalidate(self):
        self._cache = None

    def _beams(self) -> dict:
        """True traced beams (ignoring shutters)."""
        if self._cache is None:
            els = []
            for item in self.inv.values():
                if item["part"] is not None:
                    els.extend(item["part"].elements(self.lab.defocus))
            self._cache = {arm: trace(arm, port["pos"], port["dir"], els, self.lab.housings)
                           for arm, port in self.lab.ports.items()}
        return self._cache

    def _visible(self) -> dict:
        b = self._beams()
        return {arm: (b[arm] if self.shutter_open[arm] else None) for arm in K.ARMS}

    def _truth(self) -> dict:
        vis = self._visible()
        if vis["800nm"] is None or vis["opa"] is None:
            b = self._beams()
            return {"O": 0.0, "dt_fs": None, "T_800": b["800nm"].T if vis["800nm"] else 0.0,
                    "T_opa": b["opa"].T if vis["opa"] else 0.0, "eta": 0.0,
                    "end_800": "blocked" if vis["800nm"] is None else b["800nm"].end_note,
                    "end_opa": "blocked" if vis["opa"] is None else b["opa"].end_note}
        return P.truth(vis["800nm"], vis["opa"], self.lab.opa_extra_path, self.level)

    def _update_stray(self):
        vis = self._visible()
        now = any(b is not None and b.end == "stray" for b in vis.values())
        if now and not self._stray_now:
            self.stray_events += 1
        self._stray_now = now

    # ------------------------------------------------------------------------------------------
    # Validation

    def _validate(self, tool: str, args: dict) -> dict:
        spec = TOOL_SPECS[tool]["params"]
        unknown = set(args) - set(spec)
        if unknown:
            raise BadArgs(f"unknown argument(s) {sorted(unknown)} for {tool}")
        out = {}
        for name, (typ, req) in spec.items():
            if name not in args or args[name] is None:
                if req:
                    raise BadArgs(f"missing argument {name!r}")
                continue
            v = args[name]
            if typ == "num":
                if isinstance(v, bool) or not isinstance(v, (int, float)):
                    raise BadArgs(f"{name} must be a number")
                v = float(v)
                if not math.isfinite(v) or abs(v) > COORD_LIMIT:
                    raise BadArgs(f"{name} must be a finite number of sensible size")
            elif typ == "str":
                if not isinstance(v, str) or len(v) > 64:
                    raise BadArgs(f"{name} must be a short string")
            elif typ == "bool":
                if not isinstance(v, bool):
                    raise BadArgs(f"{name} must be true or false")
            elif typ == "items":
                v = self._parse_items(v)
            out[name] = v
        return out

    @staticmethod
    def _parse_items(v) -> dict[str, int]:
        order: dict[str, int] = {}
        if isinstance(v, dict):
            for k, q in v.items():
                if not isinstance(k, str) or isinstance(q, bool) or not isinstance(q, int) or q < 0 or q > 100:
                    raise BadArgs("items: {part_id: quantity} with integer quantities 0-100")
                order[k] = order.get(k, 0) + q
        elif isinstance(v, list):
            if len(v) > 100:
                raise BadArgs("items: at most 100 entries")
            for k in v:
                if isinstance(k, dict) and set(k) <= {"part_id", "qty", "quantity"} and "part_id" in k:
                    q = k.get("qty", k.get("quantity", 1))
                    k = k["part_id"]
                else:
                    q = 1
                if not isinstance(k, str) or isinstance(q, bool) or not isinstance(q, int) or q < 0 or q > 100:
                    raise BadArgs("items: list of catalogue part ids")
                order[k] = order.get(k, 0) + q
        else:
            raise BadArgs("items must be a list of part ids or an object {part_id: quantity}")
        for k in order:
            if k not in cat.PARTS:
                raise BadArgs(f"unknown catalogue part {k!r}")
        if sum(order.values()) == 0:
            raise BadArgs("empty order")
        return order

    def _arm(self, arm: str) -> str:
        if arm not in K.ARMS:
            raise BadArgs("arm must be '800nm' or 'opa'")
        return arm

    def _item(self, part: str, placed: bool | None = None) -> dict:
        if part not in self.inv:
            raise BadArgs(f"no part {part!r} in your inventory (see status)")
        return self.inv[part]

    def _stand_at(self, item) -> Any:
        p = item["part"]
        return (p.pos[0], p.pos[2]) if p is not None else "desk"

    # ------------------------------------------------------------------------------------------
    # Footprint checks

    def _footprint(self, kind: str, x: float, z: float, yaw: float, travel: float = 0.0):
        r = FOOTPRINT[kind]
        if kind == "stage":
            u = (math.cos(yaw), math.sin(yaw))
            a = (x - 20 * u[0], z - 20 * u[1])
            b = (x + (K.STAGE_APEX_OFFSET + travel + 20) * u[0], z + (K.STAGE_APEX_OFFSET + travel + 20) * u[1])
            return ("cap", a, b, r)
        return ("cap", (x, z), (x, z), r)

    @staticmethod
    def _seg_dist(p, a, b):
        ab = (b[0] - a[0], b[1] - a[1])
        L2 = ab[0] ** 2 + ab[1] ** 2
        s = 0.0 if L2 < 1e-12 else _clamp(((p[0] - a[0]) * ab[0] + (p[1] - a[1]) * ab[1]) / L2, 0.0, 1.0)
        c = (a[0] + s * ab[0], a[1] + s * ab[1])
        return math.hypot(p[0] - c[0], p[1] - c[1])

    def _cap_dist(self, c1, c2):
        _, a1, b1, _ = c1
        _, a2, b2, _ = c2
        # sample-based segment-segment distance (segments are short; this is plenty accurate)
        ds = []
        for i in range(11):
            s = i / 10
            p = (a1[0] + s * (b1[0] - a1[0]), a1[1] + s * (b1[1] - a1[1]))
            ds.append(self._seg_dist(p, a2, b2))
            q = (a2[0] + s * (b2[0] - a2[0]), a2[1] + s * (b2[1] - a2[1]))
            ds.append(self._seg_dist(q, a1, b1))
        return min(ds)

    def _fits(self, pid: str, kind: str, x: float, z: float, yaw: float, travel: float = 0.0) -> str | None:
        fp = self._footprint(kind, x, z, yaw, travel)
        _, a, b, r = fp
        for pt in (a, b):
            if not (0.0 <= pt[0] <= K.TABLE_X and 0.0 <= pt[1] <= K.TABLE_Z):
                return "the mount doesn't fit there (off the table)"
        for (x0, x1, _, _, z0, z1) in self.lab.housings:
            for i in range(11):
                s = i / 10
                p = (a[0] + s * (b[0] - a[0]), a[1] + s * (b[1] - a[1]))
                cx, cz = _clamp(p[0], x0, x1), _clamp(p[1], z0, z1)
                if math.hypot(p[0] - cx, p[1] - cz) < r:
                    return "the mount doesn't fit there (laser housing in the way)"
        for oid, it in self.inv.items():
            q = it["part"]
            if oid == pid or q is None:
                continue
            fq = self._footprint(it["kind"], q.pos[0], q.pos[2], q.yaw, q.travel)
            if self._cap_dist(fp, fq) < r + fq[3]:
                return f"the mount doesn't fit there ({oid} is in the way)"
        return None

    # ------------------------------------------------------------------------------------------
    # Tools: each returns a Plan (where to stand, time cost, action)

    def _t_status(self):
        def run():
            inv = {}
            for pid, it in self.inv.items():
                d = {"kind": it["kind"], "on_table": it["part"] is not None}
                if it["part_id"]:
                    d["catalogue_id"] = it["part_id"]
                if it["req"]:
                    d["requested_pose"] = it["req"]
                if it["kind"] == "stage":
                    d["position_mm"] = round(self.stage_cmd, 4)
                    d["travel_mm"] = it["part_travel"]
                inv[pid] = d
            return {"inventory": inv, "diagnostic_installed": self.diag, "diagnostics_owned": self.diag_owned,
                    "filter_installed": self.filter, "filters_owned": self.filters_owned,
                    "alignment_camera": self.align_cam or "free Si camera (400-1000 nm)",
                    "shutters_open": dict(self.shutter_open), "spent_eur": self.cost,
                    "spend_cap_eur": K.SPEND_CAP}
        return Plan(None, 0.0, run)

    def _t_list_catalogue(self, slot=None):
        if slot is not None and slot not in cat.SLOTS:
            raise BadArgs(f"unknown slot {slot!r}; slots: {sorted(cat.SLOTS)}")

        def run():
            items = [{"part_id": pid, "slot": p["slot"], "name": p["name"], "price_eur": p["price"]}
                     for pid, p in cat.PARTS.items() if slot is None or p["slot"] == slot]
            return {"slots": cat.SLOTS, "items": items, "free_equipment": cat.FREE_EQUIPMENT}
        return Plan(None, 0.0, run)

    def _t_get_datasheet(self, part_id):
        if part_id not in cat.PARTS:
            raise BadArgs(f"unknown catalogue part {part_id!r}")
        p = cat.PARTS[part_id]
        return Plan(None, 0.0, lambda: {"part_id": part_id, "name": p["name"], "price_eur": p["price"],
                                            "datasheet": p["datasheet"]})

    def _t_read_manual(self, device):
        m = cat.manuals(self.lab)
        if device not in m:
            raise BadArgs(f"no manual {device!r}; manuals: {sorted(m)}")
        return Plan(None, 0.0, lambda: {"device": device, "manual": m[device]})

    def _t_buy(self, items):
        price = sum(cat.PARTS[k]["price"] * q for k, q in items.items())
        if self.cost + price > K.SPEND_CAP:
            return Plan("desk", 60.0, lambda: {"outcome": f"order refused: total spend would exceed "
                                                          f"EUR {K.SPEND_CAP:.0f}", "order_eur": price})

        def run():
            notes, got = [], []
            self.cost += price
            for k, q in items.items():
                if q == 0:
                    continue
                self.bought[k] = self.bought.get(k, 0) + q
                p = cat.PARTS[k]
                for _ in range(q):
                    if p["kind"] == "mirror":
                        self.n_mirror += 1
                        pid = f"mirror-{self.n_mirror}"
                        self.inv[pid] = {"part_id": k, "kind": "mirror", "part": None, "req": None}
                        got.append(pid)
                    elif p["kind"] == "periscope":
                        self.n_periscope += 1
                        pid = f"periscope-{self.n_periscope}"
                        self.inv[pid] = {"part_id": k, "kind": "periscope", "part": None, "req": None}
                        got.append(pid)
                    elif p["kind"] == "stage":
                        if "stage" in self.inv:
                            notes.append("the previous delay stage was swapped out")
                        self.inv["stage"] = {"part_id": k, "kind": "stage", "part": None, "req": None,
                                             "part_travel": p["travel"], "drive": p["drive"]}
                        self.stage_cmd = self.stage_true = 0.0
                        self.stage_last_dir = 0
                        self._invalidate()
                        got.append("stage")
                    elif p["kind"] == "diagnostic":
                        if k not in self.diag_owned:
                            self.diag_owned.append(k)
                        if self.diag and self.diag != k:
                            notes.append(f"{k} installed in the sample mount in place of {self.diag}")
                        self.diag = k
                        got.append(f"{k} (installed in the sample mount)")
                    elif p["kind"] == "filter":
                        if k not in self.filters_owned:
                            self.filters_owned.append(k)
                        if self.filter and self.filter != k:
                            notes.append(f"{k} put in the filter holder in place of {self.filter}")
                        self.filter = k
                        got.append(f"{k} (in the signal camera's filter holder)")
                    elif p["kind"] == "camera":
                        self.align_cam = k
                        got.append(f"{k} (fitted in the flip-in alignment mount)")
            out = {"outcome": "delivered", "order_eur": price, "spent_eur": self.cost, "received": got}
            if notes:
                out["notes"] = notes
            return out
        return Plan("desk", 900.0, run)

    def _t_place(self, part, x, z, height, yaw_deg, height_in=None):
        it = self._item(part)
        kind = it["kind"]
        if it["part"] is not None:
            raise BadArgs(f"{part} is already on the table (use move, rotate or remove)")
        if kind == "periscope" and height_in is None:
            raise BadArgs("periscopes need height_in")
        if kind != "periscope" and height_in is not None:
            raise BadArgs("height_in only applies to periscopes")
        yaw = math.radians(yaw_deg)
        travel = it.get("part_travel", 0.0)
        msg = self._fits(part, kind, x, z, yaw, travel)
        if msg is None:
            for h in [height] + ([height_in] if height_in is not None else []):
                if not (K.MIN_POST_HEIGHT <= h <= K.MAX_HEIGHT):
                    msg = f"post height must be {K.MIN_POST_HEIGHT:.0f}-{K.MAX_HEIGHT:.0f} mm"
            if kind == "periscope" and msg is None and abs(height - height_in) < 30.0:
                msg = "periscope heights must be at least 30 mm apart"
        if msg is not None:
            return Plan((x, z), 60.0, lambda: {"outcome": msg})

        def run():
            r = self.rng_place
            ex, ez, eh = r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-0.5, 0.5)
            eyaw = r.gauss(0.0, math.radians(0.5))
            hin = None
            if height_in is not None:
                hin = height_in + r.uniform(-0.5, 0.5)
            p = Part(part, kind, (x + ex, height + eh, z + ez), yaw + eyaw, height_in=hin,
                     mount_err=self.lab.mount_error(part) if kind in ("mirror", "periscope") else (0.0, 0.0),
                     travel=travel, level=self.level)
            if kind == "stage":
                p.stage_pos = self.stage_true
            it["part"] = p
            it["req"] = {"x_mm": x, "z_mm": z, "height_mm": height, "yaw_deg": yaw_deg}
            if hin is not None:
                it["req"]["height_in_mm"] = height_in
            self._invalidate()
            return {"outcome": f"{part} placed"}
        return Plan((x, z), 300.0, run)

    def _placed(self, part):
        it = self._item(part)
        if it["part"] is None:
            raise BadArgs(f"{part} is not on the table")
        return it

    def _t_rotate(self, part, delta_deg):
        it = self._placed(part)
        if abs(delta_deg) > 360:
            raise BadArgs("delta_deg must be within +/-360")

        def run():
            it["part"].yaw += math.radians(delta_deg) + self.rng_place.gauss(0.0, math.radians(0.2))
            it["req"]["yaw_deg"] = it["req"]["yaw_deg"] + delta_deg
            self._invalidate()
            return {"outcome": f"{part} rotated"}
        return Plan(self._stand_at(it), 120.0, run)

    def _t_move(self, part, x, z):
        it = self._placed(part)
        p = it["part"]
        msg = self._fits(part, it["kind"], x, z, p.yaw, p.travel)
        if msg is not None:
            return Plan((x, z), 60.0, lambda: {"outcome": msg})

        def run():
            r = self.rng_place
            p.pos = (x + r.uniform(-1, 1), p.pos[1], z + r.uniform(-1, 1))
            p.yaw += r.gauss(0.0, math.radians(0.2))
            it["req"]["x_mm"], it["req"]["z_mm"] = x, z
            self._invalidate()
            return {"outcome": f"{part} moved"}
        return Plan((x, z), 180.0, run)

    def _t_remove(self, part):
        it = self._placed(part)

        def run():
            it["part"] = None
            it["req"] = None
            self._invalidate()
            return {"outcome": f"{part} back in the inventory"}
        return Plan(self._stand_at(it), 60.0, run)

    def _t_knob(self, part, axis, delta_mrad, watch=False):
        it = self._placed(part)
        if it["kind"] not in ("mirror", "periscope"):
            raise BadArgs(f"{part} has no knobs")
        if axis not in ("yaw", "pitch"):
            raise BadArgs("axis must be 'yaw' or 'pitch'")
        if abs(delta_mrad) > 200:
            raise BadArgs("delta_mrad must be within +/-200 (knob range is +/-50 mrad)")

        def run():
            p = it["part"]
            attr = "knob_yaw" if axis == "yaw" else "knob_pitch"
            cur = getattr(p, attr)
            new = cur + delta_mrad * 1e-3 * (1.0 + self.rng_noise.gauss(0.0, 0.02))
            out = {"outcome": "turned"}
            lim = 0.050
            if abs(new) > lim:
                new = math.copysign(lim, new)
                out["outcome"] = "knob at end of travel"
            setattr(p, attr, new)
            self._invalidate()
            if watch:
                if math.hypot(self.pos[0] - DESK_XZ[0], self.pos[1] - DESK_XZ[1]) <= K.WATCH_RADIUS:
                    out["camera_sample"] = self._camera("sample")
                else:
                    out["camera_sample"] = "monitor too far away to read from here"
            return out
        return Plan(self._stand_at(it), KNOB_S, run)

    def _t_ir_card(self, part=None, x=None, z=None, height=None):
        if part is not None:
            if x is not None or z is not None or height is not None:
                raise BadArgs("give either part or (x, z, height), not both")
            it = self._placed(part)

            def run():
                seen = []
                for arm, b in self._visible().items():
                    if b is None:
                        continue
                    for h in b.hits:
                        if h.part_id == part:
                            d = {"beam": arm}
                            if it["kind"] == "periscope":
                                d["mirror"] = h.role
                            d.update(self._ir_off(h.offset))
                            seen.append(d)
                return {"part": part, "beams": seen}
            return Plan(self._stand_at(it), 30.0, run)
        if x is None or z is None or height is None:
            raise BadArgs("give part, or all of x, z, height")

        def run_pt():
            seen = []
            pt = (x, height, z)
            for arm, b in self._visible().items():
                if b is None:
                    continue
                ca = closest_approach(b, pt)
                if ca is not None and ca[0] <= 30.0:
                    seen.append({"beam": arm, **self._ir_off(ca[1])})
            return {"point": {"x_mm": x, "z_mm": z, "height_mm": height}, "beams": seen}
        return Plan((x, z), 30.0, run_pt)

    def _ir_off(self, off):
        n = self.rng_noise
        return {"dx_mm": round(off[0] + n.gauss(0, 0.2), 1), "dz_mm": round(off[2] + n.gauss(0, 0.2), 1),
                "dheight_mm": round(off[1] + n.gauss(0, 0.2), 1)}

    def _t_install(self, part_id):
        if part_id not in self.diag_owned and part_id not in self.filters_owned:
            raise BadArgs(f"you don't own a diagnostic or filter {part_id!r}")
        loc = self._stand_at(self.inv["sample"])

        def run():
            if part_id in self.filters_owned:
                self.filter = part_id
                return {"outcome": f"{part_id} in the signal camera's filter holder"}
            self.diag = part_id
            return {"outcome": f"{part_id} installed in the sample mount"}
        return Plan(loc, 120.0 if part_id in self.diag_owned else 30.0, run)

    def _t_uninstall(self, what):
        if what not in ("filter", "diagnostic"):
            raise BadArgs("what must be 'filter' or 'diagnostic'")
        loc = self._stand_at(self.inv["sample"])

        def run():
            if what == "filter":
                self.filter = None
                return {"outcome": "filter holder empty"}
            self.diag = None
            return {"outcome": "sample mount empty"}
        return Plan(loc, 30.0 if what == "filter" else 60.0, run)

    def _t_measure_path(self, arm):
        arm = self._arm(arm)

        def run():
            b = self._visible()[arm]
            if b is None:
                return {"arm": arm, "outcome": "shutter closed: no beam to follow"}
            L = b.path_geom + self.rng_noise.uniform(-5.0, 5.0)
            ends = {"sample": "sample (focal plane)"}.get(b.end, b.end_note)
            return {"arm": arm, "path_mm": round(L, 1), "ends_at": ends,
                    "note": "table path from the output port; excludes anything inside the laser/OPA housing"}
        return Plan(None, 180.0, run)

    def _camera(self, plane):
        if self.inv["sample"]["part"] is None:
            return []
        vis = self._visible()
        rng = cat.PARTS[self.align_cam]["range_nm"] if self.align_cam else K.CAM_SI_RANGE
        if plane == "sample":
            return P.camera_sample(vis, self.lams, rng, self.rng_noise,
                                   K.L2_STRETCH if self.level == 2 else 1.0)
        return P.camera_lens(vis, self.lams, rng, self.rng_noise)

    def _t_view_camera(self, plane):
        if plane not in ("sample", "lens"):
            raise BadArgs("plane must be 'sample' or 'lens'")

        def run():
            out = {"plane": plane, "spots": self._camera(plane)}
            if self.inv["sample"]["part"] is None:
                out["note"] = "the sample mount is not on the table"
            return out
        return Plan("desk", 10.0, run)

    def _t_block(self, arm):
        arm = self._arm(arm)

        def run():
            self.shutter_open[arm] = False
            return {"outcome": f"{arm} shutter closed"}
        return Plan("desk", 5.0, run)

    def _t_unblock(self, arm):
        arm = self._arm(arm)

        def run():
            self.shutter_open[arm] = True
            return {"outcome": f"{arm} shutter open"}
        return Plan("desk", 5.0, run)

    def _stage(self):
        if "stage" not in self.inv:
            raise BadArgs("you don't own a delay stage")
        return self.inv["stage"]

    def _set_stage(self, cmd: float):
        it = self.inv["stage"]
        d = cmd - self.stage_cmd
        if abs(d) > 1e-12:
            self.stage_last_dir = 1 if d > 0 else -1
        self.stage_cmd = cmd
        if it["drive"] == "manual":
            self.stage_true = cmd - 0.0025 * self.stage_last_dir
        else:
            self.stage_true = cmd + self.rng_noise.gauss(0.0, 0.00005)
        if it["part"] is not None:
            it["part"].stage_pos = self.stage_true
            self._invalidate()

    def _stage_loc(self, it):
        return "desk" if it["drive"] == "motor" or it["part"] is None else self._stand_at(it)

    def _t_move_stage(self, position_mm):
        it = self._stage()
        travel = it["part_travel"]
        target = _clamp(position_mm, 0.0, travel)
        dist = abs(target - self.stage_cmd)
        cost = (2.0 + dist / 2.0) if it["drive"] == "motor" else (3.0 + dist / 1.0)

        def run():
            self._set_stage(target)
            out = {"outcome": "moved", "position_mm": round(target, 4)}
            if target != position_mm:
                out["outcome"] = "stage at end of travel"
            return out
        return Plan(self._stage_loc(it), cost, run)

    def _read(self, t_int):
        vis = self._visible()
        if self.diag is None:
            return {"note": "no detector installed in the sample mount"}
        d = cat.PARTS[self.diag]
        if self.inv["sample"]["part"] is None:
            vis = {"800nm": None, "opa": None}
        if d["model"] == "photodiode":
            return P.photodiode(vis, self.lams, d["range_nm"], self.lab.opa_extra_path, self.rng_noise)
        f = cat.filter_spec(self.filter) if (self.filter and d["readout"] == "camera") else None
        return P.nonlinear_signal(d, f, self.lab.opa_lambda, vis["800nm"], vis["opa"], self.lab.opa_extra_path,
                                  t_int, self.rng_noise, self.level)

    def _t_read_signal(self, t_int):
        if not (0.01 <= t_int <= 10.0):
            raise BadArgs("t_int must be 0.01-10 s")

        def run():
            out = {"detector": self.diag, "t_int_s": t_int}
            if self.diag and cat.PARTS[self.diag]["readout"] == "camera":
                out["filter"] = self.filter
            out.update(self._read(t_int))
            return out
        return Plan("desk", t_int + 1.0, run)

    def _t_scan(self, start_mm, end_mm, step_mm, t_int):
        it = self._stage()
        travel = it["part_travel"]
        if not (0.01 <= t_int <= 10.0):
            raise BadArgs("t_int must be 0.01-10 s")
        if not (0.0 <= start_mm <= travel and 0.0 <= end_mm <= travel):
            raise BadArgs(f"scan range must be within the stage travel 0-{travel:g} mm")
        if step_mm <= 0:
            raise BadArgs("step_mm must be positive")
        span = abs(end_mm - start_mm)
        n = int(math.floor(span / step_mm + 1e-9)) + 1
        if n > 5000:
            raise BadArgs("too many points (max 5000)")
        if n < 1 or step_mm < 1e-5:
            raise BadArgs("step_mm too small")
        sgn = 1.0 if end_mm >= start_mm else -1.0
        positions = [start_mm + sgn * i * step_mm for i in range(n)]
        motor = it["drive"] == "motor"
        if motor:
            cost = 2.0 + abs(start_mm - self.stage_cmd) / 2.0 + n * (t_int + 0.3 + step_mm / 2.0)
        else:
            cost = 3.0 + abs(start_mm - self.stage_cmd) + n * (t_int + 3.0)

        def run():
            pts = []
            sat = False
            for x in positions:
                self._set_stage(x)
                r = self._read(t_int)
                if "counts" in r:
                    pts.append([round(x, 5), r["counts"]])
                    if r.get("saturated"):
                        sat = True
                elif "note" in r:
                    return {"error": r["note"], "position_mm": round(self.stage_cmd, 5)}
                else:
                    pts.append([round(x, 5), r])
            out = {"detector": self.diag, "t_int_s": t_int, "points": pts,
                   "position_mm": round(self.stage_cmd, 5), "columns": ["position_mm", "counts"]}
            if self.diag and cat.PARTS[self.diag]["readout"] == "camera":
                out["filter"] = self.filter
            if sat:
                out["saturated"] = True
            return out
        return Plan(self._stage_loc(it), cost, run)

    def _t_submit(self):
        return Plan(None, 0.0, lambda: {"outcome": "submitted; the episode is over"})


def _jsonable(x):
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_jsonable(v) for v in x]
    if isinstance(x, float) and not math.isfinite(x):
        return str(x)
    if isinstance(x, (str, int, float, bool)) or x is None:
        return x
    return repr(x)
