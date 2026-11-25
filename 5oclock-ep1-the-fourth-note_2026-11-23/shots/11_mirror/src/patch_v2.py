import ast, os
D = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(D, 'build_s11.py'); t = open(p, encoding='utf-8').read()
reps = [("    p0 = HEADW - FWD * 0.55 - side * 0.30 + Vector((0, 0, 0.06))", "    p0 = HEADW - FWD * 0.42 - side * 0.12 + Vector((0, 0, 0.02))"),
        ("    return p, (MPOS - p).to_track_quat('-Z', 'Y')", "    tgt = MPOS + (HEADW - MPOS) * (0.16 * (1 - k) + 0.05)\n    return p, (tgt - p).to_track_quat('-Z', 'Y')")]
for x, y in reps:
    if x not in t: print('MISSING', x[:40])
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('ok')
