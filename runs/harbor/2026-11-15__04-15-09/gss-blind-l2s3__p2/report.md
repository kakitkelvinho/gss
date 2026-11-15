# Player l2s3-p2: final report (seed 3, level 2, blind Claude subagent)

I submitted at 97.4 min of lab time (142.6 min left) after spending EUR 1,900 in one order. I think I found time zero: the delay stage is at 11.896 mm, and both beams are focused on the sample point, overlapping to within about 2 µm, with relative_power about 1.0 for each.

**Parts (one order):** PD-SI EUR 300, GAP-TPA EUR 250, DL-M25 manual 25 mm stage EUR 400, PER-1 periscope EUR 500, and 3 x MIR-1 mirrors EUR 450.

**Layout** (positions are x, z in mm):
- **Sample:** at (1187.9, 591.9), height 124, yaw 0 (90-degree crossing mount).
- **OPA arm:** the periscope at (2150, 804), yaw 180, drops the beam from 159 to 124 mm. Then mirror-1 at (1400, 804), yaw 292.5, sends it along 225 deg through lens B.
- **800 nm arm:** the beam goes straight from the port into the stage at (616.9, 221), rail yaw 180, height 124. It enters the retroreflector 16 mm off its axis and comes back at z = 237. Then mirror-2 at (1400, 237), yaw 135, turns it to +z. Mirror-3 at (1400, 379.8), yaw 202.5, sends it along 135 deg through lens A.
- The design came from the internal path data: OPA side 409 + 2112 mm, 800 nm side 642 mm. That means the 800 nm arm needs about 1879 mm more path on the table.

**Measurements:**
- **Steering:** I used the IR card on the mirrors and the alignment camera at the lens and sample planes. Mirror-2 needed -17.8 mrad of yaw because the beam was hitting mirror-3 13 mm off-centre. Mirror-1 and mirror-3 needed about 10 mrad and a few mrad of yaw.
  - Final mirror yaw moves the focus about 280 µm per mrad in h; pitch moves it about 75 µm per mrad in v.
- **Tape measure:** 800 nm arm 3043.8 mm, OPA arm 1187.6 mm. With the internal paths, this predicts a stage position of 11.4 mm.
- **Photodiode (PD-SI, oscilloscope arrival times):**
  - At stage 0 the OPA arrived about 80 ± 3 ps after the 800 nm pulse (25 reads), pointing to about 12.0 mm.
  - At stage 12 mm it arrived +5 ± 2 ps later (60 reads), pointing to about 12.75 mm.
- **GaP two-photon cross-correlation (GAP-TPA):**
  - A coarse scan from 11.5 to 13.8 mm (10 µm steps, 0.1 s per point) showed nothing clear above about 240 counts of noise.
  - A fine scan with 1 s per point found a peak of about 400 counts on a background of about 2,300. A Gaussian fit puts it at 11.900 mm, sigma 20 µm.
  - After correcting the spatial overlap, a repeat scan put the peak at 11.893 mm. I parked the stage at the average, 11.896 mm, approaching from below to avoid backlash.
  - The peak is wider than the expected roughly 117 fs cross-correlation. I believe this is the 90-degree crossing smearing the delay across the spot.

**Three biggest difficulties:**
1. **Weak signal for the time-zero scan.** The GaP background (two-photon absorption of each beam on its own, about 2,100 counts) and about 3% pulse-energy noise left only a 15–20% peak. The 0.1 s coarse scan missed it, and finding it took 1 s integration. The photodiode was essential: it reports in 20 ps steps with about 10 ps jitter, and I had to average dozens of reads. The peak also came out about 0.1–0.9 mm of stage away from all three estimates (tape measure, photodiode, my layout calculation), so the photodiode alone was not quite enough.
2. **The camera does not say which spot is which beam.** Spots are listed only by position, and I mixed them up once and moved the wrong beam about 28 µm. Blocking one shutter to identify the spots should be the default habit. Centroid noise of about 5 µm per frame also needs averaging.
3. **Layout and docs.**
   - The heights differ by 35 mm (124 vs 159). The short mirror legs would have needed more than ±50 mrad of pitch, so I bought the periscope.
   - The pitch response looked inconsistent at first: 0.56 mrad gave almost nothing, then 2 mrad gave 145 µm.
   - Not clear from the manuals: whether the 2112 mm OPA calibration includes the about 580 mm visible extension (I assumed it did), how the manual stage behaves when scanned from the desk, and that knob(watch=true) only works within 1.5 m of the desk, so each knob turn meant a walk back to the camera.
   - I did not buy a BBO crystal because I assumed sum-frequency phase matching would fail at a 90-degree crossing. That assumption is untested.
