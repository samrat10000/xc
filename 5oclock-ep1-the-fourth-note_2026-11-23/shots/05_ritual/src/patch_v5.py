import ast, os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, 'build_s05.py'); t = open(p, encoding='utf-8').read()
reps = [
    # lathe() caps the first ring by default: the back plate and the rim each put a red disc OVER the glass
    ("lathe([(0.0, 0.215), (0.035, 0.215), (0.035, 0.0005)], 48), FRM", "lathe([(0.0, 0.215), (0.035, 0.215), (0.035, 0.0005)], 48, cap_back=False), FRM"),
    ("lathe([(-0.03, 0.235), (0.035, 0.235), (0.035, 0.205), (-0.03, 0.205)], 48), FRM", "lathe([(-0.03, 0.235), (0.035, 0.235), (0.035, 0.205), (-0.03, 0.205)], 48, cap_back=False), FRM"),
    # _rot_arm reads pb.matrix INCLUDING constraints: switch IK off and evaluate before posing, or the last IK result is baked in
    ("        reset(gm, gb); R(gm, 'J_Bip_L_UpperArm'", "        for S in ('L', 'R'): setinf(hands[S], 0.0)\n        bpy.context.view_layer.update()\n        reset(gm, gb); R(gm, 'J_Bip_L_UpperArm'"),
    ("        p = ROAD.matrix_world @ Vector((3.55 + 0.06 * k, 3.20 + 0.08 * k, 1.34))", "        p = ROAD.matrix_world @ Vector((3.30 + 0.06 * k, 2.85 + 0.08 * k, 1.34))"),
    # kids: no IK on non-uniformly scaled child arm bones (shear -> exploded 'strings'); FK pose to the ears instead
    ("            tgts[S] = (t_, a_, p_, po, grip(rig, S, t_, a_, p_, po))", "            tgts[S] = (t_, a_, p_, po, [])"),
    ("                R(rig, 'J_Bip_%s_UpperArm' % S, (0, 1, 0), sg * 70)", "                pass"),
    ("            cover = ease((fp - 12 - K['ph'] * 2) / 5.0); up = ease((fp - 18 - K['ph']) / 6.0)",
     "            cover = ease((fp - 12 - K['ph'] * 2) / 5.0); up = ease((fp - 18 - K['ph']) / 6.0)\n"
     "            for S, sg in (('L', 1), ('R', -1)):                                    # arms: swinging down -> palms over the ears\n"
     "                swing = 14 * math.sin(ph + (math.pi if S == 'L' else 0)) * run\n"
     "                R(rig, 'J_Bip_%s_UpperArm' % S, (0, 1, 0), sg * L(70, 4, cover))\n"
     "                R(rig, 'J_Bip_%s_UpperArm' % S, (0, 0, 1), -sg * (L(0, 18, cover)) + swing)\n"
     "                R(rig, 'J_Bip_%s_LowerArm' % S, (0, 1, 0), -sg * L(12, 156, cover))\n"
     "                R(rig, 'J_Bip_%s_Hand' % S, (0, 0, 1), sg * 20 * cover)"),
]
for x, y in reps:
    if x not in t: print('MISSING', x[:70])
    t = t.replace(x, y)
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('patched')
