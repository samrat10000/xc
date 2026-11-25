"""Shots 11-14 v2: the town in the night mirror as REAL 3D people (Sam: no flat painted people at readable size; "the night
painting in the glass can be improved"). Renders each cast member (grandma, shopkeeper, kid_boy, kid_girl, mom) in 3 stances,
front view, orthographic, RGBA, plus sprites.json (feet, head top, eye positions in pixels). paint_night11 pastes them as dark
figures with the form still faintly visible, a warm lamp rim and pale eyes.
usage: blender -b --factory-startup --python build_crowd_sprites.py -- <ABS outdir>"""
import os, sys, json, math
import bpy
from mathutils import Vector, Quaternion, Matrix
from bpy_extras.object_utils import world_to_camera_view

OUT = sys.argv[sys.argv.index('--') + 1]; os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
CASTD = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'assets', 'cast_v2'))
sc = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
sc.render.engine = 'BLENDER_EEVEE' if 'BLENDER_EEVEE' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE_NEXT'
sc.render.film_transparent = True; sc.render.resolution_x = 520; sc.render.resolution_y = 1040
sc.view_settings.view_transform = 'Standard'
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(50), 0, math.radians(30))
cd = bpy.data.cameras.new('cam'); cd.type = 'ORTHO'; cam = bpy.data.objects.new('cam', cd); sc.collection.objects.link(cam); sc.camera = cam


def load(name):
    with bpy.data.libraries.load(os.path.join(CASTD, name + '.blend'), link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    new = [o for o in dst.objects if o is not None and o.type not in ('LIGHT', 'CAMERA')]
    for o in new: sc.collection.objects.link(o)
    rig = next(o for o in new if o.type == 'ARMATURE' and o.parent is None)
    rig.location = (0, 0, 0); rig.rotation_mode = 'XYZ'; rig.rotation_euler = (0, 0, 0)       # VRM faces -Y
    for pb in rig.pose.bones: pb.rotation_mode = 'QUATERNION'
    if 'kid' in name:
        for b in rig.data.bones:
            if any(k in b.name for k in ('Arm', 'Hand', 'Index', 'Middle', 'Ring', 'Little', 'Thumb', 'Leg', 'Foot', 'Toe')): b.inherit_scale = 'FIX_SHEAR'
    return rig, new


def rot(rig, bone, axis, deg):
    pb = rig.pose.bones.get(bone)
    if pb is None: return
    ax = pb.bone.matrix_local.to_3x3().inverted() @ Vector(axis)
    pb.rotation_quaternion = Quaternion(ax, math.radians(deg)) @ pb.rotation_quaternion


def stance(rig, k, base):
    for pb in rig.pose.bones: pb.matrix_basis = base[pb.name].copy() if rig.name.startswith('grandma') else Matrix.Identity(4)   # v2: from rest (like shot 16)
    rot(rig, 'J_Bip_L_UpperArm', (0, 1, 0), 80 - 3 * k); rot(rig, 'J_Bip_R_UpperArm', (0, 1, 0), -(78 - 2 * k))
    rot(rig, 'J_Bip_L_LowerArm', (0, 0, 1), -18 - 8 * k); rot(rig, 'J_Bip_R_LowerArm', (0, 0, 1), 16 + 8 * k)
    side = (1, -1, 1)[k]
    rot(rig, 'J_Bip_C_Hips', (0, -1, 0), 3 * side); rot(rig, 'J_Bip_C_Spine', (0, -1, 0), -2 * side)
    soft = 'J_Bip_R_' if side > 0 else 'J_Bip_L_'
    rot(rig, soft + 'UpperLeg', (1, 0, 0), -5); rot(rig, soft + 'LowerLeg', (1, 0, 0), 9)
    if k == 1: rot(rig, 'J_Bip_C_Head', (0, -1, 0), 17); rot(rig, 'J_Bip_C_Neck', (0, -1, 0), 6)      # the head tilted a little too far
    if k == 2:                                                                                          # arms hanging forward, chin down
        rot(rig, 'J_Bip_L_UpperArm', (1, 0, 0), -18); rot(rig, 'J_Bip_R_UpperArm', (1, 0, 0), -18); rot(rig, 'J_Bip_C_Head', (1, 0, 0), 9)
    bpy.context.view_layer.update()


META = {}
for name in ('grandma', 'shopkeeper', 'kid_boy', 'kid_girl', 'mom'):
    rig, objs = load(name); base = {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}
    for o in objs:
        if o.type == 'MESH' and o.name.startswith('Mom_apron'): o.hide_render = True
    for k in range(3):
        stance(rig, k, base)
        dg = bpy.context.evaluated_depsgraph_get(); zs = []
        for o in objs:
            if o.type != 'MESH' or o.hide_render: continue
            ev = o.evaluated_get(dg); me = ev.to_mesh(); zs += [(o.matrix_world @ v.co).z for v in list(me.vertices)[::9]]; ev.to_mesh_clear()
        z0, z1 = min(zs), max(zs); hgt = z1 - z0
        cd.ortho_scale = 2.0; cam.location = (0, -6, z0 + 1.0); cam.rotation_euler = (math.radians(90), 0, 0)
        bpy.context.view_layer.update()
        hm = rig.matrix_world @ rig.pose.bones['J_Bip_C_Head'].matrix
        eyes = []
        for bn in ('J_Adj_L_FaceEye', 'J_Adj_R_FaceEye'):
            pb = rig.pose.bones.get(bn)
            w = rig.matrix_world @ (pb.head if pb else (rig.pose.bones['J_Bip_C_Head'].head + Vector((0.03 if 'L' in bn else -0.03, -0.08, 0.06))))
            v = world_to_camera_view(sc, cam, w); eyes.append((v.x * 520, (1 - v.y) * 1040))
        feet = world_to_camera_view(sc, cam, Vector((0, 0, z0))); top = world_to_camera_view(sc, cam, Vector((0, 0, z1)))
        fn = '%s_%d.png' % (name, k); sc.render.filepath = os.path.join(OUT, fn); bpy.ops.render.render(write_still=True)
        META[fn] = dict(feet=(feet.x * 520, (1 - feet.y) * 1040), top=(top.x * 520, (1 - top.y) * 1040), eyes=eyes, height_m=hgt)
        print('sprite', fn, round(hgt, 2), flush=True)
    for o in objs: bpy.data.objects.remove(o)
json.dump(META, open(os.path.join(OUT, 'sprites.json'), 'w'), indent=1)
