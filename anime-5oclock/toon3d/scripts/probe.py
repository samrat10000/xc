import bpy, sys, addon_utils
import addon_utils
if not any("vrm" in m for m in bpy.context.preferences.addons.keys()): addon_utils.enable("bl_ext.user_default.vrm", default_set=True)
print("VRM enabled:", [m for m in bpy.context.preferences.addons.keys() if "vrm" in m])
bpy.ops.wm.read_factory_settings(use_empty=True) if False else None
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
r = bpy.ops.import_scene.vrm(filepath=sys.argv[-1])
print("import:", r)
for o in bpy.data.objects:
    extra=''
    if o.type=='MESH':
        me=o.data; extra=f" verts={len(me.vertices)} mats={[m.name for m in me.materials]} keys={len(me.shape_keys.key_blocks) if me.shape_keys else 0}"
        import mathutils
        bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
        extra+=f" zmin={min(v.z for v in bb):.3f} zmax={max(v.z for v in bb):.3f} xw={max(v.x for v in bb)-min(v.x for v in bb):.3f}"
    print(o.name,o.type,extra)
arm=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
print([b.name for b in arm.data.bones][:80])
for n in ['J_Bip_C_Head','J_Bip_L_UpperArm','J_Bip_C_Neck','J_Bip_L_Shoulder']:
    b=arm.data.bones.get(n)
    if b: print(n, tuple(round(x,3) for x in arm.matrix_world@b.head_local))
face=[o for o in bpy.data.objects if o.type=='MESH' and o.data.shape_keys and len(o.data.shape_keys.key_blocks)>5]
if face: print("keys:",[k.name for k in face[0].data.shape_keys.key_blocks])
mat=bpy.data.materials[0]; print("mat nodes:", mat.name, [n.bl_idname for n in mat.node_tree.nodes] if mat.node_tree else None)
bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath("//")+"C:/Users/cross/Downloads/xc/anime-5oclock/toon3d/_probe.blend" if False else "C:/Users/cross/Downloads/xc/anime-5oclock/toon3d/_probe.blend")
