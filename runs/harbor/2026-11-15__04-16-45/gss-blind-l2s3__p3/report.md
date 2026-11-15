# Player l2s3-p3: final report (seed 3, level 2, blind Claude subagent)

I submitted. I believe I found time zero: a clear cross-correlation peak at delay stage position 12.754 mm, with both focal spots overlapped to within about 10 µm.

**Time and money:** I used 125.8 min of the 240 min of lab time and spent EUR 1,250 of the EUR 30,000 cap, in one buy order.

**Parts bought:** 2x MIR-1 mirrors, DL-M25 manual 25 mm delay stage, GAP-TPA GaP photodiode, PD-SI fast Si photodiode. No periscope, no filters, no crystals, no camera.

**Layout** (coordinates x, z, height in mm):
- **Sample mount:** at (988, 500, 159), yaw 0. Lens A axis is at 135°, lens B at 225°.
- **800 nm arm:** port (2250, 205, h124) → retroreflector on the stage (rail yaw 180°, reference point at (452.5, 201.5), apex height 139) → mirror-1 at (1290, 198, 159), yaw 157.5° → lens A.
  - The 800 beam passes 15 mm below the retroreflector apex, so it comes back about 30 mm higher (about 154), close to the OPA height. I fixed the 35 mm height difference between the arms this way, with no periscope.
  - The leftover 5 mm height difference doesn't matter: where the focus lands depends only on the beam's angle, not on where it hits the lens.
- **OPA arm (600 nm):** port (2250, 804, h159) → mirror-2 at (1292, 804, 159), yaw 292.5° → lens B.

**What I measured:**
- **Tape-measured paths (stage at 0):** 800 arm 3240.3 mm, OPA arm 1383.7 mm.
- **Expected stage position from the manuals:** the 800 arm needs 2521 − 642 = 1879 mm more table path than the OPA arm. That gives a stage position of about 11.2 mm.
- **PD-SI arrival times:**
  - Stage at 0: the 800 pulse arrived 60 ps before the OPA pulse.
  - Stage at 11: no difference within the 20 ps sampling.
- **GaP backgrounds:** 800 alone gave about 1473 counts and OPA alone about 822; both together about 2300 off overlap.
- **GaP scans:**
  - A first scan from 8 to 14 mm (step 0.012, 0.05 s per point) was too noisy to show anything; per-point noise was about 15%.
  - A second pass (step 0.015, 0.3 s) showed a hint near 12.75.
  - Fine scans (1 s and 3 s per point) showed a clear peak of about +350 to +450 counts on top of the 2300, about 0.07 mm wide in stage position. The centroid was 12.753 in one scan and 12.754 in the other.
- **Final state:** stage at 12.754. On the alignment camera the spots sit at (8, −29) µm and (13, −25) µm, radius about 75 x 52 µm. Both beams reach the sample at 1.01 relative power.

**Biggest difficulties:**
1. **Clipping at the retroreflector.** My first retroreflector placement (apex height 141.5, 17.8 mm off the beam centre) passed only 0.49 of the 800 power, even though the stated clear aperture is 19.1 mm radius. Lowering the offset to about 15 mm brought it back to 1.0. The real usable aperture seems smaller than the datasheet says, or the clipping happens somewhere I couldn't see. The IR card reports positions but not power, so finding where power was lost took guessing and about 20 min of re-placing the stage.
2. **A weak, broadened GaP signal.** The cross signal is only about 15–20% above the two single-beam backgrounds. The 90° crossing smears it to about 470 fs wide. My first fast scan missed it, and I spent about 50 min of scanning in total. The noise is set by how long you integrate, but the manual stage costs about 3 s per point anyway. Neither the scan speed nor how strong to expect the signal was obvious in advance.
3. **Unclear tools and docs:**
   - `place` refuses a part that is already on the table, and `move` keeps the height. Changing a height means remove plus place (about 6 min).
   - The stage starts at position 0, not mid-travel.
   - The 20 ps sampling quantises the PD-SI arrival times, so they only roughly confirmed the manual's path numbers.
   - It wasn't clear whether polarisation affects the GaP cross term: both beams are horizontally polarised, which makes their fields perpendicular at a 90° crossing.
   - It wasn't clear whether transmitted beams leaving the table count as a safety violation. I didn't check this, and I submitted with the GaP still installed.
