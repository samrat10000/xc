import bpy, sys, json
argv = sys.argv[sys.argv.index("--") + 1:]
base = argv[0]
out = {}
for kind in ("bvh", "fbx"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if kind == "bvh":
        bpy.ops.import_anim.bvh(filepath=base + ".bvh", update_scene_fps=True, update_scene_duration=True)
    else:
        bpy.ops.import_scene.fbx(filepath=base + ".fbx")
    rig = next(o for o in bpy.data.objects if o.type == "ARMATURE")
    act = rig.animation_data.action if rig.animation_data else None
    n_fc = len(act.fcurves) if act and hasattr(act, "fcurves") else -1
    rng = tuple(act.frame_range) if act else None
    s = bpy.context.scene
    pts = {}
    if kind == "bvh":
        for f in range(int(rng[0]), int(rng[1]) + 1, 3):
            s.frame_set(f)
            pts[f] = {pb.name: [list(rig.matrix_world @ pb.head), list(rig.matrix_world @ pb.tail)] for pb in rig.pose.bones}
        json.dump(pts, open(base + "_bones.json", "w"))
    out[kind] = {"bones": len(rig.pose.bones), "fcurves": n_fc, "range": rng}
print("VERIFY", out)
