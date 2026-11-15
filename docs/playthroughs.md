# Blind playthroughs (fresh Claude agents, no access to the code)

Not Harbor/OpenCode runs (no inference API key was available): each run was a fresh Claude agent
(same model family as the one that built the environment, fresh context) that got only `instruction.md`
and a CLI for the MCP tools, was told not to read the repository, played one seed against a live server,
and was scored through the token-gated verifier route.

| run | seed | version | R | eta | O | abs dt (fs) | cost (EUR) | lab time | tool calls | outcome |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | before camera power readout | 0.000 | 0.000 | 0.994 | 2599 | 2800 | 94% | 107 | probe clipped to 7% on a mirror edge (invisible: camera gave centroids only), so the time-zero peak (~70 counts) sat below the noise; burned the budget re-scanning |
| 2 | 2 | camera reports relative_power | 0.928 | 0.980 | 0.986 | 5.7 | 2050 | 53% | 59 | success: 2-mirror layout (lens facing -z), height change via a vertical offset at the retroreflector |
| 3 | 8 | camera reports relative_power | 0.929 | 0.997 | 0.998 | 1.7 | 1900 | 68% | 76 | success: 2-mirror layout, height change via mirror pitch; tape estimate 4.6 mm off, found by coarse scan |
| 4 | 9 | + de-hinted manuals, unlabelled camera, mounts block beams, polarisation | 0.878 | 0.954 | 0.977 | 3.8 | 2500 | 75% | 163 | success, slower: 2 mirrors + retro vertical offset; first scans at 0.05 s found nothing, bought a photodiode to locate time zero |
| 5 | 3 | same as run 4 | 0.724 | 0.794 | 0.969 | 20.0 | 2200 | 85% | 112 | partial: pump clipped to 89% at the lens edge, timing 20 fs off (manual-stage backlash), rebuilt the layout after mounts blocked beams, 39 min of stray beam |

Rewards are as scored at the time (C_min = EUR 2200 for runs 1-3, EUR 1900 after). Runs 2 and 3 exposed that two mirrors suffice, so
C_min is now EUR 1900.

Feedback from the agents that is still open:
- Reading all manuals costs ~45-50 min of lab time; the time cost of reading is not flagged up front (intended, but could be stated in instruction.md).
- `buy` must be called as `{"items": ...}` (the CLI passes tool arguments as a JSON object); agents tried the bare `{part: qty}` form.
- BBO readings are clamped at 0, so at low counts the noise doesn't look like the documented 1/sqrt(t) Gaussian.
- `move_stage` works before the stage is placed (harmless).
- Mount dimensions were not in the datasheet (runs 4-5); now stated (plate 38 x 38 mm, 0.5-12 mm behind the surface, post, lens-mount ring).
- Expected signal strength is not stated (deliberate after the de-hint pass: in a real lab you don't know it either).

## Level 2, seed 3 (600 nm), blind Claude subagents, 2026-11-15

These are **not Harbor runs**: each player was a fresh Claude subagent in Claude Code, given only
`instruction.md` and the lab-tools CLI from `scripts/blind_playthrough.py`, playing against a local
server and scored through the token-gated verifier route. The same-seed reference scores 0.942
(`docs/results_l2.md`), and C_min is EUR 1550.

| player | R | eta | abs dt (fs) | cost (EUR) | lab time | tool calls | parts bought | what happened |
|---|---|---|---|---|---|---|---|---|
| p1 | 0.544 | 0.777 | 6.3 | 1400 | 54% | 118 | DL-M25, 3x MIR-1, GAP-TPA, PD-SI | found time zero with GaP at 1-2 s/point, and corrected the height with a raised retroreflector (no periscope); but the 800 nm arm reached the sample at only 0.78 power, so eta < 0.9 and no efficiency bonus |
| p2 | 0.957 | 0.999 | 2.8 | 1900 | 41% | 190 | PD-SI, GAP-TPA, DL-M25, PER-1, 3x MIR-1 | success: periscope + 3 mirrors, PD-SI for coarse timing, GaP peak found at 1 s/point (11.896 mm); beat the reference |
| p3 | 0.927 | 0.968 | 16.2 | 1250 | 52% | 101 | 2x MIR-1, DL-M25, GAP-TPA, PD-SI | success with the cheapest build: 2 mirrors, height fixed by a retroreflector offset; GaP peak found at 1-3 s/point; timing 16 fs off |

All three called `submit`. Tool calls include one `list_catalogue` call made by the setup script's server check.

Notes for the task design:
- **All three found the time-zero peak with GaP; none bought GaN or the 550/40 filter.** At seed 3,
  GaP's cross signal is about +250-450 counts on a single-beam background of about 1700-2300, so
  0.05-0.3 s points miss it but 1-3 s points find it. The intended "GaP looks right but doesn't
  work, GaN + 550/40 does" decision did not happen in these runs.
- **Two players built below C_min:** EUR 1400 (p1) and EUR 1250 (p3), against C_min = EUR 1550.
  Both skipped the periscope by passing the 800 nm beam off the retroreflector's apex height, so
  it returned at the OPA height. The C_min search doesn't appear to consider this layout.

Difficulties the players named (number of players in brackets):
- **Weak, noisy GaP cross-correlation (3/3):** the peak is only about 15-20% above the single-beam
  backgrounds, so fast scans miss it and 1-3 s per point is needed. Nothing hints at the signal size
  or at the 90-degree crossing broadening it to about 330-470 fs.
- **Unclear which diagnostic works at a 90-degree crossing (3/3):** all assumed BBO sum-frequency
  can't phase-match at 90 degrees and chose GaP by reasoning; p3 also wondered whether the
  perpendicular polarisations affect the GaP cross term.
- **Coarse timing estimates are only rough (2/3, p2 and p3):** the tape measure, PD-SI (20 ps
  sampling, about 10 ps jitter) and the manuals' internal paths missed the peak by 0.1-1.5 mm of
  stage, so a scan was still needed (p1 found its estimates close enough).
- **Mirror moves and knob signs (2/3):** `move` re-seats the mirror with a yaw error of several mrad
  (p1, p3), the knob-to-camera sign isn't documented (p1), and the pitch response looked
  inconsistent at first (p2).
- **Retroreflector clipping / power loss (2/3):** p3 lost half the 800 nm power 17.8 mm off the retro
  axis, inside the stated 19.1 mm aperture; p1 ended with 0.78 transmission and asked how the
  "physical efficiency >= 0.9" gate is defined.
- **The camera doesn't say which spot is which beam (1/3, p2);** `knob(watch=true)` works only within
  1.5 m of the desk (p2); `place` can't re-place a part, and changing a height means remove + place (p3).
