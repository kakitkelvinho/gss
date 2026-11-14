# Throwaway visual study

Question: which retrofuturist layout best lets a viewer follow an optics run?

Start it from the repository root with one command:

```sh
python3 -m http.server 8765 --directory viewer
```

Open `http://localhost:8765/prototype.html?variant=A`. The floating switcher or the left and right arrow keys select three layouts:

- A, **Observatory**: large isometric view, small map inset, tool history on the right.
- B, **Lab notebook**: dedicated narrow plan column, large isometric view, right history.
- C, **Night shift**: dark instrument surface, compact plan inset, right history.

The call timeline, optics, beams, spend, lab time, and current diagnostic reward come from the bundled real run snapshots. The robot pose is illustrative and inferred from the tool name. This page is a design prototype, not the finished viewer. The score trace shows fractional values already present in the simulator's reward; no scoring code was changed.
