import bpy, sys
argv = sys.argv[sys.argv.index("--") + 1:]
mode = argv[0]
if mode == "bvh":
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_anim.bvh(filepath=argv[1])
rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
s = bpy.context.scene
for f in (1, 61):
    s.frame_set(f)
    print("PROBE", mode, f, {n: tuple(round(v, 2) for v in (rig.matrix_world @ rig.pose.bones[n].tail))
                             for n in ("Hips", "Neck", "LeftLeg", "RightLeg", "LeftForeArm", "LeftFoot")})
