# Find time zero

You are working in a (simulated) ultrafast optics lab. You control it **only through the tools of
the MCP server `gss`**. Physical actions cost simulated lab time; reading information is free.

## Goal

Bring the **800 nm** and **OPA** pulses into **spatial and temporal overlap at the sample position**
(the focal plane of the sample-mount lens): both beams focused onto the same spot, and both pulses
arriving at the same time ("time zero"). Then call `submit`.

Do it **as cheaply as possible** and within **4 hours of lab time**.

## What you have

- An empty 1200 x 2400 mm optical breadboard with two laser outputs on it:
  - **800nm** arm: 800 nm, ~100 fs (FWHM), 1 kHz amplifier output;
  - **opa** arm: ~60 fs (FWHM), from an optical parametric amplifier (OPA) pumped by the same amplifier.
    Its output wavelength differs from lab to lab; this lab's is in the table manual.
- Their positions, heights and directions, the table coordinates, and everything else about this
  particular lab are in the manuals (`read_manual`). Both shutters start closed.
- The sample mount's manual says how the two beams have to arrive at the sample (this lab's required
  geometry).
- A sample mount with a lens, an alignment camera and a signal camera, an oscilloscope, an IR viewer card, and a desk.
- A parts catalogue (`list_catalogue`, `get_datasheet`, `buy`). Total spend is capped at EUR 30,000.

## Rules

- Work in steps: plan briefly, then call a tool, and keep going from what the tools return.
- Only the tools change the lab. Physical actions take lab time; walking around the table takes time too.
  `status`, `list_catalogue`, `get_datasheet`, and `read_manual` take no lab time.
- The episode ends when you call `submit` or when the 4 hours of lab time run out (whatever state the lab is in then is scored).
- After the episode ends, every tool returns "episode over".

## Scoring

The score (0 to 1) is computed from the simulator's true final state:

- up to 0.2 for transmitted spatial overlap at the sample;
- up to 0.5 more for temporal overlap (the overlap window is about 100 fs);
- up to 0.2 for low spend and 0.1 for lab time left, awarded only when final physical efficiency
  is at least 0.9.

Reading, buying parts, and making measurements do not earn points on their own.
