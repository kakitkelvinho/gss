# Throwaway visual study

Question: can a restrained, full-window lab scene match the supplied layout sketch while keeping the robot outside the optical table?

Start it from the repository root with one command:

```sh
python3 -m http.server 8766 --directory viewer
```

Open `http://localhost:8766/prototype.html`. Playback floats at the top left. The call rail groups each optic's setup and can be collapsed to give the scene more room. Expand a group to inspect its individual calls. Money and lab time lead the telemetry; the private replay score is secondary. Run, speed, parts, and top view use the same small menu pattern.

## Static run data

`runs_bundle.js` is a checked-in, static export. It includes the four Gemini 3.1 Pro Level 1
trials and earlier demonstration runs; the ignored `jobs/` directories are not needed to view it.
The run menu shows each model, seed, level, and final score. A run can also be opened directly by
its stable ID, for example:

```text
prototype.html?run=2026-11-15__01-34-04/gss-scoring__y799vDQ&step=136
```

To add completed Harbor runs to the same static bundle, use the simulator version that produced
them and run:

```sh
python3 scripts/export_viewer_runs.py /path/to/jobs --append-existing
```

The exporter replays each action and checks the recorded physics and final diagnostics before
writing verifier-only poses and beam paths. It skips cancelled jobs. A plain static file host can
serve `prototype.html`, its CSS and JavaScript, and `runs_bundle.js`; no API key, database, or
Harbor service is needed for playback. The bundle exposes simulator truth for explanation and
must never be mounted in the playing agent's container.

Left and right arrow keys or comma and period step through calls; Space plays or pauses. Escape closes a menu. Within a menu, arrows, Home, and End move focus. The current call's coordinate marker and the table's axis labels use millimetres.

The call timeline, optics, beams, spend, lab time, and current diagnostic reward come from the bundled real run snapshots. The robot pose is illustrative and inferred from the tool name; it stands beyond the front edge of the table. The score trace shows fractional values already present in the simulator's reward. No scoring code was changed.

The look follows the screen-print posters in `pitch-deck-v6.html`: charcoal room, cream paper, orange and blue ink, Bebas Neue headlines with Oswald labels, cut-paper edges (the deck's `pcut` displacement filters) and a grain-and-wear overlay. Each step reads as a poster: the action is the cream headline and the exact call is the orange line under it. 

The table keeps the style off its geometry. It is a true orthographic projection (default yaw −14°, elevation 38°) of the simulator's millimetre coordinates, sized to the pane, so x, z and h share one scale everywhere. The 25 mm hole grid is the same affine transform applied as a pattern, and the rulers tick every 100 mm with labels every 600 mm. Mirrors, posts, the delay stage's retroreflector, lens rings and the source housings use the dimensions in `sim/constants.py` and the replay's `meta.housings_mm`. Mirror and lens orientations come from each part's effective yaw, and the retro mouth sits at apex − 40 mm, so it lands exactly on the beam's turning point. Each optic is labelled, and a faint ink line under each beam marks its footprint on the table. Only big flat shapes (slab, housings, desk, worker) get the cut-edge filter. Holes, beams, optics and ticks stay crisp.

The worker stands at the replay's `you_mm` position: behind the table, in front of it, or at the desk. It is an oxblood block mannequin built in world millimetres, so it turns with the camera. One fixed key light (high, from behind-left) shades every block and casts the worker's shadow on the table top and floor, and the table's shadow on the floor. The worker's height (1050 mm) and pose are illustrative. The beams are vermilion (800 nm) and cyan (OPA) with an ink casing, so they stand apart from the interface orange.

Camera: drag to orbit (yaw −80° to 20°, pitch 15° to 85°), shift-drag to pan, scroll to zoom toward the cursor (0.6× to 6×), and double-click or View → Reset camera to return to the default. The orbit is limited on purpose: the rulers, desk and worker placement are correct within that range, not all the way around. For repeatable video shots, the URL takes `step`, `yaw`, `pitch`, `zoom`, `panx`, `pany` and `rail=closed`, for example `prototype.html?step=108&yaw=-55&pitch=72&zoom=1.8&rail=closed`.

Score breakdown: the orange block recomputes the grader from `sim/reward.py` using the replay's diagnostic truth at the current step. It shows spot overlap ×0.2, timing ×0.5 and efficiency ×0.3 (locked until timing reaches 0.9), plus one plain sentence on why the run fails: a blocked beam, missed spots, or pulses that arrive too far apart, with the gap in fs or ps and in mm of path against the window this level allows. If a run was scored by an earlier grader, the recorded score is shown, with a note giving what today's grader would award.

## Hosting

`.github/workflows/pages.yml` publishes `viewer/` to GitHub Pages on every push to `main` that
touches it: <https://kakitkelvinho.github.io/gss/> (`index.html` forwards to `prototype.html` and keeps
the query string). Runs whose recorded verifier reward differs from today's `sim/reward.py` are
marked `old_scorer` by the exporter and show "(old scorer)" in the run menu and an "Old scorer" tag
in the score panel.
