import bpy, collections
bpy.ops.wm.open_mainfile(filepath='/home/user/w/out/anim/s3.blend')
c=collections.Counter()
for o in bpy.data.objects:
    if o.type=='MESH' and o.data.users>1: c[o.data.name]+=1
print(c.most_common(8))
for o in bpy.data.objects:
    if o.type=='MESH' and ('tyre' in o.data.name.lower()) : print(o.name, o.data.name, o.parent and o.parent.name)
