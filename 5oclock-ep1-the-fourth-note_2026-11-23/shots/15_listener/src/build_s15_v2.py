"""5 O'CLOCK Ep1 "The Fourth Note" - shot 15 "The Listener", test v2 (2 s, 48 f @24).
Passes per frame (EEVEE toon, transparent): cel_ (head on its neck), hand_ (hand + arm, masked by the crack in the comp),
town_ (3D houses with kawara roofs, windows, antennas, water heaters), fg_ (foreground loudspeaker pole).
usage: blender -b --python build_s15_v2.py -- <ABS outdir> <scale> <frames|all>"""
import sys, os, math, json, random
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
OUT = argv[0]; SCALE = float(argv[1]); FR = argv[2] if len(argv) > 2 else 'all'
os.makedirs(OUT, exist_ok=True)
HERE = os.path.dirname(os.path.abspath(__file__))
_src = open(os.path.join(HERE, 'toonlib_v4.py'), encoding='utf-8').read()
_src = _src.replace("SUNV = tuple(Vector((-0.62, 1.0, 0.24)).normalized())", "SUNV = tuple(Vector((0.156, 0.988, 0.10)).normalized())")
exec(_src)                                                      # locked toonlib, sun moved to the right of frame for this shot
exec(open(os.path.join(HERE, 'cam_v2.py'), encoding='utf-8').read())
from mathutils import Quaternion

CUR = 'cel'


def mk(name, bm, mat, parent=None, line=0.0):
    ob = mesh_obj(name, bm, mat, parent, line); ob['pass'] = CUR; return ob


def up_to(d):
    return Vector((0, 1, 0)).rotation_difference(Vector(d).normalized())


def segY(L, r, seg=14):                    # link along +Y, origin at its base joint
    return lathe([(0.0, r * 0.92), (0.08 * L, r), (0.9 * L, r * 0.93), (L, r * 0.84), (L * 0.985, r * 1.2), (L * 0.93, r * 1.2)], seg=seg)


def segNY(L, r, seg=14):                   # finger link along -Y (smooth, no ring flare: rings read as barrels)
    bm = lathe([(0.0, r * 0.94), (0.1 * L, r), (0.85 * L, r * 0.95), (L, r * 0.86)], seg=seg); bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi, 3, 'Z'), verts=bm.verts); return bm


def segNZ(L, r, seg=16):                   # link along -Z
    bm = segY(L, r, seg); bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(-90), 3, 'X'), verts=bm.verts); return bm


def ball(r):
    return ellipsoid(r, r, r, 14, 9)


def dark_inside(mat, col=(0.004, 0.002, 0.007)):
    """horn interiors (back faces) go near-black, so the mouths read as holes, not eyeballs"""
    nt = mat.node_tree; N = nt.nodes; L = nt.links
    em = [n for n in N if n.type == 'EMISSION'][0]
    src = em.inputs[0].links[0].from_socket
    geo = N.new('ShaderNodeNewGeometry')
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    L.new(geo.outputs['Backfacing'], mx.inputs[0]); L.new(src, mx.inputs[6]); mx.inputs[7].default_value = (*col, 1)
    L.new(mx.outputs[2], em.inputs[0])


RIMW = (1.0, 0.74, 0.50)
METAL = toon('metal', (0.13, 0.10, 0.15), (0.40, 0.30, 0.30), RIMW, rusty, rimfacing=0.42)
JOINT = toon('joint', (0.09, 0.07, 0.11), (0.25, 0.20, 0.23), RIMW, rimfacing=0.5)
HORNM = toon('hornm', (0.30, 0.19, 0.18), (0.56, 0.38, 0.32), RIMW, rusty, rimfacing=0.55)   # rust body so the black mouth reads
dark_inside(HORNM)
HANDM = toon('handm', (0.13, 0.10, 0.15), (0.40, 0.30, 0.30), RIMW, rimfacing=0.42)          # plain: rust streaks became rings on sideways links
NECKM = toon('neckm', (0.13, 0.10, 0.15), (0.40, 0.30, 0.30), RIMW, rusty, rimfacing=0.62)   # tighter rim: no lighthouse stripe
THROAT = emis('throat', (0.0, 0.0, 0.002))     # emission is LINEAR: 0.025 rendered as grey 0.17
HOLD = bpy.data.materials.new('hold'); HOLD.use_nodes = True
_hn = HOLD.node_tree.nodes
for _n in list(_hn): _hn.remove(_n)
HOLD.node_tree.links.new(_hn.new('ShaderNodeHoldout').outputs[0], _hn.new('ShaderNodeOutputMaterial').inputs[0])
HORN_PROF = [(y * 1.7, r) for y, r in [(0.0, 0.16), (0.25, 0.20), (0.55, 0.30), (0.95, 0.52), (1.35, 0.95), (1.65, 1.55), (1.85, 2.15), (1.92, 2.30), (1.92, 2.20)]]
LINE = 1.1                                 # >= 0.00075 x 1150 m

# ======================= HEAD: a field of horns on jointed stalks =======================
CUR = 'cel'
HEAD = empty('HEAD')
mk('hub', ball(34), JOINT, HEAD, LINE)
NECK = empty('NECK', HEAD, (0, 6, -26)); par = NECK; neck = []
for i in range(6):
    j = empty('n%d' % i, par, (0, 0, 0 if i == 0 else -82)); j.rotation_mode = 'XYZ'
    mk('nseg%d' % i, segNZ(82, 25 + 1.6 * i), NECKM, j, LINE); mk('nball%d' % i, ball(31 + 1.6 * i), JOINT, j, LINE * 0.8)
    neck.append(j); par = j
for sx in (-1, 1):                         # shoulders + upper arms: it is a being, not a tree
    sh = empty('sh%d' % sx, neck[2], (sx * 112, 0, -40)); sh.rotation_mode = 'XYZ'; sh.rotation_euler = (0, math.radians(-sx * 28), 0)
    mk('shb%d' % sx, ellipsoid(66, 48, 36, 18, 12), JOINT, sh, LINE)
    mk('sha%d' % sx, segNZ(190, 32), NECKM, sh, LINE)
    bar = mk('shbar%d' % sx, segNZ(120, 30), NECKM, neck[2], LINE)
    bar.rotation_euler = (0, math.radians(-sx * 90), 0); bar.location = (0, 0, -36)
random.seed(15)
TOWN_C = Vector((60.0, 150.0, 8.0))
stalks = []
for i in range(118):
    th = math.radians(random.triangular(0, 100, 35)); ph = random.uniform(0, 2 * math.pi)
    d = Vector((math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph) * 0.55, math.cos(th))).normalized()
    B = empty('sb%d' % i, HEAD, tuple(d * 30)); B.rotation_mode = 'QUATERNION'; B.rotation_quaternion = up_to(d)
    L1 = random.uniform(30, 92) * (0.75 + 0.45 * math.cos(th)); L2 = random.uniform(24, 56); r = random.uniform(3.0, 4.4)
    mk('ss1_%d' % i, segY(L1, r, 10), METAL, B, LINE * 0.75)
    J = empty('sj%d' % i, B, (0, L1, 0)); J.rotation_mode = 'QUATERNION'
    J.rotation_quaternion = Euler((math.radians(random.uniform(-22, 22)), 0, math.radians(random.uniform(-22, 22)))).to_quaternion()
    mk('sjb%d' % i, ball(r * 1.45), JOINT, J, LINE * 0.6)
    mk('ss2_%d' % i, segY(L2, r * 0.85, 10), METAL, J, LINE * 0.7)
    Hn = empty('sh%d' % i, J, (0, L2, 0)); Hn.rotation_mode = 'QUATERNION'
    k = random.uniform(5.4, 8.6)
    hm = mk('horn%d' % i, lathe(HORN_PROF, 24), HORNM, Hn, LINE / k); hm.scale = (k, k, k)
    mk('throat%d' % i, lathe([(2.85, 0.001), (2.85, 1.55)], 24, cap_back=False), THROAT, hm, 0)   # black hole inside the bell
    stalks.append(dict(Hn=Hn, J=J, delay=random.uniform(0, 2.5), ph=random.uniform(0, 6.3), aim=None))

# ======================= HAND: pushes out of the crack and grips the lower lip =======================
CUR = 'hand'
HAND = empty('HAND'); HAND.rotation_mode = 'XYZ'
mk('palm', ellipsoid(104, 44, 13, 24, 10), toon('palmm', (0.08, 0.06, 0.10), (0.18, 0.14, 0.17)), HAND, LINE)
fingers = []
for fi, (fx, lens, rr) in enumerate([(-66, [40, 34, 28, 22], 12.0), (-22, [44, 38, 31, 24], 13.0), (22, [43, 37, 30, 23], 12.8), (66, [36, 31, 25, 19], 11.4)]):
    mk('knuck%d' % fi, ellipsoid(rr * 1.7, rr * 1.4, rr * 1.35, 14, 9), JOINT, HAND, LINE).location = (fx, -30, 2)
    par = HAND; segs = []
    for si, L in enumerate(lens):
        j = empty('f%d_%d' % (fi, si), par, (fx, -30, 0) if si == 0 else (0, -lens[si - 1], 0)); j.rotation_mode = 'XYZ'
        rs = rr * (1 - 0.08 * si)
        mk('fs%d_%d' % (fi, si), segNY(L, rs), HANDM, j, LINE); mk('fb%d_%d' % (fi, si), ball(rs * 1.2), JOINT, j, LINE * 0.8)
        segs.append(j); par = j
    fingers.append(segs)
TH = empty('thumb', HAND, (-104, -10, -6)); TH.rotation_mode = 'XYZ'; TH.rotation_euler = (math.radians(30), 0, math.radians(-28))
thumb = []; par = TH
for si, L in enumerate([34, 28, 22]):
    j = empty('t%d' % si, par, (0, 0, 0) if si == 0 else (0, -[34, 28, 22][si - 1], 0)); j.rotation_mode = 'XYZ'
    mk('ts%d' % si, segNY(L, 13.5 * (1 - 0.08 * si)), HANDM, j, LINE); mk('tb%d' % si, ball(16 * (1 - 0.08 * si)), JOINT, j, LINE * 0.8)
    thumb.append(j); par = j
ARM = empty('ARM', HAND, (0, 40, 6)); par = ARM; arm = []
for ai in range(4):
    j = empty('a%d' % ai, par, (0, 0, 0) if ai == 0 else (0, 95, 0)); j.rotation_mode = 'XYZ'
    mk('as%d' % ai, segY(95, 26 - 2 * ai), HANDM, j, LINE); mk('ab%d' % ai, ball(32 - 2 * ai), JOINT, j, LINE * 0.8)
    arm.append(j); par = j
OCC = None


def build_occluder(f):
    """the sky itself as a holdout wall at y = CRACK_Y with the crack as its hole: whatever is behind it shows only through the gash"""
    global OCC
    bm = bmesh.new(); Y = CRACK_Y + 0.5
    up = [bm.verts.new((float(x), Y, upper_lip(float(x), f))) for x in CXS]
    lo = [bm.verts.new((float(x), Y, lower_lip(float(x), f))) for x in CXS]
    top = [bm.verts.new((float(x), Y, 5000.0)) for x in CXS]
    bot = [bm.verts.new((float(x), Y, -3000.0)) for x in CXS]
    for i in range(len(CXS) - 1):
        bm.faces.new((up[i], up[i + 1], top[i + 1], top[i])); bm.faces.new((bot[i], bot[i + 1], lo[i + 1], lo[i]))
    for xa, xb in ((-9000.0, float(CXS[0])), (float(CXS[-1]), 9000.0)):
        bm.faces.new([bm.verts.new(p) for p in ((xa, Y, -3000.0), (xb, Y, -3000.0), (xb, Y, 5000.0), (xa, Y, 5000.0))])
    me = bpy.data.meshes.new('occ'); bm.to_mesh(me); bm.free(); me.materials.append(HOLD)
    if OCC is None:
        OCC = bpy.data.objects.new('occ', me); sc.collection.objects.link(OCC); OCC['pass'] = 'hand'
    else:
        old = OCC.data; OCC.data = me; bpy.data.meshes.remove(old)

# ======================= TOWN: 3D houses (joined meshes per material) =======================
CUR = 'town'


def tiles_tex(row_axis, col_axis):
    def f(nt, ramp):
        N = nt.nodes; L = nt.links
        tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sp.inputs[0])

        def band(axis, period, thr):
            m = N.new('ShaderNodeMath'); m.operation = 'MULTIPLY'; m.inputs[1].default_value = 2 * math.pi / period
            L.new(sp.outputs[axis], m.inputs[0])
            s = N.new('ShaderNodeMath'); s.operation = 'SINE'; L.new(m.outputs[0], s.inputs[0])
            g = N.new('ShaderNodeMath'); g.operation = 'GREATER_THAN'; g.inputs[1].default_value = thr; L.new(s.outputs[0], g.inputs[0])
            return g
        a = band(row_axis, 0.9, 0.55); b = band(col_axis, 0.62, 0.86)
        s1 = N.new('ShaderNodeMath'); s1.operation = 'MULTIPLY_ADD'; s1.inputs[1].default_value = -0.30; s1.inputs[2].default_value = 1.0
        L.new(a.outputs[0], s1.inputs[0])
        s2 = N.new('ShaderNodeMath'); s2.operation = 'MULTIPLY_ADD'; s2.inputs[1].default_value = -0.16
        L.new(b.outputs[0], s2.inputs[0]); L.new(s1.outputs[0], s2.inputs[2])
        vm = N.new('ShaderNodeVectorMath'); vm.operation = 'SCALE'
        L.new(ramp.outputs[0], vm.inputs[0]); L.new(s2.outputs[0], vm.inputs['Scale'])
        return vm.outputs[0]
    return f


ROOFX = toon('roofx', (0.16, 0.16, 0.25), (0.33, 0.33, 0.44), None, tiles_tex('Y', 'X'))
ROOFY = toon('roofy', (0.16, 0.16, 0.25), (0.33, 0.33, 0.44), None, tiles_tex('X', 'Y'))
PLAST = toon('plaster', (0.33, 0.26, 0.33), (0.62, 0.52, 0.50))
WOOD = toon('wood', (0.20, 0.14, 0.16), (0.42, 0.30, 0.27))
WINL = emis('winlit', (1.0, 0.62, 0.30), 1.0)
WIND = emis('windark', (0.05, 0.045, 0.07))
ANTM = emis('ant', (0.10, 0.07, 0.10))
HEAT = toon('heater', (0.30, 0.30, 0.36), (0.66, 0.66, 0.70))
geo = {}


def bmk(key):
    if key not in geo: geo[key] = bmesh.new()
    return geo[key]


def add_box(bm, M):
    bmesh.ops.create_cube(bm, size=1.0, matrix=M)


def add_quad(bm, pts):
    vs = [bm.verts.new(p) for p in pts]; bm.faces.new(vs)


rh = random.Random(42)
row_y = 34.0
while row_y < 640:
    half = 0.30 * row_y + 18
    x = -half + rh.uniform(0, 8)
    while x < half:
        w = rh.uniform(8.5, 13.0); d = rh.uniform(8.0, 11.5); h = rh.uniform(5.2, 7.6)
        y = row_y + rh.uniform(-3, 3)
        if abs(x - 5.0) > 10.0 and rh.random() > 0.30:
            band = 'n' if y < 230 else 'f'
            g = GZ(y) - 1.2; rot = rh.choice([0.0, math.pi / 2])
            R = Matrix.Rotation(rot, 4, 'Z'); T = Matrix.Translation((x, y, g))
            M = T @ R @ Matrix.Translation((0, 0, h / 2)) @ Matrix.Diagonal((w, d, h, 1))
            add_box(bmk(('plaster' if rh.random() < 0.6 else 'wood', band)), M)
            o = 0.7; rr = rh.uniform(2.2, 3.4)
            pts = [(-w / 2 - o, -d / 2 - o, h), (w / 2 + o, -d / 2 - o, h), (w / 2 + o, 0, h + rr), (-w / 2 - o, 0, h + rr),
                   (-w / 2 - o, d / 2 + o, h), (w / 2 + o, d / 2 + o, h)]
            P = [tuple(T @ R @ Vector(p)) for p in pts]
            rb = bmk(('roofx' if rot == 0 else 'roofy', band))
            add_quad(rb, [P[0], P[1], P[2], P[3]]); add_quad(rb, [P[3], P[2], P[5], P[4]])
            gb = bmk(('plaster', band))
            vs = [gb.verts.new(P[i]) for i in (0, 3, 4)]; gb.faces.new(vs)
            vs = [gb.verts.new(P[i]) for i in (1, 5, 2)]; gb.faces.new(vs)
            # windows on the camera-facing wall (world -Y), lit or dark
            fy = y - (d / 2 if rot == 0 else w / 2) - 0.06; span = (w if rot == 0 else d)
            for wi in range(rh.randint(1, 3)):
                wx = x + rh.uniform(-span / 2 + 1.4, span / 2 - 1.4); wz = g + rh.choice([2.0, 4.6]) + 1.2
                add_quad(bmk(('winlit' if rh.random() < 0.42 else 'windark', band)), [(wx - 0.8, fy, wz), (wx + 0.8, fy, wz), (wx + 0.8, fy, wz + 1.1), (wx - 0.8, fy, wz + 1.1)])
            if rh.random() < 0.35:            # TV antenna: mast + 3 cross elements
                ax, ay, az = x + rh.uniform(-2, 2), y, g + h + rr
                ab = bmk(('ant', band))
                add_box(ab, Matrix.Translation((ax, ay, az + 1.4)) @ Matrix.Diagonal((0.12, 0.12, 2.8, 1)))
                for kz in (2.2, 2.6, 3.0):
                    add_box(ab, Matrix.Translation((ax, ay, az + kz)) @ Matrix.Diagonal((1.6 - 0.3 * (kz - 2.2), 0.08, 0.08, 1)))
            if rh.random() < 0.25:            # solar water heater on the roof
                hx = x + rh.uniform(-2.5, 2.5)
                add_box(bmk(('heater', band)), Matrix.Translation((hx, y + 1.0, g + h + rr * 0.6)) @ Matrix.Rotation(-0.5, 4, 'X') @ Matrix.Diagonal((2.4, 1.6, 0.25, 1)))
                add_box(bmk(('heater', band)), Matrix.Translation((hx, y + 1.8, g + h + rr * 0.85)) @ Matrix.Diagonal((2.6, 0.7, 0.7, 1)))
        x += w + rh.uniform(1.5, 6.0)
    row_y += rh.uniform(10.5, 14.0) * (1 + row_y / 500)
MATS = dict(plaster=PLAST, wood=WOOD, roofx=ROOFX, roofy=ROOFY, winlit=WINL, windark=WIND, ant=ANTM, heater=HEAT)
for (mname, band), bm in geo.items():
    line = 0 if mname in ('winlit', 'windark', 'ant') else (0.07 if band == 'n' else 0.30)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mk('town_%s_%s' % (mname, band), bm, MATS[mname], None, line)

# ======================= FG: loudspeaker pole on the hillside =======================
CUR = 'fg'
FGR = empty('FGR'); GZ0 = GZ(14.0)
pole = mk('pole', lathe([(0, 0.24), (3.0, 0.21), (8.2, 0.17), (8.4, 0.0)], 16), CONC, FGR, 0.05)
pole.rotation_euler = (math.radians(90), 0, 0); pole.location = (-2.6, 14.0, GZ0)
hg = mk('fghorn', lathe([(p[0] * 0.30, p[1] * 0.30) for p in HORN_PROF], 30), PAINT, FGR, 0.045)
hg.location = (-2.6, 14.0, GZ0 + 7.55); hg.rotation_mode = 'QUATERNION'
mk('fgcluster', ellipsoid(0.42, 0.30, 0.34, 18, 10), STEEL, FGR, 0.03).location = (-2.6, 14.1, GZ0 + 7.45)
mk('fgbox', ellipsoid(0.40, 0.25, 0.55, 12, 8), STEEL, FGR, 0.03).location = (-2.58, 13.9, GZ0 + 5.4)

# ======================= camera + lights =======================
cam_d = bpy.data.cameras.new('cam'); cam_d.sensor_fit = 'VERTICAL'; cam_d.sensor_height = SENSOR
cam_d.clip_start = 0.5; cam_d.clip_end = 8000
cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam


def sunlight(name, travel, energy, col):
    o = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SUN')); sc.collection.objects.link(o)
    o.data.energy = energy; o.data.color = col; o.data.angle = math.radians(1)
    o.rotation_euler = Vector(travel).to_track_quat('-Z', 'Y').to_euler(); return o


sunlight('sun', (-0.156, -0.988, -0.03), 5.0, (1.0, 0.76, 0.52))            # low sun, right of frame, behind everything
sunlight('crack', (0.10, -0.80, -0.60), 0.9, (0.62, 0.74, 1.0))            # cold light spilling from the crack above
sunlight('fill', (0.35, 1.0, -0.35), 0.12, (0.70, 0.55, 0.75))             # very weak fill: camera-facing walls stay in dusk shadow


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def ease_out(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return a + (b - a) * t


# aim every horn at the town from the head's final position (HEAD only translates, so this is constant)
HEAD.location = HEAD_POS(1.0); bpy.context.view_layer.update()
for s in stalks:
    qJ = s['J'].matrix_world.to_quaternion()
    dvec = (TOWN_C - s['Hn'].matrix_world.translation).normalized()
    s['aim'] = qJ.inverted() @ up_to(dvec)

GRIP = [12, 62, 40, 30]


def pose(f):
    fp = f - (f - 1) % 2                                          # characters on twos
    # head: rises with the deceleration of something enormous
    HEAD.location = HEAD_POS(ease_out((fp - 1) / 33.0))
    for i, j in enumerate(neck):
        j.rotation_euler = (math.radians(1.5 * math.sin(fp * 0.09 + i)), 0, math.radians(1.0 * math.sin(fp * 0.07 + i * 0.7)))
    for s in stalks:
        idle = Euler((math.radians(4 * math.sin(fp * 0.16 + s['ph'])), 0, math.radians(3 * math.cos(fp * 0.13 + s['ph'] * 1.3)))).to_quaternion()
        t0 = 31 + s['delay']; w = ease((fp - t0) / 9.0)
        q = idle.slerp(s['aim'], 0.75 * w)                         # 3/4 turn: the bells stay readable as horns
        if fp > t0 + 9:                                           # arrival: a damped wobble, all together
            k = fp - (t0 + 9)
            q = q @ Euler((math.radians(5 * math.exp(-k / 3.5) * math.sin(k * 1.7)), 0, 0)).to_quaternion()
        s['Hn'].rotation_quaternion = q
    # hand: deep on the other side -> pushes out through the gash -> slams over the lower lip
    push = ease((fp - 4) / (IMPACT - 8.0))
    y = lerp(CRACK_Y + 270.0, CRACK_Y + 8.0, push)
    z = lower_lip(HAND_X, fp) + 15.0 + lerp(26.0, 0.0, push)
    HAND.location = (HAND_X, y, z)
    HAND.rotation_euler = (math.radians(lerp(-12, -4, push)), math.radians(4), math.radians(-5))
    slam = ease((fp - (IMPACT - 3)) / 3.0)
    over = math.exp(-max(0, fp - IMPACT) / 3.0) * math.sin(max(0, fp - IMPACT) * 1.6) * (1 if fp >= IMPACT else 0)
    tight = 0.06 * ease((fp - 34) / 10.0)
    for fi, segs in enumerate(fingers):
        for si, j in enumerate(segs):
            open_a = [0, 6, 6, 5][si] + 2 * math.sin(fp * 0.3 + fi)
            a = lerp(open_a, GRIP[si] * (1 + tight) + (fi - 1.5) * 2, slam) + (7 * over if si == 1 else 0)
            j.rotation_euler = (math.radians(a), 0, math.radians((fi - 1.5) * 6 * (1 - slam) if si == 0 else 0))
    for si, j in enumerate(thumb):
        j.rotation_euler = (math.radians(lerp(4, [18, 34, 24][si], slam)), 0, 0)
    for ai, j in enumerate(arm):
        if ai: j.rotation_euler = (math.radians((12 if ai % 2 else -10) + 2 * math.sin(fp * 0.2 + ai)), 0, 0)
    # foreground horn: still trembling from the last note
    hg.rotation_quaternion = up_to((1.0 + 0.012 * math.sin(f * 1.7), -0.28, -0.06 + 0.012 * math.cos(f * 2.1)))   # side-on: the bell reads


meshes = [o for o in bpy.data.objects if o.type == 'MESH']
meta = dict(frames={})
frames = list(range(1, NF + 1)) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    cam.location = CAM_POS(f); cam.rotation_mode = 'XYZ'; cam.rotation_euler = (math.radians(90 + CAM_PITCH(f)), 0, 0)
    cam_d.lens = LENS_F(f)
    pose(f); build_occluder(f); bpy.context.view_layer.update()
    for pn in ('cel', 'hand', 'town', 'fg'):
        for o in meshes + [OCC]: o.hide_render = (o.get('pass') != pn)
        sc.render.filepath = os.path.join(OUT, '%s_%03d.png' % (pn, f))
        bpy.ops.render.render(write_still=True)
    meta['frames'][str(f)] = dict(head=list(HEAD.matrix_world.translation), hand=list(HAND.matrix_world.translation))
    print('passes', f, flush=True)
json.dump(meta, open(os.path.join(OUT, 'meta.json'), 'w'))
