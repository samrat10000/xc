import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/home/user/w/sc/trike.blend')
for n in ('Front mud-terrain knobby tyre','Rear left mud-terrain knobby tyre','Left heavy machine gun'):
    o=bpy.data.objects[n]; bb=[o.matrix_world@Vector(b) for b in o.bound_box]
    print(n, [round(min(v[i] for v in bb),2) for i in range(3)], [round(max(v[i] for v in bb),2) for i in range(3)])
