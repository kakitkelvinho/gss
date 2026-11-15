# Blind Claude runs: Level 2, seed 3

Why seed 3: its OPA runs at 600 nm. At the 90° crossing the cheap GaP photodiode, which looks right,
no longer clears its own single-beam backgrounds; the working route is GaN + the 550/40 filter. That's
a physics decision, not a trick, and it's the kind of choice the earlier blind run p2 got wrong at seed 1.
The new reference scores **0.942** here (`docs/results_l2.md`).

No API key is needed: each player is a fresh Claude subagent in Claude Code, given only `instruction.md`
and a CLI for the lab tools, against a local server. These are *not* Harbor runs, so say so wherever
the numbers are quoted.

## How to run it

`git pull`, open Claude Code in the repo, and paste the prompt below. If your Claude Code sandbox
blocks `uv` (it can't write `~/.cache/uv`), let it run those commands outside the sandbox.

```text
Run three blind playthroughs of this environment at Level 2, seed 3, and record the results.

1. Set up three players, each on its own port, with folders OUTSIDE the repo:
     uv run python scripts/blind_playthrough.py setup ~/gss-blind/l2s3-p1 --seed 3 --level 2 --port 8821
     uv run python scripts/blind_playthrough.py setup ~/gss-blind/l2s3-p2 --seed 3 --level 2 --port 8822
     uv run python scripts/blind_playthrough.py setup ~/gss-blind/l2s3-p3 --seed 3 --level 2 --port 8823
   Each setup prints a player prompt. Don't edit the prompts.

2. Launch three fresh general-purpose subagents in parallel, one per player, each given exactly its
   printed prompt and nothing else (no hints about the task, the physics, or this repo). Don't help
   them or answer them while they play. Wait for all three to finish.

3. Score each run (this also stops its server):
     uv run python scripts/blind_playthrough.py score ~/gss-blind/l2s3-p1
     (same for p2, p3)
   result.json and trajectory.json are saved in each player folder.

4. Write the results into docs/playthroughs.md under a new heading
   "Level 2, seed 3 (600 nm), blind Claude subagents, <today's date>": one table row per player with
   R, eta, |dt| (fs), cost (EUR), lab time %, tool calls, the parts it bought (from trajectory.json),
   and one line on what happened. Then list the difficulties the players named in their final replies,
   marking which ones more than one player raised. Note that these are not Harbor runs.

5. Show me the table, then commit only docs/playthroughs.md and push to main.
```

Hand the three player folders (`~/gss-blind/l2s3-p*`) to whoever builds the deck, if the logs are wanted.
