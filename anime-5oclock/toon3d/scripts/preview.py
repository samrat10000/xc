import bpy, sys, math
bpy.ops.wm.open_mainfile(filepath=sys.argv[-2])
sc=bpy.context.scene
sc.render.engine='BLENDER_EEVEE'
sc.render.resolution_x=800; sc.render.resolution_y=800
cam=bpy.data.cameras.new('c'); co=bpy.data.objects.new('c',cam); sc.collection.objects.link(co); sc.camera=co
cam.type='ORTHO'
import mathutils
views=[]
out=sys.argv[-1]
for i,(ang,z,s) in enumerate([(0,1.0,2.1),(0,1.72,0.45),(90,1.72,0.45)]):
    a=math.radians(ang)
    co.location=(3*math.sin(a),-3*math.cos(a),z); co.rotation_euler=(math.radians(90),0,a)
    cam.ortho_scale=s
    w=bpy.data.worlds.new('w') if not sc.world else sc.world; sc.world=w
    sc.render.filepath=out+f"_{i}.png"; bpy.ops.render.render(write_still=True)
