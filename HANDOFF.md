# Handoff: GSS — "Find Time Zero" — Junction 2026, AfterQuery "Break the Agent"

Team: **God's Strongest Soldiers (GSS)**. Project / repo / Harbor task name: **`gss`** (task id `gss/find-time-zero`).

Paste this whole file into a fresh Claude Code session as the first message.

## 0. One-paragraph pitch and final goal
**Final goal (what the agent must achieve):** starting from an empty table with two ultrafast beams (pump and probe), buy the cheapest set of parts that can work, then bring the two pulses into spatial and temporal overlap at the sample position, i.e. find *time zero*, within 4 h of simulated lab time. Success is measured from the simulator's true state: how well the beams overlap at the sample in space and time, with a small penalty for overspending.

**Why it matters:** lab agents are a hot area. OpenAI's BioBasicsBench tests whether agents can *interpret* raw wet-lab data. GSS tests whether an agent can *act* in a physical lab loop: plan a setup, take noisy measurements, and converge on a precise physical target under a time budget. Pump–probe alignment is a standard ultrafast-optics procedure that experts do routinely and that takes skill, not trivia.

## 1. Goal
Build a Harbor task (an RL environment) in which an AI agent must **design and align a generic pump–probe setup** in a physics simulator: choose parts as cheaply as possible, lay out the delay, then find spatial and temporal overlap ("time zero") at the sample. Frontier agents should fail for explainable reasons; a scripted expert (our reference run) should succeed. The reward is computed from simulator truth and must be unhackable.

Pitch framing: pump–probe overlap is a **standard ultrafast-optics technique**, notoriously fiddly in practice. No lab- or sample-specific details.

Stretch: post-train a small open model on experience from the environment and show it improves (tiebreaker).
Fallback: same architecture with a **cavity-locking (PDH)** task.

Team: two physics PhDs + a physics intern. Strong in optics, newer to Docker/MCP/ML. **JavaScript (Node) for simulator and MCP server**; Python only for fine-tuning.

**Guiding rule: a small environment that works end to end beats a rich one that doesn't reproduce.**

## 2. Challenge facts (from the Junction page)
- Harness: **Harbor** running the **OpenCode** agent, connecting to our environment over **MCP**. AfterQuery gives a scoring skeleton + starter kit on site (get the link from mentors; adapt to it).
- Judges rerun: our reference run, 3 agent runs, a do-nothing baseline, a stop-early baseline; then 15 min hunting reward exploits.
- Rubric: The gap 30 · Meaningful difficulty 30 · Reward integrity 25 · Craft 15 (one-command reproducible run from README).
  - Zero on "meaningful difficulty" if the gap comes from withheld info, trick wording, impossible timing or broken tools.
- Deadlines: preliminary submission Fri 23:55, final Sun 10:00 (Helsinki).

## 3. Harbor task layout (docs: https://docs.harborframework.com)
```
gss/                        # repo root; Harbor task inside
├── instruction.md          # prompt the agent sees
├── task.toml               # config; MCP server under [[environment.mcp_servers]]
├── environment/            # docker-compose: agent sandbox + SEPARATE sim container
├── solution/solve.sh       # reference (oracle) run: scripted expert, same MCP tools
└── tests/test.sh           # verifier: queries sim for true final state → /logs/verifier/reward.txt
```
Run: `harbor run -p ./gss -a opencode -m <model> -k 3 -o ./jobs` (task `[task] name = "gss/find-time-zero"` in task.toml)

### Sim interface lock-down
- OpenCode has a shell and may call the MCP endpoint directly (e.g. curl). That's fine **only if every action goes through the same time/cost accounting**, which lives **inside the sim**, never in the MCP layer.
- No `/state`, debug or admin routes reachable from the agent container. The verifier talks to the sim on a separate, non-agent-reachable route/network (or a verifier-only token).
- Tool outputs never leak true values: all readings carry realistic noise and resolution (e.g. camera centroids quantised to pixels plus noise, not exact µm).
- Sim source and hidden state live in the sim container only.

## 4. Episode structure

### No method hints
`instruction.md` gives **goal and constraints only**:
- Goal: overlap pump and probe in space and time at the sample position, as cheaply as possible, within 4 h of lab time.
- Given: source specs (pump 800 nm, ~100 fs, 1 kHz amplifier; probe from an OPA at a stated wavelength), required geometry at the sample, table layout, the tools.
- **Not** told: which nonlinear process, crystal, detector, stage or alignment procedure to use.
- Fairness: everything needed to choose well is in the catalogue, datasheets and manuals (phase-matching data, detector bandwidths, TPA response, stage travel, OPA internal path). No trick wording.

### Phase A: design (small catalogue, fixed slots)
Start with **~12–15 items in fixed slots, one item per slot** (keeps $C_\text{min}$ brute force trivial):

| Slot | Example options (cheap-inadequate vs adequate) |
|---|---|
| Fine delay stage | short-travel manual · 25 mm motorised · 100 mm motorised |
| Coarse delay | none · fold-mirror pair on rail (adds path in pump arm) |
| Overlap diagnostic | camera/pinhole (spatial only) · fast photodiode (~ns timing) · TPA photodiode (GaAsP) · BBO cut for the wavelengths · BBO wrong cut |
| Detection electronics | scope only · lock-in + chopper |

- Simulated vendor catalogue, Thorlabs-style (realistic specs and price ranges, fictional vendor/part numbers).
- Tools: `list_catalogue(slot)`, `get_datasheet(part_id)`, `buy(part_id)`. Hard cap only against absurd spending (e.g. €30k).
- **The diagnostic sits at the sample plane**, and swapping it causes no path change (matches lab practice).
- Wrong choices fail **physically** (no signal, too coarse, can't reach overlap), never as error messages.
- Grow the catalogue (more crystals/cuts, L2-specific parts) only after the end-to-end path works.

### Coarse path (central to the task)
- The probe arm carries the OPA's **1.6 m internal path** (only in the OPA manual). The fine stage gives ~20 cm of path (10 cm travel × 2), so it can't cover the mismatch.
- The agent must add path to the pump arm: `set_coarse_delay(length)` via the fold-mirror pair/rail (must be bought), with realistic placement accuracy (~mm) and a lab-time cost.
- So the manual lookup becomes a **planning decision**: without it, the agent lays out the wrong table and the fine stage never reaches time zero.

### Phase B: align and find time zero
Tools (every action costs simulated lab time inside the sim; budget **4 h**):
- `read_manual(device)`, `measure_path(arm)` → ±5 mm (tape measure; can't see inside the OPA).
- `steer(mirror, axis, delta)`: two mirrors per arm (beam-walking coupling).
- `view_camera()` → noisy, pixel-quantised spot centroids at the sample plane (spatial only).
- `block(arm)` / `unblock(arm)`.
- `move_stage(x)`, `read_signal(t_int)`.
- `scan(start, end, step, t_int)` → **returns the whole array in one call** (keeps episodes to ~60–100 tool calls).
- `submit()` → ends the episode.

### Difficulty levels (set by the required geometry, not by hints)
- **L1:** collinear geometry allowed at the sample.
- **L2:** beams must cross at **full angle $\varphi = 90°$** at the sample (each ±45° from normal). Arrival-time difference across the spot: $\Delta t(x) = 2x\sin(\varphi/2)/c$. For $w = 50\,\mu$m that's ≈ 240 fs across the spot, which broadens and weakens any cross-correlation signal. (Write the angle convention in code comments; physics review checks it.)
- Optional L3: probe wavelength randomised per seed, so the right crystal/cut changes.

### Realistic difficulty mechanics (all discoverable, all fair)
- **Narrow window:** $\tau \approx 100$ fs ≈ 30 µm of path vs a 20 cm stage path range.
- **Decoys:** each arm alone gives its own nonlinear background (single-beam SHG or TPA). The cross term is the delay-dependent part, identifiable with `block(arm)`.
- **Noise vs time:** short `t_int` hides the peak; long `t_int` burns budget.
- **Step size:** steps $> c\tau/2$ jump over the peak.
- **Coarse path:** the internal OPA path from the manual.

## 5. Reward (tests/test.sh)
Reward is computed from **true sim state, independent of which detector was bought**; the detector is only a diagnostic:

$$\eta = O_\text{spatial} \cdot \exp\!\left[-\left(\frac{\Delta t}{\tau_c}\right)^2\right]$$

with $O_\text{spatial}$ the normalised spatial overlap integral of the two beams at the sample, $\Delta t$ the true delay error at submit/time-out, and $\tau_c$ the cross-correlation width.

$$R = \eta\left(1 - \alpha\,\frac{C - C_\text{min}}{C_\text{cap} - C_\text{min}}\right),\quad \alpha \approx 0.2$$

- $C_\text{min}$ = cheapest design that can **physically reach overlap** (stage plus coarse delay covers the mismatch, and the diagnostic can resolve time zero), regardless of how well anyone aligns it. Brute force over the slots.
- Overlap dominates: a cheap design that never finds time zero scores ≈ 0. Unused lab time is not rewarded.
- Do-nothing / stop-early → ≈ 0 (episodes start far from temporal overlap, with imperfect spatial overlap).
- **Log diagnostics alongside the reward** in `reward.json` or logs, **not** in the reward: $O_\text{spatial}$, $|\Delta t|$, design viable (yes/no), cost, lab time used, number of tool calls. Use them for failure analysis, the demo and SFT filtering.
- Exploit checklist: invalid/huge/NaN arguments, negative values, direct HTTP calls bypassing accounting, debug routes, tools after submit, free repeated reads, scan spam, timeouts, log editing, buying nothing/everything.

## 6. Reference run (solution/solve.sh)
A scripted expert using the same tools (encodes experimentalist taste):
1. Read the manuals and measure both paths.
2. Buy the cheapest viable design.
3. Set the coarse delay to cancel the mismatch, including the OPA internal path.
4. Get spatial overlap on the camera.
5. Optionally check coarse timing on a fast photodiode.
6. Use `block(arm)` to identify the cross term.
7. Scan ±5 mm with step $< c\tau/4$ and adequate $t_\text{int}$.
8. Hill-climb delay and mirrors, then submit.

Target ≥ 0.9 reliably. Its action log doubles as a step-by-step lab recipe (parts list, cost, time): a by-product, not the scored deliverable.

## 7. Failure analysis (the 30-point "meaningful difficulty")
The real gap will likely come from **execution**, not the parts list. Make these easy to show from the logs:
- step sizes larger than $c\tau/2$;
- integration times too short to see the peak above noise;
- mistaking a single-arm signal for the cross term;
- burning the 4 h budget on broad scans;
- never reading the OPA manual, so the coarse delay is wrong.

## 8. Post-training (stretch; keep it minimal)
- A custom loop: the small model outputs one JSON action per turn to the sim (not OpenCode).
- SFT a small open model (e.g. Gemma 1–4B, LoRA via Unsloth/TRL on one Modal/Verda GPU) on oracle trajectories plus the best frontier trajectories (filtered with the diagnostics).
- Compare before/after on ~10 fixed seeds. A modest improvement is enough for the tiebreaker. **Must not eat Saturday.**
- Ask the AfterQuery mentor which stack he used for his overnight post-training.

## 9. Order of work
1. **Fri night, walking skeleton:** L1 sim with ~6 items, MCP server, Harbor task, verifier, reference run, one frontier run. Is there a gap, and where does the agent fail?
2. **Sat AM:** fill the catalogue to 12–15 items, harden the interface, one-command README with a results table (reference, 3 agent runs, do-nothing, stop-early). Mentor check on the idea.
3. **Sat PM:** L2, failure-analysis write-up; mentor exploit test.
4. **Sat night:** minimal post-training; replay viewer (HTML/JS, agent vs expert) for the demo.
5. **Sun AM:** freeze, reproduce from a clean clone, submit by 10:00.

## 10. Risks / sanity checks
- If L1 is too easy (frontier models know the textbook recipe), move to L2/L3 and tighten time per action; don't add unfair obscurity.
- If the agent fails because a datasheet lacks a needed number, fix the datasheet.
- Physics review of every catalogue number and the signal model (phase matching, TPA $\propto I_1 I_2$, noise, L2 angle convention) before measuring the gap.
- No API keys in the repo; fixed seeds everywhere.

## 11. Open questions for AfterQuery mentors
Starter-kit/scoring-skeleton repo · which frontier model + effort · exact stop-early baseline · one task vs many seeded episodes · separate sim container OK? · their post-training stack.
