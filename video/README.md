# Pitch video

The 2-minute pitch video is rendered from this repo; the video file itself is not kept in git.

- `v2/music.py`: the original score, synthesized from scratch (A minor, 100 BPM, 48 bars, 1:56). Writes `v2/score.wav`.
- `v2/render.py`: the shot list (camera keyframes, words, timings) and the frame renderer. It drives the lab
  viewer and `pitch-deck.html` in headless Chromium.
- `v2/make_video.py`: renders the shots in parallel (about 8 minutes on 5 workers, hard limit 20) and adds the score.

```bash
uv run python scripts/serve_viewer.py &                                           # the lab viewer on :8766
uv run --no-project --with playwright python -m playwright install chromium       # once
uv run --no-project --with numpy --with scipy python video/v2/music.py            # writes video/v2/score.wav
uv run --no-project --with playwright --with pillow --with imageio-ffmpeg python video/v2/make_video.py
```

On a bare WSL Ubuntu, Chromium may also need `libnss3`, `libnspr4` and `libasound2`.
