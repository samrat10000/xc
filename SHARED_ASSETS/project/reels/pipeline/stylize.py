"""Stylise colour+normal renders: sketch-ink look and chunky pixel look."""
import numpy as np
from PIL import Image, ImageFilter

OW, OH = 1080, 1920
PX = 4                              # pixel size at output res -> 270x480 grid
GW, GH = OW // PX, OH // PX

# limited night palette (hand-picked, no dithering)
PAL = np.array([
    [14, 12, 24], [30, 26, 52], [52, 44, 84], [84, 70, 120], [130, 112, 160],
    [196, 180, 214], [244, 236, 220], [255, 64, 40], [255, 150, 60], [255, 214, 90],
    [70, 210, 230], [26, 30, 38], [58, 62, 76], [110, 116, 132], [176, 182, 196],
], np.float32)
import os as _os
_pp = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "pal.npy")
if _os.path.exists(_pp): PAL = np.load(_pp).astype(np.float32)
INK = np.array([14, 12, 20], np.uint8)
PAPER = np.array([241, 233, 216], np.float32)

def load(p, size):
    return np.asarray(Image.open(p).convert("RGB").resize(size, Image.BILINEAR), np.float32)

def edge_map(nrm, col, size):
    n = nrm / 255.0
    gx = np.abs(np.diff(n, axis=1, append=n[:, -1:])).sum(2)
    gy = np.abs(np.diff(n, axis=0, append=n[-1:])).sum(2)
    e = np.maximum(gx, gy) > 0.22
    lum = col.mean(2) / 255.0
    lx = np.abs(np.diff(lum, axis=1, append=lum[:, -1:])); ly = np.abs(np.diff(lum, axis=0, append=lum[-1:]))
    e |= np.maximum(lx, ly) > 0.18
    return e

def _noise(h, w, seed, scale):
    r = np.random.default_rng(seed)
    small = r.random((max(2, h // scale), max(2, w // scale))).astype(np.float32)
    return np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255.0

def sketch(col_p, nrm_p, frame, reveal=1.0, colour=0.0):
    """reveal: 0..1 how much ink is drawn; colour: 0..1 marker fill."""
    S = (OW, OH)
    col = load(col_p, S); nrm = load(nrm_p, S)
    boil = frame // 2                       # lines re-jitter at 12fps like hand-drawn
    e = edge_map(nrm, col, S)
    # jitter: displace edge image by smooth noise
    dx = (_noise(OH, OW, boil * 7 + 1, 90) - .5) * 6
    dy = (_noise(OH, OW, boil * 7 + 2, 90) - .5) * 6
    yy, xx = np.mgrid[0:OH, 0:OW]
    sx = np.clip(xx + dx, 0, OW - 1).astype(int); sy = np.clip(yy + dy, 0, OH - 1).astype(int)
    e = e[sy, sx]
    ei = Image.fromarray((e * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(1.1))
    ink = np.asarray(ei, np.float32) / 255.0
    # pressure variation along strokes
    ink *= 0.75 + 0.35 * _noise(OH, OW, boil + 99, 40)
    # reveal: diagonal sweep from top-left with ragged front
    front = (xx / OW * .45 + yy / OH * .55) + (_noise(OH, OW, 5, 60) - .5) * .12
    m = np.clip((reveal * 1.25 - front) * 12, 0, 1)
    ink = np.clip(ink * m, 0, 1)
    paper = PAPER * (0.94 + 0.06 * _noise(OH, OW, 3, 3))[..., None]
    out = paper.copy()
    if colour > 0:
        # marker fill: flat-ish quantised colour, slightly offset from lines (hand-coloured)
        fill = quant(tame_ground(col, nrm)).astype(np.float32)
        fill = np.roll(fill, (4, -3), (0, 1))
        cm = np.clip((colour * 1.3 - front) * 6, 0, 1)[..., None] * .85
        out = out * (1 - cm) + (fill * .9 + paper * .1) * cm
    out = out * (1 - ink[..., None]) + INK * ink[..., None]
    return out.clip(0, 255).astype(np.uint8)

def tame_ground(col, nrm):
    """wet-road glare reads as a big flat blob in pixel art: pull the road (normal ~ +Z) down."""
    g = (np.abs(nrm[..., 0] - 188) < 10) & (np.abs(nrm[..., 1] - 188) < 10) & (nrm[..., 2] > 245)   # +Z normal (sRGB-encoded)
    out = col.copy(); out[g] = out[g] * .38 + np.array([22, 20, 36], np.float32) * .62
    return out

def quant(rgb):
    flat = rgb.reshape(-1, 3)
    d = ((flat[:, None, :] - PAL[None]) ** 2).sum(2)
    return PAL[d.argmin(1)].reshape(rgb.shape).astype(np.uint8)

def pixel(col_p, nrm_p, frame):
    G = (GW, GH)
    col = np.asarray(Image.open(col_p).convert("RGB").resize(G, Image.BOX), np.float32)
    col = tame_ground(col, np.asarray(Image.open(nrm_p).convert("RGB").resize(G, Image.NEAREST), np.float32))
    # small contrast push before quantising
    col = 255 * (col / 255) ** 0.88                     # lift the night shadows a little before quantising
    col = np.clip((col - 128) * 1.12 + 128 + 4, 0, 255)
    q = quant(col)
    q = np.asarray(Image.fromarray(q).filter(ImageFilter.ModeFilter(3)))
    q = q.copy()
    big_n = load(nrm_p, (GW * 2, GH * 2)); big_c = load(col_p, (GW * 2, GH * 2))
    e = edge_map(big_n, big_c, None)
    e = np.asarray(Image.fromarray((e * 255).astype(np.uint8)).resize(G, Image.BOX)) > 70
    q[e] = INK
    return np.asarray(Image.fromarray(q).resize((OW, OH), Image.NEAREST))

def pixel_wipe(sk, px, t, seed=11):
    """blocks flip from sketch to pixel in a staggered wave (centre-out)."""
    B = 5                                   # wipe in 5x5-pixel tiles, not single pixels
    r = np.random.default_rng(seed).random((GH // B + 1, GW // B + 1)).repeat(B, 0).repeat(B, 1)[:GH, :GW]
    yy, xx = (np.mgrid[0:GH, 0:GW] // B) * B
    d = np.hypot((xx - GW / 2) / GW, (yy - GH * .55) / GH) * 1.6
    on = (d + r * .18) < t * 1.9
    m = np.asarray(Image.fromarray((on * 255).astype(np.uint8)).resize((OW, OH), Image.NEAREST))[..., None] > 0
    return np.where(m, px, sk)
