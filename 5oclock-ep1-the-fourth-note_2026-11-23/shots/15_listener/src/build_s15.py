"""5 O'CLOCK Ep1 (The Fourth Note) shot 15 "The Listener" - test v1 (2 s, 48 f @24).
Cel passes (Blender EEVEE toon, transparent): cel_NNN.png = the Listener (hand + loudspeaker-horn head), fg_NNN.png = foreground pole + horn.
Painted sky / crack / ridges / town are drawn per frame in comp_s15.py from the SAME camera maths (cam.py).
usage: blender -b --python build_s15.py -- <ABS outdir> <scale> <frames|all>"""
import sys, os, math, json, random
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
OUT = argv[0]; SCALE = float(argv[1]); FR = argv[2] if len(argv) > 2 else 'all'
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, 'toonlib_v4.py')).read())          # copy of the locked toonlib (needs OUT, SCALE)
exec(open(os.path.join(HERE, 'cam.py')).read())                 # camera maths shared with the comp
NF = 48

LISTENER_MAT = toon('listener', (0.14, 0.10, 0.17), (0.40, 0.31, 0.32), (0.80, 0.90, 1.0), rusty, rimfacing=0.36)
HORN_MAT = toon('hornmat', (0.14, 0.10, 0.17), (0.40, 0.31, 0.32), (0.80, 0.90, 1.0), rusty, rimfacing=0.70)
JOINT_MAT = toon('joint', (0.10, 0.08, 0.13), (0.26, 0.22, 0.26), (0.80, 0.90, 1.0))
HORN_IN = toon('hornin', (0.04, 0.03, 0.06), (0.10, 0.08, 0.10), (0.7, 0.8, 1.0))
HORN_RIM = toon('hornrim', (0.30, 0.22, 0.22), (0.72, 0.56, 0.46), (0.9, 0.95, 1.0))

SC_L = 2.1                      # the Listener is built at ~hand scale then scaled up under one empty
LIST = empty('LIST'); LIST.scale = (SC_L,) * 3
LINE_L = 0.50                   # object-space hull -> 1.05 m in world (>= 0.00075 x 1150 m = 0.86 m)

HORN_PROF = [(y * 1.7, r) for y, r in [(0.0, 0.16), (0.25, 0.20), (0.55, 0.30), (0.95, 0.52), (1.35, 0.95), (1.65, 1.55), (1.85, 2.15), (1.92, 2.30), (1.92, 2.20)]]


def horn_mesh():
    bm = lathe(HORN_PROF, seg=22)
    return bm


def tilt_to(ob, d):
    d = Vector(d).normalized()
    ob.rotation_mode = 'QUATERNION'
    ob.rotation_quaternion = Vector((0, 1, 0)).rotation_difference(d)


def cyl(L, r, seg=14):
    """tapered segment along -Z (finger/arm link), origin at the top joint"""
    prof = [(0.0, r * 0.92), (0.08 * L, r), (0.9 * L, r * 0.93), (L, r * 0.84), (L * 0.985, r * 1.22), (L * 0.93, r * 1.22)]
    bm = lathe(prof, seg=seg)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-90), 3, 'X'), verts=bm.verts)
    return bm


def ball(r):
    return ellipsoid(r, r, r, 14, 9)


# ---------------- the head: a crown of rusted Showa horns, all turning together ----------------
HEAD = empty('HEAD', LIST)
core = mesh_obj('core', ellipsoid(58, 52, 62, 28, 18), JOINT_MAT, HEAD, 0.9)
# neck / body: a thick jointed mast going down behind the ridge (the head is attached to something)
NECK = empty('NECK', HEAD, (0, 0, -30))
parent = NECK
for ni in range(7):
    j = empty('n%d' % ni, parent, (0, 0, 0 if ni == 0 else -70))
    mesh_obj('nseg%d' % ni, cyl(70, 40 - 1.5 * ni), LISTENER_MAT, j, LINE_L)
    mesh_obj('nbl%d' % ni, ball(46 - 1.5 * ni), JOINT_MAT, j, LINE_L * 0.8)
    j.rotation_euler = (math.radians(3 * (-1) ** ni), 0, 0)
    parent = j
random.seed(15)
N_H = 96
horns = []
golden = math.pi * (3 - math.sqrt(5))
for i in range(N_H):
    z = 1 - (i + 0.5) / N_H * 1.55                       # a crown that is more than a hemisphere, open at the bottom
    r = math.sqrt(max(0.0, 1 - z * z)); th = i * golden
    d = Vector((r * math.cos(th), r * math.sin(th) * 0.9, z)).normalized()
    k = random.uniform(4.2, 5.8) * (1.12 if d.z > 0.5 else 1.0)
    ob = mesh_obj('horn%03d' % i, horn_mesh(), HORN_MAT, HEAD, LINE_L / k)
    # a rim ring on the mouth so each horn reads as a loudspeaker
    ob.scale = (k, k, k)
    ob.location = d * (56 + random.uniform(-3, 3))
    horns.append((ob, d, k, random.uniform(0, 0.12)))

# ---------------- the hand: articulated rusted segments, not a human hand ----------------
HAND = empty('HAND', LIST)
palm = mesh_obj('palm', ellipsoid(52, 18, 40, 22, 12), LISTENER_MAT, HAND, LINE_L)
fingers = []
for fi, (fx, lens, rr) in enumerate([(-33, [30, 32, 26], 8.2), (-11, [34, 36, 30], 8.8), (11, [33, 35, 29], 8.6), (33, [27, 29, 23], 7.8)]):
    root = empty('f%d' % fi, HAND, (fx, 0, -34))
    chain = [root]; segs = []
    parent = root
    for si, L in enumerate(lens):
        j = empty('j%d_%d' % (fi, si), parent, (0, 0, 0 if si == 0 else -lens[si - 1]))
        mesh_obj('seg%d_%d' % (fi, si), cyl(L, rr * (1 - 0.1 * si)), LISTENER_MAT, j, LINE_L)
        mesh_obj('bl%d_%d' % (fi, si), ball(rr * 1.18 * (1 - 0.1 * si)), JOINT_MAT, j, LINE_L * 0.8)
        segs.append(j); parent = j
    fingers.append(segs)
thumb_root = empty('thumb', HAND, (-48, -2, -6)); thumb_root.rotation_euler = (0, math.radians(-55), math.radians(20))
tsegs = []; parent = thumb_root
for si, L in enumerate([26, 24, 20]):
    j = empty('tj%d' % si, parent, (0, 0, 0 if si == 0 else -[26, 24, 20][si - 1]))
    mesh_obj('tseg%d' % si, cyl(L, 9.0 * (1 - 0.1 * si)), LISTENER_MAT, j, LINE_L)
    mesh_obj('tbl%d' % si, ball(10.4 * (1 - 0.1 * si)), JOINT_MAT, j, LINE_L * 0.8)
    tsegs.append(j); parent = j
# the arm: a long chain of links with too many joints, going up out of frame
ARM = empty('ARM', HAND, (0, 6, 36))
arm_links = []
parent = ARM
for ai in range(11):
    j = empty('a%d' % ai, parent, (0, 0, 0 if ai == 0 else 60))
    mesh_obj('alink%d' % ai, cyl(60, 13.5 - 0.3 * ai), LISTENER_MAT, j, LINE_L)
    mesh_obj('abl%d' % ai, ball(16.5 - 0.4 * ai), JOINT_MAT, j, LINE_L * 0.8)
    # links point UP (+Z): flip the downward -Z segment
    j.rotation_euler = (math.radians(180), 0, 0) if ai == 0 else (0, 0, 0)
    arm_links.append(j); parent = j

# ---------------- foreground: loudspeaker pole + horn (separate pass, in front of the ridge) ----------------
FG = empty('FG')
pole = mesh_obj('pole', lathe([(0, 0.24), (3.0, 0.21), (8.2, 0.17), (8.4, 0.0)], 16), CONC, FG, 0.05)
pole.rotation_euler = (math.radians(90), 0, 0)
GZ0 = GZ(14.0)
pole.location = (-2.6, 14.0, GZ0)
hg = mesh_obj('fghorn', lathe([(p[0] * 0.30, p[1] * 0.30) for p in HORN_PROF], 30), PAINT, FG, 0.045)
hg.location = (-2.6, 14.0, GZ0 + 7.55)
tilt_to(hg, (0.35, 1.0, 0.12))
mesh_obj('fgcluster', ellipsoid(0.42, 0.30, 0.34, 18, 10), STEEL, FG, 0.03).location = (-2.6, 14.1, GZ0 + 7.45)
mesh_obj('fgbox', ellipsoid(0.40, 0.25, 0.55, 12, 8), STEEL, FG, 0.03).location = (-2.58, 13.9, GZ0 + 5.4)
FGOBJS = [o for o in bpy.data.objects if o.name.startswith(('pole', 'fg')) or o.parent == FG]
FGSET = set(FGOBJS)

# ---------------- camera + lights ----------------
cam_d = bpy.data.cameras.new('cam'); cam_d.lens = LENS_F(1); cam_d.sensor_fit = 'VERTICAL'; cam_d.sensor_height = SENSOR; cam_d.clip_start = 0.5; cam_d.clip_end = 6000
cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam
key = bpy.data.objects.new('key', bpy.data.lights.new('key', 'SUN')); sc.collection.objects.link(key)
key.data.energy = 5.0; key.data.color = (0.78, 0.88, 1.0); key.data.angle = math.radians(1)
key.rotation_euler = Vector((0.0, -1.0, -0.12)).to_track_quat('-Z', 'Y').to_euler()   # light travels toward the camera: backlight from the crack
fill = bpy.data.objects.new('fill', bpy.data.lights.new('fill', 'SUN')); sc.collection.objects.link(fill)
fill.data.energy = 0.35; fill.data.color = (0.85, 0.60, 0.55)
fill.rotation_euler = Vector((-0.4, 1.0, 0.35)).to_track_quat('-Z', 'Y').to_euler()


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def pose(f):
    fp = f - (f - 1) % 2                                   # Listener on twos
    t = fp / (NF - 1)
    # ---- head rises from behind the ridge, horns turn toward the town ----
    rise = ease((fp - 6) / 40.0)
    hp = HEAD_POS(rise)
    LIST.location = (0, 0, 0)
    HEAD.location = Vector(hp) / SC_L
    turn = ease((fp - 26) / 22.0)
    HEAD.rotation_euler = (0, 0, math.radians(lerp(-8, 3, turn)))
    for ob, d, k, delay in horns:
        tt = ease((fp - 26 - delay * 40) / 20.0)
        toward = Vector((-0.30, -1.0, -0.25)).normalized()
        dd = (d * (1 - 0.62 * tt) + toward * (0.62 * tt)).normalized() if d.y < 0.45 else d
        tilt_to(ob, dd)
        ob.scale = (k, k, k * (1 + 0.05 * math.sin(fp * 0.9 + d.x * 7) * turn))
    # ---- hand slides down through the crack, then grips the lip ----
    slide = ease((fp - 4) / 22.0)
    hx, hy, hz = HAND_POS(slide)
    HAND.location = Vector((hx, hy, hz)) / SC_L
    HAND.rotation_euler = (math.radians(lerp(-8, 6, slide)), 0, math.radians(-6))
    curl = ease((fp - 22) / 18.0) + 0.04 * math.sin(fp * 0.5) * ease((fp - 38) / 6.0)
    for fi, segs in enumerate(fingers):
        for si, j in enumerate(segs):
            base = lerp(-4, -2, 0.5)
            ang = (-34 - 14 * si + fi * 2) * curl + (4 + fi) * (1 - curl)
            j.rotation_mode = 'XYZ'
            j.rotation_euler = (math.radians(ang), 0, math.radians((fi - 1.5) * 2.5 * (1 - curl)))
    for si, j in enumerate(tsegs):
        j.rotation_mode = 'XYZ'; j.rotation_euler = (math.radians((-22 - 18 * si) * curl), 0, 0)
    # arm links zig-zag (more joints than an arm should have)
    for ai, j in enumerate(arm_links):
        if ai == 0: continue
        j.rotation_mode = 'XYZ'
        j.rotation_euler = (math.radians((11 if ai % 2 else -10) + 2 * math.sin(fp * 0.2 + ai)), 0, math.radians(6 * math.sin(ai)))
    # foreground horn: it keeps vibrating in the silence
    hg.rotation_mode = 'QUATERNION'
    tilt_to(hg, (0.95 + 0.012 * math.sin(f * 1.7), 0.75, 0.12 + 0.012 * math.cos(f * 2.1)))


meta = dict(frames={}, nf=NF)
frames = list(range(1, NF + 1)) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    pc = CAM_POS(f); ptc = CAM_PITCH(f)
    cam.location = pc; cam_d.lens = LENS_F(f)
    cam.rotation_mode = 'XYZ'; cam.rotation_euler = (math.radians(90 + ptc), 0, 0)
    pose(f)
    bpy.context.view_layer.update()
    for passname, show in (('cel', False), ('fg', True)):
        for ob in bpy.data.objects:
            if ob.type == 'MESH':
                is_fg = (ob in FGSET) or (ob.parent in FGSET)
                ob.hide_render = (is_fg != show)
        sc.render.filepath = os.path.join(OUT, '%s_%03d.png' % (passname, f))
        bpy.ops.render.render(write_still=True)
    meta['frames'][str(f)] = dict(cam=list(pc), pitch=ptc,
                                  head=list(HEAD.matrix_world.translation), hand=list(HAND.matrix_world.translation))
    print('cel+fg', f, flush=True)
json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'))
