import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/home/user/w/sc/trike.blend')
for o in bpy.data.objects:
    n=o.name.lower()
    if o.type=='MESH' and ('tyre' in n or 'tire' in n or 'tread' in n or 'knob' in n or 'sidewall' in n):
        print(o.name, o.parent.name, tuple(round(v,2) for v in o.dimensions), not o.hide_render)
