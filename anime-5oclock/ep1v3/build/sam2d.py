"""Sam, drawn in 2D (cairo): tapered ink line, flat cel fill, one shadow tone. No AI images, no 3D.
draw_sam(c, pose) draws a 3/4 bust facing screen-left on a 1080x1920 canvas.
pose keys: lid 0..1, gx, gy (gaze px), brow (px up), mouth 0..1, sway (px), breath (px), tilt (deg), hand 0..1
"""
import math, cairo
import numpy as np

W, H = 1080, 1920


def hx(h, a=1.0):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)) + (a,)


LW = .68
INK = hx('#1d1a22')
SKIN, SKIN_S = hx('#cfc3b6'), hx('#a3938f')
HAIR, HAIR_S, HAIR_L = hx('#2b2a33'), hx('#1c1b23'), hx('#43424f')
HOOD, HOOD_S, HOOD_D = hx('#4a4d57'), hx('#363843'), hx('#282a34')
RED, RED_S = hx('#b3262f'), hx('#741820')
BLK, BLK_S, BLK_L = hx('#24232a'), hx('#17161b'), hx('#3d3c46')


# ------------------------------------------------------------------ curves
def spline(pts, closed=False, n=14):
    """Catmull-Rom (centripetal-ish) samples through pts"""
    P = [np.array(p, float) for p in pts]
    m = len(P)
    out = []
    rng = range(m) if closed else range(m - 1)
    for i in rng:
        if closed:
            p0, p1, p2, p3 = P[(i - 1) % m], P[i], P[(i + 1) % m], P[(i + 2) % m]
        else:
            p1, p2 = P[i], P[i + 1]
            p0 = P[i - 1] if i > 0 else p1 - (p2 - p1)
            p3 = P[i + 2] if i + 2 < m else p2 + (p2 - p1)
        for k in range(n):
            t = k / n
            out.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    if not closed:
        out.append(P[-1])
    return out


def path(c, S, close=True):
    c.move_to(*S[0])
    for p in S[1:]:
        c.line_to(*p)
    if close:
        c.close_path()


def fill(c, S, col):
    path(c, S); c.set_source_rgba(*col); c.fill()


def ink(c, pts, w=4.0, a=.15, b=.15, col=INK, closed=False, smooth=True, mid=1.0):
    """brush stroke: starts at a*w, swells to w, ends at b*w"""
    if col is INK: w *= LW
    S = spline(pts, closed) if smooth else [np.array(p, float) for p in pts]
    if closed:
        S = S + [S[0]]
    n = len(S)
    L, R = [], []
    for i in range(n):
        d = S[min(i + 1, n - 1)] - S[max(i - 1, 0)]
        l = math.hypot(*d) or 1
        nrm = np.array([-d[1], d[0]]) / l
        u = i / (n - 1)
        bell = math.sin(math.pi * min(1, max(0, u))) ** .6
        ww = w * ((a * (1 - u) + b * u) * (1 - bell) + bell * mid) / 2 if not closed else w / 2
        L.append(S[i] + nrm * ww); R.append(S[i] - nrm * ww)
    fill(c, L + R[::-1], col)


def shape(c, pts, col, lw=4.0, shadow=None, sh_col=None, smooth=True, line=INK):
    S = spline(pts, True) if smooth else [np.array(p, float) for p in pts]
    fill(c, S, col)
    if shadow:
        c.save(); path(c, S); c.clip()
        for s in shadow:
            fill(c, spline(s, True), sh_col)
        c.restore()
    if lw:
        ink(c, pts, lw, closed=True, smooth=smooth, col=line)
    return S


def lock(c, root, ctrl, tip, w0, sway=0, col=HAIR, lw=3.2, shade=None, belly=1.0, wave=13, open_root=True):
    """one tapered hair lock: root -> ctrl -> tip"""
    r, k, t = [np.array(p, float) for p in (root, ctrl, tip)]
    k = k + np.array([sway * .35, 0]); t = t + np.array([sway, abs(sway) * .08])
    C = []
    for i in range(25):
        u = i / 24
        q = (1 - u) ** 2 * r + 2 * u * (1 - u) * k + u * u * t
        dd = t - r; L_ = math.hypot(*dd) or 1; nn_ = np.array([-dd[1], dd[0]]) / L_
        C.append(q + nn_ * math.sin(u * 5.2 + r[0] * .05) * wave * u)
    A, B = [], []
    for i, p in enumerate(C):
        u = i / 24
        d = C[min(i + 1, 24)] - C[max(i - 1, 0)]
        l = math.hypot(*d) or 1
        nn = np.array([-d[1], d[0]]) / l
        ww = w0 * (1 - u ** 2.2) * min(1, .35 + u * 2.6) * (.8 + .35 * math.sin(math.pi * u) * belly)
        A.append(p + nn * ww); B.append(p - nn * ww)
    fill(c, A + B[::-1], col)
    if shade is not None:
        mid = [p * .45 + q * .55 for p, q in zip(C, B)]
        fill(c, mid + B[::-1], shade)
    ink(c, A[6:], lw, .05, .6, smooth=False)
    ink(c, B[6:], lw, .05, .6, smooth=False)


# ------------------------------------------------------------------ Sam
def eye(c, cx, cy, w, h, lid, gx, gy, far=False):
    """heavy-lidded eye. w,h = half sizes"""
    top = h * (1 - lid) * .86
    out_x = cx + w if not far else cx + w * .9
    in_x = cx - w
    up = [(in_x, cy + h * .35), (cx - w * .55, cy - top * .62 + lid * h * .5), (cx + w * .1, cy - top + lid * h * .55),
          (cx + w * .65, cy - top * .72 + lid * h * .45), (out_x, cy + h * .02 + lid * h * .25)]
    lo = [(in_x, cy + h * .35), (cx - w * .4, cy + h * .62), (cx + w * .25, cy + h * .66), (out_x, cy + h * .02 + lid * h * .25)]
    U, D = spline(up), spline(lo)
    if lid < .92:
        fill(c, U + D[::-1], hx('#ddd8d0'))
        c.save(); path(c, U + D[::-1]); c.clip()
        ir = h * .78
        ix, iy = cx + gx * (.6 if far else 1) - w * .12, cy + gy + h * .02
        c.save(); c.translate(ix, iy); c.scale(.82 if not far else .66, 1.06)
        c.arc(0, 0, ir, 0, 7); c.set_source_rgba(*hx('#4a3c36')); c.fill()
        c.arc(0, 0, ir, math.pi, 2 * math.pi); c.set_source_rgba(*hx('#2a2125')); c.fill()
        c.arc(0, 0, ir * .46, 0, 7); c.set_source_rgba(*hx('#131014')); c.fill()
        c.restore()
        ink(c, [(ix + ir * .8 * math.cos(q / 10 * 6.283) * (.82 if not far else .66), iy + ir * 1.06 * math.sin(q / 10 * 6.283)) for q in range(10)], 2.4, closed=True)
        c.arc(ix - ir * .25, iy - ir * .32, ir * .17, 0, 7); c.set_source_rgba(.9, .88, .86, .95); c.fill()
        # lid shadow across the eyeball
        sh = [(p[0], p[1] + h * .30) for p in U]
        fill(c, U + sh[::-1], (.12, .10, .14, .42))
        c.restore()
    ink(c, up, 9.5 if not far else 8, .35, .55)
    # outer lash flick
    ink(c, [(cx + w * .6, cy - top * .74 + lid * h * .45), (out_x, cy + lid * h * .25), (out_x + w * .16, cy + h * .10 + lid * h * .25)], 7, .4, .05)
    ink(c, [lo[1], lo[2], (out_x - w * .12, cy + h * .34 + lid * h * .12)], 3, .05, .2)
    # eyelid crease
    ink(c, [(cx - w * .62, cy - h * .86), (cx + w * .1, cy - h * 1.22 + lid * h * .25), (cx + w * .78, cy - h * .78)], 2.8, .05, .05)


def draw_neck(c, p):
    shape(c, [(532, 900), (556, 1010), (566, 1100), (556, 1180), (520, 1300), (640, 1480), (800, 1420), (800, 1200), (752, 1090), (738, 980), (742, 860), (640, 840)],
          SKIN, 4.6, shadow=[[(500, 880), (640, 1000), (700, 900), (760, 850), (800, 1000), (770, 1120), (820, 1480), (690, 1480), (664, 1120), (592, 1060), (520, 1010)]],
          sh_col=SKIN_S)
    ink(c, [(696, 1050), (672, 1120), (640, 1190)], 3, .05, .05)
    ink(c, [(600, 1180), (592, 1200), (598, 1216)], 2.6, .1, .1)
    ink(c, [(566, 1268), (606, 1300), (640, 1330)], 3, .05, .05)


def draw_head(c, p):
    sw = p['sway']
    # ---- back hair mass
    shape(c, [(500, 372), (640, 352), (770, 408), (858, 520), (882, 660), (858, 790), (806, 884), (742, 928), (690, 900),
              (640, 760), (520, 640), (420, 500), (440, 420)], HAIR, 4.5)
    for (r, k, t, w) in [((840, 620), (905, 760), (872, 900), 34), ((800, 700), (862, 850), (806, 968), 36), ((752, 740), (792, 880), (742, 990), 34),
                         ((716, 760), (728, 880), (690, 962), 26)]:
        lock(c, r, k, t, w, sw * .5, HAIR, 3.4, HAIR_S)
    # ---- ear
    shape(c, [(688, 716), (724, 680), (760, 694), (764, 744), (744, 800), (712, 834), (690, 818)], SKIN, 4.0,
          shadow=[[(716, 706), (748, 706), (742, 770), (712, 800), (722, 750)]], sh_col=SKIN_S)
    ink(c, [(706, 716), (736, 704), (744, 742), (726, 778)], 3, .1, .1)
    # ---- face
    face = [(404, 520), (372, 600), (357, 676), (362, 728), (351, 776), (353, 826), (366, 884), (386, 938), (410, 984), (438, 1006), (478, 1003),
            (566, 958), (650, 896), (690, 832), (702, 780), (706, 690), (690, 560), (600, 470), (480, 460)]
    shape(c, face, SKIN, 0,
          shadow=[[(700, 520), (640, 610), (622, 700), (640, 800), (610, 880), (548, 944), (486, 1010), (600, 1010), (720, 900), (740, 640)],
                  [(340, 500), (500, 440), (720, 520), (716, 640), (620, 640), (520, 600), (430, 640), (362, 668)]], sh_col=SKIN_S)
    # contour: heavy at jaw, lighter on cheek, broken under the bangs
    ink(c, [(360, 660), (363, 728), (351, 776), (353, 826), (366, 884), (386, 938), (410, 984), (438, 1006), (478, 1003), (566, 958), (650, 896), (688, 836)], 5.4, .35, .25)
    # ---- nose: bridge hint, tip, nostril, small cast shadow
    ink(c, [(398, 826), (390, 836), (384, 846)], 2.6, .05, .5)
    ink(c, [(384, 842), (379, 858), (390, 868), (404, 867)], 4.2, .5, .2)
    fill(c, spline([(404, 865), (416, 861), (424, 868), (410, 872)], True), hx('#8d7c7a'))
    ink(c, [(432, 848), (438, 862), (430, 872)], 2.4, .05, .1)
    # ---- mouth
    m = p['mouth']
    if m > .05:  # parted lips
        fill(c, spline([(400, 920), (424, 918 - m * 2), (456, 922), (438, 925 + m * 11), (412, 925 + m * 11)], True), hx('#43292c'))
    ink(c, [(390, 921), (406, 918), (424, 921), (446, 922), (468, 924)], 4.2, .25, .1)
    ink(c, [(412, 946 + m * 10), (430, 949 + m * 10), (446, 945 + m * 10)], 2.8, .05, .05)
    fill(c, spline([(414, 950 + m * 10), (430, 956 + m * 10), (448, 948 + m * 10), (436, 962 + m * 10), (420, 962 + m * 10)], True), SKIN_S)
    # ---- eyes / brows
    eye(c, 556, 771, 64, 35, p['lid'], p['gx'], p['gy'])
    eye(c, 402, 769, 37, 33, p['lid'], p['gx'], p['gy'], far=True)
    by = -p['brow']
    for B in ([(486, 712 + by), (530, 697 + by), (590, 690 + by), (648, 704 + by)], [(362, 702 + by), (386, 697 + by), (430, 712 + by)]):
        ink(c, B, 19 if B[0][0] > 450 else 15, .8, .05)
    # ---- glasses (accent)
    near = [(478, 734), (486, 729), (560, 727), (640, 730), (648, 737), (646, 770), (638, 806), (630, 813), (560, 816), (494, 811), (485, 805), (478, 770)]
    far = [(358, 737), (364, 731), (400, 729), (438, 731), (443, 737), (443, 770), (438, 805), (432, 811), (402, 813), (370, 809), (364, 802), (359, 770)]
    for G in (near, far):
        S = spline(G, True)
        fill(c, S, (.86, .90, .92, .07))
        ink(c, G, 4.6, closed=True, col=RED)
    c.save(); path(c, spline(near, True)); c.clip()
    fill(c, [(592, 700), (622, 700), (566, 840), (536, 840)], (.95, .96, 1, .13)); c.restore()
    ink(c, [(443, 752), (460, 743), (478, 750)], 4.4, .7, .7, RED)
    ink(c, [(646, 748), (690, 740), (724, 737)], 4.6, .8, .4, RED)
    # ---- top hair: skull cap then bangs from a centre parting
    cap = [(398, 566), (410, 470), (462, 398), (560, 356), (676, 366), (780, 430), (846, 540), (858, 650), (800, 700), (742, 690), (718, 640), (690, 590),
           (640, 520), (560, 470), (492, 460), (446, 496)]
    shape(c, cap, HAIR, 4.6,
          shadow=[[(690, 590), (760, 560), (860, 560), (880, 720), (740, 720), (718, 640)]], sh_col=HAIR_S)
    for r, k, t, w in [((486, 430), (392, 470), (344, 700), 40), ((470, 440), (384, 560), (318, 660), 24), ((506, 420), (440, 500), (412, 640), 34),
                       ((496, 430), (420, 560), (372, 752), 20), ((500, 440), (462, 520), (446, 600), 15)]:
        lock(c, r, k, t, w, -sw * .8, HAIR, 3.4, HAIR_S)
    for r, k, t, w in [((640, 420), (800, 520), (800, 800), 46), ((600, 410), (730, 480), (752, 742), 50), ((566, 412), (668, 470), (700, 716), 44),
                       ((548, 412), (624, 490), (622, 684), 34), ((534, 414), (572, 520), (556, 662), 25), ((522, 416), (530, 500), (496, 622), 17),
                       ((580, 420), (690, 560), (668, 762), 19)]:
        lock(c, r, k, t, w, sw, HAIR, 3.4, HAIR_S)
    # interior strand lines + a few dull lights
    for q in ([(520, 380), (590, 430), (650, 540)], [(560, 372), (668, 430), (730, 560)], [(620, 368), (742, 440), (800, 570)],
              [(492, 388), (430, 460), (388, 570)]):
        ink(c, q, 2.4, .1, .05, HAIR_L)
    for q in ([(600, 398), (650, 420), (700, 470)], [(690, 404), (748, 448), (784, 510)], [(458, 430), (432, 466), (416, 516)]):
        ink(c, q, 9, .05, .05, HAIR_L)
    lock(c, (520, 400), (452, 330), (400, 392), 12, sw * .4, HAIR, 2.6, wave=3)
    lock(c, (560, 390), (560, 330), (500, 318), 9, sw * .4, HAIR, 2.6, wave=3)


def draw_phones(c, slide):
    """headphones: band over the hair, cup on the near ear; slide 0..1 = cup pulled down off the ear"""
    ink(c, [(600, 352), (690, 366), (766, 428), (800, 520), (796, 610), (768 + slide * 22, 690 + slide * 70)], 26, .2, .9, BLK)
    ink(c, [(602, 346), (694, 354), (776, 418), (814, 518), (808, 612)], 4, .1, .3)
    ink(c, [(640, 360), (694, 376), (752, 434), (784, 520)], 3, .2, .2, BLK_L)
    x, y = 742 + slide * 26, 752 + slide * 120
    c.save(); c.translate(x, y); c.rotate(math.radians(-6 + slide * 20))
    E = lambda rx, ry, ox=0, oy=0: [(ox + rx * math.cos(a / 16 * 6.283), oy + ry * math.sin(a / 16 * 6.283)) for a in range(16)]
    shape(c, E(62, 92, -14), BLK_S, 4.2)
    shape(c, E(60, 92, 10), BLK, 4.6, shadow=[E(60, 92, 34, 14)], sh_col=BLK_S)
    shape(c, E(38, 62, 14), BLK_S, 3.0)
    ink(c, [(-18, -34), (-8, -56), (14, -66)], 4, .1, .1, BLK_L)
    c.restore()


def finger(c, b, m, t, w):
    S = spline([b, m, t], n=10)
    for ww, col in ((w + 5.2, INK), (w, SKIN)):
        c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
        path(c, S, False); c.set_source_rgba(*col); c.set_line_width(ww); c.stroke()
    off = [p + np.array([w * .08, w * .30]) for p in S[2:]]
    path(c, off, False); c.set_source_rgba(*SKIN_S); c.set_line_width(w * .36); c.stroke()
    e, d = S[-1], S[-1] - S[-4]; d = d / (math.hypot(*d) or 1)
    ink(c, [e - d * w * .1 + np.array([-d[1], d[0]]) * w * .34, e + d * w * .3, e - d * w * .1 - np.array([-d[1], d[0]]) * w * .2], 2.2, .1, .1)


def draw_hand(c, ox, oy, rot, slide):
    c.save(); c.translate(26 * slide + ox, 120 * slide + oy)
    c.translate(950, 900); c.rotate(math.radians(rot)); c.translate(-950, -900)
    shape(c, [(896, 950), (940, 900), (1010, 858), (1066, 960), (1130, 1150), (1190, 1500), (1180, 1760), (1010, 1760), (985, 1400), (945, 1140)], HOOD, 5,
          shadow=[[(896, 950), (960, 1010), (1010, 1200), (1050, 1500), (1060, 1780), (980, 1780), (960, 1300)]], sh_col=HOOD_S)
    for q in ([(918, 985), (980, 940), (1040, 902)], [(960, 1120), (1020, 1100), (1070, 1110)], [(985, 1230), (1060, 1180), (1120, 1180)]):
        ink(c, q, 3.6, .1, .05)
    finger(c, (884, 884), (834, 890), (786, 858), 34)
    shape(c, [(832, 694), (874, 690), (926, 752), (972, 828), (1000, 872), (930, 934), (884, 896), (850, 846)], SKIN, 4.2,
          shadow=[[(850, 800), (900, 830), (950, 900), (930, 940), (880, 900), (846, 850)]], sh_col=SKIN_S)
    for b, m, t, w in (((852, 812), (812, 796), (764, 806), 27), ((858, 780), (810, 752), (750, 766), 31), ((854, 746), (806, 708), (744, 722), 32), ((846, 712), (800, 668), (746, 682), 30)):
        finger(c, b, m, t, w)
    fill(c, spline([(848, 704), (880, 716), (900, 800), (872, 822), (852, 800)], True), SKIN)
    for q in ([(866, 716), (880, 712)], [(874, 750), (890, 748)], [(876, 786), (890, 786)]):
        ink(c, q, 2.4, .2, .05, smooth=False)
    c.restore()


def draw_body(c, p, part):
    br = p['breath']
    if part == 'back':
        return draw_hood_back(c)
    _front(c, br)


def draw_hood_back(c):
    # hood bunched behind the neck
    shape(c, [(640, 1200), (720, 1130), (820, 1076), (926, 1100), (990, 1190), (986, 1300), (900, 1370), (760, 1390), (620, 1330)], HOOD_S, 5,
          shadow=[[(720, 1140), (840, 1110), (930, 1180), (960, 1300), (860, 1370), (740, 1380), (800, 1250)]], sh_col=HOOD_D)
    for q in ([(760, 1120), (862, 1150), (922, 1230), (924, 1320)], [(718, 1150), (800, 1190), (850, 1280), (836, 1360)], [(880, 1094), (950, 1160), (966, 1240)]):
        ink(c, q, 4, .1, .1)


def _front(c, br):
    # torso
    body = [(452, 1276 - br), (500, 1250 - br), (552, 1370 - br), (640, 1440 - br), (740, 1420 - br), (822, 1290 - br), (902, 1334 - br * .8), (1010, 1410 - br * .6), (1100, 1520), (1140, 1980),
            (90, 1980), (130, 1740), (176, 1560), (262, 1420 - br * .6), (360, 1330 - br * .8)]
    shape(c, body, HOOD, 5.4,
          shadow=[[(1010, 1400), (930, 1500), (900, 1650), (930, 1800), (900, 1990), (1200, 1990), (1180, 1460)],
                  [(560, 1330), (640, 1400), (740, 1372), (812, 1290), (860, 1340), (800, 1460), (690, 1520), (560, 1480), (500, 1380), (490, 1290)],
                  [(176, 1570), (240, 1600), (262, 1750), (230, 1990), (60, 1990), (110, 1740)]], sh_col=HOOD_S)
    # hood collar edge, front V
    shape(c, [(470, 1256 - br), (528, 1208 - br), (560, 1290 - br), (628, 1372 - br), (690, 1430 - br), (640, 1476 - br), (560, 1410 - br), (496, 1334 - br)], HOOD, 4.6,
          shadow=[[(540, 1260), (628, 1372), (690, 1430), (650, 1470), (600, 1400), (548, 1330)]], sh_col=HOOD_S)
    shape(c, [(690, 1430 - br), (752, 1386 - br), (800, 1310 - br), (822, 1220 - br), (872, 1262 - br), (860, 1360 - br), (800, 1440 - br), (720, 1490 - br), (650, 1480 - br)], HOOD, 4.6,
          shadow=[[(700, 1440), (772, 1400), (826, 1300), (870, 1270), (860, 1360), (790, 1450), (700, 1490)]], sh_col=HOOD_S)
    # folds
    for q, w in [([(900, 1400), (870, 1500), (890, 1620)], 4.6), ([(960, 1500), (900, 1580), (880, 1700), (900, 1820)], 4), ([(300, 1440), (330, 1540), (310, 1660)], 4.4),
                 ([(236, 1560), (280, 1640), (286, 1780)], 4), ([(660, 1500), (640, 1640), (668, 1800)], 3), ([(420, 1330), (400, 1400), (420, 1470)], 3.4),
                 ([(860, 1660), (800, 1740), (700, 1790)], 3.4), ([(320, 1700), (420, 1760), (520, 1770)], 3.2)]:
        ink(c, q, w, .1, .05)
    # drawstrings
    for x0, y0, x1, y1 in ((612, 1440, 596, 1690), (716, 1476, 724, 1720)):
        q = [(x0, y0 - br), ((x0 + x1) / 2 - 8, (y0 + y1) / 2 - br), (x1, y1 - br)]
        ink(c, q, 13, .9, .9); ink(c, q, 8, .9, .9, hx('#a9a49b'))
        ink(c, [(x1, y1 - br), (x1 - 1, y1 + 34 - br)], 14, 1, 1, smooth=False); ink(c, [(x1, y1 + 2 - br), (x1 - 1, y1 + 32 - br)], 9, 1, 1, hx('#77726c'), smooth=False)


POSE = dict(lid=.28, gx=-14, gy=6, brow=0, mouth=0.0, sway=0.0, breath=0.0, tilt=0.0, slide=0.0, hand=None)


def draw_sam(c, pose=None):
    p = dict(POSE); p.update(pose or {})
    hb = draw_body(c, p, 'back')
    c.save(); c.translate(0, 62); draw_neck(c, p); c.restore()
    draw_body(c, p, 'front')
    c.save()
    c.translate(660, 1162); c.rotate(math.radians(p['tilt'])); c.translate(-660, -1100 - p['breath'] * .5)
    draw_head(c, p)
    draw_phones(c, p['slide'])
    if p['hand'] is not None: draw_hand(c, *p['hand'], p['slide'])
    c.restore()


if __name__ == '__main__':
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    c.set_source_rgb(.5, .55, .56); c.paint()
    draw_sam(c)
    import sys
    s.write_to_png(sys.argv[1])
