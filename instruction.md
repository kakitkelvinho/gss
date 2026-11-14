# Find time zero

You are working in a (simulated) ultrafast optics lab. You control it **only through the tools of
the MCP server `gss`**. Each tool call is an action in the lab and costs simulated lab time.

## Goal

Bring the **pump** and **probe** pulses into **spatial and temporal overlap at the sample position**
(the focal plane of the sample-mount lens): both beams focused onto the same spot, and both pulses
arriving at the same time ("time zero"). Then call `submit`.

Do it **as cheaply as possible** and within **4 hours of lab time**.

## What you have

- An empty 1200 x 2400 mm optical breadboard with two laser outputs on it:
  - **pump**: 800 nm, ~100 fs (FWHM), 1 kHz amplifier output;
  - **probe**: 1300 nm, ~60 fs (FWHM), from an optical parametric amplifier (OPA) pumped by the same amplifier.
- Their positions, heights and directions, the table coordinates, and everything else about this
  particular lab are in the manuals (`read_manual`). Both shutters start closed.
- A sample mount with a lens and a camera, an oscilloscope, an IR viewer card, and a desk.
- A parts catalogue (`list_catalogue`, `get_datasheet`, `buy`). Total spend is capped at EUR 30,000.

## Rules

- Only the tools change the lab. Every action takes lab time; walking around the table takes time too.
- The episode ends when you call `submit` or when the 4 hours of lab time run out (whatever state the lab is in then is scored).
- After the episode ends, every tool returns "episode over".

## Scoring

The score (0 to 1) is computed from the simulator's true final state:

- how well the two focal spots overlap at the sample, times
- how close the two pulses are in time (the overlap window is about 100 fs), times
- how much of each beam actually reaches the sample,

reduced by up to 20% for spending more than the cheapest set of parts that could do the job, and by up to
10% for the lab time used (10% if you use all 4 hours).
