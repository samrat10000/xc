import ast, os
D = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(D, 'build_s13.py'); t = open(p, encoding='utf-8').read()
reps = [("    p = HEADW - FWD * 0.30 - side * 0.05 + Vector((0, 0, 0.02))", "    p = HEADW - FWD * 0.45 - side * 0.14 + Vector((0, 0, 0.02))"),
        ("    p = p.lerp(MPOS - FWD * 0.95, 0.10 + 0.14 * k)", "    p = p.lerp(MPOS - FWD * 0.95, 0.06 + 0.12 * k)"),
        ("Vector((-0.01, -0.13, 0.01))          ", "Vector((-0.01, -0.12, -0.085))         "),
        ("Vector((-0.01, -0.13, 0.01))", "Vector((-0.01, -0.12, -0.085))   # IK places the WRIST: the index then lands on the lips")]
n = 0
for x, y in reps:
    if x in t: t = t.replace(x, y); n += 1
print('applied', n)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t)
