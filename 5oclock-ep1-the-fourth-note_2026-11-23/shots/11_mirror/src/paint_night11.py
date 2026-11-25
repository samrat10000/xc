"""Shots 11/12: the NIGHT street in the curve mirror, now with the whole town standing in the road facing the viewer, and the sky over
the mountains cracked like glass with something huge behind it. Built on paint_night.py (shot 02): same road, walls, poles, lamp.
draw(f, leaf_u=None, flicker=1.0) -> float RGB (1200x1200). Env CLOSE (0..1): how close the crowd has come (shot 12 uses ~0.7)."""
import math, os, numpy as np, cairo
from scipy.ndimage import gaussian_filter
import paint_night as P0
from paint_night import N, INK, BASE, VP, figure, xx, yy, LX, LY

CLOSE = float(os.environ.get('CLOSE', '0'))
warm = np.array([1.0, .86, .55])
rng = np.random.default_rng(11)
CROWD = []
for i in range(30):
    d = rng.uniform(0.05, 0.85)                       # depth along the road (0 = near the mirror bottom)
    side = rng.uniform(-1, 1)
    kind = rng.choice(['adult', 'adult', 'adult', 'kid', 'old'])
    CROWD.append(dict(d=d, side=side, kind=kind, eyes=rng.random() < 0.45, lean=rng.uniform(-0.03, 0.03)))


def old_figure(c, x, y, h):
    """hunched old woman: shorter, bent forward, a bun"""
    c.save(); c.translate(x, y); c.rotate(0.12); figure(c, 0, 0, h); c.restore()
    hd = h / 7.5; c.set_source_rgb(*INK); c.arc(x + hd * 0.25, y - h - hd * 0.05, hd * 0.28, 0, 7); c.fill()


def sky_crack(img, f):
    """fractures across the sky over the mountains; a huge crown of horns dimly behind them"""
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, N, N); c = cairo.Context(s)
    cx, cy = N * 0.56, N * 0.27
    c.set_source_rgba(0.01, 0.01, 0.03, 1.0)
    c.arc(cx, cy + N * 0.10, N * 0.20, math.pi, 2 * math.pi); c.fill()           # the dome of the head behind the sky
    rh = np.random.default_rng(3)
    for k in range(26):                                                                  # horns of the crown, mouths out
        a = math.pi + math.pi * (k + 0.5) / 26 + rh.uniform(-0.05, 0.05); r0 = N * 0.18; L = N * rh.uniform(0.05, 0.11)
        x0, y0 = cx + math.cos(a) * r0, cy + N * 0.10 + math.sin(a) * r0
        x1, y1 = x0 + math.cos(a) * L, y0 + math.sin(a) * L
        c.set_line_width(N * 0.006); c.move_to(x0, y0); c.line_to(x1, y1); c.stroke()
        c.arc(x1, y1, N * rh.uniform(0.012, 0.022), 0, 7); c.fill()
    sil = (np.asarray(s.get_data()).reshape(N, N, 4)[..., 3] / 255.0).astype(np.float32)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, N, N); c = cairo.Context(s)
    c.set_source_rgba(0.8, 0.9, 1.0, 1.0)
    rc = np.random.default_rng(5)
    for k in range(18):
        x, y = cx + rc.uniform(-30, 30), cy + rc.uniform(-20, 20)
        ang = rc.uniform(0, 2 * math.pi); c.set_line_width(rc.uniform(0.8, 2.0)); c.move_to(x, y)
        for j in range(rc.integers(4, 9)):
            ang += rc.uniform(-0.25, 0.25); L = rc.uniform(20, 70)
            x += math.cos(ang) * L; y += math.sin(ang) * L * 0.8
            if y > N * 0.48: break
            c.line_to(x, y)
        c.stroke()
    cr = (np.asarray(s.get_data()).reshape(N, N, 4)[..., 3] / 255.0).astype(np.float32)
    sky = (yy < N * 0.50).astype(np.float32)
    near = gaussian_filter(cr, 14) * 6
    img = img * (1 - (sil * 0.55 * sky)[..., None]) + (sil * sky * np.clip(near, 0, 1) * 0.0)[..., None]
    img = img + (cr * sky)[..., None] * np.array([0.75, 0.85, 1.0]) * 0.9 + (gaussian_filter(cr, 4) * sky)[..., None] * np.array([0.3, 0.4, 0.8]) * 0.5
    return img


# v2: the crowd as real 3D people (sprites rendered from the cast by build_crowd_sprites.py). Same placement as the painted
# version (depth d, side, CLOSE); each figure = dark body with the 3D form faintly visible, warm lamp rim, pale eyes.
SPRD = os.environ.get('NIGHT_SPRITES', os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'crowd_sprites')))
SPR = {}
if os.path.exists(os.path.join(SPRD, 'sprites.json')):
    import json
    from PIL import Image as _I
    _m = json.load(open(os.path.join(SPRD, 'sprites.json')))
    for fn, mt in _m.items():
        im = np.asarray(_I.open(os.path.join(SPRD, fn)).convert('RGBA')).astype(np.float32) / 255
        ys, xs = np.nonzero(im[..., 3] > 0.05)
        if len(ys) == 0: continue
        SPR[fn] = dict(im=im[ys.min():ys.max() + 1, xs.min():xs.max() + 1], off=(xs.min(), ys.min()), **mt)
    _r = np.random.default_rng(12)
    POOL = {'adult': [k for k in SPR if k.startswith(('shopkeeper', 'mom'))], 'kid': [k for k in SPR if k.startswith('kid')],
            'old': [k for k in SPR if k.startswith('grandma')]}
    for p in CROWD: p['spr'] = POOL[p['kind']][_r.integers(len(POOL[p['kind']]))]


def crowd3d(img, close, flicker):
    from PIL import Image as _I
    vx, vy = VP
    for p in sorted(CROWD, key=lambda q: -q['d']):
        d = max(0.0, p['d'] - 0.75 * close); t = (1 - d) ** 1.7
        y = vy + (N * 1.02 - vy) * t; x = vx + p['side'] * N * 0.55 * t
        h = (N * 0.30) * t + 10
        if p['kind'] == 'kid': h *= 0.70
        if p['kind'] == 'old': h *= 0.86
        sp = SPR[p['spr']]; sh, sw = sp['im'].shape[:2]
        k = h / max(1.0, sp['feet'][1] - sp['top'][1])
        nw, nh = max(2, int(sw * k)), max(2, int(sh * k))
        a = np.asarray(_I.fromarray((sp['im'] * 255).astype(np.uint8)).resize((nw, nh), _I.LANCZOS)).astype(np.float32) / 255
        fx = x - (sp['feet'][0] - sp['off'][0]) * k; fy = y - (sp['feet'][1] - sp['off'][1]) * k
        x0, y0 = int(round(fx)), int(round(fy)); x1, y1 = min(N, x0 + nw), min(N, y0 + nh)
        if x1 <= max(0, x0) or y1 <= max(0, y0): continue
        a = a[max(0, -y0):y1 - y0, max(0, -x0):x1 - x0]; X0, Y0 = max(0, x0), max(0, y0)
        al = a[..., 3:4]; lum = a[..., :3].mean(-1, keepdims=True)
        body = np.array(INK) * 0.9 + lum * np.array([0.10, 0.10, 0.16]) * (0.6 + 0.4 * t)          # dark, the form still reads
        edge = np.clip(al - np.roll(np.roll(al, 2, 1), 2, 0), 0, 1)                                 # lamp rim (upper-right edges)
        reg = img[Y0:y1, X0:x1]
        img[Y0:y1, X0:x1] = reg * (1 - al) + body * al + edge * warm * 0.35 * flicker * (0.4 + 0.6 * t)
        if p['eyes']:
            for ex, ey in sp['eyes']:
                cx_, cy_ = fx + (ex - sp['off'][0]) * k, fy + (ey - sp['off'][1]) * k; r = max(0.8, 0.010 * h)
                img = img + np.exp(-((xx - cx_) ** 2 + (yy - cy_) ** 2) / (2 * r * r))[..., None] * np.array([0.75, 0.80, 0.85]) * 0.9
    img = gaussian_filter(img, (0.8, 0.8, 0))
    return np.clip(img, 0, 1)


def draw(f, leaf_u=None, flicker=1.0):
    img = BASE.copy()
    img = sky_crack(img, f)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, N, N); c = cairo.Context(s)
    c.set_source_rgb(*INK); c.set_line_width(7); c.move_to(N * .33, N * .95); c.line_to(N * .335, LY); c.line_to(LX, LY - 8); c.stroke()
    la = (np.asarray(s.get_data()).reshape(N, N, 4)[..., 3:4] / 255.0)
    img = img * (1 - la) + np.array(INK) * la
    cone = np.clip(1 - np.abs(xx - (LX + (yy - LY) * .25)) / (30 + (yy - LY) * .55), 0, 1) * (yy > LY) * np.exp(-(yy - LY) / (N * .6))
    pool = np.exp(-(((xx - N * .50) / (N * .26)) ** 2 + ((yy - N * .76) / (N * .09)) ** 2))
    img = img + (cone[..., None] * .16 + pool[..., None] * .45) * warm * flicker
    if (f // 12) % 2 == 0:
        img = img + np.exp(-((xx - N * .71) ** 2 + (yy - N * .455) ** 2) / (2 * 2.5 ** 2))[..., None] * np.array([1, .15, .1]) * 1.5
    # the town, standing in the road, every face toward the viewer (far -> near)
    vx, vy = VP
    if SPR:
        return crowd3d(img, CLOSE, flicker)
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, N, N); c = cairo.Context(s)
    eyes = []
    for p in sorted(CROWD, key=lambda q: -q['d']):
        d = max(0.0, p['d'] - 0.75 * CLOSE)
        t = (1 - d) ** 1.7
        y = vy + (N * 1.02 - vy) * t
        x = vx + p['side'] * N * 0.55 * t
        h = (N * 0.30) * t + 10
        if p['kind'] == 'kid': h *= 0.70
        if p['kind'] == 'old': old_figure(c, x, y, h * 0.82)
        else:
            c.save(); c.translate(x, y); c.rotate(p['lean']); figure(c, 0, 0, h); c.restore()
        if p['eyes']: eyes.append((x, y - h + h / 7.5 * 0.55, h))
    a = (np.asarray(s.get_data()).reshape(N, N, 4)[..., 3] / 255.0).astype(np.float32)
    rim = np.clip(a - np.roll(np.roll(a, 3, 1), 3, 0), 0, 1) * .5
    img = img * (1 - a[..., None]) + np.array(INK) * a[..., None] + rim[..., None] * warm * .45 * flicker
    for (ex, ey, h) in eyes:                                   # the faces are turned to him: two pale points, no pupils
        hd = h / 7.5; r = max(0.8, hd * 0.06)
        for sx in (-1, 1):
            img = img + np.exp(-((xx - ex - sx * hd * 0.17) ** 2 + (yy - ey) ** 2) / (2 * r * r))[..., None] * np.array([0.75, 0.80, 0.85]) * 0.9
    img = gaussian_filter(img, (1.0, 1.0, 0))
    return np.clip(img, 0, 1)


if __name__ == '__main__':
    from PIL import Image
    Image.fromarray((draw(1) * 255).astype(np.uint8)).save('night11_test.png')
