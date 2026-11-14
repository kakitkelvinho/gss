# Submission requirements (AfterQuery "Break the Agent" track, Junction 2026)

These are the organisers' rules as posted on Discord, followed by where this repo stands against
each one. Keep this file updated when the organisers post something new.

Deadlines (from HANDOFF.md): preliminary submission Fri 23:55, final Sun 10:00 (Helsinki).

## The rules

**Required stack**
- **Framework: Harbor** (https://github.com/laude-institute/harbor). The environment must be a Harbor
  task made of `instruction.md`, `task.toml`, `environment/Dockerfile`, `tests/` and `solution/`.
- **Harness: OpenCode** (strongly encouraged), e.g. `harbor run -p ./my-task -a opencode -m <provider/model>`.
- **Reward:** the verifier writes one score in [0, 1] to `/logs/verifier/reward.txt`. Partial
  credit is welcome.

**Before you submit**
- Include **at least one Harbor run log with its score**, showing a model playing the environment.
  Playthroughs are also encouraged in the demo video.
- Write a **short README**: what the agent has to do, why it's hard, and how it's scored.
- Submit before the deadline.

**Inference credits:** AfterQuery does **not** provide any. Use the credits from Google, OpenAI
and Modal.

**What they're looking for:** cool simulations and environments, plus some post-training experiments.

## Status of this repo

| Requirement | Status |
|---|---|
| Harbor task layout | ✅ `instruction.md`, `task.toml`, `environment/`, `tests/`, `solution/` |
| `reward.txt` in [0, 1] | ✅ `tests/test.sh` → `tests/score.py` writes `/logs/verifier/reward.txt`, plus `reward.json` (`{"reward": r}` only, since Harbor lists every key there as a reward) and `diagnostics.json`. A NaN or out-of-range reward becomes 0, and a missing state gives 0. |
| README (what / why hard / scoring) | ✅ `README.md` |
| Oracle run through Harbor | ✅ Local Docker (OrbStack), 2026-11-14, after the PR #9 merge: L1 0.908, L2 0.907 on seed 1, about 1 m 13 s each, 0 exceptions. |
| ≥ 1 OpenCode run log + score | ⬜ **Missing.** The README results table says TODO. |
| Post-training experiment | ⬜ Stretch goal (see HANDOFF.md). |

Points to keep in mind:
- **Multi-container.** The task needs the `sim` service from `environment/docker-compose.yaml`,
  `environment_mode = "separate"` and the `[[verifier.collect]]` hook. Run it on Harbor's local
  Docker backend. Before relying on a cloud backend, check that it supports compose and multiple
  services.
- **Network.** `task.toml` does not restrict the agent's internet access, so OpenCode can reach
  its LLM provider.
- **Agent timeout.** `[agent] timeout_sec = 5400` (90 min of real time). This is separate from the
  4 h of simulated lab time. If a run hits the timeout, the collect hook still auto-submits, so
  the run gets scored.

## Running it locally

One-time setup:

```bash
# Docker Desktop or OrbStack, installed and running
uv tool install harbor
uv sync && uv run pytest          # sanity check without Docker
```

1. **Oracle run (the pipeline check, do this first):**
   ```bash
   harbor run -p . -a oracle
   ```
   A reward of about 0.9 means compose, the sim healthcheck, MCP, the collect hook and the
   separate verifier all work. Local runs on 2026-11-14 (OrbStack, seed 1): 0.9188 before the
   Level 2 merge; after it, L1 0.908 and L2 0.907. Re-check after any change to the sim or the
   expert.

2. **OpenCode run (this is the run log the submission needs).** Use a Google or OpenAI model, since
   those are the providers we have credits for:
   ```bash
   export GEMINI_API_KEY=...       # or OPENAI_API_KEY=...
   harbor run -p . -a opencode -m google/<gemini-model> -o ./jobs
   harbor run -p . -a opencode -m openai/<gpt-model>    -o ./jobs
   ```
   - For exact model IDs, run `opencode models` or check the provider's list. Check how Harbor's
     OpenCode agent passes the API key into the container. Some providers expect
     `GOOGLE_GENERATIVE_AI_API_KEY` instead of `GEMINI_API_KEY`.
   - Then check that the agent actually calls the `gss` MCP tools, and that `reward.txt` and
     `diagnostics.json` were written.
   - Copy the job directory (or its key log and the score) into the repo and fill in the README
     results table.

3. **Other seeds and levels:** `GSS_SEED=3 harbor run ...` and `GSS_LEVEL=2 harbor run ...`.
   Compose reads `${GSS_SEED:-1}` and `${GSS_LEVEL:-1}` from the host environment, and Harbor
   passes them through. This was verified on 2026-11-14: a `GSS_LEVEL=2` run showed `"level": 2`
   in `verifier/diagnostics.json`. Check `"seed"` and `"level"` there if in doubt.

4. **Summarise:** `python scripts/summarise_jobs.py jobs/` writes `jobs/summary.md` (scores plus
   a failure diagnosis per run). It reads `diagnostics.json`.

Local machine setup (macOS, Apple Silicon): OrbStack provides Docker (`brew install orbstack`),
and Harbor is installed with `uv tool install harbor`. Harbor writes job folders to `jobs/`, which
is gitignored. Run every `harbor` command from the repo root.

## Discord Q&A notes

- Other teams have asked which models the organisers will use, whether multi-container works on
  their side, and whether they use a fixed agent timeout. No answer seen yet. All three matter for
  us (see above). Questions about Unity or venue times don't apply to us.
