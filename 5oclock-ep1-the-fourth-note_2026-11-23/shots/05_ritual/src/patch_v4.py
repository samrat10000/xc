import ast, os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, 'build_s05.py'); t = open(p, encoding='utf-8').read()
reps = [
    # feet: only vertices within 0.9 m (horizontal) of the rig origin count (a stray first-frame IK vertex went to -813 m)
    ("        zs = [(mw @ v.co).z for i, v in enumerate(me.vertices) if i % 5 == 0]; ev.to_mesh_clear()",
     "        c0 = (o.parent or o).matrix_world.translation\n"
     "        zs = [w.z for i, v in enumerate(me.vertices) if i % 5 == 0 for w in (mw @ v.co,) if (w.xy - c0.xy).length < 0.9]; ev.to_mesh_clear()"),
    # cut a: arms come down from the T-pose before IK takes over (no T-pose arm when the IK lets go)
    ("        reset(gm, gb)\n        look = ease((fp - 1) / 6.0)",
     "        reset(gm, gb); R(gm, 'J_Bip_L_UpperArm', (0, 1, 0), 70); R(gm, 'J_Bip_R_UpperArm', (0, 1, 0), -70)\n        look = ease((fp - 1) / 6.0)"),
    # cut a camera: the street side of the mirror -> her profile and the glass, which then turns to the wall
    ("        p = ROAD.matrix_world @ Vector((6.15 - 0.10 * k, 4.05, 1.30))", "        p = ROAD.matrix_world @ Vector((3.55 + 0.06 * k, 3.20 + 0.08 * k, 1.34))"),
    ("        tgt = ROAD.matrix_world @ Vector((4.45, 4.55, 1.38))", "        tgt = ROAD.matrix_world @ Vector((4.45, 4.55, 1.40))"),
    ("    gm, gmo, gb = load_char('grandma', (4.62, 4.30, 0.0), -150)", "    gm, gmo, gb = load_char('grandma', (4.66, 4.28, 0.0), -140)"),
    # cut b: both kids near the centre of the frame
    ("load_char('kid_boy', (22.3, 1.7, 0.0), 0)", "load_char('kid_boy', (22.55, 1.7, 0.0), 0)"),
    ("load_char('kid_girl', (23.7, 2.3, 0.0), 0)", "load_char('kid_girl', (23.45, 2.2, 0.0), 0)"),
    ("(kb_, kbo, kbb, 22.3, 1.7, 0.0), (kg_, kgo, kgb, 23.7, 2.3, 1.3)", "(kb_, kbo, kbb, 22.55, 1.7, 0.0), (kg_, kgo, kgb, 23.45, 2.2, 1.3)"),
]
for x, y in reps:
    if x not in t: print('MISSING', x[:70])
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('patched')
