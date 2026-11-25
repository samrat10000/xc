import ast, os
D = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(D, 'build_s13.py'); t = open(p, encoding='utf-8').read()
reps = [
    ("mrot('J_Bip_L_UpperArm', (0, 1, 0), 70)", "mrot('J_Bip_L_UpperArm', (0, 1, 0), 72); mrot('J_Bip_R_UpperArm', (0, 1, 0), -72)"),
    ("POLE.location = MPOS2 + Vector((-0.6, 0.3, 0.9))", "POLE.location = MPOS2 + Vector((-0.55, -0.15, 0.85))          # elbow down at his side: only the hand rises"),
    ("mouth = mrig.matrix_world @ mrig.pose.bones['J_Bip_C_Head'].head + Vector((0.0, -0.10, 0.035))", "mouth = mrig.matrix_world @ mrig.pose.bones['J_Bip_C_Head'].head + Vector((-0.01, -0.13, 0.01))"),
    ("camB.location = MPOS2 + Vector((0.04, -1.05, 1.52))", "camB.location = MPOS2 + Vector((0.03, -0.80, 1.60))"),
    ("((MPOS2 + Vector((0, 0, 1.48))) - camB.location)", "((MPOS2 + Vector((0, 0, 1.56))) - camB.location)"),
    ("    p = p.lerp(MPOS - FWD * 0.95, 0.30 + 0.15 * k)", "    p = p.lerp(MPOS - FWD * 0.95, 0.10 + 0.14 * k)               # his real head stays at the frame edge"),
]
for x, y in reps:
    if x not in t: print('MISSING', x[:60])
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('ok')
