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
    "BBO-SFG-1300": dict(
        slot="diagnostic", kind="diagnostic", price=1200, name="BBO crystal, type-I SFG 800 nm + 1300 nm -> 495 nm, 0.1 mm, with PMT",
        model="bbo_good",
        datasheet=(
            "beta-BBO, 0.1 mm thick, cut for type-I sum-frequency generation of 800 nm + 1300 nm "
            "(theta = 23.6 deg), mounted at the sample plane with a filtered PMT for 495 nm. "
            "The cross (sum-frequency) term is proportional to I_pump x I_probe and appears only "
            "when the pulses overlap in space and time. Each beam alone also produces a weak, "
            "delay-independent background (residual SHG/scatter leaking through the filter). "
            "Peak cross signal with good alignment: ~1000 counts/shot-averaged reading; detection "
            "noise ~100 counts at 1 s integration, scaling as 1/sqrt(t_int)."),
    ),
    "BBO-SHG-800": dict(
        slot="diagnostic", kind="diagnostic", price=900, name="BBO crystal, type-I SHG 800 nm -> 400 nm, 0.1 mm, with PMT",
        model="bbo_wrong",
        datasheet=(
            "beta-BBO, 0.1 mm thick, cut for type-I second-harmonic generation of 800 nm "
            "(theta = 29.2 deg), with filtered PMT. Phase-matched for 800 nm SHG only; "
            "sum-frequency 800 + 1300 nm is strongly phase-mismatched at this cut (~1% efficiency "
            "of a matched crystal). A pump beam alone gives a strong 400 nm signal."),
    ),
    "PD-FAST": dict(
        slot="diagnostic", kind="diagnostic", price=600, name="Fast InGaAs photodiode, 25 ps rise time",
        model="photodiode",
        datasheet=(
            "InGaAs photodiode, 800-1700 nm, 25 ps rise time, mounted at the sample plane, read on "
            "the table's 1 GHz scope. Linear (not nonlinear) detector: it sees each pulse "
            "separately and reports its arrival time. Timing resolution on the 1 GHz scope: "
            "20 ps sampling, ~10 ps jitter (1 ps of delay = 0.3 mm of path)."),
    ),
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
    "mounting": "Mirrors and periscopes",
}

FREE_EQUIPMENT = (
    "Already on the table, free: a sample mount with f = 100 mm achromatic lens and a flip-in "
    "camera at the lens focal plane (also images the lens plane), a 1 GHz oscilloscope at the "
    "desk, an IR viewer card, and beam-block shutters at both output ports."
)


def manuals(lab) -> dict[str, str]:
    """Device manuals. `lab` provides per-seed facts (ports, OPA internal path)."""
    p, q = lab.ports["pump"], lab.ports["probe"]
    return {
        "table": (
            f"Optical table: {K.TABLE_X:.0f} x {K.TABLE_Z:.0f} mm breadboard. Coordinates in mm: x along "
            f"the long side (0..{K.TABLE_X:.0f}), z across (0..{K.TABLE_Z:.0f}), height = height above the "
            f"breadboard (y). Yaw angles are in degrees in the table plane, measured from +x toward +z.\n"
            f"Pump output port (amplifier, 800 nm, ~100 fs FWHM, 1 kHz): x={p['pos'][0]:.0f}, "
            f"z={p['pos'][2]:.0f}, height={p['pos'][1]:.0f}, beam travelling toward -x (yaw 180). "
            f"Collimated, 0.5 mm 1/e^2 radius, horizontally polarised (in the table plane).\n"
            f"Probe output port (OPA, 1300 nm, ~60 fs FWHM): x={q['pos'][0]:.0f}, z={q['pos'][2]:.0f}, "
            f"height={q['pos'][1]:.0f}, beam travelling toward -x (yaw 180). Collimated, 0.8 mm radius. "
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
            "OPA user manual (excerpt). Output: signal 1300 nm, ~60 fs, horizontally polarised (in the table "
            "plane, same as the 800 nm pump). The pump light travels an "
            f"internal path inside the OPA before the output port. Calibrated internal optical path "
            f"for this unit (serial on the housing): {lab.opa_path:.0f} mm, relative to the "
            "amplifier output. To reach temporal overlap with the direct 800 nm beam, the 800 nm "
            "arm must be longer than the 1300 nm arm's table path by this amount. It cannot be "
            "measured from outside the housing."
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
        "sample_mount": (
            "Sample mount with f = 100 mm lens. place(sample, x, z, height, yaw): (x, z, height) is "
            "the lens centre, yaw the direction light travels through the lens. The sample (and the "
            "installed diagnostic) sits at the focal plane 100 mm behind the lens. Lens clear "
            f"aperture radius {K.LENS_R} mm (clipping from ~{K.LENS_CLIP_START} mm). A collimated "
            "beam hitting the lens at angle theta to its axis focuses at f x theta from the axis, "
            "whatever point of the lens it hits, so overlapping the foci means matching the beams' "
            "ANGLES; where they hit the lens sets their crossing angle and must stay inside the "
            "aperture. Focal spot radius ~50 um for both beams. install(item) swaps the diagnostic; "
            "it does not change any path. Flip-in camera: view_camera('sample') images the focal "
            f"plane ({K.CAM_PIXEL*1000:.1f} um pixels, field of view +/-{K.CAM_HALF_FOV} mm, sub-pixel "
            "centroids); view_camera('lens') shows where each beam hits the lens (mm). Each spot also reports "
            "relative_power: the fraction of that beam's output power reaching the sample (~2% "
            "reading noise), so clipping on an optic shows up as a dim spot. Camera image "
            "axes: h = horizontal, positive toward the direction (lens yaw - 90 deg) in the table "
            "plane; v = up. The lens axis is h = v = 0."
        ),
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
            "that reaches the sample (relative to the scope trigger). Resolution ~20 ps (6 mm of "
            "path). Good for catching gross path errors (metres), not for finding time zero."
        ),
        "bbo": (
            "Nonlinear crystal + PMT at the sample plane. read_signal(t_int) returns counts averaged "
            "over t_int seconds; noise falls as 1/sqrt(t_int). The cross term exists only within "
            "~+/-100 fs of time zero (~30 um of path, ~15 um of stage travel) and only if the foci "
            "overlap. Each beam alone gives a delay-independent background: block one arm to "
            "measure the other's background. scan(start, end, step, t_int) moves the stage and "
            "reads at each point (max 5000 points)."
        ),
        "ir_card": (
            "IR viewer card. ir_card(part=...) shows where each beam hits that optic relative to "
            "its centre; ir_card(x=, z=, height=) shows any beam passing within 30 mm of that "
            "point. Offsets are in table coordinates (dx, dz, dheight), good to ~0.5 mm."
        ),
    }
