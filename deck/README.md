# Pitch deck sources

`bash deck/build.sh` (Node 18+, no npm install) rebuilds `pitch-deck.html` at the repo root. Edit
these scripts, never the generated HTML.

| File | What it is |
|---|---|
| `1-build-v4.js` | Slide controls from `base-v2.html` and the charts built from data |
| `2-posters-1-2.js` | Slides 1–2 as posters |
| `3-posters-rest.js` | Slides 3–10 as posters, backup slides, palette, **and the slide data (most edits go here)** |
| `scans.json` | The scripted expert's real delay scans on seed 1; regenerate with `uv run python deck/grab-scans.py` from the repo root after the expert changes |

In the deck: arrows navigate · V video cut (slides 1–10, aim for 1:50) · N speaker notes · O overview ·
F full screen. Ctrl/Cmd+P exports the submission PDF; open it online first so the fonts load.

Still open: slide 5 (the gap) waits for the Level 2 Claude playthroughs. Its `[Model A]`/`[Model B]`
rows and the bracketed reminders in the slide 5 and 8 speaker notes still need filling in.
