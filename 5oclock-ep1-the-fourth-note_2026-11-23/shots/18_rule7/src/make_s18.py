"""5 O'CLOCK Ep1 "The Fourth Note" - shot 18 "Rule seven" (4 s, 96 f @24). Top-down insert on Officer Tanaka's old rules notebook.
Rule 7 has been torn out. Under the tear, new ink writes itself, in Sam's handwriting. Then black (12 f = 0.5 s; the chime: three notes, then nothing).
Painted in 2D (numpy + PIL): aged paper, ruled lines, red margin + red hanko (the accent), real torn edge with fibres, handwriting from a
font made irregular per glyph (tilt, size, baseline, pressure wobble, ink bleed), dusk window light with a mullion shadow, dust motes, grain.
usage: python make_s18.py <outdir>"""
import os, sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, map_coordinates, zoom

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920; S = 2                    # page painted at 2x
PW, PH = int(W * 1.12) * S, int(H * 1.12) * S
rng = np.random.default_rng(18)
FE = 'C:/Windows/Fonts/Inkfree.ttf'; FES = 'C:/Windows/Fonts/segoeprb.ttf'   # v3: English rules in a real handwriting font (Sam)
FJ = 'C:/Windows/Fonts/YuGothM.ttc'; FJL = 'C:/Windows/Fonts/YuGothL.ttc'; FJB = 'C:/Windows/Fonts/YuGothB.ttc'


def fbm(h, w, sc, seed, octs=5):
    r = np.random.default_rng(seed); acc = np.zeros((h, w), np.float32); a = 1; tot = 0
    for o in range(octs):
        hh, ww = max(2, int(h / sc * 2 ** o)), max(2, int(w / sc * 2 ** o))
        acc += zoom(r.standard_normal((hh, ww)).astype(np.float32), (h / hh, w / ww), order=3)[:h, :w] * a; tot += a; a *= 0.5
    acc /= tot; return (acc - acc.mean()) / (acc.std() + 1e-6)


# ---------------- desk + notebook + page ----------------
yy, xx = np.mgrid[0:PH, 0:PW].astype(np.float32)
desk = np.stack([0.30 + 0.0 * xx, 0.19 + 0.0 * xx, 0.14 + 0.0 * xx], -1)
grain = fbm(PH, PW, 900, 1) * 0.5 + np.sin((xx * 0.004 + fbm(PH, PW, 400, 2) * 1.2) * 6) * 0.5
desk = desk * (0.86 + 0.08 * grain[..., None])
X0, X1, Y0, Y1 = int(PW * 0.10), int(PW * 0.93), int(PH * 0.07), int(PH * 0.95)            # the open notebook
cover = np.zeros((PH, PW), np.float32); cover[Y0 - 26:Y1 + 26, X0 - 26:X1 + 26] = 1
img = desk * (1 - cover[..., None]) + np.array([0.20, 0.13, 0.11]) * cover[..., None] * (0.9 + 0.1 * fbm(PH, PW, 200, 3)[..., None])
page = np.zeros((PH, PW), np.float32); page[Y0:Y1, X0:X1] = 1
page = gaussian_filter(page, 1.2)
paper = np.array([0.90, 0.85, 0.74]) * (0.95 + 0.04 * fbm(PH, PW, 300, 4)[..., None]) - 0.05 * np.clip(fbm(PH, PW, 120, 5), 0, 3)[..., None] * np.array([0.2, 0.35, 0.6])
# foxing spots + a coffee ring + yellowed edges
for i in range(40):
    cx, cy, r = rng.uniform(X0, X1), rng.uniform(Y0, Y1), rng.uniform(4, 22) * S
    paper -= (np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)) * 0.07)[..., None] * np.array([0.3, 0.5, 0.9])
cx, cy, r = X1 - 260 * S, Y0 + 300 * S, 120 * S
ring = np.exp(-((np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2) - r) / (5 * S)) ** 2)
paper -= ring[..., None] * 0.10 * np.array([0.2, 0.45, 0.8])
edge = np.minimum.reduce([xx - X0, X1 - xx, yy - Y0, Y1 - yy]) / S
paper -= np.exp(-np.clip(edge, 0, None) / 40)[..., None] * 0.10 * np.array([0.2, 0.4, 0.8])
img = img * (1 - page[..., None]) + paper * page[..., None]
# ruled lines + red margin
LINE0, LH = Y0 + 330 * S, 118 * S
for k in range(30):
    y = LINE0 + k * LH
    if y > Y1 - 40 * S: break
    band = np.exp(-((yy - y) / (1.3 * S)) ** 2) * page
    img = img * (1 - 0.35 * band[..., None]) + np.array([0.45, 0.58, 0.78]) * 0.35 * band[..., None]
MX = X0 + 150 * S
mband = np.exp(-((xx - MX) / (1.4 * S)) ** 2) * page
img = img * (1 - 0.55 * mband[..., None]) + np.array([0.80, 0.24, 0.20]) * 0.55 * mband[..., None]
BASE = img.copy()

# ---------------- handwriting: a font made irregular glyph by glyph ----------------
def hand(text, size, seed, slant, ink, wobble, fontp=FJ):
    """returns (alpha HxW float at 2x page scale, list of glyph x-extents for write-on)"""
    r = np.random.default_rng(seed); layer = Image.new('L', (PW, PH), 0); boxes = []
    return layer, boxes, r


def write_line(layer, x, y, text, size, r, slant, fontp, boxes):
    d = ImageDraw.Draw(layer)
    for ch in text:
        if ch == ' ': x += size * 0.4; continue
        lat = ch.isascii(); fs = int(size * (r.uniform(0.96, 1.04) if lat else r.uniform(0.84, 1.12))); fnt = ImageFont.truetype(fontp, fs)
        g = Image.new('L', (fs * 2, fs * 2), 0); ImageDraw.Draw(g).text((fs // 2, fs // 3), ch, font=fnt, fill=255)
        g = g.rotate((r.uniform(-2, 2) if lat else r.uniform(-7, 7)) + slant, resample=Image.BICUBIC)
        gy = y + (r.uniform(-0.025, 0.025) if lat else r.uniform(-0.09, 0.09)) * size
        layer.paste(g, (int(x), int(gy - fs // 3)), g)
        w = fnt.getlength(ch) * r.uniform(0.98, 1.06)
        boxes.append((x + fs * 0.5, x + fs * 0.5 + w, gy, gy + fs))
        x += w * r.uniform(0.96, 1.04)
    return x


def inkify(layer, seed, wob):
    a = np.asarray(layer).astype(np.float32) / 255
    if wob:                                                      # pen wobble: tiny displacement field
        dy = gaussian_filter(np.random.default_rng(seed).standard_normal(a.shape).astype(np.float32), 6) * wob
        dx = gaussian_filter(np.random.default_rng(seed + 1).standard_normal(a.shape).astype(np.float32), 6) * wob
        a = map_coordinates(a, [yy + dy, xx + dx], order=1)
    press = 0.75 + 0.25 * np.clip(fbm(PH, PW, 60, seed + 2) * 0.5 + 0.5, 0, 1)       # pressure variation
    bleed = gaussian_filter(a, 1.8 * S) * 0.45
    return np.clip(a * press + bleed, 0, 1)


R = np.random.default_rng(7)
officer = Image.new('L', (PW, PH), 0); ob = []
write_line(officer, MX + 30 * S, Y0 + 120 * S, '霧山町 五時の規則', 64 * S, R, -2, FJB, ob)
RULES = ["1. When the five o’clock song plays, freeze.", '2. Turn every mirror to the wall.', '3. Cover your ears.', "4. If they call your name, don’t turn.", '5. Never count the fourth note.', '6. If the song stops at three, go inside.']
for k, rl in enumerate(RULES):
    write_line(officer, MX + 30 * S, LINE0 + k * LH - 66 * S, rl, 37 * S, R, -1, FE, ob)
OFF = inkify(officer, 11, 3.0 * S)
# the officer's red hanko (ç”°ä¸­), slightly rotated, uneven ink
hk = Image.new('L', (PW, PH), 0); dh = ImageDraw.Draw(hk); hx, hy, hr = X1 - 190 * S, Y0 + 150 * S, 62 * S
dh.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), outline=255, width=7 * S)
fnt = ImageFont.truetype(FJB, 46 * S); dh.text((hx - 24 * S, hy - 54 * S), '田', font=fnt, fill=255); dh.text((hx - 24 * S, hy - 6 * S), '中', font=fnt, fill=255)
hk = hk.rotate(9, center=(hx, hy), resample=Image.BICUBIC)
HANKO = np.asarray(hk).astype(np.float32) / 255 * (0.55 + 0.45 * np.clip(fbm(PH, PW, 30, 21) * 0.5 + 0.6, 0, 1))
BASE = BASE * (1 - 0.88 * OFF[..., None]) + np.array([0.14, 0.15, 0.27]) * 0.88 * OFF[..., None]
BASE = BASE * (1 - 0.80 * HANKO[..., None]) + np.array([0.78, 0.13, 0.11]) * 0.80 * HANKO[..., None]

# ---------------- rule 7: torn out (ragged hole with fibres, the next page shows beneath) ----------------
TY0, TY1 = LINE0 + 6 * LH - 108 * S, LINE0 + 6 * LH + 26 * S
xs = np.arange(PW)
top = TY0 + np.cumsum(np.random.default_rng(31).normal(0, 1.8 * S, PW)) * 0.08 + gaussian_filter(np.random.default_rng(32).normal(0, 9 * S, PW), 30)
bot = TY1 + np.cumsum(np.random.default_rng(33).normal(0, 1.8 * S, PW)) * 0.08 + gaussian_filter(np.random.default_rng(34).normal(0, 9 * S, PW), 30)
hole = ((yy > top[None, :]) & (yy < bot[None, :]) & (xx > X0 + 6 * S) & (xx < X1 - 4 * S)).astype(np.float32)
hole = gaussian_filter(hole, 0.8)
under = np.array([0.76, 0.70, 0.58]) * (0.94 + 0.05 * fbm(PH, PW, 260, 41)[..., None])      # the page beneath: plainer, a shade darker
for k in range(-1, 2):
    y = LINE0 + 6 * LH - 40 * S + k * LH
    band = np.exp(-((yy - y) / (1.3 * S)) ** 2)
    under = under * (1 - 0.30 * band[..., None]) + np.array([0.45, 0.58, 0.78]) * 0.30 * band[..., None]
fib = np.zeros((PH, PW), np.float32)                               # torn-paper fibres: short pale hairs along both edges
fr = np.random.default_rng(50)
fl = Image.new('L', (PW, PH), 0); dfl = ImageDraw.Draw(fl)
for i in range(900):
    x = fr.uniform(X0, X1); e = top if i % 2 else bot; y0 = e[int(x)]
    L = fr.uniform(3, 14) * S; ang = (math.pi / 2 if i % 2 else -math.pi / 2) + fr.uniform(-0.7, 0.7)
    dfl.line([(x, y0), (x + math.cos(ang) * L, y0 + math.sin(ang) * L)], fill=int(fr.uniform(150, 255)), width=max(1, int(fr.uniform(0.6, 1.6) * S)))
FIB = np.asarray(fl).astype(np.float32) / 255
lip = np.clip(gaussian_filter(hole, 3 * S) - hole, 0, 1)            # the torn lip: whiter raw paper, thin shadow inside
BASE = BASE * (1 - hole[..., None]) + under * hole[..., None]
BASE = BASE + lip[..., None] * np.array([0.10, 0.10, 0.08]) - gaussian_filter(hole, 5 * S)[..., None] * 0.05 * (1 - hole[..., None]) - (hole * np.clip(1 - (yy - top[None, :]) / (22 * S), 0, 1))[..., None] * 0.16
BASE = BASE * (1 - FIB[..., None] * 0.6) + np.array([0.97, 0.95, 0.88]) * FIB[..., None] * 0.6

# ---------------- the new ink, in Sam's hand (slanted the other way, faster, heavier) ----------------
sam = Image.new('L', (PW, PH), 0); sb = []
RS = np.random.default_rng(77)
write_line(sam, MX + 34 * S, LINE0 + 6 * LH - 92 * S, '7. Never finish the song.', 50 * S, RS, 3, FES, sb)
SAM = inkify(sam, 71, 4.2 * S)

# ---------------- per frame: write-on, window light, motes, camera drift, grade ----------------
G = np.mgrid[0:H, 0:W].astype(np.float32); gy, gx = G
rngm = np.random.default_rng(5); NM = 50
mote = dict(x=rngm.uniform(0, 1, NM), y=rngm.uniform(0, 1, NM), r=rngm.uniform(1.0, 3.2, NM), vx=rngm.uniform(-0.0006, 0.0006, NM), vy=rngm.uniform(-0.0008, 0.0002, NM), ph=rngm.uniform(0, 6.3, NM))


def ease(t):
    t = min(max(t, 0), 1); return t * t * (3 - 2 * t)


NB = len(sb); T0, T1 = 24, 70
for f in [int(x) for x in os.environ.get('FRAMES', '').split(',') if x] or range(1, 97):
    if f >= 85:
        Image.new('RGB', (W, H), (0, 0, 0)).save(os.path.join(OUT, '%03d.png' % f)); continue
    # write-on: each glyph revealed left->right in its turn; wet ink darker, dries lighter
    rev = np.zeros((PH, PW), np.float32); wet = np.zeros((PH, PW), np.float32)
    prog = (f - T0) / (T1 - T0) * NB
    for i, (a0, a1, b0, b1) in enumerate(sb):
        k = np.clip(prog - i, 0, 1)
        if k <= 0: continue
        xcut = a0 - 20 * S + (a1 - a0 + 40 * S) * k
        m = (xx < xcut) & (yy > b0 - 30 * S) & (yy < b1 + 30 * S)
        rev[m] = 1
        wet[m] = max(0.0, 1 - (prog - i) / 6.0)
    ink = SAM * gaussian_filter(rev, 1.5 * S)
    page_f = BASE * (1 - 0.92 * ink[..., None]) + (np.array([0.06, 0.05, 0.09]) * (1 - 0.0) ) * 0.92 * ink[..., None]
    page_f = page_f - (ink * wet)[..., None] * 0.04
    # camera: slow push (2%) + handheld drift, mild perspective, shallow DOF at the top/bottom edges
    k = ease((f - 1) / 84.0); s = 1.20 + 0.03 * k                          # framed on the rules + the torn line
    cw, ch = PW / 1.12 / s, PH / 1.12 / s; cx = PW / 2 + 20 * S + 6 * S * math.sin(f * 0.07); cy = (Y0 + LINE0 + 6 * LH) / 2 + 60 * S + 4 * S * math.sin(f * 0.05) + 30 * S * k
    sy = cy - ch / 2 + gy / H * ch; sx = cx - cw / 2 + gx / W * cw
    fr_ = np.stack([map_coordinates(page_f[..., c], [sy, sx], order=1) for c in range(3)], -1)
    blur = np.stack([gaussian_filter(fr_[..., c], 6) for c in range(3)], -1)
    dof = np.clip((np.abs(gy / H - 0.52) - 0.30) / 0.2, 0, 1)[..., None]
    img_f = fr_ * (1 - dof) + blur * dof
    # dusk window light from the left with a mullion shadow; a cool fill on the right
    lx = (gx / W) + 0.25 * (gy / H)
    light = 0.78 + 0.32 * np.clip(1 - lx, 0, 1)
    mull = 1 - 0.28 * np.exp(-((lx - 0.42 - 0.01 * math.sin(f * 0.03)) / 0.035) ** 2)
    img_f = img_f * (light * mull)[..., None] * np.array([1.05, 0.97, 0.86]) + np.clip(lx - 0.7, 0, 1)[..., None] * np.array([-0.03, -0.01, 0.03])
    mm = np.zeros((H, W), np.float32); fs = f - ((f - 1) % 2)
    for i in range(NM):
        x = (mote['x'][i] + mote['vx'][i] * fs + 0.004 * math.sin(fs * 0.12 + mote['ph'][i])) * W; y = (mote['y'][i] + mote['vy'][i] * fs) * H; r = mote['r'][i]
        x0, x1_, y0, y1_ = int(max(x - 3 * r, 0)), int(min(x + 3 * r, W)), int(max(y - 3 * r, 0)), int(min(y + 3 * r, H))
        if x1_ <= x0 or y1_ <= y0: continue
        mm[y0:y1_, x0:x1_] += np.exp(-((gx[y0:y1_, x0:x1_] - x) ** 2 + (gy[y0:y1_, x0:x1_] - y) ** 2) / (2 * (r * .6) ** 2))
    img_f = img_f + (mm * np.clip(1 - lx, 0, 1))[..., None] * np.array([1.0, 0.86, 0.62]) * 0.35
    fade = 1 - ease((f - 80) / 5.0)                                   # last frames sink into the black
    img_f = np.clip(img_f, 0, 1) * 1.03 + np.array([0.02, 0.012, 0.03])
    d = ((gx / W - .5) ** 2 * 1.4 + (gy / H - .5) ** 2); img_f = img_f * (1 - 0.36 * np.clip(d * 2.4, 0, 1))[..., None]
    n_ = gaussian_filter(np.random.default_rng(f).standard_normal((H, W)).astype(np.float32), 0.6)
    img_f = (img_f + n_[..., None] * 0.016) * fade
    Image.fromarray((np.clip(img_f, 0, 1) * 255 + .5).astype(np.uint8)).save(os.path.join(OUT, '%03d.png' % f))
    print('frame', f, flush=True)
