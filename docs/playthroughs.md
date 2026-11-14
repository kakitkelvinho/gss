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
