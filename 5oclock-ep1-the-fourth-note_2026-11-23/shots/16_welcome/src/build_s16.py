"""5 O'CLOCK Ep1 "The Fourth Note" - shot 16 "Welcome home" (3 s, 72 f @24). Sam's POV down the street of the frozen town (shot 08 scene).
f1-10: it unfreezes: the hanging water falls, the boy lands and stands, the girl stands, the crow flies off. f12: in one frame every
shop sign is written backwards. f14-30: everyone turns to face him, together; f24-46: they smile and say "Okaeri, Sam." in unison.
usage: blender -b --python build_s16.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math
H16 = os.path.dirname(os.path.abspath(__file__))
S08 = os.path.normpath(os.path.join(H16, '..', '..', '08_frozen', 'src'))
CASTD = os.path.normpath(os.path.join(H16, '..', '..', '..', 'assets', 'cast_v2'))
_s = open(os.path.join(S08, 'build_s08.py'), encoding='utf-8').read()
_s = _s[:_s.index('# ---------------- the glide')]
_s = _s.replace("HERE8 = os.path.dirname(os.path.abspath(__file__))", "HERE8 = %r" % S08)
exec(_s)
from mathutils import Quaternion
NF = 72
for o in R1['objs'] + R2['objs']: o.hide_render = True                    # POV: Sam is the camera
for o in bpy.data.objects:
    if o.type == 'MESH' and any(m and m.name.startswith('susuki') for m in o.data.materials): o.hide_render = True
sk_, sko, skb = None, None, None
sk_, sko = load_char('shopkeeper', (9.6, 4.45, 0.0), 180)
arms_down(sk_, 74, 74); plant(sk_, sko, (ROAD.matrix_world @ Vector((9.6, 4.45, 0.15))).z)
for r_ in (kb, kg):                                                       # J1: kids' non-uniform bone scales shear on rotation
    for b_ in r_.data.bones:
        if any(k in b_.name for k in ('Arm', 'Hand', 'Index', 'Middle', 'Ring', 'Little', 'Thumb', 'Leg', 'Foot', 'Toe')): b_.inherit_scale = 'FIX_SHEAR'
POVW = road_pt(16.3, 0.7, 1.55)                     # v2: 2.3 m closer - the people, not the empty road, fill the frame
PEOPLE = [(kb, kbo), (kg, kgo), (gm, gmo), (sk_, sko)]
Y0 = {r.name: r.rotation_euler.z for r, _ in PEOPLE}
POSE0 = {r.name: {pb.name: pb.matrix_basis.copy() for pb in r.pose.bones} for r, _ in PEOPLE}
LIFT0 = kb.location.z
DROPS = [o for o in bpy.data.objects if o.name.startswith('drop')]
D0 = {o.name: o.location.copy() for o in DROPS}
CROW0 = croot.location.copy()
TEXTS = [o for o in bpy.data.objects if o.type == 'FONT']
print('texts', len(TEXTS), 'drops', len(DROPS))


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def standing(r):                                         # a plain standing pose from the saved cast pose: arms down
    for pb in r.pose.bones: pb.rotation_quaternion = Quaternion((1, 0, 0, 0)) if r is not gm else pb.rotation_quaternion
    arms_down(r, 68, 64)


# v2 (Sam: "people stand with arms straight down - give them natural standing poses"): relaxed fingers recorded once in
# T-pose (the curl helper assumes palms down), then every frame: elbows soft and forward, weight on one leg, breathing.
FINGERS = {}
for r_, _o in PEOPLE:
    keep = {pb.name: pb.matrix_basis.copy() for pb in r_.pose.bones}
    for pb in r_.pose.bones: pb.matrix_basis = Matrix.Identity(4)
    _curl_fingers(r_, 1, 0.32); _curl_fingers(r_, -1, 0.26)
    FINGERS[r_.name] = {pb.name: pb.rotation_quaternion.copy() for pb in r_.pose.bones
                        if any(k in pb.name for k in ('Index', 'Middle', 'Ring', 'Little', 'Thumb'))}
    for pb in r_.pose.bones: pb.matrix_basis = keep[pb.name]
STANCE = {kb.name: (1, 16, 12, 0.0), kg.name: (-1, 14, 18, 1.3), gm.name: (1, 20, 14, 2.1), sk_.name: (-1, 12, 17, 0.7)}


def natural(r, f):
    side, el, er, ph = STANCE[r.name]
    for n_, q_ in FINGERS[r.name].items(): r.pose.bones[n_].rotation_quaternion = q_.copy()
    rot(r, 'J_Bip_L_LowerArm', (0, 0, 1), -el); rot(r, 'J_Bip_R_LowerArm', (0, 0, 1), er)      # elbows bend forward
    rot(r, 'J_Bip_L_Hand', (0, 0, 1), -6); rot(r, 'J_Bip_R_Hand', (0, 0, 1), 6)
    rot(r, 'J_Bip_C_Hips', (0, -1, 0), 3.0 * side)                                             # weight on one leg
    rot(r, 'J_Bip_C_Spine', (0, -1, 0), -2.2 * side)
    soft = 'J_Bip_R_' if side > 0 else 'J_Bip_L_'
    rot(r, soft + 'UpperLeg', (1, 0, 0), -5); rot(r, soft + 'LowerLeg', (1, 0, 0), 9)
    b = math.sin(f * 0.21 + ph)                                                                # breathing
    rot(r, 'J_Bip_C_Chest', (1, 0, 0), 0.9 * b); rot(r, 'J_Bip_C_Neck', (1, 0, 0), -0.6 * b)
    rot(r, 'J_Bip_C_Head', (0, -1, 0), 2.5 * side)


def face_keys(objs, joy, vow, amt):
    for o in objs:
        ks = o.data.shape_keys if o.type == 'MESH' and o.data.shape_keys else None
        if not ks: continue
        for kb_ in ks.key_blocks:
            n = kb_.name
            if n.endswith('Fcl_MTH_Fun') or n.endswith('Fcl_ALL_Joy'): kb_.value = joy * (0.6 if n.endswith('MTH_Fun') else 0.35)
            for v in 'AIUEO':
                if n.endswith('Fcl_MTH_' + v): kb_.value = amt if v == vow else 0.0


def act(f):
    fp = f - (f - 1) % 2
    t = max(0.0, (fp - 1) / 24.0)
    for o in DROPS:                                       # the water falls (gravity) and is gone on the ground
        p0 = D0[o.name]; z = p0.z - 0.5 * 9.8 * t * t
        o.location = (p0.x, p0.y, z); o.hide_render = z < (ROAD.matrix_world @ Vector((7.4, 4.25, 0))).z + 0.02
    # the boy comes down from the jump and stands; the girl finishes her stride and stands
    for r, objs in PEOPLE:
        for pb in r.pose.bones: pb.matrix_basis = POSE0[r.name][pb.name].copy()
    if fp >= 9:
        standing(kb); standing(kg)
    for r, objs in PEOPLE:
        if r in (kb, kg) and fp < 9: continue                                  # still finishing the jump / the stride
        natural(r, fp)
    kb.location.z = LIFT0 - 0.80 * ease(fp / 8.0)
    croot.location = CROW0 + Vector((-3.0 * t, 2.0 * t, 4.5 * t))                  # the crow flies off
    # f12: every sign is written backwards, in one frame
    for o in TEXTS: o.scale.x = -abs(o.scale.x) if fp >= 12 else abs(o.scale.x)
    # everyone turns to him together (shortest way), smiles, speaks in unison
    tw = ease((fp - 14) / 14.0)
    for r, objs in PEOPLE:
        loc = r.matrix_world.translation; d = (ROAD.matrix_world.inverted() @ POVW) - (ROAD.matrix_world.inverted() @ loc)
        want = math.atan2(d.y, d.x) + math.pi / 2
        y0 = Y0[r.name]; dy = (want - y0 + math.pi) % (2 * math.pi) - math.pi
        r.rotation_euler.z = y0 + dy * tw
    joy = ease((fp - 24) / 10.0)
    vow, amt = None, 0.0
    for v, a, b in (('O', 24, 28), ('A', 28, 31), ('E', 31, 34), ('I', 34, 37), ('A', 38, 42), ('U', 42, 46)):
        if a <= fp < b: vow, amt = v, 0.45 * math.sin(math.pi * (fp - a) / (b - a))
    for r, objs in PEOPLE: face_keys(objs, joy, vow, amt)
    bpy.context.view_layer.update()
    for r, objs in PEOPLE:
        gz = (ROAD.matrix_world @ Vector((r.location.x, r.location.y, 0.0))).z
        if r is not kb or fp >= 8: plant(r, objs, gz + (0.15 if r is gm or r is sk_ else 0.0))


camd.dof.use_dof = False


def cam16(f):
    p = POVW + Vector((0.006 * math.sin(f * 0.37), 0.005 * math.sin(f * 0.29), 0.008 * math.sin(f * 0.61)))
    camd.lens = 26 + 6 * ease((f - 30) / 40.0)                              # he can't look away: a creeping push (v2 wider: "cropped")
    tgt = road_pt(10.5, 2.0, 1.15)
    return p, (tgt - p).to_track_quat('-Z', 'Y')


META = {}
frames = range(1, NF + 1) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    sc.frame_set(f)
    act(f)
    p, q = cam16(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
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
    print('frame', f, flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
