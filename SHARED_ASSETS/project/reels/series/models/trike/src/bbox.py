import bpy,sys
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=sys.argv[-1])
mn=Vector((1e9,)*3);mx=-mn
tris=0
for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    tris+=sum(len(p.vertices)-2 for p in o.data.polygons)
    for c in o.bound_box:
        w=o.matrix_world@Vector(c); mn=Vector(map(min,mn,w)); mx=Vector(map(max,mx,w))
print('BBOX',mn,mx,'tris',tris)
for o in bpy.context.scene.objects:
    if o.type=='EMPTY' and 'wheel' in o.name: print('W',o.name,o.matrix_world.translation)
