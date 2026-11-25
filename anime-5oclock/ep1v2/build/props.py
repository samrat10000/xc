"""foreground props: curve mirror, overlays (stamp, subtitles)"""
from lib import *
import lib

RED = '#d4452b'
RED_S = '#962b1f'
RED_HI = '#f07a52'


def mirror_fg(c, cx, cy, R, px, t, warm=True, pole_bottom=H + 20):
    L = hexc('#2b1d22')
    # pole
    pw = 36
    poly(c, [(px - pw / 2, pole_bottom), (px + pw / 2, pole_bottom), (px + pw / 2 - 2, cy - 40), (px - pw / 2 + 2, cy - 40)], fill=hexc(RED), line=L, lw=3)
    poly(c, [(px + 3, pole_bottom), (px + pw / 2, pole_bottom), (px + pw / 2 - 2, cy - 40), (px + 3, cy - 40)], fill=hexc(RED_S), line=None, lw=0)
    if warm:  # sun rim light on the left edge
        poly(c, [(px - pw / 2 + 2, pole_bottom), (px - pw / 2 + 8, pole_bottom), (px - pw / 2 + 8, cy - 40), (px - pw / 2 + 3, cy - 40)], fill=hexc(RED_HI), line=None, lw=0)
    # pole cap
    bez(c, [(px - pw / 2 + 2, cy - 40), (px - pw / 2, cy - 60, px + pw / 2, cy - 60, px + pw / 2 - 2, cy - 40)], fill=hexc(RED_S), line=L, lw=3)
    # traffic-safety plate on the pole
    sx0, sy0 = px - 44, cy + R + 260
    poly(c, [(sx0, sy0), (sx0 + 88, sy0), (sx0 + 88, sy0 + 250), (sx0, sy0 + 250)], fill=hexc('#eee9de'), line=L, lw=2.6)
    poly(c, [(sx0 + 6, sy0 + 6), (sx0 + 82, sy0 + 6), (sx0 + 82, sy0 + 244), (sx0 + 6, sy0 + 244)], fill=None, line=hexc('#2f4f8a'), lw=2)
    c.select_font_face(JP, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(50)
    c.set_source_rgb(*hexc('#2f4f8a')[:3])
    for i, ch in enumerate('交通安全'):
        c.move_to(sx0 + 19, sy0 + 62 + i * 56); c.show_text(ch)
    # band clamps
    for yy in (sy0 + 30, sy0 + 220):
        poly(c, [(px - pw / 2 - 4, yy), (px + pw / 2 + 4, yy), (px + pw / 2 + 4, yy + 10), (px - pw / 2 - 4, yy + 10)], fill=hexc('#8f8a90'), line=L, lw=1.8)
    # bracket arms to mirror back
    for (yy, dy) in ((cy - 70, 0), (cy + 60, 0)):
        poly(c, [(px - pw / 2, yy - 9), (cx + R + 20, yy - 9 + dy), (cx + R + 20, yy + 9 + dy), (px - pw / 2, yy + 9)], fill=hexc('#7d7880'), line=L, lw=2.4)
    # rim (back shell visible a bit on the right)
    circle(c, cx + 10, cy + 4, R + 30, fill=hexc(RED_S), line=L, lw=3)
    circle(c, cx, cy, R + 28, fill=hexc(RED), line=L, lw=3)
    if warm:
        c.arc(cx, cy, R + 21, math.radians(120), math.radians(250))
        c.set_source_rgba(*hexc(RED_HI)); c.set_line_width(9); c.stroke()
    # visor hood on top
    bez(c, [(cx - R - 34, cy - 20), (cx - R - 40, cy - R - 150, cx + R + 40, cy - R - 150, cx + R + 34, cy - 20),
            (cx + R + 20, cy - 24), (cx + R + 18, cy - R - 105, cx - R - 18, cy - R - 105, cx - R - 20, cy - 24)],
        fill=hexc(RED_S), line=L, lw=3)
    # bolts
    for a in (30, 150, 270):
        q = (cx + math.cos(math.radians(a)) * (R + 14), cy + math.sin(math.radians(a)) * (R + 14))
        circle(c, q[0], q[1], 4.5, fill=hexc('#ddd6cc'), line=L, lw=1.5)


def glass_overlay(c, cx, cy, R, t):
    # inner shadow ring
    rg = cairo.RadialGradient(cx, cy, R * .7, cx, cy, R)
    rg.add_color_stop_rgba(0, 0, 0, 0, 0)
    rg.add_color_stop_rgba(.85, 0, 0, 0, .12)
    rg.add_color_stop_rgba(1, 0, 0, 0, .55)
    c.set_source(rg); c.arc(cx, cy, R, 0, 6.283); c.fill()
    # cel highlight band (static, the glass is curved)
    c.save(); c.arc(cx, cy, R, 0, 6.283); c.clip()
    poly(c, [(cx - R, cy - R * .25), (cx - R * .25, cy - R), (cx - R * .05, cy - R), (cx - R, cy - R * .05)], fill=(1, 1, 1, .10), line=None, lw=0, boil=False)
    poly(c, [(cx - R, cy + R * .05), (cx + R * .05, cy - R), (cx + R * .14, cy - R), (cx - R, cy + R * .14)], fill=(1, 1, 1, .05), line=None, lw=0, boil=False)
    # dust specks + a dried raindrop trail
    import random
    r = random.Random(9)
    for i in range(40):
        a, d = r.uniform(0, 6.283), R * math.sqrt(r.random()) * .97
        circle(c, cx + math.cos(a) * d, cy + math.sin(a) * d, r.uniform(.6, 1.8), fill=(1, .95, .9, r.uniform(.08, .25)), line=None)
    c.restore()
    c.arc(cx, cy, R, 0, 6.283); c.set_source_rgba(*hexc('#2b1d22')); c.set_line_width(3); c.stroke()


def stamp(c, text, x=54, y=120, size=30, alpha=.92):
    c.select_font_face(MONO, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    c.set_font_size(size)
    c.move_to(x + 2, y + 2); c.set_source_rgba(0, 0, 0, .45); c.show_text(text)
    c.move_to(x, y); c.set_source_rgba(1, .97, .92, alpha); c.show_text(text)


def subtitle(c, text, y=1640, size=44, alpha=1.0, jp=None):
    c.select_font_face(SANS, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    ext = c.text_extents(text)
    x = (W - ext.width) / 2 - ext.x_bearing
    c.move_to(x, y); c.text_path(text)
    c.set_source_rgba(0, 0, 0, .55 * alpha); c.set_line_width(5); c.stroke_preserve()
    c.set_source_rgba(1, 1, 1, alpha); c.fill()
    if jp:
        c.select_font_face(JP); c.set_font_size(size * .62)
        e2 = c.text_extents(jp)
        c.move_to((W - e2.width) / 2 - e2.x_bearing, y + size * 1.05); c.text_path(jp)
        c.set_source_rgba(0, 0, 0, .5 * alpha); c.set_line_width(4); c.stroke_preserve()
        c.set_source_rgba(1, 1, 1, .85 * alpha); c.fill()


def leaf(c, x, y, ang, s, col='#c8642f', col_s='#8f3f22', flipk=1.0):
    """maple-ish leaf, cel 2-tone; flipk in [-1,1] fakes 3D tumble by squashing"""
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s * max(.12, abs(flipk)), s)
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * 2 * math.pi / 10
        r = 1.0 if i % 2 == 0 else .48
        pts.append((math.cos(a) * r * 20, math.sin(a) * r * 20))
    poly(c, pts, fill=hexc(col if flipk > 0 else col_s), line=hexc('#3a1f1a'), lw=1.6 / s, boil=False)
    poly(c, [(0, -18), (2, 0), (0, 18), (-2, 0)], fill=hexc(col_s, .6), line=None, lw=0, boil=False)
    c.restore()


def falling_leaves(c, t, seeds, area=(0, W, -100, H), speed=1.0):
    import random
    for sd in seeds:
        r = random.Random(sd)
        x0 = r.uniform(area[0], area[1]); y0 = r.uniform(area[2], area[3])
        vy = r.uniform(55, 95) * speed; vx = r.uniform(25, 60) * speed
        ph = r.uniform(0, 6.28); sc = r.uniform(.9, 1.6)
        # step on twos: quantize time like hand animation
        tq = math.floor(t * 12) / 12
        x = x0 + vx * tq + math.sin(tq * 2.2 + ph) * 38
        y = y0 + vy * tq
        y = (y + 200) % (area[3] + 400 - area[2]) + area[2] - 200
        leaf(c, x, y, math.sin(tq * 1.7 + ph) * 1.1, sc, flipk=math.cos(tq * 3.1 + ph))
