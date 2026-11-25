"""Story poster (1080x1920) styled as a Blender workspace: hero render in a camera-view viewport, node editor,
image editor, outliner, dope sheet. No text. usage: python3 poster.py hero.png side.png thumb.png out.png"""
import sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from look import lens, W as LW, H as LH

S = 2                                  # supersample for clean lines
WW, HH = 1080 * S, 1920 * S
BG, PANEL, HEAD, LINE = (24, 24, 24), (40, 40, 40), (48, 48, 48), (30, 30, 30)
WIRE, SEL, BLUE = (115, 115, 115), (255, 160, 40), (71, 114, 179)

def s(*v): return [int(x * S) for x in v]

def fit(img, w, h, fy=.5):
    r = max(w / img.width, h / img.height); im = img.resize((int(img.width * r + .5), int(img.height * r + .5)), Image.LANCZOS)
    x = (im.width - w) // 2; y = int((im.height - h) * fy); return im.crop((x, y, x + w, y + h))

def graded(p):
    im = Image.open(p).convert('RGB')
    im = lens(im.resize((LW, LH), Image.LANCZOS))
    return im

def panel(d, x0, y0, x1, y1, header=True):
    d.rounded_rectangle(s(x0, y0, x1, y1), radius=7 * S, fill=PANEL)
    if header:
        d.rounded_rectangle(s(x0, y0, x1, y0 + 26), radius=7 * S, fill=HEAD); d.rectangle(s(x0, y0 + 16, x1, y0 + 26), fill=HEAD)
        # editor-type icon + a few dropdown pills (no words)
        d.rounded_rectangle(s(x0 + 8, y0 + 6, x0 + 30, y0 + 20), radius=3 * S, fill=(62, 62, 62))
        for k, w in enumerate((34, 28, 40)):
            xx = x0 + 40 + sum((34, 28, 40)[:k]) + k * 8
            d.rounded_rectangle(s(xx, y0 + 8, xx + w, y0 + 18), radius=3 * S, fill=(56, 56, 56))

def icon_col(d, x, y, n, sel=0):
    for k in range(n):
        yy = y + k * 30
        d.rounded_rectangle(s(x, yy, x + 24, yy + 24), radius=4 * S, fill=(BLUE if k == sel else (52, 52, 52)))
        d.rounded_rectangle(s(x + 7, yy + 7, x + 17, yy + 17), radius=2 * S, outline=(200, 200, 200) if k == sel else (150, 150, 150), width=S)

def gizmo(d, cx, cy, r=38):
    d.ellipse(s(cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), fill=(255, 255, 255, 18))
    ax = [((1, .35), (230, 70, 80)), ((-.45, .55), (130, 200, 40)), ((0, -1), (60, 130, 230))]
    for (dx, dy), c in ax:
        ex, ey = cx + dx * r, cy + dy * r
        d.line(s(cx, cy, ex, ey), fill=c, width=3 * S); d.ellipse(s(ex - 9, ey - 9, ex + 9, ey + 9), fill=c)
        nx, ny = cx - dx * r * .8, cy - dy * r * .8; d.ellipse(s(nx - 7, ny - 7, nx + 7, ny + 7), fill=tuple(int(v * .45) for v in c))

def node(d, x, y, w, h, col, ins=(), outs=()):
    d.rounded_rectangle(s(x + 4, y + 5, x + w + 4, y + h + 5), radius=6 * S, fill=(12, 12, 12))
    d.rounded_rectangle(s(x, y, x + w, y + h), radius=6 * S, fill=(48, 48, 48), outline=(20, 20, 20), width=S)
    d.rounded_rectangle(s(x, y, x + w, y + 22), radius=6 * S, fill=col); d.rectangle(s(x, y + 14, x + w, y + 22), fill=col)
    for k in range(int((h - 34) / 20)):              # property rows as bars
        yy = y + 32 + k * 20
        d.rounded_rectangle(s(x + 14, yy, x + w - 14, yy + 12), radius=3 * S, fill=(70, 70, 70) if k % 3 else (84, 96, 120))
    pins = {}
    for k, c in enumerate(ins):
        yy = y + 38 + k * 20; d.ellipse(s(x - 6, yy - 6, x + 6, yy + 6), fill=c, outline=(0, 0, 0), width=S); pins[('i', k)] = (x, yy)
    for k, c in enumerate(outs):
        yy = y + 38 + k * 20; d.ellipse(s(x + w - 6, yy - 6, x + w + 6, yy + 6), fill=c, outline=(0, 0, 0), width=S); pins[('o', k)] = (x + w, yy)
    return pins

def wire(d, a, b, c):
    (x0, y0), (x1, y1) = a, b; pts = []
    for i in range(41):
        t = i / 40; mx = (x1 - x0) * .5
        bx = (1 - t) ** 3 * x0 + 3 * (1 - t) ** 2 * t * (x0 + mx) + 3 * (1 - t) * t * t * (x1 - mx) + t ** 3 * x1
        by = (1 - t) ** 3 * y0 + 3 * (1 - t) ** 2 * t * y0 + 3 * (1 - t) * t * t * y1 + t ** 3 * y1
        pts += s(bx, by)
    d.line(pts, fill=c, width=3 * S, joint='curve')

def main(hero_p, side_p, thumb_p, out):
    im = Image.new('RGB', (WW, HH), BG); d = ImageDraw.Draw(im, 'RGBA')
    # ---------------- top bar: logo-ish circle, menu pills, workspace tabs (active one lighter)
    d.rectangle(s(0, 0, 1080, 40), fill=(36, 36, 36))
    d.ellipse(s(14, 10, 34, 30), fill=(232, 125, 13)); d.ellipse(s(19, 15, 29, 25), fill=(36, 36, 36)); d.ellipse(s(22, 18, 27, 23), fill=(70, 120, 190))
    for k in range(4): d.rounded_rectangle(s(48 + k * 44, 14, 80 + k * 44, 26), radius=3 * S, fill=(62, 62, 62))
    for k in range(6):
        x = 250 + k * 92; d.rounded_rectangle(s(x, 8, x + 84, 34), radius=5 * S, fill=(80, 80, 80) if k == 3 else (46, 46, 46))
        d.rounded_rectangle(s(x + 16, 17, x + 68, 25), radius=3 * S, fill=(150, 150, 150) if k == 3 else (90, 90, 90))
    # ---------------- 3D viewport in camera view with the hero render
    vx0, vy0, vx1, vy1 = 8, 48, 1072, 1150
    panel(d, vx0, vy0, vx1, vy1)
    hero = graded(hero_p)
    view = fit(hero, (vx1 - vx0 - 4) * S, (vy1 - vy0 - 30) * S, .42)
    dim = ImageEnhance.Brightness(view).enhance(.38)
    cam = s(70, 60, 1006, 1040)          # camera frame inside the viewport (passepartout outside it)
    vv = dim.copy(); vv.paste(view.crop(cam), cam[:2])
    im.paste(vv, s(vx0 + 2, vy0 + 28))
    cx0, cy0 = vx0 + 2 + 70, vy0 + 28 + 60; cx1, cy1 = vx0 + 2 + 1006, vy0 + 28 + 1040
    for x in range(cx0, cx1, 14): d.line(s(x, cy0, min(x + 7, cx1), cy0), fill=(200, 200, 200, 160), width=S); d.line(s(x, cy1, min(x + 7, cx1), cy1), fill=(200, 200, 200, 160), width=S)
    for y in range(cy0, cy1, 14): d.line(s(cx0, y, cx0, min(y + 7, cy1)), fill=(200, 200, 200, 160), width=S); d.line(s(cx1, y, cx1, min(y + 7, cy1)), fill=(200, 200, 200, 160), width=S)
    d.polygon(s((cx0 + cx1) / 2 - 18, cy0 - 6, (cx0 + cx1) / 2 + 18, cy0 - 6, (cx0 + cx1) / 2, cy0 - 26), fill=(200, 200, 200, 120))   # camera "up" triangle
    for k in (1, 2):                      # rule-of-thirds guides
        x = cx0 + (cx1 - cx0) * k / 3; y = cy0 + (cy1 - cy0) * k / 3
        d.line(s(x, cy0, x, cy1), fill=(255, 255, 255, 28), width=S); d.line(s(cx0, y, cx1, y), fill=(255, 255, 255, 28), width=S)
    icon_col(d, vx0 + 12, vy0 + 44, 7, sel=1)
    gizmo(d, vx1 - 62, vy0 + 92)
    for k in range(4): d.rounded_rectangle(s(vx1 - 76, vy0 + 160 + k * 34, vx1 - 48, vy0 + 188 + k * 34), radius=14 * S, fill=(60, 60, 60, 200))
    # ---------------- node editor (shader graph)
    nx0, ny0, nx1, ny1 = 8, 1158, 676, 1500
    panel(d, nx0, ny0, nx1, ny1)
    for gx in range(nx0 + 10, nx1, 26):
        for gy in range(ny0 + 36, ny1, 26): d.point(s(gx, gy), fill=(52, 52, 52))
    Y, G, P, Gr = (199, 199, 41), (99, 199, 99), (99, 99, 199), (161, 161, 161)
    a = node(d, 34, 1210, 150, 120, (131, 49, 74), outs=(Y, Gr))            # texture
    b = node(d, 34, 1352, 150, 104, (131, 49, 74), outs=(Y, Gr))
    c = node(d, 238, 1236, 150, 98, (59, 88, 110), ins=(Y, Gr), outs=(Gr,))  # color ramp / converter
    e = node(d, 430, 1196, 168, 262, (35, 115, 70), ins=(Y, Y, Gr, Gr, Gr, P, G, Y), outs=(G,))   # principled
    f = node(d, 612, 1260, 54, 80, (122, 40, 40), ins=(G,))
    wire(d, a[('o', 0)], c[('i', 0)], Y); wire(d, a[('o', 1)], e[('i', 3)], Gr); wire(d, c[('o', 0)], e[('i', 2)], Gr)
    wire(d, b[('o', 0)], e[('i', 1)], Y); wire(d, b[('o', 1)], e[('i', 5)], P); wire(d, e[('o', 0)], f[('i', 0)], G)
    d.rounded_rectangle(s(428, 1194, 600, 1460), radius=7 * S, outline=SEL, width=2 * S)   # active node
    # ---------------- image editor (render result)
    ix0, iy0, ix1, iy1 = 684, 1158, 1072, 1500
    panel(d, ix0, iy0, ix1, iy1)
    for yy in range(iy0 + 28, iy1, 16):                      # checker behind the image
        for xx in range(ix0, ix1, 16):
            if ((xx - ix0) // 16 + (yy - iy0) // 16) % 2: d.rectangle(s(xx, yy, min(xx + 16, ix1), min(yy + 16, iy1 - 2)), fill=(46, 46, 46))
    side = fit(graded(side_p), (ix1 - ix0 - 40) * S, (iy1 - iy0 - 64) * S, .55)
    im.paste(side, s(ix0 + 20, iy0 + 44))
    # ---------------- outliner (rows of icons + bars, a selected row) and properties-ish second image
    ox0, oy0, ox1, oy1 = 8, 1508, 430, 1730
    panel(d, ox0, oy0, ox1, oy1)
    cols = [(232, 125, 13), (110, 180, 255), (232, 125, 13), (180, 120, 255), (232, 125, 13), (120, 200, 120), (232, 125, 13), (110, 180, 255)]
    for k in range(9):
        y = oy0 + 34 + k * 21; ind = [0, 1, 1, 2, 1, 2, 2, 1, 0][k]
        if k == 3: d.rectangle(s(ox0 + 2, y - 3, ox1 - 2, y + 16), fill=(51, 77, 128))
        d.polygon(s(ox0 + 12 + ind * 16, y + 2, ox0 + 20 + ind * 16, y + 7, ox0 + 12 + ind * 16, y + 12), fill=(150, 150, 150))
        d.rounded_rectangle(s(ox0 + 26 + ind * 16, y, ox0 + 40 + ind * 16, y + 14), radius=3 * S, fill=cols[k % len(cols)])
        d.rounded_rectangle(s(ox0 + 48 + ind * 16, y + 3, ox0 + 48 + ind * 16 + [160, 120, 140, 110, 150, 90, 130, 170, 100][k], y + 11), radius=3 * S, fill=(220, 220, 220) if k == 3 else (120, 120, 120))
        for j in range(2): d.ellipse(s(ox1 - 44 + j * 20, y + 2, ox1 - 34 + j * 20, y + 12), outline=(150, 150, 150), width=S)
    tx0, ty0, tx1, ty1 = 438, 1508, 1072, 1730
    panel(d, tx0, ty0, tx1, ty1)
    th = fit(graded(thumb_p), (tx1 - tx0 - 4) * S, (ty1 - ty0 - 30) * S, .38)
    im.paste(th, s(tx0 + 2, ty0 + 28))
    # ---------------- dope sheet / timeline with keyframes and the playhead
    lx0, ly0, lx1, ly1 = 8, 1738, 1072, 1912
    panel(d, lx0, ly0, lx1, ly1)
    d.rectangle(s(lx0 + 2, ly0 + 28, lx1 - 2, ly0 + 46), fill=(34, 34, 34))
    for x in range(lx0 + 40, lx1 - 10, 24):
        d.line(s(x, ly0 + 40, x, ly0 + 46), fill=(90, 90, 90), width=S)
        d.line(s(x, ly0 + 50, x, ly1 - 6), fill=(32, 32, 32), width=S)
    rng = np.random.default_rng(7)
    for r in range(5):
        y = ly0 + 62 + r * 22
        if r % 2: d.rectangle(s(lx0 + 2, y - 10, lx1 - 2, y + 10), fill=(44, 44, 44))
        xs = sorted(set(int(v) for v in rng.uniform(60, 1040, 9 - r)))
        for x in xs:
            x = lx0 + 40 + (x - 40) // 24 * 24; c = (255, 255, 255) if r == 0 else ((230, 210, 120) if r % 2 else (200, 200, 200))
            d.polygon(s(x, y - 7, x + 7, y, x, y + 7, x - 7, y), fill=c, outline=(0, 0, 0))
    ph = lx0 + 40 + 24 * 27
    d.line(s(ph, ly0 + 30, ph, ly1 - 4), fill=BLUE, width=2 * S); d.rounded_rectangle(s(ph - 18, ly0 + 28, ph + 18, ly0 + 46), radius=4 * S, fill=BLUE)
    d.rounded_rectangle(s(ph - 9, ly0 + 34, ph + 9, ly0 + 40), radius=2 * S, fill=(225, 235, 255))
    out_im = im.resize((1080, 1920), Image.LANCZOS)
    out_im.save(out); print('ok', out)

if __name__ == '__main__':
    main(*sys.argv[1:5])
