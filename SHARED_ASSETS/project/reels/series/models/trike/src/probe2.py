import bpy,sys
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=sys.argv[-1])
def bb(o):
    ps=[o.matrix_world@Vector(c) for c in o.bound_box]; return [round(min(p[i] for p in ps),2) for i in range(3)],[round(max(p[i] for p in ps),2) for i in range(3)]
import collections
for g in [o for o in bpy.data.objects if o.type=='EMPTY' and o.name[:2] in ('01','02','03','04','05','06','07','08','09')]:
    print('##',g.name)
    seen=collections.OrderedDict()
    for c in g.children:
        if c.type!='MESH':continue
        b=c.name.split('.')[0]
        if b in seen: seen[b][0]+=1; continue
        seen[b]=[1,c.active_material.name[:14] if c.active_material else '',len(c.data.polygons),bb(c)]
    for k,v in seen.items(): print('  ',k,v)
