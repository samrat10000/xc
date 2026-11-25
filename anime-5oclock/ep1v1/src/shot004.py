"""004_street: wide down the lane. Everyone stopped dead, heads tilted up at the town speaker. Only the
wind, a rolling ball and the camera's slow creep move. Real perspective (camera dolly re-projects the world)."""
import sys
from lane import *
import lib

LNC = hexc('#2b1d22')
FPS = 24


def S(cam, X, Y, Z):
    return cam.p(X, Y, Z)


def shape(c, cam, X, Z, pts, fill, lw=2.2, line=LNC, yoff=0.0):
    """pts in metres (x right, y up) relative to the figure's foot point, drawn at depth Z"""
    q = [cam.p(X + x, y + yoff, Z) for (x, y) in pts]
    poly(c, q, fill=fill, line=line, lw=lw * 7 / Z)


def ell_m(cx, cy, rx, ry, n=18, a0=0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n)]


def cast_shadow(c, cam, X, Z, hgt, w):
    # sun low on the left: shadow falls to the right and a bit toward camera
    q = [cam.p(X - w, 0, Z), cam.p(X + w, 0, Z), cam.p(X + w + hgt * 1.6, 0, Z - hgt * .5), cam.p(X - w + hgt * 1.6, 0, Z - hgt * .5 - .1)]
    poly(c, q, fill=hexc('#4b3f58', .42), line=None, lw=0)


def grandma(c, cam, X, Z, t):
    w = math.sin(t * 5.1) * .012 if int(t * 12) % 2 == 0 else math.sin(t * 5.1 + .5) * .012
    cast_shadow(c, cam, X, Z, 1.4, .25)
    # trolley (in front of her, to the left)
    shape(c, cam, X, Z, [(-.62, .08), (-.3, .08), (-.28, .62), (-.6, .64)], hexc('#7b4f5e'))
    for k in range(3):
        y = .2 + k * .14
        shape(c, cam, X, Z, [(-.6, y), (-.29, y), (-.29, y + .02), (-.6, y + .02)], hexc('#5a3946'), lw=0)
    shape(c, cam, X, Z, [(-.33, .6), (-.3, .62), (-.12, .92), (-.15, .93)], hexc('#8a8590'))
    for wx in (-.58, -.34):
        q = cam.p(X + wx, .06, Z); circle(c, q[0], q[1], .06 * cam.f / Z, fill=hexc('#2a2830'), line=LNC, lw=1.5)
    # legs + skirt
    shape(c, cam, X, Z, [(-.1, 0), (-.03, 0), (-.03, .45), (-.1, .45)], hexc('#d8c3b3'))
    shape(c, cam, X, Z, [(.03, 0), (.1, 0), (.1, .45), (.03, .45)], hexc('#d8c3b3'))
    shape(c, cam, X, Z, [(-.12, 0), (-.01, 0), (-.01, .05), (-.12, .05)], hexc('#3a3440'))
    shape(c, cam, X, Z, [(.01, 0), (.12, 0), (.12, .05), (.01, .05)], hexc('#3a3440'))
    shape(c, cam, X, Z, [(-.2 + w, .42), (.21 + w, .42), (.16, .78), (-.16, .78)], hexc('#5d5b6e'))
    # cardigan, slightly hunched
    shape(c, cam, X, Z, [(-.2, .74), (.2, .74), (.22, 1.12), (.1, 1.25), (-.12, 1.25), (-.24, 1.1)], hexc('#8c7a96'))
    shape(c, cam, X, Z, [(.05, .74), (.2, .74), (.22, 1.12), (.1, 1.25), (.04, 1.2)], hexc('#6d5e78'), lw=0)
    # arm reaching to the trolley handle (stopped mid-push)
    shape(c, cam, X, Z, [(-.2, 1.12), (-.12, 1.08), (-.13, .92), (-.2, .9)], hexc('#8c7a96'))
    # head tilted UP (back of head, bun)
    shape(c, cam, X, Z, ell_m(.0, 1.33, .1, .11), hexc('#bcb7c0'))
    shape(c, cam, X, Z, ell_m(.0, 1.43, .055, .045), hexc('#a9a3ae'))
    shape(c, cam, X, Z, [(-.02, 1.3), (.06, 1.24), (.09, 1.3), (.03, 1.36)], hexc('#d9bfae'), lw=0)  # ear sliver lit


def boy(c, cam, X, Z, t):
    cast_shadow(c, cam, X, Z, 1.3, .2)
    for (a, b) in ((-.1, -.02), (.02, .1)):
        shape(c, cam, X, Z, [(a, 0), (b, 0), (b, .55), (a, .55)], hexc('#1f2230'))
        shape(c, cam, X, Z, [(a - .02, 0), (b + .02, 0), (b + .02, .06), (a - .02, .06)], hexc('#f1ede6'))
    shape(c, cam, X, Z, [(-.17, .52), (.17, .52), (.19, 1.0), (.1, 1.08), (-.1, 1.08), (-.19, 1.0)], hexc('#22263a'))
    # school backpack (black), yellow safety cover strip (real detail)
    shape(c, cam, X, Z, [(-.16, .62), (.16, .62), (.17, .98), (-.17, .98)], hexc('#14151d'))
    shape(c, cam, X, Z, [(-.16, .86), (.16, .86), (.17, .98), (-.17, .98)], hexc('#e6c23a'), lw=1.4)
    # arms hanging, one hand open (dropped the ball)
    shape(c, cam, X, Z, [(-.25, .98), (-.18, 1.0), (-.18, .62), (-.24, .6)], hexc('#22263a'))
    shape(c, cam, X, Z, [(.18, 1.0), (.25, .98), (.24, .6), (.18, .62)], hexc('#22263a'))
    shape(c, cam, X, Z, ell_m(-.215, .56, .035, .045), hexc('#ecc9b3'))
    shape(c, cam, X, Z, ell_m(.215, .56, .035, .045), hexc('#ecc9b3'))
    # head up, school cap
    shape(c, cam, X, Z, ell_m(0, 1.18, .11, .12), hexc('#1b1a22'))
    shape(c, cam, X, Z, ell_m(0, 1.25, .12, .07, 12, math.pi, 2 * math.pi), hexc('#e6c23a'))


def salaryman(c, cam, X, Z, t):
    flap = math.sin(math.floor(t * 12) / 12 * 6) * .02
    cast_shadow(c, cam, X, Z, 1.75, .22)
    for (a, b) in ((-.13, -.03), (.03, .13)):
        shape(c, cam, X, Z, [(a, 0), (b, 0), (b, .85), (a, .85)], hexc('#2d3140'))
        shape(c, cam, X, Z, [(a - .02, 0), (b + .02, 0), (b + .02, .05), (a - .02, .05)], hexc('#151418'))
    shape(c, cam, X, Z, [(-.23, .8 + flap), (.23, .8 - flap), (.24, 1.45), (.14, 1.52), (-.14, 1.52), (-.24, 1.45)], hexc('#353a4c'))
    shape(c, cam, X, Z, [(.06, .82), (.23, .8 - flap), (.24, 1.45), (.14, 1.52), (.06, 1.5)], hexc('#272b3a'), lw=0)
    # briefcase hanging from the right hand, still
    shape(c, cam, X, Z, [(.22, .45), (.5, .45), (.5, .72), (.22, .72)], hexc('#3b2b26'))
    shape(c, cam, X, Z, [(.3, .72), (.42, .72), (.42, .78), (.3, .78)], hexc('#2b201c'))
    shape(c, cam, X, Z, [(.23, 1.45), (.3, 1.42), (.38, .8), (.31, .8)], hexc('#353a4c'))
    shape(c, cam, X, Z, [(-.3, 1.42), (-.23, 1.45), (-.26, .82), (-.32, .82)], hexc('#353a4c'))
    # head tilted up: short black hair, collar
    shape(c, cam, X, Z, [(-.08, 1.5), (.08, 1.5), (.07, 1.56), (-.07, 1.56)], hexc('#f0eee8'))
    shape(c, cam, X, Z, ell_m(0, 1.66, .105, .115), hexc('#1d1c24'))
    shape(c, cam, X, Z, [(-.1, 1.6), (-.06, 1.57), (-.05, 1.66), (-.1, 1.68)], hexc('#e2bca8'), lw=0)


def girl_bike(c, cam, X, Z, t):
    cast_shadow(c, cam, X, Z, 1.55, .5)
    # bicycle side-on (mamachari), stopped
    P = lambda x, y: cam.p(X + x, y, Z)
    for wx in (-.55, .55):
        q = P(wx, .33); r = .33 * cam.f / Z
        circle(c, q[0], q[1], r, fill=None, line=LNC, lw=2.2 * 7 / Z)
        circle(c, q[0], q[1], r * .15, fill=hexc('#77727e'), line=LNC, lw=1.2)
    for (a, b) in (((-.55, .33), (0, .33)), ((0, .33), (.4, .75)), ((-.55, .33), (-.2, .8)), ((-.2, .8), (.4, .75)), ((.55, .33), (.45, .9)), ((0, .33), (-.2, .8))):
        line(c, P(*a), P(*b), hexc('#c9c1b8'), 3.2 * 7 / Z)
    shape(c, cam, X, Z, [(.38, .95), (.62, .98), (.62, 1.02), (.38, 1.0)], hexc('#4a4650'))
    shape(c, cam, X, Z, [(.42, .78), (.72, .78), (.7, .98), (.44, .98)], hexc('#9a9397'))  # front basket
    # girl standing astride, one foot down; uniform skirt navy, white shirt, cardigan
    shape(c, cam, X, Z, [(-.12, 0), (-.05, 0), (-.08, .55), (-.14, .55)], hexc('#e8cbb7'))
    shape(c, cam, X, Z, [(-.24, .5), (.06, .5), (.03, .8), (-.2, .8)], hexc('#2e3550'))
    shape(c, cam, X, Z, [(-.2, .78), (.04, .78), (.06, 1.24), (-.22, 1.24)], hexc('#d9d0bf'))
    sway = math.sin(math.floor(t * 12) / 12 * 4) * .03
    # long hair hanging down her back, moving a little in the wind (head tilted up)
    shape(c, cam, X, Z, [(-.18, 1.3), (-.02, 1.3), (.0 + sway, .95), (-.2 + sway, .95)], hexc('#2a2530'))
    shape(c, cam, X, Z, ell_m(-.1, 1.4, .1, .11), hexc('#2a2530'))


def speaker_pole(c, cam, X, Z):
    P = cam.p
    lw = 2.6 * 7 / Z
    poly(c, [P(X - .16, 0, Z), P(X + .16, 0, Z), P(X + .11, 10.5, Z), P(X - .11, 10.5, Z)], fill=hexc('#b7aa9b'), line=LNC, lw=lw)
    cx, cy = P(X, 10.0, Z)
    s = cam.f / Z
    for (sx, sy) in ((-1, -1), (1, -1), (-1, .4), (1, .4)):
        a = (cx + sx * .1 * s, cy + sy * .08 * s)
        b = (cx + sx * .75 * s, cy + sy * .3 * s - .1 * s)
        q = [(a[0], a[1] - .05 * s), (b[0], b[1] - .22 * s), (b[0], b[1] + .22 * s), (a[0], a[1] + .05 * s)]
        poly(c, q, fill=hexc('#d3ccc6'), line=LNC, lw=lw)
        c.save(); c.translate(*b); c.scale(.3, 1); c.arc(0, 0, .22 * s, 0, 6.283); c.restore()
        c.set_source_rgba(*hexc('#3a3346')); c.fill()
    circle(c, cx, cy, .1 * s, fill=hexc('#8d8792'), line=LNC, lw=lw)


def ball(c, cam, t):
    # dropped by the boy, rolling slowly toward camera down the slight slope
    tq = math.floor(t * 12) / 12
    Z = 6.0 - tq * .5
    X = -.35 + tq * .12
    q = cam.p(X, .11, Z)
    r = .11 * cam.f / Z
    sh = cam.p(X + .2, 0, Z - .05)
    c.save(); c.translate(sh[0], sh[1]); c.scale(1, .3); c.arc(0, 0, r * 1.1, 0, 6.283); c.restore()
    c.set_source_rgba(.29, .24, .34, .45); c.fill()
    circle(c, q[0], q[1], r, fill=hexc('#efe9df'), line=LNC, lw=2.2)
    a = -tq * 5.5
    c.save(); c.translate(*q); c.rotate(a)
    c.arc(0, 0, r, -.6, .6); c.arc_negative(0, 0, r * .45, .6, -.6); c.close_path()
    c.set_source_rgba(*hexc('#cf3b2a')); c.fill()
    c.arc(0, 0, r, math.pi - .6, math.pi + .6); c.arc_negative(0, 0, r * .45, math.pi + .6, math.pi - .6); c.close_path()
    c.fill(); c.restore()


def frame(f):
    t = f / FPS
    lib.BOIL.amp = 0.4; lib.BOIL.set_frame(f, 2)
    # slow creep forward (true dolly, world re-projected)
    dz = 0.55 * (t / 3.0)
    cam = Cam(f=980, cx=520, cy=1250, h=1.35, x0=-.2)
    cam2 = Cam(f=980, cx=520, cy=1130, h=1.35, x0=-.2)
    # shift world toward camera by dz: wrap the projector
    base = cam.p
    cam.p = lambda X, Y, Z: base(X, Y, Z - dz)
    far, near = scene(DAY, t, cam)
    img = over(np.zeros((H, W, 3), np.float32), blur(far, 2.2))
    img = over(img, near)
    s, c = surface()
    speaker_pole(c, cam, 1.9, 17.0)
    items = [(11.0, lambda: girl_bike(c, cam, 1.55, 11.0, t)), (8.2, lambda: salaryman(c, cam, .7, 8.2, t)),
             (6.4, lambda: boy(c, cam, -.5, 6.4, t)), (5.0, lambda: grandma(c, cam, -1.25, 5.0, t))]
    for z, fn in items:
        fn()
        if z == 6.4:
            ball(c, cam, t)
    img = over(img, to_np(s))
    # warm low sun
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx + 80) ** 2 + (yy - 1050) ** 2) / 1250
    warm = np.clip(1 - d, 0, 1)[..., None] ** 1.6 * np.array([1.0, .62, .32], np.float32) * .45
    img = 1 - (1 - img) * (1 - warm)
    s, c = surface()
    from props import stamp
    stamp(c, 'KIRIYAMA  DAY 001  17:00:0' + str(4 + int(t)))
    img = over(img, to_np(s))
    img = bloom(img, .82, 22, .25)
    img = vignette(img, .24)
    img = grain(img, f + 1300, .018)
    return img


if __name__ == '__main__':
    f = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    save(frame(f), sys.argv[2] if len(sys.argv) > 2 else 'f004.jpg')
