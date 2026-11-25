"""002_speaker: low angle up the town loudspeaker pole at 17:00. Chime plays 3 notes; crows lift off."""
import sys, random
from lib import *
from props import stamp, RED
import lib

LN = hexc('#2b1d22')
CHIME_T = [0.55, 1.05, 1.55]   # note onsets in this shot (s)
TAKEOFF = 0.62


def sky(c, t):
    g = cairo.LinearGradient(0, 0, 0, H)
    for o, col in ((0, '#55618f'), (.35, '#a98aa8'), (.7, '#eab08c'), (1, '#f8d4a4')):
        g.add_color_stop_rgb(o, *hexc(col)[:3])
    c.set_source(g); c.paint()
    # sun low right, behind roofs
    rg = cairo.RadialGradient(900, 1650, 10, 900, 1650, 900)
    rg.add_color_stop_rgba(0, 1, .95, .82, 1); rg.add_color_stop_rgba(.2, 1, .85, .62, .55); rg.add_color_stop_rgba(1, 1, .8, .6, 0)
    c.set_source(rg); c.paint()
    for (x, y, w, h, col, a) in ((-100, 260, 700, 60, '#8a7ea6', .7), (420, 190, 820, 44, '#9483a8', .6), (80, 620, 620, 52, '#d79f97', .75),
                                  (560, 760, 640, 40, '#e6ac8f', .7), (-60, 980, 520, 36, '#f0bd95', .7)):
        dx = t * 6  # slow drift
        x += dx
        bez(c, [(x, y + h), (x + w * .1, y + h * .2, x + w * .2, y, x + w * .35, y + h * .25),
                (x + w * .5, y - h * .3, x + w * .7, y, x + w * .8, y + h * .3),
                (x + w * .9, y + h * .3, x + w, y + h * .7, x + w, y + h)], fill=hexc(col, a), line=None, lw=0)


def roofs(c):
    # blurred foreground roof edges from the low angle, bottom corners
    poly(c, [(-20, 1500), (330, 1660), (360, 1960), (-20, 1960)], fill=hexc('#3a3550'), line=LN, lw=3)
    poly(c, [(-20, 1490), (330, 1652), (330, 1675), (-20, 1515)], fill=hexc('#5d5470'), line=None, lw=0)
    poly(c, [(1100, 1580), (760, 1720), (740, 1960), (1100, 1960)], fill=hexc('#433c57'), line=LN, lw=3)
    # antenna on the right roof
    line(c, (930, 1660), (930, 1440), LN, 4)
    for k, w in enumerate((120, 90, 60)):
        line(c, (930 - w / 2, 1480 + k * 34), (930 + w / 2, 1480 + k * 34), LN, 3)


def pole_and_speakers(c, t):
    # tapered concrete pole, low angle convergence
    P0l, P0r = (380, 1960), (520, 1960)
    P1l, P1r = (522, 330), (574, 330)
    poly(c, [P0l, P0r, P1r, P1l], fill=hexc('#7d7488'), line=LN, lw=3.2)
    poly(c, [(470, 1960), P0r, P1r, (556, 330)], fill=hexc('#5e566e'), line=None, lw=0)
    # sun rim light on the right edge
    poly(c, [(505, 1960), P0r, P1r, (568, 330)], fill=hexc('#f6c79a', .9), line=None, lw=0)
    # step bolts
    for k in range(9):
        y = 1800 - k * 115
        u = (1960 - y) / (1960 - 330)
        xl = 380 + (522 - 380) * u; xr = 520 + (574 - 520) * u
        s = -1 if k % 2 else 1
        x = xl if s < 0 else xr
        line(c, (x, y), (x + s * (40 - 20 * u), y - 4), LN, 5 - 2 * u)
    # control box (bosai)
    bx, by = 600, 980
    poly(c, [(bx - 10, by), (bx + 150, by - 10), (bx + 150, by + 210), (bx - 10, by + 220)], fill=hexc('#c9c3bd'), line=LN, lw=3)
    poly(c, [(bx + 120, by - 8), (bx + 150, by - 10), (bx + 150, by + 210), (bx + 120, by + 212)], fill=hexc('#9c95a0'), line=None, lw=0)
    c.select_font_face('IPAGothic', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(19); c.set_source_rgba(*hexc('#2a3a6a'))
    for i, ch in enumerate('防災行政無線'):
        c.move_to(bx + 14, by + 34 + i * 27); c.show_text(ch)
    for yy in (by + 30, by + 180):
        poly(c, [(bx - 30, yy), (bx, yy - 2), (bx, yy + 12), (bx - 30, yy + 12)], fill=hexc('#8d8792'), line=LN, lw=2)
    # conduit to the speakers
    line(c, (bx + 40, by), (560, 480), LN, 6)
    line(c, (bx + 40, by), (560, 480), hexc('#8d8792'), 3)
    # crossarm with wires
    poly(c, [(300, 640), (820, 610), (820, 640), (300, 672)], fill=hexc('#5e566e'), line=LN, lw=3)
    # speaker array: 4 horns (two up, two down), low angle
    cx, cy = 548, 430
    horns = [(-1, -1), (1, -1), (-1, 1), (1, 1)]
    for (sx, sy) in horns:
        ang = math.atan2(sy * .55, sx)
        L = 230
        bx2, by2 = cx + math.cos(ang) * L, cy + math.sin(ang) * L * .9 + sy * 20
        nx, ny = -math.sin(ang), math.cos(ang)
        r0, r1 = 26, 92
        q = [(cx + nx * r0, cy + ny * r0), (bx2 + nx * r1, by2 + ny * r1), (bx2 - nx * r1, by2 - ny * r1), (cx - nx * r0, cy - ny * r0)]
        poly(c, q, fill=hexc('#d3ccc6'), line=LN, lw=3)
        # shadow underside
        q2 = [(cx, cy), (bx2, by2), (bx2 - nx * r1, by2 - ny * r1), (cx - nx * r0, cy - ny * r0)]
        poly(c, q2, fill=hexc('#a59daa', .85), line=None, lw=0)
        # bell mouth (ellipse)
        c.save(); c.translate(bx2, by2); c.rotate(ang); c.scale(.32, 1)
        c.arc(0, 0, r1, 0, 6.283); c.restore()
        c.set_source_rgba(*hexc('#3a3346')); c.fill_preserve(); c.set_source_rgba(*LN); c.set_line_width(3); c.stroke()
        c.save(); c.translate(bx2, by2); c.rotate(ang); c.scale(.2, .62)
        c.arc(0, 0, r1, 0, 6.283); c.restore()
        c.set_source_rgba(*hexc('#1a1622')); c.fill()
        # rim ring
        c.save(); c.translate(bx2, by2); c.rotate(ang); c.scale(.32, 1)
        c.arc(0, 0, r1 + 6, 0, 6.283); c.restore()
        c.set_source_rgba(*LN); c.set_line_width(3); c.stroke()
    # hub
    circle(c, cx, cy, 34, fill=hexc('#8d8792'), line=LN, lw=3)
    # tip antenna + red aviation-style marker (accent)
    line(c, (548, 330), (548, 150), LN, 4)
    circle(c, 548, 150, 7, fill=hexc(RED), line=LN, lw=2)


def wires(c, t, shake):
    pts = []
    for k, (a, b, d) in enumerate((((300, 650), (-40, 720), 30), ((300, 655), (1120, 560), 40), ((820, 622), (1120, 700), 25),
                                    ((820, 618), (-40, 520), 60), ((560, 640), (1120, 860), 50))):
        sw = math.sin(t * 2 + k) * (1.5 + shake * 6)
        sag(c, a, b, d + sw, LN, 2.6)
        pts.append((a, b, d + sw))
    return pts


CROWS = [(0.25, 2, -1.0), (0.42, 1, 1.0), (0.6, 2, -1.0), (0.78, 1, 1.0), (0.12, 3, 1.0), (0.66, 3, -1.0)]


def crow(c, x, y, s, phase, flying, face):
    c.save(); c.translate(x, y); c.scale(s * face, s)
    if not flying:
        body = [(-30, 0), (-12, -26), (14, -30), (26, -44), (40, -40), (34, -28), (24, -18), (10, 2), (-30, 8)]
        poly(c, body, fill=hexc('#15121b'), line=LN, lw=2 / s)
        poly(c, [(40, -40), (54, -37), (38, -33)], fill=hexc('#15121b'), line=None, lw=0)
        line(c, (-2, 6), (-4, 18), LN, 2 / s); line(c, (8, 4), (8, 18), LN, 2 / s)
        circle(c, 33, -38, 1.6, fill=(.8, .8, .9, 1), line=None)
    else:
        # 4 drawings wing cycle
        k = int(phase) % 4
        wy = [-70, -25, 30, -25][k]
        wx = [10, 30, 20, 30][k]
        body = [(-36, 0), (-10, -10), (20, -10), (40, -14), (52, -10), (40, -2), (20, 6), (-36, 6)]
        poly(c, body, fill=hexc('#15121b'), line=LN, lw=2 / s)
        poly(c, [(-36, 0), (-58, -8), (-60, 10), (-36, 6)], fill=hexc('#15121b'), line=LN, lw=2 / s)
        for side in (1, .7):
            wing = [(-8, -6), (wx * side - 20, wy * side), (wx * side + 30, wy * side * .9 - 6), (16, -8)]
            poly(c, wing, fill=hexc('#1d1924'), line=LN, lw=2 / s)
    c.restore()


def crows(c, t, wire_pts):
    for i, (u, wi, face) in enumerate(CROWS):
        a, b, d = wire_pts[wi]
        x = a[0] + (b[0] - a[0]) * u
        y = a[1] + (b[1] - a[1]) * u + d * 4 * u * (1 - u)
        start = TAKEOFF + i * .07
        if t < start:
            bob = 3 if (int(t * 12) + i) % 9 == 0 else 0
            crow(c, x, y - 2 - bob, 1.0, 0, False, face)
        else:
            tt = t - start
            tq = math.floor(tt * 12) / 12
            vx = face * (220 + i * 40); vy = -(260 + i * 25)
            fx = x + vx * tq; fy = y + vy * tq + 70 * tq * tq
            s = 1.0 + tq * .25
            crow(c, fx, fy, s, tq * 12 / 1.2, True, face)


def frame(f, fps=24):
    t = f / fps
    lib.BOIL.amp = 0.5; lib.BOIL.set_frame(f, 2)
    # tiny loudspeaker vibration on each note (camera micro-shake)
    shake = 0
    for n in CHIME_T:
        if 0 <= t - n < .35:
            shake = max(shake, 1 - (t - n) / .35)
    s, c = surface(); sky(c, t); bg = to_np(s)[..., :3]
    s, c = surface(); roofs(c); r = to_np(s)
    img = over(bg, blur(r, 7))
    s, c = surface()
    c.translate(math.sin(f * 1.7) * shake * 1.5, math.cos(f * 2.3) * shake * 1.5)
    wp = wires(c, t, shake)
    pole_and_speakers(c, t)
    crows(c, t, wp)
    img = over(img, to_np(s))
    s, c = surface()
    stamp(c, 'KIRIYAMA  DAY 001  17:00:00' if t > .3 else 'KIRIYAMA  DAY 001  16:59:59')
    img = over(img, to_np(s))
    img = bloom(img, .8, 26, .35)
    img = vignette(img, .25)
    img = grain(img, f + 500, .018)
    return img


if __name__ == '__main__':
    f = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    save(frame(f), sys.argv[2] if len(sys.argv) > 2 else 'f002.jpg')
