"""Compose final 1080x1920 frames: style per segment + HUD + captions.
usage: python3 compose.py PASSDIR OUTDIR [start end]"""
import sys, os, json, math
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stylize as S, timeline as T
from font import text_mask

PD, OD = sys.argv[1], sys.argv[2]
A0, A1 = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (0, T.N - 1)
os.makedirs(OD, exist_ok=True)
PTS = json.load(open(f"{PD}/points_0_383.json"))
GW, GH, PX = 180, 320, 6          # HUD grid (6 px) is separate from the image grid (4 px)

C_BG = (20, 16, 34); C_TXT = (244, 236, 220); C_YEL = (255, 214, 90); C_RED = (255, 64, 40)
C_ORG = (255, 150, 60); C_CYAN = (70, 210, 230); C_DIM = (84, 70, 120); C_INK = (14, 12, 20)

def sm(t): t = min(1, max(0, t)); return t * t * (3 - 2 * t)
def P(kind, f): return f"{PD}/{kind}/{f:04d}.png"

# ------------------------------------------------------------------ HUD layer (grid resolution)
class Layer:
    def __init__(s):
        s.rgb = np.zeros((GH, GW, 3), np.uint8); s.a = np.zeros((GH, GW), bool)
    def rect(s, x, y, w, h, c):
        x0, y0, x1, y1 = max(0, x), max(0, y), min(GW, x + w), min(GH, y + h)
        if x1 > x0 and y1 > y0: s.rgb[y0:y1, x0:x1] = c; s.a[y0:y1, x0:x1] = True
    def mask(s, m, x, y, c):
        h, w = m.shape
        for yy in range(h):
            Y = y + yy
            if not 0 <= Y < GH: continue
            for xx in np.nonzero(m[yy])[0]:
                X = x + xx
                if 0 <= X < GW: s.rgb[Y, X] = c; s.a[Y, X] = True
    def text(s, t, x, y, c, scale=1):
        s.mask(text_mask(t, scale), x, y, c)
    def tbox(s, lines, cx, y, scale=1, fg=C_TXT, bg=C_BG, border=C_TXT, pad=3, chars=None, bold=False):
        """centred box with border; chars limits typed-on characters."""
        ms = []
        n = 0
        for ln in lines:
            if chars is not None:
                ln = ln[:max(0, chars - n)]; n += len(ln) + 0
            mm = text_mask(ln if ln else " ", scale)
            if bold: mm = np.pad(mm, ((0, 0), (0, 1))); mm = mm | np.roll(mm, 1, 1)
            ms.append(mm)
        full = [np.pad(text_mask(l, scale), ((0, 0), (0, 1 if bold else 0))) for l in lines]
        w = max(m.shape[1] for m in full) + pad * 2; h = sum(m.shape[0] for m in full) + pad * 2 + (len(lines) - 1) * 2 * scale
        x = cx - w // 2
        s.rect(x - 1, y - 1, w + 2, h + 2, border); s.rect(x, y, w, h, bg)
        s.rect(x + 1, y + h + 1, w + 1, 1, C_INK); s.rect(x + w + 1, y + 1, 1, h + 1, C_INK)   # drop shadow
        yy = y + pad
        for m, fm in zip(ms, full):
            xx = x + pad + (w - pad * 2 - fm.shape[1]) // 2
            if bold:   # ink drop shadow + two-tone face (hand-lettered sign look)
                s.mask(m, xx + 1, yy + 1, C_INK)
                s.mask(m, xx, yy, fg)
                lower = m.copy(); lower[: m.shape[0] // 2 + 1] = False
                s.mask(lower, xx, yy, C_ORG)
            else:
                s.mask(m, xx, yy, fg)
            yy += fm.shape[0] + 2 * scale
        return x, y, w, h
    def line(s, x0, y0, x1, y1, c):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n):
            t = i / max(1, n - 1); s.rect(int(round(x0 + (x1 - x0) * t)), int(round(y0 + (y1 - y0) * t)), 1, 1, c)

def fmt(n): return f"{int(round(n)):,}"

def hud(L, f):
    # top-left: speed label with blinking rec dot
    lab = T.slowmo_label(f)
    if T.C_RAMP[0] <= f < T.C_RAMP[0] + 8: lab = "SLOWING..."
    if T.E_RAMP[0] <= f < T.E_RAMP[0] + 10: lab = "SPEEDING UP..."
    L.rect(4, 5, len(lab) * 6 + 11, 11, C_BG); L.rect(4, 15, len(lab) * 6 + 11, 1, C_ORG)
    if (f // 12) % 2 == 0: L.rect(6, 8, 3, 3, C_RED)
    L.text(lab, 12, 7, C_ORG if "SLOW" in lab or "UP" in lab else C_TXT)
    # top-right: rpm counter + meter
    r = T.rpm_shown(f)
    rs = (f"{r:.1f}" if r < 100 else fmt(r)) + " RPM"
    w = len(rs) * 6 + 6
    L.rect(GW - w - 4, 5, w, 11, C_BG); L.text(rs, GW - w - 1, 7, C_YEL)
    segs = int(round(14 * min(1, (math.log10(max(r, 1)) / math.log10(3000)))))
    for i in range(14):
        L.rect(GW - w - 4 + i * 3, 17, 2, 2, C_CYAN if i < segs else C_DIM)

def caption(L, f):
    D0 = T.D_SLOW[0]; cyc = 720 / (750 / T.SLOW)      # frames per 4-stroke cycle in slow-mo (~80.6)
    # hook
    if f < 58:
        ch = int(max(0, f - 2) * 2.2)
        y = 34 + (1 if f in (3, 4) else 0)
        L.tbox(["WHAT'S UNDER", "THE HOOD?"], GW // 2, y, 2, chars=None, bold=True, fg=C_YEL)   # full hook from frame 0 = thumbnail
        if f > 18: L.tbox(["150 EXPLOSIONS A SECOND"], GW // 2, 82, 1, fg=C_INK, bg=C_YEL, border=C_INK, pad=2,
                         chars=int((f - 18) * 2.5))
    elif f < D0:
        pass
    elif f < D0 + cyc:
        L.tbox(["1 CYLINDER", "4 STROKES"], GW // 2, 30, 1)
        st = T.stroke(1, f)
        ws = [len(nm) * 6 + 5 for nm in T.STROKE_NAME]; x = (GW - sum(ws) - 3 * 2) // 2
        for i, nm in enumerate(T.STROKE_NAME):
            on = i == st
            L.rect(x, 58, ws[i], 11, C_YEL if on else C_BG)
            L.text(nm, x + 3, 60, C_INK if on else C_TXT if i < st else C_DIM)
            x += ws[i] + 2
        labels(L, f)
    elif f < D0 + 2 * cyc:
        L.tbox(["FIRING ORDER:", "1-4-2-5-3-6"], GW // 2, 30, 1)
        order = [1, 4, 2, 5, 3, 6]
        fired = [c for c in order if 0 <= (T.crank(f) - T.FIRE[c]) % 720 < 120]
        for i in range(1, 7):
            p = PTS[str(f)][f"cyl{i}"]; X = int(p[0] * GW); Y = int((1 - p[1]) * GH) - 16
            on = i in fired
            L.rect(X - 5, Y - 1, 11, 11, C_YEL if on else C_BG); L.text(str(i), X - 2, Y + 1, C_INK if on else C_TXT)
    elif f < T.E_RAMP[0]:
        L.tbox(["ONE BANG EVERY", "THIRD OF A TURN"], GW // 2, 30, 1)
        if f > D0 + 2 * cyc + 14:
            L.tbox(["SO THE CRANK", "NEVER STOPS"], GW // 2, 64, 1, fg=C_INK, bg=C_YEL, border=C_INK, pad=2,
                   chars=int((f - D0 - 2 * cyc - 14) * 2))
    elif f >= T.F_END[0] + 4:
        L.tbox(["3,000 RPM", "= 150 BANGS", "EVERY SECOND."], GW // 2, 36, 2, bold=True, fg=C_YEL, chars=int((f - T.F_END[0] - 4) * 2.5))
    # BANG! pop on cylinder 1's power stroke (first cycle) and every bang in slow-mo
    if D0 <= f < T.E_RAMP[0]:
        for c in range(1, 7):
            a = (T.crank(f) - T.FIRE[c]) % 720
            if f < 164 and c not in (1, 4): continue          # front slice: only the front pair is visible
            if f >= 245 and c < 4: continue                   # 3/4 view: the cut-open near bank
            if a < 40:
                p = PTS[str(f)][f"cyl{c}"]; X = int(p[0] * GW); Y = int((1 - p[1]) * GH) - 34
                sc = 2 if a < 10 else 1
                m = text_mask("BANG!", sc)
                L.mask(np.pad(m, 1) | np.roll(np.pad(m, 1), 1, 0) | np.roll(np.pad(m, 1), 1, 1), X - m.shape[1] // 2 - 1, Y - 1, C_INK)
                L.mask(m, X - m.shape[1] // 2, Y, C_YEL if a < 10 else C_ORG)

def labels(L, f):
    pts = PTS[str(f)]
    t0 = f - T.D_SLOW[0]
    for i, (key, name, tx, ty) in enumerate([("piston", "PISTON", 120, 96), ("rod", "CONNECTING ROD", 84, 226),
                                              ("crank", "CRANKSHAFT", 6, 208)]):
        if t0 < 8 + i * 9: continue
        p = pts[key]; X = int(p[0] * GW); Y = int((1 - p[1]) * GH)
        w = len(name) * 6 + 3
        ex = min(max(X, tx), tx + w - 2); ey = ty + 10 if ty < Y else ty - 2       # leader meets the label edge
        L.line(X, Y, ex, ey, C_TXT); L.rect(X - 1, Y - 1, 3, 3, C_YEL)
        L.rect(tx - 2, ty - 2, w, 11, C_BG); L.rect(tx - 2, ty + 9, w, 1, C_YEL)
        L.text(name, tx, ty, C_TXT)

# ------------------------------------------------------------------ base image per segment
def xray_img(f):
    return S.pixel(P("xcol", f), P("nrm", f), f)

def base(f):
    if f < T.B_FILL[0]:
        return S.sketch(P("col", f), P("nrm", f), f, reveal=sm(f / 30), colour=0)
    if f < T.C_RAMP[0]:
        sk = S.sketch(P("col", f), P("nrm", f), f, reveal=1, colour=sm((f - 34) / 10))
        if f < 44: return sk
        return S.pixel_wipe(sk, S.pixel(P("col", f), P("nrm", f), f), sm((f - 44) / 12))
    if f < T.C_RAMP[1]:
        t = sm((f - 62) / 18)
        a = S.pixel(P("col", f), P("nrm", f), f)
        return a if t <= 0 else S.pixel_wipe(a, xray_img(f), t, seed=5)
    if f in (82, 83, 164, 165, 245, 246):        # ink impact frames on the hard cuts
        return S.sketch(P("xcol", f), P("nrm", f), f, reveal=1, colour=.75)
    if f < T.E_RAMP[0]:
        return xray_img(f)
    if f < T.E_RAMP[1]:
        t = sm((f - T.E_RAMP[0]) / 24)
        return S.pixel_wipe(xray_img(f), S.pixel(P("col", f), P("nrm", f), f), t, seed=9)
    return S.pixel(P("col", f), P("nrm", f), f)

def shake(f):
    """hand-keyed camera bumps: on every slow-mo bang, and the launch."""
    if T.D_SLOW[0] <= f < T.E_RAMP[0]:
        for c in range(1, 7):
            a = (T.crank(f) - T.FIRE[c]) % 720
            if a < 9: return [(2, -1), (-1, 1)][int(a // 4.5) % 2]
    if T.F_END[0] <= f < T.F_END[0] + 4: return [(0, 2), (1, -1), (-1, 1), (0, 0)][f - T.F_END[0]]
    return (0, 0)

def streaks(img, f):
    """road-rush speed lines on the asphalt (pixel grid), scaled by playback speed."""
    s = T.speed(f)
    if s < .3 or f < 44: return img
    G = (S.GW, S.GH); px = S.PX
    nrm = np.asarray(Image.open(P("nrm", f)).convert("RGB").resize(G, Image.NEAREST), np.int16)
    g = (np.abs(nrm[..., 0] - 188) < 10) & (np.abs(nrm[..., 1] - 188) < 10) & (nrm[..., 2] > 245)
    r = np.random.default_rng(77); n = int(38 * s)
    out = img.copy()
    for i in range(n):
        y = int(r.integers(S.GH // 3, S.GH)); L = int(r.integers(14, 40)); v = r.uniform(22, 44)
        x = int((r.uniform(0, S.GW) - f * v) % (S.GW + 40)) - 20
        for xx in range(max(0, x), min(S.GW, x + L)):
            if g[y, xx]:
                out[y * px:(y + 1) * px, xx * px:(xx + 1) * px] = (out[y * px:(y + 1) * px, xx * px:(xx + 1) * px] * .35 + np.array([214, 200, 230]) * .65).astype(np.uint8)
    return out

for f in range(A0, A1 + 1):
    img = streaks(base(f), f)
    L = Layer(); hud(L, f); caption(L, f)
    up_rgb = L.rgb.repeat(PX, 0).repeat(PX, 1); up_a = L.a.repeat(PX, 0).repeat(PX, 1)
    img = np.where(up_a[..., None], up_rgb, img)
    dx, dy = shake(f)
    if dx or dy: img = np.roll(img, (dy * PX, dx * PX), (0, 1))
    # 1-frame white-hot flash on the first slow-mo bang and the launch
    if f in (T.F_END[0],):
        img = (img * .4 + 255 * .6).astype(np.uint8)
    Image.fromarray(img).save(f"{OD}/{f:04d}.png")
