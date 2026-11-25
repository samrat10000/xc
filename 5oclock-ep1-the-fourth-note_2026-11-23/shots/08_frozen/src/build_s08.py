"""5 O'CLOCK Ep1 "The Fourth Note" - shot 08 "The frozen town" (5 s, 120 f @24).
The third note ends and everything stops mid-motion: leaves hang in the air, a kid hangs mid-jump, Grandma's watering-can
water hangs as droplets, a crow is fixed mid-flap. One continuous glide at walking height weaves through it and ends on
Sam, the only thing still moving. Reuses the approved shot 04 street + Sam rig (build_s04.py, executed up to its render loop).
usage: blender -b --python build_s08.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math, random
HERE8 = os.path.dirname(os.path.abspath(__file__))
S04 = os.path.normpath(os.path.join(HERE8, '..', '..', '04_ride', 'src'))
CASTD = os.path.normpath(os.path.join(HERE8, '..', '..', '..', 'assets', 'cast_v2'))
_s = open(os.path.join(S04, 'build_s04.py'), encoding='utf-8').read()
_s = _s[:_s.index('META = {}')]                                          # scene, Sam, camera helpers, haze: everything but the render loop
_s = _s.replace("HERE = os.path.dirname(os.path.abspath(__file__)); D = HERE", "HERE = %r; D = HERE" % S04)
_s = _s.replace("NF = 96; DELAY = 12", "NF = 120; DELAY = 12")
exec(_s)
from mathutils import Quaternion
NF = 120

# ---------------- Sam: still riding (the only moving thing). The late twin is not used here. ----------------
for o in R2['objs']: o.hide_render = True


def sam_x(f):                                                            # overrides 04: further down the road, same speed
    t = (f - 1) / 24.0; return 27.0 + 3.9 * t + 0.5 * 0.15 * t * t      # far down the road: the glide catches him at the end


# ---------------- frozen townsfolk (cast v2), posed once, held ----------------
def load_char(name, loc, yaw):
    with bpy.data.libraries.load(os.path.join(CASTD, name + '.blend'), link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    new = [o for o in dst.objects if o is not None and o.type not in ('LIGHT', 'CAMERA')]
    for o in new: sc.collection.objects.link(o)
    rig = next(o for o in new if o.type == 'ARMATURE' and o.parent is None)
    rig.parent = ROAD; rig.location = loc; rig.rotation_mode = 'XYZ'; rig.rotation_euler = (0, 0, math.radians(yaw))
    for pb in rig.pose.bones: pb.rotation_mode = 'QUATERNION'
    return rig, new


def rot(rig, bone, axis, deg):
    """rotate a bone about a CHARACTER-space axis (X = its left, -Y = its front, Z = up), on top of its saved pose"""
    pb = rig.pose.bones.get(bone)
    if pb is None: return
    ax = pb.bone.matrix_local.to_3x3().inverted() @ Vector(axis)
    pb.rotation_quaternion = Quaternion(ax, math.radians(deg)) @ pb.rotation_quaternion


def arms_down(rig, l=68, r=68):
    rot(rig, 'J_Bip_L_UpperArm', (0, 1, 0), l); rot(rig, 'J_Bip_R_UpperArm', (0, 1, 0), -r)


def lowest_z(objs):
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); zs = []
    for o in objs:
        if o.type != 'MESH': continue
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world
        zs += [(mw @ v.co).z for i, v in enumerate(me.vertices) if i % 7 == 0]; ev.to_mesh_clear()
    return min(zs)


def plant(rig, objs, ground_z_world, lift=0.0):
    """feet locked to the ground (R3): measure the lowest vertex, offset the rig"""
    dz = lowest_z(objs) - ground_z_world
    rig.location.z -= dz - lift


def hand_world(rig, side):
    pb = rig.pose.bones['J_Bip_%s_Hand' % side]; bpy.context.view_layer.update()
    return rig.matrix_world @ pb.tail


cast_objs = []
# kid (boy) hangs mid-jump off the kerb, knees tucked, arms flung up: faces the oncoming camera
kb, kbo = load_char('kid_boy', (10.6, -0.9, 0.0), -90)       # v3: was ON the glide path (camera flew through him, Sam's 25-26 s glitch)
rot(kb, 'J_Bip_C_Spine', (1, 0, 0), 12)
for s_, sg in (('L', 1), ('R', -1)):
    rot(kb, 'J_Bip_%s_UpperLeg' % s_, (1, 0, 0), -62 if s_ == 'L' else -38)
    rot(kb, 'J_Bip_%s_LowerLeg' % s_, (1, 0, 0), 88 if s_ == 'L' else 70)
    rot(kb, 'J_Bip_%s_UpperArm' % s_, (0, 1, 0), sg * -35)            # arms up and out
    rot(kb, 'J_Bip_%s_LowerArm' % s_, (0, 0, 1), sg * 30)
rot(kb, 'J_Bip_C_Head', (1, 0, 0), -10)
rot(kb, 'J_Bip_R_LowerLeg', (1, 0, 0), 30)
plant(kb, kbo, (ROAD.matrix_world @ Vector((10.6, -0.9, 0.0))).z, lift=0.80)   # clearly airborne
# kid (girl) frozen mid-stride crossing the road
kg, kgo = load_char('kid_girl', (16.2, -0.4, 0.0), 180)
rot(kg, 'J_Bip_C_Spine', (1, 0, 0), 10)
rot(kg, 'J_Bip_L_UpperLeg', (1, 0, 0), -38); rot(kg, 'J_Bip_L_LowerLeg', (1, 0, 0), 30)
rot(kg, 'J_Bip_R_UpperLeg', (1, 0, 0), 26); rot(kg, 'J_Bip_R_LowerLeg', (1, 0, 0), 72)
arms_down(kg, 62, 62); rot(kg, 'J_Bip_L_UpperArm', (0, 0, 1), 32); rot(kg, 'J_Bip_R_UpperArm', (0, 0, 1), 30)
rot(kg, 'J_Bip_L_LowerArm', (0, 0, 1), -40); rot(kg, 'J_Bip_R_LowerArm', (0, 0, 1), 45)
plant(kg, kgo, (ROAD.matrix_world @ Vector((16.2, -0.4, 0.0))).z, lift=0.06)   # mid-stride: back foot just off the road
# Grandma watering the pots in front of her shop: right arm out with the can, water frozen in the air
gm, gmo = load_char('grandma', (7.4, 4.25, 0.0), -37)       # 3/4 toward the glide: the can and the water are on our side
arms_down(gm, 70, 40); rot(gm, 'J_Bip_R_UpperArm', (0, 0, 1), 52); rot(gm, 'J_Bip_R_LowerArm', (0, 0, 1), 22)
rot(gm, 'J_Bip_L_LowerArm', (0, 0, 1), -70)
plant(gm, gmo, (ROAD.matrix_world @ Vector((7.4, 4.25, 0.15))).z)
for rig, side in ((gm, 'R'), (gm, 'L')):
    try: _curl_fingers(rig, 1 if side == 'L' else -1, 0.85 if side == 'R' else 0.25)   # v4: free hand relaxed (0.85 = a claw)       # side is +1/-1 in rider.py
    except Exception as e: print('curl', e)
cast_objs = kbo + kgo + gmo

# ---------------- watering can (real shape: oval body, long spout, top handle) + frozen water ----------------
WATERM = toon('water08', (0.42, 0.62, 0.80), (0.80, 0.90, 0.98), (1.0, 0.95, 0.86), None, 0.4)
CANM = toon('can08', (0.30, 0.42, 0.36), (0.50, 0.68, 0.56), (1.0, 0.86, 0.6), None, 0.5)
hw = hand_world(gm, 'R')
can = empty('can_root'); can.location = hw + Vector((0.0, 0.0, -0.10))
yawc = gm.matrix_world.to_euler().z
can.rotation_euler = (math.radians(28), 0, yawc - math.radians(90))      # tilted: pouring
mesh_obj('can_body', ellipsoid(0.12, 0.07, 0.10, 20, 12), CANM, can, 0.004).location = (0, 0, -0.06)
sp = mesh_obj('can_spout', lathe([(0.0, 0.022), (0.30, 0.012), (0.33, 0.02)], 12), CANM, can, 0.003)
sp.location = (0.08, 0, -0.04); sp.rotation_euler = (0, 0, math.radians(-90)); sp.rotation_mode = 'XYZ'
sp.rotation_euler = (math.radians(-35), 0, math.radians(-90))
bm = bmesh.new()
for i in range(12):
    a = math.pi * i / 11
    bm.verts.new((0.0 + 0.09 * math.cos(a), 0, 0.04 + 0.08 * math.sin(a)))
mesh_obj('can_handle', lathe([(0, 0.012), (0.001, 0.012)], 8), CANM, can, 0.003).location = (0, 0, 0.06)
bpy.context.view_layer.update()
tip = sp.matrix_world @ Vector((0, 0.33, 0))
dirv = (sp.matrix_world.to_3x3() @ Vector((0, 1, 0))).normalized()
rr = random.Random(8)
for i in range(46):                                                       # a frozen arc of water: stream breaking into drops
    t = i / 45 * 0.42
    p = tip + dirv * (1.4 * t) + Vector((0, 0, -4.9 * t * t)) + Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) * 0.012 * (1 + 6 * t)
    r = (0.013 if i < 12 else rr.uniform(0.006, 0.014))
    d = mesh_obj('drop%d' % i, ellipsoid(r, r, r * (1.6 if i < 12 else 1.0), 10, 7), WATERM, None, 0.0025)
    d.location = p
# v4 (Sam: "water is not frozen... it should look like a liquid, falling"): the stream keeps pouring while the town is frozen.
import re as _re
DROPS = [o for o in bpy.data.objects if _re.fullmatch(r'drop\d+(\.\d+)?', o.name)]   # NOT the verge meshes 'drop'/'drop_fwd' (K18)
WJ = [Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-1, 1))) for _ in DROPS]


def pour(f):
    """each drop rides the parabola from the spout and loops: a continuous stream that thins and breaks into drops as it falls"""
    for i, d in enumerate(DROPS):
        t = ((i / len(DROPS)) * 0.42 + f * 0.022) % 0.42
        vel = dirv * 1.4 + Vector((0, 0, -9.8 * t))
        d.location = tip + dirv * (1.4 * t) + Vector((0, 0, -4.9 * t * t)) + WJ[i] * 0.010 * (1 + 5 * t)
        d.rotation_mode = 'QUATERNION'; d.rotation_quaternion = vel.to_track_quat('Z', 'Y')
        d.scale = (1.0 - 0.3 * min(1, t / 0.2), 1.0 - 0.3 * min(1, t / 0.2), 1.0 + 2.2 * (1 - min(1, t / 0.25)) + 0.8 * min(1, vel.length / 4))
        d.hide_render = t > 0.40                                                 # it leaves the frame / lands in the pots

# ---------------- leaves hanging in the air (real 7-lobed maple outlines) ----------------
def maple(scale):
    bm = bmesh.new(); pts = []
    for k in range(70):
        a = 2 * math.pi * k / 70
        lobe = 0.55 + 0.45 * abs(math.cos(3.5 * a)) ** 0.6                 # 7 pointed lobes
        serr = 1 + 0.06 * math.sin(a * 42)                                 # serrated edge
        notch = 0.35 if abs(((a - 4.712) + math.pi) % (2 * math.pi) - math.pi) < 0.18 else 1.0   # stem notch at the bottom
        rr_ = scale * lobe * serr * notch
        pts.append(bm.verts.new((rr_ * math.cos(a), rr_ * math.sin(a) * 0.95, 0)))
    c = bm.verts.new((0, 0, 0))
    for p, q in zip(pts, pts[1:] + pts[:1]): bm.faces.new((c, p, q))
    st = [bm.verts.new((0, -scale * 0.3, 0.002)), bm.verts.new((0.004, -scale * 1.25, 0.002)), bm.verts.new((-0.004, -scale * 1.25, 0.002))]
    bm.faces.new(st)
    return bm


# ---------------- crow fixed mid-flap over the road (CC0 raven, its own fly clip, frozen at the downstroke) ----------------
before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=os.path.join(HERE8, 'crow_tehbucket_raven_cc0.glb'))
crow = [o for o in bpy.data.objects if o not in before]
crig = next((o for o in crow if o.type == 'ARMATURE'), None)
croot = next(o for o in crow if o.parent is None)
if crig and crig.animation_data is None: crig.animation_data_create()
acts = [a for a in bpy.data.actions if a.name not in ('',)]
fly = next((a for a in acts if 'fly' in a.name.lower()), acts[0] if acts else None)
print('crow actions', [a.name for a in acts], 'using', fly.name if fly else None)
if crig and fly:
    crig.animation_data.action = fly
    fr0, fr1 = fly.frame_range; sc.frame_set(int(fr0 + (fr1 - fr0) * 0.35))
    bpy.context.view_layer.update()
    mats = {pb.name: pb.matrix_basis.copy() for pb in crig.pose.bones}
    crig.animation_data.action = None
    for pb in crig.pose.bones: pb.matrix_basis = mats[pb.name]
for o in crow:
    if o.type == 'MESH':
        o.data.materials.clear(); o.data.materials.append(CROW)
        for p in o.data.polygons: p.use_smooth = True
        sd = o.modifiers.new('sub', 'SUBSURF'); sd.levels = 2; sd.render_levels = 2
        outline(o, 0.0035)
bpy.context.view_layer.update()
dims = max((o.dimensions.length for o in crow if o.type == 'MESH'), default=1.0)
croot.scale = (croot.scale[0] * 0.9 / dims,) * 3                          # ~0.9 m wingtip to wingtip
croot.parent = ROAD; croot.location = (22.5, 1.1, 2.35); croot.rotation_mode = 'XYZ'; croot.rotation_euler = (math.radians(-12), math.radians(8), math.radians(200))

# ---------------- the glide: one continuous move at walking height, weaving, ends on Sam ----------------
WP = [(4.4, 2.6, 1.22), (6.2, 3.0, 1.32), (9.4, 3.1, 1.48), (12.0, 1.1, 1.46), (15.2, 0.5, 1.50), (18.8, -0.9, 1.52), (22.0, 0.3, 1.60), (28.0, 0.4, 1.50), (36.0, 0.2, 1.45), (43.0, 0.0, 1.40)]


def cr(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return tuple(0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t2 + (-a + 3 * b - 3 * c + d) * t3) for a, b, c, d in zip(p0, p1, p2, p3))


def path(u):                                                                # u 0..1 over the waypoints
    n = len(WP) - 1; s = min(u * n, n - 1e-6); i = int(s); t = s - i
    P = [WP[max(0, i - 1)], WP[i], WP[i + 1], WP[min(n, i + 2)]]
    return cr(*P, t)


def cam08(f):
    u = ease((f - 1) / 104.0) * 0.82 + 0.18 * ((f - 1) / 119.0)                # glide: gentle start, travelling, eases toward Sam
    u = min(u, 1.0)
    x, y, z = path(u)
    # final second: settle beside and slightly behind Sam, matching his speed
    k = ease((f - 92) / 24.0)
    sx = sam_x(f)
    x = x * (1 - k) + (sx - 2.3) * k; y = y * (1 - k) + (LANE - 1.25) * k; z = z * (1 - k) + 1.38 * k
    p = road_pt(x, y, z) + Vector((0.012 * math.sin(f * 0.31), 0.010 * math.sin(f * 0.47 + 1), 0.008 * math.sin(f * 0.71)))
    xa, ya, za = path(min(1.0, u + 0.05))
    x0_, y0_, z0_ = path(u)
    look_path = road_pt(xa, ya, za * 0.97) - road_pt(x0_, y0_, z0_)           # v4: path-to-path (the blended camera overtook the
    if look_path.length < 1e-4: look_path = road_pt(x0_ + 1, y0_, z0_) - road_pt(x0_, y0_, z0_)   # look-ahead point = 1-frame backward snap, 28 s)
    look_sam = road_pt(sx + 0.4, LANE, 1.05) - road_pt(x, y, z)
    look_gm = (can.matrix_world.translation + Vector((0, 0, -0.15))) - p
    g0 = 1 - ease((f - 6) / 26.0)
    d = (look_path.normalized() * (1 - k) + look_sam.normalized() * k).normalized()
    d = (d * (1 - g0) + look_gm.normalized() * g0).normalized()
    q = d.to_track_quat('-Z', 'Y') @ Quaternion((0, 0, 1), math.radians(0.3 * math.sin(f * 0.23)))
    return p, q


camd.lens = 30
for o in bpy.data.objects:                                                 # susuki stalks read as cactus (R6): out of this shot
    if o.type == 'MESH' and any(m and m.name.startswith('susuki') for m in o.data.materials): o.hide_render = True
rl = random.Random(77)
for i in range(70):
    u_ = rl.uniform(0.02, 0.95); px, py, pz = path(u_)                          # hang them along the glide: they pass the lens
    x = px + rl.uniform(-1.0, 1.0); y = py + rl.choice((-1, 1)) * rl.uniform(1.4, 2.6); z = pz + rl.uniform(-0.9, 0.6)   # v4: >= 1.4 m (a leaf smeared the lens at 27.5 s)   # v3: >=0.9 m off the lens (no smears)
    lf = mesh_obj('leaf08_%d' % i, maple(rl.uniform(0.07, 0.10)), rl.choice(LEAFC), ROAD, 0.0028)
    lf.location = (x, y, z); lf.rotation_euler = (rl.uniform(0, 6.3), rl.uniform(0, 6.3), rl.uniform(0, 6.3))
    lf.data.materials[0].use_backface_culling = False


META = {}
frames = range(1, NF + 1) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    sc.frame_set(f)
    pose_rider(R1, f); pour(f); bpy.context.view_layer.update(); pose_strings(R1, f)
    p, q = cam08(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    fw = q @ Vector((0, 0, -1)); fw.z = 0; fw.normalize()                       # v4: horizon from the camera's OWN heading (a fixed
    s_ = proj(cam.location + SUN * 1000); h_ = proj(cam.location + fw * 5000)   # +y point swung off-axis as the glide turned = sky flicker)
    if s_[2] < 0: s_ = (-5.0, -5.0, s_[2])                                    # sun behind the camera: no disk
    gpoly, vis = glass_proj()
    sx_ = proj(R1['B']['root'].matrix_world.translation)
    META[f] = dict(sx=s_[0], sy=s_[1], hy=h_[1], glass=gpoly, refl=bool(vis), samx=sx_[0])
    sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    if vis:                                                                   # the frozen street reflected in the shop window
        for o in FAR: o.visible_camera = False
        pm, qm = mirror_cam(p, q); cam.location = pm; cam.rotation_quaternion = qm
        bpy.context.view_layer.update()
        sc.render.filepath = os.path.join(OUT, 'refl_%03d.png' % f); bpy.ops.render.render(write_still=True)
        for o in FAR: o.visible_camera = True
        cam.location = p; cam.rotation_quaternion = q
    print('frame', f, 'refl' if vis else '', flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
