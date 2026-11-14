"""Physical and lab constants. Units: mm, s, fs, EUR unless stated otherwise."""

import math

C_MM_PER_FS = 2.99792458e-4  # speed of light

# Table (y-up convention: XZ is the table plane, +Y is height above the breadboard)
TABLE_X = 2400.0
TABLE_Z = 1200.0
MAX_HEIGHT = 300.0
MIN_POST_HEIGHT = 50.0
WALK_OFFSET = 300.0  # the walkway ring runs 300 mm outside the table edge
WALK_SPEED = 500.0  # mm/s, careful walking around an optical table
REACH = 600.0  # you can reach 600 mm in from the edge you stand at
DESK = (-WALK_OFFSET, 0.0, 600.0)  # desk with monitor and scope, at the x=0 end of the table
WATCH_RADIUS = 1500.0  # monitor readable within 1.5 m of the desk

# Arms: the direct 800 nm amplifier output and the OPA output (wavelength set per seed, see Lab)
ARMS = ("800nm", "opa")
OPA_LAMBDAS_NM = (1300.0, 600.0, 450.0)

# Pulses: Gaussian, durations quoted as intensity FWHM
TAU_800_FWHM = 100.0
TAU_OPA_FWHM = 60.0
# Cross-correlation 1/e half-width used in eta: exp(-(dt/tau_c)^2).
# Intensity I(t) ~ exp(-4 ln2 t^2 / FWHM^2) = exp(-t^2/T^2) with T = FWHM / (2 sqrt(ln2)).
# The cross-correlation of two such Gaussians has T_c^2 = T1^2 + T2^2.
TAU_C = math.sqrt(TAU_800_FWHM**2 + TAU_OPA_FWHM**2) / (2 * math.sqrt(math.log(2)))  # ~70 fs

# Beams (1/e^2 intensity radius of the collimated beam) and focusing
# The OPA's output telescope is set so that every wavelength focuses to the same ~52 um spot:
# w_coll(lambda) = lambda f / (pi W0_OPA), i.e. 0.80 mm at 1300 nm, 0.37 mm at 600 nm, 0.28 mm at 450 nm.
W_800 = 0.5
LAMBDA_800 = 800e-6
LENS_F = 100.0


def waist(lam: float, w_coll: float) -> float:
    return lam * LENS_F / (math.pi * w_coll)


W0_800 = waist(LAMBDA_800, W_800)  # ~51 um
W0_OPA = waist(1300e-6, 0.8)  # ~52 um at every OPA wavelength


def opa_w_coll(lam_nm: float) -> float:
    return lam_nm * 1e-6 * LENS_F / (math.pi * W0_OPA)

# Optics apertures
MIRROR_R = 12.7  # 1" optic
CLIP_START = 10.0  # transmission starts dropping this far off-centre
RETRO_R = 19.05  # 1.5" hollow retroreflector on the delay stage
RETRO_CLIP_START = 16.5
LENS_R = 12.7
LENS_CLIP_START = 10.5
STAGE_APEX_OFFSET = 90.0  # apex is 90 mm beyond the stage reference point at position 0
RETRO_FRONT = 40.0  # entrance face is 40 mm in front of the apex
# Mount bodies (they block beams): kinematic mount plate behind each 1" optic, posts, lens-mount ring
MOUNT_HALF = 19.0  # 38 mm square plate around the optic
MOUNT_DEPTH = (0.5, 12.0)  # plate occupies this range behind the reflecting surface
POST_R = 6.35  # 1/2" post
POST_BEHIND = 6.0  # post axis sits this far behind the reflecting surface
LENS_MOUNT_R = 25.4  # 2" lens-mount ring around the 1" lens

# Episode
BUDGET_S = 4 * 3600.0
MIN_ACTION_S = 5.0
SPEND_CAP = 30000.0
ALPHA = 0.2
BETA = 0.1  # soft lab-time penalty: using the whole budget costs 10% of the reward

# Detector models (see physics.py). Counts are for the reference alignment (T = O = 1).
CROSS_A = 1000.0  # cross term at time zero for a phase-matched crystal / allowed two-photon process
PM_MISMATCH = 0.01  # BBO used away from its cut
BBO_SHG_MATCHED = 20000.0  # single-beam SHG of a beam its cut is matched for
BBO_SHG_OTHER = 300.0  # single-beam SHG of a beam the cut is not matched for (x PM_MISMATCH)
GAN_TPA_SELF = 330.0  # one-colour two-photon yellow emission of a beam with 2 h nu > Eg
TPA_PD_SELF_800 = 1500.0  # two-photon photocurrent of the 800 nm beam alone in a TPA photodiode
TPA_PD_SELF_OPA = 800.0
LINEAR_ABS = 5.0e5  # one-photon absorption (h nu > Eg): huge linear signal
SCATTER = 2.0e5  # fundamental scattered into the signal camera's ROI (unfiltered)
SIG_CAM_SAT = 60000  # signal camera ROI saturates here
NOISE_FLOOR = 30.0  # counts at 1 s, scales 1/sqrt(t_int)
SOURCE_FLUCT = 0.03  # pulse-to-pulse/drift fluctuation of the total signal; does not average away
CAM_SI_RANGE = (400.0, 1000.0)
CAM_VSWIR_RANGE = (400.0, 1700.0)
CAM_PIXEL = 0.0055
CAM_NOISE_PX = 0.3
CAM_HALF_FOV = 4.0
SCOPE_QUANT_PS = 20.0
SCOPE_JITTER_PS = 10.0

# ----------------------------------------------------------------------------------------------
# Level 2: beams cross at full angle 90 deg at the sample (each 45 deg from the sample normal), each
# through its own f = 100 mm lens. On the tilted sample each spot is stretched by 1/cos45 along the
# horizontal in-plane direction t. Across the overlap region the relative arrival time varies as
# dt(x) = 2 x sin(phi/2) / c (x along t). The intensity product I_1 I_2 along t is Gaussian with
# 1/e half-width a = W_t / 2 (W_t = sqrt2 * 52 um), so the measured cross-correlation is the 70 fs one
# convolved with a Gaussian of 1/e half-width 2 a sin(phi/2) / c:
#   tau_eff^2 = tau_c^2 + (2 a sin(phi/2) / c)^2  (~187 fs), peak scaled by tau_c / tau_eff (~0.37).
# The reward uses tau_eff (the overlap window this geometry actually has).
L2_HALF_ANGLE = math.radians(45.0)
L2_STRETCH = 1.0 / math.cos(L2_HALF_ANGLE)
_A_T = W0_OPA * L2_STRETCH / 2.0
TAU_C_L2 = math.sqrt(TAU_C ** 2 + (2 * _A_T * math.sin(L2_HALF_ANGLE) / C_MM_PER_FS) ** 2)
L2_PEAK = TAU_C / TAU_C_L2
L2_SCATTER = 0.01  # signal camera looks head-on along the sample normal: only diffuse scatter
L2_LENS_SEP = 100.0  # each lens sits f = 100 mm before the sample point along its own axis
