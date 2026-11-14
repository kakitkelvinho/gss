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
and so on. Every action costs lab time, and walking around the table costs time too.

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

$$\eta = T_{800}\,T_\text{opa}\;O\;\exp\!\left[-\left(\frac{\Delta t}{\tau_c}\right)^2\right],\qquad
R = \eta\left(1 - 0.2\,\frac{C - C_\text{min}}{C_\text{cap} - C_\text{min}} - 0.1\,\frac{t_\text{lab}}{4\,\text{h}}\right)$$

- $O$ is the normalised overlap of the two focal spots.
- $\Delta t$ is the true delay error, and $\tau_c \approx 70$ fs.
- $T$ is the clipping transmission of each arm.
- $C$ is the total spend. $C_\text{min}$ is the cheapest workable design for the seed's OPA wavelength (€7,750 at 1300 nm, €1,250 at 600 nm, €2,000 at 450 nm; brute-forced from the catalogue with the detector model), and $C_\text{cap}$ = €30k.
- $t_\text{lab}$ is the lab time used: every action takes physical time, so brute-force iteration (swarm-style knob searches, blind scans) is penalised softly here and hard-capped by the 4 h budget.

Diagnostics go to `reward.json` but are not part of the reward: O, |Δt|, T per arm, design
viability, cost, lab time, tool calls, stray-beam events and time, and footprint.

**Reward integrity**
- Every action, including raw HTTP calls to `/mcp`, goes through `Episode.call`, which validates
  arguments and charges lab time inside the sim. Malformed calls cost 5 s, and every action costs
  at least 5 s.
- The agent's container holds no simulator code or state. Its only route to the sim is
  `http://sim:8000/mcp`. There are no `/state` or debug routes, and tool outputs are noisy and
  quantised.
- The verifier route is token-gated and returns 404 otherwise. The token is minted inside the sim
  container at start-up and exists nowhere else.
- After the agent's container is stopped, a Harbor `[[verifier.collect]]` hook in the sim container
  reads the final state. Reading it auto-submits the episode. The state is then handed to a
  **separate verifier container** as an artifact, so `tests/` is never in the agent's sandbox.

## Run it

```bash
harbor run -p . -a opencode -m <provider/model>   # one agent run (needs Docker)
harbor run -p . -a oracle                          # reference (scripted expert) run
GSS_SEED=3 harbor run -p . -a opencode -m <provider/model>   # another seed (default 1)
```

After the runs, summarise them (scores plus a failure diagnosis per run) into `jobs/summary.md`:

```bash
python scripts/summarise_jobs.py jobs/
```

Without Docker:

```bash
uv sync
uv run pytest                          # 42 tests: physics, ledger, exploits, MCP server, Harbor flow
uv run python solution/expert.py 1 2 3 # in-process expert on seeds 1-3
uv run python scripts/baselines.py     # reference / do-nothing / stop-early over MCP -> docs/results.md
```

## Results

Seeds 1–10, played over MCP and scored through the verifier route (full table in
[docs/results.md](docs/results.md); the expert's action log is in
[docs/expert_recipe_seed1.md](docs/expert_recipe_seed1.md)):

| policy | mean R | min R | max lab time | pass criterion |
|---|---|---|---|---|
| reference (scripted expert) | 0.919 | 0.915 | 63.5% | η ≥ 0.9 and ≤ 65% of budget on every seed ✅ |
| do-nothing | 0.000 | 0.000 | 0.0% | R < 0.05 ✅ |
| stop-early (viable design + spatial overlap, no timing scan) | 0.000 | 0.000 | 47.7% | R < 0.05 ✅ |

Frontier-agent runs (OpenCode): *TODO, these need inference credits.* Add the Harbor job logs and
scores here.

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

## Disclosure

All code was written at the event. **QUOP** (https://kakitkelvinho.github.io/quop/, the author's own
earlier open-source tool) is planned only as a replay *viewer*. No QUOP code is copied, and the
exporter has not been written yet.

MIT licence.
