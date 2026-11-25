"""5 O'CLOCK Ep1 "The Fourth Note" - shot 05 "The ritual" (3.5 s = 3 cuts x 28 f @24) on the approved shot 04 street.
(a) Grandma stops sweeping and turns her shop's little mirror to face the wall (profile, lens 45). Line: "Ears. Quickly." at f17.
(b) Two kids stop running, press their hands over their ears and look up (low camera, backlit by the sun over the bay).
(c) The shopkeeper, back to camera, hauls the shutter down, then glances over his shoulder.
usage: blender -b --python build_s05.py -- <ABS outdir> <scale> <frames|all> <a|b|c>"""
import os, sys, math, random
HERE5 = os.path.dirname(os.path.abspath(__file__))
S04 = os.path.normpath(os.path.join(HERE5, '..', '..', '04_ride', 'src'))
CASTD = os.path.normpath(os.path.join(HERE5, '..', '..', '..', 'assets', 'cast_v2'))
CUT = (sys.argv[sys.argv.index('--') + 1:] + ['a'] * 4)[3]
_s = open(os.path.join(S04, 'build_s04.py'), encoding='utf-8').read()
_s = _s[:_s.index('META = {}')]
_s = _s.replace("HERE = os.path.dirname(os.path.abspath(__file__)); D = HERE", "HERE = %r; D = HERE" % S04)
exec(_s)
from mathutils import Quaternion
NF = 28
for o in R1['objs'] + R2['objs']: o.hide_render = True                      # no Sam in this shot
for o in bpy.data.objects:                                                   # susuki stalks read as cactus (R6)
    if o.type == 'MESH' and any(m and m.name.startswith('susuki') for m in o.data.materials): o.hide_render = True


def load_char(name, loc, yaw):
    with bpy.data.libraries.load(os.path.join(CASTD, name + '.blend'), link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    new = [o for o in dst.objects if o is not None and o.type not in ('LIGHT', 'CAMERA')]
    for o in new: sc.collection.objects.link(o)
    rig = next(o for o in new if o.type == 'ARMATURE' and o.parent is None)
    rig.parent = ROAD; rig.location = loc; rig.rotation_mode = 'XYZ'; rig.rotation_euler = (0, 0, math.radians(yaw))
    for pb in rig.pose.bones: pb.rotation_mode = 'QUATERNION'
    for b in (rig.data.bones if 'kid' in name else []):
        if any(k in b.name for k in ('Arm', 'Hand', 'Index', 'Middle', 'Ring', 'Little', 'Thumb', 'Leg', 'Foot', 'Toe')):
            b.inherit_scale = 'FIX_SHEAR'
    base = {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}
    return rig, new, base


def reset(rig, base):
    for pb in rig.pose.bones:
        if pb.name in base: pb.matrix_basis = base[pb.name].copy()
    for n_, q_ in FCURL.get(rig.name, {}).items(): rig.pose.bones[n_].rotation_quaternion = q_.copy()   # v2: keep the grip


FCURL = {}


def finger_curl(rig, amt_l, amt_r):
    """v2 fix: reset() restored every bone each frame and wiped the finger curl (flat hands on the mirror/shutter).
    Compute the curl once in T-pose (the helper assumes palms down), store it, and reset() re-applies it every frame."""
    keep = {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}
    infl = [(c, c.influence) for pb in rig.pose.bones for c in pb.constraints]
    for c, _ in infl: c.influence = 0.0
    for pb in rig.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    _curl_fingers(rig, 1, amt_l); _curl_fingers(rig, -1, amt_r)
    FCURL[rig.name] = {pb.name: pb.rotation_quaternion.copy() for pb in rig.pose.bones
                       if any(k in pb.name for k in ('Index', 'Middle', 'Ring', 'Little', 'Thumb'))}
    for pb in rig.pose.bones: pb.matrix_basis = keep[pb.name]
    for c, v in infl: c.influence = v


def lowest_z(objs, report=False):
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); best = (1e9, '')
    for o in objs:
        if o.type != 'MESH' or o.hide_render or 'randoseru' in o.name or 'Outline' in o.name: continue
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world
        c0 = (o.parent or o).matrix_world.translation
        zs = [w.z for i, v in enumerate(me.vertices) if i % 5 == 0 for w in (mw @ v.co,) if (w.xy - c0.xy).length < 0.9]; ev.to_mesh_clear()
        if zs and min(zs) < best[0]: best = (min(zs), o.name)
    if report: print('LOWEST', best)
    return best[0]


def plant(rig, objs, x, y):                                                  # feet locked to the road (R3): ABSOLUTE, never cumulative
    gz = (ROAD.matrix_world @ Vector((x, y, 0.0))).z
    rig.location.z = 0.0
    low = lowest_z(objs, bool(os.environ.get('DBG')))
    rig.location.z = (ROAD.matrix_world.inverted() @ Vector((0, 0, gz - low + (ROAD.matrix_world @ Vector((x, y, 0))).z))).z * 0 + (gz - low)


def R(rig, bone, axis, deg):
    if deg: _rot_arm(rig, bone, axis, deg)


def grip(rig, side, target, aim, palm, pole):
    """the 04 recipe: IK wrist to target, hand aimed along the object, palm rolled onto it, fingers curled"""
    S = side
    c = PB(rig, 'J_Bip_%s_LowerArm' % S).constraints.new('IK'); c.target = target; c.pole_target = pole; c.chain_count = 2; c.pole_angle = 0
    hc = PB(rig, 'J_Bip_%s_Hand' % S).constraints.new('DAMPED_TRACK'); hc.target = aim; hc.track_axis = 'TRACK_Y'
    hb = rig.data.bones['J_Bip_%s_Hand' % S]; R0 = hb.matrix_local.to_3x3()
    best = max((('TRACK_X', R0.col[0]), ('TRACK_NEGATIVE_X', -R0.col[0]), ('TRACK_Z', R0.col[2]), ('TRACK_NEGATIVE_Z', -R0.col[2])), key=lambda a: a[1].dot(Vector((0, 0, -1))))
    lc = PB(rig, 'J_Bip_%s_Hand' % S).constraints.new('LOCKED_TRACK'); lc.target = palm; lc.lock_axis = 'LOCK_Y'; lc.track_axis = best[0]
    return [c, hc, lc]


def setinf(cons, v):
    for c in cons: c.influence = v


def mouth(objs, vow, amt):
    for o in objs:
        ks = o.data.shape_keys if o.type == 'MESH' and o.data.shape_keys else None
        if not ks: continue
        for v in 'AIUEO':
            kb = ks.key_blocks.get('Fcl_MTH_' + v)
            if kb: kb.value = amt if v == vow else 0.0


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def L(a, b, t): return a + (b - a) * t


def E(name, loc, parent=None):
    e = empty(name, parent or ROAD, loc); return e


CAMP = None
ANIM = None
CH = []
camd.lens = 45

# =============================== (a) Grandma and the little mirror ===============================
if CUT == 'a':
    # v2 staging: the broom already leans on the pillar (she has stopped sweeping); both hands take the mirror's rim and turn it
    # to the wall. Camera on her right side: her profile + the mirror glass at 3/4 (lens 45).
    MIR = E('mirror_pivot', (4.20, 4.80, 1.50))                  # lathe axis = local +Y = the glass normal
    FRM = toon('mirror_frame05', (0.45, 0.08, 0.06), (0.80, 0.16, 0.12), (1.0, 0.8, 0.6), None, 0.5)
    GL = toon('mirror_glass05', (0.40, 0.46, 0.60), (0.80, 0.86, 0.96), (1.0, 0.95, 0.85), None, 0.5)
    mesh_obj('mirror_back', lathe([(0.0, 0.215), (0.035, 0.215), (0.035, 0.0005)], 48, cap_back=False), FRM, MIR, 0.005)
    mesh_obj('mirror_rim', lathe([(-0.03, 0.235), (0.035, 0.235), (0.035, 0.205), (-0.03, 0.205)], 48, cap_back=False), FRM, MIR, 0.005)
    mesh_obj('mirror_glass', lathe([(-0.012, 0.0005), (-0.008, 0.12), (0.0, 0.205)], 48, cap_back=False), GL, MIR, 0)   # convex
    arm_ = mesh_obj('mirror_arm', lathe([(0, 0.014), (0.22, 0.014)], 10), STEEL, ROAD, 0.003)
    arm_.location = (4.20, 4.80, 1.50); arm_.rotation_euler = (0, 0, 0)                                         # into the pillar (+y)
    # the broom she just stopped using, leaning on the pillar
    BR = E('broom', (4.62, 4.80, 0.0)); BR.rotation_euler = (math.radians(14), 0, math.radians(8))
    HND = toon('broom_handle', (0.40, 0.30, 0.18), (0.74, 0.60, 0.38), (1.0, 0.85, 0.6), None, 0.5)
    TW = toon('broom_twigs', (0.38, 0.30, 0.16), (0.70, 0.58, 0.32), (1.0, 0.86, 0.55), None, 0.5)
    h = mesh_obj('broom_h', lathe([(0, 0.016), (1.25, 0.014), (1.26, 0.0)], 10), HND, BR, 0.004)
    h.rotation_euler = (math.radians(90), 0, 0); h.location = (0, 0, 0.32)
    bm = bmesh.new(); rr = random.Random(5)
    for k in range(70):
        a = math.radians(rr.uniform(-30, 30)); L_ = rr.uniform(0.30, 0.42); w = 0.0045
        top = Vector((math.sin(a) * 0.03, rr.uniform(-0.012, 0.012), 0.34)); bot = Vector((math.sin(a) * L_ * 0.95, rr.uniform(-0.04, 0.04), 0.0))
        bm.faces.new([bm.verts.new(top - Vector((w, 0, 0))), bm.verts.new(top + Vector((w, 0, 0))), bm.verts.new(bot + Vector((w, 0, 0))), bm.verts.new(bot - Vector((w, 0, 0)))])
    mesh_obj('broom_twigs', bm, TW, BR, 0.0015)
    gm, gmo, gb = load_char('grandma', (4.66, 4.28, 0.0), -140)     # faces the mirror (up-left in the shot)
    CH = [(gm, gmo)]
    for nm in ('broom',): pass
    # rim grips: the hand targets ride on the mirror, so the hands turn WITH it
    hands = {}
    for S, sx in (('L', 1), ('R', -1)):
        t_ = E('mt' + S, (sx * 0.225, -0.035, -0.02), MIR); a_ = E('ma' + S, (sx * 0.225, -0.035, 0.30), MIR)
        p_ = E('mp' + S, (sx * 0.06, 0.3, -0.02), MIR); po = E('mpo' + S, (4.62 + sx * 0.5, 3.95, 0.95))
        hands[S] = grip(gm, S, t_, a_, p_, po)
    finger_curl(gm, 0.62, 0.30)
    # v3 (probe: blending IK influence swung her arm out sideways like a T-pose): the IK stays at full strength and the TARGET
    # travels - from her hand's rest spot, up in a small arc to the rim, rides the rim, then follows through and drops back.
    RIM_T = hands['L'][0].target; REACH = E('reachL', (0, 0, 0)); hands['L'][0].target = REACH
    REST = {}

    def ANIM(f):
        fp = float(f)                                                                 # v3: on ones ("a robot flipped it")
        for S in ('L', 'R'): setinf(hands[S], 0.0)
        bpy.context.view_layer.update()
        reset(gm, gb); R(gm, 'J_Bip_L_UpperArm', (0, 1, 0), 70); R(gm, 'J_Bip_R_UpperArm', (0, 1, 0), -70)
        look = ease((fp - 1) / 6.0); reach = ease((fp - 5) / 6.5); turn = ease((fp - 11) / 9.0); back = ease((fp - 22) / 7.0)
        R(gm, 'J_Bip_C_Head', (1, 0, 0), -16 * look * (1 - back))                        # eyes up to the mirror
        R(gm, 'J_Bip_C_Neck', (0, 0, 1), 34 * back); R(gm, 'J_Bip_C_Head', (0, 0, 1), 16 * back)   # then to the street / the kids
        # v3 body mechanics: she leans in to reach, the push comes from the torso (twist + lean), the arm follows through
        # after the release and her body rocks back; the head trails the shoulders by ~2 frames.
        push = ease((fp - 11) / 8.0); rel = ease((fp - 19) / 7.0)
        R(gm, 'J_Bip_C_Spine', (1, 0, 0), 4 * reach + 5 * push * (1 - rel) - 2 * math.sin(math.pi * rel))
        R(gm, 'J_Bip_C_Spine', (0, 0, 1), -9 * push * (1 - 0.6 * rel)); R(gm, 'J_Bip_C_Chest', (0, 0, 1), -6 * push * (1 - 0.5 * rel))
        R(gm, 'J_Bip_C_Neck', (0, 0, 1), 5 * ease((fp - 13) / 8.0) * (1 - back))
        # mirror: slow to start (a stiff old swivel), released at 19, swings on by momentum, overshoots and settles damped
        KEYS = [(1, -32), (11, -32), (19, -108), (24, -176), (27, -188), (31, -177), (35, -181.5), (39, -179.6), (99, -180)]
        th = KEYS[-1][1]
        for (fa, aa), (fb, ab) in zip(KEYS, KEYS[1:]):
            if fa <= fp < fb: u = (fp - fa) / (fb - fa); th = aa + (ab - aa) * (u * u if fa == 11 else ease(u)); break   # push: ease-in
        MIR.rotation_mode = 'XYZ'; MIR.rotation_euler = (0, 0, math.radians(th))                  # glass toward the street -> to the wall
        bpy.context.view_layer.update()
        if 'hand' not in REST:                                                    # her relaxed left hand (FK, no constraints)
            REST['hand'] = gm.matrix_world @ PB(gm, 'J_Bip_L_Hand').head
            MIR.rotation_euler = (0, 0, math.radians(-108)); bpy.context.view_layer.update()
            REST['rel'] = RIM_T.matrix_world.translation.copy()                  # the rim where she lets go (fp 19)
            MIR.rotation_euler = (0, 0, math.radians(th)); bpy.context.view_layer.update()
        rest, rim = REST['hand'], RIM_T.matrix_world.translation.copy()
        rel = REST['rel']; push_dir = (rel - (MIR.matrix_world.translation)).cross(Vector((0, 0, 1))).normalized()
        if fp < 12:
            e = ease((fp - 4) / 8.0); p = rest.lerp(rim, e) + Vector((0, 0, 0.10 * math.sin(math.pi * e)))
        elif fp < 19:
            p = rim
        else:                                                                     # follow-through past the release, then down
            e1 = ease((fp - 19) / 4.0); e2 = ease((fp - 22) / 9.0)
            p = (rel + push_dir * 0.07 * e1).lerp(rest, e2) + Vector((0, 0, 0.03 * math.sin(math.pi * e2)))
        REACH.location = ROAD.matrix_world.inverted() @ p
        setinf(hands['R'], 0.0); setinf(hands['L'], 1.0)
        hands['L'][1].influence = hands['L'][2].influence = ease((fp - 8) / 4.0) * (1 - ease((fp - 19) / 5.0))   # hand shapes to the rim only near it
        R(gm, 'J_Bip_R_LowerArm', (0, 0, 1), 18); R(gm, 'J_Bip_R_Hand', (0, 0, 1), 6)                # free hand: soft elbow, at rest
        bpy.context.view_layer.update(); plant(gm, gmo, 4.62, 4.30)
        mouth(gmo, ('E', 'A', 'U', 'I', 'U')[int(min(4, max(0, (fp - 17) // 2)))], 0.5 if 17 <= fp <= 27 else 0.0)

    def CAMP(f):
        k = ease((f - 1) / 27.0)
        p = ROAD.matrix_world @ Vector((3.30 + 0.06 * k, 2.85 + 0.08 * k, 1.34)) + Vector((0.005 * math.sin(f * 0.4), 0, 0.004 * math.sin(f * 0.7)))
        tgt = ROAD.matrix_world @ Vector((4.45, 4.55, 1.40))
        return p, (tgt - p).to_track_quat('-Z', 'Y')

# =============================== (b) the kids cover their ears ===============================
if CUT == 'b':
    camd.lens = 35
    kb_, kbo, kbb = load_char('kid_boy', (22.55, 1.7, 0.0), 0)
    kg_, kgo, kgb = load_char('kid_girl', (23.45, 2.2, 0.0), 0)                  # both run toward the camera (-y), then stop
    CH = [(kb_, kbo), (kg_, kgo)]
    KIDS = []
    for rig, objs, base, x0, y0, ph in ((kb_, kbo, kbb, 22.55, 1.7, 0.0), (kg_, kgo, kgb, 23.45, 2.2, 1.3)):
        tgts = {}
        for S, sg in (('L', 1), ('R', -1)):
            t_ = E('ear_' + S + rig.name, (0, 0, 0)); a_ = E('earA_' + S + rig.name, (0, 0, 0)); p_ = E('earP_' + S + rig.name, (0, 0, 0))
            po = E('earPole_' + S + rig.name, (0, 0, 0))
            tgts[S] = (t_, a_, p_, po, grip(rig, S, t_, a_, p_, po))              # v3: real IK (the list was empty = FK wings)
        KIDS.append(dict(rig=rig, objs=objs, base=base, x=x0, y=y0, ph=ph, t=tgts))

    def ANIM(f):
        fp = float(f)                                                         # v3: on ones
        for K in KIDS:
            rig = K['rig']
            for S_ in ('L', 'R'): setinf(K['t'][S_][4], 0.0)                     # v4: no IK pull (target at origin) while posing/planting
            reset(rig, K['base'])
            run = 1 - ease((fp - 6 - K['ph'] * 2) / 6.0)                          # running, then they stop
            y = K['y'] - 0.9 * ease((fp - 1) / (14.0 + K['ph'] * 2))              # stop ~3 m from the lens              # decelerating toward the camera
            ph = fp * 0.55 + K['ph']
            for S, sg in (('L', 1), ('R', -1)):
                R(rig, 'J_Bip_%s_UpperLeg' % S, (1, 0, 0), (-32 * math.sin(ph + (0 if S == 'L' else math.pi))) * run)
                R(rig, 'J_Bip_%s_LowerLeg' % S, (1, 0, 0), (34 + 28 * math.sin(ph + (0.8 if S == 'L' else math.pi + 0.8))) * run)
                pass
            R(rig, 'J_Bip_C_Spine', (1, 0, 0), 10 * run)
            cover = ease((fp - 12 - K['ph'] * 2) / 5.0); up = ease((fp - 18 - K['ph']) / 6.0)
            for S, sg in (('L', 1), ('R', -1)):                                    # arms: FK = the run swing only (v3: the FK
                swing = 14 * math.sin(ph + (math.pi if S == 'L' else 0)) * run       # lerp to the ears flapped them out like wings)
                R(rig, 'J_Bip_%s_UpperArm' % S, (0, 1, 0), sg * 79)                    # v4: a real hang, not an A-pose
                R(rig, 'J_Bip_%s_UpperArm' % S, (0, 0, 1), swing)
                R(rig, 'J_Bip_%s_LowerArm' % S, (0, 1, 0), -sg * 18)
            R(rig, 'J_Bip_C_Neck', (1, 0, 0), -14 * up); R(rig, 'J_Bip_C_Head', (1, 0, 0), -16 * up)
            R(rig, 'J_Bip_C_UpperChest', (1, 0, 0), -4 * up)
            rig.location = (K['x'], y, rig.location.z)
            bpy.context.view_layer.update()
            plant(rig, K['objs'], K['x'], y)
            if os.environ.get('DBG'): print('DBG', fp, rig.name, round(rig.location.z, 3))
            bpy.context.view_layer.update()
            hd = PB(rig, 'J_Bip_C_Head'); hw = rig.matrix_world @ hd.head; hx = (rig.matrix_world.to_3x3() @ Vector((1, 0, 0))).normalized()
            fwd = (rig.matrix_world.to_3x3() @ Vector((0, -1, 0))).normalized()
            for S, sg in (('L', 1), ('R', -1)):
                t_, a_, p_, po, cons = K['t'][S]
                setinf(cons, 0.0); bpy.context.view_layer.update()
                fk = rig.matrix_world @ PB(rig, 'J_Bip_%s_LowerArm' % S).tail          # where the running hand is (FK wrist)
                ear = hw + Vector((0, 0, 0.07)) + hx * sg * 0.095                    # palm flat over the ear
                Mi = ROAD.matrix_world.inverted()
                # v3: full-strength IK, the TARGET travels: wrist from its swing spot, up IN FRONT of the chest, to the ear
                wr = (ear + hx * sg * 0.035)
                p = fk.lerp(wr, cover) + fwd * 0.18 * math.sin(math.pi * cover) + Vector((0, 0, 0.04 * math.sin(math.pi * cover)))
                t_.location = Mi @ p
                a_.location = Mi @ (ear + Vector((0, 0, 0.25)))
                p_.location = Mi @ (ear - hx * sg * 0.30)
                pole_lo = hw + hx * sg * 0.22 + fwd * 0.40 - Vector((0, 0, 0.65))     # v4: elbows low + forward while the hands rise,
                pole_hi = ear + hx * sg * 0.35 + fwd * 0.10 - Vector((0, 0, 0.25))    # opening out only as the palms reach the ears
                po.location = Mi @ pole_lo.lerp(pole_hi, ease((cover - 0.45) / 0.55))
                if cover > 0.001:
                    cons[0].influence = 1.0; cons[1].influence = cons[2].influence = ease((cover - 0.5) / 0.5)   # hand shapes to the ear late

    def CAMP(f):
        k = ease((f - 1) / 27.0)
        p = ROAD.matrix_world @ Vector((23.0, -1.70 + 0.06 * k, 0.80)) + Vector((0.006 * math.sin(f * 0.5), 0, 0.004 * math.sin(f * 0.8)))
        tgt = ROAD.matrix_world @ Vector((23.0, 6.0, 2.05))      # the bay and the low sun behind them
        return p, (tgt - p).to_track_quat('-Z', 'Y')

# =============================== (c) the shopkeeper pulls the shutter ===============================
if CUT == 'c':
    camd.lens = 31                                                               # v4: wider - his hands stay in frame to the bottom
    sk, sko, skb = load_char('shopkeeper', (8.55, 4.42, 0.0), 180)               # back to camera, facing the shop
    CH = [(sk, sko)]
    SHM = toon('shutter05', (0.34, 0.34, 0.40), (0.66, 0.67, 0.70), (1.0, 0.86, 0.62), tex_rows(0.075, 0.6, 'Z') if 'tex_rows' in dir() else None, 0.5)
    BOX = toon('shutter_box05', (0.30, 0.30, 0.34), (0.58, 0.58, 0.62), (1.0, 0.86, 0.62), None, 0.5)
    X0s, X1s, YS = 7.35, 9.75, 4.93
    bm = bmesh.new(); box(bm, ((X0s + X1s) / 2, YS - 0.06, 2.62), (X1s - X0s + 0.2, 0.30, 0.34), 0)
    mesh_obj('shutter_box', bm, BOX, ROAD, 0.006)
    SH = E('shutter', ((X0s + X1s) / 2, YS - 0.12, 2.45))
    bm = bmesh.new(); box(bm, (0, 0, -1.0), (X1s - X0s, 0.03, 2.0), 0)
    sp = mesh_obj('shutter_slats', bm, SHM, SH, 0.005)
    bm = bmesh.new(); box(bm, (0, -0.025, -2.0), (X1s - X0s, 0.06, 0.07), 0)
    mesh_obj('shutter_bar', bm, BOX, SH, 0.005)
    # v2 (Sam: "the shutter-closing hands look broken"): targets live in street space (NOT under the scaled shutter, which
    # squashed their offsets), recomputed from the bar each frame. Overhand hook: overhead = fingers up, palms forward on the
    # bar; as it comes down to the chest the hands roll to palms down, pushing. Shoulder-width, elbows out and down.
    tgt = {}; TG = {}
    XC = (X0s + X1s) / 2
    # v3 (Sam: "he closes the shutter by crisscrossing his hands. Who does that?"): he faces +y (yaw 180), so HIS left is -x.
    # v1/v2 had L at +x = crossed wrists. Now L at -x, R at +x, shoulder width, elbows down and back.
    for S, dx in (('L', -0.30), ('R', 0.30)):
        t_ = E('sh_t' + S, (0, 0, 0)); a_ = E('sh_a' + S, (0, 0, 0)); p_ = E('sh_p' + S, (0, 0, 0))
        po = E('sh_po' + S, (8.55 + dx * 1.9, 3.70, 0.45))
        tgt[S] = grip(sk, S, t_, a_, p_, po); TG[S] = (dx, t_, a_, p_)
    finger_curl(sk, 0.92, 0.92)                                                  # v4: hook over the bar (0.62 read as a thumbs-up)

    def ANIM(f):
        fp = float(f)                                                                 # v3: on ones (twos read robotic on a body pull)
        reset(sk, skb)
        # real mechanics: a small lift to free the slats (anticipation), then the pull, slowing as the bar meets chest height
        lift = math.sin(math.pi * min(1.0, max(0.0, (fp - 1) / 5.0))) * 0.06
        pull = ease((fp - 4) / 16.0)
        s_ = L(0.24, 0.90, pull) - lift; SH.scale = (1, 1, s_)                      # v4: all the way down to his waist (it closes)                      # bar 1.97 m (overhead, in reach) -> chest height
        zb = 2.45 - 2.0 * s_; yb = YS - 0.12 - 0.025
        for S, (dx, t_, a_, p_) in TG.items():
            lag = 0.012 * math.sin(fp * 0.5 + (0 if S == 'L' else 1.7)) * (1 - pull)  # hands never move as one block
            w = Vector((XC + dx, yb - 0.10, zb - 0.02 + lag))
            d = Vector((0, 0, 1)).lerp(Vector((0, 1, 0)), pull).normalized()        # fingers: up -> forward
            pd = Vector((0, 1, 0)).lerp(Vector((0, 0.25, -1)), pull).normalized()  # palm: forward -> down onto the bar
            t_.location = w; a_.location = w + d * 0.30; p_.location = w + pd * 0.40
        settle = ease((fp - 20) / 6.0)
        R(sk, 'J_Bip_C_Spine', (1, 0, 0), L(-6, 30, pull) - 5 * settle); R(sk, 'J_Bip_C_Chest', (1, 0, 0), L(-4, 16, pull) - 3 * settle)   # v4: bends with it
        R(sk, 'J_Bip_C_Spine', (0, 0, 1), 4 * math.sin(math.pi * pull))           # weight rolls a little onto the right side mid-pull
        glance = ease((fp - 20) / 6.0)
        R(sk, 'J_Bip_C_Neck', (0, 0, 1), -26 * glance); R(sk, 'J_Bip_C_Head', (0, 0, 1), -22 * glance); R(sk, 'J_Bip_C_UpperChest', (0, 0, 1), -8 * glance)
        bend = math.sin(math.pi * min(1.0, pull * 1.15)) * 0.8 + 0.2 * pull          # knees give as the weight comes down, then recover
        for S in ('L', 'R'):
            R(sk, 'J_Bip_%s_UpperLeg' % S, (1, 0, 0), -(14 if S == 'L' else 9) * bend); R(sk, 'J_Bip_%s_LowerLeg' % S, (1, 0, 0), (24 if S == 'L' else 16) * bend)
        sk.location = (8.55, 4.42, sk.location.z); bpy.context.view_layer.update(); plant(sk, sko, 8.55, 4.42)

    def CAMP(f):
        k = ease((f - 1) / 27.0)
        p = ROAD.matrix_world @ Vector((8.95, 2.15 + 0.10 * k, 1.42)) + Vector((0.005 * math.sin(f * 0.45), 0, 0.004 * math.sin(f * 0.7)))
        tgt = ROAD.matrix_world @ Vector((8.45, 5.0, 1.62 - 0.45 * k))           # v4: tilts down with the bar
        return p, (tgt - p).to_track_quat('-Z', 'Y')

# =============================== render ===============================
META = {}
frames = range(1, NF + 1) if FR == 'all' else [int(x) for x in FR.split(',')]
if CUT == 'a': plant(gm, gmo, 4.55, 4.40)
for f in frames:
    sc.frame_set(f)
    ANIM(f)
    p, q = CAMP(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    s_ = proj(cam.location + SUN * 1000); h_ = proj(cam.location + Vector((0, 1, 0)) * 5000)
    gpoly, vis = glass_proj()
    META[f] = dict(sx=s_[0], sy=s_[1], hy=h_[1], glass=gpoly, refl=bool(vis), samx=0.5)
    sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    if vis:
        for o in FAR: o.visible_camera = False
        pm, qm = mirror_cam(p, q); cam.location = pm; cam.rotation_quaternion = qm
        bpy.context.view_layer.update()
        sc.render.filepath = os.path.join(OUT, 'refl_%03d.png' % f); bpy.ops.render.render(write_still=True)
        for o in FAR: o.visible_camera = True
        cam.location = p; cam.rotation_quaternion = q
    print('frame', f, CUT, 'refl' if vis else '', flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
