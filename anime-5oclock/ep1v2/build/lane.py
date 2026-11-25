"""Kiriyama lane at 16:59 (day) and the same lane at night. Drawn in vector with a pinhole camera."""
import math, random
from lib import *

DAY = dict(
    sky=[(0, '#9aa3c0'), (.35, '#d8adA0'), (.7, '#f4bf8e'), (1, '#fde0b0')],
    glow='#fff2d8', mtn_far='#a7a3b8', mtn_near='#857f9c', tower='#4b4660',
    wall_l='#eed5b2', wall_s='#a596a6', roof_l='#5d6476', roof_s='#424859', roof_line='#2d2b38',
    block_l='#d4c4ad', block_s='#8e8597', road_l='#988a8c', road_s='#6a6176', edge='#ece4d6',
    pole_l='#c2b4a3', pole_s='#81778a', win='#6f7894', win_lit=None, wire='#3b3340',
    line='#2e2128', bgline='#5f4d57', vend='#e8eef0', vend_glow=None, green='#7d8c66', green_s='#56604f',
    light=None, star=False)
NIGHT = dict(
    sky=[(0, '#050a1a'), (.6, '#0d1a35'), (.9, '#1a2a4c'), (1, '#243556')],
    glow='#2b3c60', mtn_far='#121c33', mtn_near='#0d1528', tower='#0a1020',
    wall_l='#2a3550', wall_s='#1a2238', roof_l='#151d31', roof_s='#0f1526', roof_line='#070b14',
    block_l='#26304a', block_s='#171f33', road_l='#1f2840', road_s='#141b2d', edge='#5a6680',
    pole_l='#2c3650', pole_s='#1a2135', win='#05080f', win_lit=None, wire='#05070d',
    line='#060912', bgline='#0b1120', vend='#dff3ff', vend_glow='#bfe8ff', green='#16241e', green_s='#0e1814',
    light='#dff4e6', star=True)


def C(p, k, a=1.0):
    return hexc(p[k], a)


def sky(c, p, horizon):
    g = cairo.LinearGradient(0, 0, 0, horizon)
    for o, col in p['sky']:
        g.add_color_stop_rgb(o, *hexc(col)[:3])
    c.set_source(g); c.rectangle(0, 0, W, horizon + 40); c.fill()
    if not p['star']:
        # sun glow low on the left, behind houses
        rg = cairo.RadialGradient(150, horizon - 60, 10, 150, horizon - 60, 700)
        rg.add_color_stop_rgba(0, *hexc(p['glow'])[:3], .95)
        rg.add_color_stop_rgba(.25, *hexc(p['glow'])[:3], .45)
        rg.add_color_stop_rgba(1, *hexc(p['glow'])[:3], 0)
        c.set_source(rg); c.rectangle(0, 0, W, horizon + 40); c.fill()
        # flat painted cloud bands (cel, two tones)
        for (x, y, w, h, col) in [(-80, 300, 620, 46, '#e9c3ad'), (380, 250, 520, 34, '#e3bcab'),
                                   (640, 470, 600, 40, '#efcaa9'), (-40, 560, 420, 28, '#f3d2ae'),
                                   (120, 160, 380, 22, '#c4b3b9')]:
            bez(c, [(x, y + h), (x + w * .1, y + h * .2, x + w * .2, y, x + w * .35, y + h * .25),
                    (x + w * .5, y - h * .3, x + w * .7, y, x + w * .8, y + h * .3),
                    (x + w * .9, y + h * .3, x + w, y + h * .7, x + w, y + h)],
                fill=hexc(col, .85), line=None, lw=0)
    else:
        rnd = random.Random(5)
        for i in range(260):
            x, y = rnd.uniform(0, W), rnd.uniform(0, horizon * .85)
            r = rnd.choice([.6, .8, 1, 1.2, 1.8])
            circle(c, x, y, r, fill=(1, 1, .95, rnd.uniform(.35, .9)), line=None)


def mountains(c, p, hz, t):
    rnd = random.Random(3)
    def ridge(base, amp, seed, col):
        r = random.Random(seed)
        pts = [(-20, hz + 30)]
        x = -20
        y = base
        while x < W + 40:
            pts.append((x, y))
            x += r.uniform(30, 70)
            y = base - amp * (0.5 + 0.5 * math.sin(x / 210 + seed)) - r.uniform(0, amp * .25)
        pts += [(W + 40, hz + 30)]
        poly(c, pts, fill=hexc(p[col]), line=None, lw=0, boil=False)
    ridge(hz - 150, 180, 1, 'mtn_far')
    # big near hill at the end of the lane carrying the tower
    pts=[(-20,hz+30)]
    for i in range(0,41):
        x=-20+i*(W+40)/40
        d=(x-560)/330
        pts.append((x, hz-40-170*math.exp(-d*d)-8*math.sin(x/37)))
    pts.append((W+40,hz+30))
    poly(c, pts, fill=hexc(p['mtn_near']), line=None, lw=0, boil=False)
    # the 1964 radio tower on the ridge (story object)
    tx, ty, th = 548, hz - 205, 150
    col = hexc(p['tower'])
    c.set_line_width(2.2)
    for s in (-1, 1):
        line(c, (tx + s * 26, ty + th * .1), (tx + s * 3, ty - th), col, 2.4)
    for k in range(9):
        y = ty + th * .1 - k * th * 1.1 / 9
        w = 26 * (1 - k / 9.5)
        line(c, (tx - w, y), (tx + w, y), col, 1.3)
        y2 = y - th * 1.1 / 9
        w2 = 26 * (1 - (k + 1) / 9.5)
        line(c, (tx - w, y), (tx + w2, y2), col, 1.0)
        line(c, (tx + w, y), (tx - w2, y2), col, 1.0)
    # aviation light: blinks
    on = (t % 1.6) < .8
    if on:
        for r, a in ((26, .18), (12, .4), (4, 1)):
            circle(c, tx, ty - th - 4, r, fill=(.95, .2, .15, a), line=None)
    else:
        circle(c, tx, ty - th - 4, 3.2, fill=(.35, .1, .1, 1), line=None)


def house(c, cam, p, xa, xb, z1, z2, h, rh, ridge='z', seed=0, lit_side=True):
    """xa = road-facing x. lit_side: road face lit (right side of street faces the sun)."""
    rnd = random.Random(seed)
    L = hexc(p['line']) if z1 < 14 else hexc(p['bgline'])
    lw = max(1.0, 2.6 * 8 / z1)
    face_col = C(p, 'wall_l' if lit_side else 'wall_s')
    front_col = C(p, 'wall_s')
    P = cam.p
    # front (camera facing) face
    poly(c, [P(xb, 0, z1), P(xa, 0, z1), P(xa, h, z1), P(xb, h, z1)], fill=front_col, line=L, lw=lw)
    # road face
    poly(c, [P(xa, 0, z1), P(xa, 0, z2), P(xa, h, z2), P(xa, h, z1)], fill=face_col, line=L, lw=lw)
    # windows on road face
    nwin = max(1, int((z2 - z1) / 3.2))
    for k in range(nwin):
        za = z1 + (k + .3) * (z2 - z1) / nwin
        zb = za + (z2 - z1) / nwin * .45
        for (ya, yb) in ((1.0, 2.1), (h * .6, h * .6 + 1.05)):
            if ya + .3 > h:
                continue
            q = [P(xa, ya, za), P(xa, ya, zb), P(xa, yb, zb), P(xa, yb, za)]
            poly(c, q, fill=C(p, 'win'), line=L, lw=lw * .7)
            if p['win_lit'] is None and not p['star']:
                # sky reflection streak (cel)
                q2 = [P(xa, yb - .25, za + .05), P(xa, yb - .25, zb), P(xa, yb, zb), P(xa, yb, za + .05)]
                poly(c, q2, fill=hexc('#c9b7b6', .8), line=None, lw=0)
            # sill
            line(c, P(xa, ya - .05, za - .1), P(xa, ya - .05, zb + .1), L, lw * .6)
        # AC unit / laundry pole details
        if rnd.random() < .5:
            yy = h * .6 - .1
            q = [P(xa + (.01 if xa > 0 else -.01), yy - .6, zb + .3), P(xa, yy - .6, zb + .9), P(xa, yy, zb + .9), P(xa, yy, zb + .3)]
            poly(c, q, fill=hexc(p['edge']) if not p['star'] else C(p, 'wall_s'), line=L, lw=lw * .6)
    # roof
    o = .45
    if ridge == 'z':
        xm = (xa + xb) / 2
        road_plane = [P(xa + (o if xa < xb else -o), h - .15, z1 - o), P(xa + (o if xa < xb else -o), h - .15, z2 + o),
                      P(xm, h + rh, z2 + o), P(xm, h + rh, z1 - o)]
        # fix overhang direction: eave goes toward the road
        dx = -o if xb < xa else o
        road_plane = [P(xa + (-dx) * 0 - (o if xb > xa else -o), h - .15, z1 - o),
                      P(xa - (o if xb > xa else -o), h - .15, z2 + o),
                      P(xm, h + rh, z2 + o), P(xm, h + rh, z1 - o)]
        gable = [P(xb + (o if xb > xa else -o), h - .15, z1 - o), P(xa - (o if xb > xa else -o), h - .15, z1 - o), P(xm, h + rh, z1 - o)]
        poly(c, [P(xb, h, z1), P(xa, h, z1), P(xm, h + rh * .92, z1)], fill=front_col, line=L, lw=lw)
        poly(c, road_plane, fill=C(p, 'roof_l' if lit_side else 'roof_s'), line=hexc(p['roof_line']), lw=lw)
        # tile rows
        for k in range(1, 6):
            u = k / 6
            a = P(xa + (xm - xa) * u, h + rh * u, z1 - o)
            b = P(xa + (xm - xa) * u, h + rh * u, z2 + o)
            line(c, a, b, hexc(p['roof_line'], .55), lw * .45)
        # gable edge trim
        poly(c, gable, fill=None, line=hexc(p['roof_line']), lw=lw * 1.4, close=False)
    else:
        # ridge along x: road face gets a gable
        zm = (z1 + z2) / 2
        poly(c, [P(xa, h, z1), P(xa, h, z2), P(xa, h + rh, zm)], fill=face_col, line=L, lw=lw)
        front_roof = [P(xa - (o if xb > xa else -o), h - .1, z1 - o), P(xb + (o if xb > xa else -o), h - .1, z1 - o),
                      P(xb + (o if xb > xa else -o), h + rh, zm), P(xa - (o if xb > xa else -o), h + rh, zm)]
        poly(c, front_roof, fill=C(p, 'roof_s'), line=hexc(p['roof_line']), lw=lw)
        poly(c, [P(xa - (o if xb > xa else -o), h - .1, z1 - o), P(xa - (o if xb > xa else -o), h + rh, zm),
                 P(xa - (o if xb > xa else -o), h - .1, z2 + o)], fill=None, line=hexc(p['roof_line']), lw=lw * 1.5, close=False)


def wall(c, cam, p, x, z1, z2, h=1.5, lit=True, cap=True):
    P = cam.p
    L = hexc(p['line']) if z1 < 14 else hexc(p['bgline'])
    lw = max(.9, 2.4 * 6 / max(z1, 2))
    poly(c, [P(x, 0, z1), P(x, 0, z2), P(x, h, z2), P(x, h, z1)], fill=C(p, 'block_l' if lit else 'block_s'), line=L, lw=lw)
    # block courses
    for k in range(1, 8):
        y = h * k / 8
        line(c, P(x, y, z1), P(x, y, z2), hexc(p['line'], .25 if z1 < 14 else .15), lw * .4)
    zz = z1
    k = 0
    while zz < z2:
        for r in range(8):
            y0, y1 = h * r / 8, h * (r + 1) / 8
            zj = zz + (.2 if r % 2 else 0)
            if z1 < zj < z2:
                line(c, P(x, y0, zj), P(x, y1, zj), hexc(p['line'], .18), lw * .35)
        zz += .4
        if zz > z1 + 30:
            break
    # top cap
    line(c, P(x, h, z1), P(x, h, z2), L, lw * 1.2)


def pole(c, cam, p, x, z, t, hgt=9.5, lamp=False, wires_to=None):
    P = cam.p
    L = hexc(p['line']) if z < 14 else hexc(p['bgline'])
    r = .16
    lw = max(1, 2.6 * 6 / z)
    poly(c, [P(x - r, 0, z), P(x + r, 0, z), P(x + r * .7, hgt, z), P(x - r * .7, hgt, z)], fill=C(p, 'pole_l'), line=L, lw=lw)
    poly(c, [P(x + r * .1, 0, z), P(x + r, 0, z), P(x + r * .7, hgt, z), P(x + r * .05, hgt, z)], fill=C(p, 'pole_s'), line=None, lw=0)
    # climbing steps
    for k in range(6):
        y = 2.2 + k * .55
        s = -1 if k % 2 else 1
        line(c, P(x + s * r * .8, y, z), P(x + s * (r + .28), y, z), L, lw * .6)
    # crossarm + insulators
    arm = [(x - 1.1, hgt - .55), (x + .9, hgt - .55)]
    poly(c, [P(arm[0][0], arm[0][1], z), P(arm[1][0], arm[1][1], z), P(arm[1][0], arm[1][1] - .14, z), P(arm[0][0], arm[0][1] - .14, z)],
         fill=C(p, 'pole_s'), line=L, lw=lw * .8)
    for ix in (-0.95, -0.2, .75):
        q = P(x + ix, hgt - .45, z)
        circle(c, q[0], q[1], max(1.2, 4.5 * 6 / z), fill=hexc(p['edge']), line=L, lw=lw * .5)
    # transformer
    if z < 30:
        q0, q1 = P(x - .55, hgt - 2.6, z), P(x - .2, hgt - 1.5, z)
        poly(c, [q0, (q1[0], q0[1]), q1, (q0[0], q1[1])], fill=C(p, 'pole_l'), line=L, lw=lw * .8)
    if lamp:
        a, b = P(x, hgt - 3.0, z), P(x - 1.3, hgt - 2.8, z)
        line(c, a, b, L, lw * .9)
        q = P(x - 1.35, hgt - 2.95, z)
        rr = max(2, 10 * 6 / z)
        poly(c, [(q[0] - rr * 1.4, q[1] - rr * .3), (q[0] + rr * 1.4, q[1] - rr * .3), (q[0] + rr, q[1] + rr * .4), (q[0] - rr, q[1] + rr * .4)],
             fill=C(p, 'pole_s'), line=L, lw=lw * .6)
    return [P(x + ix, hgt - .45, z) for ix in (-0.95, -0.2, .75)]


def vending(c, cam, p, x, z, t, flick=1.0):
    P = cam.p
    L = hexc(p['line'])
    w, d, h = .95, .75, 1.85
    lw = 2.4 * 6 / z
    front = [P(x, 0, z), P(x, 0, z + w), P(x, h, z + w), P(x, h, z)]
    poly(c, [P(x - d, 0, z), P(x, 0, z), P(x, h, z), P(x - d, h, z)], fill=hexc('#b23a2e' if not p['star'] else '#3a1416'), line=L, lw=lw)
    poly(c, front, fill=hexc('#c8473a' if not p['star'] else '#4a1a1c'), line=L, lw=lw)
    # display window with drinks
    a, b = .95, 1.7
    win = [P(x + .01, a, z + .08), P(x + .01, a, z + w - .08), P(x + .01, b, z + w - .08), P(x + .01, b, z + .08)]
    poly(c, win, fill=hexc(p['vend'], 1 if not p['star'] else flick), line=L, lw=lw * .6)
    cols = ['#3d6fb0', '#e0a23a', '#6aa04f', '#d2d2c8', '#9b3d6b', '#4d4d4d']
    for row in range(3):
        for k in range(6):
            zz = z + .12 + k * (w - .24) / 6
            yy = a + .07 + row * .24
            q = [P(x + .01, yy, zz + .02), P(x + .01, yy, zz + .1), P(x + .01, yy + .17, zz + .1), P(x + .01, yy + .17, zz + .02)]
            cc = hexc(cols[(k + row * 2) % 6], 1 if not p['star'] else .55 * flick)
            poly(c, q, fill=cc, line=None, lw=0)
    # buttons strip + slot
    poly(c, [P(x + .01, .78, z + .1), P(x + .01, .78, z + w - .1), P(x + .01, .9, z + w - .1), P(x + .01, .9, z + .1)], fill=hexc('#2a2a2e'), line=None, lw=0)
    poly(c, [P(x + .01, .18, z + .25), P(x + .01, .18, z + w - .25), P(x + .01, .38, z + w - .25), P(x + .01, .38, z + .25)], fill=hexc('#1c1c22'), line=L, lw=lw * .5)


def scene(p, t, cam=None, people=None):
    """returns (fg_list) drawn into separate depth layers for DOF: far, mid, near (numpy RGBA)"""
    cam = cam or Cam()
    hz = cam.cy
    layers = []
    # FAR: sky + mountains + houses beyond 20 m
    s, c = surface()
    sky(c, p, hz)
    mountains(c, p, hz, t)
    _street(c, cam, p, t, zmin=22, zmax=140)
    layers.append(to_np(s))
    s, c = surface()
    _street(c, cam, p, t, zmin=0.5, zmax=22)
    layers.append(to_np(s))
    return layers


def _road(c, cam, p, zmin, zmax):
    P = cam.p
    z0, z1 = max(zmin, 1.2), zmax
    poly(c, [P(-14, 0, z0), P(14, 0, z0), P(14, 0, z1), P(-14, 0, z1)], fill=C(p, 'block_s'), line=None, lw=0, boil=False)
    poly(c, [P(-2.3, 0, z0), P(2.3, 0, z0), P(2.3, 0, z1), P(-2.3, 0, z1)], fill=C(p, 'road_l'), line=None, lw=0, boil=False)
    # stop line + manhole near camera
    if zmin < 6:
        poly(c, [P(-2.0, 0, 4.2), P(0.1, 0, 4.2), P(0.1, 0, 4.55), P(-2.0, 0, 4.55)], fill=C(p, 'edge', .85), line=None, lw=0, boil=False)
        m = [P(.9 + .45 * math.cos(a / 20 * 6.283), 0, 7.0 + .45 * math.sin(a / 20 * 6.283)) for a in range(20)]
        poly(c, m, fill=hexc('#5b5560' if not p['star'] else '#10172a'), line=hexc(p['line'], .7), lw=1.6, boil=False)
    # long shadow of the left wall/houses falling across the left of the road (sun low on the left)
    if not p['star']:
        poly(c, [P(-2.3, 0, z0), P(-0.9, 0, z0), P(-1.2, 0, z1), P(-2.3, 0, z1)], fill=C(p, 'road_s', .85), line=None, lw=0, boil=False)
    # edge lines
    for x in (-2.0, 2.0):
        poly(c, [P(x - .07, 0, z0), P(x + .07, 0, z0), P(x + .07, 0, z1), P(x - .07, 0, z1)], fill=C(p, 'edge', .9), line=None, lw=0, boil=False)
    # gutter grates right
    for z in range(int(z0) + 1, int(min(z1, 40)), 3):
        poly(c, [P(2.1, 0, z), P(2.3, 0, z), P(2.3, 0, z + 1.2), P(2.1, 0, z + 1.2)], fill=hexc('#55505e' if not p['star'] else '#0c111d'), line=None, lw=0, boil=False)
    # asphalt patches / cracks (cel)
    rnd = random.Random(11)
    for i in range(14):
        z = rnd.uniform(z0 + .5, min(z1, 30))
        x = rnd.uniform(-1.6, 1.6)
        q = [P(x, 0, z), P(x + rnd.uniform(.4, 1.2), 0, z + rnd.uniform(-.3, .3)), P(x + rnd.uniform(.3, .9), 0, z + rnd.uniform(.6, 1.8)), P(x - .2, 0, z + 1)]
        poly(c, q, fill=C(p, 'road_s', .35), line=None, lw=0, boil=False)


def _street(c, cam, p, t, zmin, zmax):
    """draw everything whose depth is in [zmin, zmax), far to near"""
    P = cam.p
    # objects: (z_sort, fn)
    items = []
    items.append((1e9, lambda: _road(c, cam, p, zmin, zmax)))
    # left houses & walls (shadow side faces road)
    zs = [(3.0, 9.0, 6.4, 2.2, 'z'), (10.0, 15.0, 5.8, 2.6, 'x'), (16.5, 23.0, 6.6, 2.0, 'z'), (24.0, 30.0, 6.0, 2.5, 'x'),
          (31.0, 38.0, 6.8, 2.0, 'z'), (39.0, 46.0, 6.0, 2.4, 'x'), (47.0, 55.0, 6.5, 2.0, 'z'), (56.0, 66.0, 7.2, 2.4, 'x'),
          (68.0, 80.0, 6.4, 2.0, 'z'), (82.0, 96.0, 6.2, 2.3, 'z')]
    for i, (z1, z2, h, rh, rg) in enumerate(zs):
        if zmin <= z1 < zmax:
            items.append((z1 + .5, lambda z1=z1, z2=z2, h=h, rh=rh, rg=rg, i=i: house(c, cam, p, -3.4, -10, z1, z2, h, rh, rg, seed=i, lit_side=False)))
    # right houses (lit faces)
    zs2 = [(9.0, 16.0, 6.2, 2.3, 'x'), (17.0, 25.0, 6.8, 2.0, 'z'), (26.0, 33.0, 6.0, 2.6, 'x'), (34.0, 42.0, 7.0, 2.0, 'z'),
           (43.0, 50.0, 6.2, 2.4, 'x'), (51.0, 60.0, 6.6, 2.0, 'z'), (61.0, 72.0, 6.0, 2.5, 'x'), (74.0, 88.0, 6.8, 2.1, 'z')]
    for i, (z1, z2, h, rh, rg) in enumerate(zs2):
        if zmin <= z1 < zmax:
            items.append((z1 + .5, lambda z1=z1, z2=z2, h=h, rh=rh, rg=rg, i=i: house(c, cam, p, 3.6, 10, z1, z2, h, rh, rg, seed=20 + i, lit_side=True)))
    # block walls
    for (x, lit, segs) in ((-2.45, False, [(1.0, 9.6), (10.6, 30), (30.8, 60), (61, 100)]), (2.5, True, [(1.0, 8.6), (9.4, 33), (33.8, 60), (61, 100)])):
        for (z1, z2) in segs:
            if zmin <= z1 < zmax:
                items.append((z1 + .2, lambda x=x, z1=z1, z2=z2, lit=lit: wall(c, cam, p, x, z1, z2, 1.5, lit)))
    # vending machine at the left wall gap (z 9.6-10.6)
    if zmin <= 9.7 < zmax:
        items.append((9.65, lambda: vending(c, cam, p, -2.4, 9.65, t, _flick(t))))
    # trees/garden shrubs peeking over walls
    for (x, z, r) in ((-2.9, 6.0, 1.6), (-3.1, 19.0, 2.0), (3.0, 28.0, 1.8), (-3.0, 42.0, 2.2), (3.1, 55.0, 2.1)):
        if zmin <= z < zmax:
            items.append((z + .1, lambda x=x, z=z, r=r: _shrub(c, cam, p, x, z, r)))
    # poles on right
    pole_tops = {}
    for z in (7.5, 19.5, 31.5, 43.5, 55.5, 67.5, 79.5, 91.5):
        if zmin <= z < zmax:
            items.append((z - .3, lambda z=z: pole_tops.__setitem__(z, pole(c, cam, p, 2.75, z, t, lamp=True))))
    if p['light']:
        for z in (7.5, 19.5, 31.5, 43.5, 55.5, 67.5, 79.5, 91.5):
            if zmin <= z < zmax:
                items.append((z - .2, lambda z=z: _pool(c, cam, p, z, t)))
    items.sort(key=lambda it: -it[0])
    for _, fn in items:
        fn()
    # wires between consecutive poles (only when both in this band or the near one is)
    zs_all = (7.5, 19.5, 31.5, 43.5, 55.5, 67.5, 79.5, 91.5)
    for a, b in zip(zs_all[:-1], zs_all[1:]):
        if not (zmin <= a < zmax):
            continue
        for k, ix in enumerate((-0.95, -0.2, .75)):
            pa, pb = cam.p(2.75 + ix, 9.05, a), cam.p(2.75 + ix, 9.05, b)
            sw = math.sin(t * 1.3 + k) * 2
            sag(c, pa, pb, 18 * 8 / a + sw, hexc(p['wire']), max(.8, 2.0 * 8 / a))
    # wires crossing the street to left houses
    for z in (7.5, 19.5, 31.5):
        if zmin <= z < zmax:
            pa = cam.p(2.75, 8.2, z)
            pb = cam.p(-3.6, 5.6, z + 2.5)
            sag(c, pa, pb, 25 * 8 / z + math.sin(t * 1.1 + z) * 2, hexc(p['wire']), max(.8, 1.7 * 8 / z))


def _flick(t):
    # vending machine fluorescent: mostly steady, rare stutter
    ph = (t * 24) % 97
    return .55 if 40 < ph < 42 or 44 < ph < 45 else 1.0


def _shrub(c, cam, p, x, z, r):
    P = cam.p
    cx, cy = P(x, 1.5 + r * .7, z)
    rad = r * cam.f / z * .55
    rnd = random.Random(int(z * 10))
    pts = []
    n = 14
    for i in range(n):
        a = i / n * 2 * math.pi
        rr = rad * rnd.uniform(.82, 1.08)
        pts.append((cx + math.cos(a) * rr * 1.1, cy + math.sin(a) * rr * .8))
    poly(c, pts, fill=C(p, 'green'), line=hexc(p['bgline'] if z > 14 else p['line']), lw=max(1, 2.2 * 6 / z))
    # shadow half
    pts2 = [q for q in pts if q[0] > cx - rad * .1]
    if len(pts2) > 3:
        poly(c, pts2, fill=C(p, 'green_s', .8), line=None, lw=0)


def lamp_on(z, t):
    # one lamp (z=19.5) dies and stutters; others steady
    if abs(z - 19.5) < .1:
        ph = (t * 24) % 53
        return 0.0 if (8 < ph < 11 or 14 < ph < 15 or 30 < ph < 34) else 1.0
    return 1.0


def _pool(c, cam, p, z, t):
    on = lamp_on(z, t)
    if on <= 0:
        return
    P = cam.p
    col = hexc(p['light'])[:3]
    cx, cy = P(1.4, 0, z + .3)
    rx = 2.6 * cam.f / z
    c.save(); c.translate(cx, cy); c.scale(1, .22)
    rg = cairo.RadialGradient(0, 0, 0, 0, 0, rx)
    rg.add_color_stop_rgba(0, *col, .55 * on); rg.add_color_stop_rgba(.55, *col, .22 * on); rg.add_color_stop_rgba(1, *col, 0)
    c.set_source(rg); c.arc(0, 0, rx, 0, 6.283); c.fill(); c.restore()
    q = P(2.75 - 1.35, 9.5 - 2.95, z)
    r = 60 * 7 / z
    rg = cairo.RadialGradient(q[0], q[1] + 2, 0, q[0], q[1] + 2, r)
    rg.add_color_stop_rgba(0, 1, 1, 1, 1 * on); rg.add_color_stop_rgba(.15, *col, .7 * on); rg.add_color_stop_rgba(1, *col, 0)
    c.set_source(rg); c.arc(q[0], q[1] + 2, r, 0, 6.283); c.fill()
