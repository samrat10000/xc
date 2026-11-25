import ast, os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, 'build_s05.py'); t = open(p, encoding='utf-8').read()
reps = [
    # non-uniform child-proportion bone scales shear their children when they rotate -> limbs collapse into thin lines
    ("    for pb in rig.pose.bones: pb.rotation_mode = 'QUATERNION'\n    base = {",
     "    for pb in rig.pose.bones: pb.rotation_mode = 'QUATERNION'\n"
     "    for b in rig.data.bones:\n"
     "        if any(k in b.name for k in ('Arm', 'Hand', 'Index', 'Middle', 'Ring', 'Little', 'Thumb', 'Leg', 'Foot', 'Toe')):\n"
     "            b.inherit_scale = 'FIX_SHEAR'\n"
     "    base = {"),
    # grandma: hold the rim until f23, then let go over 5 frames (no arm flung out sideways)
    ("        for S in ('L', 'R'): setinf(hands[S], reach * (1 - 0.85 * back))", "        for S in ('L', 'R'): setinf(hands[S], reach * (1 - ease((fp - 23) / 5.0)))"),
]
for x, y in reps:
    if x not in t: print('MISSING', x[:70])
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('patched')
