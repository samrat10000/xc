"""shot 14 f1-36: the ECU inside the glass. Night street (paint_night11, crowd close, blurred: shallow focus) behind the ecu render of the
reflection's mouth; convex-glass barrel warp, cold sheen, glass dust, grain. usage: python ecu_s14.py <celdir> <outdir>"""
import os, sys, math, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates
CEL, OUT = sys.argv[1:3]; os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import paint_night11 as PN
PN.CLOSE = 1.0
W, H = 1080, 1920
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
u, v = (xx / W - 0.5) * 2, (yy / H - 0.5) * 2
rr = u * u * 0.5 + v * v * 0.5
k = 0.10                                                     # barrel: it is a convex mirror
sx = (u * (1 - k * rr) * 0.5 + 0.5) * W; sy = (v * (1 - k * rr) * 0.5 + 0.5) * H
dust = gaussian_filter((np.random.default_rng(4).random((H, W)) > 0.9993).astype(np.float32), 1.2) * 3
for f in range(1, 37):
    p = os.path.join(CEL, 'ecu_%03d.png' % f)
    if not os.path.exists(p): continue
    night = PN.draw(f)
    bg = np.asarray(Image.fromarray((night * 255).astype(np.uint8)).resize((int(H * 1.0), H), Image.BICUBIC)).astype(np.float32) / 255
    x0 = (bg.shape[1] - W) // 2; bg = bg[:, x0:x0 + W]
    bg = np.stack([gaussian_filter(bg[..., c], 9) for c in range(3)], -1)
    e = np.asarray(Image.open(p).convert('RGBA').resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    img = bg * (1 - e[..., 3:4]) + e[..., :3] * e[..., 3:4]
    img = np.stack([map_coordinates(img[..., c], [sy, sx], order=3, mode='nearest') for c in range(3)], -1)
    sheen = np.clip(1 - np.abs((xx / W) * 0.7 + (yy / H) * 0.3 - 0.35) / 0.08, 0, 1) * 0.05
    img = img * np.array([0.92, 0.96, 1.06]) + sheen[..., None] + dust[..., None] * np.array([0.5, 0.55, 0.6]) * 0.25
    img = img * (1 - 0.45 * np.clip(rr * 1.3 - 0.2, 0, 1))[..., None]
    g = gaussian_filter(np.random.default_rng(f).standard_normal((H, W)).astype(np.float32), 0.6)
    img = img + g[..., None] * 0.012
    sh = np.stack([gaussian_filter(img[..., c], 1.4) for c in range(3)], -1); img = img + 0.6 * (img - sh)   # v4: unsharp - crisp lips
    Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8)).save(os.path.join(OUT, '%03d.png' % f))
    print('ecu', f, flush=True)
