"""003_sam: close-up. Sam hears something wrong under his music, eyes flick up, head lifts, he pushes one
headphone cup off his ear. Background: the same lane, heavy lens blur."""
import sys
from lane import *
from sam import draw_sam
import lib

FPS = 24


def ease(u):
    u = min(1, max(0, u))
    return u * u * (3 - 2 * u)


def on_twos(t):
    return math.floor(t * 12) / 12


def pose_at(t):
    tq = on_twos(t)
    p = {}
    # eye dart (snap over 2 drawings) at 0.55 s
    g0, g1 = (.1, .35), (-.55, -.85)
    u = 0 if tq < .55 else (.6 if tq < .62 else 1)
    p['gaze'] = (g0[0] + (g1[0] - g0[0]) * u, g0[1] + (g1[1] - g0[1]) * u)
    p['up'] = ease((tq - .85) / .6)
    p['brow'] = ease((tq - .7) / .4)
    p['hand'] = ease((tq - 1.3) / .45)
    p['cup'] = ease((tq - 1.8) / .5)
    # blink: drawings at 2.45 .. 2.66
    b = 0
    for (a, v) in ((2.45, .5), (2.53, 1), (2.62, .55)):
        if tq >= a:
            b = v
    if tq >= 2.7:
        b = 0
    if tq < .45 and .2 <= tq < .3:
        b = .55
    p['blink'] = b
    p['mouth'] = .35 if tq > 2.85 else 0
    p['breath'] = math.sin(tq * 2 * math.pi / 3.2)
    p['sway'] = math.sin(tq * 2.1) * 3 + (6 * math.exp(-(tq - 1.6) * 2) * math.sin(tq * 9) if tq > 1.6 else 0)
    return p


def frame(f):
    t = f / FPS
    lib.BOIL.amp = 0.35; lib.BOIL.set_frame(f, 2)
    cam = Cam(f=700, cx=640, cy=1420, h=1.6, x0=0.6)
    far, near = scene(DAY, t, cam)
    img = over(np.zeros((H, W, 3), np.float32), blur(far, 14))
    img = over(img, blur(near, 16))
    # warm low sun from the left
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx + 100) ** 2 + (yy - 1000) ** 2) / 1300
    warm = np.clip(1 - d, 0, 1)[..., None] ** 1.5 * np.array([1.0, .66, .36], np.float32) * .55
    img = 1 - (1 - img) * (1 - warm)
    s, c = surface()
    c.translate(-215, -330); c.scale(1.38, 1.38)
    draw_sam(c, pose_at(t))
    ch = to_np(s)
    # soft gradient light over the character (GW-style overlay): warm on the left, cool shade on the right
    g = np.clip((xx - 300) / 700, 0, 1)[..., None]
    tint = (1 - g) * np.array([1.06, 1.0, .94], np.float32) + g * np.array([.86, .86, .96], np.float32)
    ch[..., :3] = np.clip(ch[..., :3] * tint, 0, 1)
    img = over(img, ch)
    img = bloom(img, .8, 24, .3)
    img = vignette(img, .25)
    img = grain(img, f + 900, .016)
    return img


if __name__ == '__main__':
    f = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    save(frame(f), sys.argv[2] if len(sys.argv) > 2 else 'f003.jpg')
