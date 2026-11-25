"""003_sam v3: hand-drawn 2D Sam (sam2d.py) over the blurred Kiriyama lane. 84 f, on twos.
usage: python shot003.py <out_dir> [frame frame ...]"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../ep1v2/build'))
import numpy as np, cairo
from scipy.ndimage import gaussian_filter
import lane, lib
from lib import blur, over, bloom, vignette, grain, save, to_np, Cam
import sam2d

W, H = 1080, 1920


def plate():
    cam = Cam(f=820, cx=760, cy=1330, h=1.6, x0=.5)
    far, near = lane.scene(lane.DAY, 0.0, cam)
    img = over(np.zeros((H, W, 3), np.float32), blur(far, 8)); img = over(img, blur(near, 11))
    # dusk regrade: pull saturation, cool the mids, keep a pale sky
    l = img.mean(-1, keepdims=True)
    img = l + (img - l) * .62
    img = img * np.array([.90, .92, .93], np.float32) * .90 + np.array([.01, .02, .025], np.float32)
    rng = np.random.default_rng(4)          # broad brush texture
    n = gaussian_filter(rng.normal(0, 1, (H, W)), (10, 46)); n /= n.std()
    n2 = gaussian_filter(rng.normal(0, 1, (H, W)), (60, 24)); n2 /= n2.std()
    return np.clip(img * (1 + .007 * n + .012 * n2)[..., None], 0, 1).astype(np.float32)


def ez(t, a, b):
    x = max(0., min(1., (t - a) / (b - a))); return x * x * (3 - 2 * x)


def pose(t):
    up = ez(t, .80, 1.20); sl = ez(t, 1.92, 2.34)
    gaze = 0 if t < .58 else (.5 if t < .66 else 1)
    lid = .46 - .14 * gaze - .06 * up
    fr = round(t * 24)
    for f0 in (10, 56):                                   # blinks: half, closed, closed, half
        lid = {f0: .72, f0 + 2: 1.0, f0 + 4: .8}.get(fr, lid)
    sway = 5 * math.sin(2 * math.pi * t / 2.6) + (16 * math.exp(-(t - 1.2) * 3.2) * math.sin((t - 1.2) * 9) if t > 1.2 else 0) \
        + (-12 * math.exp(-(t - 2.3) * 4) * math.sin((t - 2.3) * 10) if t > 2.3 else 0)
    hand = None
    if t >= 1.16:
        k = min(1, (t - 1.16) / .42); k = 1 - (1 - k) ** 2.6
        hand = (190 * (1 - k), 640 * (1 - k), 14 * (1 - k))
    mouth = {60: .25, 62: .5, 64: .7, 66: .6, 68: .55, 70: .4, 72: .25}.get(fr, .12 if fr > 72 else 0)
    return dict(lid=lid, gx=-10 - 12 * gaze, gy=9 - 13 * gaze, brow=1 + 8 * up, mouth=mouth, sway=sway,
                breath=4 * math.sin(2 * math.pi * t / 2.4), tilt=1.8 - 3.6 * up + 1.6 * sl, slide=sl, hand=hand)


def frame(f, PL):
    t = (f // 2 * 2) / 24
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    sam2d.draw_sam(c, pose(t))
    ch = to_np(s)
    push = 1 + .012 * f / 84
    img = over(PL, ch)
    # cool key grade + lower-third falloff, like a painted cel under one light
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    img = img * (1 - .34 * np.clip(yy - .45, 0, 1) ** 1.2)
    img = vignette(img, .22)
    img = bloom(img, .78, 22, .18)
    img = grain(img, f + 900, .010)
    if push > 1:
        from PIL import Image
        im = Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8))
        dx, dy = W * (1 - 1 / push) / 2, H * (1 - 1 / push) / 2.6
        im = im.transform((W, H), Image.AFFINE, (1 / push, 0, dx, 0, 1 / push, dy), Image.BICUBIC)
        return np.asarray(im, np.float32) / 255
    return img


if __name__ == '__main__':
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    fs = [int(x) for x in sys.argv[2:]] or range(84)
    PL = plate()
    for f in fs:
        save(frame(f, PL), os.path.join(out, f'{f + 1:04d}.png'))
