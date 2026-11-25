import ast, os
D = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(D, 'make_s18.py'); t = open(p, encoding='utf-8').read()
x = "LINE0 + k * LH - 70 * S, rl, 50 * S, R, -3, FJ, ob)"
if x not in t: print('MISSING')
t = t.replace(x, "LINE0 + k * LH - 66 * S, rl, 42 * S, R, -3, FJ, ob)")
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('ok')
