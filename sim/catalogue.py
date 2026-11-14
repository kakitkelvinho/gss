"""Simulated vendor catalogue ("Lumen Photonics", fictional), datasheets and device manuals.

Everything the agent needs to choose well is in here. There are no trick omissions:
if an agent fails because a number is missing, fix the datasheet. Datasheets and manuals give
specifications and conventions only, no procedures.
"""

from __future__ import annotations

from sim import constants as K

_BBO_COMMON = ("Mounted at the sample plane (0.1 mm thick, 5 x 5 mm, AR coated 650-1300 nm); the light leaving "
               "it is read by the signal camera through the filter holder.")
_PD_SCOPE = ("Mounted at the sample plane, read on the table's 1 GHz scope, which reports the arrival time of "
             "each pulse (20 ps sampling, ~10 ps jitter).")

# kind: what the item physically is. slot: purchase category.
PARTS: dict[str, dict] = {
    "DL-M25": dict(
        slot="delay_stage", kind="stage", price=400, name="Manual micrometer delay stage, 25 mm",
        travel=25.0, drive="manual",
        datasheet=(
            "Manual linear stage, 25 mm travel, carrying a 1.5\" hollow gold retroreflector. "
            "Micrometer graduation 1 um. Backlash on direction reversal: about 5 um. Turned by hand "
            "at the stage: ~3 s per scan point plus integration time. See manual 'delay_stage'."),
    ),
    "DL-C25": dict(
        slot="delay_stage", kind="stage", price=2500, name="Closed-loop motorised delay stage, 25 mm",
        travel=25.0, drive="motor",
        datasheet=(
            "Motorised linear stage with optical encoder (closed loop), 25 mm travel, 1.5\" hollow "
            "gold retroreflector. Repeatability 0.1 um, speed 2 mm/s, settle 0.3 s per scan point. "
            "Driven from the desk controller. See manual 'delay_stage'."),
    ),
    "DL-C100": dict(
        slot="delay_stage", kind="stage", price=4000, name="Closed-loop motorised delay stage, 100 mm",
        travel=100.0, drive="motor",
        datasheet=(
            "Motorised linear stage with optical encoder (closed loop), 100 mm travel, 1.5\" hollow "
            "gold retroreflector. Repeatability 0.1 um, speed 2 mm/s, settle 0.3 s per scan point. "
            "Driven from the desk controller. See manual 'delay_stage'."),
    ),
    # --- Overlap diagnostics (sit in the sample mount at the focal plane; swapping changes no path) ---
    # BBO type-I cut angles from the Zhang et al. Sellmeier equations (o + o -> e).
    "BBO-T292": dict(
        slot="diagnostic", kind="diagnostic", price=900, model="bbo", readout="camera", cut=(800.0, 800.0),
        name="beta-BBO crystal 0.1 mm, theta = 29.2 deg, type I",
        datasheet="beta-BBO, cut theta = 29.2 deg, phi = 90 deg (type I, o + o -> e). " + _BBO_COMMON,
    ),
    "BBO-T236": dict(
        slot="diagnostic", kind="diagnostic", price=1200, model="bbo", readout="camera", cut=(800.0, 1300.0),
        name="beta-BBO crystal 0.1 mm, theta = 23.6 deg, type I",
        datasheet="beta-BBO, cut theta = 23.6 deg, phi = 90 deg (type I, o + o -> e). " + _BBO_COMMON,
    ),
    "BBO-T341": dict(
        slot="diagnostic", kind="diagnostic", price=1200, model="bbo", readout="camera", cut=(800.0, 600.0),
        name="beta-BBO crystal 0.1 mm, theta = 34.1 deg, type I",
        datasheet="beta-BBO, cut theta = 34.1 deg, phi = 90 deg (type I, o + o -> e). " + _BBO_COMMON,
    ),
    "BBO-T408": dict(
        slot="diagnostic", kind="diagnostic", price=1300, model="bbo", readout="camera", cut=(800.0, 450.0),
        name="beta-BBO crystal 0.1 mm, theta = 40.8 deg, type I",
        datasheet="beta-BBO, cut theta = 40.8 deg, phi = 90 deg (type I, o + o -> e). " + _BBO_COMMON,
    ),
    "GAN-1": dict(
        slot="diagnostic", kind="diagnostic", price=800, model="pl", readout="camera", eg_ev=3.4,
        band_nm=(520.0, 600.0),
        name="GaN on sapphire sample, 10 x 10 mm",
        datasheet=(
            "Undoped GaN epilayer (4 um) on c-plane sapphire, 10 x 10 mm. Direct band gap 3.4 eV (365 nm). "
            "Photoluminescence: band-edge line at 365 nm and the broad defect ('yellow') band, 520-600 nm. "
            "Mounted at the sample plane; its emission is read by the signal camera through the filter holder."),
    ),
    "GAP-TPA": dict(
        slot="diagnostic", kind="diagnostic", price=250, model="tpa_pd", readout="electrical", eg_ev=2.26,
        name="GaP photodiode, 1 mm^2, with gated integrator",
        datasheet=(
            "GaP photodiode, 1 mm^2, indirect band gap 2.26 eV (549 nm); specified photoresponse 150-550 nm. "
            "Transimpedance amplifier and gated integrator; read_signal returns integrator counts "
            "(~30 counts rms at 1 s, falling as 1/sqrt(t_int)). Mounted at the sample plane."),
    ),
    "PD-SI": dict(
        slot="diagnostic", kind="diagnostic", price=300, model="photodiode", readout="scope", range_nm=(350.0, 1100.0),
        name="Fast Si photodiode, 350-1100 nm, 150 MHz",
        datasheet="Si photodiode, 350-1100 nm, 150 MHz bandwidth. " + _PD_SCOPE,
    ),
    "PD-FAST": dict(
        slot="diagnostic", kind="diagnostic", price=600, model="photodiode", readout="scope", range_nm=(800.0, 1700.0),
        name="Fast InGaAs photodiode, 800-1700 nm, 25 ps rise time",
        datasheet="InGaAs photodiode, 800-1700 nm, 25 ps rise time. " + _PD_SCOPE,
    ),
    # --- Filters for the signal camera (one at a time in the filter holder) ---
    "F-BP400": dict(slot="filter", kind="filter", price=180, passband=[(395.0, 405.0, 0.9)], leak=1e-4,
                    name="Bandpass filter 400 nm, 10 nm FWHM",
                    datasheet="Hard-coated bandpass, 395-405 nm, T > 90%; OD 4 elsewhere (300-1700 nm)."),
    "F-BP495": dict(slot="filter", kind="filter", price=180, passband=[(490.0, 500.0, 0.9)], leak=1e-4,
                    name="Bandpass filter 495 nm, 10 nm FWHM",
                    datasheet="Hard-coated bandpass, 490-500 nm, T > 90%; OD 4 elsewhere (300-1700 nm)."),
    "F-BP550": dict(slot="filter", kind="filter", price=200, passband=[(530.0, 570.0, 0.9)], leak=1e-4,
                    name="Bandpass filter 550 nm, 40 nm FWHM",
                    datasheet="Hard-coated bandpass, 530-570 nm, T > 90%; OD 4 elsewhere (300-1700 nm)."),
    "F-VIS495": dict(slot="filter", kind="filter", price=220, passband=[(495.0, 710.0, 0.85)], leak=1e-4,
                     name="Colour-glass stack: 495 nm longpass + KG3 shortpass",
                     datasheet=("Stacked GG495-type longpass and KG3-type shortpass. T ~ 85% at 495-710 nm; OD 4 "
                                "below 490 nm and above 720 nm.")),
    "F-UV": dict(slot="filter", kind="filter", price=220, passband=[(325.0, 385.0, 0.8)], leak=1e-4,
                 name="Colour-glass stack: UG1 + BG40",
                 datasheet="Stacked UG1/BG40-type glass. T ~ 80% at 325-385 nm; OD 4 at 400-1700 nm."),
    "F-SP775": dict(slot="filter", kind="filter", price=120, passband=[(300.0, 765.0, 0.9)], leak=1e-4,
                    extra_leak=[(770.0, 900.0, 0.05)],
                    name="Shortpass filter, 775 nm edge",
                    datasheet=("Dielectric shortpass, T > 90% at 300-765 nm. Blocking OD 1.3 from 770 to 900 nm, "
                               "OD 4 above 900 nm.")),
    # --- Camera ---
    "CAM-VSWIR": dict(slot="camera", kind="camera", price=6500, range_nm=(400.0, 1700.0),
                      name="VIS-SWIR InGaAs camera for the flip-in mount, 400-1700 nm",
                      datasheet=("InGaAs focal-plane camera, spectral range 400-1700 nm. Fits the sample mount's "
                                 "flip-in holder in place of the Si alignment camera (same plane, 5.5 um pixel "
                                 "scale, same calibration).")),
    # --- Mounting ---
    "MIR-1": dict(
        slot="mounting", kind="mirror", price=150, name="1\" protected silver mirror in kinematic mount, on post",
        datasheet=(
            "1\" (25.4 mm) protected silver mirror, >95% at 450-2000 nm. Kinematic mount with "
            "two knobs (yaw, pitch), +/-50 mrad range each. Clear aperture: beams more than about "
            "10 mm from the centre start to clip. "
            "Mount plate 38 x 38 mm, centred on the optic, from 0.5 to 12 mm behind the mirror surface; "
            "1/2\" post (6.35 mm radius) below the plate, 6 mm behind the mirror surface. "
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
    "Already on the table, free: a sample mount with f = 100 mm achromatic lens(es); a flip-in Si CMOS "
    "alignment camera at the sample (also images the lens plane), specified 400-1000 nm; a zoomed Si CMOS "
    "signal camera looking at the sample (400-1000 nm) through an empty filter holder; a 1 GHz oscilloscope "
    "at the desk; an IR/visible viewer card (400-1700 nm); and beam-block shutters at both output ports."
)


def manuals(lab) -> dict[str, str]:
    """Device manuals: specifications and conventions only (no procedures). `lab` provides the
    per-seed facts (ports, split paths inside the laser housing, OPA wavelength and internal path)."""
    p, q = lab.ports["800nm"], lab.ports["opa"]
    lo = lab.opa_lambda
    w_o = K.opa_w_coll(lo)
    cam = (f"view_camera('sample') images the sample ({K.CAM_PIXEL*1000:.1f} um pixels, field of view "
           f"+/-{K.CAM_HALF_FOV} mm); view_camera('lens') images the lens plane. Each spot reports its centroid, "
           "1/e^2 radius and relative_power (fraction of that beam's output power reaching the sample, ~2% "
           "reading noise). The camera does not distinguish wavelengths: spots are listed by position.")
    l1_sample = (
        "Sample mount with an f = 100 mm achromatic lens. place(sample, x, z, height, yaw): (x, z, "
        "height) is the lens centre, yaw the direction light travels through the lens. The sample "
        "position (and the installed diagnostic) is the lens focal plane. Lens clear aperture radius "
        f"{K.LENS_R} mm, held in a 2\" mount ring (outer radius {K.LENS_MOUNT_R} mm). install(part_id) swaps "
        "the diagnostic (or the signal-camera filter) without moving the mount. Flip-in alignment camera "
        "(Si CMOS, specified 400-1000 nm; CAM-VSWIR replaces it): " + cam + " Image axes: h horizontal, "
        "positive toward (lens yaw - 90 deg) in the table plane; v up; the lens axis is h = v = 0."
    )
    l2_sample = (
        "Sample mount, 90-degree crossing version. The experiment requires the two beams to cross at a "
        "full angle of 90 deg at the sample, each arriving 45 deg from the sample normal through its own "
        "lens (both beams through the same lens is not the required geometry). place(sample, x, z, height, "
        "yaw): (x, z, height) is the sample point, yaw the direction the sample's front face points (its "
        "normal). Two f = 100 mm achromatic lenses, each 100 mm before the sample point on its own axis: "
        "lens A axis along (yaw + 135 deg), lens B along (yaw + 225 deg) (directions light travels through "
        f"them). Lens clear aperture radius {K.LENS_R} mm, 2\" mount rings (outer radius {K.LENS_MOUNT_R} mm). "
        "install(part_id) swaps the diagnostic (or the signal-camera filter) without moving the mount. The "
        "alignment and signal cameras look at the sample head-on along its normal, from the front. Flip-in "
        "alignment camera (Si CMOS, specified 400-1000 nm; CAM-VSWIR replaces it): " + cam + " Sample "
        "image axes: h horizontal in the sample surface, positive toward (yaw + 90 deg); v up; the sample "
        "point is h = v = 0. Lens images report which lens (A or B) and h, v in that lens's frame (h "
        "positive toward its axis - 90 deg, v up)."
    )
    return {
        "table": (
            f"Optical table: {K.TABLE_X:.0f} x {K.TABLE_Z:.0f} mm breadboard. Coordinates in mm: x along "
            f"the long side (0..{K.TABLE_X:.0f}), z across (0..{K.TABLE_Z:.0f}), height = height above the "
            f"breadboard (y). Yaw angles are in degrees in the table plane, measured from +x toward +z.\n"
            f"Laser housing (amplifier, 800 nm, ~100 fs FWHM, 1 kHz, pulse energy stability ~3% rms, and an "
            f"OPA pumped by it) at the x = {K.TABLE_X:.0f} end. Inside the housing the amplifier output is "
            f"split: one part exits at the 800 nm port ({lab.split_800:.0f} mm of path from the split), the "
            f"other goes to the OPA input ({lab.split_opa:.0f} mm of path from the split).\n"
            f"800 nm output port (arm '800nm'): x={p['pos'][0]:.0f}, z={p['pos'][2]:.0f}, "
            f"height={p['pos'][1]:.0f}, beam travelling toward -x (yaw 180). Collimated, 0.5 mm 1/e^2 radius, "
            f"horizontally polarised.\n"
            f"OPA output port (arm 'opa'; OPA, {lo:.0f} nm, ~60 fs FWHM): x={q['pos'][0]:.0f}, "
            f"z={q['pos'][2]:.0f}, height={q['pos'][1]:.0f}, beam travelling toward -x (yaw 180). Collimated, "
            f"{w_o:.2f} mm 1/e^2 radius, horizontally polarised.\n"
            f"Laser housings occupy x > {p['pos'][0]:.0f} around each port. Both shutters start closed. "
            f"Any beam leaving the table is a laser-safety violation (logged).\n"
            f"Desk (computer, monitor, scope, stage controller) at x=-300, z=600, beside the x=0 end. "
            f"You walk on a walkway 300 mm outside the table edge (tool responses give your position as "
            f"you_at, or 'desk') at 0.5 m/s, and can reach 0.6 m in from the table edge. "
            f"Catalogue, datasheets, manuals, buying, camera, signal reads, motorised stage moves and "
            f"scans happen at the desk; knobs, placement, the IR card and the tape measure happen at the "
            f"table. knob(..., watch=true) also returns a camera frame if you are within 1.5 m of the desk. "
            f"measure_path is a tape measure along the beam (good to about +/-5 mm).\n"
            f"Placing a part takes ~5 min and lands within ~1 mm of the requested position; yaw set by eye "
            f"is good to ~0.5 deg.\n{FREE_EQUIPMENT}"
        ),
        "opa": (
            f"OPA user manual (excerpt). Current output {lo:.0f} nm, ~60 fs, horizontally polarised. Signal "
            "and idler outputs (1100-2600 nm) leave after the parametric stages; visible outputs (450-700 nm) "
            "are generated in the frequency-mixing extension, which adds ~580 mm of internal path. Internal "
            f"optical path from the OPA pump input to the output port in the current ({lab.opa_route}) "
            f"configuration, factory calibration for this unit: {lab.opa_path:.0f} mm."
        ),
        "delay_stage": (
            "Delay stage manual. place(stage, x, z, height, yaw): (x, z) is the stage reference point at "
            "the front of the rail and height the retroreflector apex height; yaw is the rail direction, "
            "pointing from the reference point toward the retroreflector. The retroreflector apex sits "
            f"{K.STAGE_APEX_OFFSET:.0f} mm + stage position along the rail from the reference point. Hollow "
            f"gold retroreflector, entrance face {K.RETRO_FRONT:.0f} mm in front of the apex, clear aperture "
            f"radius {K.RETRO_R:.1f} mm. Stage positions are in mm from 0 to the travel limit."
        ),
        "sample_mount": l1_sample if lab.level == 1 else l2_sample,
        "signal_camera": (
            f"Signal camera: zoomed Si CMOS, specified {K.CAM_SI_RANGE[0]:.0f}-{K.CAM_SI_RANGE[1]:.0f} nm (no "
            "specified response outside that range). It integrates the light leaving the sample in a fixed "
            "region of interest, through the filter holder (empty unless a filter is installed). Read noise "
            f"~{K.NOISE_FLOOR:.0f} counts rms at 1 s, falling as 1/sqrt(t_int); the ROI saturates at "
            f"{K.SIG_CAM_SAT} counts (reported as saturated). install(filter_id) puts a filter in the holder, "
            "uninstall('filter') empties it. The filter holder is not in the alignment camera's path."
        ),
        "mirror": (
            "Kinematic mirror mount. place(mirror-N, x, z, height, yaw): yaw is the direction the "
            "reflecting face points (its normal) in the table plane. knob(mirror, 'yaw'|'pitch', "
            "delta_mrad) tilts the mirror; range +/-50 mrad, actuator repeatability ~2%. rotate(part, deg) "
            "loosens the base, turns it and re-tightens (re-seat error ~0.2 deg)."
        ),
        "periscope": (
            "In-line periscope. place(periscope-N, x, z, height, yaw, height_in): yaw is the beam "
            "travel direction (in and out), height_in the input beam height, height the output "
            "height. Knobs act on the top mirror."
        ),
        "photodiode": (
            "Fast photodiode on the 1 GHz scope: read_signal returns the arrival time of each pulse "
            "reaching it, relative to the scope trigger (20 ps sampling, ~10 ps jitter)."
        ),
        "nonlinear": (
            "Crystal / sample / integrating-photodiode diagnostics in the sample mount. read_signal(t_int) "
            "returns counts averaged over t_int seconds (signal-camera ROI counts for crystals and samples, "
            "integrator counts for the GaP photodiode). scan(start, end, step, t_int) steps the delay stage "
            "and reads at each point (max 5000 points)."
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
