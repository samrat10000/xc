"""Ep1 storyboard strip: rough pencil panels (5), red accent. Panel 1 uses the real look-test frame."""
import math, random
import cairo
from PIL import Image
import numpy as np

PW, PH = 432, 768
GAP, TOP, CAP = 28, 90, 200
NW = 5 * PW + 6 * GAP
NH = TOP + PH + CAP
PAPER = (0.96, 0.94, 0.9)
PEN = (0.22, 0.2, 0.22)
REDC = (0.83, 0.27, 0.17)
rnd = random.Random(4)


def pencil(c, pts, w=2.2, col=PEN, close=False, passes=2, jit=1.6):
    for k in range(passes):
        c.new_path()
        P = [(x + rnd.uniform(-jit, jit), y + rnd.uniform(-jit, jit)) for x, y in pts]
        c.move_to(*P[0])
        for p in P[1:]:
            c.line_to(*p)
        if close:
            c.close_path()
        c.set_source_rgba(*col, .75 if k else .9)
        c.set_line_width(w * (1 if k == 0 else .6))
        c.stroke()


def fillp(c, pts, col, a=1):
    c.new_path(); c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path(); c.set_source_rgba(*col, a); c.fill()


def ell(cx, cy, rx, ry, n=40, a0=0, a1=2 * math.pi):
    return [(cx + rx * math.cos(a0 + (a1 - a0) * i / n), cy + ry * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def hatch(c, x0, y0, x1, y1, step=9, col=PEN, a=.35):
    c.save(); c.rectangle(x0, y0, x1 - x0, y1 - y0); c.clip()
    for k in range(-int((y1 - y0)), int(x1 - x0), step):
        c.move_to(x0 + k, y1); c.line_to(x0 + k + (y1 - y0), y0)
    c.set_source_rgba(*col, a); c.set_line_width(1.2); c.stroke(); c.restore()


def notes(c, x, y, n_ok, missing=True, s=1.0):
    c.select_font_face('DejaVu Sans'); c.set_font_size(46 * s)
    for i in range(4):
        xx = x + i * 62 * s
        if i < n_ok:
            c.move_to(xx, y - i * 14 * s); c.set_source_rgba(*PEN, .95); c.show_text('♪')
        elif missing:
            c.set_source_rgba(*REDC, 1); c.set_line_width(4)
            yy = y - i * 14 * s - 16 * s
            c.move_to(xx, yy - 16 * s); c.line_to(xx + 30 * s, yy + 16 * s)
            c.move_to(xx + 30 * s, yy - 16 * s); c.line_to(xx, yy + 16 * s); c.stroke()
        else:
            c.move_to(xx, y - i * 14 * s); c.set_source_rgba(*REDC, 1); c.show_text('♪')


def person(c, x, y, s, face_up=True, kind='man'):
    """rough standing figure from behind, head tilted up toward the speaker"""
    h = 160 * s
    head = (x, y - h + 14 * s)
    pencil(c, ell(head[0], head[1] - (6 * s if face_up else 0), 13 * s, 15 * s), 2)
    fillp(c, ell(head[0], head[1] - (6 * s if face_up else 0), 13 * s, 15 * s), PEN, .55)
    body = [(x - 22 * s, y - h + 34 * s), (x + 22 * s, y - h + 34 * s), (x + 26 * s, y - h * .45), (x - 26 * s, y - h * .45)]
    if kind == 'grandma':
        body = [(x - 20 * s, y - h + 40 * s), (x + 20 * s, y - h + 40 * s), (x + 34 * s, y - 20 * s), (x - 34 * s, y - 20 * s)]
    fillp(c, body, PEN, .35); pencil(c, body, 2, close=True)
    for dx in (-12, 12):
        pencil(c, [(x + dx * s, y - h * .45), (x + dx * s * 1.1, y)], 3)
    for dx in (-26, 26):
        pencil(c, [(x + dx * s, y - h + 40 * s), (x + dx * s * 1.15, y - h * .5)], 2.5)


def panel(c, i, x0, y0):
    c.save(); c.translate(x0, y0); c.rectangle(0, 0, PW, PH); c.clip()
    c.set_source_rgb(1, 1, 1); c.paint()
    if i == 0:
        im = Image.open('f001.jpg').convert('RGB').resize((PW, PH), Image.LANCZOS)
        a = np.array(im)
        bgra = np.dstack([a[..., 2], a[..., 1], a[..., 0], np.full(a.shape[:2], 255, np.uint8)]).copy()
        s = cairo.ImageSurface.create_for_data(bytearray(bgra.tobytes()), cairo.FORMAT_ARGB32, PW, PH)
        c.set_source_surface(s, 0, 0); c.paint()
    elif i == 1:
        # low angle: pole + loudspeaker horns, crows lifting off
        g = cairo.LinearGradient(0, 0, 0, PH); g.add_color_stop_rgb(0, .93, .85, .78); g.add_color_stop_rgb(1, .99, .9, .78)
        c.set_source(g); c.paint()
        pole = [(180, PH + 10), (232, PH + 10), (214, 140), (196, 140)]
        fillp(c, pole, (.75, .72, .7)); pencil(c, pole, 2.4, close=True)
        for (hx, hy, d) in ((205, 220, -1), (205, 220, 1), (205, 330, -1), (205, 330, 1)):
            horn = [(hx, hy - 16), (hx + d * 120, hy - 48), (hx + d * 132, hy + 40), (hx, hy + 16)]
            fillp(c, horn, (.86, .84, .8)); pencil(c, horn, 2.4, close=True)
            pencil(c, ell(hx + d * 126, hy - 4, 10, 44), 2)
        for k in range(7):
            bx, by = 60 + rnd.uniform(0, 330), 420 + rnd.uniform(0, 250)
            pencil(c, [(bx - 18, by), (bx - 6, by - 8), (bx, by), (bx + 6, by - 8), (bx + 18, by)], 2.6)
        notes(c, 90, 140, 3, True, .9)
    elif i == 2:
        # Sam close: red glasses, one headphone pulled off, looking up
        c.set_source_rgb(.97, .9, .82); c.paint()
        hatch(c, 0, 0, PW, PH, 14, PEN, .12)
        cx, cy = 210, 380
        face = ell(cx, cy, 105, 135)
        fillp(c, face, (1, .96, .92)); pencil(c, face, 2.6)
        hair = [(cx - 125, cy - 30), (cx - 115, cy - 140), (cx - 30, cy - 175), (cx + 70, cy - 165), (cx + 125, cy - 90), (cx + 118, cy - 20),
                (cx + 90, cy - 85), (cx + 40, cy - 70), (cx + 10, cy - 105), (cx - 30, cy - 70), (cx - 80, cy - 95)]
        fillp(c, hair, (.18, .17, .2)); pencil(c, hair, 2.4, close=True)
        for ex in (-45, 45):
            pencil(c, ell(cx + ex, cy - 10, 30, 22), 3.5, REDC)
            fillp(c, ell(cx + ex, cy - 18, 9, 11), PEN)
        pencil(c, [(cx - 15, cy - 10), (cx + 15, cy - 10)], 3, REDC)
        pencil(c, [(cx - 20, cy + 70), (cx + 15, cy + 66)], 2.2)
        # headphones: one on ear (left), one pulled down in hand
        pencil(c, ell(cx - 112, cy + 10, 26, 44), 3); fillp(c, ell(cx - 112, cy + 10, 26, 44), PEN, .8)
        pencil(c, [(cx - 112, cy - 30), (cx - 60, cy - 190), (cx + 80, cy - 190), (cx + 150, cy + 100)], 4)
        pencil(c, ell(cx + 160, cy + 140, 28, 40), 3); fillp(c, ell(cx + 160, cy + 140, 28, 40), PEN, .8)
        hand = [(cx + 120, cy + 170), (cx + 200, cy + 150), (cx + 215, cy + 210), (cx + 140, cy + 240)]
        fillp(c, hand, (1, .95, .9)); pencil(c, hand, 2.4, close=True)
        hood = [(cx - 160, PH), (cx - 120, cy + 150), (cx + 120, cy + 150), (cx + 190, PH)]
        fillp(c, hood, (.45, .45, .5)); pencil(c, hood, 2.4, close=True)
        c.select_font_face('DejaVu Sans'); c.set_font_size(34); c.set_source_rgba(*PEN, .8)
        c.move_to(300, 120); c.show_text('?')
    elif i == 3:
        # wide street: everyone frozen, faces up to the speaker
        g = cairo.LinearGradient(0, 0, 0, PH); g.add_color_stop_rgb(0, .95, .83, .74); g.add_color_stop_rgb(.55, .99, .9, .76); g.add_color_stop_rgb(.56, .82, .79, .8); g.add_color_stop_rgb(1, .7, .68, .72)
        c.set_source(g); c.paint()
        vp = (216, 420)
        for x in (-40, 470):
            pencil(c, [(x, PH), vp], 2.2)
        for x in (60, 370):
            pencil(c, [(x, 520), (vp[0] + (x - vp[0]) * .2, vp[1] - 10)], 1.6)
        pencil(c, [(360, 430), (364, 80)], 3)
        for (hx, d) in ((362, -1), (362, 1)):
            pencil(c, [(hx, 110), (hx + d * 42, 96), (hx + d * 46, 128), (hx, 122)], 2.2, close=True)
        person(c, 110, 690, 1.0, kind='grandma')
        person(c, 300, 640, .8)
        person(c, 200, 520, .5)
        person(c, 260, 480, .35)
        # little ball rolling on its own
        pencil(c, ell(150, 720, 14, 14), 2.2, REDC)
        for (x, y) in ((110, 470), (300, 430)):
            c.set_source_rgba(*PEN, .6); c.set_line_width(1.4)
        # sight lines to speaker (dashed)
        c.set_dash([8, 8]); c.set_source_rgba(*REDC, .7); c.set_line_width(1.6)
        for (x, y) in ((110, 540), (300, 520), (200, 445)):
            c.move_to(x, y); c.line_to(362, 120)
        c.stroke(); c.set_dash([])
    elif i == 4:
        # mirror close: night reflection Sam staring at us, no headphones
        c.set_source_rgb(.95, .85, .76); c.paint()
        cx, cy, R = 216, 360, 190
        fillp(c, ell(cx, cy, R + 22, R + 22), REDC)
        fillp(c, ell(cx, cy, R, R), (.08, .11, .2))
        pencil(c, ell(cx, cy, R + 22, R + 22), 2.8); pencil(c, ell(cx, cy, R, R), 2.4)
        # reflected lane at night
        for x in (-60, 60):
            pencil(c, [(cx + x * 3, cy + R * .9), (cx + x * .2, cy + 20)], 1.6, (.5, .55, .7))
        # reflected Sam: head and shoulders, eyes glowing faintly, looking at camera
        fillp(c, ell(cx, cy + 40, 52, 64), (.18, .21, .32))
        fillp(c, [(cx - 100, cy + R), (cx - 70, cy + 105), (cx + 70, cy + 105), (cx + 100, cy + R)], (.14, .17, .27))
        for ex in (-20, 20):
            pencil(c, ell(cx + ex, cy + 32, 13, 9), 2.6, REDC)
            fillp(c, ell(cx + ex, cy + 32, 3.5, 3.5), (.95, .95, 1))
        pencil(c, [(216, 650), (216, PH)], 6, REDC)
        notes(c, 70, 700, 3, False, .9)
        c.select_font_face('DejaVu Sans Mono', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(26)
        c.set_source_rgba(*REDC, 1); c.move_to(268, 650); c.show_text('4th note')
    c.restore()
    c.rectangle(x0, y0, PW, PH); c.set_source_rgb(*PEN); c.set_line_width(3); c.stroke()


CAPS = [("001  4:59 PM", "The street mirror shows", "the same street at NIGHT."),
        ("002  5:00 PM", "The town chime always plays", "4 notes. Today: only 3."),
        ("003  Sam", "Headphones on, so he barely", "heard it. He looks up."),
        ("004  Everyone", "Everyone else froze,", "staring up at the speaker."),
        ("005  The answer", "In the mirror, night-Sam", "stares back. The 4th note plays.")]

s = cairo.ImageSurface(cairo.FORMAT_ARGB32, NW, NH)
c = cairo.Context(s)
c.set_source_rgb(*PAPER); c.paint()
c.select_font_face('Inter', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(40)
c.set_source_rgb(*PEN); c.move_to(GAP, 62); c.show_text("5 O'CLOCK  ·  Episode 1  ·  \"Three Notes\"")
for i in range(5):
    x0 = GAP + i * (PW + GAP)
    panel(c, i, x0, TOP)
    t, l1, l2 = CAPS[i]
    c.select_font_face('Inter', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(30)
    c.set_source_rgb(*REDC); c.move_to(x0, TOP + PH + 48); c.show_text(t)
    c.select_font_face('Inter'); c.set_font_size(27); c.set_source_rgb(*PEN)
    c.move_to(x0, TOP + PH + 90); c.show_text(l1)
    c.move_to(x0, TOP + PH + 128); c.show_text(l2)
s.write_to_png('board.png')
