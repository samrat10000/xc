"""Composite shot 07 (comp_s01 v4 recipe + visible sound): painted sunset BG (push-in, DOF) + cel layer, light wrap, bloom, dust motes,
grade, vignette, grain. Each chime note sends a ring outward from the horn through the painted sky: the clouds are displaced along the
ring and lit slightly (you SEE the sound). Notes at f6, f30, f54; the fourth (f78) never comes.
usage: python comp_s07.py <celdir> <bg.png> <outdir> [frames]"""
import sys, os, glob, math, json, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates

CEL, BGP, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)
W, H = 1080, 1920
META = json.load(open(os.path.join(CEL, 'meta.json')))
NOTES = [6, 30, 54]
bg0 = np.asarray(Image.open(BGP).convert('RGB')).astype(np.float32) / 255
bgH, bgW = bg0.shape[:2]
bgb = np.stack([gaussian_filter(bg0[..., c], 2.2) for c in range(3)], -1)
rng = np.random.default_rng(3); NM = 60
mote = dict(x=rng.uniform(0.0, 1.0, NM), y=rng.uniform(0.3, 1.0, NM), r=rng.uniform(1.2, 4.0, NM), vx=rng.uniform(-0.0005, 0.0004, NM), vy=rng.uniform(-0.0012, -0.0002, NM), ph=rng.uniform(0, 6.3, NM))
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def ease(t):
    t = min(max(t, 0), 1); return t * t * (3 - 2 * t)


def frame(f, celpath):
    m = META[str(f)]; SX, SY = m['sx'], m['sy']; HX, HY = m['hx'] * W, m['hy'] * H
    k = ease((f - 1) / 107.0); s = 1.0 + 0.012 * k
    cw, ch = int(W * 1.1 / s), int(H * 1.1 / s); cx, cy = bgW // 2 + int(6 * math.sin(f * 0.05)), bgH // 2
    crop = bgb[cy - ch // 2:cy + ch // 2, cx - cw // 2:cx + cw // 2]
    # visible sound: rings expanding from the horn mouth, displacing the sky radially
    gy = yy * (crop.shape[0] / H); gx = xx * (crop.shape[1] / W)
    dx = xx - HX; dy = yy - HY; dist = np.sqrt(dx * dx + dy * dy) + 1e-3
    disp = np.zeros((H, W), np.float32); lift = np.zeros((H, W), np.float32)
    for n in NOTES:
        t = f - n
        if t < 0: continue
        R = 60 + t * 62.0; fade = math.exp(-t / 22.0)
        band = np.exp(-((dist - R) / (26 + t * 0.8)) ** 2)
        disp += band * 34 * fade * np.sin((dist - R) / 18.0)
        lift += band * fade
    gy2 = gy + (dy / dist) * disp * (crop.shape[0] / H); gx2 = gx + (dx / dist) * disp * (crop.shape[1] / W)
    bg = np.stack([map_coordinates(crop[..., c], [gy2, gx2], order=1, mode='nearest') for c in range(3)], -1)
    edge = np.zeros((H, W), np.float32)
    for n in NOTES:
        tt = f - n
        if tt >= 0: edge += np.exp(-((dist - (60 + tt * 62.0)) / 3.5) ** 2) * math.exp(-tt / 18.0)
    sky = (1 - np.clip((yy / H - 0.75) * 4, 0, 1))[..., None]
    bg = bg + (lift[..., None] * np.array([0.22, 0.15, 0.10]) + edge[..., None] * np.array([0.55, 0.45, 0.32])) * sky
    cel = np.asarray(Image.open(celpath).convert('RGBA').resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    a = cel[..., 3:4]; rgb = cel[..., :3]
    dsun = np.sqrt(((xx / W - SX) * W / H) ** 2 + (yy / H - SY) ** 2); beam = np.exp(-dsun / 0.32)
    wrapsrc = np.stack([gaussian_filter(bg[..., c] * (1 - a[..., 0]), 10) for c in range(3)], -1)
    inner = np.clip(1 - gaussian_filter(a[..., 0], 7), 0, 1)[..., None] * a
    img = rgb * a + bg * (1 - a)
    img = img + wrapsrc * inner * (0.45 * beam[..., None] + 0.08)
    fs = f - ((f - 1) % 2); mm = np.zeros((H, W), np.float32)
    for i in range(NM):
        x = (mote['x'][i] + mote['vx'][i] * fs + 0.004 * math.sin(fs * 0.12 + mote['ph'][i])) * W; y = (mote['y'][i] + mote['vy'][i] * fs) * H; r = mote['r'][i]
        x0, x1, y0, y1 = int(max(x - 3 * r, 0)), int(min(x + 3 * r, W)), int(max(y - 3 * r, 0)), int(min(y + 3 * r, H))
        if x1 <= x0 or y1 <= y0: continue
        mm[y0:y1, x0:x1] += np.exp(-((xx[y0:y1, x0:x1] - x) ** 2 + (yy[y0:y1, x0:x1] - y) ** 2) / (2 * (r * .6) ** 2)) * (0.6 + 0.4 * math.sin(fs * 0.4 + mote['ph'][i] * 3))
    img = img + (mm * beam)[..., None] * np.array([1.0, 0.85, 0.6]) * 0.55
    hi = np.clip(img.max(-1, keepdims=True) - 0.82, 0, 1) / 0.18 * img
    img = img + np.stack([gaussian_filter(hi[..., c], 28) for c in range(3)], -1) * 0.28 + beam[..., None] * np.array([0.10, 0.04, 0.0]) * 0.6
    img = np.clip(img, 0, 1) * 1.04 + np.array([0.035, 0.02, 0.05])
    d = ((xx / W - .5) ** 2 * 1.4 + (yy / H - .5) ** 2)
    img = img * (1 - 0.30 * np.clip(d * 2.4, 0, 1))[..., None]
    n_ = gaussian_filter(np.random.default_rng(f).standard_normal((H, W)).astype(np.float32), 0.6)
    img = img + n_[..., None] * 0.018 * (0.7 + 0.6 * (1 - img.mean(-1, keepdims=True)))
    Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)).save(os.path.join(OUT, '%03d.png' % f))


cels = sorted(glob.glob(os.path.join(CEL, 'cel_*.png')))
want = None if len(sys.argv) < 5 else set(int(x) for x in sys.argv[4].split(','))
for c in cels:
    f = int(os.path.basename(c)[4:7])
    if want and f not in want: continue
    frame(f, c); print('comp', f, flush=True)
