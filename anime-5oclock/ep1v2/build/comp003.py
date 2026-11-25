"""003_sam v2: drawn lane background (same as v1) + toon 3D Sam alpha frames rendered in Blender.
usage: python comp003.py <alpha_frames_dir> <out_dir>   (frames named 0001.png.. or any sorted *.png)"""
import sys, glob, os
import numpy as np
from PIL import Image
from lane import *
import lib

def bg(f):
    t = f / 24
    lib.BOIL.amp = 0.35; lib.BOIL.set_frame(f, 2)
    cam = Cam(f=700, cx=640, cy=1420, h=1.6, x0=0.6)
    far, near = scene(DAY, t, cam)
    img = over(np.zeros((H, W, 3), np.float32), blur(far, 14))
    img = over(img, blur(near, 16))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx + 100) ** 2 + (yy - 1000) ** 2) / 1300
    warm = np.clip(1 - d, 0, 1)[..., None] ** 1.5 * np.array([1.0, .66, .36], np.float32) * .55
    return 1 - (1 - img) * (1 - warm)

if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    frames = sorted(glob.glob(os.path.join(src, '*.png')))
    plate = None
    for f, p in enumerate(frames):
        if plate is None or f % 2 == 0:      # background drawn on twos too
            plate = bg(f)
        ch = np.asarray(Image.open(p).convert('RGBA'), np.float32) / 255
        if ch.shape[:2] != (H, W):
            ch = np.asarray(Image.open(p).convert('RGBA').resize((W, H), Image.LANCZOS), np.float32) / 255
        img = over(plate, ch)
        img = bloom(img, .8, 24, .3)
        img = vignette(img, .25)
        img = grain(img, f + 900, .016)
        save(img, os.path.join(out, f'{f + 1:04d}.png'))
    print('done', len(frames))
