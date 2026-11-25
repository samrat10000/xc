"""5 O'CLOCK Ep1 v3 - NEW shot 10b "Arrive" (2 s, 48 f @24). Sam v2 note: "add one scene when Sam stops with his bicycle at the
mirror where everything is black inside" - it established nothing before the crowd appeared.
Wide, behind his right shoulder at the shot-02 crossroads: Sam stands beside his mamachari, left hand on its grip; he settles
from the stop, then lifts his eyes (neck leads, head follows) to the curve mirror. The glass is pitch black (comp_s10b.py).
Reuses build_s11.py (02 set + toon Sam) up to its camera, and the shot-04 bike (bike.py needs only toonlib_v4).
usage: blender -b --python build_s10b.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math, json
A = sys.argv[sys.argv.index('--') + 1:]
H = os.path.dirname(os.path.abspath(__file__))
S11 = os.path.normpath(os.path.join(H, '..', '..', '11_mirror', 'src'))
S04 = os.path.normpath(os.path.join(H, '..', '..', '04_ride', 'src'))
_s = open(os.path.join(S11, 'build_s11.py'), encoding='utf-8').read()
_s = _s[:_s.index('# ---------------- camera')]
_s = _s.replace("H11 = os.path.dirname(os.path.abspath(__file__))", "H11 = %r" % S11)
sys.argv = [sys.argv[0], '--'] + A
exec(_s)
from mathutils import Quaternion, Matrix
NF = 48
# v4 (Sam: "the headphones are hanging from his hood cap"; "a faint black wire on the left"):
# from behind, the s11 neck pose left the band across his shoulder blades. Lift it to the nape (cups on the collarbones, as in 09).
_up = Matrix.Translation(Vector((0, 0, 0.075)) + FWD * 0.045)
for o in HP_OBJS: o.matrix_world = _up @ o.matrix_world
for o in bpy.data.objects:                                       # the loose wire strands of the 02 set read as a stray black line here
    if o.type == 'CURVE' and not o.name.startswith('txt'): o.hide_render = True          # every wire curve of the 02 set
    elif o.type == 'MESH' and any(m and m.name.startswith('wire') for m in o.data.materials): o.hide_render = True

# ---------------- the bike, parked on his left, front wheel toward the mirror ----------------
exec(open(os.path.join(S04, 'bike.py'), encoding='utf-8').read())
LEFT = -side                                                      # his left (side = his +X = his left in rig space? measured below)
broot = empty('bike_parent'); bpy.context.view_layer.update()
hipw = rig.matrix_world @ rig.pose.bones['J_Bip_C_Hips'].head
sx_ = (rig.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()   # VRM +X = the character's left
B = make_bike(broot)
yawb = math.atan2(FWD.y, FWD.x)
broot.rotation_euler = (0, 0, yawb); bpy.context.view_layer.update()


def PB(n): return rig.pose.bones[n]


# v3 probe: the arm could not reach (bike placed by guess). Now: the arm on the bike side is found from the skeleton, the bike is
# placed so its NEAR grip sits where that hand naturally hangs (52 cm below the shoulder, a little forward and out).
SIDE_L = (rig.matrix_world @ PB('J_Bip_L_UpperArm').head - hipw).dot(sx_) > 0
HS = 'L' if SIDE_L else 'R'                                       # the hand on the +sx_ side holds the bike
shw = rig.matrix_world @ PB('J_Bip_%s_UpperArm' % HS).head
G = shw + Vector((0, 0, -0.50)) + FWD * 0.14 + sx_ * 0.10
best = None
for gi in (0, 1):
    gl = B['grips'][gi]
    rotm = broot.matrix_world.to_3x3()
    root = G - rotm @ gl
    centre = root + rotm @ Vector((0.55, 0, 0))
    away = (centre - hipw).dot(sx_)                                # the bike body must be OUTSIDE him, not through him
    if best is None or away > best[0]: best = (away, gi, root)
_, GI, root = best
broot.location = Vector((root.x, root.y, 0.0)); bpy.context.view_layer.update()
g_w = B['root'].matrix_world @ B['grips'][GI]
tgt = empty('g10_t'); tgt.location = g_w + Vector((0, 0, 0.03)) - FWD * 0.05
aim = empty('g10_a'); aim.location = g_w + FWD * 0.12 - sx_ * 0.03 - Vector((0, 0, 0.03))
pole = empty('g10_p'); pole.location = shw + sx_ * 0.35 - FWD * 0.35 + Vector((0, 0, -0.35)) + 0 * hipw - FWD * 0.45 + Vector((0, 0, -0.2))
c = PB('J_Bip_%s_LowerArm' % HS).constraints.new('IK'); c.target = tgt; c.pole_target = pole; c.chain_count = 2
hc = PB('J_Bip_%s_Hand' % HS).constraints.new('DAMPED_TRACK'); hc.target = aim; hc.track_axis = 'TRACK_Y'

# v2 render: the free arm's FK pose bent it behind his back. Pin it with IK: hand hangs beside his thigh, elbow back and out.
FS = 'R' if HS == 'L' else 'L'
shf = rig.matrix_world @ PB('J_Bip_%s_UpperArm' % FS).head
ft = empty('free_t'); ft.location = Vector((shf.x, shf.y, 0)) - sx_ * 0.06 + FWD * 0.03 + Vector((0, 0, hipw.z - 0.12))
fp_ = empty('free_p'); fp_.location = shf - sx_ * 0.25 - FWD * 0.30 + Vector((0, 0, -0.30))
cf = PB('J_Bip_%s_LowerArm' % FS).constraints.new('IK'); cf.target = ft; cf.pole_target = fp_; cf.chain_count = 2
BASE = {pb.name: pb.rotation_quaternion.copy() for pb in rig.pose.bones}
for n_ in [pb.name for pb in rig.pose.bones if pb.name.startswith('J_Bip_%s_' % HS) and any(k in pb.name for k in ('Index', 'Middle', 'Ring', 'Little'))]:
    b_ = rig.data.bones[n_]; ax = (b_.matrix_local.to_3x3().inverted() @ Vector((0, 1, 0))).normalized()
    BASE[n_] = Quaternion(ax, math.radians(-48)) @ BASE[n_]       # fingers round the grip


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def act(f):
    for n_, q_ in BASE.items(): rig.pose.bones[n_].rotation_quaternion = q_.copy()
    settle = math.exp(-f / 7.0) * math.sin(f * 0.42)                  # the stop's follow-through: a small rock, damped
    breath = math.sin(f * 0.26) * (0.6 + 0.4 * math.exp(-f / 20))     # still out of breath from the ride
    lift_n = ease((f - 14) / 14.0); lift_h = ease((f - 17) / 15.0)    # neck leads, head follows (overlap)
    rot('J_Bip_C_Spine', (1, 0, 0), 6 * settle + 1.2 * breath + 4 * (1 - lift_n))
    rot('J_Bip_C_Chest', (1, 0, 0), 0.8 * breath)
    rot('J_Bip_C_Neck', (1, 0, 0), 14 * (1 - lift_n) - 6 * lift_n)    # head down at the road -> up at the glass
    rot('J_Bip_C_Head', (1, 0, 0), 10 * (1 - lift_h) - 14 * lift_h)
    rot('J_Bip_C_Head', (0, 0, 1), 4 * math.sin(f * 0.11) * (1 - lift_h))
    FS = 'R' if HS == 'L' else 'L'; sg_ = 1 if FS == 'R' else -1
    # free arm: the s11 hang (an extra bend twisted it behind his back): soft elbow, not a plank
    rot('J_Bip_R_UpperLeg', (1, 0, 0), -3); rot('J_Bip_R_LowerLeg', (1, 0, 0), 6)  # weight on the left leg
    bpy.context.view_layer.update()


# ---------------- camera: wide, behind his right shoulder, a slow push + tilt from him up to the black glass ----------------
cam_d = bpy.data.cameras.new('cam'); cam_d.sensor_fit = 'VERTICAL'; cam_d.sensor_height = 36
cam_d.clip_start = 0.05; cam_d.clip_end = 2000; cam_d.dof.use_dof = True; cam_d.dof.aperture_fstop = 3.5
cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
bpy.context.view_layer.update()
HEADW = rig.matrix_world @ rig.pose.bones['J_Bip_C_Head'].head


def cam10b(f):
    k = ease((f - 1) / 47.0)
    p0 = HEADW - FWD * 3.0 - sx_ * 1.15 + Vector((0, 0, -0.55))
    p1 = HEADW - FWD * 2.2 - sx_ * 0.80 + Vector((0, 0, -0.35))
    p = p0.lerp(p1, k) + Vector((0.004 * math.sin(f * 0.23), 0, 0.003 * math.sin(f * 0.37)))
    tgt = (HEADW + Vector((0, 0, -0.35))).lerp(MPOS + Vector((0, 0, -0.25)), 0.35 + 0.45 * k)
    cam_d.lens = 30 + 6 * k; cam_d.dof.focus_distance = (HEADW - p).length
    return p, (tgt - p).to_track_quat('-Z', 'Y')


META = {}
frames = list(range(1, NF + 1)) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    sc.frame_set(f); act(f)
    p, q = cam10b(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    c_ = world_to_camera_view(sc, cam, MPOS); e = world_to_camera_view(sc, cam, MPOS + SIDE * R)
    s_ = world_to_camera_view(sc, cam, cam.location + SUN * 100)
    META[f] = dict(mx=c_.x, my=1 - c_.y, mr=abs(e.x - c_.x), sx=s_.x, sy=1 - s_.y, leaf=[0, 0, False])
    sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    print('frame', f, flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
