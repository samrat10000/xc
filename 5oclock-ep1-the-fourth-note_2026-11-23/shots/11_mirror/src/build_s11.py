"""5 O'CLOCK Ep1 "The Fourth Note" - shot 11 "In the mirror" (3.5 s, 84 f @24). Over Sam's shoulder into the curve mirror, slow push.
Outside: the golden 5 PM crossroads of shot 02. Inside the glass (comp, paint_night11.py): night, the whole town standing in the road facing
him, the sky over the mountains cracked like glass with something huge behind it. Sam stands in the foreground, headphones at his neck (09).
Reuses the shot 02 set (exec of build_s02.py up to its camera); the glass renders key-green and comp_s11.py maps the night insert into it.
usage: blender -b --python build_s11.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math, json
A11 = sys.argv[sys.argv.index('--') + 1:]
H11 = os.path.dirname(os.path.abspath(__file__))
S02 = os.path.normpath(os.path.join(H11, '..', '..', '02_mirror', 'src'))
_s = open(os.path.join(S02, 'build_s02.py'), encoding='utf-8').read()
_s = _s[:_s.index('# --- camera')]
_s = _s.replace("HERE = os.path.dirname(os.path.abspath(__file__))", "HERE = %r" % S02)
sys.argv = [sys.argv[0], '--'] + A11
exec(_s)
from mathutils import Quaternion, Matrix
from bpy_extras.object_utils import world_to_camera_view
NF = 84
for o in bpy.data.objects:
    if o.name.startswith('leaf'): o.hide_render = True

# ---------------- Sam, standing in the foreground (approved toon Sam), arms down, headphones at his neck ----------------
SAMB = os.path.normpath(os.path.join(H11, '..', '..', '..', 'assets', 'toon_sam', 'sam_toon.blend'))
with bpy.data.libraries.load(SAMB, link=False) as (src, dst):
    dst.objects = [n for n in src.objects]
SAM = [o for o in dst.objects if o is not None and o.type not in ('LIGHT', 'CAMERA')]
for o in SAM: sc.collection.objects.link(o)
rig = next(o for o in SAM if o.type == 'ARMATURE' and o.parent is None)
for pb in rig.pose.bones: pb.rotation_mode = 'QUATERNION'


def rot(bone, ax, deg):
    pb = rig.pose.bones[bone]; b = rig.data.bones[bone]
    pb.rotation_quaternion = Quaternion((b.matrix_local.to_3x3().inverted() @ Vector(ax)).normalized(), math.radians(deg)) @ pb.rotation_quaternion


GROUND = 0.0
SPOS = MPOS - FWD * 1.9; SPOS.z = GROUND
rig.location = SPOS; rig.rotation_mode = 'XYZ'
yaw = math.atan2(FWD.y, FWD.x) - math.pi / 2                     # Sam faces the mirror (his front is -Y in rig space)
rig.rotation_euler = (0, 0, yaw + math.pi)
rot('J_Bip_L_UpperArm', (0, 1, 0), 70); rot('J_Bip_R_UpperArm', (0, 1, 0), -70)
rot('J_Bip_C_Neck', (1, 0, 0), -10); rot('J_Bip_C_Head', (1, 0, 0), -12)        # looking up into the mirror
bpy.context.view_layer.update()
HP_OBJS = [o for o in SAM if o.name.startswith('Headphone') and o.parent == rig]
HEADW = rig.matrix_world @ rig.pose.bones['J_Bip_C_Head'].head
piv = HEADW + Vector((0, 0, 0.09)); side = (rig.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
back = (rig.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
M = Matrix.Translation(Vector((0, 0, -0.205)) - back * 0.02) @ Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-78), 4, side) @ Matrix.Translation(-piv)
for o in HP_OBJS:
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = M @ mw
bpy.context.view_layer.update()
lowest = min((o.matrix_world @ v.co).z for o in SAM if o.type == 'MESH' and o.name.startswith('Body') for v in o.data.vertices)
rig.location.z += GROUND - lowest

# ---------------- camera: over his right shoulder, looking up into the glass, slow push ----------------
cam_d = bpy.data.cameras.new('cam'); cam_d.lens = 40; cam_d.sensor_fit = 'VERTICAL'; cam_d.sensor_height = 36
cam_d.clip_start = 0.05; cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 2.4
cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
bpy.context.view_layer.update()
HEADW = rig.matrix_world @ rig.pose.bones['J_Bip_C_Head'].head


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def cam11(f):
    k = ease((f - 1) / 83.0)
    p0 = HEADW - FWD * 0.42 - side * 0.12 + Vector((0, 0, 0.02))
    p = p0.lerp(MPOS - FWD * 1.25 - side * 0.12, 0.22 * k) + Vector((0.004 * math.sin(f * 0.21), 0, 0.003 * math.sin(f * 0.33)))
    cam_d.lens = 40 + 10 * k; cam_d.dof.focus_distance = (MPOS - p).length
    tgt = MPOS + (HEADW - MPOS) * (0.16 * (1 - k) + 0.05)
    return p, (tgt - p).to_track_quat('-Z', 'Y')


META = {}
frames = list(range(1, NF + 1)) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    sc.frame_set(f)
    p, q = cam11(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    c = world_to_camera_view(sc, cam, MPOS); e = world_to_camera_view(sc, cam, MPOS + SIDE * R)
    s_ = world_to_camera_view(sc, cam, cam.location + SUN * 100)
    META[f] = dict(mx=c.x, my=1 - c.y, mr=abs(e.x - c.x), sx=s_.x, sy=1 - s_.y, leaf=[0, 0, False])
    sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    print('frame', f, flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
print('SUN', META[frames[0]]['sx'], META[frames[0]]['sy'])
