import ast, os
D = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(D, 'build_s10.py'); t = open(p, encoding='utf-8').read()
for x, y in (("camd.lens = 78 + 52 * k", "camd.lens = 85 + 115 * k"), ("tgt = HEADW + Vector((0, 0, 0.02 - 0.10 * (1 - k)))", "tgt = HEADW + Vector((0, 0, 0.05 - 0.20 * (1 - k)))")):
    if x not in t: print('MISSING', x)
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('ok')
