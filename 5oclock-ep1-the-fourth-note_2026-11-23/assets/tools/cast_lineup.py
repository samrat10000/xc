"""G3 check: Sam + the cast at TRUE relative scale, arms down, front and side, one image.
usage: blender -b -P cast_lineup.py -- <castdir> <out.png>"""
import bpy, os, sys, math
from mathutils import Vector, Quaternion
a = sys.argv[sys.argv.index('--') + 1:]
CAST, OUT = a[0], a[1]
HERE = os.path.dirname(os.path.abspath(__file__))
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
files = [os.path.join(HERE, '..', 'toon_sam', 'sam_toon.blend')] + [os.path.join(CAST, n + '.blend') for n in ('grandma', 'shopkeeper', 'kid_girl', 'kid_boy')]
rigs = []
for i, fp in enumerate(files):
    before = set(bpy.data.objects)
    with bpy.data.libraries.load(fp, link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    new = [o for o in dst.objects if o is not None]
    for o in new:
        if o.type in ('LIGHT', 'CAMERA'): continue
        sc.collection.objects.link(o)
    rig = next(o for o in new if o.type == 'ARMATURE' and o.parent is None)
    rig.location.x += (i - 2) * 0.62
    rigs.append(rig)
    for side, sg in (('L', 1), ('R', -1)):                          # arms down from the T-pose
        pb = rig.pose.bones.get('J_Bip_%s_UpperArm' % side)
        if pb:
            pb.rotation_mode = 'QUATERNION'
            ax = pb.bone.matrix_local.to_3x3().inverted() @ Vector((0, 1, 0))
            pb.rotation_quaternion = Quaternion(ax, math.radians(68 * sg)) @ pb.rotation_quaternion
sun = bpy.data.objects.new('Key', bpy.data.lights.new('Key', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.data.color = (1.0, 0.82, 0.62); sun.rotation_euler = Vector((-0.42, -0.84, 0.30)).to_track_quat('Z', 'Y').to_euler()
cd = bpy.data.cameras.new('c'); cd.type = 'ORTHO'; cd.ortho_scale = 3.3
cam = bpy.data.objects.new('c', cd); sc.collection.objects.link(cam); sc.camera = cam
sc.render.engine = 'BLENDER_EEVEE'; sc.render.film_transparent = False
sc.world = bpy.data.worlds.new('w'); sc.world.color = (0.55, 0.55, 0.58)
sc.view_settings.view_transform = 'Standard'; sc.render.resolution_x, sc.render.resolution_y = 1400, 760
base = OUT[:-4]
cam.location = (0, -6, 0.85); cam.rotation_euler = (math.radians(90), 0, 0)
sc.render.filepath = base + '_front.png'; bpy.ops.render.render(write_still=True)
for i, r in enumerate(rigs):                                         # side view: turn each to profile in place
    r.rotation_mode = 'XYZ'; r.rotation_euler = (0, 0, math.radians(90))
sc.render.filepath = base + '_side.png'; bpy.ops.render.render(write_still=True)
print('LINEUP', base)
