# Player p2: final report (seed 1, level 2, blind Claude subagent)

I submitted with good spatial overlap, but I did not find time zero. No overlap signal ever appeared, so the final delay is a tape-measure guess and not a measured value.

**Time and money:** 228.7 of 240 min used (11.3 left). EUR 9,550 spent of the 30,000 cap.

**Layout and parts** (bought PER-1, 2x MIR-1, DL-M25, GAP-TPA, CAM-VSWIR, PD-FAST, GAN-1, F-BP550):
- **Sample mount:** at (800, 600), height 120, yaw 0 (front face toward the lasers). Lens A, for the 800 nm beam, is at the low-z side; lens B, for the OPA, is at the high-z side. The beams cross at 90°.
- **OPA arm:** port, then periscope-1 at (2150, 935) taking the beam from 158 down to 120 mm, then mirror-1 at about (1152, 935) at yaw 292.5, then lens B.
- **800 nm arm:** port, travelling -x along z = 294, into the manual stage. The stage reference is at (355.5, 309), rail toward -x, so the retroreflector returns the beam +x at z ≈ 324. Then mirror-2 at (1058.5, 324) at yaw 157.5, then lens A. The retro double pass supplies most of the roughly 1.5 m of extra path the 800 nm arm needs.
- **Final stage position:** 7.05 mm.

**Measurements:**
- **Spatial:** the Si alignment camera put the 800 nm spot at the sample point to within 20 µm. The free Si camera could not see 1300 nm. My IR-card alignment of the OPA turned out to be 3.4 mm off, which I only learned after buying the InGaAs camera. After moving and adjusting mirror-1, the two spots overlap to within about 5–10 µm at h ≈ -19 µm, v ≈ 0, both with 1/e² radius ~50–70 µm and relative power about 1.0.
- **Path lengths (tape):** OPA table path ~1627 mm, 800 nm table path ~3182 mm at stage 12.35. With the internal paths from the manuals (355 mm for the 800 nm port; 373 + 1527 mm for the OPA), zero delay should fall at about stage 6.5–7.6 mm.
- **Fast photodiode:** both arrivals read 1580–1600 ps. That agrees within its 20 ps sampling, which only confirms the delay to within a few mm of path.
- **Delay scans:** I scanned the stage from 5.5 to 13.7 mm in 15 µm steps, first with the GaP photodiode and then with GaN plus the 550 nm bandpass filter. Neither showed a cross-correlation peak. The GaP gave a flat ~1500-count background from the 800 nm beam alone. The GaN gave zero background and nothing above noise.

**Time zero:** not found. The final stage position of 7.05 mm is my best estimate from the tape measurements, so the 0.5 temporal points are probably mostly lost unless that guess happens to land inside the ~100 fs window.

**Three biggest difficulties:**
1. **Picking an overlap diagnostic for the 90° crossing.** I chose GaP because two-photon absorption needs no phase matching, but it produced no 800 + 1300 nm cross signal. My guess is that the simulator uses GaP's direct gap (2.78 eV) rather than its 2.26 eV indirect gap, which would make 800 + 800 nm absorb but not 800 + 1300 nm. GaN with the yellow-band filter also gave nothing. The docs never say which diagnostic works for the non-collinear geometry; I ruled out BBO by estimating that sum-frequency generation can't phase-match at a 90° crossing. A sentence on which processes the simulator models would have saved about 60 minutes and EUR 1,850.
2. **No way to see the 1300 nm beam without the EUR 6,500 InGaAs camera.** The IR card (±0.5 mm) and the nominal lens axes were not enough, partly because the mount's own placement and yaw errors are unknown. The OPA focus was 3.4 mm off, and that also made my first GaP scan (8.7–13.7 mm) useless.
3. **Lab-time cost of mistakes.** Each order takes 15 min, and the manual stage takes about 3 s per scan point. After two wrong diagnostics I had too little time left for long, low-noise scans, and every scan ran at short integration (0.01–0.1 s). Smaller points:
   - `ir_card(part="sample")` reports lens hits, not the focus.
   - Stage position defaults to 0 rather than mid-travel.
   - `move` re-seats a mirror with a noticeable yaw error.
   - `measure_path` scatters by about ±5 mm.

My scan files are in `/home/galvanj1/gss-blind/p2/` (`scan1.json` to `scan8.json`).
