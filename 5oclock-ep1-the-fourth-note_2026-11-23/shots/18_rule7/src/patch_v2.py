import ast, os
D = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(D, 'make_s18.py'); t = open(p, encoding='utf-8').read()
reps = [
    ("s = 1.42 + 0.03 * k", "s = 1.20 + 0.03 * k"),
    ("cx = PW / 2 + 40 * S + 6 * S * math.sin(f * 0.07)", "cx = PW / 2 + 20 * S + 6 * S * math.sin(f * 0.07)"),
    # handwriting, not a font: stronger per-glyph irregularity, more wobble and bleed
    ("fs = int(size * r.uniform(0.92, 1.08))", "fs = int(size * r.uniform(0.84, 1.12))"),
    ("g = g.rotate(r.uniform(-4, 4) + slant, resample=Image.BICUBIC)", "g = g.rotate(r.uniform(-7, 7) + slant, resample=Image.BICUBIC)"),
    ("gy = y + r.uniform(-0.05, 0.05) * size", "gy = y + r.uniform(-0.09, 0.09) * size"),
    ("OFF = inkify(officer, 11, 1.6 * S)", "OFF = inkify(officer, 11, 3.0 * S)"),
    ("SAM = inkify(sam, 71, 2.4 * S)", "SAM = inkify(sam, 71, 4.2 * S)"),
    ("    bleed = gaussian_filter(a, 1.4 * S) * 0.35", "    bleed = gaussian_filter(a, 1.8 * S) * 0.45"),
    # the tear: a real shadow under the torn lip, the page beneath clearly another sheet
    ("- gaussian_filter(hole, 5 * S)[..., None] * 0.05 * (1 - hole[..., None])", "- gaussian_filter(hole, 5 * S)[..., None] * 0.05 * (1 - hole[..., None]) - (hole * np.clip(1 - (yy - top[None, :]) / (22 * S), 0, 1))[..., None] * 0.16"),
    ("under = np.array([0.80, 0.75, 0.64])", "under = np.array([0.76, 0.70, 0.58])"),
]
for x, y in reps:
    if x not in t: print('MISSING', x[:60])
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('ok')
