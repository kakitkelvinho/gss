# Throwaway visual study

Question: can a restrained, full-window lab scene match the supplied layout sketch while keeping the robot outside the optical table?

Start it from the repository root with one command:

```sh
python3 -m http.server 8766 --directory viewer
```

Open `http://localhost:8766/prototype.html`. Playback floats at the top left. The call rail groups each optic's setup and can be collapsed to give the scene more room. Expand a group to inspect its individual calls. Money and lab time lead the telemetry; the private replay score is secondary. Run, speed, parts, and top view use the same small menu pattern.

Left and right arrow keys or comma and period step through calls; Space plays or pauses. Escape closes a menu. Within a menu, arrows, Home, and End move focus. The current call's coordinate marker and the table's axis labels use millimetres.

The call timeline, optics, beams, spend, lab time, and current diagnostic reward come from the bundled real run snapshots. The robot pose is illustrative and inferred from the tool name; it stands beyond the front edge of the table. The score trace shows fractional values already present in the simulator's reward. No scoring code was changed.

The worker is a segmented cut-paper mannequin inspired by the *Anatomy of a Murder* poster. The table is projected from its 2400 × 1200 mm coordinates with a 25 mm hole pattern and a 40 mm drawn edge thickness. Optical mounts and beam paths use replay positions; mount bases attach to the table plane while optic heads remain at snapshot beam height. Source housings attach to the replay's output port positions. The charcoal room, lighter breadboard, pale metal mount details, and distinct red/violet beam colours keep the physical layout readable. The mount drawings show recognizable hardware, but their visible dimensions are illustrative rather than CAD models.
