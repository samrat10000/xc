# shot 15 v2: camera, timeline and crack geometry shared by the Blender build and the comp (pure python + numpy)
import math
import numpy as np
W_PX, H_PX = 1080, 1920
SENSOR = 36.0
NF = 108
CRACK_Y = 1150.0
IMPACT = 56                           # frame the fingers slam over the lip


def _ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def LENS_F(f):                        # slow push (lens 38 -> 41.5)
    return 38.0 + 3.5 * _ease((f - 1) / 107.0)


def SHAKE(f):                         # impact shake, decaying (degrees)
    if f < IMPACT: return 0.0
    k = f - IMPACT
    return 0.32 * math.exp(-k / 5.0) * math.sin(k * 2.4)


def CAM_PITCH(f):                     # the scale shot: slow tilt up + shake on the slam
    return 4.0 + 5.5 * _ease((f - 1) / 107.0) + SHAKE(f)


def CAM_POS(f):                       # hillside viewpoint above the town, tiny handheld drift
    return (0.10 * math.sin(f * 0.11), 0.0, 28.0 + 0.05 * math.sin(f * 0.07) + 0.06 * SHAKE(f))


def GZ(y):                            # ground height: the hillside falls toward the town
    return max(0.0, 24.0 - 0.17 * y)


def HEAD_POS(rise):
    return (95.0, 1100.0, 20.0 + 300.0 * rise)


# ---- the crack: a jagged gash in the sky plane y = CRACK_Y ----
_r = np.random.default_rng(7)
CXS = np.linspace(-700.0, 640.0, 120)
_J = (np.interp(CXS, np.linspace(-700, 640, 26), _r.standard_normal(26)) * 15
      + np.interp(CXS, np.linspace(-700, 640, 80), _r.standard_normal(80)) * 5)
HAND_X = -215.0


def crack_open(f):                    # 0..1: splits open, then tears wider when the hand slams through
    return 0.62 * _ease((f - 1) / 22.0) + 0.38 * _ease((f - IMPACT + 3) / 7.0)


def crack_center(x):
    return 470.0 + float(np.interp(x, CXS, _J)) * 0.9


def crack_half(x, f):
    j = abs(float(np.interp(x, CXS, _J)))
    prof = math.exp(-((x + 40.0) / 420.0) ** 2)
    hand = math.exp(-((x - HAND_X) / 180.0) ** 2) * _ease((f - IMPACT + 3) / 7.0) * 26.0
    return 1.0 + crack_open(f) * 78.0 * prof * (0.8 + 0.2 * j / 15.0) + hand


def lower_lip(x, f):
    return crack_center(x) - crack_half(x, f)


def upper_lip(x, f):
    return crack_center(x) + crack_half(x, f)


def project(P, f):
    """world point -> pixel (x, y) in 1080x1920, y down; plus depth"""
    c = CAM_POS(f); p = math.radians(CAM_PITCH(f))
    ty = (SENSOR / 2) / LENS_F(f); tx = ty * W_PX / H_PX
    d = (P[0] - c[0], P[1] - c[1], P[2] - c[2])
    depth = d[1] * math.cos(p) + d[2] * math.sin(p)
    xs = d[0] / depth
    ys = (-d[1] * math.sin(p) + d[2] * math.cos(p)) / depth
    return (W_PX * (0.5 + xs / (2 * tx)), H_PX * (0.5 - ys / (2 * ty)), depth)
