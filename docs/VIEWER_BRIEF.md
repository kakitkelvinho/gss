# GSS run viewer: design brief

This is a brief for refining the interface before implementation. The viewer explains what a model did while playing the **Find Time Zero** simulated optics lab. It is a separate, read-only presentation tool. It does not control the lab or change scoring.

## What a viewer should understand

At any selected tool call, a viewer should be able to answer:

1. What action did the model take, with which arguments, and what did the tool return?
2. Which parts had it bought and placed, where were they, and where did the two beams travel?
3. Did the beams reach the sample, overlap in space, and arrive together in time?
4. How much simulated lab time and money had been spent?
5. Where did the run diverge from a successful alignment?

The agent only receives noisy instrument outputs. The replay may show simulator truth for explanation, but must label it **private replay diagnostic**. A live viewer, if added later, must keep that truth inaccessible to the playing agent.

## Main layout

The centre is split into **two synchronised windows**:

| Window | Purpose | Presentation |
|---|---|---|
| Top-down | Inspect layout and beam routing precisely | Scaled 2400 × 1200 mm table; coordinate grid, ports, components, beam paths, sample and clipping or termination points. Zoom and pan if useful. |
| Isometric | Make the physical setup and height changes legible | A 2D projection of the same 3D positions, with flat shaded component drawings and depth ordering. Show periscopes, mirror heights, sample mount and raised beam segments. This is illustrative, like an isometric strategy game, not a 3D engine. |

Use a consistent colour for the 800 nm arm and another for the OPA arm in both windows and the console. The top-down window is the geometric reference. The isometric window should make the setup easy to understand in a video without pretending to show millimetre-scale offsets accurately.

A side pane is a **tool-call console**: numbered calls, simulated timestamps, tool name, compact arguments, and the returned outcome or measurement. Selecting a call sets both windows to the state *after* that call. An expanded entry may show the full tool response. Failed calls and `submit` should be visually distinct.

A playback bar spans the two views: step backward and forward, play/pause, speed, scrubber, current call/total calls, and simulated lab time. Keyboard shortcuts are welcome if they stay discoverable. A small readout shows spatial overlap `O`, timing error `Δt`, beam transmission, spent euros, and final reward when available. Make clear which values the agent could observe and which are private replay diagnostics.

## Playback first; live later

The first milestone loads a finished Harbor run from its exported `trajectory.json` and `diagnostics.json` files. It should run locally from repo-owned code, without an AI Studio account or hosted service. Playback is enough to record the submission video and can be paused on a failure.

The existing trajectory already has each call's `tool`, `args`, compact `result`, `t_s`, and hidden `truth`. It does **not** yet contain the complete true component poses and traced beam segments needed for accurate table drawings. Add those as **verifier-only visual snapshots** after each action, using the simulator's current state. Both views must consume the same snapshot rather than independently guessing the beam paths from tool arguments. Keep the visual snapshot outside MCP tool responses.

A later live mode could display the same snapshots as they arrive through a separate observer path. It should not be part of the first milestone or create a path for the agent to read hidden state.

## Suggested first demo sequence

1. Start with an empty table and the two closed-shutter output ports.
2. Play through reading manuals, buying parts, and placing optics; show the table filling in both views.
3. Pause on camera or IR-card measurements and the steering calls that follow them.
4. Show the delay-stage scans and the approach to time zero.
5. End on the final score, then compare with a model run that failed or spent too much time.

Expert and model runs should be selectable in the same viewer. Side-by-side run comparison is optional; switching between runs is enough for the first version.

## Boundaries

- Build the viewer and its drawings in this repo. Do not copy QUOP code or assets or modify QUOP for this event.
- Keep it read-only. The simulator and Harbor remain the source of truth for actions and scores.
- Preserve the existing agent-visible MCP tool responses and the verifier token boundary.
- Prefer a small web page using SVG or Canvas for the two projections. Avoid a 3D engine and external hosting for the first version.
- Export any files needed for the video from the repo before the temporary Google account expires.

## Implementation handoff

Relevant files: `sim/episode.py` records the trajectory; `sim/optics.py` computes actual beam traces; `server/collect.py` exports verifier data; `tests/score.py` copies it into Harbor job artifacts. Sample finished runs are under `jobs/` (gitignored). The work should be developed in a separate branch or worktree if another agent is also editing the simulator.

Before writing the UI, agree on one versioned snapshot schema, including units and whether coordinates are `(x, height, z)` or `(x, z, height)`. The simulator uses `(x, height, z)` internally while tool arguments use separate `x`, `z`, and `height` fields.
