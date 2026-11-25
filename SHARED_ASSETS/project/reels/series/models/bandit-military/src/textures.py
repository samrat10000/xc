"""All 2D textures for the military Bandit: camo, panel/chassis recolours, tread plate, perforated mesh, stencil decals."""
import numpy as np, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, label, zoom, binary_dilation, binary_erosion
TEX, SK, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(5)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def hexc(h): return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)], np.float32)
def pnoise(n, sigma, seed):  # periodic smooth noise in [-1,1]
    r = np.random.default_rng(seed).standard_normal((n, n))
    f = np.fft.fft2(r); ky = np.fft.fftfreq(n)[:, None]; kx = np.fft.fftfreq(n)[None, :]
    f *= np.exp(-(kx ** 2 + ky ** 2) * (sigma ** 2) * 2 * np.pi ** 2)
    a = np.real(np.fft.ifft2(f)); a = (a - a.mean()) / a.std(); return np.clip(a / 2.5, -1, 1)
def save(a, name, mode='RGB'):
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), mode).save(os.path.join(OUT, name)); print('wrote', name, flush=True)
def grime(name, n):
    im = np.asarray(Image.open(os.path.join(TEX, name)).convert('RGB').resize((n, n), Image.LANCZOS)).astype(np.float32)
    L = im.mean(-1); g = L / L.mean(); return np.clip(g, .55, 1.6)

# ---------------- woodland camo, 1 tile = 4x4 UV units, grime tiled 4x inside
N = 2048
def warp(a, s, amt, seed):
    wx = pnoise(N, s, seed) * amt; wy = pnoise(N, s, seed + 1) * amt
    yy, xx = np.mgrid[0:N, 0:N]
    return a[((yy + wy).astype(int)) % N, ((xx + wx).astype(int)) % N]
A = warp(pnoise(N, 95, 1) + .25 * pnoise(N, 18, 2), 30, 40, 3)
B = warp(pnoise(N, 80, 4) + .25 * pnoise(N, 15, 5), 30, 40, 6)
Cn = warp(pnoise(N, 38, 7) + .3 * pnoise(N, 9, 8), 20, 30, 9)
green, dkgreen, brown, black = hexc('#555b3d'), hexc('#363d28'), hexc('#5b4a35'), hexc('#22221e')
col = np.zeros((N, N, 3), np.float32) + green
col[A > .16] = brown
col[B > .22] = dkgreen
col[(Cn > .38) & (A < .3)] = black
# faded / sun-bleached + dust bloom
dust = (pnoise(N, 120, 11) * .5 + .5)[..., None]
col = col * (1 - .18 * dust) + hexc('#857c63') * .18 * dust
g = np.tile(grime('Weathered_graphite_armor_-_aged_color.png', 512), (4, 4))[..., None]
col = col * g ** .8
save(col, 'camo.png')
# raised panels: darker olive drab single tone, keeps its own wear map
g2 = grime('Raised_ash_gray_panels_-_aged_color.png', 768)[..., None]
od = hexc('#40452f') * (1 - .1 * (pnoise(768, 60, 12)[..., None] * .5 + .5))
save(od * g2 ** .9, 'olive_panels.png')
g3 = grime('Dark_forged_tubular_chassis_-_aged_color.png', 512)[..., None]
src = np.asarray(Image.open(os.path.join(TEX, 'Dark_forged_tubular_chassis_-_aged_color.png')).convert('RGB').resize((512, 512))).astype(np.float32)
rust = np.clip((src[..., 0] - src[..., 2]) / 60, 0, 1)[..., None]          # keep the rusty spots of the original
save((hexc('#2b2d26') * (1 - rust) + hexc('#5a3a22') * rust) * g3 ** .6, 'chassis.png')

# ---------------- diamond tread plate normal map (tile = 25 cm)
T = 512
yy, xx = np.mgrid[0:T, 0:T] / T
h = np.zeros((T, T), np.float32)
for cx, cy, ang in [(.25, .25, .785), (.75, .25, -.785), (.25, .75, -.785), (.75, .75, .785)]:
    for ox in (-1, 0, 1):
        for oy in (-1, 0, 1):
            dx = xx - cx - ox; dy = yy - cy - oy
            u = dx * np.cos(ang) + dy * np.sin(ang); v = -dx * np.sin(ang) + dy * np.cos(ang)
            d = (u / .16) ** 2 + (v / .035) ** 2
            h = np.maximum(h, np.clip(1 - d, 0, 1) ** .35)
h = gaussian_filter(h, 1.2, mode='wrap') + .03 * pnoise(T, 6, 13)
gy, gx = np.gradient(h * 6)
n = np.stack([-gx, gy, np.ones_like(h)], -1); n /= np.linalg.norm(n, axis=-1, keepdims=True)
save((n * .5 + .5) * 255, 'tread_nrm.png')
wear = (h > .5) * 1.
save(np.stack([np.zeros_like(h), (.55 - .25 * wear) * 255, (.85) * 255 + 0 * h], -1), 'tread_rm.png')   # glTF: G=rough, B=metal
tb = hexc('#4a4d45') * (1 - .25 * (pnoise(T, 30, 14)[..., None] * .5 + .5)) * (1 + .35 * wear[..., None])
save(tb, 'tread_col.png')

# ---------------- perforated mesh plate (RGBA, round holes, staggered; tile = 12 cm)
P = 256
yy, xx = np.mgrid[0:P, 0:P] / P
holes = np.zeros((P, P), bool)
for i in range(8):
    for j in range(8):
        cx = (i + .5 * (j % 2)) / 8; cy = (j + .5) / 8
        for ox in (-1, 0, 1):
            holes |= ((xx - cx - ox) ** 2 + (yy - cy) ** 2) < (.042 ** 2)
mc = hexc('#3b3e35') * (1 - .2 * (pnoise(P, 20, 15)[..., None] * .5 + .5))
rgba = np.concatenate([mc * np.ones((P, P, 1)), (~holes)[..., None] * 255.], -1)
save(rgba, 'perf_mesh.png', 'RGBA')

# ---------------- stencil helpers
def stencil_text(txt, size, squeeze=.78, track=.08):
    f = ImageFont.truetype(FONT, size)
    glyphs = []
    for ch in txt:
        if ch == ' ':
            glyphs.append(np.zeros((int(size * 1.2), int(size * .3)), bool)); continue
        bb = f.getbbox(ch); w = bb[2] + 4; im = Image.new('L', (w, int(size * 1.2)), 0)
        ImageDraw.Draw(im).text((2, 0), ch, font=f, fill=255)
        m = np.asarray(im) > 128
        # stencil bridges: cut every enclosed counter to the outside, top and bottom
        lab, nl = label(~m)
        for k in range(1, nl + 1):
            ys, xs = np.nonzero(lab == k)
            if ys.min() == 0 or xs.min() == 0 or ys.max() == m.shape[0] - 1 or xs.max() == m.shape[1] - 1: continue
            cx = int(xs.mean()); bw = max(2, size // 11)
            col_ = m[:, cx]
            m[:ys.min(), cx - bw // 2:cx + bw // 2 + 1] = False if True else m
            m[ys.max():, cx - bw // 2:cx + bw // 2 + 1] = False
        glyphs.append(m)
    gap = int(size * track)
    W = sum(g.shape[1] for g in glyphs) + gap * len(glyphs); Hh = glyphs[0].shape[0]
    out = np.zeros((Hh, W), bool); x = 0
    for g in glyphs:
        out[:, x:x + g.shape[1]] |= g; x += g.shape[1] + gap
    ys, xs = np.nonzero(out); out = out[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    im = Image.fromarray((out * 255).astype(np.uint8)).resize((max(1, int(out.shape[1] * squeeze)), out.shape[0]), Image.LANCZOS)
    return np.asarray(im) / 255.
def place(canvas, m, x, y, anchor='lt'):
    h, w = m.shape
    if anchor == 'c': x -= w // 2; y -= h // 2
    canvas[y:y + h, x:x + w] = np.maximum(canvas[y:y + h, x:x + w], m)
def distress(a, seed, amount=.35, spray=True):
    Hh, Ww = a.shape
    n = zoom(np.random.default_rng(seed).random((Hh // 6 + 1, Ww // 6 + 1)), 6, order=1)[:Hh, :Ww]
    n2 = np.random.default_rng(seed + 1).random((Hh, Ww))
    chips = gaussian_filter(n, 2) < (.5 - amount * .5) * 0 + amount * .55
    a = a * (1 - chips * .95) * (1 - (n2 < .08) * .7)
    if spray:
        a = np.maximum(gaussian_filter(a, 1.0) * .95, a * .9)
        a = np.maximum(a, gaussian_filter(a, 6) * .18 * (n2 < .25))      # overspray dusting
    return np.clip(a, 0, 1)
def rgba_of(layers, Hh, Ww):
    out = np.zeros((Hh, Ww, 4), np.float32)
    for a, c in layers:
        c = hexc(c)
        out[..., :3] = out[..., :3] * (1 - a[..., None]) + c * a[..., None]
        out[..., 3] = np.maximum(out[..., 3], a * 255)
    return out

# ---------------- cow skull emblem from the sculpt's front depth
d = np.load(SK); dep = d['depth'].astype(np.float32); occ = dep >= 0
dep[~occ] = dep[occ].max() + 10
dep = dep.T[::-1]            # rows = z (top first), cols = y
occ = occ.T[::-1]
sm = gaussian_filter(dep, 1.5)
gy, gx = np.gradient(sm)
nrm = np.stack([-gx, -gy, np.full_like(gx, 1.4)], -1); nrm /= np.linalg.norm(nrm, axis=-1, keepdims=True)
L = np.array([-.45, .55, .7]); L /= np.linalg.norm(L)
lit = (nrm @ L)
deep = (dep - gaussian_filter(dep, 12)) > 2.5
sk = occ & (lit > .42) & ~deep
sk = binary_erosion(sk, iterations=1)
def emblem(size):
    # canvas wider for horns
    hh, ww = sk.shape; pad = int(ww * .9)
    E = np.zeros((hh + 40, ww + 2 * pad), np.float32)
    E[40:, pad:pad + ww] = sk
    im = Image.fromarray((E * 255).astype(np.uint8)); dr = ImageDraw.Draw(im)
    cy = 40 + int(hh * .04); cxl = pad + int(ww * .1); cxr = pad + int(ww * .9)
    for s, cx in ((-1, cxl), (1, cxr)):
        pts_o = []; pts_i = []
        for k in range(26):
            t = k / 25
            x = cx + s * (t * ww * .95); y = cy + 18 - 140 * t ** 2.2 + 50 * t
            th = 16 * (1 - t) + 1.5
            pts_o.append((x, y - th)); pts_i.append((x, y + th))
        if s < 0: pts_o = pts_o[:21]; pts_i = pts_i[:21]       # broken left horn, like the sculpt
        dr.polygon(pts_o + pts_i[::-1], fill=255)
        for k in range(3):                                       # growth ring gaps
            t = .12 + k * .07; x = cx + s * t * ww * .95; y = cy + 18 - 140 * t ** 2.2 + 50 * t
            dr.line([(x, y - 20), (x + s * 6, y + 20)], fill=0, width=3)
    E = np.asarray(im) / 255.
    ys, xs = np.nonzero(E > .5); E = E[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    s = size / max(E.shape)
    return np.asarray(Image.fromarray((E * 255).astype(np.uint8)).resize((int(E.shape[1] * s), int(E.shape[0] * s)), Image.LANCZOS)) / 255.

SAND, BLK, RED = '#cfc6a6', '#151512', '#7a1a14'
# hood (1000x1000) -- same layout zones as the old badge
H_ = 1000; a_s = np.zeros((H_, H_)); a_k = np.zeros((H_, H_))
em = emblem(470)
ring = np.zeros((H_, H_)); yy, xx = np.mgrid[0:H_, 0:H_]
r = np.sqrt((xx - 250) ** 2 + (yy - 225) ** 2); ring[(r > 140) & (r < 156)] = 1
a_k[(r < 162)] = 1                            # black backing disc
place(a_s, em, 250, 238, 'c'); a_s = np.maximum(a_s, ring)
place(a_s, stencil_text('BANDIT', 64), 250, 420, 'c')
place(a_s, stencil_text('RECON  07', 30), 250, 475, 'c')
place(a_s, stencil_text('4B-07', 44, .8), 70, 40)
place(a_k, stencil_text('NO STEP', 26), 250, 545, 'c')
hood = rgba_of([(distress(a_k, 1, .25) * .85, BLK), (distress(a_s, 2, .3), SAND)], H_, H_)
save(hood, 'decal_hood.png', 'RGBA')
# door / livery (1600x600)
a_s = np.zeros((600, 1600)); a_k = np.zeros((600, 1600)); a_r = np.zeros((600, 1600))
place(a_s, stencil_text('B-07', 210, .82), 830, 40)
place(a_s, stencil_text('DEAD ROADS RECON', 46), 832, 290)
place(a_s, stencil_text('3RD SURVIVOR COY', 30), 832, 352)
em2 = emblem(250); place(a_k, np.clip(binary_dilation(em2 > .5, iterations=7) * 1., 0, 1), 700, 190, 'c'); place(a_s, em2, 700, 190, 'c')
# kill tallies: rows of 4 strokes + slash, red-brown, hand painted
tal = Image.new('L', (1600, 600), 0); dr = ImageDraw.Draw(tal)
r2 = np.random.default_rng(3)
for g in range(9):
    gx0 = 1290 + (g % 3) * 95; gy0 = 70 + (g // 3) * 85
    for k in range(4):
        x = gx0 + k * 17 + r2.uniform(-2, 2); dr.line([(x, gy0 + r2.uniform(-3, 3)), (x + r2.uniform(-4, 4), gy0 + 62)], fill=255, width=7)
    if g < 8: dr.line([(gx0 - 8, gy0 + 52), (gx0 + 70, gy0 + 8)], fill=255, width=7)
a_r = np.asarray(tal) / 255.
door = rgba_of([(distress(a_k, 3, .2) * .8, BLK), (distress(a_s, 4, .3), SAND), (distress(a_r, 5, .15, False) * .9, RED)], 600, 1600)
save(door, 'decal_door.png', 'RGBA')
# rocker (1600x600): faded black/sand hazard chevrons + stencils
a_s = np.zeros((600, 1600)); a_k = np.zeros((600, 1600))
for k in range(4):
    x0 = 940 + k * 60
    poly = Image.new('L', (1600, 600), 0); ImageDraw.Draw(poly).polygon([(x0, 140), (x0 + 30, 140), (x0 - 20, 240), (x0 - 50, 240)], fill=255)
    a_s = np.maximum(a_s, np.asarray(poly) / 255.)
place(a_s, stencil_text('TOW', 60), 1350, 160)
place(a_k, stencil_text('DO NOT STEP', 40), 600, 420)
place(a_s, stencil_text('FUEL JP-8', 34), 100, 160)
rock = rgba_of([(distress(a_k, 6, .3) * .8, BLK), (distress(a_s, 7, .35), SAND)], 600, 1600)
save(rock, 'decal_rocker.png', 'RGBA')
# ammo can side stencil (512x256): yellow-on-olive, like real ammo cans
a_y = np.zeros((256, 512))
place(a_y, stencil_text('CARTRIDGES', 40), 256, 70, 'c')
place(a_y, stencil_text('CAL .50  LINKED', 34), 256, 130, 'c')
place(a_y, stencil_text('M2  200 RDS', 30), 256, 185, 'c')
can = np.zeros((256, 512, 4)); can[..., :3] = hexc('#4b5034'); can[..., 3] = 255
y_ = distress(a_y, 8, .25)[..., None]
can[..., :3] = can[..., :3] * (1 - y_) + hexc('#c9a93a') * y_
can[..., :3] *= (np.random.default_rng(9).random((256, 512, 1)) * .1 + .92)
save(can, 'ammo_can.png', 'RGBA')
# jerry can side emboss stencil
a_w = np.zeros((256, 256)); place(a_w, stencil_text('WATER', 40), 128, 128, 'c')
jc = np.zeros((256, 256, 4)); jc[..., :3] = hexc('#454b30'); jc[..., 3] = 255
w_ = distress(a_w, 10, .3)[..., None]; jc[..., :3] = jc[..., :3] * (1 - w_) + hexc('#d6d0bb') * w_
save(jc, 'jerry_water.png', 'RGBA')
# preview the emblem for the record
save(rgba_of([(emblem(600), SAND)], *emblem(600).shape), 'emblem_preview.png', 'RGBA')
