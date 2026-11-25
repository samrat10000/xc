import ast, os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, 'build_s06.py'); t = open(p, encoding='utf-8').read()
reps = [
    ("for lp, (u, v) in zip(f_.loops, ((1, 1), (1, 0), (0, 0), (0, 1))): lp[uv].uv = (u, v)",
     "for lp, (u, v) in zip(f_.loops, ((0, 0), (0, 1), (1, 1), (1, 0))): lp[uv].uv = (u, v)          # v2: was upside down"),
    # v2 framing: close over the bar, the phone fills a third of the frame, the right hand comes in to tap
    ("    root = B['root'].matrix_world\n    p = root @ Vector((-0.42, -0.34, 1.52)) + Vector((0.004 * math.sin(f * 0.9), 0, 0.006 * math.sin(f * 1.3)))\n    tgt = PH.matrix_world @ Vector((0.0, 0.0, 0.0))",
     "    root = B['root'].matrix_world\n    p = PH.matrix_world @ Vector((-0.20, -0.07, 0.30)) + Vector((0.003 * math.sin(f * 0.9), 0, 0.004 * math.sin(f * 1.3)))\n    tgt = PH.matrix_world @ Vector((0.012, 0.0, 0.0))"),
    ("camd.lens = 50; camd.dof.use_dof = True", "camd.lens = 42; camd.dof.use_dof = True"),
    ("tap_local = steer.matrix_world.inverted() @ (PH.matrix_world @ Vector((0.03, 0.022, 0.03)))",
     "bpy.context.view_layer.update()\ntap_local = steer.matrix_world.inverted() @ (PH.matrix_world @ Vector((0.035, 0.018, 0.05)))"),
]
for x, y in reps:
    if x not in t: print('MISSING', x[:70])
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('patched')
