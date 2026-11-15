# Player p1: final report (seed 1, level 2, blind Claude subagent)

I submitted with both beams overlapped at the sample and the delay stage set to the time zero I measured. Lab time used was 115.6 of 240 min, and I spent EUR 10,650 of the 30,000 cap.

**Purchases (two orders):**
- First order, EUR 4,150: PER-1 periscope, 2x MIR-1 mirrors, DL-C25 motorised stage, GAP-TPA photodiode, PD-FAST photodiode.
- Second order, EUR 6,500: the CAM-VSWIR camera.

**Layout:** sample point at x=550, z=628, height 158, yaw 0. The 800 nm beam goes through lens A (axis 135 deg) and the OPA beam (1300 nm) through lens B (axis 225 deg).
- **800 nm arm:**
  - Periscope at (2150, 294), raising the beam from 120 to 158 mm.
  - It then runs -x to the stage retroreflector: stage reference point at (199, 311), rail yaw 180. The beam enters 17 mm off the retro axis, so it comes back along z of about 328.
  - mirror-1 at (850, 328), yaw 157.5, then sends it toward the sample at 135 deg.
- **OPA arm:** mirror-2 at (857, 935), yaw 292.5, sends it straight toward the sample at 225 deg.
- Final steering was done with the periscope and mirror knobs.

**Measurements:**
- **Phase matching (my own calculation):** BBO-T236 matches collinear 800+1300 sum-frequency light, but at the required 90-degree crossing it would need a cut of about 86 deg. So I used two-photon absorption in GaP instead: 800+1300 is 2.5 eV, above GaP's 2.26 eV gap.
- **Camera spots:** with the InGaAs camera both focal spots ended within about 10 um of the sample point, radii about 73 x 50 um. Relative power was 0.96–1.02 at the sample and 0.98–0.99 at the lenses. The beams hit the lenses about 9 mm off-centre, but nothing was clipped.
- **PD-FAST timing scan:** fitting 101 points of arrival times over the full 25 mm of travel predicted time zero at a stage position of 15.56 mm.
- **Tape measure:** both paths, with the internal path lengths from the manuals added, predicted about 11.45 mm.
- **GaP scans:** about 1500 counts of background from the 800 nm beam alone, and a cross-correlation peak of about +350 counts on top of it. Two fine scans at 1 s per point fitted the centre at 14.487 and 14.4865 mm, with a full width of about 50 um of stage (roughly 330 fs, probably smeared by the 90-degree crossing). At 14.4865 mm a 2 s read gave 1815 counts against about 1500 background.

**Time zero:** yes, I think I found it, to within roughly ±5 um of stage (about ±30 fs). The peak showed up twice at the same place, about 350 counts above background, and I left the stage there.

**Three biggest difficulties:**
1. **The OPA beam was invisible until I bought the EUR 6,500 camera.** The free Si camera can't see 1300 nm, and the IR card (±0.5 mm) is too coarse to aim the beam to the sub-mrad needed. I tried to use the fast photodiode's 1 mm² area as an edge detector. It kept reporting the OPA pulse after I steered the spot about 5 mm away, so it apparently doesn't check whether the beam hits it. That cost 20 mrad of knob travel and some time; there was no cheap way to find the OPA spot.
2. **The coarse time-zero tools disagreed and both were wrong.** The fast photodiode was off by about 1.07 mm of stage (about 7 ps), and the tape measure plus the manuals' internal paths by about 3 mm. My first fine scans around the photodiode estimate found nothing, which cost about 25 minutes. The datasheet doesn't say that photodiode arrival times can carry an offset like this.
3. **The GaP signal is weak against the 800 nm background.** The peak is about 350 counts on 1500, with noise of about 100–180 counts per 0.1 s point, so a single 5 um-step scan only barely showed it. The datasheets give no expected signal size. Smaller issues:
   - The stage manual doesn't say which way the retroreflector faces relative to the rail yaw; I guessed it faces the reference point, and that worked.
   - Lab time also jumped by the 15 min order time, which was easy to forget.
   - My first 800 nm placement missed the retro by about 2 mm (the beam sat 18–21 mm off its axis, beyond the 19.1 mm aperture). With nothing behind it, the beam went on toward the table edge before I corrected it. That may have been logged as a laser-safety violation.

My notes and scan data are in /home/galvanj1/gss-blind/p1 (pdscan.json, tpa1–5.json, pm.py, sm.py, k.sh).
