# Player l2s3-p1: final report (seed 3, level 2, blind Claude subagent)

I submitted with both pulses overlapped in space and, I'm fairly sure, in time. I used 130.1 of the 240 lab minutes (109.9 left) and spent EUR 1,400 of the 30,000 cap.

**Parts (one order):** DL-M25 manual 25 mm delay stage (400), 3 x MIR-1 mirrors (450), GAP-TPA GaP photodiode (250), PD-SI Si photodiode (300).

**Layout** (positions in mm; sample at x=1080, z=500, height 159, yaw 0, so the 800 nm beam goes through lens A and the OPA through lens B, crossing at 90 deg):
- **800 nm arm:** port → mirror-1 at (1500, 205), height 124, yaw 45, which sends the beam +z → retroreflector on the stage (reference at (1500, 955.5), rail yaw 90).
  - I set the retroreflector's apex height to 141.5, so the beam comes back 35 mm higher, at 159. That matches the OPA height, so no periscope was needed.
  - The returning beam passes over mirror-1 to mirror-2 at (1500, 89.7), height 159, yaw 112.5, which sends it to the sample along 135 deg.
- **OPA arm:** port → mirror-3 at (1377.9, 804), height 159, yaw 292.5 → sample along 225 deg.
- The only adjustments were moving mirror-2 and mirror-3 and turning their yaw and pitch knobs.

**What I measured:**
- **Spatial overlap:** on the sample camera both focal spots ended within about 3 µm of h=v=0 (radii about 75 x 50 µm). On the lens camera, lens A was hit about (0.7, 0.1) mm off centre and lens B about (1.1, -0.1) mm. Relative power at the sample was 1.00 for the OPA and about 0.77–0.80 for 800 nm.
- **Coarse timing:**
  - Manuals: path from the split is 642 mm for 800 nm versus 409 + 2112 = 2521 mm for the OPA.
  - Tape measure on the table: 3162.4 mm for 800 nm and 1302.3 mm for the OPA, so 800 nm was about 19 mm short at stage position 12.5.
  - PD-SI: the OPA arrived about 75 ps later (about 22 mm). Both point to a stage position around 22–24.
- **Fine timing:** a GaP two-photon cross-correlation, with a background of about 1715 counts from each beam alone.
  - Fast scans at 0.05–0.1 s per point showed nothing, because laser-energy noise (about 200 counts) hid the peak.
  - Scans at 1–2 s per point found a peak of about +250 to +300 counts at stage 21.46 mm, with a FWHM of about 50 µm on the stage (about 330 fs). That is wider than the pulses, as expected when the delay varies across the spots at a 90 deg crossing.
- **Final setting:** a Gaussian fit put the centre at 21.463 mm. I moved the stage there approaching from below (to avoid backlash) and confirmed about 2050 counts there before submitting.

**Time zero:** yes, I believe so, to roughly ±20 fs. The peak showed up at the same place in three separate scans and agrees with the tape and photodiode estimates.

**Three biggest difficulties:**
1. **A weak, noisy timing signal.** The cross-correlation peak is only about 15% above the background and the noise is dominated by pulse-energy fluctuation, so integration time matters much more than step size. I wasted about 30 minutes on fast scans before switching to 1–2 s per point. The docs give no hint of how large the cross signal is, or that the 90 deg crossing smears and weakens it.
2. **Knob signs and mirror moves.**
   - The manual gives the beam's turning sense, but not which way that moves a spot in the sample or lens camera frames. I got the sign wrong for yaw and had to measure it.
   - I also mixed up the angle of incidence (22.5 vs 67.5 deg) in the pitch factor. That was my mistake, not the docs'.
   - `move` seems to add a yaw re-seat error of several mrad, though the manual only mentions re-seat error for `rotate`, so each move needed re-correcting with the knobs.
3. **Unclear docs and efficiency.**
   - The signal camera's "no specified response" outside 400–1000 nm, and BBO phase-matching at a 90 deg crossing, make it unclear which diagnostic is meant to work for 600+800 nm. Nothing confirms that GaP two-photon absorption works across the gap except trying it.
   - The 800 nm arm delivers only about 0.8 of its power, apparently from five reflections (two silver mirrors plus three in the gold retroreflector). If "physical efficiency ≥ 0.9" uses that number, my layout may lose the spend and time bonus. The task brief doesn't define that efficiency, so I couldn't tell during the run.
   - Shutters and camera reads happen at the desk while knobs are at the table, so every check costs a walk.
