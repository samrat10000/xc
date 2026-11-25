"""Composite Ep3 Shot 01: painted BG (parallax, DOF) + cel layer, light wrap, sun bloom,
dust motes on twos, tower blink, violet shadow grade, vignette, grain (4-worker parallel).
usage: python comp_s01.py <celdir> <bg.png> <meta.json> <outdir> [frames]
"""
import sys, os, glob, math, json
import multiprocessing as mp
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3.0 - 2.0 * t)


def _init_worker(celdir, bgp, meta_path, outdir):
    global CEL, OUT, W, H, SX, SY, BG_B, BG_W, BG_H, RED, MOTE, XX, YY, BEAM
    CEL, OUT = celdir, outdir
    W, H = 1080, 1920
    meta = json.load(open(meta_path, encoding='utf-8'))
    SX, SY = float(meta["SUN_SCREEN"][0]), float(meta["SUN_SCREEN"][1])
    bg0 = np.asarray(Image.open(bgp)).astype(np.float32) / 255.0
    RED = np.load(bgp.replace('.png', '_red.npy'))
    BG_H, BG_W = bg0.shape[:2]
    BG_B = np.stack([gaussian_filter(bg0[..., c], 2.2) for c in range(3)], -1)
    rng = np.random.default_rng(301)
    nm = 75
    MOTE = dict(
        x=rng.uniform(0.15, 0.95, nm),
        y=rng.uniform(0.18, 0.88, nm),
        r=rng.uniform(1.2, 4.2, nm),
        vx=rng.uniform(-0.0005, 0.0004, nm),
        vy=rng.uniform(-0.0012, -0.0002, nm),
        ph=rng.uniform(0, 6.28, nm),
    )
    YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
    dsun = np.sqrt(((XX / W - SX) * W / H) ** 2 + (YY / H - SY) ** 2)
    BEAM = np.exp(-dsun / 0.32)


def _process_one(args):
    f, celpath = args
    k = ease((f - 1) / 71.0)
    s = 1.0 + 0.012 * k
    cw, ch = int(W * 1.1 / s), int(H * 1.1 / s)
    cx = BG_W // 2 + int(5 * math.sin(f * 0.05))
    cy = BG_H // 2 + int(3 * math.sin(f * 0.04))
    crop = BG_B[cy - ch // 2:cy + ch // 2, cx - cw // 2:cx + cw // 2]
    bg = np.asarray(Image.fromarray((np.clip(crop, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)).astype(np.float32) / 255.0

    # Radio tower red light blink
    if (f // 12) % 2 == 0:
        rx = int((RED[0] - (cx - cw // 2)) * W / cw)
        ry = int((RED[1] - (cy - ch // 2)) * H / ch)
        if 0 <= rx < W and 0 <= ry < H:
            g = np.exp(-((XX - rx) ** 2 + (YY - ry) ** 2) / (2 * 3.0 ** 2))
            bg = bg + g[..., None] * np.array([1.0, 0.15, 0.10], np.float32) * 1.25

    cel = np.asarray(Image.open(celpath).convert('RGBA').resize((W, H), Image.LANCZOS)).astype(np.float32) / 255.0
    a = cel[..., 3:4]; rgb = cel[..., :3]

    # Light wrap: sky bleeds softly into cel edges
    wrapsrc = np.stack([gaussian_filter(bg[..., c] * (1.0 - a[..., 0]), 10.0) for c in range(3)], -1)
    inner = np.clip(1.0 - gaussian_filter(a[..., 0], 7.0), 0.0, 1.0)[..., None] * a
    img = rgb * a + bg * (1.0 - a)
    img = img + wrapsrc * inner * (0.45 * BEAM[..., None] + 0.08)

    # Dust motes in sun beam (on twos)
    fs = f - ((f - 1) % 2)
    m = np.zeros((H, W), np.float32)
    for i in range(len(MOTE['x'])):
        x = (MOTE['x'][i] + MOTE['vx'][i] * fs + 0.004 * math.sin(fs * 0.12 + MOTE['ph'][i])) * W
        y = (MOTE['y'][i] + MOTE['vy'][i] * fs) * H
        r = MOTE['r'][i]
        x0, x1 = int(max(x - 3 * r, 0)), int(min(x + 3 * r, W))
        y0, y1 = int(max(y - 3 * r, 0)), int(min(y + 3 * r, H))
        if x1 <= x0 or y1 <= y0:
            continue
        tw = 0.6 + 0.4 * math.sin(fs * 0.4 + MOTE['ph'][i] * 3.0)
        m[y0:y1, x0:x1] += np.exp(-((XX[y0:y1, x0:x1] - x) ** 2 + (YY[y0:y1, x0:x1] - y) ** 2) / (2 * (r * 0.6) ** 2)) * tw
    img = img + (m * BEAM)[..., None] * np.array([1.0, 0.85, 0.60], np.float32) * 0.55

    # Bloom + warm beam haze
    hi = np.clip(img.max(-1, keepdims=True) - 0.74, 0.0, 1.0) / 0.26 * img
    bl = np.stack([gaussian_filter(hi[..., c], 28.0) for c in range(3)], -1)
    img = img + bl * 0.56 + BEAM[..., None] * np.array([0.13, 0.055, 0.0], np.float32) * 0.95

    # Grade: slight violet shadow lift
    img = np.clip(img, 0.0, 1.0)
    img = img * 1.06 + np.array([0.035, 0.02, 0.05], np.float32)

    # Vignette + film grain
    d = ((XX / W - 0.5) ** 2 * 1.4 + (YY / H - 0.5) ** 2)
    img = img * (1.0 - 0.25 * np.clip(d * 2.4, 0.0, 1.0))[..., None]
    n = gaussian_filter(np.random.default_rng(f).standard_normal((H, W)).astype(np.float32), 0.6)
    img = img + n[..., None] * 0.018 * (0.7 + 0.6 * (1.0 - img.mean(-1, keepdims=True)))
    outp = os.path.join(OUT, f'{f:03d}.png')
    Image.fromarray((np.clip(img, 0.0, 1.0) * 255 + 0.5).astype(np.uint8)).save(outp)
    return f


def main():
    celdir, bgp, meta_path, outdir = sys.argv[1:5]
    os.makedirs(outdir, exist_ok=True)
    want = None if len(sys.argv) < 6 else set(int(x) for x in sys.argv[5].split(','))
    cels = sorted(glob.glob(os.path.join(celdir, 'cel_*.png')))
    tasks = []
    for c in cels:
        f = int(os.path.basename(c)[4:7])
        if want and f not in want:
            continue
        tasks.append((f, c))

    n_workers = min(4, max(1, len(tasks)))
    if n_workers == 1:
        _init_worker(celdir, bgp, meta_path, outdir)
        for t in tasks:
            print('comp', _process_one(t), flush=True)
    else:
        with mp.Pool(n_workers, initializer=_init_worker, initargs=(celdir, bgp, meta_path, outdir)) as pool:
            for f in pool.imap_unordered(_process_one, tasks):
                print('comp', f, flush=True)


if __name__ == '__main__':
    main()
