import bpy
from mathutils import Vector
bpy.ops.wm.open_mainfile(filepath='/home/user/w/out/shots/l4.blend')
sc=bpy.context.scene
rig=[o for o in bpy.data.objects if o.type=='ARMATURE' and 'Walker' in o.name][0]
for f in (1, 20, 30):
    sc.frame_set(f); dg=bpy.context.evaluated_depsgraph_get()
    pb=rig.pose.bones['head']; h=rig.matrix_world@(pb.head+(pb.tail-pb.head)*.45)
    e=[o for o in bpy.data.objects if o.name.startswith('Walker eyeL')][0]
    ee=e.evaluated_get(dg); me=ee.to_mesh(); c=sum((ee.matrix_world@v.co for v in me.vertices),Vector())/len(me.vertices)
    print(f, h[:], c[:], rig.matrix_world.translation[:])
