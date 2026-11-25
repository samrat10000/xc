"""005_answer: slow push into the curve mirror. In the night street inside it, night-Sam stands in the road
looking straight at us, no headphones. At 1.2 s the 4th note plays (from inside the mirror). Black at 2.0 s."""
import sys
from lane import *
from props import *
import lib

FPS = 24
NOTE_T = 1.2
BLACK_T = 2.05


def night_sam(c, cam, X, Z, t):
    P = lambda x, y: cam.p(X + x, y, Z)
    L = hexc('#03050b')
    def sh(pts, col, lw=1.6):
        poly(c, [P(*q) for q in pts], fill=hexc(col), line=L, lw=lw)
    # legs (jeans), hoodie, arms hanging, head
    sh([(-.17, 0), (-.03, 0), (-.04, .86), (-.16, .86)], '#1b2742')
    sh([(.03, 0), (.17, 0), (.16, .86), (.04, .86)], '#1b2742')
    sh([(-.2, 0), (-.02, 0), (-.02, .06), (-.2, .06)], '#9aa3b8')
    sh([(.02, 0), (.2, 0), (.2, .06), (.02, .06)], '#9aa3b8')
    sh([(-.25, .8), (.25, .8), (.27, 1.42), (.12, 1.5), (-.12, 1.5), (-.27, 1.42)], '#1e2333')
    sh([(-.34, 1.4), (-.26, 1.44), (-.24, .84), (-.31, .82)], '#1e2333')
    sh([(.26, 1.44), (.34, 1.4), (.31, .82), (.24, .84)], '#1e2333')
    sh([(-.06, 1.48), (.06, 1.48), (.05, 1.56), (-.05, 1.56)], '#5d6b8a')
    # face, lit cold from the streetlight above
    q = P(0, 1.66); r = .105 * cam.f / Z
    c.save(); c.translate(*q); c.scale(1, 1.18); c.arc(0, 0, r, 0, 6.283); c.restore()
    c.set_source_rgba(*hexc('#8e9cbc')); c.fill_preserve(); c.set_source_rgba(*L); c.set_line_width(1.6); c.stroke()
    # messy hair (same silhouette language as Sam)
    hp = [(-.13, 1.64), (-.14, 1.78), (-.06, 1.83), (.06, 1.83), (.14, 1.77), (.13, 1.64), (.09, 1.7), (.05, 1.62), (.0, 1.7), (-.05, 1.62), (-.09, 1.7)]
    sh(hp, '#0a0d16')
    # red glasses (accent) with two pale eyes looking at camera
    for ex in (-.045, .045):
        e = P(ex, 1.665); rr = .032 * cam.f / Z
        c.arc(e[0], e[1], rr, 0, 6.283); c.set_source_rgba(*hexc('#e2402c')); c.set_line_width(max(1.2, rr * .28)); c.stroke()
        glow = .85 if t < NOTE_T else 1.0
        circle(c, e[0], e[1] + rr * .1, rr * .32, fill=(0.92, 0.95, 1, glow), line=None)
    # no headphones: bare ears catching light
    for ex in (-.11, .11):
        e = P(ex, 1.65); circle(c, e[0], e[1], .022 * cam.f / Z, fill=hexc('#7d8aa8'), line=L, lw=1)


def frame(f):
    t = f / FPS
    if t >= BLACK_T:
        img = np.zeros((H, W, 3), np.float32)
        s, c = surface()
        if t > BLACK_T + .35:
            c.select_font_face('IPAGothic'); c.set_font_size(30)
            txt = '五時のチャイム'
            e = c.text_extents(txt); c.move_to((W - e.width) / 2, 930); c.set_source_rgba(1, 1, 1, .8); c.show_text(txt)
            c.select_font_face('DejaVu Sans Mono', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(26)
            txt = "5 O'CLOCK  ·  DAY 001"
            e = c.text_extents(txt); c.move_to((W - e.width) / 2, 990); c.set_source_rgba(1, 1, 1, .6); c.show_text(txt)
        img = over(img, to_np(s))
        return grain(img, f + 2000, .012)
    lib.BOIL.amp = 0.45; lib.BOIL.set_frame(f, 2)
    u = t / BLACK_T
    k = u * u * (3 - 2 * u)
    R = 400 + 70 * k
    CX, CY = 540, 860
    PX = CX + R + 80
    cam = Cam(f=950, cx=420, cy=1250, h=1.5, x0=-0.6)
    far, near = scene(DAY, t + 3.0, cam)
    img = over(np.zeros((H, W, 3), np.float32), blur(far, 10))
    img = over(img, blur(near, 8))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - 60) ** 2 + (yy - 1080) ** 2) / 1100
    warm = np.clip(1 - d, 0, 1)[..., None] ** 1.6 * np.array([1.0, .62, .32], np.float32) * .42
    img = 1 - (1 - img) * (1 - warm)
    # night street with night-Sam
    ncam = Cam(f=820, cx=540, cy=1080, h=1.9, x0=0.3)
    nfar, nnear = scene(NIGHT, t + 3.0, ncam)
    nimg = over(np.zeros((H, W, 3), np.float32), nfar)
    nimg = over(nimg, nnear)
    s, c = surface()
    night_sam(c, ncam, .3, 4.2, t)
    nimg = over(nimg, to_np(s))
    nimg = bloom(nimg, .75, 10, .6)
    # at the 4th note the reflection flares very slightly (light, not a morph)
    if t >= NOTE_T:
        a = max(0, 1 - (t - NOTE_T) / .5)
        nimg = np.clip(nimg * (1 + .35 * a), 0, 1)
    s, c = surface()
    mirror_fg(c, CX, CY, R, PX, t)
    img = over(img, to_np(s))
    # mirror centre aimed so night-Sam sits just below centre
    img = fisheye_into(img, nimg, CX, CY, R, 560, 1150, 470, flip=True, k=.8)
    s, c = surface()
    glass_overlay(c, CX, CY, R, t)
    sec = 13 if t >= NOTE_T else 12
    stamp(c, f'KIRIYAMA  DAY 001  17:00:{sec:02d}')
    img = over(img, to_np(s))
    img = bloom(img, .82, 22, .25)
    img = vignette(img, .3)
    img = grain(img, f + 1700, .018)
    return img


if __name__ == '__main__':
    f = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    save(frame(f), sys.argv[2] if len(sys.argv) > 2 else 'f005.jpg')
