# Submission text (draft)

Paste-ready text for the submission form. Numbers are under the current grader (2026-11-15).

## One line

An AI agent has to build and align a femtosecond pump–probe experiment from an empty optical table,
in a physics simulator, and find time zero: **watch it happen at <https://kakitkelvinho.github.io/gss/>**.

## Short description

GSS: Find Time Zero is a Harbor task in which an agent designs, buys, places and aligns the optics for a
pump–probe setup through about twenty MCP tools, then scans a delay stage until two ultrafast pulses
overlap at the sample. The agent sees only noisy instrument readings, never the simulator's state. The
score comes from the true final physics:
- up to 0.2 for spatial overlap;
- up to 0.5 for timing, falling with every femtosecond of error;
- up to 0.3 for low spend and lab time, only once the setup works.

**See the lab, not the logs:** every recorded run, from the scripted reference to Gemini to blind Claude,
replays step by step in a 3D lab view with each tool call and the score explained:
<https://kakitkelvinho.github.io/gss/>. Judges can watch their own runs the same way:
`uv run python scripts/serve_viewer.py` shows each run as soon as it finishes.

## Try it

```bash
harbor run -p . -a opencode -m <provider/model>   # default: Level 2, the 90° crossing
harbor run -p . -a oracle                          # scripted reference
uv run python scripts/serve_viewer.py              # watch the runs in the lab view
```

## Results (current grader)

Scores are per level and are not comparable across levels.

| level | agent | R |
|---|---|---|
| 2 | scripted reference, seeds 1–10 | mean 0.835 (0.781–0.904) |
| 2 | Claude, 6 blind playthroughs (seeds 1, 3; not Harbor) | 0.897, 0.886, 0.868, 0.846, 0.540, 0.197 |
| 1 | scripted reference, seeds 1–10 | mean 0.818 (0.777–0.877) |
| 1 | Gemini 3.8 Flash (Harbor) | 0.809, 0.199, 0.185 |
| 1 | Gemini 3.1 Pro Preview (Harbor, 4 runs) | 0.000 each |

Agents fail on real lab problems:
- invisible infrared beams;
- choosing a detector that can see the signal;
- clipping on optics;
- a weak time-zero signal that needs patient scanning.

Details: README.md, docs/playthroughs.md, docs/DECISIONS.md.

## Still to check before sending

- The deck (`pitch-deck.html`) must be rebuilt from `deck/` with Node (`bash deck/build.sh`) to show the
  current-grader numbers.
- Settle the C_min / GaP question at Level 2, 600 nm (docs/DECISIONS.md, "Tougher grading").
