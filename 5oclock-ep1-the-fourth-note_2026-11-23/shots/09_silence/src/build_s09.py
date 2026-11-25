"""5 O'CLOCK Ep1 "The Fourth Note" - shot 09 "Silence" (3 s, 72 f @24). Close-up on Sam coasting: the music dies (battery 0%) at f12,
his right hand pulls the headphones down to his neck (f14-34), he brakes to a stop (f48), his left foot comes down and locks to the road,
he looks around and frowns. Line "...Hello?" at 29.8 s = f31. The camera rides with him in close-up, then settles to a medium as he stops.
Reuses the approved shot 04 rider + bike (exec of build_s04.py up to its render loop).
usage: blender -b --python build_s09.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math
H9 = os.path.dirname(os.path.abspath(__file__))
S04 = os.path.normpath(os.path.join(H9, '..', '..', '04_ride', 'src'))
_s = open(os.path.join(S04, 'build_s04.py'), encoding='utf-8').read()
_s = _s[:_s.index('META = {}')]
_s = _s.replace("HERE = os.path.dirname(os.path.abspath(__file__)); D = HERE", "HERE = %r; D = HERE" % S04)
exec(_s)
from mathutils import Quaternion
NF = 72
for o in R2['objs']: o.hide_render = True
for o in bpy.data.objects:
    if o.type == 'MESH' and any(m and m.name.startswith('susuki') for m in o.data.materials): o.hide_render = True
rig = R1['rig']; B = R1['B']; IK1 = R1['ik']; SK = R1['face'].data.shape_keys.key_blocks
STOP = 48


def sam_x(f):                                                   # coasting, then a smooth brake to a stop at f48
    t = min((f - 1) / 24.0, (STOP - 1) / 24.0)
    return 40.0 + 3.9 * t - 3.9 * t * t / 4.0


# ---------------- headphones: one pivot on the head bone; it slides down to the neck ----------------
HP_OBJS = [o for o in R1['objs'] if o.name.startswith('Headphone') and o.parent == rig]
bpy.context.view_layer.update()
HEADB = PB(rig, 'J_Bip_C_Head')
HP = bpy.data.objects.new('hp_pivot', None); sc.collection.objects.link(HP)
HP.parent = rig; HP.parent_type = 'BONE'; HP.parent_bone = 'J_Bip_C_Head'
bpy.context.view_layer.update()
HP.matrix_world = Matrix.Translation(rig.matrix_world @ HEADB.head + Vector((0, 0, 0.09)))
bpy.context.view_layer.update()
for o in HP_OBJS:
    mw = o.matrix_world.copy(); o.parent = HP; o.parent_type = 'OBJECT'; o.matrix_world = mw
HP_REST = HP.matrix_basis.copy()


def headphones(f):
    fp = f                                       # v3: on ones (natural hand motion)
    k = ease((fp - 18) / 12.0)                                   # down over half a second
    HP.matrix_basis = HP_REST
    bpy.context.view_layer.update()
    piv = HP.matrix_world.translation
    side = (rig.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()          # his left-right axis
    R = Matrix.Translation(piv) @ Matrix.Rotation(math.radians(-78 * k), 4, side) @ Matrix.Translation(-piv)
    T = Matrix.Translation(Vector((0, 0, -0.205 * k)) - (rig.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized() * 0.02 * k)
    HP.matrix_world = T @ R @ HP.matrix_world


# ---------------- hands, foot, head, face (layered on top of the 04 pose each frame) ----------------
hR = IK1['hand_R']; aL = IK1['ankle_L']
HR0 = hR.location.copy(); AL0 = aL.location.copy()     # targets are re-set every frame (no stale world matrices)
# v2 (Sam: "pulled down with a curled wrist - grab with four fingers"): the hand's aim + palm-roll targets also follow the cup;
# the four fingers relax from the bar-grip curl to a drape over the cup. Every target is reset each frame (J10).
_hc = PB(rig, 'J_Bip_R_Hand').constraints
AIM = next(c.target for c in _hc if c.type == 'DAMPED_TRACK'); PALM = next(c.target for c in _hc if c.type == 'LOCKED_TRACK')
AIM0, PALM0 = AIM.location.copy(), PALM.location.copy()
FING = {pb.name: pb.rotation_quaternion.copy() for pb in rig.pose.bones
        if pb.name.startswith('J_Bip_R_') and any(k in pb.name for k in ('Index', 'Middle', 'Ring', 'Little'))}


def act(f):
    fp = f                                       # v3: on ones (natural hand motion)
    hR.location = HR0; aL.location = AL0; AIM.location = AIM0; PALM.location = PALM0
    for n_, q_ in FING.items(): rig.pose.bones[n_].rotation_quaternion = q_.copy()
    bpy.context.view_layer.update()
    # right hand: grip -> the right ear cup (four fingers over its outer face, thumb under) -> pulls down with it -> back
    grip_w = hR.matrix_world.translation.copy(); aim_w = AIM.matrix_world.translation.copy(); palm_w = PALM.matrix_world.translation.copy()
    cup = next((o for o in HP_OBJS if o.name.startswith('Headphone_Cup_R')), None)
    if cup:
        cup_w = sum((cup.matrix_world @ Vector(c_) for c_ in cup.bound_box), Vector()) / 8.0   # the cup's real centre, not its origin
        hm = rig.matrix_world @ PB(rig, 'J_Bip_C_Head').matrix
        up = (hm.to_3x3() @ Vector((0, 1, 0))).normalized()                      # the head bone points up the head
        out = -(rig.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()      # his right
        k = ease((fp - 12) / 6.0) * (1 - ease((fp - 32) / 6.0))
        sl = ease((fp - 18) / 12.0)                                               # the slide down (same timing as headphones())
        band = (HP.matrix_world.translation - cup_w).normalized()                 # from the cup up along the band to its pivot
        # v3 (Sam: "his hand is going through the headphones"): measure the cup's real half-thickness along his right axis and
        # keep the palm 2.5 cm OUTSIDE its outer face (palm ~2 cm thick) - the hand holds the cup from outside, never inside it
        ht_ = max((cup.matrix_world @ Vector(c_) - cup_w).dot(out) for c_ in cup.bound_box)
        wrist = cup_w + out * (ht_ + 0.035) - band * (0.07 - 0.04 * sl)
        hR.matrix_world = Matrix.Translation(grip_w.lerp(wrist, k))
        AIM.matrix_world = Matrix.Translation(aim_w.lerp(cup_w + band * 0.16 + out * 0.03, k))  # fingers follow the band, riding the cup
        PALM.matrix_world = Matrix.Translation(palm_w.lerp(cup_w - out * 0.30, k))           # palm faces in, onto the cup
        for n_, q_ in FING.items():                                               # bar-grip fist -> 40 % drape over the rim
            rig.pose.bones[n_].rotation_quaternion = Quaternion((1, 0, 0, 0)).slerp(q_, 1.0 - 0.6 * k)
    # left foot: off the pedal, down to the road beside the bike, locked there
    pedal_w = aL.matrix_world.translation.copy()
    ground_w = B['root'].matrix_world @ Vector((0.18, 0.30, 0.09))
    kf = ease((fp - 40) / 8.0)
    aL.matrix_world = Matrix.Translation(pedal_w.lerp(ground_w, kf))
    B['root'].rotation_euler = (math.radians(-5.5 * kf), 0, 0)                   # the bike leans onto the planted foot

    def rot(name, ax, deg):
        pb = rig.pose.bones[name]; b = rig.data.bones[name]
        pb.rotation_quaternion = pb.rotation_quaternion @ Quaternion((b.matrix_local.to_3x3().inverted() @ Vector(ax)).normalized(), math.radians(deg))
    up = ease((fp - 44) / 8.0)                                                    # sits up as he stops
    rot('J_Bip_C_Spine', (1, 0, 0), -12 * up); rot('J_Bip_C_Neck', (1, 0, 0), -8 * up)
    look = (24 * ease((fp - 50) / 6.0) - 46 * ease((fp - 60) / 7.0))              # looks left, then right
    rot('J_Bip_C_Neck', (0, 0, 1), look * 0.55); rot('J_Bip_C_Head', (0, 0, 1), look * 0.45)
    # face: lyrics stop when the music dies; frown grows; "...Hello?" small, unsure
    for v in 'AIUEO': SK['Face.M_F00_000_00_Fcl_MTH_' + v].value = SK['Face.M_F00_000_00_Fcl_MTH_' + v].value if fp < 12 else 0.0
    SK['Face.M_F00_000_00_Fcl_BRW_Angry'].value = 0.45 * ease((fp - 12) / 10.0)
    SK['Face.M_F00_000_00_Fcl_ALL_Surprised'].value = 0.30 * math.exp(-max(0, fp - 13) / 6.0) * (1 if fp >= 12 else 0)
    for v, a, b_, amp in (('E', 31, 35, 0.35), ('O', 35, 40, 0.40)):
        if a <= fp < b_: SK['Face.M_F00_000_00_Fcl_MTH_' + v].value = amp * math.sin(math.pi * (fp - a) / (b_ - a))
    SK['Face.M_F00_000_00_Fcl_EYE_Close'].value = 1.0 if fp in (25, 57) else 0.0


# ---------------- camera: rides with him in close-up, then settles to a medium as he stops ----------------
camd.clip_start = 0.02; camd.dof.use_dof = True; camd.dof.aperture_fstop = 2.2


def cam09(f):
    k = ease((f - 30) / 30.0)
    root = B['root'].matrix_world
    head = rig.matrix_world @ PB(rig, 'J_Bip_C_Head').head
    near = root @ Vector((1.15, -0.85, 1.50)); far_ = root @ Vector((2.7, -2.0, 1.30))
    p = near.lerp(far_, k) + Vector((0.004 * math.sin(f * 0.8), 0, 0.004 * math.sin(f * 1.1)))
    tgt = head.lerp(root @ Vector((0.25, 0, 1.0)), k * 0.8)
    camd.lens = 50 - 16 * k; camd.dof.focus_distance = (head - p).length
    return p, (tgt - p).to_track_quat('-Z', 'Y')


META = {}
frames = range(1, NF + 1) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    sc.frame_set(f)
    pose_rider(R1, f); headphones(f); act(f); bpy.context.view_layer.update(); pose_strings(R1, f)
    p, q = cam09(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    s_ = proj(cam.location + SUN * 1000); h_ = proj(cam.location + Vector((0, 1, 0)) * 5000)
    META[f] = dict(sx=s_[0], sy=s_[1], hy=h_[1], glass=[(0, 0)] * 4, refl=False, samx=0.5)
    sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    print('frame', f, flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))

