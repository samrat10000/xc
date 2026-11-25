"""Painted sunset sky for Ep3 Shot 01 (110% oversize for parallax drift).
Matches locked 01_speaker_v4 gradient stops, dual sun glow, 3 stratus cloud layers,
3 fbm mountain ridges + 1964 radio tower + subtle starry rift hint in zenith.
usage: python paint_bg01.py <meta.json> <out.png>
"""
import sys, json, numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image

META = json.load(open(sys.argv[1], encoding='utf-8'))
OUT = sys.argv[2]
SX, SY = float(META["SUN_SCREEN"][0]), float(META["SUN_SCREEN"][1])
# Map frame coordinates (0..1) into 110% oversize canvas
SX_BG = (SX - 0.5) / 1.1 + 0.5
SY_BG = (SY - 0.5) / 1.1 + 0.5

W, H = 1188, 2112
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
u, v = xx / W, yy / H


def C(*c):
    return np.array(c, np.float32)


def grad(stops):
    img = np.zeros((H, W, 3), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (v >= p0) & (v < p1)
        t = ((v - p0) / (p1 - p0))[m][:, None]
        img[m] = C(*c0) * (1 - t) + C(*c1) * t
    img[v >= stops[-1][0]] = C(*stops[-1][1])
    return img


def fbm(sx, sy, oct=5, seed=0):
    r = np.random.default_rng(seed)
    acc = np.zeros((H, W), np.float32); a = 1.0; tot = 0.0
    for o in range(oct):
        hh, ww = max(2, int(H / sy * 2 ** o / 64)), max(2, int(W / sx * 2 ** o / 64))
        n = r.standard_normal((hh, ww)).astype(np.float32)
        n = zoom(n, (H / hh, W / ww), order=3)[:H, :W]
        acc += n * a; tot += a; a *= 0.5
    acc /= tot
    return (acc - acc.mean()) / max(acc.std(), 1e-5)


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


sky = grad([
    (0.0, (0.13, 0.12, 0.27)),
    (0.22, (0.30, 0.20, 0.38)),
    (0.42, (0.70, 0.36, 0.42)),
    (0.58, (0.97, 0.55, 0.36)),
    (0.70, (1.0, 0.76, 0.48)),
    (0.80, (1.0, 0.86, 0.62)),
])

d = np.sqrt(((u - SX_BG) * W / H) ** 2 + (v - SY_BG) ** 2)
glow = (
    np.exp(-d / 0.06)[..., None] * C(1.0, 0.88, 0.60) * 0.95
    + np.exp(-d / 0.26)[..., None] * C(1.0, 0.62, 0.34) * 0.55
)
sky = sky + glow

# Three stratus cloud layers
for (y0, y1, sx, sy, thr, col, seed, rimk) in [
    (0.04, 0.28, 7.0, 1.0, 0.25, (0.24, 0.17, 0.34), 11, 0.25),
    (0.22, 0.50, 9.0, 1.2, 0.45, (0.46, 0.25, 0.40), 12, 0.60),
    (0.46, 0.68, 12.0, 1.4, 0.75, (0.80, 0.42, 0.42), 13, 1.00),
]:
    n = fbm(sx, sy, 6, seed)
    band = sstep(y0, y0 + 0.06, v) * (1 - sstep(y1 - 0.08, y1, v))
    m = sstep(thr, thr + 0.06, n * band + band * 0.4 - 0.4)
    below = np.roll(m, -int(0.010 * H), axis=0)
    under = np.clip(m - below, 0, 1)
    rim = gaussian_filter(np.clip(m - np.roll(m, -int(0.004 * H), axis=0), 0, 1), 0.8)
    near = np.exp(-np.abs(u - SX_BG) / 0.35) * np.exp(-np.abs(v - SY_BG) / 0.30)
    base = C(*col)[None, None] * (1 - 0.15 * gaussian_filter(n, 3)[..., None].clip(-1, 1))
    lit = C(1.0, 0.62, 0.42)
    cl = base + (lit - base) * (gaussian_filter(under, 6)[..., None] * 1.6 * near[..., None]).clip(0, 0.85)
    sky = sky * (1 - m[..., None]) + cl * m[..., None]
    sky += rim[..., None] * C(1.0, 0.85, 0.55) * (0.5 + 1.4 * near[..., None]) * rimk

# Faint scar of the Episode 1/2 sky rift high in the purple zenith (thin starry slit)
rift_y = 0.135 + 0.006 * np.sin(u * 17.0) + 0.004 * np.cos(u * 31.0)
rift_w = 0.0045 * np.exp(-((u - 0.58) / 0.28) ** 2)
rift_m = sstep(rift_w, rift_w * 0.2, np.abs(v - rift_y))
sky = sky * (1 - rift_m[..., None] * 0.78) + C(0.05, 0.06, 0.16) * (rift_m[..., None] * 0.78)
rift_edge = np.clip(sstep(rift_w * 1.5, rift_w * 0.8, np.abs(v - rift_y)) - rift_m, 0, 1)
sky += rift_edge[..., None] * C(0.65, 0.78, 1.0) * 0.32

# Crisp sun disk
sky = sky + (C(1.0, 0.97, 0.86) - sky) * sstep(0.024, 0.020, d)[..., None]


def ridge(seed, base, amp, sm):
    r = np.random.default_rng(seed)
    y = np.zeros(W)
    for o in range(7):
        n = 3 * 2 ** o
        y += np.interp(np.linspace(0, n, W), np.arange(n + 1), r.standard_normal(n + 1)) * 0.55 ** o
    y = gaussian_filter(y, max(1, sm / 4))
    return base - amp * (y - y.min()) / max(y.max() - y.min(), 1e-5)


RED = (0, 0)
for seed, base, amp, col, sm in [
    (21, 0.72, 0.070, (0.62, 0.40, 0.50), 14),
    (22, 0.77, 0.055, (0.38, 0.24, 0.36), 9),
    (23, 0.81, 0.032, (0.20, 0.13, 0.22), 5),
]:
    rl = ridge(seed, base, amp, sm)
    m = gaussian_filter((v > rl[None, :]).astype(np.float32), 0.7)
    haze = np.exp(-np.abs(u - SX_BG) / 0.30)[..., None] * C(0.25, 0.12, 0.05) * (0.9 if seed == 21 else 0.3)
    sky = sky * (1 - m[..., None]) + (C(*col) + haze) * m[..., None]
    if seed == 22:
        tx = 0.26; ty = rl[int(tx * W)]
        tw = (np.abs(u - tx) < (0.0012 + 0.0055 * np.clip((v - (ty - 0.065)) / 0.065, 0, 1))) & (v > ty - 0.065) & (v < ty + 0.01)
        sky[tw] = C(0.30, 0.19, 0.30)
        RED = (int(tx * W), int((ty - 0.067) * H))

np.save(OUT.replace('.png', '_red.npy'), np.array(RED))
img = np.clip(sky, 0, 1)
Image.fromarray((img * 255 + 0.5).astype(np.uint8)).save(OUT)
print('WROTE', OUT, 'SUN_BG', round(SX_BG, 3), round(SY_BG, 3), 'RED', RED)
