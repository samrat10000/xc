"""Concept frames for the zombie series plan. Pixel grid 180x320 -> x4 nearest. No dithering:
flat palette colours, stepped bands for gradients."""
import sys, numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, '/mnt/project-files/reels/pipeline')
from font import text_mask

GW, GH, UP = 180, 320, 4
OUT = '/tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/z/out/'
import os; os.makedirs(OUT, exist_ok=True)
R = np.random.default_rng(7)

INK = (14, 12, 20); PAPER = (241, 233, 216); C_BG = (20, 16, 34); TXT = (244, 236, 220)
YEL = (255, 214, 90); ORG = (255, 150, 60); RED = (255, 64, 40); CYAN = (70, 210, 230)
NIGHT = [(14, 12, 24), (22, 18, 40), (30, 26, 52), (42, 34, 68), (52, 44, 84), (70, 56, 104), (84, 70, 120)]
FIRE = [(120, 30, 34), (190, 56, 38), (255, 96, 44), (255, 150, 60), (255, 214, 90)]
SKIN = [(112, 150, 92), (88, 124, 78), (130, 150, 110), (100, 120, 120)]
SKIN_D = [(62, 92, 60), (52, 76, 52), (80, 96, 70), (60, 74, 80)]
SHIRT = [(120, 60, 64), (70, 84, 120), (110, 104, 80), (84, 70, 120), (150, 120, 90), (60, 62, 76)]
PANTS = [(42, 48, 64), (58, 62, 76), (60, 46, 40), (36, 40, 52)]

# palette for the car photo quantise (stylize PAL + extras)
CARPAL = np.array(np.load('/mnt/project-files/reels/pipeline/pal.npy')[:22].tolist() + [
    [255, 214, 90], [255, 150, 60], [255, 64, 40], [70, 210, 230], [244, 236, 220], [196, 120, 210],
    [176, 182, 196], [110, 116, 132], [58, 62, 76], [26, 30, 38], [84, 96, 80], [62, 70, 60]], np.float32)

def quant(rgb, pal):
    f = rgb.reshape(-1, 3).astype(np.float32)
    d = ((f[:, None] - pal[None]) ** 2).sum(2)
    return pal[d.argmin(1)].reshape(rgb.shape).astype(np.uint8)

class Canvas:
    def __init__(s, bg=NIGHT[0]):
        s.a = np.zeros((GH, GW, 3), np.uint8); s.a[:] = bg
    def rect(s, x, y, w, h, c):
        x0, y0, x1, y1 = max(0, int(x)), max(0, int(y)), min(GW, int(x + w)), min(GH, int(y + h))
        if x1 > x0 and y1 > y0: s.a[y0:y1, x0:x1] = c
    def bands(s, y0, y1, cols):
        n = len(cols); h = (y1 - y0) / n
        for i, c in enumerate(cols): s.rect(0, y0 + i * h, GW, h + 1, c)
    def poly(s, pts, c):
        from PIL import ImageDraw
        m = Image.new('L', (GW, GH), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
        mm = np.asarray(m) > 0; s.a[mm] = c
    def blend_poly(s, pts, c, k):
        from PIL import ImageDraw
        m = Image.new('L', (GW, GH), 0); ImageDraw.Draw(m).polygon(pts, fill=255)
        mm = np.asarray(m) > 0
        s.a[mm] = (s.a[mm] * (1 - k) + np.array(c) * k).astype(np.uint8)
    def sprite(s, sp, x, y):
        """sp: RGBA uint8 array; x,y = bottom-centre"""
        h, w = sp.shape[:2]; x0 = int(x - w / 2); y0 = int(y - h)
        for yy in range(h):
            Y = y0 + yy
            if not 0 <= Y < GH: continue
            row = sp[yy]; on = row[:, 3] > 0
            for xx in np.nonzero(on)[0]:
                X = x0 + xx
                if 0 <= X < GW: s.a[Y, X] = row[xx, :3]
    def text(s, t, x, y, c, scale=1):
        m = text_mask(t, scale); h, w = m.shape
        sub = s.a[y:y + h, x:x + w]; mm = m[:sub.shape[0], :sub.shape[1]]
        sub[mm] = c
    def tw(s, t, scale=1): return text_mask(t, scale).shape[1]
    def tag(s, t, x, y, fg=TXT, bg=C_BG, under=None, right=False):
        w = s.tw(t) + 4
        if right: x = x - w
        s.rect(x, y, w, 11, bg); s.text(t, x + 2, y + 2, fg)
        if under: s.rect(x, y + 11, w, 1, under)
        return w
    def hook(s, lines, y, scale=2):
        ms = [text_mask(l, scale) for l in lines]
        ms = [np.pad(m, ((0, 0), (0, 1))) | np.roll(np.pad(m, ((0, 0), (0, 1))), 1, 1) for m in ms]
        w = max(m.shape[1] for m in ms) + 8; h = sum(m.shape[0] for m in ms) + 8 + (len(ms) - 1) * 4
        x = (GW - w) // 2
        s.rect(x - 1, y - 1, w + 2, h + 2, TXT); s.rect(x, y, w, h, C_BG)
        s.rect(x + 1, y + h + 1, w + 1, 1, INK); s.rect(x + w + 1, y + 1, 1, h + 1, INK)
        yy = y + 4
        for m in ms:
            xx = x + (w - m.shape[1]) // 2
            mh = m.shape[0]
            for Y in range(mh):
                for X in np.nonzero(m[Y])[0]:
                    s.a[yy + Y + 1, xx + X + 1] = INK
            for Y in range(mh):
                c = YEL if Y < mh // 2 else ORG
                for X in np.nonzero(m[Y])[0]:
                    s.a[yy + Y, xx + X] = c
            yy += mh + 4
        return y + h
    def save(s, name):
        Image.fromarray(s.a).resize((GW * UP, GH * UP), Image.NEAREST).save(OUT + name, optimize=True)

def outline(sp):
    a = sp[..., 3] > 0
    p = np.pad(a, 1)
    ring = (p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:]) & ~a
    sp = np.pad(sp, ((1, 1), (1, 1), (0, 0)))
    ring = np.pad(ring, 1)
    sp[ring] = (*INK, 255)
    return sp

# ---------------------------------------------------------------- characters
def body(kind='walker', var=0, lit=1.0, pose=0):
    W, H = 20, 26
    sp = np.zeros((H, W, 4), np.uint8)
    def r(x, y, w, h, c):
        sp[max(0, y):y + h, max(0, x):x + w] = (*[min(255, int(v * lit)) for v in c], 255)
    sk, skd = SKIN[var % 4], SKIN_D[var % 4]
    sh, pa = SHIRT[var % 6], PANTS[var % 4]
    shd = tuple(int(v * .7) for v in sh)
    if kind == 'walker':
        r(6, 18, 3, 8 - pose, pa); r(11, 18 - 0, 3, 8, pa)          # legs
        r(6, 10, 8, 9, sh); r(6, 10, 2, 9, shd)                       # torso
        r(13, 11, 6, 2, sk); r(13, 14, 5, 2, skd)                    # arms out front
        r(7, 3, 6, 7, sk); r(7, 7, 6, 3, skd); r(11, 5, 1, 1, YEL)    # head, eye
        r(9, 8, 3, 1, (60, 20, 26))                                   # mouth
        r(8, 13, 2, 2, (120, 24, 30))                                 # stain
    elif kind == 'runner':
        r(4, 19, 3, 6, pa); r(12, 18, 3, 4, pa); r(14, 21, 3, 3, pa)
        r(7, 11, 8, 8, sh); r(7, 11, 2, 8, shd)
        r(14, 10, 6, 2, sk); r(2, 14, 5, 2, skd)
        r(11, 4, 6, 6, sk); r(11, 8, 6, 2, skd); r(15, 6, 1, 1, RED)
        r(14, 8, 3, 1, (60, 20, 26))
    elif kind == 'crawler':
        sp = np.zeros((12, 24, 4), np.uint8)
        def r(x, y, w, h, c): sp[y:y + h, x:x + w] = (*[min(255, int(v * lit)) for v in c], 255)
        r(2, 6, 14, 5, sh); r(2, 9, 14, 2, shd); r(15, 4, 6, 6, sk); r(15, 8, 6, 2, skd); r(19, 6, 1, 1, YEL)
        r(17, 10, 2, 2, skd); r(8, 10, 2, 2, skd); r(0, 9, 4, 2, pa)
        return outline(sp)
    elif kind == 'brute':
        sp = np.zeros((40, 30, 4), np.uint8)
        def r(x, y, w, h, c): sp[y:y + h, x:x + w] = (*[min(255, int(v * lit)) for v in c], 255)
        r(7, 28, 6, 12, pa); r(17, 28, 6, 12, pa)
        r(3, 11, 24, 18, (96, 80, 72)); r(3, 11, 6, 18, (66, 56, 52)); r(12, 16, 6, 6, (120, 24, 30))
        r(0, 13, 4, 14, sk); r(26, 13, 4, 14, sk); r(0, 25, 5, 4, skd); r(25, 25, 5, 4, skd)
        r(10, 2, 10, 10, sk); r(10, 8, 10, 4, skd); r(12, 5, 2, 1, RED); r(17, 5, 2, 1, RED)
        r(12, 9, 6, 2, (60, 20, 26))
        return outline(sp)
    elif kind == 'screamer':
        r(6, 18, 3, 8, pa); r(11, 18, 3, 8, pa)
        r(6, 10, 8, 9, sh); r(6, 10, 2, 9, shd)
        r(3, 2, 2, 9, sk); r(15, 2, 2, 9, sk)                           # arms up
        r(7, 3, 6, 7, sk); r(7, 7, 6, 3, skd); r(8, 5, 1, 1, YEL); r(11, 5, 1, 1, YEL)
        r(9, 7, 2, 3, (40, 10, 16))                                     # open mouth
    return outline(sp)

def human(cols, lit=1.0, gear=None):
    hood, skin, pants, hair = cols
    sp = np.zeros((26, 18, 4), np.uint8)
    def r(x, y, w, h, c): sp[y:y + h, x:x + w] = (*[min(255, int(v * lit)) for v in c], 255)
    r(5, 18, 3, 8, pants); r(10, 18, 3, 8, pants)
    r(4, 10, 10, 9, hood); r(4, 10, 2, 9, tuple(int(v * .7) for v in hood))
    r(2, 11, 2, 7, hood); r(14, 11, 2, 7, hood); r(2, 18, 2, 2, skin); r(14, 18, 2, 2, skin)
    r(5, 2, 8, 8, skin); r(5, 1, 8, 3, hair); r(5, 1, 2, 6, hair); r(8, 5, 1, 1, INK); r(11, 5, 1, 1, INK)
    if gear == 'bat': r(15, 6, 2, 13, (150, 110, 70))
    if gear == 'torch': r(15, 14, 3, 2, (200, 200, 210)); r(17, 13, 1, 4, YEL)
    if gear == 'radio': r(14, 13, 3, 5, (58, 62, 76)); r(16, 9, 1, 4, (58, 62, 76))
    if gear == 'pack': r(1, 10, 3, 8, (84, 96, 80))
    return outline(sp)

CAST = {
    'SAM':   ((230, 120, 50), (222, 176, 140), (42, 48, 64), (30, 22, 20)),
    'FRIEND 1': ((70, 150, 200), (190, 140, 100), (58, 62, 76), (20, 16, 18)),
    'FRIEND 2': ((150, 90, 190), (230, 190, 160), (60, 46, 40), (120, 60, 30)),
    'FRIEND 3': ((90, 170, 110), (160, 110, 80), (36, 40, 52), (40, 30, 30)),
}

# ---------------------------------------------------------------- car
CAR = np.asarray(Image.open('/tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/z/car.png').convert('RGBA'))
def car(width, flip=False, rot=0, bright=1.0):
    im = Image.fromarray(CAR)
    if flip: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    h = int(im.height * width / im.width)
    sm = np.asarray(im.resize((width, h), Image.BOX)).copy()
    rgb = sm[..., :3].astype(np.float32)
    rgb = 255 * (rgb / 255) ** 0.85 * bright
    rgb = np.clip((rgb - 128) * 1.15 + 132, 0, 255)
    q = quant(rgb, CARPAL)
    q = np.asarray(Image.fromarray(q).filter(ImageFilter.ModeFilter(5 if width > 100 else 3)))
    al = (sm[..., 3] > 110).astype(np.uint8) * 255
    return outline(np.dstack([q, al]))

def headlights(c, x0, y0, spread, length, k=.28, col=(230, 236, 214), dir=1):
    for i, kk in enumerate([k, k * .7]):
        sp = spread * (1 + i * .5)
        c.blend_poly([(x0, y0 - 2), (x0, y0 + 2), (x0 + dir * length, y0 + sp), (x0 + dir * length, y0 - sp * .6)], col, kk)

# ---------------------------------------------------------------- city bits
def skyline(c, base, seed=1, fires=(), tall=1.0, col=NIGHT[2], win=(255, 214, 90), wink=.18):
    r = np.random.default_rng(seed); x = -4
    while x < GW:
        w = int(r.integers(10, 26)); h = int(r.integers(30, 110) * tall)
        c.rect(x, base - h, w, h, col)
        c.rect(x, base - h, 1, h, tuple(min(255, v + 10) for v in col))
        for wy in range(base - h + 4, base - 4, 5):
            for wx in range(x + 2, x + w - 2, 4):
                if r.random() < wink: c.rect(wx, wy, 2, 2, win if r.random() > .15 else ORG)
        if r.random() < .3: c.rect(x + w // 2, base - h - 6, 1, 6, col)
        x += w + int(r.integers(0, 3))
    for fx in fires:
        # stepped glow (bands, no noise)
        for i, (rad, cc, k) in enumerate([(30, FIRE[0], .35), (20, FIRE[1], .45), (11, FIRE[2], .6)]):
            pts = [(fx + rad * 1.3 * np.cos(t), base - 40 + rad * .45 * np.sin(t)) for t in np.linspace(0, 2 * np.pi, 20)]
            c.blend_poly(pts, cc, k)
        rr_ = np.random.default_rng(fx)
        for j in range(7):   # flame tongues: chunky blocks
            fxx = fx + int(rr_.integers(-14, 14)); hh = int(rr_.integers(6, 16))
            c.rect(fxx, base - 44 - hh, 3, hh, FIRE[3]); c.rect(fxx, base - 44 - hh // 2, 3, hh // 2, FIRE[2])
        # smoke column: chunky blocks
        for j in range(6):
            sx = fx + j * 3 - 4; sy = base - 90 - j * 14
            c.rect(sx - 6 - j, sy - 10, 12 + j * 2, 12, NIGHT[3 if j % 2 else 4])

def moon(c, x, y, r_=9):
    for yy in range(-r_, r_ + 1):
        for xx in range(-r_, r_ + 1):
            if xx * xx + yy * yy <= r_ * r_:
                c.a[y + yy, x + xx] = (230, 226, 210) if (xx - 3) ** 2 + (yy + 2) ** 2 > 20 else (200, 196, 186)

def stars(c, n, ymax, seed=3):
    r = np.random.default_rng(seed)
    for _ in range(n): c.a[int(r.integers(0, ymax)), int(r.integers(0, GW))] = (130, 112, 160)

def road(c, horizon, vx=90, col=(30, 28, 44), edge=(52, 44, 84)):
    c.poly([(vx - 6, horizon), (vx + 6, horizon), (GW + 70, GH), (-70, GH)], col)
    # wet-road reflection stripes (stepped)
    c.blend_poly([(vx - 2, horizon), (vx + 2, horizon), (vx + 30, GH), (vx - 30, GH)], (52, 44, 84), .45)
    for i in range(8):
        t0 = (i / 8) ** 1.8; t1 = ((i + .45) / 8) ** 1.8
        y0 = horizon + (GH - horizon) * t0; y1 = horizon + (GH - horizon) * t1
        w0 = .5 + 3 * t0; w1 = .5 + 3 * t1
        c.poly([(vx - w0, y0), (vx + w0, y0), (vx + w1, y1), (vx - w1, y1)], (230, 214, 160))

# ================================================================ FRAME 1: cold open / thumbnail
def f1():
    c = Canvas()
    c.bands(0, 150, [NIGHT[0], NIGHT[1], NIGHT[2], NIGHT[3], (70, 40, 70), (110, 50, 56)])
    stars(c, 40, 90); moon(c, 140, 40)
    skyline(c, 172, seed=4, fires=(40, 128), tall=.8, col=NIGHT[3], wink=.08)
    skyline(c, 180, seed=9, tall=.6, col=NIGHT[2], wink=.12)
    c.rect(0, 180, GW, GH - 180, (22, 20, 34))
    road(c, 180)
    # abandoned car silhouettes
    for (x, y, w) in [(20, 214, 26), (150, 222, 30)]:
        c.rect(x, y - 8, w, 8, NIGHT[3]); c.rect(x + 5, y - 13, w - 12, 6, NIGHT[3]); c.rect(x + 2, y - 1, 5, 3, INK); c.rect(x + w - 7, y - 1, 5, 3, INK)
    # horde mid-ground, darker
    for i in range(26):
        x = int(R.integers(5, 175)); y = int(R.integers(196, 236))
        k = R.choice(['walker', 'walker', 'runner', 'screamer'])
        c.sprite(body(k, int(R.integers(0, 6)), lit=.45 + (y - 196) / 80), x, y)
    # car facing camera, headlights
    sp = car(118); headlights(c, 132, 268, 40, 60, k=.22); 
    c.sprite(sp, 92, 300)
    # foreground zombies lit by headlights
    for x, y, k, v in [(18, 318, 'walker', 1), (164, 312, 'runner', 2), (150, 330, 'walker', 3)]:
        c.sprite(body(k, v, lit=1.05), x, y)
    c.tag('DAY 1  03:12 AM', 6, 6, under=ORG)
    c.rect(c.tw('DAY 1  03:12 AM') + 14, 9, 3, 3, RED)
    c.tag('EP 1', 174, 6, fg=YEL, right=True, under=CYAN)
    c.hook(['THE CITY FELL', 'AT 3:12 AM'], 26)
    c.save('f1-cold-open.png')

# ================================================================ FRAME 2: the build (sketch -> pixel)
def f2():
    BW = GW * 3; bh = int(CAR.shape[0] * BW / CAR.shape[1])
    im = np.asarray(Image.fromarray(CAR).resize((BW, bh), Image.BILINEAR), np.float32)
    lum = im[..., :3].mean(2) / 255; al = im[..., 3] > 128
    e = (np.abs(np.diff(lum, axis=1, append=lum[:, -1:])) + np.abs(np.diff(lum, axis=0, append=lum[-1:]))) > .11
    er = np.asarray(Image.fromarray((al * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(3))) > 0
    e = (e & er) | (al & ~er)
    gh = int(CAR.shape[0] * GW / CAR.shape[1])
    ei = Image.fromarray((e * 255).astype(np.uint8)).resize((GW, gh), Image.BOX)
    ink = np.asarray(ei) > 75
    c = Canvas(bg=PAPER)
    # paper grain: 3 flat tones in blocks of 4 (not per-pixel)
    r = np.random.default_rng(2).random((GH // 4 + 1, GW // 4 + 1)).repeat(4, 0).repeat(4, 1)[:GH, :GW]
    c.a[r > .8] = (234, 225, 206)
    # construction lines
    for y in (150, 236): c.rect(0, y, GW, 1, (200, 190, 172))
    for x in (30, 150): c.rect(x, 110, 1, 150, (200, 190, 172))
    y0 = 140
    sub = c.a[y0:y0 + ink.shape[0]]; sub[ink[:sub.shape[0]]] = INK
    # bottom part flips to pixel art in 5x5 tiles along a diagonal
    px = Canvas(); px.bands(0, GH, NIGHT[:5])
    px.rect(0, 236, GW, GH, (30, 28, 44))
    sp = car(GW, bright=1.05); px.sprite(sp, GW // 2, y0 + sp.shape[0] - 1)
    B = 5; rr = np.random.default_rng(11).random((GH // B + 1, GW // B + 1)).repeat(B, 0).repeat(B, 1)[:GH, :GW]
    yy, xx = (np.mgrid[0:GH, 0:GW] // B) * B
    on = (xx / GW * .9 + yy / GH * .5 + rr * .08) > .95
    c.a[on] = px.a[on]
    # callouts
    def call(t, tx, ty, px_, py_):
        c.rect(min(tx, px_), py_, abs(px_ - tx) + 1, 1, INK) if False else None
        w = c.tw(t) + 4
        lx = tx + w // 2
        # leader line
        for yv in range(min(ty + 11, py_), max(ty + 11, py_)): c.a[yv, lx] = INK
        c.rect(lx - 1, py_ - 1, 3, 3, ORG)
        c.tag(t, tx, ty, fg=TXT, bg=C_BG, under=ORG)
    call('ROOF LED 15x3', 64, 108, 0, 150)
    call('RAM BAR', 124, 260, 0, 220)
    call('MUD TYRES', 8, 260, 0, 228)
    c.tag('BUILD LOG  NIGHT 1', 6, 6, under=ORG)
    c.tag('EP 2', 174, 6, fg=YEL, right=True, under=CYAN)
    c.hook(['I BUILT THIS', 'IN ONE NIGHT'], 26)
    c.tag('SKETCH', 6, 290, fg=INK, bg=PAPER); c.tag('-> PIXEL', 44, 290, fg=YEL)
    c.save('f2-the-build.png')

# ================================================================ FRAME 3: the smash (slow-mo)
def f3():
    c = Canvas()
    c.bands(0, 170, [NIGHT[0], NIGHT[1], NIGHT[2], NIGHT[3], NIGHT[4]])
    skyline(c, 170, seed=12, fires=(150,), tall=.9, col=NIGHT[2], wink=.1)
    c.rect(0, 170, GW, GH, (26, 24, 40))
    # street lamps
    for lx in (20, 170):
        c.rect(lx, 90, 2, 90, NIGHT[4]); c.rect(lx - 8, 88, 10, 3, NIGHT[5]); c.blend_poly([(lx - 8, 91), (lx + 2, 91), (lx + 14, 176), (lx - 22, 176)], (180, 170, 200), .12)
    # speed lines (horizontal streaks, flat)
    r = np.random.default_rng(5)
    for _ in range(30):
        y = int(r.integers(176, 300)); x = int(r.integers(-20, 120)); c.rect(x, y, int(r.integers(10, 40)), 1, (52, 44, 84))
    sp = car(130); headlights(c, 150, 250, 26, 40, k=.3)
    c.sprite(sp, 88, 282)
    # zombies flying off the ram bar
    for (x, y, ang, k, v) in [(150, 200, 40, 'walker', 1), (168, 150, -70, 'runner', 2), (128, 128, 120, 'walker', 4),
                              (100, 110, -20, 'screamer', 3), (160, 268, 15, 'walker', 0)]:
        s = body(k, v, lit=1.05); im = Image.fromarray(s).rotate(ang, Image.NEAREST, expand=True)
        c.sprite(np.asarray(im), x, y)
    # debris chunks
    for (x, y) in [(140, 180), (120, 150), (170, 120), (110, 170), (156, 236)]:
        c.rect(x, y, 3, 2, (120, 24, 30)); c.rect(x + 5, y - 6, 2, 2, (176, 182, 196))
    for i in range(14):
        x = int(r.integers(0, 60)); y = int(r.integers(230, 300))
        c.sprite(body('walker', i, lit=.55), x, y)
    c.tag('SLOW-MO 1/84', 6, 6, fg=ORG, under=ORG); c.rect(3, 9, 2, 3, RED)
    w = c.tag('x 47', 174, 6, fg=YEL, right=True, under=CYAN)
    c.text('KILLS', 174 - w - 32, 8, TXT)
    c.hook(['STRAIGHT', 'THROUGH THEM'], 26)
    c.save('f3-the-smash.png')

# ================================================================ FRAME 4: the horde (instancing)
def f4():
    c = Canvas()
    c.bands(0, 120, [NIGHT[0], NIGHT[1], NIGHT[2], (70, 40, 70)])
    skyline(c, 120, seed=21, fires=(60,), tall=.7, col=NIGHT[3], wink=.06)
    # high-angle street: two building walls converging
    c.poly([(0, 120), (60, 120), (0, 260)], NIGHT[2]); c.poly([(GW, 120), (120, 120), (GW, 260)], NIGHT[2])
    c.poly([(60, 120), (120, 120), (GW, 260), (GW, GH), (0, GH), (0, 260)], (30, 28, 44))
    for y in range(130, 250, 9):
        t = (y - 120) / 140
        for xx in (int(6 + (1 - t) * 40), int(GW - 10 - (1 - t) * 40)):
            c.rect(xx, y, 3, 3, YEL if (y // 9) % 3 else ORG)
    pts = []
    r = np.random.default_rng(14)
    for i in range(240):
        y = 125 + (r.random() ** 1.3) * 175
        t = (y - 120) / 200
        x = 90 + (r.random() - .5) * (40 + t * 220)
        pts.append((y, x))
    pts.sort()
    for i, (y, x) in enumerate(pts):
        t = (y - 120) / 200
        s = body(r.choice(['walker', 'walker', 'walker', 'runner', 'screamer']), int(r.integers(0, 12)), lit=.5 + t * .55)
        if t < .4:   # far: half size
            s = np.asarray(Image.fromarray(s).resize((s.shape[1] // 2, s.shape[0] // 2), Image.NEAREST))
        elif t < .7:
            s = np.asarray(Image.fromarray(s).resize((int(s.shape[1] * .7), int(s.shape[0] * .7)), Image.NEAREST))
        c.sprite(s, x, y)
    c.sprite(body('brute', 0, lit=.95), 132, 236)
    sp = car(100, flip=True); headlights(c, 82, 286, 30, -60, k=.2, dir=1)
    c.sprite(sp, 90, 322)
    c.tag('HORDE', 6, 6, under=ORG); c.tag('214', 40, 6, fg=RED, bg=C_BG)
    c.tag('FUEL LOW', 174, 6, fg=ORG, right=True, under=RED)
    c.hook(['THE WHOLE', 'STREET MOVED'], 26)
    c.save('f4-the-horde.png')

# ================================================================ FRAME 5: cliffhanger, bridge gone
def f5():
    c = Canvas()
    c.bands(0, 230, [NIGHT[0], NIGHT[1], NIGHT[1], NIGHT[2], NIGHT[3], (70, 40, 70)])
    stars(c, 60, 180, seed=8); moon(c, 40, 120, 12)
    skyline(c, 232, seed=31, tall=.45, col=NIGHT[2], wink=.1)
    # river: stepped bands + moon reflection blocks
    c.bands(232, GH, [(22, 26, 50), (18, 22, 42), (14, 18, 34), (12, 14, 28)])
    for i in range(10): c.rect(34 + (i % 3) * 3, 240 + i * 8, 14 - (i % 4) * 2, 2, (130, 112, 160))
    # broken bridge decks
    c.poly([(0, 196), (62, 196), (70, 204), (56, 212), (0, 212)], (58, 62, 76))
    c.rect(0, 196, 62, 2, (110, 116, 132))
    c.poly([(126, 200), (GW, 200), (GW, 216), (118, 216), (124, 208)], (58, 62, 76))
    c.rect(126, 200, GW - 126, 2, (110, 116, 132))
    for x in (10, 40, 150): c.rect(x, 212, 6, 120, (42, 48, 54)); c.rect(x, 212, 2, 120, (58, 62, 76))
    # hanging rebar + falling chunks
    for x in (58, 64, 122): c.rect(x, 210, 1, 10, (110, 116, 132))
    for (x, y) in [(70, 240), (110, 262), (88, 286)]: c.rect(x, y, 5, 3, (58, 62, 76))
    # car mid-air, nose up
    sp = car(96, rot=12); c.sprite(sp, 94, 196)
    c.tag('BRIDGE OUT', 6, 6, fg=RED, under=RED)
    c.tag('EP 7', 174, 6, fg=YEL, right=True, under=CYAN)
    y = c.hook(['THE BRIDGE', 'IS GONE'], 26)
    c.tag('TO BE CONTINUED', (GW - c.tw('TO BE CONTINUED') - 4) // 2, 300, fg=YEL, under=ORG)
    c.save('f5-bridge-gone.png')

# ================================================================ FRAME 6: rooftop rescue
def f6():
    c = Canvas()
    c.bands(0, GH, [NIGHT[0], NIGHT[1], NIGHT[2], NIGHT[2], NIGHT[3]])
    stars(c, 30, 100, seed=13)
    skyline(c, 220, seed=40, tall=.8, col=NIGHT[1], wink=.05)
    # hero building
    c.rect(40, 96, 100, 230, (52, 44, 84)); c.rect(40, 96, 4, 230, (70, 56, 104)); c.rect(36, 92, 108, 5, (84, 70, 120))
    r = np.random.default_rng(3)
    for wy in range(108, 300, 14):
        for wx in range(50, 134, 14):
            c.rect(wx, wy, 7, 8, (255, 214, 90) if r.random() < .2 else (30, 26, 52))
    # friend on rooftop with torch beam
    c.sprite(human(CAST['FRIEND 1'], gear='torch'), 110, 92)
    c.blend_poly([(118, 79), (120, 81), (176, 40), (170, 30)], (255, 236, 170), .35)
    # zombies climbing the wall
    for (x, y) in [(52, 290), (70, 270), (60, 250), (90, 300), (120, 286), (130, 262)]:
        s = np.asarray(Image.fromarray(body('runner', int(r.integers(0, 6)), lit=.75)).rotate(90 if x < 90 else -90, Image.NEAREST, expand=True))
        c.sprite(s, x, y)
    c.rect(0, 300, GW, 20, (26, 24, 40))
    for i in range(18): c.sprite(body('walker', i, lit=.6), int(r.integers(0, GW)), int(r.integers(306, 322)))
    # car with LED matrix message
    sp = car(84, flip=True); c.sprite(sp, 128, 318)
    c.tag('HOLD ON', 104, 262, fg=RED, bg=INK, under=RED)
    c.tag('FRIEND 1  FOUND', 6, 6, under=CYAN)
    c.tag('EP 9', 174, 6, fg=YEL, right=True, under=CYAN)
    c.hook(['3 DAYS ON', 'THE ROOF'], 26)
    c.save('f6-rooftop.png')

# ================================================================ cast sheet
def cast():
    W, H = 220, 74
    cs = np.zeros((H, W, 3), np.uint8); cs[:] = C_BG
    cv = Canvas.__new__(Canvas); cv.a = cs
    global GW, GH
    ow, oh = GW, GH; GW, GH = W, H
    x = 14
    for name, cols in CAST.items():
        g = {'SAM': 'bat', 'FRIEND 1': 'torch', 'FRIEND 2': 'radio', 'FRIEND 3': 'pack'}[name]
        cv.sprite(human(cols, gear=g), x, 34); x += 22
    xs = 106
    for k in ['walker', 'runner', 'crawler', 'screamer']:
        cv.sprite(body(k, 1), xs, 34); xs += 24
    cv.sprite(body('brute', 0), 206, 40)
    for i in range(12): cv.sprite(body('walker', i), 10 + i * 17, 72)
    GW, GH = ow, oh
    Image.fromarray(cs).resize((W * 4, H * 4), Image.NEAREST).save(OUT + 'cast.png', optimize=True)
    # individual sprites for the cast cards
    for name, cols in CAST.items():
        g = {'SAM': 'bat', 'FRIEND 1': 'torch', 'FRIEND 2': 'radio', 'FRIEND 3': 'pack'}[name]
        Image.fromarray(human(cols, gear=g)).resize((20 * 6, 28 * 6), Image.NEAREST).save(OUT + f"c-{name.replace(' ', '').lower()}.png")
    for k in ['walker', 'runner', 'crawler', 'screamer', 'brute']:
        s = body(k, 1); Image.fromarray(s).resize((s.shape[1] * 6, s.shape[0] * 6), Image.NEAREST).save(OUT + f"z-{k}.png")
    s = car(90); Image.fromarray(s).resize((s.shape[1] * 4, s.shape[0] * 4), Image.NEAREST).save(OUT + 'c-car.png')

for f in [f1, f2, f3, f4, f5, f6, cast]: f()
print('ok')
