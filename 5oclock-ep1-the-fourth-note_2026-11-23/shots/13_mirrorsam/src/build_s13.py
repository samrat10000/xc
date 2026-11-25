"""5 O'CLOCK Ep1 "The Fourth Note" - shot 13 "Mirror-Sam" (3 s, 72 f @24). Close on the curve mirror over Sam's shoulder. Sam turns his head
away (f18); his reflection does not. It keeps looking at us, smiles slowly, says "Your turn" (f56) and lifts a finger to its lips.
The reflection is a second Sam rendered in a separate NIGHT-lit pass (msam_NNN.png, 1200x1200) and placed in the glass over the night street
(comp). It is NOT mirrored (his hair parts the wrong way for a reflection) and its eyes have no catch-lights.
usage: blender -b --python build_s13.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math, json
A13 = sys.argv[sys.argv.index('--') + 1:]
H13 = os.path.dirname(os.path.abspath(__file__))
S11 = os.path.normpath(os.path.join(H13, '..', '..', '11_mirror', 'src'))
_s = open(os.path.join(S11, 'build_s11.py'), encoding='utf-8').read()
_s = _s[:_s.index('META = {}')]
_s = _s.replace("H11 = os.path.dirname(os.path.abspath(__file__))", "H11 = %r" % S11)
sys.argv = [sys.argv[0], '--'] + A13
__file__ = os.path.join(S11, 'build_s11.py')
exec(_s)
from mathutils import Quaternion
NF = 72

# ---------------- the reflection: a second Sam, far away from the set, lit for night ----------------
with bpy.data.libraries.load(SAMB, link=False) as (src, dst):
    dst.objects = [n for n in src.objects]
MS = [o for o in dst.objects if o is not None and o.type not in ('LIGHT', 'CAMERA')]
for o in MS: sc.collection.objects.link(o)
mrig = next(o for o in MS if o.type == 'ARMATURE' and o.parent is None)
MPOS2 = Vector((200.0, 200.0, 0.0))
mrig.location = MPOS2; mrig.rotation_mode = 'XYZ'; mrig.rotation_euler = (0, 0, 0)          # faces -Y = toward camera B
for pb in mrig.pose.bones: pb.rotation_mode = 'QUATERNION'
DARK = emis('noglint13', (0.02, 0.02, 0.03))
for o in MS:
    if o.type == 'MESH':
        for i, ms in enumerate(o.material_slots):
            if ms.material and ms.material.name.startswith('Sam_EyeHighlight'): o.material_slots[i].material = DARK   # no catch-light
MFACE = next(o for o in MS if o.type == 'MESH' and o.name.startswith('Face') and not o.name.startswith('Face_Outline'))
MK = MFACE.data.shape_keys.key_blocks
# headphones at his neck too (same as Sam)
bpy.context.view_layer.update()
mh = mrig.matrix_world @ mrig.pose.bones['J_Bip_C_Head'].head
mpiv = mh + Vector((0, 0, 0.09)); mside = Vector((1, 0, 0)); mback = Vector((0, 1, 0))
MM = Matrix.Translation(Vector((0, 0, -0.205)) - mback * 0.02) @ Matrix.Translation(mpiv) @ Matrix.Rotation(math.radians(-78), 4, mside) @ Matrix.Translation(-mpiv)
for o in [o for o in MS if o.name.startswith('Headphone') and o.parent == mrig]:
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = MM @ mw


def mrot(bone, ax, deg):
    pb = mrig.pose.bones[bone]; b = mrig.data.bones[bone]
    pb.rotation_quaternion = Quaternion((b.matrix_local.to_3x3().inverted() @ Vector(ax)).normalized(), math.radians(deg)) @ pb.rotation_quaternion


mrot('J_Bip_L_UpperArm', (0, 1, 0), 72); mrot('J_Bip_R_UpperArm', (0, 1, 0), -72)
MBASE = {pb.name: pb.matrix_basis.copy() for pb in mrig.pose.bones}
# finger to the lips: IK on the right arm to a target at his mouth; fingers curled except the index
bpy.context.view_layer.update()
mouth = mrig.matrix_world @ mrig.pose.bones['J_Bip_C_Head'].head + Vector((-0.01, -0.12, -0.085))   # IK places the WRIST: the index then lands on the lips
hand_rest = mrig.matrix_world @ mrig.pose.bones['J_Bip_R_Hand'].head + Vector((0, 0, -0.5))
TGT = bpy.data.objects.new('ms_tgt', None); sc.collection.objects.link(TGT)
POLE = bpy.data.objects.new('ms_pole', None); sc.collection.objects.link(POLE); POLE.location = MPOS2 + Vector((-0.55, -0.15, 0.85))          # elbow down at his side: only the hand rises
ik = mrig.pose.bones['J_Bip_R_LowerArm'].constraints.new('IK'); ik.target = TGT; ik.pole_target = POLE; ik.chain_count = 2; ik.pole_angle = 0
for fn in ('Middle', 'Ring', 'Little', 'Thumb'):
    for j in (1, 2, 3):
        b = mrig.pose.bones.get('J_Bip_R_%s%d' % (fn, j))
        if b: b.rotation_quaternion = Quaternion((0, 0, 1), math.radians(-70 if fn != 'Thumb' else -30)) @ b.rotation_quaternion
FINGER_BASE = {pb.name: pb.matrix_basis.copy() for pb in mrig.pose.bones if 'Middle' in pb.name or 'Ring' in pb.name or 'Little' in pb.name or 'Thumb' in pb.name}

# camera B for the reflection pass
camB_d = bpy.data.cameras.new('camB'); camB_d.lens = 46; camB_d.sensor_fit = 'VERTICAL'; camB_d.sensor_height = 36
camB = bpy.data.objects.new('camB', camB_d); sc.collection.objects.link(camB)
camB.location = MPOS2 + Vector((0.03, -0.80, 1.60)); camB.rotation_mode = 'QUATERNION'
camB.rotation_quaternion = ((MPOS2 + Vector((0, 0, 1.56))) - camB.location).to_track_quat('-Z', 'Y')
# night lights for the reflection pass only
DAY = [o for o in bpy.data.objects if o.type == 'LIGHT']
NIGHT = []
for name, travel, en, col in (('moon13', (0.4, 0.8, -0.6), 1.4, (0.55, 0.65, 1.0)), ('lamp13', (-0.7, -0.4, -0.5), 2.6, (1.0, 0.82, 0.52))):
    o = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SUN')); sc.collection.objects.link(o)
    o.data.energy = en; o.data.color = col; o.rotation_euler = Vector(travel).to_track_quat('-Z', 'Y').to_euler(); o.hide_render = True
    NIGHT.append(o)


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


SAM_BASE = {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}


def act(f):
    fp = f - (f - 1) % 2
    # real Sam turns his head away (looks back over his shoulder at the street)
    for pb in rig.pose.bones: pb.matrix_basis = SAM_BASE[pb.name].copy()
    turn = ease((fp - 18) / 6.0)
    rot('J_Bip_C_Neck', (0, 0, 1), 28 * turn); rot('J_Bip_C_Head', (0, 0, 1), 18 * turn)
    # the reflection: does not turn; tiny head tilt, slow smile, line, finger to lips
    for pb in mrig.pose.bones: pb.matrix_basis = MBASE[pb.name].copy()
    for n, m in FINGER_BASE.items(): mrig.pose.bones[n].matrix_basis = m.copy()
    mrot('J_Bip_C_Head', (0, 1, 0), 4 * ease((fp - 24) / 20.0))
    smile = ease((fp - 26) / 22.0)
    for k in ('MTH_Fun', 'ALL_Fun'):
        kb = MK.get('Face.M_F00_000_00_Fcl_' + k)
        if kb: kb.value = (0.55 if k == 'MTH_Fun' else 0.18) * smile
    for v in 'AIUEO': MK['Face.M_F00_000_00_Fcl_MTH_' + v].value = 0.0
    for v, a, b_, amp in (('U', 56, 60, 0.35), ('A', 60, 64, 0.30)):
        if a <= fp < b_: MK['Face.M_F00_000_00_Fcl_MTH_' + v].value = amp * math.sin(math.pi * (fp - a) / (b_ - a))
    up = ease((fp - 62) / 8.0)
    TGT.location = hand_rest.lerp(mouth, up); ik.influence = up
    MK['Face.M_F00_000_00_Fcl_EYE_Close'].value = 0.0                 # he never blinks


def cam13(f):
    k = ease((f - 1) / 71.0)
    p = HEADW - FWD * 0.45 - side * 0.14 + Vector((0, 0, 0.02))
    p = p.lerp(MPOS - FWD * 0.95, 0.06 + 0.12 * k)               # his real head stays at the frame edge
    cam_d.lens = 48 + 8 * k; cam_d.dof.focus_distance = (MPOS - p).length
    tgt = MPOS + (HEADW - MPOS) * 0.06
    return p, (tgt - p).to_track_quat('-Z', 'Y')


META = {}
frames = list(range(1, NF + 1)) if FR == 'all' else [int(x) for x in FR.split(',')]
RX, RY = sc.render.resolution_x, sc.render.resolution_y
for f in frames:
    sc.frame_set(f); act(f)
    p, q = cam13(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    c = world_to_camera_view(sc, cam, MPOS); e = world_to_camera_view(sc, cam, MPOS + SIDE * R)
    s_ = world_to_camera_view(sc, cam, cam.location + SUN * 100)
    META[f] = dict(mx=c.x, my=1 - c.y, mr=abs(e.x - c.x), sx=s_.x, sy=1 - s_.y, leaf=[0, 0, False])
    sc.camera = cam; sc.render.resolution_x, sc.render.resolution_y = RX, RY
    sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    # the reflection pass: night lights only, square
    for o in DAY: o.hide_render = True
    for o in NIGHT: o.hide_render = False
    sc.camera = camB; sc.render.resolution_x = sc.render.resolution_y = 1200
    sc.render.filepath = os.path.join(OUT, 'msam_%03d.png' % f); bpy.ops.render.render(write_still=True)
    for o in DAY: o.hide_render = False
    for o in NIGHT: o.hide_render = True
    print('frame', f, flush=True)
sc.camera = cam
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
print('SUN', META[frames[0]]['sx'], META[frames[0]]['sy'])
