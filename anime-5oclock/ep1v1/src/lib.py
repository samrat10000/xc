"""5 O'CLOCK 2D pipeline: cel drawing in cairo (vector), numpy post (DOF blur, fisheye, bloom, grain).
Flat cel fills + one shadow tone + thin warm-dark line. No AI images anywhere."""
import math, random
import numpy as np, cairo
from scipy.ndimage import gaussian_filter, map_coordinates

W, H = 1080, 1920
LINE = (0.17, 0.11, 0.12)


def hexc(h, a=1.0):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


def surface(w=W, h=H):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    c = cairo.Context(s)
    c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.set_line_cap(cairo.LINE_CAP_ROUND)
    return s, c


def to_np(s):
    """premultiplied BGRA -> float RGBA (straight)"""
    s.flush()
    a = np.ndarray((s.get_height(), s.get_width(), 4), np.uint8, s.get_data()).astype(np.float32) / 255
    rgb = a[..., [2, 1, 0]]
    al = a[..., 3:4]
    rgb = np.where(al > 1e-4, rgb / np.maximum(al, 1e-4), 0)
    return np.concatenate([rgb, al], -1)


def over(dst, src):
    a = src[..., 3:4]
    out = dst.copy()
    out[..., :3] = src[..., :3] * a + dst[..., :3] * (1 - a)
    if dst.shape[-1] == 4:
        out[..., 3:4] = a + dst[..., 3:4] * (1 - a)
    return out


class Boil:
    """hand-drawn line boil: tiny per-drawing jitter that changes on twos"""
    def __init__(self, amp=0.6, seed=0):
        self.amp, self.seed = amp, seed
        self.k = 0

    def set_frame(self, f, step=2):
        self.k = f // step
        self.rng = random.Random(self.seed * 7919 + self.k)

    def j(self, x, y):
        if self.amp <= 0:
            return x, y
        # deterministic per position+drawing
        h = math.sin(x * 12.9898 + y * 78.233 + self.k * 3.7) * 43758.5453
        h2 = math.sin(x * 39.346 + y * 11.135 + self.k * 5.1) * 24634.6345
        return x + (h - math.floor(h) - .5) * 2 * self.amp, y + (h2 - math.floor(h2) - .5) * 2 * self.amp


BOIL = Boil(0.0)


def poly(c, pts, fill=None, line=LINE, lw=2.2, close=True, boil=True):
    if len(pts) < 2:
        return
    P = [BOIL.j(*p) if boil else p for p in pts]
    c.move_to(*P[0])
    for p in P[1:]:
        c.line_to(*p)
    if close:
        c.close_path()
    if fill is not None:
        c.set_source_rgba(*fill)
        if line is not None and lw > 0:
            c.fill_preserve()
        else:
            c.fill()
    if line is not None and lw > 0:
        c.set_source_rgba(*line) if len(line) == 4 else c.set_source_rgb(*line)
        c.set_line_width(lw)
        c.stroke()
    c.new_path()


def bez(c, segs, fill=None, line=LINE, lw=2.2, close=True):
    """segs: [(x,y)] start then tuples of 6 for curves or 2 for lines"""
    x, y = BOIL.j(*segs[0])
    c.move_to(x, y)
    for s in segs[1:]:
        if len(s) == 6:
            p = [BOIL.j(s[i], s[i + 1]) for i in (0, 2, 4)]
            c.curve_to(*p[0], *p[1], *p[2])
        else:
            c.line_to(*BOIL.j(*s))
    if close:
        c.close_path()
    if fill is not None:
        c.set_source_rgba(*fill)
        c.fill_preserve() if (line is not None and lw > 0) else c.fill()
    if line is not None and lw > 0:
        c.set_source_rgba(*(line if len(line) == 4 else line + (1,)))
        c.set_line_width(lw)
        c.stroke()
    c.new_path()


def line(c, a, b, col=LINE, lw=2.0):
    c.move_to(*BOIL.j(*a)); c.line_to(*BOIL.j(*b))
    c.set_source_rgba(*(col if len(col) == 4 else col + (1,)))
    c.set_line_width(lw); c.stroke()


def sag(c, a, b, droop, col=LINE, lw=1.6, n=24):
    """power line catenary-ish"""
    c.move_to(*a)
    for i in range(1, n + 1):
        t = i / n
        x = a[0] + (b[0] - a[0]) * t
        y = a[1] + (b[1] - a[1]) * t + droop * 4 * t * (1 - t)
        c.line_to(x, y)
    c.set_source_rgba(*(col if len(col) == 4 else col + (1,)))
    c.set_line_width(lw); c.stroke()


def circle(c, x, y, r, fill=None, line=LINE, lw=2.2):
    c.arc(x, y, r, 0, 2 * math.pi)
    if fill is not None:
        c.set_source_rgba(*fill)
        c.fill_preserve() if line is not None else c.fill()
    if line is not None:
        c.set_source_rgba(*(line if len(line) == 4 else line + (1,)))
        c.set_line_width(lw); c.stroke()
    c.new_path()


class Cam:
    def __init__(self, f=950, cx=540, cy=1150, h=1.45, x0=0.0):
        self.f, self.cx, self.cy, self.h, self.x0 = f, cx, cy, h, x0

    def p(self, X, Y, Z):
        Z = max(Z, 0.05)
        return (self.cx + self.f * (X - self.x0) / Z, self.cy - self.f * (Y - self.h) / Z)

    def ps(self, pts):
        return [self.p(*q) for q in pts]


# ---------------- post -----------------
def blur(img, s):
    if s <= 0:
        return img
    return np.stack([gaussian_filter(img[..., i], s) for i in range(img.shape[-1])], -1)


def bloom(rgb, thr=0.8, s=18, k=0.35):
    lum = rgb.max(-1, keepdims=True)
    hi = np.clip((lum - thr) / (1 - thr), 0, 1) * rgb
    return np.clip(rgb + blur(hi, s) * k, 0, 1)


def grain(rgb, f, amt=0.022, seed=1):
    r = np.random.default_rng(seed * 1000 + f)
    n = r.normal(0, 1, rgb.shape[:2]).astype(np.float32)
    n = gaussian_filter(n, 0.7) * 1.6
    lum = rgb.mean(-1, keepdims=True)
    w = 0.6 + 0.8 * (1 - lum)  # more in shadows like film
    return np.clip(rgb + n[..., None] * amt * w, 0, 1)


def vignette(rgb, k=0.28):
    yy, xx = np.mgrid[0:rgb.shape[0], 0:rgb.shape[1]].astype(np.float32)
    d = ((xx / rgb.shape[1] - .5) ** 2 * 1.6 + (yy / rgb.shape[0] - .5) ** 2)
    return rgb * (1 - k * np.clip(d * 2.2, 0, 1))[..., None]


def fisheye_into(dst, src, cx, cy, R, scx, scy, sR, flip=True, k=0.82):
    """paint src (convex-mirror warped) into circle (cx,cy,R) of dst"""
    y0, y1 = int(cy - R), int(cy + R) + 1
    x0, x1 = int(cx - R), int(cx + R) + 1
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx, dy = (xx - cx) / R, (yy - cy) / R
    r = np.sqrt(dx * dx + dy * dy)
    m = r <= 1.0
    rs = r / np.sqrt(np.maximum(1 - k * r * r, 0.05))
    sc = np.where(r > 1e-5, rs / np.maximum(r, 1e-5), 1)
    sx = scx + (-dx if flip else dx) * sc * sR
    sy = scy + dy * sc * sR
    out = dst
    for ch in range(3):
        v = map_coordinates(src[..., ch], [sy, sx], order=1, mode='nearest')
        reg = out[y0:y1, x0:x1, ch]
        # antialiased edge
        a = np.clip((1.0 - r) * R, 0, 1)
        reg[:] = reg * (1 - a) + v * a
    return out


def save(rgb, path):
    from PIL import Image
    Image.fromarray((np.clip(rgb[..., :3], 0, 1) * 255 + 0.5).astype(np.uint8)).save(path, quality=93)
