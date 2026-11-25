import ast, os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, 'build_s05.py'); t = open(p, encoding='utf-8').read()
reps = [
    # reset must restore the FULL pose (matrix writes from _rot_arm also change bone location/scale -> drift over sequential frames)
    ("    base = {pb.name: pb.rotation_quaternion.copy() for pb in rig.pose.bones}", "    base = {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}"),
    ("        if pb.name in base: pb.rotation_quaternion = base[pb.name].copy()", "        if pb.name in base: pb.matrix_basis = base[pb.name].copy()"),
    # shear fix only where bone scales are non-uniform (the kids); on Grandma it stretched the IK arms
    ("    for b in rig.data.bones:\n        if any(", "    for b in (rig.data.bones if 'kid' in name else []):\n        if any("),
]
for x, y in reps:
    if x not in t: print('MISSING', x[:70])
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('patched')
