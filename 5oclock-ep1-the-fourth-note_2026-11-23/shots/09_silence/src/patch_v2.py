import ast, os
D = os.path.dirname(os.path.abspath(__file__)); p = os.path.join(D, 'build_s09.py'); t = open(p, encoding='utf-8').read()
reps = [("hR = IK1['hand_R']; aL = IK1['ankle_L']", "hR = IK1['hand_R']; aL = IK1['ankle_L']\nHR0 = hR.location.copy(); AL0 = aL.location.copy()     # targets are re-set every frame (no stale world matrices)"),
        ("    fp = f - (f - 1) % 2\n    bpy.context.view_layer.update()\n    # right hand", "    fp = f - (f - 1) % 2\n    hR.location = HR0; aL.location = AL0\n    bpy.context.view_layer.update()\n    # right hand")]
for x, y in reps:
    if x not in t: print('MISSING', x[:50])
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('ok')
