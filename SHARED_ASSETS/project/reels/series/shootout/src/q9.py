import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/home/user/w/out/anim/s9.blend')
sc=bpy.context.scene; sc.frame_set(30); c=sc.camera.matrix_world.translation
print('cam',c[:])
for n in ('TRIKE_root','TRIKE_body','wF','wRL','wRR'):
    o=bpy.data.objects[n]; print(n, tuple(round(x,2) for x in o.matrix_world.translation), tuple(round(x,2) for x in o.matrix_world.to_euler()))
for o in bpy.data.objects:
    if o.type=='MESH' and 'tyre' in o.name and 'hull' not in o.name:
        print(o.name, tuple(round(x,2) for x in o.matrix_world.translation), o.parent.name, tuple(round(x,2) for x in o.location))
