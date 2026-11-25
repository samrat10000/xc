"""Shot 17: what the curve mirror shows - the REAL Kiriyama at 5 PM, warm and normal: Sam's house, the lit genkan, his mother on the
doorstep calling his name, looking up and down the street. She cannot see him. Same API as paint_night.draw(f, leaf_u=None, flicker=1.0)."""
import math, numpy as np, cairo
from scipy.ndimage import gaussian_filter
N = 1200
yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)


def _a(s):
    s.flush(); return np.ndarray((N, N, 4), np.uint8, s.get_data()).astype(np.float32) / 255


def base(sky_only=False):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, N, N); c = cairo.Context(s)
    g = cairo.LinearGradient(0, 0, 0, N * .55)                                  # warm 5 PM sky
    for p, col in ((0, (.36, .26, .46)), (.45, (.95, .55, .40)), (.75, (1.0, .80, .55)), (1, (1.0, .88, .66))): g.add_color_stop_rgb(p, *col)
    c.set_source(g); c.paint()
    c.set_source_rgb(.55, .38, .46); c.move_to(0, N * .50)
    for x in np.linspace(0, N, 30): c.line_to(x, N * .50 - 30 * abs(math.sin(x / N * 4 + 1)) - 18 * abs(math.sin(x / N * 11)))
    c.line_to(N, N); c.line_to(0, N); c.close_path(); c.fill()
    if sky_only: return _a(s)[..., [2, 1, 0]]
    c.set_source_rgb(.42, .36, .40); c.rectangle(0, N * .62, N, N * .38); c.fill()                        # the road
    c.set_source_rgb(.62, .56, .54); c.rectangle(0, N * .60, N, N * .03); c.fill()                         # kerb
    # Sam's house: plaster wall, kawara roof, sliding genkan door with warm light behind frosted glass, a nameplate
    c.set_source_rgb(.86, .78, .66); c.rectangle(N * .18, N * .22, N * .64, N * .40); c.fill()
    c.set_source_rgb(.28, .28, .36); c.move_to(N * .12, N * .24); c.line_to(N * .50, N * .10); c.line_to(N * .88, N * .24); c.close_path(); c.fill()
    c.set_source_rgba(.15, .15, .22, 1); c.set_line_width(2)
    for k in range(14):
        x = N * .14 + k * N * .052; c.move_to(x, N * .235); c.line_to(N * .50 + (x - N * .50) * 0.4, N * .115); c.stroke()
    c.set_source_rgb(.45, .32, .24); c.rectangle(N * .40, N * .34, N * .22, N * .28); c.fill()                 # door frame
    c.set_source_rgb(1.0, .86, .58); c.rectangle(N * .415, N * .355, N * .19, N * .25); c.fill()               # warm light
    c.set_source_rgba(.45, .32, .24, 1); c.set_line_width(5)
    for k in range(1, 4): c.move_to(N * .415 + k * N * .0475, N * .355); c.line_to(N * .415 + k * N * .0475, N * .605); c.stroke()
    for k in range(1, 5): c.move_to(N * .415, N * .355 + k * N * .05); c.line_to(N * .605, N * .355 + k * N * .05); c.stroke()
    c.set_source_rgb(.90, .88, .82); c.rectangle(N * .66, N * .40, N * .05, N * .07); c.fill()                 # nameplate
    c.set_source_rgb(.55, .55, .58); c.rectangle(N * .36, N * .62, N * .30, N * .025); c.fill()                # step
    c.set_source_rgb(.30, .48, .30); c.arc(N * .26, N * .58, N * .06, 0, 7); c.fill(); c.arc(N * .78, N * .57, N * .07, 0, 7); c.fill()  # potted shrubs
    c.set_source_rgb(.52, .32, .24); c.rectangle(N * .23, N * .58, N * .06, N * .05); c.fill(); c.rectangle(N * .745, N * .58, N * .07, N * .05); c.fill()
    return _a(s)[..., [2, 1, 0]]


BASE = base()


def mother(c, x, y, h, turn, call):
    """his mother on the step: apron, hair tied back, one hand cupped to her mouth, calling; she looks left/right (turn -1..1)"""
    hd = h / 7.2
    c.save(); c.translate(x, y)
    T = lambda u: -h + hd * u
    c.set_source_rgb(.16, .11, .15)                                              # body + skirt
    c.move_to(-hd * .9, T(1.4)); c.curve_to(-hd * 1.0, T(2.8), -hd * 1.2, T(5.2), -hd * 1.25, T(6.9)); c.line_to(hd * 1.25, T(6.9))
    c.curve_to(hd * 1.2, T(5.2), hd * 1.0, T(2.8), hd * .9, T(1.4)); c.close_path(); c.fill()
    c.set_source_rgb(.74, .70, .62)                                              # apron
    c.move_to(-hd * .6, T(2.0)); c.line_to(hd * .6, T(2.0)); c.line_to(hd * .85, T(5.6)); c.line_to(-hd * .85, T(5.6)); c.close_path(); c.fill()
    c.set_source_rgb(.88, .72, .62)                                              # face, turned
    c.save(); c.translate(turn * hd * .12, T(.55)); c.scale(1 - .25 * abs(turn), 1); c.arc(0, 0, hd * .48, 0, 7); c.fill(); c.restore()
    c.set_source_rgb(.18, .13, .14); c.arc(turn * hd * .12, T(.38), hd * .52, math.pi, 2 * math.pi); c.fill()
    c.arc(turn * hd * .12 - hd * .45 * (1 if turn >= 0 else -1), T(.45), hd * .2, 0, 7); c.fill()            # tied-back hair
    c.set_source_rgb(.16, .11, .15); c.set_line_width(hd * .36)                    # calling: hand cupped to her mouth
    c.move_to(hd * .8, T(1.6)); c.line_to(hd * .7, T(.95 - .05 * call)); c.stroke()
    c.set_source_rgb(.88, .72, .62); c.arc(hd * .5 + turn * hd * .1, T(.82), hd * .17, 0, 7); c.fill()
    c.set_source_rgb(.16, .11, .15); c.set_line_width(hd * .34); c.move_to(-hd * .8, T(1.6)); c.line_to(-hd * .95, T(3.6)); c.stroke()
    c.set_source_rgb(.20, .16, .16); c.rectangle(-hd * .55, T(6.9), hd * .4, hd * .3); c.fill(); c.rectangle(hd * .15, T(6.9), hd * .4, hd * .3); c.fill()
    c.restore()


import os
DAYDIR = os.environ.get('DAY17_DIR', '')
SKY = base(sky_only=True)


def draw(f, leaf_u=None, flicker=1.0):
    p = os.path.join(DAYDIR, 'day_%03d.png' % max(1, int(f))) if DAYDIR else ''
    if p and os.path.exists(p):                                                # v2: the 3D day render (real mother, real house)
        from PIL import Image
        im = np.asarray(Image.open(p).convert('RGBA').resize((N, N), Image.LANCZOS)).astype(np.float32) / 255
        a = im[..., 3:4]; img = SKY * (1 - a) + im[..., :3] * a
        glow = np.exp(-(((xx - N * .50) / (N * .22)) ** 2 + ((yy - N * .55) / (N * .22)) ** 2))
        return np.clip(img + glow[..., None] * np.array([.10, .06, .02]), 0, 1)
    img = BASE.copy()
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, N, N); c = cairo.Context(s)
    turn = math.sin(f * 0.07) * 0.9; call = 1.0 if (f // 10) % 2 == 0 else 0.0
    mother(c, N * .51, N * .62, N * .27, turn, call)
    a = _a(s); m = a[..., 3:4]; rgb = a[..., [2, 1, 0]]
    rgb = np.where(m > 0, rgb / np.maximum(m, 1e-3), 0)
    img = img * (1 - m) + rgb * m
    glow = np.exp(-(((xx - N * .51) / (N * .18)) ** 2 + ((yy - N * .50) / (N * .18)) ** 2))   # warm genkan glow on her
    img = img + glow[..., None] * np.array([.20, .13, .05])
    img = gaussian_filter(img, (1.0, 1.0, 0))
    return np.clip(img, 0, 1)


if __name__ == '__main__':
    from PIL import Image
    Image.fromarray((draw(1) * 255).astype(np.uint8)).resize((600, 600)).save('day17_test.png')
