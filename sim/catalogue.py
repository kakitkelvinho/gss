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
    "BBO-T236": dict(
        slot="diagnostic", kind="diagnostic", price=1200,
        name="beta-BBO crystal 0.1 mm, theta = 23.6 deg, type I, with 450-550 nm bandpass filter and PMT",
        model="bbo_good",
        datasheet=(
            "beta-BBO, 0.1 mm thick, cut theta = 23.6 deg, phi = 90 deg (type I, o + o -> e). Mounted at "
            "the sample plane, followed by a 450-550 nm bandpass filter and a photon-counting PMT. "
            "Counting noise ~100 counts rms at 1 s integration, falling as 1/sqrt(t_int)."),
    ),
    "BBO-T292": dict(
        slot="diagnostic", kind="diagnostic", price=900,
        name="beta-BBO crystal 0.1 mm, theta = 29.2 deg, type I, with 380-420 nm bandpass filter and PMT",
        model="bbo_wrong",
        datasheet=(
            "beta-BBO, 0.1 mm thick, cut theta = 29.2 deg, phi = 90 deg (type I, o + o -> e). Mounted at "
            "the sample plane, followed by a 380-420 nm bandpass filter and a photon-counting PMT. "
            "Counting noise ~100 counts rms at 1 s integration, falling as 1/sqrt(t_int)."),
    ),
    "PD-FAST": dict(
        slot="diagnostic", kind="diagnostic", price=600, name="Fast InGaAs photodiode, 25 ps rise time",
        model="photodiode",
        datasheet=(
            "InGaAs photodiode, 800-1700 nm, 25 ps rise time, mounted at the sample plane, read on "
            "the table's 1 GHz scope, which reports the arrival time of each pulse (20 ps sampling, "
            "~10 ps jitter)."),
    ),
    "MIR-1": dict(
        slot="mounting", kind="mirror", price=150, name="1\" protected silver mirror in kinematic mount, on post",
        datasheet=(
            "1\" (25.4 mm) protected silver mirror, >97% at 700-2000 nm. Kinematic mount with "
            "two knobs (yaw, pitch), +/-50 mrad range each. Clear aperture: beams more than about "
            "10 mm from the centre start to clip. "
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
    "mounting": "Mirrors and periscopes",
}

FREE_EQUIPMENT = (
    "Already on the table, free: a sample mount with f = 100 mm achromatic lens and a flip-in "
    "camera at the lens focal plane (also images the lens plane), a 1 GHz oscilloscope at the "
    "desk, an IR viewer card, and beam-block shutters at both output ports."
)


def manuals(lab) -> dict[str, str]:
    """Device manuals: specifications and conventions only (no procedures). `lab` provides the
    per-seed facts (ports, split paths inside the laser housing, OPA internal path)."""
    p, q = lab.ports["pump"], lab.ports["probe"]
    return {
        "table": (
            f"Optical table: {K.TABLE_X:.0f} x {K.TABLE_Z:.0f} mm breadboard. Coordinates in mm: x along "
            f"the long side (0..{K.TABLE_X:.0f}), z across (0..{K.TABLE_Z:.0f}), height = height above the "
            f"breadboard (y). Yaw angles are in degrees in the table plane, measured from +x toward +z.\n"
            f"Laser housing (amplifier, 800 nm, ~100 fs FWHM, 1 kHz, and an OPA pumped by it) at the "
            f"x = {K.TABLE_X:.0f} end. Inside the housing the amplifier output is split: one part exits at "
            f"the pump port ({lab.split_pump:.0f} mm of path from the split), the other goes to the OPA "
            f"input ({lab.split_opa:.0f} mm of path from the split).\n"
            f"Pump output port (800 nm): x={p['pos'][0]:.0f}, z={p['pos'][2]:.0f}, height={p['pos'][1]:.0f}, "
            f"beam travelling toward -x (yaw 180). Collimated, 0.5 mm 1/e^2 radius, horizontally polarised.\n"
            f"Probe output port (OPA signal, 1300 nm, ~60 fs FWHM): x={q['pos'][0]:.0f}, z={q['pos'][2]:.0f}, "
            f"height={q['pos'][1]:.0f}, beam travelling toward -x (yaw 180). Collimated, 0.8 mm 1/e^2 radius, "
            f"horizontally polarised.\n"
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
            "OPA user manual (excerpt). Signal output 1300 nm, ~60 fs, horizontally polarised. "
            f"Internal optical path from the OPA pump input to the signal output port, factory "
            f"calibration for this unit: {lab.opa_path:.0f} mm."
        ),
        "delay_stage": (
            "Delay stage manual. place(stage, x, z, height, yaw): (x, z) is the stage reference point at "
            "the front of the rail and height the retroreflector apex height; yaw is the rail direction, "
            "pointing from the reference point toward the retroreflector. The retroreflector apex sits "
            f"{K.STAGE_APEX_OFFSET:.0f} mm + stage position along the rail from the reference point. Hollow "
            f"gold retroreflector, entrance face {K.RETRO_FRONT:.0f} mm in front of the apex, clear aperture "
            f"radius {K.RETRO_R:.1f} mm. Stage positions are in mm from 0 to the travel limit."
        ),
        "sample_mount": (
            "Sample mount with an f = 100 mm achromatic lens. place(sample, x, z, height, yaw): (x, z, "
            "height) is the lens centre, yaw the direction light travels through the lens. The sample "
            "position (and the installed diagnostic) is the lens focal plane. Lens clear aperture radius "
            f"{K.LENS_R} mm. install(item) swaps the diagnostic without moving the mount. Flip-in camera: "
            f"view_camera('sample') images the focal plane ({K.CAM_PIXEL*1000:.1f} um pixels, field of view "
            f"+/-{K.CAM_HALF_FOV} mm); view_camera('lens') images the lens plane. Each spot reports its "
            "centroid, 1/e^2 radius and relative_power (fraction of that beam's output power reaching the "
            "sample, ~2% reading noise). Image axes: h horizontal, positive toward (lens yaw - 90 deg) in "
            "the table plane; v up; the lens axis is h = v = 0. The camera does not distinguish wavelengths: "
            "spots are listed by position."
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
        "bbo": (
            "Crystal detector: crystal at the sample plane, followed by a filter and a PMT. read_signal(t_int) "
            "returns PMT counts averaged over t_int seconds. scan(start, end, step, t_int) steps the "
            "delay stage and reads at each point (max 5000 points)."
        ),
        "ir_card": (
            "IR viewer card. ir_card(part=...) shows where each beam hits that optic relative to "
            "its centre; ir_card(x=, z=, height=) shows any beam passing within 30 mm of that "
            "point. Offsets are in table coordinates (dx, dz, dheight), good to ~0.5 mm."
        ),
    }
