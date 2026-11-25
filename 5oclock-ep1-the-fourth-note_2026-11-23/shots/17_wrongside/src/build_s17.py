"""5 O'CLOCK Ep1 "The Fourth Note" - shot 17 "The wrong side" (3 s, 72 f @24). Close two-shot: Sam and a curve mirror. In the glass
(comp, paint_day17.py): the real Kiriyama, warm and normal, his mother on their doorstep calling him; she can't see him.
He steps to the glass and presses his palm flat on it (IK, palm to the glass, fingers spread, no gap). Line "Mom...?" at f29.
Reuses shot 11's build (shot 02 set + toon Sam) with the mirror lowered to hand height for this corner.
usage: blender -b --python build_s17.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math, json
A17 = sys.argv[sys.argv.index('--') + 1:]
H17 = os.path.dirname(os.path.abspath(__file__))
S11 = os.path.normpath(os.path.join(H17, '..', '..', '11_mirror', 'src'))
_s = open(os.path.join(S11, 'build_s11.py'), encoding='utf-8').read()
_s = _s[:_s.index('\n# ---------------- camera')]
_s = _s.replace("H11 = os.path.dirname(os.path.abspath(__file__))", "H11 = %r" % S11)
_s = _s.replace("_s = _s[:_s.index('# --- camera')]", "_s = _s[:_s.index('# --- camera')]\n_s = _s.replace('MPOS = FWD * 3.0 + SIDE * 0.0 + Vector((0, 0, 2.55))', 'MPOS = FWD * 3.0 + SIDE * 0.0 + Vector((0, 0, 1.62))')")
_s = _s.replace("SPOS = MPOS - FWD * 1.9; SPOS.z = GROUND", "SPOS = MPOS - FWD * 0.80; SPOS.z = GROUND")
_s = _s.replace("rot('J_Bip_C_Neck', (1, 0, 0), -10); rot('J_Bip_C_Head', (1, 0, 0), -12)", "rot('J_Bip_C_Head', (1, 0, 0), 4)")
sys.argv = [sys.argv[0], '--'] + A17
__file__ = os.path.join(S11, 'build_s11.py')
exec(_s)
from mathutils import Quaternion, Matrix
from bpy_extras.object_utils import world_to_camera_view
NF = 72
print('MPOS', tuple(round(x, 2) for x in MPOS))

# ---------------- the hand on the glass ----------------
GLASS_PT = MPOS - FWD * 0.035 + SIDE * 0.06 + Vector((0, 0, -0.04))
T = bpy.data.objects.new('t17', None); sc.collection.objects.link(T)
AIM = bpy.data.objects.new('aim17', None); sc.collection.objects.link(AIM)
PALM = bpy.data.objects.new('palm17', None); sc.collection.objects.link(PALM)
POLE = bpy.data.objects.new('pole17', None); sc.collection.objects.link(POLE)
c1 = rig.pose.bones['J_Bip_R_LowerArm'].constraints.new('IK'); c1.target = T; c1.pole_target = POLE; c1.chain_count = 2; c1.pole_angle = 0
c2 = rig.pose.bones['J_Bip_R_Hand'].constraints.new('DAMPED_TRACK'); c2.target = AIM; c2.track_axis = 'TRACK_Y'
hb = rig.data.bones['J_Bip_R_Hand']; R0 = hb.matrix_local.to_3x3()
best = max((('TRACK_X', R0.col[0]), ('TRACK_NEGATIVE_X', -R0.col[0]), ('TRACK_Z', R0.col[2]), ('TRACK_NEGATIVE_Z', -R0.col[2])), key=lambda a: a[1].dot(Vector((0, 0, -1))))
c3 = rig.pose.bones['J_Bip_R_Hand'].constraints.new('LOCKED_TRACK'); c3.target = PALM; c3.lock_axis = 'LOCK_Y'; c3.track_axis = best[0]
for fn in ('Index', 'Middle', 'Ring', 'Little'):                            # fingers spread flat on the glass
    b = rig.pose.bones.get('J_Bip_R_%s1' % fn)
    if b: b.rotation_quaternion = Quaternion((0, 0, 1), math.radians({'Index': 9, 'Middle': 2, 'Ring': -5, 'Little': -11}[fn])) @ b.rotation_quaternion
FACE = next(o for o in SAM if o.type == 'MESH' and o.name == 'Face')
SK = FACE.data.shape_keys.key_blocks
SAM_BASE = {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}
LOC0 = rig.location.copy()
bpy.context.view_layer.update()
HAND_REST = rig.matrix_world @ rig.pose.bones['J_Bip_R_Hand'].head


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def act(f):
    fp = f - (f - 1) % 2
    for c in (c1, c2, c3): c.influence = 0.0
    bpy.context.view_layer.update()
    for pb in rig.pose.bones: pb.matrix_basis = SAM_BASE[pb.name].copy()
    step = ease((fp - 1) / 12.0)
    rig.location = LOC0 + FWD * 0.34 * step                                      # one step to the glass
    press = ease((fp - 12) / 12.0)
    tr = 0.003 * math.sin(fp * 1.9) * ease((fp - 30) / 6.0)                     # the hand trembles, pressed flat
    T.location = HAND_REST.lerp(GLASS_PT - FWD * 0.01, press) + SIDE * tr
    AIM.location = T.location + Vector((0, 0, 0.30)) + SIDE * 0.04
    PALM.location = T.location + FWD * 0.5
    POLE.location = T.location - FWD * 0.35 + SIDE * 0.45 - Vector((0, 0, 0.35))
    for c in (c1, c2, c3): c.influence = press
    rot('J_Bip_C_Head', (1, 0, 0), 6 * press); rot('J_Bip_C_Neck', (0, 0, 1), -6 * ease((fp - 44) / 10.0))
    SK['Face.M_F00_000_00_Fcl_BRW_Sorrow'].value = 0.7 * ease((fp - 16) / 10.0)
    SK['Face.M_F00_000_00_Fcl_EYE_Close'].value = 0.25 * ease((fp - 40) / 8.0)
    for v in 'AIUEO': SK['Face.M_F00_000_00_Fcl_MTH_' + v].value = 0.0
    for v, a, b_, amp in (('O', 29, 33, 0.35), ('O', 34, 38, 0.25)):             # "Mom...?" - breaking, two small breaths
        if a <= fp < b_: SK['Face.M_F00_000_00_Fcl_MTH_' + v].value = amp * math.sin(math.pi * (fp - a) / (b_ - a))


cam_d = bpy.data.cameras.new('cam'); cam_d.lens = 42; cam_d.sensor_fit = 'VERTICAL'; cam_d.sensor_height = 36
cam_d.clip_start = 0.05; cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 2.4
cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam


def cam17(f):
    k = ease((f - 1) / 71.0)
    head = rig.matrix_world @ rig.pose.bones['J_Bip_C_Head'].head
    mid = head.lerp(MPOS, 0.45)
    p = mid - FWD * 0.55 + SIDE * 1.10 + Vector((0, 0, -0.05)) + (FWD * 0.10 - SIDE * 0.12) * k
    cam_d.dof.focus_distance = (head - p).length
    return p, (mid - p).to_track_quat('-Z', 'Y')


META = {}
frames = list(range(1, NF + 1)) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    sc.frame_set(f); act(f)
    bpy.context.view_layer.update()
    p, q = cam17(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    c = world_to_camera_view(sc, cam, MPOS); e = world_to_camera_view(sc, cam, MPOS + SIDE * R)
    s_ = world_to_camera_view(sc, cam, cam.location + SUN * 100)
    META[f] = dict(mx=c.x, my=1 - c.y, mr=abs(e.x - c.x), sx=s_.x, sy=1 - s_.y, leaf=[0, 0, False])
    sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    print('frame', f, flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
print('SUN', META[frames[0]]['sx'], META[frames[0]]['sy'])
