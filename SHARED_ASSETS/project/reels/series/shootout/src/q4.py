import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/home/user/w/out/shots/l1.blend')
sc=bpy.context.scene; sc.frame_set(14); c=sc.camera.matrix_world.translation
for o in bpy.data.objects:
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(b) for b in o.bound_box]
    mn=Vector(map(min,*bb)); mx=Vector(map(max,*bb))
    if all(mn[i]-.3<c[i]<mx[i]+.3 for i in range(3)): print(o.name, mn[:], mx[:])
print(c)
