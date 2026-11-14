"""Simulated vendor catalogue ("Lumen Photonics", fictional), datasheets and device manuals.

Everything the agent needs to choose well is in here. There are no trick omissions:
if an agent fails because a number is missing, fix the datasheet.
"""

from __future__ import annotations

from sim import constants as K

# kind: what the item physically is. slot: one-per-slot purchase category.
PARTS: dict[str, dict] = {
    "DL-M25": dict(
        slot="delay_stage", kind="stage", price=400, name="Manual micrometer delay stage, 25 mm",
        travel=25.0, drive="manual",
        datasheet=(
            "Manual linear stage, 25 mm travel, carrying a 1.5\" hollow gold retroreflector. "
            "Micrometer graduation 1 um. Backlash on direction reversal: about 5 um (approach a "
            "target position from one side for reproducible positioning). Moving it means turning "
            "the micrometer by hand AT the stage; a hand-turned scan costs about 3 s per point "
            "plus integration time. Optical path added = 2 x stage displacement. See manual "
            "'delay_stage' for geometry."),
    ),
    "DL-C25": dict(
        slot="delay_stage", kind="stage", price=2500, name="Closed-loop motorised delay stage, 25 mm",
        travel=25.0, drive="motor",
        datasheet=(
            "Motorised linear stage with optical encoder (closed loop), 25 mm travel, 1.5\" hollow "
            "gold retroreflector. Repeatability 0.1 um, speed 2 mm/s, settle 0.3 s per scan point. "
            "Driven from the desk controller. Optical path added = 2 x stage displacement. See "
            "manual 'delay_stage' for geometry."),
    ),
    "DL-C100": dict(
        slot="delay_stage", kind="stage", price=4000, name="Closed-loop motorised delay stage, 100 mm",
        travel=100.0, drive="motor",
        datasheet=(
            "Motorised linear stage with optical encoder (closed loop), 100 mm travel, 1.5\" hollow "
            "gold retroreflector. Repeatability 0.1 um, speed 2 mm/s, settle 0.3 s per scan point. "
            "Driven from the desk controller. Optical path added = 2 x stage displacement."),
    ),
    # --- Overlap diagnostics (sit in the sample mount at the focal plane; swapping changes no path) ---
    # Optical ones emit light that the signal camera behind the sample reads through the filter holder.
    "BBO-SHG-800": dict(
        slot="diagnostic", kind="diagnostic", price=900, model="bbo", readout="camera", cut=(800.0, 800.0),
        name="BBO crystal, type-I, cut for SHG of 800 nm (400 nm out), 0.1 mm",
        datasheet=(
            "beta-BBO, 0.1 mm thick, theta = 29.2 deg, type-I, cut for second-harmonic generation of "
            "800 nm -> 400 nm. AR coated 650-1300 nm. Phase matching is angle specific: any other "
            "wavelength pair (sum frequency, or SHG of another wavelength) is strongly phase-mismatched "
            "at this cut, ~1% of the efficiency of a crystal cut for it. The 800 nm beam alone gives a "
            "strong 400 nm signal (~20000 counts on the signal camera, unfiltered, good alignment). "
            "The emitted light is read by the signal camera through the filter holder."),
    ),
    "BBO-SFG-1300": dict(
        slot="diagnostic", kind="diagnostic", price=1200, model="bbo", readout="camera", cut=(800.0, 1300.0),
        name="BBO crystal, type-I, cut for SFG 800 nm + 1300 nm (495 nm out), 0.1 mm",
        datasheet=(
            "beta-BBO, 0.1 mm thick, theta = 26.5 deg, type-I, cut for sum-frequency generation "
            "800 nm + 1300 nm -> 495 nm. AR coated 650-1300 nm. The sum-frequency (cross) term is "
            "proportional to I_800 x I_1300 and appears only when the pulses overlap in space and time: "
            "~1000 counts on the signal camera at time zero with good alignment. Other pairs (SHG of "
            "either beam, other wavelengths) are phase-mismatched at this cut (~1%), but each beam alone "
            "still makes some second harmonic (800 nm -> 400 nm, 1300 nm -> 650 nm)."),
    ),
    "BBO-SFG-600": dict(
        slot="diagnostic", kind="diagnostic", price=1200, model="bbo", readout="camera", cut=(800.0, 600.0),
        name="BBO crystal, type-I, cut for SFG 800 nm + 600 nm (343 nm out), 0.1 mm",
        datasheet=(
            "beta-BBO, 0.1 mm thick, theta = 37.0 deg, type-I, cut for sum-frequency generation "
            "800 nm + 600 nm -> 343 nm. Cross term ~1000 photon-counts-equivalent at time zero with good "
            "alignment; other pairs ~1% (phase-mismatched). Each beam alone makes some second harmonic "
            "(400 nm, 300 nm). Output is in the near UV: check your detector's spectral range."),
    ),
    "BBO-SFG-450": dict(
        slot="diagnostic", kind="diagnostic", price=1300, model="bbo", readout="camera", cut=(800.0, 450.0),
        name="BBO crystal, type-I, cut for SFG 800 nm + 450 nm (288 nm out), 0.1 mm",
        datasheet=(
            "beta-BBO, 0.1 mm thick, theta = 47.5 deg, type-I, cut for sum-frequency generation "
            "800 nm + 450 nm -> 288 nm. Cross term ~1000 photon-counts-equivalent at time zero with good "
            "alignment; other pairs ~1% (phase-mismatched). Each beam alone makes some second harmonic "
            "(400 nm, 225 nm). Output is in the deep UV: check your detector's spectral range."),
    ),
    "GAN-1": dict(
        slot="diagnostic", kind="diagnostic", price=800, model="pl", readout="camera", eg_ev=3.4,
        band_nm=(520.0, 600.0),
        name="GaN on sapphire sample, 10 x 10 mm (two-photon luminescence)",
        datasheet=(
            "Wide-gap semiconductor, GaN epilayer on sapphire. Band gap 3.4 eV (365 nm): transparent "
            "to photons below the gap. Carriers created across the gap (one photon above 3.4 eV, or two "
            "photons whose energies add up to more than 3.4 eV, absorbed together) relax through the "
            "defect levels and emit the broad 'yellow band' luminescence, 520-600 nm (isotropic, "
            "independent of the exciting wavelengths). Two-photon absorption of one photon from each "
            "beam needs the pulses overlapped in space and time and gives ~1000 counts on the signal "
            "camera at time zero with good alignment. A single beam whose two photons together exceed "
            "the gap also excites the yellow band on its own (~330 counts). Photon energy E[eV] = "
            "1239.84 / lambda[nm]. Read by the signal camera through the filter holder."),
    ),
    "GAP-TPA": dict(
        slot="diagnostic", kind="diagnostic", price=250, model="tpa_pd", readout="electrical", eg_ev=2.26,
        name="GaP photodiode for two-photon detection, 1 mm^2, with amplifier",
        datasheet=(
            "GaP photodiode (band gap 2.26 eV, i.e. 549 nm), transimpedance amplifier and gated "
            "integrator read on the scope (read_signal returns counts). Photons above the gap are "
            "absorbed linearly (a huge photocurrent, ~5e5 counts for a full beam). Photons below the "
            "gap only give a photocurrent by two-photon absorption: a single beam whose two photons "
            "add up to more than 2.26 eV gives a delay-independent background (800 nm alone: ~1500 "
            "counts; another wavelength: ~800 counts), and one photon from each beam gives the cross "
            "term (~1000 counts at time zero, good alignment). Photon energy E[eV] = 1239.84 / lambda[nm]. "
            "Sits at the sample plane; not read through the filter holder."),
    ),
    "PD-SI": dict(
        slot="diagnostic", kind="diagnostic", price=300, model="photodiode", readout="scope", range_nm=(350.0, 1100.0),
        name="Fast Si photodiode, 350-1100 nm, 150 MHz",
        datasheet=(
            "Si photodiode, 350-1100 nm, 150 MHz, mounted at the sample plane, read on the table's 1 GHz "
            "scope. Linear detector: it sees each pulse separately and reports its arrival time "
            "(clock-referenced edge timing, ~20 ps sampling, ~10 ps jitter; 1 ps of delay = 0.3 mm of "
            "path). Blind outside 350-1100 nm."),
    ),
    "PD-IGA": dict(
        slot="diagnostic", kind="diagnostic", price=600, model="photodiode", readout="scope", range_nm=(800.0, 1700.0),
        name="Fast InGaAs photodiode, 800-1700 nm, 25 ps rise time",
        datasheet=(
            "InGaAs photodiode, 800-1700 nm, 25 ps rise time, mounted at the sample plane, read on the "
            "table's 1 GHz scope. Linear detector: it sees each pulse separately and reports its "
            "arrival time (~20 ps sampling, ~10 ps jitter; 1 ps of delay = 0.3 mm of path). Blind "
            "outside 800-1700 nm."),
    ),
    # --- Filters for the signal camera (one at a time in the filter holder) ---
    "F-BP400": dict(slot="filter", kind="filter", price=180, passband=[(395.0, 405.0, 0.9)], leak=1e-4,
                    name="Bandpass filter 400 nm, 10 nm FWHM",
                    datasheet="Hard-coated bandpass, 400 +/- 5 nm, T > 90%; OD 4 elsewhere (300-1700 nm)."),
    "F-BP495": dict(slot="filter", kind="filter", price=180, passband=[(490.0, 500.0, 0.9)], leak=1e-4,
                    name="Bandpass filter 495 nm, 10 nm FWHM",
                    datasheet="Hard-coated bandpass, 495 +/- 5 nm, T > 90%; OD 4 elsewhere (300-1700 nm)."),
    "F-BP550": dict(slot="filter", kind="filter", price=200, passband=[(530.0, 570.0, 0.9)], leak=1e-4,
                    name="Bandpass filter 550 nm, 40 nm FWHM",
                    datasheet="Hard-coated bandpass, 530-570 nm, T > 90%; OD 4 elsewhere (300-1700 nm)."),
    "F-VIS495": dict(slot="filter", kind="filter", price=220, passband=[(495.0, 710.0, 0.85)], leak=1e-4,
                     name="Colour-glass stack: 495 nm longpass + KG3 shortpass (495-710 nm)",
                     datasheet=("Stacked GG495-type longpass and KG3-type heat-absorbing shortpass. Passes "
                                "~495-710 nm (T ~ 85%); OD 4 below 490 nm and above 720 nm.")),
    "F-UV": dict(slot="filter", kind="filter", price=220, passband=[(325.0, 385.0, 0.8)], leak=1e-4,
                 name="Colour-glass stack: UG1 + BG40 (325-385 nm)",
                 datasheet="Stacked UG1/BG40-type glass. Passes ~325-385 nm (T ~ 80%); OD 4 at 400-1700 nm."),
    "F-SP775": dict(slot="filter", kind="filter", price=120, passband=[(300.0, 765.0, 0.9)], leak=1e-4,
                    extra_leak=[(770.0, 900.0, 0.05)],
                    name="Shortpass filter, 775 nm edge",
                    datasheet=("Dielectric shortpass, T > 90% at 300-765 nm. Edge at 775 nm; blocking is "
                               "only OD 1.3 (5%) from 770 to 900 nm, OD 4 above.")),
    # --- Camera ---
    "CAM-VSWIR": dict(slot="camera", kind="camera", price=6500, range_nm=(400.0, 1700.0),
                      name="VIS-SWIR InGaAs camera for the flip-in mount, 400-1700 nm",
                      datasheet=("Replaces the free Si alignment camera in the sample mount's flip-in "
                                 "holder (same plane, same 5.5 um pixel scale and calibration). Spectral "
                                 "range 400-1700 nm: sees 800 nm and SWIR beams alike.")),
    "MIR-1": dict(
        slot="mounting", kind="mirror", price=150, name="1\" protected silver mirror in kinematic mount, on post",
        datasheet=(
            "1\" (25.4 mm) protected silver mirror, >97% at 700-2000 nm. Kinematic mount with "
            "two knobs (yaw, pitch), +/-50 mrad range each. Clear aperture: beams more than about "
            "10 mm from the centre start to clip; beyond 12.7 mm the beam misses the mirror. "
            "Post height 50-300 mm. Footprint ~25 mm radius."),
    ),
    "PER-1": dict(
        slot="mounting", kind="periscope", price=500, name="In-line periscope, two 1\" mirrors",
        datasheet=(
            "Rigid in-line periscope: lower 1\" mirror sends the beam vertically, top 1\" mirror "
            "sends it on in the original direction at the new height. Input and output heights "
            "50-300 mm, at least 30 mm apart. Top mirror has a kinematic mount (yaw, pitch "
            "knobs, +/-50 mrad). Polarisation is preserved (in-line design). Footprint ~40 mm radius."),
    ),
}

SLOTS = {
    "delay_stage": "Delay stage with retroreflector (fine delay)",
    "diagnostic": "Overlap diagnostic for the sample mount",
    "filter": "Filters for the signal camera's filter holder",
    "camera": "Cameras for the flip-in alignment mount",
    "mounting": "Mirrors and periscopes",
}

FREE_EQUIPMENT = (
    "Already on the table, free: a sample mount with f = 100 mm achromatic lens; a flip-in Si CMOS "
    "alignment camera at the lens focal plane (also images the lens plane), specified 400-1000 nm and "
    "blind outside that range; a zoomed Si CMOS signal camera behind the sample (400-1000 nm) that "
    "integrates the light from the sample in a region of interest, through an empty filter holder; "
    "a 1 GHz oscilloscope at the desk; an IR/visible viewer card (400-1700 nm); and beam-block "
    "shutters at both output ports."
)


def manuals(lab) -> dict[str, str]:
    """Device manuals. `lab` provides per-seed facts (ports, OPA internal path)."""
    p, q = lab.ports["800nm"], lab.ports["opa"]
    lo = lab.opa_lambda
    w_o = K.opa_w_coll(lo)
    l1_sample = (
            "Sample mount with f = 100 mm lens. place(sample, x, z, height, yaw): (x, z, height) is "
            "the lens centre, yaw the direction light travels through the lens. The sample (and the "
            "installed diagnostic) sits at the focal plane 100 mm behind the lens. Lens clear "
            f"aperture radius {K.LENS_R} mm (clipping from ~{K.LENS_CLIP_START} mm). A collimated "
            "beam hitting the lens at angle theta to its axis focuses at f x theta from the axis, "
            "whatever point of the lens it hits, so overlapping the foci means matching the beams' "
            "ANGLES; where they hit the lens sets their crossing angle and must stay inside the "
            "aperture. Focal spot radius ~50 um for both beams. install(part_id) swaps the diagnostic "
            "(or the signal-camera filter); it does not change any path. Flip-in alignment camera (Si "
            "CMOS, 400-1000 nm, blind outside; a bought VIS-SWIR camera replaces it): "
            "view_camera('sample') images the focal "
            f"plane ({K.CAM_PIXEL*1000:.1f} um pixels, field of view +/-{K.CAM_HALF_FOV} mm, sub-pixel "
            "centroids); view_camera('lens') shows where each beam hits the lens (mm). Each spot also reports "
            "relative_power: the fraction of that beam's output power reaching the sample (~2% "
            "reading noise), so clipping on an optic shows up as a dim spot. Camera image "
            "axes: h = horizontal, positive toward the direction (lens yaw - 90 deg) in the table "
            "plane; v = up. The lens axis is h = v = 0."
        )
    l2_sample = (
            "Sample mount, 90-degree crossing version (the experiment needs the two beams to cross at a "
            "full angle of 90 deg at the sample, each arriving 45 deg from the sample normal). "
            "place(sample, x, z, height, yaw): (x, z, height) is the sample point (common focus), yaw "
            "the direction the sample's front face points (its normal, toward the incoming beams). Two "
            "f = 100 mm lenses are built in, 100 mm before the sample point along their own axes: lens A "
            "takes a beam travelling along (yaw + 135 deg), lens B one travelling along (yaw + 225 deg); "
            "each beam must come through its own lens (the same lens for both is not the required "
            f"geometry and does not count as overlap). Lens clear aperture radius {K.LENS_R} mm (clipping "
            f"from ~{K.LENS_CLIP_START} mm). A collimated beam hitting a lens at angle theta to its axis "
            "focuses at f x theta from that axis, so overlapping the foci means matching each beam's "
            "angle to its own lens. Focal spot radius ~50 um, stretched by 1/cos45 (~70 um) along the "
            "sample's horizontal axis because the sample is tilted. Across the overlap region the two "
            "pulses arrive at different times (dt(x) = 2 x sin45 / c), so the cross-correlation is "
            f"broadened to a 1/e half-width of ~{K.TAU_C_L2:.0f} fs and its peak is ~{K.L2_PEAK:.2f} of "
            "the collinear value. install(part_id) swaps the diagnostic (or the signal-camera filter); "
            "it does not change any path. Flip-in alignment camera (Si CMOS, 400-1000 nm, blind "
            "outside; a bought VIS-SWIR camera replaces it) looks at the sample head-on along its "
            f"normal: view_camera('sample') gives spots on the sample surface ({K.CAM_PIXEL*1000:.1f} um "
            f"pixels, field of view +/-{K.CAM_HALF_FOV} mm, sub-pixel centroids; h = horizontal in-plane "
            "axis, positive toward (yaw + 90 deg), v = up); view_camera('lens') shows which lens each "
            "beam hits and where (mm, in that lens's frame: h positive toward (lens axis - 90 deg), "
            "v up). Each spot also reports relative_power (fraction of that beam's output power "
            "reaching the sample, ~2% noise). The signal camera also looks head-on from the front, so "
            "only diffuse scatter (~1% of the collinear case) reaches it."
        )
    return {
        "table": (
            f"Optical table: {K.TABLE_X:.0f} x {K.TABLE_Z:.0f} mm breadboard. Coordinates in mm: x along "
            f"the long side (0..{K.TABLE_X:.0f}), z across (0..{K.TABLE_Z:.0f}), height = height above the "
            f"breadboard (y). Yaw angles are in degrees in the table plane, measured from +x toward +z.\n"
            f"800 nm output port (arm '800nm'; amplifier, 800 nm, ~100 fs FWHM, 1 kHz): x={p['pos'][0]:.0f}, "
            f"z={p['pos'][2]:.0f}, height={p['pos'][1]:.0f}, beam travelling toward -x (yaw 180). "
            f"Collimated, 0.5 mm 1/e^2 radius, horizontally polarised (in the table plane).\n"
            f"OPA output port (arm 'opa'; OPA, {lo:.0f} nm, ~60 fs FWHM): x={q['pos'][0]:.0f}, z={q['pos'][2]:.0f}, "
            f"height={q['pos'][1]:.0f}, beam travelling toward -x (yaw 180). Collimated, {w_o:.2f} mm radius "
            f"(focuses to the same ~50 um spot as the 800 nm beam). "
            f"The OPA is pumped by the same amplifier; both ports are path-matched at the amplifier's "
            f"split EXCEPT for the OPA's internal path (see manual 'opa').\n"
            f"Laser housings occupy x > {p['pos'][0]:.0f} around each port. Both shutters start CLOSED "
            f"(use unblock). Any beam leaving the table is a laser-safety violation (logged).\n"
            f"Desk (computer, monitor, scope, stage controller) at x=-300, z=600, beside the x=0 end. "
            f"You walk on a walkway 300 mm outside the table edge (tool responses give your position there as "
            f"you_at, or 'desk') at 0.5 m/s, and can reach 0.6 m in from the table edge. "
            f"measure_path is a tape measure along the beam: good to about +/-5 mm. "
            f"Catalogue, datasheets, manuals, buying, camera, signal reads, motorised stage moves and "
            f"scans happen at the desk; knobs, placement and the IR card happen at the part. "
            f"knob(..., watch=true) also returns a camera frame if you are within 1.5 m of the desk.\n"
            f"Placing a part takes ~5 min and lands within ~1 mm of the requested position; yaw set "
            f"by eye is good to ~0.5 deg. Kinematic knobs then fine-tune (+/-50 mrad).\n{FREE_EQUIPMENT}"
        ),
        "opa": (
            f"OPA user manual (excerpt). Current output: {lo:.0f} nm, ~60 fs, horizontally polarised (in the "
            "table plane, same as the 800 nm beam). The amplifier light travels an internal path inside "
            "the OPA before the output port. Signal/idler outputs (1100-2600 nm) leave after the "
            "parametric stages; visible outputs (e.g. 450 or 600 nm) additionally pass the "
            "frequency-mixing extension box, which adds about 580 mm. Calibrated internal optical "
            f"path for this unit in its current configuration ({lab.opa_route} route, serial on the "
            f"housing): {lab.opa_path:.0f} mm, relative to the amplifier output. To reach temporal "
            "overlap with the direct 800 nm beam, the 800 nm arm must be longer than the OPA arm's "
            "table path by this amount. It cannot be measured from outside the housing."
        ),
        "delay_stage": (
            "Delay stage manual. place(stage, x, z, height, yaw): (x, z, height) is the stage "
            "reference point at the front of the rail; yaw is the direction light travels INTO the "
            "retroreflector (along the rail). The retroreflector apex sits "
            f"{K.STAGE_APEX_OFFSET:.0f} mm + stage position along the rail from the reference point; "
            f"its entrance face is {K.RETRO_FRONT:.0f} mm in front of the apex, clear aperture radius "
            f"{K.RETRO_R:.1f} mm. A hollow retroreflector returns the beam exactly antiparallel, "
            "displaced through the apex: a beam entering d mm to one side of the apex line leaves "
            "d mm on the other side (2d separation). Enter about 10-15 mm off the apex so the return "
            "can be picked off by a mirror. Path added = 2 x (distance from entrance to apex). "
            "If the incoming beam is not parallel to the rail, the returned beam shifts sideways "
            "by about 2 x (stage travel) x (misalignment angle) as the stage moves; align the "
            "input beam parallel to the rail by checking the return at both ends of travel. "
            "Positions are in mm from 0 to the travel limit."
        ),
        "sample_mount": l1_sample if lab.level == 1 else l2_sample,
        "mirror": (
            "Kinematic mirror mount. place(mirror-N, x, z, height, yaw): yaw is the direction the "
            "reflecting face points (its normal) in the table plane. A beam travelling along "
            "direction a and leaving along b needs a normal along (b - a). knob(mirror, 'yaw'|'pitch', "
            "delta_mrad) tilts the mirror; a mirror tilt of delta deflects the reflected beam by up "
            "to 2 x delta. Knob range +/-50 mrad, actuator repeatability ~2%. rotate(part, deg) "
            "loosens the base, turns it, and re-tightens (re-seat error ~0.2 deg)."
        ),
        "periscope": (
            "In-line periscope. place(periscope-N, x, z, height, yaw, height_in): yaw is the beam "
            "travel direction (in and out), height_in the input beam height, height the output "
            "height. Knobs act on the top mirror."
        ),
        "photodiode": (
            "Fast photodiode on the 1 GHz scope: read_signal returns the arrival time of each pulse "
            "it is sensitive to that reaches the sample (relative to the scope trigger). Resolution "
            "~20 ps (6 mm of path). Good for catching gross path errors (metres), not for finding time "
            "zero. Block one arm at a time to be sure which pulse is which."
        ),
        "nonlinear": (
            "Nonlinear overlap diagnostics (crystals, semiconductor samples, two-photon photodiodes) in "
            "the sample mount. read_signal(t_int) returns counts averaged over t_int seconds; noise "
            "(read-out floor plus ~3% source fluctuations of the total signal) falls as 1/sqrt(t_int). "
            "The cross term exists only within ~+/-100 fs of time zero (~30 um of path, ~15 um of stage "
            "travel) and only if the foci overlap. Single beams can give delay-independent signals of "
            "their own (second harmonic, one-colour two-photon absorption), and scattered laser light "
            "reaches the signal camera unless a filter blocks it: block each arm in turn to see what "
            "each one contributes. scan(start, end, step, t_int) moves the stage and reads at each "
            "point (max 5000 points)."
            + (" With the beams crossing at 90 deg, no BBO cut can be phase-matched (sum frequency at "
               "~1% of a collinear matched crystal); two-photon absorption needs no phase matching."
               if lab.level == 2 else "")
        ),
        "signal_camera": (
            f"Signal camera: zoomed Si CMOS behind the sample, specified {K.CAM_SI_RANGE[0]:.0f}-"
            f"{K.CAM_SI_RANGE[1]:.0f} nm (no specified response outside; treat it as blind). It integrates "
            "the light leaving the sample in a fixed region of interest, through the filter holder "
            "(empty unless you install a filter). Scattered laser light at the sample is ~2e5 counts per "
            f"beam unfiltered; the ROI saturates at {K.SIG_CAM_SAT} counts (reported as saturated). "
            "install(filter_id) puts a filter in the holder, uninstall('filter') empties it. The filter "
            "does not affect the alignment camera."
        ),
        "ir_card": (
            "IR viewer card. ir_card(part=...) shows where each beam hits that optic relative to "
            "its centre; ir_card(x=, z=, height=) shows any beam passing within 30 mm of that "
            "point. Offsets are in table coordinates (dx, dz, dheight), good to ~0.5 mm."
        ),
    }


def filter_spec(part_id: str) -> dict:
    p = PARTS[part_id]
    return {"pass": p["passband"], "leak": p["leak"], "extra_leak": p.get("extra_leak", [])}
