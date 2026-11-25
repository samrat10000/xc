"""001_mirror: locked shot. 16:59 golden lane, the curve mirror shows the same lane at night."""
import sys
from lane import *
from props import *
import lib

CX, CY, R, PX = 545, 720, 262, 905


def frame(f, fps=24, dur=3.0):
    t = f / fps
    lib.BOIL.amp = 0.45
    lib.BOIL.set_frame(f, 2)
    cam = Cam(f=950, cx=540, cy=1180, h=1.5, x0=-0.3)
    far, near = scene(DAY, t, cam)
    bg = np.zeros((H, W, 3), np.float32)
    img = over(bg, blur(far, 6.5))
    img = over(img, blur(near, 3.2))
    # warm low sun wash from the left (screen blend)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - 60) ** 2 + (yy - 1080) ** 2) / 1100
    warm = np.clip(1 - d, 0, 1)[..., None] ** 1.6 * np.array([1.0, .62, .32], np.float32) * .42
    img = 1 - (1 - img) * (1 - warm)
    # long cast shadow of the mirror pole across the road (sun low, left)
    s, c = surface()
    poly(c, [(PX - 16, 1925), (PX + 16, 1925), (W + 60, 1560), (W + 60, 1510)], fill=hexc('#4a3f55', .38), line=None, lw=0, boil=False)
    img = over(img, blur(to_np(s), 2.5))
    # night lane for the mirror: camera looks back along the street (other side)
    ncam = Cam(f=820, cx=540, cy=1080, h=1.9, x0=0.3)
    nfar, nnear = scene(NIGHT, t, ncam)
    nimg = over(np.zeros((H, W, 3), np.float32), nfar)
    nimg = over(nimg, nnear)
    nimg = bloom(nimg, .75, 10, .6)
    s, c = surface()
    mirror_fg(c, CX, CY, R, PX, t)
    fg = to_np(s)
    img = over(img, fg)
    img = fisheye_into(img, nimg, CX, CY, R, 560, 1060, 640, flip=True, k=.8)
    s, c = surface()
    glass_overlay(c, CX, CY, R, t)
    sec = 47 + int(t)
    stamp(c, f'KIRIYAMA  DAY 001  16:59:{sec:02d}')
    img = over(img, to_np(s))
    # two leaves drifting through, near the lens (soft focus) and one in focus plane
    s, c = surface()
    falling_leaves(c, t, [3], area=(-150, 700, 900, 1900), speed=1.3)
    img = over(img, blur(to_np(s), 5))
    s, c = surface()
    falling_leaves(c, t, [12], area=(100, 900, 300, 1700), speed=.8)
    img = over(img, to_np(s))
    img = bloom(img, .82, 22, .25)
    img = vignette(img, .22)
    img = grain(img, f, .018)
    return img


if __name__ == '__main__':
    f = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    save(frame(f), sys.argv[2] if len(sys.argv) > 2 else 'f001.jpg')
