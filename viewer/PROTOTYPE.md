# Throwaway visual study

Question: can a restrained, full-window lab scene match the supplied layout sketch while keeping the robot outside the optical table?

Start it from the repository root with one command:

```sh
python3 -m http.server 8766 --directory viewer
```

Open `http://localhost:8766/prototype.html`. The player floats at the top left, tool calls at the right, and score, money, and lab time below the calls. Parts and top view open from small edge buttons.

Left and right arrow keys step through calls; Space plays or pauses. Escape closes a menu. Within a menu, arrows, Home, and End move focus.

The call timeline, optics, beams, spend, lab time, and current diagnostic reward come from the bundled real run snapshots. The robot pose is illustrative and inferred from the tool name; it stands beyond the front edge of the table. The score trace shows fractional values already present in the simulator's reward. No scoring code was changed.
