import bpy, sys
argv = sys.argv[sys.argv.index("--") + 1:]
base = argv[0]
rig = bpy.data.objects["MocapRig"]
ad = rig.animation_data
print("ACTION", ad.action.name if ad and ad.action else None, getattr(ad, "action_slot", None) if ad else None,
      len(ad.action.fcurves) if ad and ad.action else 0)
for o in bpy.context.view_layer.objects: o.select_set(False)
rig.select_set(True); bpy.context.view_layer.objects.active = rig
bpy.ops.export_scene.fbx(filepath=base + ".fbx", use_selection=True, object_types={"ARMATURE"},
                         add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=False,
                         bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
                         bake_anim_simplify_factor=0.0)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=base + ".fbx")
r = next(o for o in bpy.data.objects if o.type == "ARMATURE")
a = r.animation_data.action if r.animation_data else None
print("FBX_REIMPORT", a.name if a else None, a.frame_range[:] if a else None, len(a.fcurves) if a else 0)
