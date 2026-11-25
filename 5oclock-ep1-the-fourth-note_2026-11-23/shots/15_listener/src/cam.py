# shared camera + timeline maths for shot 15 (pure python: used by build_s15.py inside Blender and by comp_s15.py)
import math
W_PX, H_PX = 1080, 1920
SENSOR = 36.0
LENS = 38.0
NF = 48


def _ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def LENS_F(f):                       # slow push in = lens 38 -> 41.5 (about 9% over the test)
    return 38.0 + 3.5 * _ease((f - 1) / 47.0)


def CAM_PITCH(f):                    # slow tilt up (deg): the scale shot
    return 4.0 + 5.5 * _ease((f - 1) / 47.0)


def CAM_POS(f):                      # eye height, tiny handheld drift
    return (0.10 * math.sin(f * 0.11), 0.0, 28.0 + 0.05 * math.sin(f * 0.07))


def HEAD_POS(rise):                  # world metres, head centre, behind the ridge -> above it
    return (60.0, 1150.0, 60.0 + 440.0 * rise)


def HAND_POS(slide):
    return (-185.0, 1120.0, 860.0 - 340.0 * slide)


def project(P, f):
    """world point -> pixel (x, y) in the 1080x1920 frame, y down; also depth"""
    c = CAM_POS(f); p = math.radians(CAM_PITCH(f))
    ty = (SENSOR / 2) / LENS_F(f); tx = ty * W_PX / H_PX
    d = (P[0] - c[0], P[1] - c[1], P[2] - c[2])
    fw = (0.0, math.cos(p), math.sin(p)); up = (0.0, -math.sin(p), math.cos(p))
    depth = d[0] * fw[0] + d[1] * fw[1] + d[2] * fw[2]
    xs = d[0] / depth
    ys = (d[0] * up[0] + d[1] * up[1] + d[2] * up[2]) / depth
    return (W_PX * (0.5 + xs / (2 * tx)), H_PX * (0.5 - ys / (2 * ty)), depth)


def GZ(y):                         # hillside: ground height at distance y (we look down over the town)
    return max(0.0, 24.0 - 0.17 * y)
