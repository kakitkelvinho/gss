# GSS design decisions (grilling session, Fri 2026-11-14)

Agreed decisions for the Friday walking skeleton. These take precedence over HANDOFF.md wherever the two disagree.
Q-numbers refer to the grilling session.

## Stack and process
- **Python 3.12**, `uv` + lockfile, `fastmcp` (pinned, as in Harbor's `hello-mcp` example) over streamable-http on port 8000, `pytest`. numpy turned out to be unnecessary. (Q21, Q44)
- `sim/` is a plain package with no MCP imports and no third-party dependencies (stdlib only). The SFT loop (HANDOFF §8) imports it directly. (Q44)
- One episode per server process. The seed comes from env `GSS_SEED`. There is no reset tool. (Q2)
- MIT `LICENSE`. All code is written at the event.

## The room (blank table)
- 1.2 × 2.4 m breadboard. Coordinates follow QUOP's convention: mm, table plane XZ, +Y is height.
  A desk with the monitor and scope sits at one fixed end. (Q13′, Q39)
- Fixed per seed and stated in `instruction.md`: position, direction and height (90–160 mm) of the
  pump output port (800 nm, 100 fs FWHM, 1 kHz) and of the OPA output port (1300 nm, 60 fs FWHM).
  (Q3, Q12, Q40)
- The OPA's internal path, 1.50–1.70 m per seed, appears **only** in the OPA manual, as this unit's calibrated value. (Q40)
- Separate random streams: "lab" (ports, mount errors) and "noise" (measurements). A seed always produces the
  same table, whatever the agent does. (Q40)
- The table size, desk position and catalogue are fixed across seeds.

## Catalogue (L1)
| Slot | Items |
|---|---|
| Delay stage | manual micrometer 25 mm (~€400, ~5 µm backlash, ~3 s per hand-turned scan point) · closed-loop motorised 25 mm (~€2.5k, 0.1 µm repeatability) · closed-loop motorised 100 mm (~€4k) (Q18′, Q24′, Q34) |
| Overlap diagnostic (sample mount) | correct-cut BBO, type-I SFG 800+1300→495 nm · wrong-cut BBO (800 nm SHG cut: strong pump background, cross term ~1%) · fast photodiode (Q3, Q16, Q17) |
| Mounting | 1" mirror in kinematic mount (~€150) · periscope, a rigid two-mirror height changer (~€500) (Q24, Q29) |

- Free table equipment: camera at the sample mount (`"sample"` = focal plane, `"lens"` = where each beam hits the lens), a 1 GHz scope (photodiode timing ±50 ps), and an IR card. (Q1, Q17′, Q37)
- Buying costs 15 min and can happen at any time. A second item in an occupied slot swaps in, and both purchases count toward C. A purchase that would push total spend past €30k is refused. (Q7)
- Swapping diagnostics in the sample mount doesn't change any path.

## Physics
- **Beam model:** one centre line per beam (no lens-design ray tracing). It travels straight until it meets a part, then reflects
  off that mirror's **actual** normal: the yaw set by eye + mount error + knob yaw/pitch. Nothing snaps to the beam. (Q33′, Q35)
- **Clipping:** 1" optics. Transmission starts dropping about 10 mm off-centre, and a beam that lands off the mirror entirely carries on past it. Transmission T enters η. (Q25)
- **Heights:** only periscopes change a beam's height. A beam at the wrong height misses the sample. Polarisation rotation is deferred. (Q29)
- **Delay stage:** adds 2·x of path wherever it sits in a route. A beam that isn't parallel to the rail makes the spot drift by ~2·x·θ as the stage moves. Its manual explains this; nothing hints at how hard it is to align. (Q34, Q36)
- **Focusing (decided after grilling):** the sample mount is free table equipment: an f = 100 mm lens with the sample at its focal plane (plus a small per-seed defocus δz).
  Beams arrive roughly parallel (non-collinear, a few mm apart on the lens) and cross at the focus with w0 ≈ 50 µm
  (pump W = 0.5 mm, probe W = 0.8 mm). Thin lens: spot = f·θ + δz·θ − δz·ρ/f. One mirror centres the beam on the lens, the other overlaps the foci.
  Crossing angle is ignored in L1 and matters in L2.
- **Spatial overlap:** normalised overlap of the two focal spots at the sample plane, O = (2w1w2/(w1²+w2²))·exp(−2d²/(w1²+w2²)) ≈ exp(−d²/w0²). (Q9, Q15′)
- **Shutters:** both arms start blocked, so do-nothing makes no stray beams.
- **Timing:** Δt = t_pump − t_probe. Pulses are Gaussian, quoted as intensity FWHM. τ_c = √(τ₁²+τ₂²)/(2√ln2) ≈ 70 fs (1/e half-width). (Q4, Q12)
- **BBO signal:** S = A·T·O·exp(−(Δt/τ_c)²) + b_pump + b_probe + N(0, σ/√t_int), quantised to 1 count.
  Correct cut: A=1000, b_pump=50, b_probe=20, σ=100 /√s. Wrong cut: A=10, b_pump=2000. (Q16)
- **Fast photodiode:** arrival time of each unblocked beam on the 1 GHz scope, 20 ps quantisation, 10 ps jitter. (Q17, Q17′)
- **Manual stage:** ~5 µm backlash on reversal. **Motorised stage:** 0.1 µm, 2 mm/s. (Q18, Q24′)

## Agent tools (all lab-time accounting is inside the sim)
- Layout and alignment: `place(part, x, z, height, yaw_deg)` 5 min, with ±1 mm and yaw σ≈0.5° error · `rotate(part, Δdeg)` 2 min, σ≈0.2° ·
  `move(part, x, z)` 3 min · `remove(part)` 1 min · `knob(mirror, yaw|pitch, Δmrad, watch=false)` 30 s (tuned down from 1 min so the expert fits in 65% of the budget), ±50 mrad range, 2% error ·
  `ir_card(part | x,z,height)` 30 s, ±0.5 mm. (Q32′)
- Information: `list_catalogue` 1 min · `get_datasheet` 2 min · `read_manual` 5 min (includes `"table"`) · `measure_path(arm)` 3 min, ±5 mm, can't see inside the OPA · `buy`. (Q19)
- Measurement: `view_camera(plane)` 10 s, centroid + 1/e² radius per visible beam, 5.5 µm pixels, 0.3 px noise, 0.1 px quantisation, 5 mm field of view (Q14′) ·
  `block/unblock(arm)` 5 s · `move_stage` 2 s + travel · `read_signal(t_int)` t_int + 1 s, t_int ∈ [0.01, 10] s ·
  `scan(start, end, step, t_int)` Σ(t_int + 0.3 s + travel), ≤ 5000 points. (Q18)
- `submit()` ends the episode.
- **Walking:** the person has a position. They walk around the table's edge at 0.5 m/s and can reach 0.6 m in from the edge. Camera, signal and scan reads happen at the desk.
  `knob(watch=true)` returns a camera reading for free only when within 1.5 m of the desk. (Q38, Q39)
- Every action costs at least 5 s. Every response is compact JSON with units in the key names, `lab_time_remaining_min` and the person's position. (Q19, Q20)
- Malformed arguments are rejected with a message and still cost 5 s. Physically impossible actions come back as lab outcomes ("mount doesn't fit there", "knob at end of travel") and cost the time wasted finding out. (Q42)
- Budget 4 h. An action that would pass 4 h is refused and the episode auto-submits. After submit or timeout, every tool returns "episode over". (Q8, Q41)

## Reward and diagnostics
- η = T_pump·T_probe·O·exp(−(Δt/τ_c)²), computed from true state, whatever detector was bought.
- R = η·(1 − 0.2·(C − C_min)/(C_cap − C_min) − 0.1·t_lab/t_budget), with C_cap = €30k. The soft time term (added after the first blind playthrough, user decision) makes slow trial-and-error cost reward, not just budget.
- C_min is computed per seed: the cheapest stage + the correct-cut BBO + the minimum mirrors/periscopes that can physically make up the path difference, found by an offline layout search. (Q6, Q27)
- Logged in `reward.json`, not in R: O, |Δt|, T per arm, design viable, cost, lab time, tool calls, stray-beam count and time, footprint. (Q26, Q43)

## Integrity
- `/verifier/*` lives on the sim server and needs a bearer token held only in the sim container's env and in `tests/`. Without the token it returns 404, and it never changes state. (Q22)
- The trajectory log (every action, true state, hidden Δt and O per step) is readable only through the verifier. (Q31)
- **QUOP** (https://kakitkelvinho.github.io/quop/, the author's own earlier open-source tool, Apache-2.0) is used **only as a viewer**.
  The sim writes QUOP-format setup JSON, using an exporter written at the event. No QUOP code is copied, and QUOP is not modified for the hackathon. This is disclosed in the README. (Q23‴)

## Pass criteria and plan
- Reference run: η ≥ 0.9 on every seed 1–10, using ≤ 65% of the budget. Do-nothing and stop-early both get R < 0.05 on every seed. (Q11, Q41)
- Steps, with a commit and push after each:
  1. `sim/` + pytest, including an in-process expert.
  2. MCP server + verifier route.
  3. Reference run + baselines.
  4. Thin Harbor/compose glue modelled on `hello-mcp`.
- Fallback: if layout isn't working by ~01:00, the Friday submission uses fixed routes. (Q28)

## Implementation notes (step 1)
- `install(part_id)` (2 min, at the sample mount) swaps between owned diagnostics; buying a diagnostic installs it.
- The stage starts at position 0 after purchase. The reference layout puts time zero near mid-travel, so the stop-early baseline (overlap, no timing) scores 0.
- C_min = cheapest stage + correct-cut BBO + 2 mirrors = EUR 1900 (same for every seed). Originally 4 mirrors (EUR 2200); blind playthroughs found working 2-mirror layouts.
- Separate random streams: lab (`gss-lab-<seed>`), per-mount tilt errors (`gss-mount-<seed>-<part>`), placement errors and measurement noise.

## De-hint pass (after blind playthroughs 2-3 succeeded)
- Manuals and datasheets give specifications and conventions only, no procedures (removed e.g. "the 800 nm arm
  must be longer by this amount", "overlapping the foci means matching angles", "enter 10-15 mm off the apex",
  "block one arm to measure the background", "path added = 2 x displacement", expected peak counts).
- Relative timing is no longer stated as "path-matched except the OPA": the table manual gives the per-seed paths
  from the amplifier's split to the pump port and to the OPA input; the OPA manual gives its internal path.
  Time zero needs pump table path + split_pump = probe table path + split_opa + opa_internal.
- Crystal part ids/names no longer name the process: BBO-T236 (theta 23.6 deg, 450-550 nm filter) and BBO-T292
  (theta 29.2 deg, 380-420 nm filter). The agent has to work out which one detects 800 + 1300 nm SFG (495 nm).
- Corrected the SFG cut angle to 23.6 deg (BBO Sellmeier); it was wrongly 26.5 deg.

## Buildability (physical, not a separate score)
- Mount bodies block beams: every mirror has a 38 mm square plate 0.5-12 mm behind the optic and a 1/2" post
  from the table up to the plate; periscope mirrors have plates; the lens sits in a 2" mount ring. A beam that
  passes behind or under another optic's mount is absorbed (logged as "mount of ..."), as on a real table.
- Polarisation is tracked through every reflection (perfect-conductor rule). The type-I SFG cross term scales
  with cos^2 of each beam's angle from horizontal, so out-of-plane routing (e.g. a 90-degree image-rotating
  turn) kills the signal. Gently sloped paths rotate it only slightly, as in reality. The reward (eta) is unchanged.
- The reference layout had to change: the probe now hits the lens at z = 592 and the pump at 608, so the probe
  passes the pump's last mirror on its reflecting side, and the pump enters the retro 15 mm off the apex
  (30 mm separation) so the return clears the pick-off mirror's mount.
