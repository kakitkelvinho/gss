# Player p3: final report (seed 1, level 2, blind Claude subagent)

I played the p3 lab to the end and submitted. I think I found time zero: the delay stage is set at 11.973 mm.

**Time and money:** 116.9 of the 240 lab-time minutes (123 left) and EUR 8,550 of the 30,000 cap.
- First order, EUR 2,050: periscope PER-1 (500), 2x mirror MIR-1 (300), manual 25 mm stage DL-M25 (400), GaP photodiode GAP-TPA (250), InGaAs fast photodiode PD-FAST (600).
- Second order, EUR 6,500: the InGaAs camera CAM-VSWIR.

**Layout** (all beams at height 120 mm):
- **Sample mount:** at (600, 600), yaw 0. Lens A gets the 800 nm beam travelling at 135 deg; lens B gets the OPA beam (1300 nm) travelling at 225 deg. They cross at 90 deg.
- **OPA arm:** port, then periscope-1 at (2150, 935) taking it from 158 to 120 mm, then mirror-2 at (935, 935) with yaw 292.5, then lens B.
- **800 nm arm:** port, then straight into the stage's retroreflector (rail yaw 180, reference point at (174.5, 309), apex near x = 72, offset 15 mm sideways). It comes back 30 mm over, hits mirror-1 at (876, 324) with yaw 157.5, then lens A.
- The retroreflector fold supplies the roughly 1545 mm of extra 800 nm path that the manuals imply: 373 + 1527 − 355 mm.

**What I measured:**
- **Spatial:** I steered mirror-1 and mirror-2 with their knobs. Final camera spots at the sample: 800 nm at (−4, −3) µm, OPA at (−1, +3) µm, both about 72 x 51 µm radius, relative power about 1.0. Both beams pass about 9.8 mm off their lens centres but still transmit about 100%.
- **Coarse timing (PD-FAST, 40 readings):** the 800 nm pulse arrives 2 ± 3 ps after the OPA pulse, so the design was already close.
- **Fine timing (GaP, 800+1300 two-photon absorption):** a stage scan found a cross-correlation peak. The background is about 1500 counts from the 800 nm beam alone, and the peak adds about 350 to 400. The peak is about 50 µm wide in stage position and centred at 11.972–11.974 mm on two repeat scans. I parked the stage there, approaching from below because of backlash, and read 1922 counts.

**Three biggest difficulties:**
1. **The Si alignment camera can't see the 1300 nm OPA at all.** Nothing in the docs says how to see the OPA focus without the EUR 6,500 InGaAs camera, which is three times everything else I bought. The IR card is only good to ±0.5 mm, far too coarse for spots about 50 µm across. I spent about 10 minutes searching the Si camera over a knob grid before buying it, and the beam turned out to have been in its field of view all along.
2. **The GaP signal was hard to read, and the overlap peak came out wider than I expected.** The noise behaves differently from the datasheet: about 250 counts at 0.05 s, not the roughly 134 its 1/sqrt(t) scaling implies. My first fast scan missed the peak and gave a false candidate. The peak was about 2 to 3 times wider than the 60 and 100 fs pulses suggest, I assume from the 90-degree crossing. The ideal approach seems to be type-I BBO sum-frequency at 495 nm, but two horizontally polarised beams crossing at 90 deg have nearly orthogonal polarisations, which looks like it rules that out. The docs don't address this.
3. **The IR card readings were confusing.**
   - `ir_card(part="sample")` gave offsets that didn't match where the beams actually focused: 800 nm looked about 3 mrad off when it was really about 50 mrad off.
   - The mirror knob responses weren't documented and were asymmetric: pitch moved the spot 188 µm/mrad on mirror-1 but only 74 µm/mrad on mirror-2.
   - `knob(watch=true)` stopped working a few cm outside its 1.5 m range ("monitor too far away"), which forced trips to the desk for the OPA mirror.
   - Placement errors were bigger than the stated ±0.5 deg would suggest: mirror-1 needed about 21 mrad of knob correction, and both beams ended up about 10 mm off-centre on the lenses.
   - The fast photodiode's 20 ps sampling meant I had to average many reads, and `t_int` didn't average for me.
