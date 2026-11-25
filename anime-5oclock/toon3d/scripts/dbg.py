import bpy, math
bpy.ops.wm.open_mainfile(filepath='C:/Users/cross/Downloads/xc/anime-5oclock/toon3d/sam_toon.blend')
sc=bpy.context.scene
f=bpy.data.objects['Face']
for i,m in enumerate(f.data.materials): print(i, m.name, m.surface_render_method, m.use_backface_culling)
m=[m for m in f.data.materials if 'Skin' in m.name][0]
print([ (n.type, getattr(n,'image',None) and n.image.name) for n in m.node_tree.nodes if n.type=='TEX_IMAGE'])
cam_d=bpy.data.cameras.new('c'); cam=bpy.data.objects.new('c',cam_d); sc.collection.objects.link(cam); sc.camera=cam
cam_d.type='ORTHO'; cam_d.ortho_scale=0.35; cam.location=(0,-3,1.73); cam.rotation_euler=(math.radians(90),0,0)
sc.render.resolution_x=sc.render.resolution_y=400; sc.eevee.taa_render_samples=8
for tag,hide in (('a',True),('b',False)):
    bpy.data.objects['Face_Outline'].hide_render=hide
    sc.render.filepath=f'C:/Users/cross/AppData/Local/Temp/claude/2025787e23e4a901/f11d269a-c5f1-40b4-9f86-0161f90ec98f/scratchpad/dbg_{tag}.png'
    bpy.ops.render.render(write_still=True)
