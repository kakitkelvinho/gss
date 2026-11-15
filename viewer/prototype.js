// Throwaway UI prototype. The viewer uses verifier-only snapshots from runs_bundle.js.
const runs = window.GSS_RUNS_BUNDLE?.runs.filter(run => run.trajectory?.length) ?? [];
const app = document.getElementById('app');
const query = new URLSearchParams(location.search), num = (key, fallback) => Number.isFinite(Number(query.get(key))) && query.get(key) !== null ? Number(query.get(key)) : fallback;
const DEFAULT_CAM = { yaw: -14, pitch: 38, zoom: 1, panX: 0, panY: 0 };
const CAM_LIMITS = { yaw: [-80, 20], pitch: [15, 85], zoom: [0.6, 6] };
const clamp = (v, [lo, hi]) => Math.max(lo, Math.min(hi, v));
const runById = runs.findIndex(run => run.id === query.get('run'));
const initialRun = runById >= 0 ? runById : clamp(Math.trunc(num('run', 3)), [0, Math.max(0, runs.length - 1)]);
const initialStep = clamp(Math.trunc(num('step', 108)), [0, Math.max(0, (runs[initialRun]?.trajectory.length || 1) - 1)]);
const state = { cam: { yaw: clamp(num('yaw', DEFAULT_CAM.yaw), CAM_LIMITS.yaw), pitch: clamp(num('pitch', DEFAULT_CAM.pitch), CAM_LIMITS.pitch), zoom: clamp(num('zoom', 1), CAM_LIMITS.zoom), panX: num('panx', 0), panY: num('pany', 0) }, run: initialRun, step: initialStep, playing: false, speed: 1, timer: null, menu: null, railOpen: new URLSearchParams(location.search).get('rail') !== 'closed', expanded: new Set(), selectedPart: null };

function esc(value) { return String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]); }
function fmtTime(seconds) { const n = Math.round(seconds || 0); return `${Math.floor(n / 3600)}:${String(Math.floor(n % 3600 / 60)).padStart(2, '0')}:${String(n % 60).padStart(2, '0')}`; }
function money(n) { return `€${Math.round(n || 0).toLocaleString('en-US')}`; }
function currentRun() { return runs[state.run] || runs[0]; }
function currentCall() { return currentRun()?.trajectory[Math.min(state.step, currentRun().trajectory.length - 1)]; }
function shortArgs(args) { const parts = Object.entries(args || {}).slice(0, 2).map(([key, value]) => value && typeof value === 'object' ? `${Object.keys(value).length} ${key}` : `${key} ${typeof value === 'number' ? Number(value.toFixed(2)) : String(value).slice(0, 18)}`); return parts.join(' · ') || '—'; }
function cleanTool(tool) { return (tool || 'tool').replaceAll('_', ' '); }
function contextFor(call) { const t = call.tool || ''; if (/read_manual|get_datasheet/.test(t)) return { verb: 'Reading the optics manual', pose: 'manual' }; if (/buy|catalogue/.test(t)) return { verb: 'Choosing lab equipment', pose: 'buy' }; if (/place|knob|move_stage|steer/.test(t)) return { verb: 'Adjusting the optical path', pose: 'adjust' }; if (/scan|signal|camera|ir_card|measure/.test(t)) return { verb: 'Taking a measurement', pose: 'measure' }; return { verb: 'Working through the run', pose: 'observe' }; }

function actionCoordinates(call) {
  const args = call.args || {}, parts = call.snapshot?.parts || [];
  if (state.selectedPart) { const selected = parts.find(part => part.id === state.selectedPart); if (selected) return selected.pos; }
  if (Number.isFinite(args.x) && Number.isFinite(args.z)) return { x: args.x, z: args.z };
  const referenced = parts.find(part => part.id === args.part || part.id === args.mirror);
  if (referenced) return referenced.pos;
  if (args.plane === 'sample') return parts.find(part => part.kind === 'sample')?.pos || null;
  return null;
}
// ---- Scene geometry: a true orthographic view of the simulator's millimetre coordinates. ----
// World axes follow sim/vec.py: x along the 2400 mm table, z across the 1200 mm table, h up from the table top.
// Every optic is drawn from the replay pose with the simulator's own mount dimensions (sim/constants.py).
const DEG = Math.PI / 180;
const C = { ink: '#16120F', ink2: '#2B231D', ink3: '#413629', room: '#1E1915', floor: '#0E0B09', paper: '#EDE3CC', paper2: '#F7F0DF', table: '#D3C6A8', tableHole: '#3A3027', house: '#DCCFB2', house2: '#C9BB9C', fig: '#8E2A24', figTop: '#B23A30', figDark: '#5E1B17', laser800: '#FF4A26', laserOpa: '#3CC8EC', kraft: '#9C927E', kraft2: '#776E5C', orange: '#E8742A', blue: '#4A8FC4' };
const BEAMS = [['800nm', C.laser800, '800 nm'], ['opa', C.laserOpa, 'OPA']];
// Orthographic camera: yaw about the vertical axis, then pitch down. The drawing stays a true projection at any setting.
const VIEW = {}, TOWARD_VIEWER = {};
function setView(yaw, pitch) { Object.assign(VIEW, { c: Math.cos(yaw * DEG), s: Math.sin(yaw * DEG), sf: Math.sin(pitch * DEG), cf: Math.cos(pitch * DEG) }); Object.assign(TOWARD_VIEWER, { x: VIEW.s * VIEW.cf, z: VIEW.c * VIEW.cf, h: VIEW.sf }); }
setView(DEFAULT_CAM.yaw, DEFAULT_CAM.pitch);
const LIGHT_DIR = norm({ x: 0.75, z: 1.0, h: -1.1 }), LIGHT = norm({ x: -LIGHT_DIR.x, z: -LIGHT_DIR.z, h: 0 });
const MM = { table: { x: 2400, z: 1200 }, slab: 60, floor: -760, robot: 1050, mountHalf: 19, mountDepth: [0.5, 12], postR: 6.35, postBehind: 6, lensRing: 25.4, retroR: 19.05, apex: 90, retroFront: 40, minPost: 50 };
const SCENE = { w: 1200, h: 800, fit: { x0: 40, y0: 96, x1: 1160, y1: 600 } };
let FIT = { k: 0.4, ox: 0, oy: 0 };

function norm(v) { const l = Math.hypot(v.x, v.z, v.h || 0) || 1; return { x: v.x / l, z: v.z / l, h: (v.h || 0) / l }; }
function dot(a, b) { return a.x * b.x + a.z * b.z + (a.h || 0) * (b.h || 0); }
function cross(a, b) { return { x: a.z * b.h - a.h * b.z, z: a.h * b.x - a.x * b.h, h: a.x * b.z - a.z * b.x }; }
function add(p, v, t = 1) { return { x: p.x + v.x * t, z: p.z + v.z * t, h: (p.h || 0) + (v.h || 0) * t }; }
function yawVec(deg) { return { x: Math.cos(deg * DEG), z: Math.sin(deg * DEG), h: 0 }; }
function raw(p) { return { x: p.x * VIEW.c - p.z * VIEW.s, y: (p.x * VIEW.s + p.z * VIEW.c) * VIEW.sf - (p.h || 0) * VIEW.cf }; }
function depth(p) { return (p.x * VIEW.s + p.z * VIEW.c) * VIEW.cf + (p.h || 0) * VIEW.sf; }
function proj(p) { const r = raw(p); return { x: FIT.ox + FIT.k * r.x, y: FIT.oy + FIT.k * r.y }; }
function pt(p) { const q = proj(p); return `${q.x.toFixed(1)},${q.y.toFixed(1)}`; }
function poly(list, attrs) { return `<polygon points="${list.map(pt).join(' ')}" ${attrs}/>`; }
function line(a, b, attrs) { const p = proj(a), q = proj(b); return `<line x1="${p.x.toFixed(1)}" y1="${p.y.toFixed(1)}" x2="${q.x.toFixed(1)}" y2="${q.y.toFixed(1)}" ${attrs}/>`; }
function px(mm) { return (mm * FIT.k).toFixed(2); }

function fitScene(meta) {
  setView(DEFAULT_CAM.yaw, DEFAULT_CAM.pitch);
  const T = MM.table, pts = [];
  for (const x of [0, T.x]) for (const z of [0, T.z]) for (const h of [0, -MM.slab]) pts.push({ x, z, h });
  for (const b of meta?.housings_mm || []) for (const x of [b.x0, b.x1]) for (const z of [b.z0, b.z1]) pts.push({ x, z, h: b.h1 });
  const desk = meta?.desk_mm || { x: -300, z: 600 }; pts.push({ x: desk.x - 380, z: desk.z - 300, h: 0 });
  const r = pts.map(raw), xs = r.map(p => p.x), ys = r.map(p => p.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys), f = SCENE.fit;
  const k = Math.min((f.x1 - f.x0) / (maxX - minX), (f.y1 - f.y0) / (maxY - minY));
  const ox = (f.x0 + f.x1) / 2 - k * (minX + maxX) / 2, oy = f.y0 - k * minY, centre = { x: T.x / 2, z: T.z / 2, h: 0 }, rc0 = raw(centre);
  const ax = ox + k * rc0.x, ay = oy + k * rc0.y, cam = state.cam, z = cam.zoom, cx = SCENE.w / 2, cy = SCENE.h / 2;
  setView(cam.yaw, cam.pitch); const rc = raw(centre);
  FIT = { k: k * z, ox: (ax - k * rc.x - cx) * z + cx + cam.panX, oy: (ay - k * rc.y - cy) * z + cy + cam.panY };
}

// A convex block: centre on its base, yaw of its length axis, length L, width W, from h0 to h1.
function block({ c, yaw = 0, L, W, h0, h1 }, fills, extra = '') {
  const a = yawVec(yaw), b = { x: -a.z, z: a.x, h: 0 };
  const corner = (sa, sb, h) => ({ x: c.x + a.x * sa * L / 2 + b.x * sb * W / 2, z: c.z + a.z * sa * L / 2 + b.z * sb * W / 2, h });
  const faces = [
    { n: a, q: [corner(1, -1, h0), corner(1, 1, h0), corner(1, 1, h1), corner(1, -1, h1)] },
    { n: { x: -a.x, z: -a.z, h: 0 }, q: [corner(-1, -1, h0), corner(-1, 1, h0), corner(-1, 1, h1), corner(-1, -1, h1)] },
    { n: b, q: [corner(-1, 1, h0), corner(1, 1, h0), corner(1, 1, h1), corner(-1, 1, h1)] },
    { n: { x: -b.x, z: -b.z, h: 0 }, q: [corner(-1, -1, h0), corner(1, -1, h0), corner(1, -1, h1), corner(-1, -1, h1)] },
  ];
  const sides = faces.filter(f => dot(f.n, TOWARD_VIEWER) > 1e-6).map(f => poly(f.q, `fill="${dot(f.n, LIGHT) > 0 ? fills.light : fills.dark}" ${extra}`)).join('');
  return sides + poly([corner(-1, -1, h1), corner(1, -1, h1), corner(1, 1, h1), corner(-1, 1, h1)], `fill="${fills.top}" ${extra}`);
}
function disc(center, normal, r, attrs, n = 30) {
  const nn = norm(normal), u = Math.abs(nn.h) > 0.95 ? { x: 1, z: 0, h: 0 } : norm({ x: -nn.z, z: nn.x, h: 0 }), v = cross(nn, u), list = [];
  for (let i = 0; i < n; i++) { const t = i / n * Math.PI * 2; list.push(add(add(center, u, Math.cos(t) * r), v, Math.sin(t) * r)); }
  return poly(list, attrs);
}
function post(at, h1) { return line({ ...at, h: 0 }, { ...at, h: h1 }, `stroke="${C.ink}" stroke-width="${px(MM.postR * 2)}"`); }
function postBase(at, yaw) { return block({ c: { x: at.x, z: at.z }, yaw, L: 25, W: 64, h0: 0, h1: 10 }, INK_FILLS); }
const INK_FILLS = { top: C.ink3, light: C.ink2, dark: C.ink };
const MOUNT_FILLS = { top: '#5A4B3C', light: C.ink3, dark: C.ink };
const OPTIC = `fill="${C.paper2}" stroke="${C.ink}" stroke-width="1"`;

function mirrorSvg(part) {
  const yaw = part.eff_yaw_deg ?? part.yaw_deg ?? 0, n = yawVec(yaw), p = part.pos, stem = add(p, n, -MM.postBehind);
  const [d0, d1] = MM.mountDepth, plate = block({ c: add(p, n, -(d0 + d1) / 2), yaw, L: d1 - d0, W: MM.mountHalf * 2, h0: p.h - MM.mountHalf, h1: p.h + MM.mountHalf }, MOUNT_FILLS);
  const face = disc(add(p, n, 0.4), n, 12.7, OPTIC);
  return postBase(stem, yaw) + post(stem, p.h - MM.mountHalf) + (dot(n, TOWARD_VIEWER) > 0 ? plate + face : face + plate);
}
function periscopeSvg(part) {
  const d = yawVec(part.eff_yaw_deg ?? part.yaw_deg ?? 180), u = { x: -d.z, z: d.x, h: 0 }, p = part.pos, top = part.h_in ?? p.h + 40;
  const tower = add({ x: p.x, z: p.z }, u, 30);
  const upper = { x: p.x, z: p.z, h: top }, lower = { x: p.x, z: p.z, h: p.h };
  const mirror = (at, n) => disc(at, n, MM.mountHalf, `fill="${C.ink2}"`) + disc(add(at, n, 0.5), n, 12.7, OPTIC);
  const body = postBase(tower, part.yaw_deg) + block({ c: tower, yaw: part.yaw_deg, L: 26, W: 26, h0: 10, h1: top + 24 }, MOUNT_FILLS);
  const arms = line(add(upper, u, 4), add(upper, u, 24), `stroke="${C.ink}" stroke-width="${px(10)}"`) + line(add(lower, u, 4), add(lower, u, 24), `stroke="${C.ink}" stroke-width="${px(10)}"`);
  const mirrors = mirror(upper, { x: -d.x, z: -d.z, h: -1 }) + mirror(lower, { x: d.x, z: d.z, h: 1 });
  return depth(tower) < depth(p) ? body + arms + mirrors : mirrors + arms + body;
}
function stageSvg(part) {
  const yaw = part.eff_yaw_deg ?? part.yaw_deg ?? 180, d = yawVec(yaw), p = part.pos, sp = part.stage_pos_mm ?? 0, travel = part.travel_mm ?? 25;
  const apex = add(p, d, MM.apex + sp), face = add(apex, d, -MM.retroFront);
  const rail = block({ c: add({ x: p.x, z: p.z }, d, (MM.apex - MM.retroFront + MM.apex + travel + 16) / 2), yaw, L: MM.retroFront + travel + 40, W: 72, h0: 0, h1: 34 }, INK_FILLS);
  const carriage = block({ c: add({ x: face.x, z: face.z }, d, MM.retroFront / 2 + 6), yaw, L: MM.retroFront + 12, W: 56, h0: 34, h1: p.h + MM.retroR + 6 }, MOUNT_FILLS);
  const knob = line(add({ ...apex, h: 17 }, d, 28), add({ ...apex, h: 17 }, d, 58), `stroke="${C.ink2}" stroke-width="${px(18)}"`);
  const n = { x: -d.x, z: -d.z, h: 0 }, mouth = disc(add(face, n, 0.5), n, MM.retroR, `fill="${C.paper2}" stroke="${C.ink}" stroke-width="1"`) + disc(add(face, n, 0.6), n, MM.retroR * 0.45, `fill="${C.kraft}"`);
  return dot(n, TOWARD_VIEWER) > 0 ? knob + rail + carriage + mouth : mouth + knob + rail + carriage;
}
function sampleSvg(part, hit) {
  const lenses = part.lenses?.length ? part.lenses : [{ pos: part.pos, dir: yawVec(part.yaw_deg + 180), radius_mm: 12.7, sample_pos: part.pos }];
  const sampleAt = lenses[0].sample_pos || part.pos, n = yawVec(part.yaw_deg ?? 180), u = norm({ x: -n.z, z: n.x, h: 0 }), up = { x: 0, z: 0, h: 1 };
  const lensSvg = lenses.map(lens => {
    const at = lens.pos, ring = disc(at, lens.dir, lens.mount_radius_mm ?? MM.lensRing, `fill="${C.ink2}"`), glass = disc(add(at, lens.dir, 0.4), lens.dir, lens.radius_mm ?? 12.7, `fill="#CFE0E4" stroke="${C.ink}" stroke-width="1"`);
    const stand = { x: at.x, z: at.z };
    return postBase(stand, lens.yaw_deg ?? part.yaw_deg) + post(stand, at.h - (lens.mount_radius_mm ?? MM.lensRing)) + ring + glass;
  }).join('');
  const corner = (a, b) => add(add(sampleAt, u, a), up, b), half = 22, facing = dot(n, TOWARD_VIEWER) > 0;
  const plate = poly([corner(-half, -half), corner(half, -half), corner(half, half), corner(-half, half)], `fill="${facing ? C.paper : C.kraft}" stroke="${C.ink}" stroke-width="1.2"`);
  const star = facing && hit ? poly([[0, 17], [3, 3], [17, 0], [3, -3], [0, -17], [-3, -3], [-17, 0], [-3, 3]].map(([a, b]) => corner(a, b)), `fill="${C.orange}"`) + disc(add(sampleAt, n, 0.5), n, 2.6, `fill="${C.ink}"`) : '';
  const holder = postBase({ x: sampleAt.x, z: sampleAt.z }, part.yaw_deg) + post({ x: sampleAt.x, z: sampleAt.z }, sampleAt.h - half);
  return holder + plate + star + lensSvg;
}
function housingSvg(box, port, label, color) {
  const c = { x: (box.x0 + box.x1) / 2, z: (box.z0 + box.z1) / 2 };
  const body = block({ c, yaw: 0, L: box.x1 - box.x0, W: box.z1 - box.z0, h0: box.h0, h1: box.h1 }, { top: C.house, light: C.house2, dark: C.kraft }, 'filter="url(#pcutS)"');
  const aperture = port ? disc(port.pos, { x: -1, z: 0, h: 0 }, 13, `fill="${C.ink}"`) + disc(add(port.pos, { x: -1, z: 0, h: 0 }, 1), { x: -1, z: 0, h: 0 }, 8, `fill="${color}"`) : '';
  const q = proj({ x: box.x0, z: box.z0, h: box.h1 }), w = label.length * 11 + 34, x = q.x - w - 8, y = q.y - 8;
  return { body: body + aperture, label: `<rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${w}" height="28" fill="${C.ink}"/><rect x="${(x + 8).toFixed(1)}" y="${(y + 9).toFixed(1)}" width="10" height="10" fill="${color}"/><text x="${(x + 25).toFixed(1)}" y="${(y + 22).toFixed(1)}" class="sc-house">${label}</text>` };
}
function tableSvg() {
  const T = MM.table, top = [{ x: 0, z: 0 }, { x: T.x, z: 0 }, { x: T.x, z: T.z }, { x: 0, z: T.z }], at = h => top.map(p => ({ ...p, h }));
  const slabBox = { c: { x: T.x / 2, z: T.z / 2, h: -MM.slab / 2 }, u: { x: T.x / 2, z: 0, h: 0 }, v: { x: 0, z: T.z / 2, h: 0 }, w: { x: 0, z: 0, h: MM.slab / 2 } };
  const shadow = `<g fill="${C.floor}" opacity=".55">${shadowOn([slabBox], MM.floor)}</g>`;
  const legs = [[250, 220], [T.x - 250, 220], [250, T.z - 220], [T.x - 250, T.z - 220]].sort((a, b) => depth({ x: a[0], z: a[1] }) - depth({ x: b[0], z: b[1] }))
    .map(([x, z]) => block({ c: { x, z }, L: 170, W: 170, h0: MM.floor, h1: -MM.slab }, { top: C.ink, light: C.ink3, dark: C.ink2 })).join('');
  const slab = block({ c: { x: T.x / 2, z: T.z / 2 }, L: T.x, W: T.z, h0: -MM.slab, h1: 0 }, { top: C.table, light: C.kraft, dark: C.kraft2 }, 'filter="url(#pcutS)"');
  const k = FIT.k, m = [k * VIEW.c, k * VIEW.s * VIEW.sf, -k * VIEW.s, k * VIEW.c * VIEW.sf, FIT.ox, FIT.oy].map(v => v.toFixed(5)).join(' ');
  const holes = `<defs><pattern id="holes" width="25" height="25" patternUnits="userSpaceOnUse" patternTransform="matrix(${m})"><circle cx="12.5" cy="12.5" r="3.3" fill="${C.tableHole}" opacity=".5"/></pattern></defs>${poly(at(0), 'fill="url(#holes)"')}`;
  const ticks = [];
  for (let x = 0; x <= T.x; x += 100) { const major = x % 600 === 0; ticks.push(line({ x, z: T.z, h: -MM.slab }, { x, z: T.z + (major ? 70 : 35), h: -MM.slab }, `stroke="${C.paper}" stroke-width="${major ? 1.6 : 0.9}"`)); if (major) { const q = proj({ x, z: T.z + 150, h: -MM.slab }); ticks.push(`<text x="${q.x.toFixed(1)}" y="${(q.y + 4).toFixed(1)}" text-anchor="middle" class="sc-tick">${x === T.x ? 'X 2400 MM' : x}</text>`); } }
  for (let z = 0; z <= T.z; z += 100) { const major = z % 600 === 0; ticks.push(line({ x: 0, z, h: -MM.slab }, { x: major ? -70 : -35, z, h: -MM.slab }, `stroke="${C.paper}" stroke-width="${major ? 1.6 : 0.9}"`)); if (major && z) { const q = proj({ x: -120, z, h: -MM.slab }); ticks.push(`<text x="${q.x.toFixed(1)}" y="${(q.y + 4).toFixed(1)}" text-anchor="end" class="sc-tick">${z === T.z ? 'Z 1200 MM' : z}</text>`); } }
  return { under: shadow + legs, slab: slab + holes, ticks: ticks.join('') };
}
function deskSvg(meta) {
  const at = meta?.desk_mm || { x: -300, z: 600 }, c = { x: at.x - 260, z: at.z - 120 };
  const desk = block({ c, L: 200, W: 420, h0: MM.floor, h1: -120 }, { top: C.kraft, light: C.kraft2, dark: C.ink3 }, 'filter="url(#pcutS)"');
  const screen = block({ c: { x: c.x - 40, z: c.z }, L: 20, W: 300, h0: -120, h1: 120 }, INK_FILLS);
  const s = [{ x: c.x - 29, z: c.z - 130, h: -100 }, { x: c.x - 29, z: c.z + 130, h: -100 }, { x: c.x - 29, z: c.z + 130, h: 100 }, { x: c.x - 29, z: c.z - 130, h: 100 }];
  return desk + screen + poly(s, `fill="${C.paper}"`);
}
// ---- The worker: a blocky mannequin built in world millimetres, so it turns with the camera and casts real shadows. ----
// One fixed key light travels along LIGHT_DIR (from high behind-left); block faces and shadows both use it.
function cuboid(c, u, v, w, fills, edge = '') {
  const P = (a, b, d) => add(add(add(c, u, a), v, b), w, d);
  const faces = [[u, [P(1, 1, 1), P(1, 1, -1), P(1, -1, -1), P(1, -1, 1)]], [u, [P(-1, 1, 1), P(-1, 1, -1), P(-1, -1, -1), P(-1, -1, 1)], -1],
    [v, [P(1, 1, 1), P(1, 1, -1), P(-1, 1, -1), P(-1, 1, 1)]], [v, [P(1, -1, 1), P(1, -1, -1), P(-1, -1, -1), P(-1, -1, 1)], -1],
    [w, [P(1, 1, 1), P(1, -1, 1), P(-1, -1, 1), P(-1, 1, 1)]], [w, [P(1, 1, -1), P(1, -1, -1), P(-1, -1, -1), P(-1, 1, -1)], -1]];
  return faces.map(([axis, q, sign = 1]) => { const n = norm({ x: axis.x * sign, z: axis.z * sign, h: (axis.h || 0) * sign }); return { n, q }; })
    .filter(f => dot(f.n, TOWARD_VIEWER) > 1e-6)
    .map(f => { const lit = -dot(f.n, LIGHT_DIR); return poly(f.q, `fill="${f.n.h > 0.6 ? fills.top : lit > 0.15 ? fills.light : fills.dark}" ${edge}`); }).join('');
}
function corners(c, u, v, w) { const out = []; for (const a of [-1, 1]) for (const b of [-1, 1]) for (const d of [-1, 1]) out.push(add(add(add(c, u, a), v, b), w, d)); return out; }
function hull(points) {
  const p = points.map(q => [q.x, q.y]).sort((a, b) => a[0] - b[0] || a[1] - b[1]), cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lower = [], upper = [];
  for (const q of p) { while (lower.length > 1 && cr(lower.at(-2), lower.at(-1), q) <= 0) lower.pop(); lower.push(q); }
  for (const q of p.reverse()) { while (upper.length > 1 && cr(upper.at(-2), upper.at(-1), q) <= 0) upper.pop(); upper.push(q); }
  return lower.slice(0, -1).concat(upper.slice(0, -1));
}
// Shadow of a set of boxes on the horizontal plane h = plane, along the key light. Parts below the plane cast nothing on it.
function shadowOn(boxes, plane) {
  return boxes.map(b => {
    const pts = corners(b.c, b.u, b.v, b.w).map(p => { const q = { ...p, h: Math.max(p.h, plane) }, t = (plane - q.h) / LIGHT_DIR.h; return proj(add(q, LIGHT_DIR, t)); });
    return `<polygon points="${hull(pts).map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' ')}"/>`;
  }).join('');
}
function segmentBox(a, b, t, fills) {
  const c = { x: (a.x + b.x) / 2, z: (a.z + b.z) / 2, h: (a.h + b.h) / 2 }, u = { x: (b.x - a.x) / 2, z: (b.z - a.z) / 2, h: (b.h - a.h) / 2 };
  const along = norm(u), side = Math.abs(along.h) > 0.95 ? { x: 1, z: 0, h: 0 } : norm(cross(along, { x: 0, z: 0, h: 1 })), up = norm(cross(side, along));
  return { c, u, v: { x: side.x * t / 2, z: side.z * t / 2, h: side.h * t / 2 }, w: { x: up.x * t / 2, z: up.z * t / 2, h: up.h * t / 2 }, fills };
}
function figureBoxes(pose, you, facing) {
  const f = norm(facing), s = { x: -f.z, z: f.x, h: 0 }, F = { x: you.x, z: you.z, h: MM.floor };
  const L = (fwd, side, h) => ({ x: F.x + f.x * fwd + s.x * side, z: F.z + f.z * fwd + s.z * side, h: F.h + h });
  const box = (fwd, side, h, lf, ls, lh, fills = FIG) => ({ c: L(fwd, side, h), u: { x: f.x * lf / 2, z: f.z * lf / 2, h: 0 }, v: { x: s.x * ls / 2, z: s.z * ls / 2, h: 0 }, w: { x: 0, z: 0, h: lh / 2 }, fills });
  const boxes = [box(0, -72, 235, 120, 95, 470), box(0, 72, 235, 120, 95, 470), box(0, 0, 640, 170, 310, 330), box(10, 0, 925, 175, 165, 180)];
  const hands = { observe: [[40, -205, 420], [40, 205, 420]], adjust: [[470, -110, 830], [470, 110, 830]], measure: [[40, -205, 420], [330, 115, 720]], manual: [[300, -95, 640], [300, 95, 640]], buy: [[40, -205, 420], [60, 225, 1180]] }[pose] || [[40, -205, 420], [40, 205, 420]];
  hands.forEach(([hf, hs, hh], i) => {
    const sh = L(0, i ? 172 : -172, 770), hand = L(hf, hs, hh), out = i ? 1 : -1;
    const elbow = add(L((hf) * .45, (hs * .5 + out * 190 * .5), (770 + hh) / 2 - 70), { x: 0, z: 0, h: 0 });
    boxes.push(segmentBox(sh, elbow, 82, FIG), segmentBox(elbow, hand, 70, FIG));
  });
  if (pose === 'manual') boxes.push(box(330, 0, 650, 150, 210, 36, PROP));
  if (pose === 'measure') boxes.push(box(360, 115, 735, 14, 150, 105, PROP));
  if (pose === 'buy') boxes.push(box(70, 225, 1260, 14, 120, 120, PROP));
  return boxes;
}
const FIG = { top: C.figTop, light: C.fig, dark: C.figDark };
const PROP = { top: '#F09A55', light: C.orange, dark: '#B9561A' };
function figureSvg(boxes) {
  const edge = `stroke="${C.ink}" stroke-width=".8" stroke-linejoin="round"`;
  return boxes.slice().sort((a, b) => depth(a.c) - depth(b.c)).map(b => cuboid(b.c, b.u, b.v, b.w, b.fills, edge)).join('');
}
function facingFor(pose, you, target) {
  if (you.at_desk) return { x: -1, z: 0, h: 0 };
  if (target && (pose === 'adjust' || pose === 'measure')) { const d = { x: target.x - you.x, z: target.z - you.z, h: 0 }; if (Math.hypot(d.x, d.z) > 1) return d; }
  return you.z < 0 ? { x: 0, z: 1, h: 0 } : you.z > MM.table.z ? { x: 0, z: -1, h: 0 } : { x: you.x < 0 ? 1 : -1, z: 0, h: 0 };
}
function headlineText(call, action) { return [action.verb.toUpperCase(), `${cleanTool(call.tool)}${Object.keys(call.args || {}).length ? ' · ' + shortArgs(call.args) : ''}`.toUpperCase()]; }
// Size the drawing to the real pane so the table never letterboxes; the poster headline takes a fixed band at the bottom.
function layoutScene(call, action) {
  const shell = app.querySelector('.scene-shell'), w = Math.max(320, shell?.clientWidth || innerWidth), h = Math.max(300, shell?.clientHeight || innerHeight);
  const [first, detail] = headlineText(call, action), room = w - 80, fitSize = (text, max) => Math.min(max, room / (Math.max(text.length, 8) * 0.42));
  const big = fitSize(first, Math.min(46, w * .036)), small = fitSize(detail, Math.min(24, w * .019)), line2 = h - 72, line1 = line2 - small - 8;
  Object.assign(SCENE, { w, h, big, small, line1, line2, fit: { x0: 24, y0: w < 700 ? 64 : 104, x1: w - 96, y1: line1 - big - 4 } });
}
function headline(call, action) {
  const [first, detail] = headlineText(call, action), x = SCENE.w - 40;
  return `<text x="${x}" y="${SCENE.line1.toFixed(0)}" text-anchor="end" class="sc-big" style="font-size:${SCENE.big.toFixed(0)}px;fill:${C.paper}" opacity=".82">${esc(first)}</text>
    <text x="${x}" y="${SCENE.line2.toFixed(0)}" text-anchor="end" class="sc-big sc-detail" style="font-size:${SCENE.small.toFixed(0)}px;fill:${C.orange}">${esc(detail)}</text>`;
}
function shortId(id) { return String(id).replace(/^mirror-/, 'M').replace(/^periscope-/, 'P').toUpperCase(); }
function partLabel(part) {
  const top = part.kind === 'periscope' ? (part.h_in ?? part.pos.h) + 30 : part.pos.h + (part.kind === 'sample' ? 34 : 26), q = proj({ ...part.pos, h: top });
  return `<text x="${q.x.toFixed(1)}" y="${(q.y - 6).toFixed(1)}" text-anchor="middle" class="sc-part">${esc(shortId(part.id))}</text>`;
}
function sceneSvg(call) {
  const run = currentRun(), meta = run?.meta || {}, snap = call.snapshot || {}, parts = snap.parts || [], beams = snap.beams || {}, action = contextFor(call);
  layoutScene(call, action); fitScene(meta);
  const table = tableSvg(), hit = BEAMS.every(([key]) => beams[key]?.open && beams[key]?.end === 'sample');
  const labels = [], objects = parts.map(part => ({ d: depth(part.pos), svg: part.kind === 'mirror' ? mirrorSvg(part) : part.kind === 'stage' ? stageSvg(part) : part.kind === 'periscope' ? periscopeSvg(part) : part.kind === 'sample' ? sampleSvg(part, hit) : '' }));
  (meta.housings_mm || []).forEach((box, i) => { const [key, color, label] = BEAMS[i === 0 ? 0 : 1]; const h = housingSvg(box, meta.ports?.[key], label, color); labels.push(h.label); objects.push({ d: depth({ x: box.x0, z: (box.z0 + box.z1) / 2 }), svg: h.body }); });
  objects.sort((a, b) => a.d - b.d); parts.forEach(part => labels.push(partLabel(part)));
  const beamSvg = BEAMS.map(([key, color]) => beams[key]?.open ? (beams[key].segments || []).map(([a, b]) => line(a, b, `stroke="${C.ink}" stroke-width="6" stroke-linecap="round" opacity=".7"`) + line(a, b, `stroke="${color}" stroke-width="3.2" stroke-linecap="round"`)).join('') : '').join('');
  const beamShadow = BEAMS.map(([key]) => beams[key]?.open ? (beams[key].segments || []).map(([a, b]) => line({ ...a, h: 0 }, { ...b, h: 0 }, `stroke="${C.ink}" stroke-width="1.6" opacity=".22"`)).join('') : '').join('');
  const target = actionCoordinates(call), targetPart = parts.find(p => target && p.pos.x === target.x && p.pos.z === target.z);
  const marker = target ? (() => {
    const g = { x: target.x, z: target.z, h: 0 }, q = proj(g), left = q.x > SCENE.w * .62, bx = left ? q.x - 196 : q.x + 30;
    const lift = targetPart ? line(g, { ...g, h: targetPart.pos.h }, `stroke="${C.orange}" stroke-width="1.4" stroke-dasharray="4 3"`) : '';
    return disc(g, { x: 0, z: 0, h: 1 }, 48, `fill="none" stroke="${C.orange}" stroke-width="2.4"`) + line(add(g, { x: 1, z: 0 }, -80), add(g, { x: 1, z: 0 }, 80), `stroke="${C.orange}" stroke-width="1.4"`) + line(add(g, { x: 0, z: 1 }, -80), add(g, { x: 0, z: 1 }, 80), `stroke="${C.orange}" stroke-width="1.4"`) + lift
      + `<rect x="${bx.toFixed(1)}" y="${(q.y - 44).toFixed(1)}" width="166" height="26" fill="${C.ink}"/><text x="${(bx + 10).toFixed(1)}" y="${(q.y - 25).toFixed(1)}" class="sc-coord">X ${Math.round(target.x)} · Z ${Math.round(target.z)} MM</text>`;
  })() : '';
  const you = snap.you_mm || meta.desk_mm || { x: -300, z: 600 }, behind = depth({ x: you.x, z: you.z, h: 0 }) < depth({ x: MM.table.x / 2, z: MM.table.z / 2, h: 0 }), front = !behind;
  const tx = proj(targetPart?.pos || target || { x: 1200, z: 600 }).x, figBoxes = figureBoxes(action.pose, you, facingFor(action.pose, you, targetPart?.pos || target)), figure = figureSvg(figBoxes);
  const topClip = `<clipPath id="tableTop">${poly([{ x: 0, z: 0, h: 0 }, { x: MM.table.x, z: 0, h: 0 }, { x: MM.table.x, z: MM.table.z, h: 0 }, { x: 0, z: MM.table.z, h: 0 }], '')}</clipPath>`;
  const figShadowFloor = `<g fill="${C.floor}" opacity=".6">${shadowOn(figBoxes, MM.floor)}</g>`, figShadowTable = `${topClip}<g clip-path="url(#tableTop)" fill="${C.ink}" opacity=".26">${shadowOn(figBoxes, 0)}</g>`;
  const deskAt = meta.desk_mm || { x: -300, z: 600 }, deskBehind = depth({ x: deskAt.x - 260, z: deskAt.z, h: 0 }) < depth({ x: MM.table.x / 2, z: MM.table.z / 2, h: 0 }), desk = deskSvg(meta);
  return `<svg viewBox="0 0 ${SCENE.w} ${SCENE.h}" preserveAspectRatio="xMidYMid slice" role="img" aria-label="Optical table in millimetre-true projection, with the worker beside it">
    <rect width="${SCENE.w}" height="${SCENE.h}" fill="${C.room}"/>
    ${figShadowFloor}${deskBehind ? desk : ''}${behind ? figure : ''}${table.under}${table.slab}${figShadowTable}${table.ticks}${beamShadow}
    ${objects.map(o => o.svg).join('')}${beamSvg}${labels.join('')}${marker}
    ${deskBehind ? '' : desk}${behind ? '' : figure}${headline(call, action)}
  </svg>`;
}
function mapSvg(call) {
  const snap = call.snapshot || {}, parts = snap.parts || [], beams = snap.beams || {};
  const sx = x => 15 + x / 2400 * 300, sz = z => 10 + z / 1200 * 150;
  const beam = BEAMS.map(([key, color]) => beams[key]?.open ? (beams[key].segments || []).map(seg => `<path d="M${sx(seg[0].x)},${sz(seg[0].z)} L${sx(seg[1].x)},${sz(seg[1].z)}" stroke="${color}" stroke-width="2.4" stroke-linecap="round"/>`).join('') : '').join('');
  const houses = (currentRun()?.meta?.housings_mm || []).map(b => `<rect x="${sx(b.x0)}" y="${sz(b.z0)}" width="${sx(b.x1) - sx(b.x0)}" height="${sz(b.z1) - sz(b.z0)}" fill="${C.kraft}"/>`).join('');
  return `<svg class="map-svg" viewBox="0 0 330 170" role="img" aria-label="Top down layout of the optical table"><defs><pattern id="mapHoles" width="${300 / 24}" height="${150 / 12}" patternUnits="userSpaceOnUse" x="15" y="10"><circle cx="${150 / 24}" cy="${75 / 12}" r=".9" fill="${C.ink}" opacity=".35"/></pattern></defs><rect x="15" y="10" width="300" height="150" fill="${C.paper}"/><rect x="15" y="10" width="300" height="150" fill="url(#mapHoles)"/>${houses}${beam}${parts.map(p => `<g><circle cx="${sx(p.pos.x)}" cy="${sz(p.pos.z)}" r="4" fill="${C.ink}"/><title>${esc(p.id)}</title></g>`).join('')}</svg>`;
}
function scoreSvg(run, step) {
  const trajectory = run.trajectory, end = Math.max(1, step), values = trajectory.slice(0, end + 1).map(t => Math.max(0, Math.min(1, Number(t.truth?.reward || 0))));
  const path = values.map((v, i) => `${i ? 'L' : 'M'}${(i / Math.max(end, 1) * 270).toFixed(1)},${(32 - v * 29).toFixed(1)}`).join(' ');
  return `<svg class="graph" viewBox="0 0 270 34" preserveAspectRatio="none" aria-label="Score history"><path d="M0 32 H270" stroke="var(--line)"/><path d="${path}" fill="none" stroke="#16120F" stroke-width="2.4" vector-effect="non-scaling-stroke"/></svg>`;
}
// ---- Score breakdown: the grader in sim/reward.py, recomputed from the replay's diagnostic truth at this step. ----
// reward = 0.2 x spatial + 0.5 x timing + 0.3 efficiency (efficiency only once timing >= 0.9).
// spatial = T_800 x T_opa x O; timing = eta = T_800 x T_opa x O x exp(-(dt / tau)^2).
const GRADER = { spatial: 0.2, timing: 0.5, alpha: 0.2, beta: 0.1, success: 0.9, tau: { 1: 70.04, 2: 186.21 }, mmPerFs: 0.000299792458 };
function fmtDt(fs) { const a = Math.abs(fs); return a >= 1000 ? `${(a / 1000).toFixed(1)} ps` : `${Math.round(a)} fs`; }
function endName(end) { return end === 'sample' ? 'the sample' : String(end || 'nowhere').replace(/^mount of /, 'the mount of ').replace(/^lens mount$/, 'the lens mount'); }
function breakdown(run, call) {
  const t = call.truth || {}, meta = run.meta || {}, level = meta.level || 1, T8 = t.T_800 || 0, To = t.T_opa || 0, O = t.O || 0, eta = Math.max(0, Math.min(1, t.eta || 0));
  const spatial = GRADER.spatial * Math.max(0, Math.min(1, T8 * To * O)), timing = GRADER.timing * eta, success = eta >= GRADER.success;
  const cap = meta.spend_cap_eur || 30000, cmin = meta.c_min_eur || 0, costFrac = Math.max(0, Math.min(1, ((call.snapshot?.cost_eur || 0) - cmin) / (cap - cmin))), timeFrac = Math.max(0, Math.min(1, (call.t_s || 0) / (meta.budget_s || 14400)));
  const efficiency = success ? GRADER.alpha * (1 - costFrac) + GRADER.beta * (1 - timeFrac) : 0, total = Math.min(1, spatial + timing + efficiency);
  const tau = GRADER.tau[level] || GRADER.tau[1], reach = T8 * To * O, window = reach > GRADER.success ? tau * Math.sqrt(Math.log(reach / GRADER.success)) : null;
  const isFinal = call.tool === 'submit' || state.step === run.trajectory.length - 1, recorded = Number(t.reward ?? total);
  let reason;
  if (!(t.end_800 === 'sample' && t.end_opa === 'sample')) reason = t.end_800 !== 'sample' ? `800 nm beam ends at ${endName(t.end_800)}` : `OPA beam ends at ${endName(t.end_opa)}`;
  else if (O < 0.5) reason = `Spots miss each other at the sample (overlap ${(O * 100).toFixed(0)}%)`;
  else if (!success && Number.isFinite(t.dt_fs)) reason = `Spots overlap, but the pulses arrive ${fmtDt(t.dt_fs)} apart (${(Math.abs(t.dt_fs) * GRADER.mmPerFs).toFixed(2)} mm of path). Needs ${window ? `≤ ${Math.round(window)} fs` : 'better overlap first'}.`;
  else if (!success) reason = 'Spots overlap, but the timing has not been measured';
  else reason = `Pulses meet in space and time (Δt ${fmtDt(t.dt_fs)})`;
  const verdict = success ? (isFinal ? 'Passed' : 'Working') : isFinal ? 'Failed' : 'Not yet';
  const row = (label, weight, value, points, note) => `<div class="bd-row"><span class="bd-label">${label} <em>×${weight.toFixed(1)}</em></span><span class="bd-value">${note}</span><span class="bd-bar"><i style="width:${(points / weight * 100).toFixed(1)}%"></i></span><strong>${points.toFixed(2)}</strong></div>`;
  const legacy = isFinal && Math.abs(recorded - total) > 0.005 ? `<p class="bd-note">Recorded score ${recorded.toFixed(3)} came from an earlier grader. Today's grader gives ${total.toFixed(3)}.</p>` : '';
  return `<div class="bd-head"><span class="bd-verdict ${success ? 'ok' : isFinal ? 'bad' : ''}">${verdict}</span>${run.old_scorer ? '<span class="bd-old" title="This run was graded by an earlier version of the scorer">Old scorer</span>' : ''}<span class="bd-total">${(isFinal ? recorded : total).toFixed(3)}</span></div>
    <p class="bd-reason">${esc(reason)}</p>
    ${row('Spot overlap', GRADER.spatial, O, spatial, `${(O * 100).toFixed(1)}%${T8 * To < 0.99 ? ` · T ${(T8 * To * 100).toFixed(0)}%` : ''}`)}
    ${row('Timing', GRADER.timing, eta, timing, Number.isFinite(t.dt_fs) ? `Δt ${fmtDt(t.dt_fs)}` : 'no overlap')}
    ${row('Efficiency', 0.3, efficiency, efficiency, success ? `cost ${Math.round((1 - costFrac) * 100)}% · time ${Math.round((1 - timeFrac) * 100)}%` : 'locked until timing ≥ 0.9')}${legacy}`;
}
function runName(run, index) { return `Run ${index + 1} · ${run.model} · seed ${run.meta.seed} · L${run.meta.level} · R ${Number(run.diagnostics?.reward || 0).toFixed(3)}${run.old_scorer ? ' (old scorer)' : ''}`; }
function groupCalls(trajectory) {
  const groups = []; let setup = null;
  trajectory.forEach((call, index) => {
    let phase;
    if (call.tool === 'place') { setup = `Set up ${call.args?.part || 'optic'}`; phase = setup; }
    else if (/read_manual|get_datasheet|list_catalogue/.test(call.tool)) { setup = null; phase = 'Read manuals'; }
    else if (call.tool === 'buy') { setup = null; phase = 'Purchase parts'; }
    else if (/scan|move_stage|measure_path|read_signal/.test(call.tool)) { setup = null; phase = 'Timing and signals'; }
    else if (call.tool === 'submit') { setup = null; phase = 'Submit'; }
    else if (call.tool === 'status') phase = setup || groups.at(-1)?.phase || 'Status';
    else phase = setup || 'Alignment checks';
    const last = groups.at(-1);
    if (last?.phase === phase && call.tool !== 'place') last.end = index;
    else groups.push({ phase, start: index, end: index });
  });
  return groups;
}
function stepsMarkup(trajectory) {
  return groupCalls(trajectory).map(group => {
    const active = state.step >= group.start && state.step <= group.end;
    const count = group.end - group.start + 1, open = state.expanded.has(group.start);
    const heading = `<button class="phase-row ${active ? 'active' : ''}" ${count === 1 ? `data-step="${group.start}"` : `data-group="${group.start}" aria-expanded="${open}"`}><span class="phase-name">${esc(group.phase)}</span><span class="phase-count">${count > 1 ? `${count} calls` : String(group.start + 1).padStart(3, '0')}</span><span class="phase-arrow">${count > 1 ? open ? '⌄' : '›' : ''}</span></button>`;
    if (!open || count === 1) return heading;
    const calls = trajectory.slice(group.start, group.end + 1).map((call, offset) => {
      const index = group.start + offset;
      return `<button class="call-row child ${index === state.step ? 'active' : ''}" data-step="${index}" aria-current="${index === state.step ? 'step' : 'false'}"><span class="number">${String(index + 1).padStart(3, '0')}</span><span class="summary">${esc(cleanTool(call.tool))}${Object.keys(call.args || {}).length ? ` · ${esc(shortArgs(call.args))}` : ''}</span><span class="mark">${call.result?.error ? '!' : index === state.step ? '●' : ''}</span></button>`;
    }).join('');
    return heading + calls;
  }).join('');
}
function menuMarkup(call) {
  if (state.menu === 'run') return `<div class="flyout run-flyout" role="menu" aria-label="Run"><div class="flyout-title">Run</div>${runs.map((run, i) => `<button class="flyout-item" role="menuitem" tabindex="${i === 0 ? 0 : -1}" data-run="${i}"><span class="mini-icon">${i === state.run ? '●' : '○'}</span><span>${esc(runName(run, i))}</span></button>`).join('')}</div>`;
  if (state.menu === 'speed') return `<div class="flyout speed-flyout" role="menu" aria-label="Speed"><div class="flyout-title">Speed</div>${[1, 2, 4].map((speed, i) => `<button class="flyout-item" role="menuitem" tabindex="${i === 0 ? 0 : -1}" data-speed="${speed}"><span class="mini-icon">${speed === state.speed ? '●' : '○'}</span><span>${speed}×</span></button>`).join('')}</div>`;
  if (state.menu === 'parts') {
    const parts = call.snapshot?.parts || [];
    return `<div class="flyout parts-flyout" role="menu" aria-label="Parts"><div class="flyout-title">Parts · ${parts.length}</div>${parts.map((part, i) => `<button class="flyout-item" role="menuitem" tabindex="${i === 0 ? 0 : -1}" data-part="${esc(part.id)}"><span class="mini-icon">${part.id === state.selectedPart ? '●' : part.kind === 'mirror' ? '◉' : part.kind === 'stage' ? '▤' : '◇'}</span><span>${esc(part.id)}</span></button>`).join('')}</div>`;
  }
  if (state.menu === 'view') return `<div class="flyout view-flyout" role="menu" aria-label="View"><div class="flyout-title">Top view</div><button class="flyout-item" role="menuitem" tabindex="0" data-action="reset-view"><span class="mini-icon">▣</span><span>Reset camera</span></button>${mapSvg(call)}</div>`;
  return '';
}
function render() {
  const run = currentRun(), call = currentCall(); if (!run || !call) { app.textContent = 'No run snapshots found.'; return; }
  const trajectory = run.trajectory, score = Number(call.truth?.reward || 0);
  app.innerHTML = `<main class="app ${state.railOpen ? '' : 'rail-closed'}">
    <section class="scene-shell"><div class="scene">${sceneSvg(call)}</div></section>
    <div class="player" aria-label="Playback">
      <button class="run-trigger" data-action="run" aria-label="Choose run" aria-expanded="${state.menu === 'run'}" aria-haspopup="menu">▤</button><span class="run-label">${esc(runName(run, state.run))}</span>
      <button data-action="prev" aria-label="Previous step" title="← or ,">‹</button><button data-action="play" aria-label="${state.playing ? 'Pause' : 'Play'}" aria-pressed="${state.playing}" title="Space">${state.playing ? 'Ⅱ' : '▶'}</button><button data-action="next" aria-label="Next step" title="→ or .">›</button>
      <input class="scrub" type="range" min="0" max="${trajectory.length-1}" value="${state.step}" aria-label="Scrub steps"><span class="counter">${state.step+1}/${trajectory.length}</span><button data-action="speed" aria-label="Playback speed" aria-expanded="${state.menu === 'speed'}" aria-haspopup="menu">${state.speed}×</button>
    </div>
    <aside class="sidebar"><section class="call-panel"><div class="panel-heading">Steps <small>${trajectory.length} calls</small></div><div class="current-call">${state.step + 1}/${trajectory.length} · ${esc(cleanTool(call.tool))}${Object.keys(call.args || {}).length ? ` · ${esc(shortArgs(call.args))}` : ''}</div><div class="call-stack">${stepsMarkup(trajectory)}</div></section>
      <section class="score-panel"><div class="totals"><div><span>Money</span><strong>${money(call.snapshot?.cost_eur)}</strong><small>of ${money(run.meta.spend_cap_eur)}</small></div><div><span>Lab time</span><strong>${fmtTime(call.t_s)}</strong><small>of ${fmtTime(run.meta.budget_s)}</small></div></div><div class="breakdown">${breakdown(run, call)}</div>${scoreSvg(run,state.step)}</section></aside>
    <button class="rail-toggle" data-action="rail" aria-label="${state.railOpen ? 'Hide steps' : 'Show steps'}" title="${state.railOpen ? 'Hide steps' : 'Show steps'}">${state.railOpen ? '‹' : '›'}</button>
    <button class="corner-button parts-trigger" data-action="parts" aria-label="Parts" aria-expanded="${state.menu === 'parts'}" aria-haspopup="menu">≡</button><span class="hint">Parts</span>
    <button class="corner-button view-trigger" data-action="view" aria-label="View" aria-expanded="${state.menu === 'view'}" aria-haspopup="menu">▣</button><span class="view-hint">View</span>
    <div class="shortcut-hints">Space play · ← → step · drag orbit · shift-drag pan · scroll zoom · double-click reset</div>${menuMarkup(call)}</main>`;
  const active = app.querySelector('.phase-row.active'), stack = app.querySelector('.call-stack');
  if (active && stack) { const top = active.offsetTop - stack.offsetTop, bottom = top + active.offsetHeight; if (top < stack.scrollTop) stack.scrollTop = top; else if (bottom > stack.scrollTop + stack.clientHeight) stack.scrollTop = bottom - stack.clientHeight; }
}
function changeStep(next) { const max = currentRun().trajectory.length - 1; state.step = Math.max(0, Math.min(max, next)); state.selectedPart = null; if (state.step === max && state.playing) stop(); render(); }
function stop() { state.playing = false; clearInterval(state.timer); state.timer = null; }
function togglePlay() { if (state.playing) { stop(); render(); return; } if (state.step >= currentRun().trajectory.length - 1) state.step = 0; state.playing = true; state.timer = setInterval(() => changeStep(state.step + 1), 720 / state.speed); render(); }
function setMenu(menu) { state.menu = state.menu === menu ? null : menu; render(); if (state.menu) app.querySelector('.flyout-item')?.focus(); else app.querySelector(`[data-action="${menu}"]`)?.focus(); }
app.addEventListener('click', e => {
  const button = e.target.closest('button'); if (!button) return;
  if (button.dataset.step !== undefined) { changeStep(Number(button.dataset.step)); return; }
  if (button.dataset.group !== undefined) { const id = Number(button.dataset.group); state.expanded.has(id) ? state.expanded.delete(id) : state.expanded.add(id); render(); app.querySelector(`[data-group="${id}"]`)?.focus(); return; }
  if (button.dataset.part !== undefined) { state.selectedPart = button.dataset.part; state.menu = null; render(); return; }
  if (button.dataset.run !== undefined) { stop(); state.run = Number(button.dataset.run); state.step = currentRun().trajectory.length - 2; state.selectedPart = null; state.expanded.clear(); state.menu = null; render(); return; }
  if (button.dataset.speed !== undefined) { const wasPlaying = state.playing; stop(); state.speed = Number(button.dataset.speed); state.menu = null; wasPlaying ? togglePlay() : render(); return; }
  switch (button.dataset.action) {
    case 'prev': changeStep(state.step - 1); break;
    case 'play': togglePlay(); break;
    case 'next': changeStep(state.step + 1); break;
    case 'run': setMenu('run'); break;
    case 'speed': setMenu('speed'); break;
    case 'parts': setMenu('parts'); break;
    case 'view': setMenu('view'); break;
    case 'rail': state.railOpen = !state.railOpen; state.menu = null; render(); break;
    case 'close-menu': setMenu(state.menu); break;
    case 'reset-view': state.cam = { ...DEFAULT_CAM }; state.menu = null; render(); break;
  }
});
app.addEventListener('change', e => { if (e.target.matches('input[type=range]')) changeStep(Number(e.target.value)); });
document.addEventListener('pointerdown', e => { if (state.menu && !e.target.closest('.flyout,[aria-haspopup="menu"]')) { const menu = state.menu; state.menu = null; render(); app.querySelector(`[data-action="${menu}"]`)?.focus(); } });
document.addEventListener('keydown', e => {
  if (state.menu && e.key === 'Escape') { e.preventDefault(); setMenu(state.menu); return; }
  const items = [...app.querySelectorAll('.flyout-item')];
  if (state.menu && items.length && ['ArrowDown','ArrowUp','ArrowLeft','ArrowRight','Home','End'].includes(e.key)) {
    e.preventDefault(); const current = items.indexOf(document.activeElement);
    const next = e.key === 'Home' ? 0 : e.key === 'End' ? items.length - 1 : (current + (e.key === 'ArrowDown' || e.key === 'ArrowRight' ? 1 : -1) + items.length) % items.length;
    items.forEach((item, i) => item.tabIndex = i === next ? 0 : -1); items[next].focus(); return;
  }
  if (state.menu && (e.key === ' ' || e.key === 'Enter')) return;
  if (/INPUT|TEXTAREA|SELECT/.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable) return;
  if (e.key === 'Escape') { state.menu = null; render(); return; }
  if (e.key === 'ArrowLeft' || e.key === ',') changeStep(state.step - 1);
  if (e.key === 'ArrowRight' || e.key === '.') changeStep(state.step + 1);
  if (e.key === ' ') { e.preventDefault(); togglePlay(); }
});
let sceneFrame = 0, drag = null;
function redrawScene() { if (sceneFrame) return; sceneFrame = requestAnimationFrame(() => { sceneFrame = 0; const el = app.querySelector('.scene'), call = currentCall(); if (el && call) el.innerHTML = sceneSvg(call); }); }
app.addEventListener('pointerdown', e => { if (e.button !== 0 || !e.target.closest('.scene')) return; drag = { x: e.clientX, y: e.clientY, pan: e.shiftKey, id: e.pointerId }; e.target.closest('.scene').setPointerCapture(e.pointerId); });
app.addEventListener('pointermove', e => {
  if (!drag || e.pointerId !== drag.id) return;
  const dx = e.clientX - drag.x, dy = e.clientY - drag.y, cam = state.cam; drag.x = e.clientX; drag.y = e.clientY;
  if (drag.pan) { cam.panX += dx; cam.panY += dy; } else { cam.yaw = clamp(cam.yaw - dx * 0.3, CAM_LIMITS.yaw); cam.pitch = clamp(cam.pitch + dy * 0.25, CAM_LIMITS.pitch); }
  redrawScene();
});
app.addEventListener('pointerup', () => { drag = null; });
app.addEventListener('pointercancel', () => { drag = null; });
app.addEventListener('wheel', e => {
  const scene = e.target.closest('.scene'); if (!scene) return; e.preventDefault();
  const cam = state.cam, rect = scene.getBoundingClientRect(), mx = e.clientX - rect.left - rect.width / 2, my = e.clientY - rect.top - rect.height / 2;
  const next = clamp(cam.zoom * Math.exp(-e.deltaY * 0.0015), CAM_LIMITS.zoom), ratio = next / cam.zoom;
  cam.panX = mx - (mx - cam.panX) * ratio; cam.panY = my - (my - cam.panY) * ratio; cam.zoom = next; redrawScene();
}, { passive: false });
app.addEventListener('dblclick', e => { if (e.target.closest('.scene')) { state.cam = { ...DEFAULT_CAM }; redrawScene(); } });
addEventListener('resize', () => render());
render();
render(); // second pass sizes the drawing to the scene pane that the first pass created
