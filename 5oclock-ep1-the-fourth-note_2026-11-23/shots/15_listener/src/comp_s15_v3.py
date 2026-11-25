"""Composite shot 15 v2. Painted layers are projected per frame with the same camera as Blender (cam_v2.py).
Order: sky + clouds (pulled toward the crack) -> crack (night sky of the other side, stars, glass edges, fractures)
-> far ridge -> hand (masked by the crack lips) -> head (aerial haze) -> mountain (treeline, texture, rim) -> ground + road
-> 3D town -> wires/poles/tower -> fg pole -> shards -> glare, impact flash, bloom, grade, vignette, grain.
usage: python comp_s15_v2.py <celdir> <outdir> [frames]"""
import sys, os, math, glob, numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, map_coordinates, zoom, binary_erosion
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cam_v3 import *

CEL, OUT = sys.argv[1:3]
os.makedirs(OUT, exist_ok=True)
W, H = W_PX, H_PX
SS = 2
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def C(*c): return np.array(c, np.float32)


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a + 1e-9), 0, 1); return t * t * (3 - 2 * t)


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


# ---------------- angular maps ----------------
AZ0, AZ1, EL0, EL1 = -60.0, 60.0, -10.0, 60.0


def fbm_map(seed, sx, sy, ppd=10, octs=6):
    r = np.random.default_rng(seed); hh = int((EL1 - EL0) * ppd); ww = int((AZ1 - AZ0) * ppd)
    acc = np.zeros((hh, ww), np.float32); a = 1; tot = 0
    for o in range(octs):
        h = max(2, int(hh / sy * 2 ** o / 64)); w = max(2, int(ww / sx * 2 ** o / 64))
        acc += zoom(r.standard_normal((h, w)).astype(np.float32), (hh / h, ww / w), order=3)[:hh, :ww] * a; tot += a; a *= 0.5
    acc /= tot
    return (acc - acc.mean()) / acc.std()


def samp(m, az, el, ppd=10):
    return map_coordinates(m, [(el - EL0) * ppd, (az - AZ0) * ppd], order=1, mode='nearest')


CLOUDS = [(-1.0, 16.0, 7, 1.0, 0.25, (0.24, 0.17, 0.34), 1, 0.25), (3.0, 26.0, 9, 1.2, 0.45, (0.46, 0.25, 0.40), 2, 0.6),
          (-0.5, 12.0, 12, 1.4, 0.75, (0.80, 0.42, 0.42), 3, 1.0), (20.0, 60.0, 11, 1.0, 0.40, (0.27, 0.19, 0.37), 4, 0.0)]   # high cloud: no empty top
CMAPS = [fbm_map(c[6], c[2] * 1.4, c[3] * 3.0) for c in CLOUDS]
TEX = fbm_map(41, 0.35, 0.35, ppd=10)
rs = np.random.default_rng(9)
STAR = np.zeros((int((EL1 - EL0) * 30), int((AZ1 - AZ0) * 30)), np.float32)
idx = rs.integers(0, STAR.size, 9000); STAR.flat[idx] = rs.uniform(0.25, 1.0, 9000) ** 2
STAR = gaussian_filter(STAR, 0.6) * 6
SUN_AZ, SUN_EL = 9.0, 1.2
CRACK_AZ = math.degrees(math.atan2(-40, CRACK_Y)); CRACK_EL = math.degrees(math.atan2(470 - 28, CRACK_Y))


def angle_grids(f):
    p = math.radians(CAM_PITCH(f)); ty = (SENSOR / 2) / LENS_F(f); tx = ty * W / H
    X, Y = np.meshgrid(((np.arange(W) + .5) / W - .5) * 2 * tx, (.5 - (np.arange(H) + .5) / H) * 2 * ty)
    dy = math.cos(p) - Y * math.sin(p); dz = math.sin(p) + Y * math.cos(p)
    n = np.sqrt(X * X + dy * dy + dz * dz)
    return np.degrees(np.arctan2(X, dy)).astype(np.float32), np.degrees(np.arcsin(dz / n)).astype(np.float32)


def sky(f, az, el):
    v = np.clip(0.80 - (el + 1.0) / 26.0 * 0.80, 0, 0.80)
    stops = [(0.0, (0.13, 0.12, 0.27)), (0.22, (0.30, 0.20, 0.38)), (0.42, (0.70, 0.36, 0.42)), (0.58, (0.97, 0.55, 0.36)), (0.70, (1.0, 0.76, 0.48)), (0.80, (1.0, 0.86, 0.62))]
    img = np.zeros((H, W, 3), np.float32)
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        m = (v >= p0) & (v < p1); t = ((v - p0) / (p1 - p0))[m][:, None]
        img[m] = C(*c0) * (1 - t) + C(*c1) * t
    img[v >= 0.8] = C(*stops[-1][1])
    pour = ease((f - 2) / 30.0)
    dA = az - CRACK_AZ; dE = el - CRACK_EL; dd = np.sqrt(dA * dA + dE * dE) + 1e-3
    pull = 7.0 * pour * np.exp(-dd / 16.0)
    saz = az - dA / dd * pull; sel = el - dE / dd * pull
    dsun = np.sqrt(((az - SUN_AZ) * np.cos(np.radians(el))) ** 2 + (el - SUN_EL) ** 2)
    img = img + np.exp(-dsun / 2.0)[..., None] * C(1.0, 0.85, 0.55) * 0.8 + np.exp(-dsun / 9.0)[..., None] * C(1.0, 0.55, 0.30) * 0.30
    for (e0, e1, sx, sy, thr, col, seed, rimk), cm in zip(CLOUDS, CMAPS):
        n = samp(cm, saz, sel)
        band = sstep(e0, e0 + (3 if e0 < 15 else 9), el) * (1 - sstep(e1 - 4, e1, el))   # high cloud fades in: no hard line
        m = sstep(thr, thr + 0.06, n * band + band * 0.4 - 0.4)
        under = np.clip(m - np.roll(m, -int(0.010 * H), axis=0), 0, 1)
        rim = gaussian_filter(np.clip(m - np.roll(m, -int(0.004 * H), axis=0), 0, 1), 0.8)
        near = np.exp(-np.abs(az - SUN_AZ) / 26.0) * np.exp(-np.abs(el - SUN_EL) / 12.0)
        base = C(*col)[None, None]
        cl = base + (C(1.0, 0.62, 0.42) - base) * (gaussian_filter(under, 6)[..., None] * 1.6 * near[..., None]).clip(0, 0.85)
        img = img * (1 - m[..., None]) + cl * m[..., None]
        img += rim[..., None] * C(1.0, 0.85, 0.55) * (0.5 + 1.4 * near[..., None]) * rimk
    return img


# ---------------- crack: lips, fractures, shards ----------------
def lip_rows(f):
    """screen-space upper/lower lip row per pixel column (NaN outside the crack)"""
    up = [project((x, CRACK_Y, upper_lip(x, f)), f) for x in CXS]
    lo = [project((x, CRACK_Y, lower_lip(x, f)), f) for x in CXS]
    cols = np.arange(W, dtype=np.float32)
    ux = np.array([p[0] for p in up]); uy = np.array([p[1] for p in up]); ly = np.array([p[1] for p in lo]); lx = np.array([p[0] for p in lo])
    U = np.interp(cols, ux, uy, left=np.nan, right=np.nan); L = np.interp(cols, lx, ly, left=np.nan, right=np.nan)
    return U, L, up, lo


rf = np.random.default_rng(23)
FRACS = []
for k in range(18):
    upper = k % 2 == 0
    x0 = float(rf.uniform(-560, 520)); sgn = 1 if upper else -1
    pts = [(x0, 0.0)]; ang = math.radians(90 * sgn + rf.uniform(-55, 55)); Ltot = float(rf.uniform(70, 240))
    acc = 0.0
    while acc < Ltot:                                # glass cracks: long straight runs, sharp small kinks (not lightning)
        s = float(rf.uniform(22, 48)); ang += math.radians(rf.uniform(-13, 13))
        pts.append((pts[-1][0] + s * math.cos(ang), pts[-1][1] + s * math.sin(ang))); acc += s
    FRACS.append(dict(upper=upper, pts=pts, L=Ltot, late=bool(rf.random() < 0.35 and abs(x0 - HAND_X) < 260), w=float(rf.uniform(1.0, 2.2))))


def fracture_layer(f):
    im = Image.new('L', (W * SS, H * SS), 0); dr = ImageDraw.Draw(im)
    for fr in FRACS:
        g = ease((f - 3) / 22.0) if not fr['late'] else ease((f - IMPACT) / 6.0)
        if g <= 0: continue
        x0 = fr['pts'][0][0]; base = upper_lip(x0, f) if fr['upper'] else lower_lip(x0, f)
        out = []; acc = 0.0; lim = g * fr['L']
        for (ax, ay), (bx, by) in zip(fr['pts'], fr['pts'][1:]):
            sl = math.hypot(bx - ax, by - ay)
            if acc + sl > lim:
                t = (lim - acc) / sl; bx, by = ax + (bx - ax) * t, ay + (by - ay) * t
            p = project((ax, CRACK_Y, base + ay), f); q = project((bx, CRACK_Y, base + by), f)
            out.append((p[0] * SS, p[1] * SS, q[0] * SS, q[1] * SS)); acc += sl
            if acc >= lim: break
        for i, (a, b, c, d) in enumerate(out):
            wpx = max(1, int(fr['w'] * SS * (1 - 0.6 * i / max(1, len(out)))))
            dr.line([(a, b), (c, d)], fill=255, width=wpx)
    return np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255


rsh = np.random.default_rng(31)
SHARDS = [dict(x=float(HAND_X + rsh.uniform(-140, 140)), vx=float(rsh.uniform(-10, 10)), vy=float(rsh.uniform(-18, -4)), vz=float(rsh.uniform(-6, 14)),
               s=float(rsh.uniform(5, 15)), rot=float(rsh.uniform(0, 6.3)), w=float(rsh.uniform(-3, 3)), d0=float(rsh.uniform(0, 3))) for _ in range(22)]


def shards_draw(img, f):
    if f < IMPACT: return img
    im = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    for s in SHARDS:
        t = (f - IMPACT - s['d0']) / 24.0
        if t < 0: continue
        z0 = lower_lip(s['x'], IMPACT)
        cx, cy, cz = s['x'] + s['vx'] * t, CRACK_Y + s['vy'] * t, z0 + s['vz'] * t - 0.5 * 45.0 * t * t
        a = s['rot'] + s['w'] * t
        tri = [(cx + s['s'] * math.cos(a + k * 2.2), cy, cz + s['s'] * 0.8 * math.sin(a + k * 2.2 + 0.3 * k)) for k in range(3)]
        sp = [(p[0] * SS, p[1] * SS) for p in (project(q, f) for q in tri)]
        flip = math.sin(a * 1.7) > 0
        dr.polygon(sp, fill=(40, 46, 86, 255) if flip else (236, 150, 110, 255), outline=(220, 236, 255, 255))
    lay = np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    return img * (1 - lay[..., 3:4]) + lay[..., :3] * lay[..., 3:4]


# ---------------- terrain ----------------
def ridge_pts(seed, y, zbase, zamp, n=160, spikes=0.0):
    r = np.random.default_rng(seed); xs = np.linspace(-1600, 1600, n); zz = np.zeros(n)
    for o in range(6):
        k = 3 * 2 ** o
        zz += np.interp(np.linspace(0, k, n), np.arange(k + 1), r.standard_normal(k + 1)) * 0.55 ** o
    zz = (zz - zz.min()) / (zz.max() - zz.min()) * zamp + zbase
    if spikes:                                    # cedar treeline: small pointed bumps
        clump = np.interp(np.linspace(0, 40, n), np.arange(41), (r.random(41) < 0.65).astype(float))   # forest patches and gaps
        zz = zz + np.abs(r.standard_normal(n)) * spikes * (r.random(n) < 0.45) * clump
    return [(float(x), y, float(z)) for x, z in zip(xs, zz)]


FAR = ridge_pts(31, 1000.0, 40.0, 110.0)
MTN = ridge_pts(11, 800.0, 40.0, 95.0, n=900, spikes=5.5)


def polys_layer(items, f):
    im = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    for pts, col in items:
        sp = [(x * SS, y * SS) for x, y, d in (project(p, f) for p in pts) if d > 0]
        if len(sp) >= 3: dr.polygon(sp, fill=tuple(int(c * 255) for c in col) + (255,))
    return np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255


def ridge_poly(pts):
    return pts + [(pts[-1][0], pts[-1][1], -200), (pts[0][0], pts[0][1], -200)]


def ground_items():
    its = [([(-900, 6.0, GZ(6.0)), (900, 6.0, GZ(6.0)), (900, 141.0, 0.0), (-900, 141.0, 0.0)], (0.17, 0.12, 0.19)),
           ([(-1400, 141.0, 0.0), (1400, 141.0, 0.0), (1400, 790.0, 0.0), (-1400, 790.0, 0.0)], (0.21, 0.14, 0.21))]
    ys = list(np.arange(6.0, 206.0, 8.0))
    for a, b in zip(ys, ys[1:]):
        za, zb = GZ(a) + 0.04, GZ(b) + 0.04
        its.append(([(0.8, a, za), (9.2, a, za), (9.2, b, zb), (0.8, b, zb)], (0.20, 0.15, 0.22)))
        its.append(([(0.55, a, za + .02), (0.85, a, za + .02), (0.85, b, zb + .02), (0.55, b, zb + .02)], (0.42, 0.34, 0.40)))
        its.append(([(9.15, a, za + .02), (9.45, a, za + .02), (9.45, b, zb + .02), (9.15, b, zb + .02)], (0.42, 0.34, 0.40)))
        its.append(([(1.15, a, za + .02), (1.30, a, za + .02), (1.30, b, zb + .02), (1.15, b, zb + .02)], (0.62, 0.58, 0.60)))
        if int(a // 8) % 2 == 0:
            its.append(([(4.9, a, za + .02), (5.1, a, za + .02), (5.1, a + 4.0, GZ(a + 4.0) + .06), (4.9, a + 4.0, GZ(a + 4.0) + .06)], (0.80, 0.66, 0.30)))
    for mx, my in [(3.0, 30.0), (6.5, 62.0), (3.5, 118.0)]:
        its.append(([(mx - .5, my, GZ(my) + .05), (mx + .5, my, GZ(my) + .05), (mx + .5, my + .8, GZ(my + .8) + .05), (mx - .5, my + .8, GZ(my + .8) + .05)], (0.30, 0.24, 0.30)))
    # ÃƒÂ¥Ã‚Â¾Ã‚ÂÃƒÂ¨Ã‚Â¡Ã…â€™ road text block (painted as two worn bars, readable as road marking at this distance)
    for k, yy0 in enumerate((22.0, 23.6)):
        its.append(([(2.2, yy0, GZ(yy0) + .05), (4.4, yy0, GZ(yy0) + .05), (4.4, yy0 + 0.9, GZ(yy0 + .9) + .05), (2.2, yy0 + 0.9, GZ(yy0 + .9) + .05)], (0.66, 0.62, 0.62)))
    return its


GROUND = ground_items()


def lines_layer(f):
    im = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0)); dr = ImageDraw.Draw(im); ink = (26, 16, 30, 255)

    def L(p, q, wpx):
        a = project(p, f); b = project(q, f)
        if a[2] > 0 and b[2] > 0: dr.line([(a[0] * SS, a[1] * SS), (b[0] * SS, b[1] * SS)], fill=ink, width=max(1, int(wpx * SS)))

    def wire(p, q, sag, wpx, n=26):
        pts = []
        for k in range(n + 1):
            t = k / n; pr = project((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t - sag * 4 * t * (1 - t)), f)
            if pr[2] > 0: pts.append((pr[0] * SS, pr[1] * SS))
        if len(pts) > 1: dr.line(pts, fill=ink, width=max(1, int(wpx * SS)))

    poles = [(-2.6, 14.0), (14.0, 31.0), (-24.0, 36.0), (36.0, 60.0), (-52.0, 72.0), (66.0, 105.0), (-90.0, 118.0)]
    for px, py in poles:
        g0 = GZ(py)
        if py > 15: L((px, py, g0), (px, py, g0 + 8.4), max(1.5, 90.0 / py))
        L((px - 1.1, py, g0 + 7.7), (px + 1.1, py, g0 + 7.7), max(1.5, 70.0 / py)); L((px - 0.9, py, g0 + 6.9), (px + 0.9, py, g0 + 6.9), max(1.2, 50.0 / py))
    for a, b in zip(poles, poles[1:]):
        for dz, w in ((7.7, 1.6), (6.9, 1.4), (8.2, 1.3)):
            wire((a[0], a[1], GZ(a[1]) + dz), (b[0], b[1], GZ(b[1]) + dz), 0.9, max(1.0, w * 20.0 / max(a[1], 20) + 1.0))
    tx0, ty0 = -330.0, 1000.0; base = float(np.interp(tx0, [p[0] for p in FAR], [p[2] for p in FAR]))
    for k in range(10):
        z0 = base + 14 * k; z1 = z0 + 14; w0 = 9 * (1 - k / 11.0) + 1.2; w1 = 9 * (1 - (k + 1) / 11.0) + 1.2
        L((tx0 - w0, ty0, z0), (tx0 - w1, ty0, z1), 1.6); L((tx0 + w0, ty0, z0), (tx0 + w1, ty0, z1), 1.6)
        L((tx0 - w0, ty0, z0), (tx0 + w1, ty0, z1), 0.9); L((tx0 + w0, ty0, z0), (tx0 - w1, ty0, z1), 0.9)
    L((tx0, ty0, base + 140), (tx0, ty0, base + 160), 1.6)
    lay = np.asarray(im.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    return lay, project((tx0, ty0, base + 163), f)


def load(n, f):
    return np.asarray(Image.open(os.path.join(CEL, '%s_%03d.png' % (n, f))).convert('RGBA').resize((W, H), Image.LANCZOS)).astype(np.float32) / 255


def over(img, lay):
    return img * (1 - lay[..., 3:4]) + lay[..., :3] * lay[..., 3:4]


def frame(f):
    az, el = angle_grids(f)
    img = sky(f, az, el)
    # ---- crack: night sky of the other side through a jagged gash ----
    U, Lo, up, lo = lip_rows(f)
    inside = (yy >= U[None, :]) & (yy <= Lo[None, :])
    m = gaussian_filter(inside.astype(np.float32), 0.7)
    cyc = np.nanmean((U + Lo) / 2)
    night = C(0.03, 0.04, 0.11) + (C(0.10, 0.16, 0.34) - C(0.03, 0.04, 0.11)) * np.exp(-np.abs(yy - cyc) / 60.0)[..., None]
    night = night + (samp(STAR, az, el, 30) * 0.9)[..., None] * C(0.85, 0.90, 1.0)
    img = img * (1 - m[..., None]) + night * m[..., None]
    edge = np.clip(m - binary_erosion(inside, iterations=2).astype(np.float32), 0, 1)
    fr = fracture_layer(f)
    glint = np.clip(edge + fr, 0, 1)
    img = img + edge[..., None] * C(0.80, 0.92, 1.0) * 0.95 + fr[..., None] * C(0.86, 0.90, 1.0) * 0.55
    img = img + gaussian_filter(edge, 6)[..., None] * C(0.45, 0.62, 1.0) * 0.50 + gaussian_filter(fr, 3)[..., None] * C(0.55, 0.65, 1.0) * 0.08
    img = img + gaussian_filter(edge, 26)[..., None] * C(0.35, 0.50, 0.95) * 0.45 * ease((f - 1) / 10.0)
    # ---- far ridge ----
    far = polys_layer([(ridge_poly(FAR), (0.50, 0.34, 0.48))], f)
    img = over(img, far)
    haze_sun = np.exp(-np.abs(az - SUN_AZ) / 28.0)[..., None] * C(0.30, 0.14, 0.06)
    img = img + far[..., 3:4] * haze_sun * 0.8
    # ---- hand: visible through the gash, and below the lower lip once it is through ----
    hand = load('hand', f)                       # occlusion by the sky wall is done in 3D (holdout with the crack hole)
    ha = hand[..., 3:4]
    bgc = img.copy()
    img = img * (1 - ha) + (hand[..., :3] * 0.88 + bgc * 0.12) * ha
    # ---- head with aerial haze (thicker toward the ridge: scale) ----
    mtn = polys_layer([(ridge_poly(MTN), (0.36, 0.23, 0.34))], f)
    ridge_row = np.argmax(mtn[..., 3] > 0.5, axis=0).astype(np.float32); ridge_row[ridge_row == 0] = H
    hz = (0.06 + 0.28 * sstep(ridge_row[None, :] - 560, ridge_row[None, :] + 10, yy))[..., None]
    cel = load('cel', f); a = cel[..., 3:4]
    soft = np.stack([gaussian_filter(img[..., k], 45) for k in range(3)], -1)      # haze is air colour, never background detail
    tint = soft * 0.6 + C(0.95, 0.62, 0.48) * 0.4
    crgb = cel[..., :3] * (1 - hz) + tint * hz
    comp = img * (1 - a) + crgb * a
    wa = np.clip(a + ha, 0, 1)
    wrap = np.stack([gaussian_filter(img[..., c] * (1 - wa[..., 0]), 12) for c in range(3)], -1)
    inner = np.clip(1 - gaussian_filter(wa[..., 0], 8), 0, 1)[..., None] * wa
    img = comp + wrap * inner * 0.45
    # ---- mountain: forest texture, base haze, sun-side rim on the treeline ----
    n = samp(TEX, az, el)
    mrgb = mtn[..., :3] * (0.86 + 0.10 * np.clip(n, -1.5, 1.5))[..., None]
    mrgb = mrgb + (1 - sstep(-1.5, 5.5, el))[..., None] * C(0.20, 0.10, 0.10) * 0.55 + haze_sun * 0.45
    img = img * (1 - mtn[..., 3:4]) + mrgb * mtn[..., 3:4]
    rimm = np.clip(mtn[..., 3] - np.roll(mtn[..., 3], 4, axis=0), 0, 1)
    img = img + gaussian_filter(rimm, 1.0)[..., None] * C(1.0, 0.72, 0.45) * (0.20 + 1.0 * np.exp(-np.abs(az - SUN_AZ) / 14.0))[..., None]
    # ---- ground, 3D town, lines, fg ----
    img = over(img, polys_layer(GROUND, f))
    town = load('town', f)
    img = img * (1 - town[..., 3:4]) + (town[..., :3] * 0.9 + C(0.30, 0.18, 0.26) * 0.1) * town[..., 3:4]
    lines, red = lines_layer(f)
    img = img * (1 - lines[..., 3:4]) + C(0.10, 0.06, 0.12) * lines[..., 3:4]
    if (f // 12) % 2 == 0:
        # the 1964 tower's red light bends toward the crack (stretched along the direction to the gash, more each second)
        cx0, cy0, _ = project((-40.0, CRACK_Y, crack_center(-40.0)), f)
        vx, vy = cx0 - red[0], cy0 - red[1]; vl = math.hypot(vx, vy) + 1e-6; vx, vy = vx / vl, vy / vl
        along = (xx - red[0]) * vx + (yy - red[1]) * vy; across = -(xx - red[0]) * vy + (yy - red[1]) * vx
        stretch = 3.2 + 60.0 * ease((f - 20) / 70.0)
        lg = np.exp(-(np.clip(along, 0, None) ** 2) / (2 * stretch ** 2) - (np.clip(-along, 0, None) ** 2) / (2 * 3.2 ** 2) - across ** 2 / (2 * 2.6 ** 2))
        img = img + lg[..., None] * C(1.0, 0.15, 0.1) * 1.3
    img = shards_draw(img, f)
    img = over(img, load('fg', f))
    # ---- light ----
    sx, sy, _ = project((CRACK_Y * math.tan(math.radians(SUN_AZ)), CRACK_Y, CRACK_Y * math.tan(math.radians(SUN_EL)) + 28.0), f)
    dsx = np.sqrt((xx - sx) ** 2 + (yy - sy) ** 2) / H
    img = img + (np.exp(-dsx / 0.07) * 0.22 + np.exp(-dsx / 0.24) * 0.08)[..., None] * C(1.0, 0.70, 0.42)
    if f >= IMPACT:
        k = f - IMPACT
        img = img + math.exp(-k / 1.6) * 0.16 * C(0.70, 0.82, 1.0) * (0.4 + 0.6 * np.exp(-np.abs(yy - cyc) / 500.0))[..., None]
    hi = np.clip(img.max(-1, keepdims=True) - 0.86, 0, 1) / 0.14 * img
    img = img + np.stack([gaussian_filter(hi[..., c], 28) for c in range(3)], -1) * 0.28
    img = np.clip(img, 0, 1) * 1.04 + C(0.035, 0.02, 0.05)
    d = ((xx / W - .5) ** 2 * 1.4 + (yy / H - .5) ** 2)
    img = img * (1 - 0.30 * np.clip(d * 2.4, 0, 1))[..., None]
    g = gaussian_filter(np.random.default_rng(f).standard_normal((H, W)).astype(np.float32), 0.6)
    img = img + g[..., None] * 0.018 * (0.7 + 0.6 * (1 - img.mean(-1, keepdims=True)))
    Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)).save(os.path.join(OUT, '%03d.png' % f))


want = sorted(int(x) for x in sys.argv[3].split(',')) if len(sys.argv) > 3 else sorted(int(os.path.basename(p)[4:7]) for p in glob.glob(os.path.join(CEL, 'cel_*.png')))
for f in want:
    frame(f); print('comp', f, flush=True)
