import bpy
bpy.ops.wm.open_mainfile(filepath='/home/user/w/out/shots/l4.blend')
b=bpy.data.objects.get('round'); print(b, b and b.users_collection, b and b.hide_render, b and b.dimensions[:], b and b.location[:])
print(bpy.context.scene.camera.location[:])
