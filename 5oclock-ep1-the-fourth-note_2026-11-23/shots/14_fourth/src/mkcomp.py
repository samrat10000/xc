"""make comp_s14.py (wide frames) from shot 11's comp: night insert in the glass + the ring crack (4 hand-keyed drawings), glints, shake"""
import os, sys
D = os.path.dirname(os.path.abspath(__file__)); t = open(os.path.join(sys.argv[1], 'comp_s11.py'), encoding='utf-8').read()
crack = '''
import json as _j
from PIL import ImageDraw as _D
_M14 = _j.load(open(os.path.join(sys.argv[1], 'meta.json')))
_rng = np.random.default_rng(14)
_RAD = [(_rng.uniform(0, 6.283), [_rng.uniform(-0.25, 0.25) for _ in range(6)]) for _ in range(13)]
_RING = [(i / 60.0 * 6.283, 0.52 + _rng.uniform(-0.05, 0.05)) for i in range(61)]
_BR = [(_rng.uniform(0, 6.283), _rng.uniform(0.55, 0.9), _rng.uniform(-0.8, 0.8)) for _ in range(16)]


def _stage(f):
    return 0 if f < 40 else 1 if f < 41 else 2 if f < 43 else 3 if f < 45 else 4      # hand-keyed drawings, held


def _crack(img, f):
    m = _M14[str(f)]; s = _stage(f)
    if s == 0: return img
    Hh, Ww = img.shape[:2]; cx, cy, r = m['mx'] * Ww, m['my'] * Hh, m['mr'] * Ww * 0.92
    L = Image.new('L', (Ww, Hh), 0); Ld = Image.new('L', (Ww, Hh), 0); d = _D.Draw(L); dd = _D.Draw(Ld)
    reach = {1: 0.18, 2: 0.55, 3: 1.0, 4: 1.0}[s]
    for a0, jit in _RAD:
        pts = [(cx, cy)]
        for i in range(6):
            rr = r * reach * (i + 1) / 6; a = a0 + jit[i] * 0.15
            pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
        d.line(pts, fill=255, width=3); dd.line([(x + 2, y + 2) for x, y in pts], fill=255, width=3)
    if s >= 3:
        pts = [(cx + math.cos(a) * r * q, cy + math.sin(a) * r * q) for a, q in _RING]
        d.line(pts, fill=255, width=3); dd.line([(x + 2, y + 2) for x, y in pts], fill=255, width=3)
    if s >= 4:
        for a, q, bend in _BR:
            x0, y0 = cx + math.cos(a) * r * q, cy + math.sin(a) * r * q
            d.line([(x0, y0), (x0 + math.cos(a + bend) * r * 0.22, y0 + math.sin(a + bend) * r * 0.22)], fill=230, width=2)
    lw = np.asarray(L).astype(np.float32)[..., None] / 255; ld = np.asarray(Ld).astype(np.float32)[..., None] / 255
    inside = ((np.mgrid[0:Hh, 0:Ww][1] - cx) ** 2 + (np.mgrid[0:Hh, 0:Ww][0] - cy) ** 2 < r * r)[..., None].astype(np.float32)
    img = img * (1 - 0.45 * ld * inside) + lw * inside * np.array([0.92, 0.96, 1.0]) * 0.95
    if 42 <= f <= 54:                                                      # glints flare on the fresh edges
        gk = math.exp(-(f - 44) ** 2 / 10.0)
        for a, q in _RING[::9]:
            gx, gy = cx + math.cos(a) * r * q, cy + math.sin(a) * r * q
            yy_, xx_ = np.mgrid[0:Hh, 0:Ww]
            star = np.exp(-((xx_ - gx) ** 2 + (yy_ - gy) ** 2) / 18.0) + np.exp(-((yy_ - gy) ** 2) / 2.0 - ((xx_ - gx) ** 2) / 900.0) * 0.5 + np.exp(-((xx_ - gx) ** 2) / 2.0 - ((yy_ - gy) ** 2) / 900.0) * 0.5
            img = img + star[..., None] * gk * 0.8
    if 40 <= f <= 46:                                                      # the shock: a few frames of shake
        img = np.roll(img, (int(6 * math.sin(f * 5.1)), int(5 * math.cos(f * 4.3))), axis=(0, 1))
    return img
'''
save = "    Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)).save(os.path.join(OUT, '%03d.png' % f))"
if save not in t: print('MISSING save')
t = t.replace(save, "    img = _crack(img, f)\n" + save)
t = t.replace("import paint_night11 as PN", "import paint_night11 as PN\nPN.CLOSE = 1.0" + crack)
open(os.path.join(D, 'comp_s14.py'), 'w', encoding='utf-8').write(t); print('ok')
