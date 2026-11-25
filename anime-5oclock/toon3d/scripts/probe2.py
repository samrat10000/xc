import bpy
for m in bpy.data.materials:
    if not m.node_tree: continue
    imgs=[(n.name,n.image.name if n.image else None) for n in m.node_tree.nodes if n.type=='TEX_IMAGE']
    ext=getattr(m,'vrm_addon_extension',None)
    am=None
    try: am=(ext.mtoon1.alpha_mode, ext.mtoon1.alpha_cutoff, ext.mtoon1.double_sided)
    except Exception as e: am=str(e)
    print(m.name, m.surface_render_method, am, imgs[:3])
for o in bpy.data.objects:
    if o.type=='MESH': print(o.name,[ (md.type,md.name) for md in o.modifiers], o.parent and o.parent.name)
arm=bpy.data.objects['Armature'] if 'Armature' in bpy.data.objects else [o for o in bpy.data.objects if o.type=='ARMATURE'][0]
print(arm.name)
for n in ['J_Adj_L_FaceEye','J_Adj_R_FaceEye','J_Bip_L_UpperArm','J_Bip_C_Head']:
    b=arm.data.bones[n]; print(n, b.matrix_local.to_3x3())
