"""GSS pitch video v2: animated lab shots and deck posters, cut to an original score (music.py).

Everything is rendered frame by frame in headless Chromium:
- lab shots: the 3D viewer stepped through real recorded runs, with an animated camera;
- poster shots: the deck's posters with their own entrance animations, slow push-ins and beat pulses;
- words: a few cut-paper labels inside the picture (pinned to real table positions in lab shots, so they
  move with the camera), slammed in on the beat.

Run from the repo root, with the viewer served (uv run python scripts/serve_viewer.py) and score.wav built:
    uv run --no-project --with playwright --with pillow --with imageio-ffmpeg python video/v2/render.py [--preview]
Writes video/v2/gss_pitch_v2.mp4 (1:56, 1920x1080, 30 fps, with the score). --preview writes key frames only.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import os
import subprocess

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DECK = "file://" + os.path.join(ROOT, "pitch-deck.html")
VIEWER = "http://localhost:8766/prototype.html"
FPS = 30
W, H = 1920, 1080
BPM = 100.0
BEAT = 60.0 / BPM
BAR = 4 * BEAT
TOTAL = 48 * BAR + 0.8  # 116.0 s
INK = (22, 18, 15)
CREAM = (237, 227, 204)

CLAUDE = "2026-11-15__04-15-09/gss-blind-l2s3__p2"
FLASH = "2026-11-14__18-19-55/gss__5MASNh3"


def tb(bar: float) -> float:
    """1-based bar (fractions allowed) -> seconds."""
    return (bar - 1) * BAR


def ease(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def ease_out(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return 1 - (1 - u) ** 3


def lerp(a, b, u):
    return a + (b - a) * u


def keyframes(kf, t):
    """kf: list of (t, dict). Smooth interpolation of numeric fields."""
    if t <= kf[0][0]:
        return dict(kf[0][1])
    for (t0, a), (t1, b) in zip(kf, kf[1:]):
        if t <= t1:
            u = ease((t - t0) / max(1e-6, t1 - t0))
            return {k: lerp(a[k], b.get(k, a[k]), u) if isinstance(a[k], (int, float)) else a[k] for k in a}
    return dict(kf[-1][1])


# ------------------------------------------------------------------------------------------ words
# A word: (bar_in, bar_out, text, style, size, placement). Placement for lab shots:
#   ("anchor", target, dx, dy)   target = "sample" | "stage" | "agent" | "housings" | "table" | (x, z, h)
# and for posters: ("fixed", x, y). Styles: tag (cream paper), strip (orange), ink (dark), alert (dark/orange).
# Rotation is a small fixed tilt per word, like pasted paper.

SHOTS = [
    # kind, first bar, bars, spec
    ("poster", 1, 3, dict(slide=1, zoom=(1.0, 1.07), focus=(0.62, 0.45), words=[])),
    ("lab", 4, 3, dict(run=CLAUDE, steps=[(0, 0)], cam=[(0, dict(yaw=-62, pitch=22, zoom=1.9, tx=1200, tz=600, th=0)),
                                                        (7.2, dict(yaw=-18, pitch=40, zoom=1.05, tx=1150, tz=600, th=0))],
                       words=[(4.5, 7, "EMPTY TABLE.", "tag", 120, ("anchor", (1200, 600, 0), -380, -300)),
                              (5.5, 7, "TWO LASERS.", "strip", 96, ("anchor", "housings", -300, -150))])),
    ("poster", 7, 2, dict(slide=3, zoom=(1.02, 1.12), focus=(0.62, 0.42), words=[])),
    ("poster", 9, 2, dict(slide=4, zoom=(1.08, 1.0), focus=(0.6, 0.4),
                          words=[(9.5, 11, "NO PEEKING.", "strip", 92, ("fixed", 1560, 900))])),
    ("lab", 11, 2, dict(run=CLAUDE, steps=[(0, 0), (4.8, 31)],
                        cam=[(0, dict(yaw=-20, pitch=30, zoom=1.7, tx=300, tz=600, th=300)),
                             (4.8, dict(yaw=-30, pitch=36, zoom=1.3, tx=800, tz=600, th=150))],
                        words=[(11.0, 13, "BLIND.", "tag", 130, ("fixed", 560, 240))])),
    ("lab", 13, 2, dict(run=CLAUDE, steps=[(0, 31), (4.8, 40)],
                        cam=[(0, dict(yaw=-30, pitch=58, zoom=1.25, tx=1300, tz=500, th=0)),
                             (4.8, dict(yaw=-10, pitch=52, zoom=1.45, tx=1350, tz=500, th=0))],
                        words=[(13.25, 15, "BUILD.", "tag", 120, ("anchor", (1400, 380, 160), 120, -330))])),
    ("lab", 15, 2, dict(run=CLAUDE, steps=[(0, 40), (4.8, 58)],
                        cam=[(0, dict(yaw=12, pitch=20, zoom=2.2, tx=1350, tz=600, th=120)),
                             (4.8, dict(yaw=-2, pitch=26, zoom=1.9, tx=1250, tz=600, th=120))],
                        words=[(15.25, 17, "ALIGN.", "strip", 120, ("anchor", "sample", -420, -320))])),
    ("lab", 17, 2, dict(run=CLAUDE, steps=[(0, 58), (4.8, 125)],
                        cam=[(0, dict(yaw=-14, pitch=80, zoom=1.3, tx=1200, tz=560, th=0)),
                             (4.8, dict(yaw=-24, pitch=72, zoom=1.45, tx=1150, tz=560, th=0))],
                        words=[(17.25, 19, "TWO BEAMS. ONE SPOT.", "tag", 104, ("anchor", "sample", 160, -300))])),
    ("lab", 19, 2, dict(run=CLAUDE, steps=[(0, 125), (4.4, 188)],
                        cam=[(0, dict(yaw=-4, pitch=62, zoom=1.8, tx=760, tz=320, th=120)),
                             (4.2, dict(yaw=-10, pitch=56, zoom=2.6, tx=680, tz=260, th=120))],
                        words=[(19.25, 21, "SCAN.", "alert", 150, ("anchor", "stage", 220, -300))])),
    ("lab", 21, 4, dict(run=CLAUDE, steps=[(0, 189)], flash=True,
                        cam=[(0, dict(yaw=-30, pitch=30, zoom=4.2, tx=1188, tz=592, th=124)),
                             (2.4, dict(yaw=-34, pitch=34, zoom=2.4, tx=1188, tz=592, th=124)),
                             (9.6, dict(yaw=-8, pitch=44, zoom=1.15, tx=1200, tz=580, th=0))],
                        words=[(21.0, 25, "TIME ZERO.", "tag", 190, ("anchor", "sample", -470, -360)),
                               (22.0, 25, "Δt 2.8 fs", "ink", 92, ("anchor", "sample", 120, 150)),
                               (23.0, 25, "SCORE 0.90", "strip", 92, ("anchor", "sample", 160, 290))])),
    ("poster", 25, 2, dict(slide=5, zoom=(1.0, 1.05), focus=(0.5, 0.45), pulse=True,
                           words=[(25.5, 27, "NOT WHAT IT CLAIMS.", "strip", 92, ("fixed", 1480, 900))])),
    ("poster", 27, 2, dict(slide=6, zoom=(1.05, 1.0), focus=(0.55, 0.45), pulse=True,
                           words=[(27.5, 29, "CLAUDE: 4 OF 6 FOUND TIME ZERO", "tag", 70, ("fixed", 1540, 800))])),
    ("lab", 29, 4, dict(run=FLASH, steps=[(0, 20), (9.4, 140)],
                        cam=[(0, dict(yaw=10, pitch=18, zoom=1.7, tx=1300, tz=650, th=100)),
                             (9.6, dict(yaw=-36, pitch=24, zoom=1.5, tx=1000, tz=650, th=100))],
                        words=[(29.0, 31, "GEMINI 3.8 FLASH", "ink", 84, ("anchor", (1700, 900, 0), -200, 160)),
                               (31.0, 33, "“SETUP COMPLETE.”", "tag", 120, ("fixed", 760, 200))])),
    ("lab", 33, 2, dict(run=FLASH, steps=[(0, 148)], flash=True, shake=True,
                        cam=[(0, dict(yaw=-24, pitch=32, zoom=3.6, tx=640, tz=600, th=120)),
                             (4.8, dict(yaw=-28, pitch=36, zoom=2.4, tx=650, tz=600, th=120))],
                        words=[(33.0, 35, "46 PS OFF.", "alert", 200, ("anchor", "sample", -60, -390)),
                               (34.0, 35, "SCORE 0.18", "tag", 92, ("anchor", "sample", 120, 210))])),
    ("poster", 35, 2, dict(slide=7, zoom=(1.0, 1.06), focus=(0.4, 0.4), words=[])),
    ("poster", 37, 2, dict(slide=2, zoom=(1.06, 1.0), focus=(0.4, 0.4), words=[])),
    ("lab", 39, 5, dict(run=CLAUDE, steps=[(0, 189)],
                        cam=[(0, dict(yaw=-78, pitch=20, zoom=1.6, tx=1200, tz=600, th=0)),
                             (12.0, dict(yaw=18, pitch=46, zoom=1.0, tx=1200, tz=600, th=0))],
                        words=[(40.0, 44, "EVERY RUN REPLAYS.", "tag", 120, ("anchor", (1200, 600, 0), -360, -380)),
                               (42.0, 44, "KAKITKELVINHO.GITHUB.IO/GSS", "strip", 80, ("anchor", (1200, 600, 0), -420, 330))])),
    ("poster", 44, 2, dict(slide=8, zoom=(1.0, 1.05), focus=(0.4, 0.4), pulse=True, words=[])),
    ("poster", 46, 3.334, dict(slide=9, zoom=(1.0, 1.06), focus=(0.35, 0.5), words=[], fade_out=True)),
]

GROOVE_BARS = set(range(21, 29)) | set(range(39, 46))

OVERLAY_JS = r"""
() => {
  if (window.__fx) return;
  const css = document.createElement('style');
  css.textContent = `
    .player,.sidebar,.rail-toggle,.corner-button,.hint,.view-hint,.shortcut-hints,.scene .sc-big { display:none !important; }
    #fx { position:fixed; inset:0; pointer-events:none; z-index:9999; }
    #fx svg { position:absolute; inset:0; width:100%; height:100%; }
    .gss-stp { position:absolute; left:0; top:0; transform-origin:50% 60%; font-family:'Bebas Neue',Impact,sans-serif;
           line-height:.92; padding:.10em .26em .02em; white-space:nowrap; letter-spacing:.02em; filter:url(#pcutS); }
    .gss-stp.gss-tag   { background:#EDE3CC; color:#16120F; box-shadow:10px 10px 0 #16120F; }
    .gss-stp.gss-strip { background:#E8742A; color:#16120F; box-shadow:10px 10px 0 #16120F; }
    .gss-stp.gss-ink   { background:#16120F; color:#EDE3CC; box-shadow:10px 10px 0 rgba(237,227,204,.25); }
    .gss-stp.gss-alert { background:#16120F; color:#E8742A; box-shadow:12px 12px 0 #E8742A; }`;
  document.head.appendChild(css);
  const fx = document.createElement('div'); fx.id = 'fx';
  fx.innerHTML = '<svg viewBox="0 0 1920 1080" preserveAspectRatio="none"></svg>';
  document.body.appendChild(fx);
  window.__fx = fx;
}
"""

UPDATE_JS = r"""
(words) => {
  const fx = window.__fx, svg = fx.querySelector('svg');
  svg.innerHTML = '';
  const keep = new Set();
  for (const w of words) {
    keep.add(w.id);
    let el = document.getElementById(w.id);
    if (!el) { el = document.createElement('div'); el.id = w.id; el.className = 'gss-stp gss-' + w.style; el.textContent = w.text; fx.appendChild(el); }
    el.style.fontSize = w.size + 'px';
    const bw = el.offsetWidth, bh = el.offsetHeight;
    let ax = null, ay = null, x = w.x, y = w.y;
    if (w.anchor) { ax = w.anchor[0]; ay = w.anchor[1]; x = ax + w.dx; y = ay + w.dy; }
    x = Math.max(30, Math.min(1920 - bw - 40, x - bw / 2)); y = Math.max(30, Math.min(1080 - bh - 40, y - bh / 2));
    el.style.transform = `translate(${x}px, ${y}px) rotate(${w.rot}deg) scale(${w.scale})`;
    el.style.opacity = w.opacity;
    if (ax !== null && w.opacity > 0.05) {
      const cx = x + bw / 2, cy = y + bh / 2;
      const ex = cx + (ax - cx) * Math.min(1, w.line), ey = cy + (ay - cy) * Math.min(1, w.line);
      svg.insertAdjacentHTML('beforeend',
        `<line x1="${cx}" y1="${cy}" x2="${ex}" y2="${ey}" stroke="#16120F" stroke-width="9" stroke-linecap="round" opacity="${w.opacity}"/>` +
        `<line x1="${cx}" y1="${cy}" x2="${ex}" y2="${ey}" stroke="#EDE3CC" stroke-width="4" stroke-linecap="round" opacity="${w.opacity}"/>` +
        (w.line >= 1 ? `<circle cx="${ax}" cy="${ay}" r="13" fill="#E8742A" stroke="#16120F" stroke-width="5" opacity="${w.opacity}"/>` : ''));
    }
  }
  for (const el of [...fx.querySelectorAll('.gss-stp')]) if (!keep.has(el.id)) el.remove();
}
"""

LAB_JS = r"""
(a) => {
  state.step = a.step;
  const call = currentRun().trajectory[a.step];
  // look-at: set the camera, compute where the target lands with no pan, then pan it to the frame point
  Object.assign(state.cam, { yaw: a.yaw, pitch: a.pitch, zoom: a.zoom, panX: 0, panY: 0 });
  sceneSvg(call);
  const p0 = proj({ x: a.tx, z: a.tz, h: a.th });
  state.cam.panX = a.fx - p0.x + a.jx; state.cam.panY = a.fy - p0.y + a.jy;
  render();
  const snap = call.snapshot || {}, parts = snap.parts || [];
  const pos = id => { const p = parts.find(q => q.kind === id || q.id === id); return p ? p.pos : null; };
  const meta = currentRun().meta || {}, you = snap.you_mm || meta.desk_mm || { x: -300, z: 600 };
  const hs = meta.housings_mm || [], hx = hs.length ? { x: hs[0].x0, z: (hs[0].z1 + hs[hs.length - 1].z0) / 2, h: 380 } : { x: 2250, z: 600, h: 300 };
  const targets = { sample: pos('sample'), stage: pos('stage'), agent: { x: you.x, z: you.z, h: 820 }, housings: hx };
  const out = {};
  for (const [k, v] of Object.entries(a.anchors)) {
    const t = typeof v === 'string' ? targets[v] : { x: v[0], z: v[1], h: v[2] };
    if (t) { const q = proj({ x: t.x, z: t.z, h: t.h || 0 }); out[k] = [q.x, q.y]; }
  }
  return out;
}
"""

POSTER_JS = r"""
(a) => {
  window.__anims.forEach(x => { x.currentTime = a.ms; });
  const s = document.querySelector('.slide.active svg');
  if (s) { s.style.transformOrigin = `${a.fx * 100}% ${a.fy * 100}%`; s.style.transform = `scale(${a.zoom})`; }
}
"""


def shot(page) -> Image.Image:
    return Image.open(io.BytesIO(page.screenshot(type="jpeg", quality=95))).convert("RGB")


def word_state(words, t_abs, anchors=None):
    out = []
    for i, (b_in, b_out, text, style, size, place) in enumerate(words):
        t_in, t_out = tb(b_in), tb(b_out)
        if not (t_in <= t_abs < t_out):
            continue
        u = (t_abs - t_in) / 0.24
        scale = 1.0 + 0.32 * (1 - ease_out(u)) - 0.05 * math.sin(min(1.0, u) * math.pi) * (u < 1)
        tilt = [-3.0, 2.2, -1.6, 2.8, -2.4][i % 5]
        rot = tilt + (1 - ease_out(u)) * 6 * (1 if i % 2 else -1)
        op = min(1.0, (t_abs - t_in) / 0.06, (t_out - t_abs) / 0.1)
        line = ease_out((t_abs - t_in - 0.08) / 0.3)
        w = dict(id=f"w{abs(hash((text, b_in))) % 10**8}", text=text, style=style, size=size, rot=rot, scale=scale,
                 opacity=max(0.0, op), line=line, anchor=None, dx=0, dy=0, x=0, y=0)
        if place[0] == "anchor":
            w["anchor"] = (anchors or {}).get(f"a{i}")
            w["dx"], w["dy"] = place[2], place[3]
            if w["anchor"] is None:
                w["x"], w["y"] = 960 + place[2], 540 + place[3]
        else:
            w["x"], w["y"] = place[1], place[2]
        out.append(w)
    return out


def flash_amount(t_local):
    return max(0.0, 0.85 * (1 - t_local / 0.35)) if t_local < 0.35 else 0.0


def render_lab(page, spec, t0, t_local, loaded):
    if loaded.get("run") != spec["run"]:
        page.goto(f"{VIEWER}?run={spec['run'].replace('/', '%2F')}&step=0&rail=closed")
        page.wait_for_load_state("networkidle")
        page.wait_for_function("() => typeof currentRun === 'function' && currentRun() && currentRun().trajectory")
        page.evaluate("document.fonts.ready")
        page.evaluate(OVERLAY_JS)
        page.wait_for_timeout(300)
        loaded["run"] = spec["run"]
    st = spec["steps"]
    if len(st) == 1:
        step = st[0][1]
    else:
        (ta, sa), (tb_, sb) = st[0], st[-1]
        step = round(lerp(sa, sb, max(0.0, min(1.0, (t_local - ta) / (tb_ - ta)))))
    cam = keyframes(spec["cam"], t_local)
    jx = jy = 0.0
    if spec.get("shake") and t_local < 1.2:
        amp = 26 * (1 - t_local / 1.2) ** 2
        jx, jy = amp * math.sin(t_local * 83), amp * math.cos(t_local * 61)
    words = spec.get("words", [])
    anchors = {f"a{i}": w[5][1] for i, w in enumerate(words) if w[5][0] == "anchor"}
    res = page.evaluate(LAB_JS, dict(step=step, anchors=anchors, fx=960, fy=560, jx=jx, jy=jy, **cam))
    page.evaluate(UPDATE_JS, word_state(words, t0 + t_local, res))
    return shot(page)


def render_poster(page, spec, t0, t_local, loaded, dur):
    if loaded.get("slide") != spec["slide"]:
        page.goto(f"{DECK}#{spec['slide']}")
        page.reload()
        page.wait_for_load_state("networkidle")
        page.evaluate("document.fonts.ready")
        page.evaluate(OVERLAY_JS)
        page.evaluate("() => { window.__anims = document.getAnimations(); window.__anims.forEach(a => a.pause()); }")
        loaded["slide"] = spec["slide"]
    z0, z1 = spec["zoom"]
    zoom = lerp(z0, z1, ease(t_local / dur))
    if spec.get("pulse"):
        beat_phase = ((t0 + t_local) % BEAT) / BEAT
        zoom *= 1 + 0.012 * math.exp(-beat_phase * 6)
    page.evaluate(POSTER_JS, dict(ms=t_local * 1000.0, zoom=zoom, fx=spec["focus"][0], fy=spec["focus"][1]))
    page.evaluate(UPDATE_JS, word_state(spec.get("words", []), t0 + t_local))
    return shot(page)


def finish(img, spec, t0, tl):
    if spec.get("flash"):
        fa = flash_amount(tl)
        if fa > 0:
            img = Image.blend(img, Image.new("RGB", (W, H), CREAM), fa)
    if spec.get("fade_out"):
        rem = TOTAL - (t0 + tl)
        if rem < 1.2:
            img = Image.blend(img, Image.new("RGB", (W, H), INK), 1 - rem / 1.2)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--shots", default="", help="comma-separated shot numbers (1-based) to preview or render")
    ap.add_argument("--segments", default="", help="render the --shots as separate clips into this folder")
    a = ap.parse_args()
    total_bars = sum(s[2] for s in SHOTS)
    assert abs(total_bars * BAR - TOTAL) < 0.02, (total_bars * BAR, TOTAL)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        lab = browser.new_page(viewport={"width": W, "height": H})
        deck = browser.new_page(viewport={"width": W, "height": H})
        if a.segments:
            import imageio_ffmpeg
            os.makedirs(a.segments, exist_ok=True)
            wanted = [int(x) for x in a.shots.split(",") if x]
            for si in wanted:
                kind, bar0, bars, spec = SHOTS[si - 1]
                t0, dur = tb(bar0), bars * BAR
                n = int(round((t0 + dur) * FPS)) - int(round(t0 * FPS))
                path = os.path.join(a.segments, f"shot_{si:02d}.mp4")
                wr = imageio_ffmpeg.write_frames(path, (W, H), fps=FPS, codec="libx264", quality=None, macro_block_size=1,
                                                 output_params=["-crf", "21", "-maxrate", "6M", "-bufsize", "12M", "-preset", "medium", "-pix_fmt", "yuv420p"])
                wr.send(None)
                loaded = {}
                for f in range(n):
                    tl = f / FPS
                    img = render_lab(lab, spec, t0, tl, loaded) if kind == "lab" else render_poster(deck, spec, t0, tl, loaded, dur)
                    img = finish(img, spec, t0, tl)
                    wr.send(img.tobytes())
                wr.close()
                print(f"shot {si} done ({n} frames)", flush=True)
            browser.close()
            return
        if a.preview:
            os.makedirs(os.path.join(HERE, "preview"), exist_ok=True)
        else:
            import imageio_ffmpeg
            silent = os.path.join(HERE, "_video_only.mp4")
            wr = imageio_ffmpeg.write_frames(silent, (W, H), fps=FPS, codec="libx264", quality=None, macro_block_size=1,
                                             output_params=["-crf", "18", "-preset", "slow", "-pix_fmt", "yuv420p"])
            wr.send(None)
        n_total = int(round(TOTAL * FPS))
        frame_i = 0
        for si, (kind, bar0, bars, spec) in enumerate(SHOTS):
            t0, dur = tb(bar0), bars * BAR
            n = int(round((t0 + dur) * FPS)) - int(round(t0 * FPS))
            loaded_lab, loaded_deck = {}, {}
            if a.preview and a.shots and str(si + 1) not in a.shots.split(","):
                continue
            picks = {int(n * 0.15), int(n * 0.6), n - 2} if a.preview else None
            for f in range(n):
                if a.preview and f not in picks:
                    continue
                tl = f / FPS
                if kind == "lab":
                    img = render_lab(lab, spec, t0, tl, loaded_lab)
                else:
                    img = render_poster(deck, spec, t0, tl, loaded_deck, dur)
                img = finish(img, spec, t0, tl)
                if a.preview:
                    img.save(os.path.join(HERE, "preview", f"s{si + 1:02d}_{f:04d}.png"))
                else:
                    wr.send(img.tobytes())
                    frame_i += 1
            loaded_lab.clear(); loaded_deck.clear()
            print(f"shot {si + 1}/{len(SHOTS)} ({kind}, bars {bar0}-{bar0 + bars - 1:g})", flush=True)
        browser.close()
        if a.preview:
            return
        wr.close()
    exe = imageio_ffmpeg.get_ffmpeg_exe()
    out = os.path.join(HERE, "gss_pitch_v2.mp4")
    subprocess.run([exe, "-y", "-loglevel", "error", "-i", silent, "-i", os.path.join(HERE, "score.wav"),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out], check=True)
    os.remove(silent)
    print(f"wrote {out}: {frame_i} frames = {frame_i / FPS:.2f} s (target {TOTAL:.2f} s)")


if __name__ == "__main__":
    main()
