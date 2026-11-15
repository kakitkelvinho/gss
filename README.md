# GSS: Find Time Zero

A Harbor task (`gss/find-time-zero`) in which an agent **designs and aligns a pump–probe setup in a
physics simulator** and then finds *time zero*. It starts from a blank optical table, buys parts,
places and aligns mirrors by hand, overlaps two ultrafast beams at a sample, and scans a delay stage
until the two pulses arrive together. Built at Junction 2026 for AfterQuery's "Break the Agent" track
by **God's Strongest Soldiers (GSS)**.

## What the agent has to do

There are two laser outputs on an empty 1.2 × 2.4 m breadboard: the `800nm` arm (amplifier, 100 fs)
and the `opa` arm (60 fs, from an OPA whose output is 1300, 600 or 450 nm depending on the seed). The goal is to get both beams onto the **same 50 µm focal spot** at
the sample and to make both pulses **arrive within ~100 fs of each other**, as cheaply as possible
and within **4 h of simulated lab time**. Everything is done through ~20 MCP tools: `buy`, `place`,
`knob`, `ir_card`, `view_camera`, `measure_path`, `move_stage`, `scan`, `read_signal`, `submit`,
and so on. Physical actions cost lab time, and walking around the table costs time too. Reading
manuals, datasheets, the catalogue, and status is free.

`instruction.md` gives only the goal and the constraints. The agent has to work out the method
from the catalogue, datasheets and manuals:

- **Coarse delay is a layout decision.** The OPA pulse has travelled through the OPA, whose internal
  path (1.5–1.7 m on the signal route, ~0.58 m more on the visible route; stated only in the OPA
  manual) has to be matched by laying out a longer 800 nm arm.
  The 25 mm delay stage can only fix the last few millimetres.
- **Real alignment.** The beams are centre-line rays that reflect off each mirror's *actual*
  normal: the yaw set by eye (±0.5°), plus a mount error, plus the knob settings. Optics clip near
  their edges. Nothing snaps into place, so the agent has to steer with knobs, IR cards and a
  camera.
- **Overlap at the focus means matching beam angles** (spot = f·θ for a thin lens, plus a hidden
  per-seed defocus).
- **Finding time zero:** the cross-correlation peak is ~20 µm of path (~10 µm of stage travel)
  wide, on top of single-beam backgrounds and noise. Step size, integration time and scan range
  trade off against the time budget.
- **Choosing the right parts depends on the OPA wavelength** (photon energies $E = 1239.84/\lambda$):
  - a BBO only works for the pair it is cut for, *and* its sum frequency must land where the Si
    signal camera can see (400–1000 nm): 800 + 1300 → 495 nm works, 800 + 450 → 288 nm is invisible;
  - a two-photon semiconductor needs $E_{800} + E_\text{opa} > E_g$; GaP (2.26 eV) is a cheap
    two-photon photodiode at 1300/600 nm but absorbs 450 nm linearly; GaN (3.4 eV) gives yellow-band
    luminescence at 450/600 nm but nothing at 1300 nm;
  - a filter must pass the signal and block scattered laser light (unfiltered scatter saturates the
    signal camera; a 775 nm shortpass leaks 800 nm; a UV glass stack blocks the yellow band; at 600 nm
    the broad 495–710 nm stack lets the OPA scatter through);
  - the free Si alignment camera can't see 1300 nm, so that seed needs the VIS-SWIR camera;
  - fast photodiodes give only a coarse (~10 ps) arrival time, and only for wavelengths in their range.

## Level 2: 90° crossing (`GSS_LEVEL=2`)

The beams must cross at a full angle of 90° at the sample (each 45° from the normal), through a mount with
**one f = 100 mm lens per beam**; the same lens for both beams doesn't count. What changes:

- The spot is stretched by $1/\cos 45°$ on the tilted sample. Across it the two pulses arrive at different
  times, $\Delta t(x) = 2x\sin(\varphi/2)/c$, which broadens the cross-correlation to a 1/e half-width of
  ~186 fs and lowers its peak to ~0.37. The reward uses this broadened window.
- No BBO cut can be phase-matched at 90° (~1%); two-photon absorption needs no phase matching. The
  signal camera looks head-on from the front (as in the lab: emission seen along the normal), so only
  diffuse scatter (~1%) reaches it.
- Routes: 1300 nm → GaP only (+ VIS-SWIR camera); 600 nm → GaN + 550/40 (GaP's reduced peak no longer
  clears its two single-beam backgrounds); 450 nm → GaN + 550/40 or the 495–710 stack.
- Short lever arms near the two lenses, and a ±0.5° sample-mount yaw error magnified by the tilt, make
  beam steering harder.

The scripted expert succeeds on seeds 1–10 over MCP at both levels within 65% of the lab budget.

## Why it's hard (and fair)

Everything needed is in the manuals and datasheets: no trick wording and no withheld numbers. The
difficulty is **execution in a physical loop**: planning a layout that can reach time zero,
converging noisy alignment steps, and then scanning efficiently. Typical ways to fail:
- never reading the OPA manual, so the stage can't reach time zero;
- scan steps larger than the peak;
- integration times too short to see the peak;
- mistaking a single-beam background for the cross term;
- burning the budget on broad scans.

## How it is scored

The reward is computed from the **simulator's true final state**, whatever detector was bought:

$$S = T_{800}T_\text{opa}O,\qquad
\eta = S\exp\!\left[-\left(\frac{\Delta t}{\tau_c}\right)^2\right]$$

$$R = 0.2S + 0.5\eta + \mathbf{1}_{\eta\geq0.9}\left[0.2(1-c) + 0.1\left(1-\frac{t_\text{lab}}{4\,\text{h}}\right)\right],\qquad
c = \operatorname{clip}\!\left(\frac{C-C_\text{min}}{C_\text{cap}-C_\text{min}},0,1\right)$$

- $O$ is the normalised overlap of the two focal spots.
- $\Delta t$ is the true delay error, and $\tau_c \approx 70$ fs.
- $T$ is the clipping transmission of each arm.
- $C$ is the total spend. $C_\text{min}$ is the cheapest workable design for the seed's OPA wavelength and level (L1: €7,450 at 1300 nm, €950 at 600 nm, €1,700 at 450 nm; L2: €7,300 / €1,550 / €1,550; brute-forced from the catalogue with the detector model: stage, the minimum mirrors (2 in L1, 1 in L2), diagnostic + filter, and a camera that sees 1300 nm), and $C_\text{cap}$ = €30k.
- $S$ awards up to 0.2 for transmitted spatial overlap. Timing awards up to another 0.5. Cost and
  time can earn the last 0.3 only when the true final efficiency $\eta$ is at least 0.9. No points
  are awarded for reading, purchases, tool calls, or measurements themselves.
- $t_\text{lab}$ is physical lab time: alignment and scans use time, while passive information reads
  are free. The 4 h budget still caps physical work.

Diagnostics include each score component, success, O, |Δt|, T per arm, design viability, cost,
lab time, tool calls, stray-beam events and time, and footprint.

**Reward integrity**
- Every tool call, including raw HTTP calls to `/mcp`, goes through `Episode.call`, which validates
  arguments and charges physical actions inside the sim. Malformed calls cost 5 s. Passive reads
  cost no lab time and cannot improve the score by themselves.
- The agent's container holds no simulator code or state. Its only route to the sim is
  `http://sim:8000/mcp`. There are no `/state` or debug routes, and tool outputs are noisy and
  quantised.
- The verifier route is token-gated and returns 404 otherwise. The token is minted inside the sim
  container at start-up and exists nowhere else.
- After the agent's container is stopped, a Harbor `[[verifier.collect]]` hook in the sim container
  reads the final state. Reading it auto-submits the episode. The state is then handed to a
  **separate verifier container** as an artifact, so `tests/` is never in the agent's sandbox.

## Run it

On Windows, follow [the WSL 2 and Docker setup guide](docs/WINDOWS_SETUP.md), then run
`bash scripts/setup-harbor-wsl.sh` inside Ubuntu. For Gemini runs, `bash scripts/run-gemini.sh`
shows a model menu and prompts for the API key each time. Every recorded run can be replayed step by
step, with the score explained, at **<https://kakitkelvinho.github.io/gss/>** (source in `viewer/`).

```bash
harbor run -p . -a opencode -m <provider/model>   # one agent run (needs Docker)
harbor run -p . -a oracle                          # reference (scripted expert) run
GSS_SEED=3 harbor run -p . -a opencode -m <provider/model>   # another seed (default 1)
GSS_LEVEL=2 harbor run -p . -a opencode -m <provider/model>  # 90 deg crossing (default level 1)
```

After the runs, summarise them (scores plus a failure diagnosis per run) into `jobs/summary.md`:

```bash
python scripts/summarise_jobs.py jobs/
```

Without Docker:

```bash
uv sync
uv run pytest                          # 77 tests: physics, routes, L2, ledger, exploits, MCP server, Harbor flow
uv run python solution/expert.py 1 2 3 # in-process expert on seeds 1-3
uv run python scripts/baselines.py     # reference / do-nothing / stop-early over MCP -> docs/results.md
uv run python scripts/baselines.py --level 2   # same for L2 -> docs/results_l2.md
uv run python scripts/blind_playthrough.py setup <folder outside repo> --level 2   # blind test by a fresh agent (no API key)
```

## Results

Seeds 1–10, played over MCP and scored through the verifier route (full tables in
[docs/results.md](docs/results.md) and [docs/results_l2.md](docs/results_l2.md); the expert's action logs
are in [docs/expert_recipe_seed1.md](docs/expert_recipe_seed1.md) and
[docs/expert_recipe_seed1_l2.md](docs/expert_recipe_seed1_l2.md)):

| level | policy | mean R | min R | max lab time | pass criterion |
|---|---|---|---|---|---|
| 1 | reference (scripted expert) | 0.931 | 0.925 | 47.2% | η ≥ 0.9 and ≤ 65% of budget on every seed ✅ |
| 1 | do-nothing | 0.000 | 0.000 | 0.0% | R = 0 ✅ |
| 1 | stop-early (spatial overlap, no timing scan) | 0.199 | 0.197 | 39.3% | spatial credit only, R ≤ 0.2 ✅ |
| 2 | reference (scripted expert) | 0.941 | 0.935 | 55.4% | η ≥ 0.9 and ≤ 65% of budget on every seed ✅ |
| 2 | do-nothing | 0.000 | 0.000 | 0.0% | R = 0 ✅ |
| 2 | stop-early | 0.199 | 0.195 | 38.7% | spatial credit only, R ≤ 0.2 ✅ |

Raw Harbor job folders, with their verifier scores, are in [runs/harbor/](runs/harbor/). To add your
own runs to the repo and the [live viewer](https://kakitkelvinho.github.io/gss/):
`python3 scripts/publish_runs.py <your harbor jobs folder>`, then commit `runs/` and `viewer/runs/` and push;
the site rebuilds on every push to `main`.

Historical blind playthroughs by fresh Claude agents with no access to the code, under earlier task
versions ([docs/playthroughs.md](docs/playthroughs.md)):
on the first version, 1 of 3 failed (R = 0, an invisible clipping problem, since fixed) and 2 succeeded
(R ≈ 0.93); after the de-hint and buildability changes, 2 runs scored R = 0.88 and 0.72 (slower, with partial
failures such as clipping at the lens edge and timing off by backlash).

Four OpenCode + Gemini 3.1 Pro Preview trials on Level 1 (seeds 1–3, seed 1 repeated) scored
0.000 under the graded reward; all four failed to route both beams to the sample. The same-seed
reference scores are 0.925–0.933. See the [run report](docs/gemini-pro-results.md) and
[static replay](viewer/prototype.html). `python scripts/summarise_jobs.py jobs/` writes a local
score and failure summary for future runs; `python3 scripts/export_viewer_runs.py jobs`
adds finished runs as independent files in `viewer/runs/`. The static [run archive](viewer/stats.html)
aggregates recorded scores by model and level. See [contribution instructions](viewer/PROTOTYPE.md#static-run-data).

## Layout

```
task.toml, instruction.md        Harbor task (MCP server "gss" at http://sim:8000/mcp)
environment/Dockerfile           agent container (no sim code)
environment/docker-compose.yaml  adds the "sim" service
environment/sim/Dockerfile       simulator + FastMCP server
sim/                             pure-Python physics core (stdlib only): optics tracer, lab, episode, reward
server/                          FastMCP wrapper, verifier routes, Harbor collect hook
solution/                        scripted expert, MCP reference client, solve.sh
tests/                           separate verifier image + grader
docs/DECISIONS.md                design decisions (they take precedence over HANDOFF.md)
```

## Licence

MIT licence.
