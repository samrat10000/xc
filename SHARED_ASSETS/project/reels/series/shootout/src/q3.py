import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/home/user/w/sc/trike.blend')
import collections
seen=collections.defaultdict(list)
for o in bpy.data.objects:
    n=o.name.lower()
    if o.type=='MESH' and not o.hide_render and any(k in n for k in ('led','pod','lamp','light','barrel','muzzle','gun','charg','handle','lever','belt','ammo')):
        c=sum((o.matrix_world@Vector(b) for b in o.bound_box),Vector())/8
        seen[o.name.split('.')[0]].append(tuple(round(v,2) for v in c))
for k,v in seen.items(): print(k, v[:4])
