"""Sam, close-up 3/4 view facing screen-left. One fixed design: black messy hair, red-frame glasses,
charcoal hoodie, black over-ear headphones. Drawn as vector cel art; pose params change the drawing."""
from lib import *
import lib

LN = hexc('#2a1c22')
SK, SK_S, SK_S2 = hexc('#f2d5c2'), hexc('#d6a595'), hexc('#c08a80')
RIM = hexc('#ffd2a6')
HR, HR_S, HR_HI = hexc('#2c2a36'), hexc('#1d1b24'), hexc('#575268')
HD, HD_S, HD_HI = hexc('#4a4c57'), hexc('#33343e'), hexc('#6b6a74')
GL = hexc('#cf3b2a')
PH, PH_S = hexc('#1c1b21'), hexc('#2e2d36')
EYE_W = hexc('#f7f1ec')
IRIS, IRIS_D = hexc('#4a2f2a'), hexc('#24161a')


def lerp(a, b, u):
    return a + (b - a) * u


def lp(p, q, u):
    return (lerp(p[0], q[0], u), lerp(p[1], q[1], u))


class X:
    """2D transform for the head group: rotate about pivot, then offset"""
    def __init__(self, ang=0, piv=(560, 1060), off=(0, 0)):
        self.c, self.s, self.piv, self.off = math.cos(ang), math.sin(ang), piv, off

    def __call__(self, p):
        x, y = p[0] - self.piv[0], p[1] - self.piv[1]
        return (self.piv[0] + x * self.c - y * self.s + self.off[0], self.piv[1] + x * self.s + y * self.c + self.off[1])

    def segs(self, segs):
        out = [self(segs[0])]
        for s in segs[1:]:
            if len(s) == 6:
                a, b, c = self((s[0], s[1])), self((s[2], s[3])), self((s[4], s[5]))
                out.append(a + b + c)
            else:
                out.append(self(s))
        return out


def B(c, T, segs, fill=None, line=LN, lw=2.6, close=True):
    bez(c, T.segs(segs), fill=fill, line=line, lw=lw, close=close)


def body(c, pose):
    br = pose.get('breath', 0) * 4
    # hoodie torso (not in head transform)
    hood = [(250, 1960), (300, 1440, 350, 1330, 440, 1250), (500, 1155, 560, 1240, 640, 1225),
            (720, 1130, 820, 1230, 880, 1320), (950, 1390, 990, 1700, 1010, 1960)]
    hood = [(p[0], p[1] - br) if len(p) == 2 else tuple(v - (br if i % 2 else 0) for i, v in enumerate(p)) for p in hood]
    bez(c, hood, fill=HD, line=LN, lw=3)
    # shadow side (right, away from sun)
    bez(c, [(700, 1960), (720, 1640, 760, 1450, 760, 1260), (840, 1200, 900, 1330, 930, 1420), (970, 1540, 990, 1780, 1010, 1960)], fill=HD_S, line=None, lw=0)
    # rim light on left shoulder
    bez(c, [(262, 1960), (300, 1500, 350, 1360, 446, 1262), (420, 1240, 360, 1450, 300, 1960)], fill=hexc('#8f7f86'), line=None, lw=0)
    # hood bunched behind the neck
    bez(c, [(600, 1175), (650, 1130, 760, 1080, 840, 1150), (900, 1150, 900, 1300, 860, 1340), (800, 1230, 720, 1260, 600, 1235)], fill=HD_S, line=LN, lw=3)
    bez(c, [(640, 1170), (700, 1170, 780, 1150, 830, 1190)], line=hexc('#2a1c22', .7), lw=2, close=False)
    # drawstrings
    for (x0, x1) in ((470, 455), (560, 585)):
        bez(c, [(x0, 1262), (x0 - 8, 1360, x1 + 6, 1440, x1, 1520)], line=hexc('#d9d3cf'), lw=6, close=False)
        bez(c, [(x0, 1262), (x0 - 8, 1360, x1 + 6, 1440, x1, 1520)], line=LN, lw=1.4, close=False)
        circle(c, x1, 1528, 7, fill=hexc('#bdb5b2'), line=LN, lw=1.5)
    # collar/neck opening
    bez(c, [(430, 1198), (480, 1230, 560, 1290, 640, 1232)], line=LN, lw=2.6, close=False)
    # fabric folds
    for seg in ([(380, 1440), (420, 1520, 430, 1680, 420, 1780)], [(800, 1440), (790, 1540, 800, 1700, 830, 1800)], [(600, 1340), (620, 1420, 640, 1560, 630, 1640)]):
        bez(c, seg, line=hexc('#2a1c22', .55), lw=2, close=False)


def neck(c, T):
    B(c, T, [(515, 1012), (515, 1080, 500, 1150, 465, 1192), (540, 1222, 620, 1206, 680, 1172), (668, 1100, 664, 1040, 662, 980)], fill=SK, lw=2.6)
    # neck shadow under the jaw (cel)
    B(c, T, [(515, 1020), (550, 1070, 610, 1066, 662, 990), (664, 1060, 668, 1120, 680, 1172), (610, 1150, 560, 1110, 500, 1090)], fill=SK_S, line=None, lw=0)
    # throat line
    B(c, T, [(520, 1110), (526, 1140, 530, 1165, 528, 1195)], line=hexc('#2a1c22', .45), lw=1.6, close=False)


def ear(c, T):
    B(c, T, [(640, 880), (670, 850, 700, 870, 698, 910), (696, 960, 676, 990, 650, 985), (640, 950)], fill=SK_S, lw=2.4)
    B(c, T, [(655, 900), (676, 890, 684, 920, 670, 950)], line=hexc('#2a1c22', .7), lw=1.8, close=False)


def head_back_hair(c, T, sway):
    s = sway
    B(c, T, [(470, 640), (560, 560, 700, 580, 760, 690), (790, 760, 780, 860, 740, 930),
             (720, 980 + s, 690, 1010 + s, 660, 1000), (690, 940, 700, 860, 650, 760)], fill=HR, lw=2.8)
    # nape strands
    B(c, T, [(700, 950), (720, 1000 + s, 712, 1040 + s, 690, 1060 + s), (690, 1020, 680, 990, 670, 980)], fill=HR, lw=2.4)


def face(c, T, pose):
    up = pose.get('up', 0)
    # face mask, 3/4 left. Points move slightly with 'up' (chin forward, jaw line visible longer)
    cy = lerp(0, -8, up)
    chin = lp((452, 1046), (438, 1030), up)
    jaw = lp((540, 1020), (540, 1005), up)
    segs = [(408, 690), (392, 740, 384, 790, 388, 828),   # temple/brow
            (392, 845, 396, 852, 392, 866),                 # brow ridge to eye socket
            (382, 900, 384, 930, 400, 960),                 # cheek
            (410, 990, 428, chin[1] - 10, chin[0], chin[1]),  # chin
            (470, chin[1] - 2, jaw[0] - 40, jaw[1] + 2, jaw[0], jaw[1]),
            (600, 1000, 640, 970, 655, 930), (660, 860), (640, 700)]
    B(c, T, segs, fill=SK, lw=2.8)
    # cel shadow on the far-from-sun side: right cheek toward ear + under the cheekbone
    B(c, T, [(600, 760), (622, 830, 612, 910, 590, 960), (575, 990, 548, 1012, 530, 1018),
             (560, 1015, 620, 990, 655, 930), (660, 860), (640, 700)], fill=SK_S, line=None, lw=0)
    # soft blush (flat, low alpha)
    B(c, T, [(420, 925), (440, 910, 480, 912, 500, 928), (480, 945, 440, 945, 420, 925)], fill=hexc('#e9a49a', .35), line=None, lw=0)
    # rim light on the sun-side contour
    B(c, T, [(392, 870), (383, 905, 386, 935, 401, 962), (397, 935, 393, 905, 396, 872)], fill=RIM, line=None, lw=0)
    # nose (3/4): bridge shadow + tip
    nose_tip = lp((418, 940), (414, 930), up)
    B(c, T, [(440, 870), (432, 900, 424, 925, nose_tip[0], nose_tip[1]), (426, 950), (440, 952)], fill=SK_S, line=None, lw=0)
    B(c, T, [(nose_tip[0] + 4, nose_tip[1] - 4), (nose_tip[0] - 2, nose_tip[1] + 6, 426, 950, 436, 950)], line=LN, lw=2.2, close=False)
    # mouth
    m = pose.get('mouth', 0)
    my = lerp(992, 980, up)
    if m < .15:
        B(c, T, [(446, my), (462, my + 2, 480, my + 1, 492, my - 3)], line=LN, lw=2.4, close=False)
        B(c, T, [(455, my + 14), (465, my + 17, 474, my + 16)], line=hexc('#2a1c22', .35), lw=1.6, close=False)
    else:
        o = m * 12
        B(c, T, [(446, my), (466, my - 2, 482, my - 2, 492, my - 3), (488, my + o * .6, 470, my + o, 452, my + o * .6)], fill=hexc('#6b3036'), lw=2.2)


def eye(c, T, cx, cy, w, h, blink, gaze, up, far=False):
    """anime eye: upper lid line (thick), lower lid hint, iris w/ highlight. blink 0 open .. 1 closed"""
    op = max(0.0, 1 - blink)
    h = h * (1 + .22 * up)
    lift = up * 13
    top = cy - h * .55 * op - lift * op
    bot = cy + h * .45
    l, r = cx - w / 2, cx + w / 2
    if op > .12:
        # sclera
        B(c, T, [(l, cy + 2), (l + w * .25, top + 2, r - w * .2, top, r, cy - 4), (r - w * .15, bot + 2, l + w * .3, bot + 4, l, cy + 2)], fill=EYE_W, line=None, lw=0)
        # iris (clipped to sclera)
        c.save()
        sp = T.segs([(l, cy + 2), (l + w * .25, top + 2, r - w * .2, top, r, cy - 4), (r - w * .15, bot + 2, l + w * .3, bot + 4, l, cy + 2)])
        c.move_to(*sp[0])
        for s in sp[1:]:
            c.curve_to(*s)
        c.close_path(); c.clip()
        ix, iy = T((cx + gaze[0] * w * .22 - w * .06, cy + gaze[1] * h * .2 - lift * .3))
        ir = w * (.3 if not far else .26)
        c.save(); c.translate(ix, iy); c.scale(1, 1.18)
        c.arc(0, 0, ir, 0, 6.283); c.restore()
        c.set_source_rgba(*IRIS); c.fill()
        c.save(); c.translate(ix, iy); c.scale(1, 1.18); c.arc(0, -ir * .25, ir * .55, 0, 6.283); c.restore()
        c.set_source_rgba(*IRIS_D); c.fill()
        # top lid shadow on the eyeball
        c.move_to(*sp[0]); c.curve_to(*sp[1])
        c.line_to(*T((r, top + h * .35))); c.line_to(*T((l, top + h * .35))); c.close_path()
        c.set_source_rgba(.55, .35, .35, .28 * (1 - .7 * up)); c.fill()
        # highlights
        circle(c, ix - ir * .35, iy - ir * .5, ir * .22, fill=(1, 1, 1, .95), line=None)
        circle(c, ix + ir * .35, iy + ir * .45, ir * .1, fill=(1, 1, 1, .7), line=None)
        c.restore()
        # upper lid line: thick, tapered (filled shape)
        B(c, T, [(l - 4, cy + 6), (l + w * .2, top - 2, r - w * .25, top - 4, r + 6, cy - 2),
                 (r - w * .25, top + 5, l + w * .25, top + 6, l - 4, cy + 6)], fill=LN, line=None, lw=0)
        # lower lid hint
        B(c, T, [(l + w * .35, bot + 3), (l + w * .6, bot + 4, r - w * .15, bot - 2, r - 2, cy + 6)], line=hexc('#2a1c22', .55), lw=1.8, close=False)
        # crease
        B(c, T, [(l + w * .2, top - 12), (l + w * .5, top - 20, r - w * .2, top - 16, r, cy - 14)], line=hexc('#2a1c22', .45), lw=1.6, close=False)
    else:
        # closed: lashes line curving down
        B(c, T, [(l - 4, cy + 2), (l + w * .3, cy + 10, r - w * .3, cy + 10, r + 4, cy)], line=LN, lw=4, close=False)
        B(c, T, [(l + w * .2, cy - 6), (l + w * .5, cy - 10, r - w * .2, cy - 8, r, cy - 8)], line=hexc('#2a1c22', .4), lw=1.6, close=False)


def brows(c, T, up, raise_):
    d = raise_ * 10 + up * 6
    B(c, T, [(398, 818 - d), (420, 800 - d, 446, 796 - d, 462, 804 - d), (440, 806 - d, 420, 812 - d, 398, 818 - d)], fill=HR, line=LN, lw=1.5)
    B(c, T, [(492, 806 - d), (530, 790 - d, 575, 792 - d, 600, 810 - d), (570, 804 - d, 530, 802 - d, 492, 812 - d)], fill=HR, line=LN, lw=1.5)


def glasses(c, T, up):
    # near lens (right, bigger) and far lens (left, foreshortened), thin red frames
    y = lerp(852, 846, up)
    B(c, T, [(478, y - 30), (520, y - 40, 585, y - 38, 606, y - 22), (614, y + 10, 600, y + 38, 560, y + 42), (510, y + 44, 484, y + 30, 478, y - 30)], fill=hexc('#ffffff', .06), line=GL, lw=3.4)
    B(c, T, [(398, y - 26), (418, y - 34, 444, y - 34, 458, y - 26), (462, y + 4, 456, y + 30, 436, y + 34), (412, y + 34, 398, y + 18, 398, y - 26)], fill=hexc('#ffffff', .06), line=GL, lw=3.0)
    # bridge
    B(c, T, [(458, y - 18), (466, y - 24, 472, y - 24, 478, y - 18)], line=GL, lw=3, close=False)
    # temple arm to the ear
    B(c, T, [(606, y - 20), (660, 868)], line=GL, lw=3.2, close=False)
    # lens glints (cel)
    B(c, T, [(500, y - 30), (520, y - 34), (488, y + 20), (480, y + 10)], fill=hexc('#ffffff', .22), line=None, lw=0)


def front_hair(c, T, sway, up):
    s = sway
    # main hair volume (puffs beyond the skull); bottom edge hidden under the locks
    B(c, T, [(372, 800), (340, 690, 380, 575, 480, 530), (560, 495, 680, 505, 750, 570), (800, 620, 806, 700, 780, 770),
             (750, 820, 720, 800, 700, 760), (600, 700, 480, 690, 372, 800)], fill=HR, lw=2.8)
    # locks: (root x, root y, tip x, tip y, half width, bend)
    locks = [(392, 690, 366, 862, 30, -10), (432, 680, 398, 892, 34, -14), (478, 676, 456, 900, 36, -8),
             (522, 676, 520, 868, 34, 6), (566, 676, 590, 846, 32, 12), (612, 680, 646, 820, 30, 14),
             (660, 690, 702, 800, 28, 12), (452, 690, 432, 840, 22, -6), (545, 690, 548, 820, 20, 4)]
    for i, (rx, ry, tx, ty, w, bend) in enumerate(locks):
        k = 1.0 + (i % 3) * .15
        tx2, ty2 = tx + s * .6 * k, ty + abs(s) * .2
        mx, my = (rx + tx2) / 2 + bend, (ry + ty2) / 2
        sg = [(rx - w, ry), (rx - w * .9, my - 30, mx - w * .35, my, tx2, ty2),
              (mx + w * .45, my - 10, rx + w * .8, my - 40, rx + w, ry)]
        B(c, T, sg, fill=HR, line=None, lw=0)
        B(c, T, sg, line=LN, lw=2.3, close=False)
        # inner strand line
        B(c, T, [(rx + w * .1, ry + 20), (mx + 2, my, tx2 + (rx - tx2) * .25, ty2 - (ty2 - ry) * .25)], line=hexc('#0e0d12', .55), lw=1.3, close=False)
    # side lock in front of the ear
    B(c, T, [(690, 760), (706, 830, 704 + s * .4, 900, 690 + s * .5, 960), (680, 900, 672, 830, 660, 770)], fill=HR, lw=2.3)
    # cel highlight: one crescent with a jagged lower edge (angel ring)
    B(c, T, [(418, 628), (470, 585, 560, 566, 650, 576), (700, 584, 730, 600, 748, 622),
             (738, 630), (716, 652), (704, 624), (694, 628), (668, 606), (646, 640), (630, 602), (612, 610), (590, 596),
             (560, 628), (546, 592), (530, 600), (508, 596), (482, 634), (470, 606), (452, 612), (438, 642), (430, 624)], fill=HR_HI, line=None, lw=0)
    # warm rim light on the sun-side outline
    B(c, T, [(374, 796), (344, 690, 382, 582, 478, 534), (400, 600, 372, 690, 384, 790)], fill=hexc('#8f7070'), line=None, lw=0)
    # messy tufts at the crown
    for (a0, a1, tip) in (((520, 520), (556, 512), (548, 500 + s * .2)), ((700, 552), (728, 574), (734, 548))):
        B(c, T, [a0, (a0[0] + 10, tip[1] - 6, tip[0] - 10, tip[1] - 4, tip[0], tip[1]), a1], fill=HR, lw=2.0)


def headphones(c, T, cup_off, sway):
    """band over the head; near cup on the ear. cup_off 0..1 slides it back off the ear onto the neck"""
    on = (712, 872)
    off = (770, 1010)
    cx, cy = lp(on, off, cup_off)
    ang = lerp(-0.18, 0.5, cup_off)
    # band over the crown
    top = (585, 535)
    B(c, T, [(455, 585), (510, 535, 610, 520, 680, 548), (750, 585, cx + 10, cy - 150, cx, cy - 70)], line=PH, lw=16, close=False)
    B(c, T, [(455, 585), (510, 535, 610, 520, 680, 548), (750, 585, cx + 10, cy - 150, cx, cy - 70)], line=PH_S, lw=6, close=False)
    # cup
    pc = T((cx, cy))
    c.save(); c.translate(*pc); c.rotate(ang)
    c.save(); c.scale(.72, 1); c.arc(0, 0, 78, 0, 6.283); c.restore()
    c.set_source_rgba(*PH); c.fill_preserve(); c.set_source_rgba(*LN); c.set_line_width(3); c.stroke()
    c.save(); c.scale(.5, .78); c.arc(8, 0, 78, 0, 6.283); c.restore()
    c.set_source_rgba(*PH_S); c.fill()
    # a small red logo dot? keep accent to glasses only; use grey ring
    c.save(); c.scale(.5, .78); c.arc(8, 0, 40, 0, 6.283); c.restore()
    c.set_source_rgba(.42, .41, .47, 1); c.set_line_width(3); c.stroke()
    # cable hanging down
    c.restore()
    p0 = T((cx + 10, cy + 70))
    c.move_to(*p0); c.curve_to(p0[0] + 10, p0[1] + 120, p0[0] - 60, p0[1] + 220, p0[0] - 90 + sway, 1960)
    c.set_source_rgba(*PH); c.set_line_width(4); c.stroke()


def capsule(c, p0, p1, r0, r1, fill, lw=2.2, shade=None):
    ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    pts = []
    for i in range(13):   # cap around p1 (front)
        a = ang - math.pi / 2 + math.pi * i / 12
        pts.append((p1[0] + math.cos(a) * r1, p1[1] + math.sin(a) * r1))
    for i in range(13):   # cap around p0 (back)
        a = ang + math.pi / 2 + math.pi * i / 12
        pts.append((p0[0] + math.cos(a) * r0, p0[1] + math.sin(a) * r0))
    c.new_path(); c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path()
    c.set_source_rgba(*fill); c.fill_preserve()
    if shade:
        c.save(); c.clip_preserve()
        nx, ny = -math.sin(ang), math.cos(ang)
        c.new_path()
        c.move_to(p0[0] + nx * r0 * .35, p0[1] + ny * r0 * .35); c.line_to(p1[0] + nx * r1 * .35, p1[1] + ny * r1 * .35)
        c.line_to(p1[0] + nx * r1 * 3, p1[1] + ny * r1 * 3); c.line_to(p0[0] + nx * r0 * 3, p0[1] + ny * r0 * 3); c.close_path()
        c.set_source_rgba(*shade); c.fill(); c.restore()
        c.new_path(); c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)
        c.close_path()
    c.set_source_rgba(*LN); c.set_line_width(lw); c.stroke()


def hand(c, T, u, cup):
    """fingertips curling over the earcup rim from behind (rest of the hand hidden by the cup)"""
    if u <= 0:
        return
    on, off = (712, 872), (770, 1010)
    cx, cy = lp(on, off, cup)
    ang = lerp(-0.18, 0.5, cup)
    k = min(1, u * 2.2)
    c.save(); p = T((cx, cy)); c.translate(*p); c.rotate(ang)
    # tips slide in from the back edge of the cup
    sx = lerp(70, 0, k * k * (3 - 2 * k))
    tips = [(-62, 22, 40, 11), (-56, 4, 44, 12), (-48, 30, 38, 11.5), (-38, 54, 30, 10)]
    tips = [(-6, -50, 58, 15), (-3, -18, 66, 16), (0, 14, 60, 15.5), (4, 44, 46, 13.5)]
    # back of the hand peeking out behind the cup's right edge
    bez(c, [(52 + sx, -70), (110 + sx, -80, 140 + sx, -10, 120 + sx, 80), (90 + sx, 100, 60 + sx, 80, 50 + sx, 60)], fill=SK_S, line=LN, lw=2.4)
    for (x, y, L, r) in tips:
        x0 = 58 + sx; x1 = x0 - L
        c.new_path()
        capsule(c, (x0, y), (x1 + r, y + 3), r + .5, r, SK, 2.2, SK_S)
        # nail
        c.save(); c.translate(x1 + r * 1.2, y + 2); c.scale(1, .7); c.arc(0, 0, r * .55, 0, 6.283); c.restore()
        c.set_source_rgba(*hexc('#f7e3d8')); c.fill_preserve(); c.set_source_rgba(*hexc('#2a1c22', .5)); c.set_line_width(1.2); c.stroke()
        # joint crease
        c.move_to(x1 + L * .55, y - r * .7 + 2); c.line_to(x1 + L * .55, y + r * .7 + 2)
        c.set_source_rgba(*hexc('#2a1c22', .4)); c.set_line_width(1.2); c.stroke()
    c.restore()


def draw_sam(c, pose):
    up = pose.get('up', 0)
    sway = pose.get('sway', 0)
    T = X(ang=lerp(0, -0.07, up), piv=(580, 1150), off=(0, lerp(0, -6, up)))
    body(c, pose)
    neck(c, T)
    head_back_hair(c, T, sway)
    ear(c, T)
    face(c, T, pose)
    brows(c, T, up, pose.get('brow', 0))
    eye(c, T, 430, 862, 54, 38, pose.get('blink', 0), pose.get('gaze', (0, 0)), up, far=True)
    eye(c, T, 540, 866, 84, 48, pose.get('blink', 0), pose.get('gaze', (0, 0)), up)
    glasses(c, T, up)
    front_hair(c, T, sway, up)
    headphones(c, T, pose.get('cup', 0), sway)
    hand(c, T, pose.get('hand', 0), pose.get('cup', 0))
