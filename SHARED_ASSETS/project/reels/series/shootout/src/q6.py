import bpy, sys
bpy.ops.wm.open_mainfile(filepath=sys.argv[-2])
sc=bpy.context.scene; sc.frame_set(20)
r=bpy.data.objects['rain']; r.hide_render = sys.argv[-1]=='1'
sc.render.filepath=f'/home/user/w/out/probe/diag_{sys.argv[-1]}.png'; bpy.ops.render.render(write_still=True)
