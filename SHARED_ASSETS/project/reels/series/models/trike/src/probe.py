import bpy,sys
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=sys.argv[-1])
def bb(o):
    ps=[o.matrix_world@Vector(c) for c in o.bound_box]; return [round(min(p[i] for p in ps),3) for i in range(3)],[round(max(p[i] for p in ps),3) for i in range(3)]
for g in [o for o in bpy.data.objects if o.type=='EMPTY']:
    ch=[c for c in g.children if c.type=='MESH']
    print('##',g.name,len(ch),'par=',g.parent.name if g.parent else None)
    if 'wheel' in g.name:
        for c in ch: print('   ',c.name,c.active_material.name if c.active_material else '',len(c.data.polygons),bb(c))
for i in bpy.data.images: print('IMG',i.name,i.size[:])
