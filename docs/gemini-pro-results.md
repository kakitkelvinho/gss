# GSS run summary

Four completed OpenCode + Gemini 3.1 Pro Preview trials on Level 1, using the graded reward in
commit `78cd401`. Seeds 1, 2, and 3 were tested; seed 1 was repeated. All four trials scored
0.000. The scripted reference scored 0.917, 0.922, and 0.926 on seeds 1, 2, and 3 respectively
([baseline table](results.md)). Cancelled setup attempts are excluded.

These were valid task failures: none of the four trials brought both beams to the sample at the
same time, so their maximum spatial overlap remained zero. The two `timeout` labels below mean
the **simulated four-hour lab budget**, not a Harbor agent timeout. The [static replay](../viewer/prototype.html)
contains verifier-only geometry snapshots for every action. Re-export from the local Harbor jobs
with `python3 scripts/export_viewer_runs.py jobs --append-existing`.

R = graded final reward; eta = transmitted spatial and temporal overlap; O = spatial overlap; |dt| = timing error.

| run | model | seed | level | OPA nm | R | eta | O | abs dt (fs) | EUR (C_min) | min | calls | ended | tags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-15__01-00-16/gss-scoring__eCUaRvt | gemini/gemini-3.1-pro-preview | 1 | 1 | 1300 | 0.000 | 0.000 | 0.00 | – | 13700 (7450) | 236 | 90 | agent | design-not-viable, overspent, beam-not-at-sample, stray-beams |
| 2026-11-15__01-12-43/gss-scoring__PvHDfV5 | gemini/gemini-3.1-pro-preview | 1 | 1 | 1300 | 0.000 | 0.000 | 0.00 | – | 15080 (7450) | 239 | 174 | timeout | overspent, beam-not-at-sample, stray-beams, timeout, malformed-calls |
| 2026-11-15__01-34-04/gss-scoring__y799vDQ | gemini/gemini-3.1-pro-preview | 2 | 1 | 450 | 0.000 | 0.000 | 0.00 | – | 6700 (1700) | 238 | 137 | agent | overspent, beam-not-at-sample, stray-beams |
| 2026-11-15__01-42-54/gss-scoring__P4CSFoh | gemini/gemini-3.1-pro-preview | 3 | 1 | 600 | 0.000 | 0.000 | 0.00 | – | 7030 (950) | 238 | 145 | timeout | overspent, beam-not-at-sample, stray-beams, timeout |

## Failure modes across runs

- `overspent`: 4 of 4 runs
- `beam-not-at-sample`: 4 of 4 runs
- `stray-beams`: 4 of 4 runs
- `timeout`: 2 of 4 runs
- `design-not-viable`: 1 of 4 runs
- `malformed-calls`: 1 of 4 runs

## Per run

### 2026-11-15__01-00-16/gss-scoring__eCUaRvt (gemini/gemini-3.1-pro-preview, seed 1, OPA 1300 nm): R = 0.000
- bought: BBO-T292, CAM-VSWIR, PD-FAST; design viable: False
- **design-not-viable**: no working detection route at 1300 nm (bought ['BBO-T292', 'CAM-VSWIR', 'DL-C100', 'MIR-1', 'PD-FAST', 'PER-1']; working: BBO-T236+F-BP495, BBO-T236+F-VIS495, GAP-TPA)
- **overspent**: EUR 6250 above the cheapest workable design
- **beam-not-at-sample**: at the end: 800nm -> mount of mirror-4, opa -> leaves the table
- **stray-beams**: 1 beam(s) left the table (229.83 min)

### 2026-11-15__01-12-43/gss-scoring__PvHDfV5 (gemini/gemini-3.1-pro-preview, seed 1, OPA 1300 nm): R = 0.000
- bought: BBO-T236, BBO-T292, CAM-VSWIR, F-BP495, PD-FAST; design viable: True
- **overspent**: EUR 7630 above the cheapest workable design
- **beam-not-at-sample**: at the end: 800nm -> mount of mirror-1, opa -> leaves the table
- **stray-beams**: 4 beam(s) left the table (62.09 min)
- **timeout**: ran out of the 4 h lab time
- **malformed-calls**: 15 rejected tool calls

### 2026-11-15__01-34-04/gss-scoring__y799vDQ (gemini/gemini-3.1-pro-preview, seed 2, OPA 450 nm): R = 0.000
- bought: F-BP550, GAN-1, PD-SI; design viable: True
- **overspent**: EUR 5000 above the cheapest workable design
- **beam-not-at-sample**: at the end: 800nm -> lens mount, opa -> mount of mirror-1
- **stray-beams**: 7 beam(s) left the table (129.93 min)

### 2026-11-15__01-42-54/gss-scoring__P4CSFoh (gemini/gemini-3.1-pro-preview, seed 3, OPA 600 nm): R = 0.000
- bought: BBO-T292, F-BP400, GAP-TPA; design viable: True
- **overspent**: EUR 6080 above the cheapest workable design
- **beam-not-at-sample**: at the end: 800nm -> leaves the table, opa -> sample
- **stray-beams**: 12 beam(s) left the table (95.83 min)
- **timeout**: ran out of the 4 h lab time

