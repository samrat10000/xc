import bpy
bpy.ops.wm.open_mainfile(filepath='/home/user/w/out/walker/walker.blend')
print([c.name for c in bpy.data.collections]); r=[o for o in bpy.data.objects if o.type=='ARMATURE'][0]
print(r.name, r.location[:], [o.name for o in r.children][:40])
print('head', (r.matrix_world@r.pose.bones['head'].head)[:])
print('nonchild', [o.name for o in bpy.data.objects if o.parent is None])
