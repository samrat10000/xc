"""Composite shot 15 "The Listener". Everything painted (sky, crack, ridges, town, wires, tower) is drawn per frame from the SAME camera maths as the
Blender build (cam.py), so painted layers and the cel layer never drift apart.
Order: sky+clouds -> sun glare -> crack light -> far ridges -> Listener cel -> front mountain/ridges/town -> wires -> fg cel -> light wrap, bloom, grade, vignette, grain.
usage: python comp_s15.py <celdir> <outdir> [frames comma list]"""
import sys, os, math, glob, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, map_coordinates, zoom
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cam import *

CEL, OUT = sys.argv[1:3]
os.makedirs(OUT, exist_ok=True)
W, H = W_PX, H_PX
SS = 2
rng0 = np.random.default_rng(15)


def C(*c): return np.array(c, np.float32)


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a + 1e-9), 0, 1); return t * t * (3 - 2 * t)


# ---------- angular noise maps (az -70..70 deg, el -8..70 deg), 10 px / deg ----------
AZ0, AZ1, EL0, EL1, PPD = -70.0, 70.0, -8.0, 70.0, 10


def fbm_map(seed, sx, sy, octs=6):
    r = np.random.default_rng(seed); hh = int((EL1 - EL0) * PPD); ww = int((AZ1 - AZ0) * PPD)
    acc = np.zeros((hh, ww), np.float32); a = 1; tot = 0
    for o in range(octs):
        h = max(2, int(hh / sy * 2 ** o / 64)); w = max(2, int(ww / sx * 2 ** o / 64))
        n = r.standard_normal((h, w)).astype(np.float32)
        acc += zoom(n, (hh / h, ww / w), order=3)[:hh, :ww] * a; tot += a; a *= 0.5
    acc /= tot
    return (acc - acc.mean()) / acc.std()


CLOUDS = [(0.0, 18.0, 7, 1.0, 0.25, (0.24, 0.17, 0.34), 1, 0.25), (3.0, 24.0, 9, 1.2, 0.45, (0.46, 0.25, 0.40), 2, 0.6),
          (0.5, 15.0, 12, 1.4, 0.75, (0.80, 0.42, 0.42), 3, 1.0)]
CMAPS = [fbm_map(c[6], c[2] * 1.4, c[3] * 3.0) for c in CLOUDS]

SUN_AZ, SUN_EL = 10.5, 0.8
CRACK_AZ, CRACK_EL = -3.5, math.degrees(math.atan2(470 - 28.0, 1150))     # roughly where the crack sits


def angle_grids(f):
    p = math.radians(CAM_PITCH(f)); ty = (SENSOR / 2) / LENS_F(f); tx = ty * W / H
    xs = ((np.arange(W) + .5) / W - .5) * 2 * tx; ys = (.5 - (np.arange(H) + .5) / H) * 2 * ty
    X, Y = np.meshgrid(xs, ys)
    fw = np.array([0, math.cos(p), math.sin(p)]); up = np.array([0, -math.sin(p), math.cos(p)])
    dx = X; dy = fw[1] + Y * up[1]; dz = fw[2] + Y * up[2]
    n = np.sqrt(dx * dx + dy * dy + dz * dz)
    az = np.degrees(np.arctan2(dx, dy)).astype(np.float32); el = np.degrees(np.arcsin(dz / n)).astype(np.float32)
    return az, el


def sample_map(m, az, el):
    return map_coordinates(m, [(el - EL0) * PPD, (az - AZ0) * PPD], order=1, mode='nearest')


def sky_layer(f, az, el):
    v = np.clip(0.80 - el / 48.0 * 0.80, 0, 0.80)
    stops = [(0.0, (0.13, 0.12, 0.27)), (0.22, (0.30, 0.20, 0.38)), (0.42, (0.70, 0.36, 0.42)), (0.58, (0.97, 0.55, 0.36)), (0.70, (1.0, 0.76, 0.48)), (0.80, (1.0, 0.86, 0.62))]
    img = np.zeros((H, W, 3), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (v >= p0) & (v < p1); t = ((v - p0) / (p1 - p0))[m][:, None]
        img[m] = C(*c0) * (1 - t) + C(*c1) * t
    img[v >= 0.8] = C(*stops[-1][1])
    # clouds sucked toward the crack
    pour = sstep(2, 26, f)
    dA = az - CRACK_AZ; dE = el - CRACK_EL; dd = np.sqrt(dA * dA + dE * dE) + 1e-3
    pull = 9.0 * pour * np.exp(-dd / 22.0)
    saz = az - dA / dd * pull; sel = el - dE / dd * pull * 0.8
    dsun = np.sqrt(((az - SUN_AZ) * np.cos(np.radians(el))) ** 2 + (el - SUN_EL) ** 2)
    glow = np.exp(-dsun / 2.8)[..., None] * C(1.0, 0.85, 0.55) * 0.9 + np.exp(-dsun / 12)[..., None] * C(1.0, 0.55, 0.30) * 0.45
    img = img + glow
    for (e0, e1, sx, sy, thr, col, seed, rimk), cm in zip(CLOUDS, CMAPS):
        n = sample_map(cm, saz, sel)
        band = sstep(e0, e0 + 3, el) * (1 - sstep(e1 - 4, e1, el))
        m = sstep(thr, thr + 0.06, n * band + band * 0.4 - 0.4)
        below = np.roll(m, -int(0.010 * H), axis=0)
        under = np.clip(m - below, 0, 1)
        rim = gaussian_filter(np.clip(m - np.roll(m, -int(0.004 * H), axis=0), 0, 1), 0.8)
        near = np.exp(-np.abs(az - SUN_AZ) / 28.0) * np.exp(-np.abs(el - SUN_EL) / 14.0)
        base = C(*col)[None, None] * np.ones((H, W, 1), np.float32)
        cl = base + (C(1.0, 0.62, 0.42) - base) * (gaussian_filter(under, 6)[..., None] * 1.6 * near[..., None]).clip(0, 0.85)
        img = img * (1 - m[..., None]) + cl * m[..., None]
        img += rim[..., None] * C(1.0, 0.85, 0.55) * (0.5 + 1.4 * near[..., None]) * rimk
    img = img + (C(1.0, 0.97, 0.86) - img) * sstep(0.95, 0.80, dsun)[..., None]
    return img, dsun


# ---------- world -> screen helpers ----------
def proj_poly(pts, f):
    return [project(p, f)[:2] for p in pts]


def ridge_pts(seed, y, zbase, zamp, x0=-1400, x1=1400, n=140):
    r = np.random.default_rng(seed); xs = np.linspace(x0, x1, n); zz = np.zeros(n)
    for o in range(6):
        k = 3 * 2 ** o
        zz += np.interp(np.linspace(0, k, n), np.arange(k + 1), r.standard_normal(k + 1)) * 0.55 ** o
    zz = (zz - zz.min()) / (zz.max() - zz.min())
    return [(float(x), y, zbase + zamp * float(z)) for x, z in zip(xs, zz)]


def layer_from_polys(items, f):
    """items: list of (world polygon pts, rgb) -> RGBA float layer, supersampled"""
    im = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    for pts, col in items:
        sp = [(x * SS, y * SS) for x, y, d in (project(p, f) for p in pts) if d > 0]
        if len(sp) >= 3:
            dr.polygon(sp, fill=tuple(int(c * 255) for c in col) + (255,))
    im = im.resize((W, H), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255


def ridge_poly(pts, zfloor=-50):
    return pts + [(pts[-1][0], pts[-1][1], zfloor), (pts[0][0], pts[0][1], zfloor)]


FAR = ridge_pts(31, 1000.0, 40.0, 110.0)
MTN = ridge_pts(11, 800.0, 40.0, 95.0)
MID = ridge_pts(12, 330.0, 10.0, 34.0)
HILL = ridge_pts(13, 190.0, 2.0, 16.0)


def town_items(f):
    r = np.random.default_rng(21); items = []
    for i in range(46):
        y = r.uniform(40, 190); x = r.uniform(-150, 150) * y / 60 * 0.6 + r.uniform(-30, 30)
        w = r.uniform(9, 17); hb = r.uniform(5.5, 9.0); ridge_h = hb + r.uniform(2.0, 3.6)
        d = y
        col = tuple(np.array((0.20, 0.13, 0.22)) * (0.75 + 0.25 * (1 - d / 190)))
        g = GZ(y)
        items.append(((y, i), [(x - w / 2, y, g - 6), (x + w / 2, y, g - 6), (x + w / 2, y, g + hb), (x + w / 3.4, y, g + ridge_h), (x - w / 3.4, y, g + ridge_h), (x - w / 2, y, g + hb)], col))
        if r.random() < 0.55:
            wz = g + hb * 0.55; wx = x + r.uniform(-w / 3, w / 3)
            items.append(((y - 0.01, i + 1000), [(wx - 0.9, y, wz), (wx + 0.9, y, wz), (wx + 0.9, y, wz + 1.3), (wx - 0.9, y, wz + 1.3)], (1.0, 0.78, 0.45)))
    items.sort(key=lambda t: -t[0][0])
    return [(p, c) for _, p, c in items]


TOWN = town_items(0)


def draw_lines(layer_rgb, alpha_mask_fn):
    pass


def lines_layer(f):
    """wires, poles, the 1964 radio tower, roof tile lines, antennas: thin dark world-space lines"""
    im = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    ink = (26, 16, 30, 255)

    def L(p, q, wpx):
        a = project(p, f); b = project(q, f)
        if a[2] > 0 and b[2] > 0:
            dr.line([(a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS)], fill=ink, width=max(1, int(wpx * SS)))

    def wire(p, q, sag, wpx, n=26):
        pts = []
        for k in range(n + 1):
            t = k / n; x = p[0] + (q[0] - p[0]) * t; y = p[1] + (q[1] - p[1]) * t; z = p[2] + (q[2] - p[2]) * t - sag * 4 * t * (1 - t)
            pr = project((x, y, z), f)
            if pr[2] > 0: pts.append((pr[0] * SS, pr[1] * SS))
        if len(pts) > 1: dr.line(pts, fill=ink, width=max(1, int(wpx * SS)))

    poles = [(-2.6, 14.0), (14.0, 31.0), (-24.0, 36.0), (36.0, 60.0), (-52.0, 72.0), (66.0, 105.0), (-90.0, 118.0)]
    for px, py in poles:
        g0 = GZ(py); L((px, py, g0), (px, py, g0 + 8.4), max(2.0, 120.0 / py))
        L((px - 1.1, py, g0 + 7.7), (px + 1.1, py, g0 + 7.7), max(1.5, 70.0 / py))
        L((px - 0.9, py, g0 + 6.9), (px + 0.9, py, g0 + 6.9), max(1.2, 50.0 / py))
    for (a, b) in zip(poles, poles[1:]):
        for dz, w in ((7.7, 1.6), (6.9, 1.4), (8.2, 1.3)):
            wire((a[0], a[1], GZ(a[1]) + dz), (b[0], b[1], GZ(b[1]) + dz), 0.9, max(1.0, w * 20.0 / max(a[1], 20) + 1.0))
    # 1964 radio tower on the far-ridge (lattice), red light on top
    tx0, ty0 = -330.0, 1000.0; base = MTN_Z_AT(tx0)
    for k in range(10):
        z0 = base + 14 * k; z1 = z0 + 14; w0 = 9 * (1 - k / 11.0) + 1.2; w1 = 9 * (1 - (k + 1) / 11.0) + 1.2
        L((tx0 - w0, ty0, z0), (tx0 - w1, ty0, z1), 1.4); L((tx0 + w0, ty0, z0), (tx0 + w1, ty0, z1), 1.4)
        L((tx0 - w0, ty0, z0), (tx0 + w1, ty0, z1), 0.8); L((tx0 + w0, ty0, z0), (tx0 - w1, ty0, z1), 0.8)
    L((tx0, ty0, base + 140), (tx0, ty0, base + 160), 1.4)
    im = im.resize((W, H), Image.LANCZOS)
    red = project((tx0, ty0, base + 163), f)
    return np.asarray(im).astype(np.float32) / 255, red


def MTN_Z_AT(x):
    xs = [p[0] for p in FAR]; zs = [p[2] for p in FAR]
    return float(np.interp(x, xs, zs))


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def crack_layer(f, az, el):
    """the sky splits: jagged gash at y=1150, cold light of the other side pours out"""
    t = ease((f - 1) / 12.0); t2 = 0.75 + 0.25 * ease((f - 12) / 30.0)
    Hh = 95.0 * t * t2 + 1.2                                    # half-opening in metres
    xs = np.linspace(-640, 640, 90); r = np.random.default_rng(7)
    jag = np.interp(xs, np.linspace(-640, 640, 24), r.standard_normal(24)) * 16 + np.interp(xs, np.linspace(-640, 640, 70), r.standard_normal(70)) * 5
    prof = np.exp(-((xs + 80) / 330.0) ** 2) ** 1.0
    zc = 470 + jag * 0.9
    up = [(float(x), 1150.0, float(c + Hh * pf * (0.8 + 0.2 * abs(j) / 16))) for x, c, pf, j in zip(xs, zc, prof, jag)]
    lo = [(float(x), 1150.0, float(c - Hh * pf * (0.8 + 0.2 * abs(j) / 16))) for x, c, pf, j in zip(xs, zc, prof, jag)]
    poly = up + lo[::-1]
    im = Image.new('L', (W * SS, H * SS), 0); dr = ImageDraw.Draw(im)
    sp = [(x * SS, y * SS) for x, y, d in (project(p, f) for p in poly)]
    dr.polygon(sp, fill=255)
    m = np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    cx, cy, _ = project((-80, 1150, 470), f)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 / 2.2 + (yy - cy) ** 2)
    core = C(0.86, 0.93, 1.0); edge = C(0.40, 0.55, 0.85)
    inner = (core * np.exp(-d / 260.0)[..., None] + edge * (1 - np.exp(-d / 260.0))[..., None]) * (0.80 + 0.20 * np.clip((yy - cy) / 160.0 + 0.5, 0, 1))[..., None]
    # faint distant skyline of the other Earth inside the crack
    n = gaussian_filter(np.random.default_rng(f // 2).standard_normal((H, W)).astype(np.float32), 5)
    inner = inner * (0.94 + 0.06 * n[..., None])
    glow = (np.exp(-d / (150.0 + 90 * t))[..., None] * C(0.70, 0.82, 1.0) * 0.38 * t) + (np.exp(-d / 520.0)[..., None] * C(0.35, 0.45, 0.80) * 0.16 * t)
    return m, inner, glow, (cx, cy)


def ground_items():
    its = []
    ys = list(np.arange(6.0, 206.0, 8.0))
    its.append(([(-700, 6.0, GZ(6.0)), (700, 6.0, GZ(6.0)), (700, 206.0, GZ(206.0)), (-700, 206.0, GZ(206.0))], (0.17, 0.12, 0.19)))
    for a, b in zip(ys, ys[1:]):
        za, zb = GZ(a) + 0.04, GZ(b) + 0.04
        # asphalt road down the slope, kerbs, worn centre dashes, edge lines, a manhole
        its.append(([(0.8, a, za), (9.2, a, za), (9.2, b, zb), (0.8, b, zb)], (0.20, 0.15, 0.22)))
        its.append(([(0.55, a, za + 0.02), (0.85, a, za + 0.02), (0.85, b, zb + 0.02), (0.55, b, zb + 0.02)], (0.42, 0.34, 0.40)))
        its.append(([(9.15, a, za + 0.02), (9.45, a, za + 0.02), (9.45, b, zb + 0.02), (9.15, b, zb + 0.02)], (0.42, 0.34, 0.40)))
        its.append(([(1.15, a, za + 0.02), (1.30, a, za + 0.02), (1.30, b, zb + 0.02), (1.15, b, zb + 0.02)], (0.62, 0.58, 0.60)))
        if int(a // 8) % 2 == 0:
            its.append(([(4.9, a, za + 0.02), (5.1, a, za + 0.02), (5.1, a + 4.0, GZ(a + 4.0) + 0.06), (4.9, a + 4.0, GZ(a + 4.0) + 0.06)], (0.80, 0.66, 0.30)))
    for k, (mx, my) in enumerate([(3.0, 30.0), (6.5, 62.0), (3.5, 118.0)]):
        its.append(([(mx - 0.5, my, GZ(my) + 0.05), (mx + 0.5, my, GZ(my) + 0.05), (mx + 0.5, my + 0.8, GZ(my + 0.8) + 0.05), (mx - 0.5, my + 0.8, GZ(my + 0.8) + 0.05)], (0.30, 0.24, 0.30)))
    return its


GROUND = ground_items()


def MTN_layers(f):
    far = layer_from_polys([(ridge_poly(FAR), (0.50, 0.34, 0.48))], f)
    mtn = layer_from_polys([(ridge_poly(MTN), (0.36, 0.23, 0.34))], f)
    mid = layer_from_polys([(ridge_poly(MID), (0.24, 0.16, 0.26))], f)
    hill = layer_from_polys([(ridge_poly(HILL), (0.19, 0.12, 0.21))], f)
    gnd = layer_from_polys(GROUND, f)
    town = layer_from_polys(TOWN, f)
    return far, mtn, mid, hill, gnd, town


def over(base, layer, tint=None):
    a = layer[..., 3:4]; rgb = layer[..., :3]
    return base * (1 - a) + rgb * a


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def load(path):
    return np.asarray(Image.open(path).convert('RGBA').resize((W, H), Image.LANCZOS)).astype(np.float32) / 255


def frame(f):
    az, el = angle_grids(f)
    img, dsun = sky_layer(f, az, el)
    m, inner, glow, (cx, cy) = crack_layer(f, az, el)
    img = img + glow
    img = img * (1 - m[..., None]) + inner * m[..., None]
    far, mtn, mid, hill, gnd, town = MTN_layers(f)
    # haze toward the sun side on every ridge
    haze = np.exp(-np.abs(az - SUN_AZ) / 30.0)[..., None] * C(0.30, 0.14, 0.06)
    img = over(img, far * np.array([1, 1, 1, 1], np.float32))
    img = img + far[..., 3:4] * haze * 0.9
    cel = load(os.path.join(CEL, 'cel_%03d.png' % f))
    a = cel[..., 3:4]
    # distance haze on the Listener (1150 m away): pull it toward the crack-side sky, keep the rim
    cel_rgb = cel[..., :3] * 0.9 + img * 0.10
    comp = img * (1 - a) + cel_rgb * a
    # light wrap from the crack onto the Listener's inner edge (cold) and from the sun side (warm)
    wrapsrc = np.stack([gaussian_filter(img[..., c] * (1 - a[..., 0]), 12) for c in range(3)], -1)
    inner_edge = np.clip(1 - gaussian_filter(a[..., 0], 8), 0, 1)[..., None] * a
    comp = comp + wrapsrc * inner_edge * 0.5
    img = comp
    img = over(img, mtn); img = img + mtn[..., 3:4] * haze * 0.6
    img = over(img, mid); img = over(img, hill); img = over(img, gnd); img = over(img, town)
    # sun-side rim on the ridges + soft texture so the slabs do not read flat
    for lay, k in ((far, 0.5), (mtn, 0.9)):
        rimm = np.clip(lay[..., 3] - np.roll(lay[..., 3], 5, axis=0), 0, 1)
        img = img + gaussian_filter(rimm, 1.2)[..., None] * C(1.0, 0.72, 0.45) * (0.25 + 0.9 * np.exp(-np.abs(az - SUN_AZ) / 20.0))[..., None] * k
    lines, red = lines_layer(f)
    ink = np.array([0.10, 0.06, 0.12], np.float32)
    img = img * (1 - lines[..., 3:4]) + ink * lines[..., 3:4]
    # tower red light blink
    if (f // 12) % 2 == 0:
        g = np.exp(-((xx - red[0]) ** 2 + (yy - red[1]) ** 2) / (2 * 3.2 ** 2))
        img = img + g[..., None] * np.array([1.0, 0.15, 0.1]) * 1.3
    # foreground cel pass (pole + horn, in front of everything)
    fg = load(os.path.join(CEL, 'fg_%03d.png' % f))
    img = img * (1 - fg[..., 3:4]) + fg[..., :3] * fg[..., 3:4]
    # light wrap of the sun/crack onto the foreground silhouette edge
    # veiling glare: sun on the right, crack in the middle (keeps the frame from going flat)
    sx, sy, sd = project((1150 * math.tan(math.radians(SUN_AZ)), 1150.0, 1150 * math.tan(math.radians(SUN_EL)) + 1.6), f)
    dsx = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2) / H
    img = img + (np.exp(-dsx / 0.07) * 0.22 + np.exp(-dsx / 0.22) * 0.07)[..., None] * C(1.0, 0.72, 0.42) * (1 - 0.7 * ease((f - 1) / 47.0))
    # bloom
    hi = np.clip(img.max(-1, keepdims=True) - 0.80, 0, 1) / 0.2 * img
    bl = np.stack([gaussian_filter(hi[..., c], 28) for c in range(3)], -1)
    img = img + bl * 0.30
    img = np.clip(img, 0, 1)
    img = img * 1.04 + np.array([0.035, 0.02, 0.05])
    d = ((xx / W - .5) ** 2 * 1.4 + (yy / H - .5) ** 2)
    img = img * (1 - 0.30 * np.clip(d * 2.4, 0, 1))[..., None]
    n = gaussian_filter(np.random.default_rng(f).standard_normal((H, W)).astype(np.float32), 0.6)
    img = img + n[..., None] * 0.018 * (0.7 + 0.6 * (1 - img.mean(-1, keepdims=True)))
    Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)).save(os.path.join(OUT, '%03d.png' % f))


want = sorted(int(x) for x in sys.argv[3].split(',')) if len(sys.argv) > 3 else sorted(int(os.path.basename(p)[4:7]) for p in glob.glob(os.path.join(CEL, 'cel_*.png')))
for f in want:
    frame(f); print('comp', f, flush=True)
