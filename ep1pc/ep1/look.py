import os, sys, glob, subprocess, math, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
FPS, W, H = 24, 1080, 1920
SH = '/tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/ep1/out'

# ------------------------------------------------------------------ grade + lens
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = np.clip(1 - .38 * (((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2), .45, 1)[..., None]

def lens(img):
    a = np.asarray(img).astype(np.float32) / 255
    lum = a.max(2)
    # halation: blurred highlights bleed warm-red into the surround
    hi = Image.fromarray((np.clip((lum - .86) / .14, 0, 1) * 255).astype(np.uint8))
    hb = np.asarray(hi.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    a = a + hb[..., None] * np.array([.30, .10, .05]) * .35
    # anamorphic streak: very bright points smear horizontally in blue
    vh = Image.fromarray((np.clip((lum - .96) / .04, 0, 1) * 255).astype(np.uint8))
    st = np.asarray(vh.resize((W // 24, H // 2), Image.BOX).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    a = a + st[..., None] * np.array([.10, .22, .45]) * .5
    a = a * VIG
    lm = a.mean(2, keepdims=True)
    a = a + (1 - lm) * np.array([-.012, .004, .018]) + lm * np.array([.015, .004, -.012])
    a = np.clip(a, 0, 1) ** 1.04
    im = Image.fromarray((a * 255 + .5).astype(np.uint8))
    # chromatic edges: red slightly larger, blue slightly smaller than green
    r, g, b = im.split()
    def sc(ch, k):
        w2, h2 = int(W * k), int(H * k); c = ch.resize((w2, h2), Image.BILINEAR)
        x0, y0 = (w2 - W) // 2, (h2 - H) // 2
        return c.crop((x0, y0, x0 + W, y0 + H)) if k > 1 else ch
    r = sc(r, 1.0025)
    b2 = b.resize((int(W * .9975), int(H * .9975)), Image.BILINEAR); bb = Image.new('L', (W, H)); bb.paste(b2, ((W - b2.width) // 2, (H - b2.height) // 2)); b = ImageChops.lighter(bb, ImageChops.multiply(b, Image.new('L', (W, H), 0))) if False else bb
    return Image.merge('RGB', (r, g, b))

def src_frame(folder, i):
    d = os.path.join(SH, folder); p = os.path.join(d, f'f{i:04d}.png')
    if not os.path.exists(p):
        fs = sorted(glob.glob(os.path.join(d, 'f*.png')))
        if not fs: return None
        nums = [int(os.path.basename(f)[1:5]) for f in fs]; p = fs[int(np.argmin([abs(n - i) for n in nums]))]
    return Image.open(p).convert('RGB').resize((W, H), Image.LANCZOS)

