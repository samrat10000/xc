import bpy,sys
bpy.ops.import_scene.gltf(filepath='car/nt.glb')
tops=[o for o in bpy.data.objects if o.parent is None]
print('TOPS',[o.name for o in tops][:40])
for o in bpy.data.objects:
    if o.type=='EMPTY': print('E',o.name,o.parent.name if o.parent else None,tuple(round(x,2) for x in o.matrix_world.translation))
