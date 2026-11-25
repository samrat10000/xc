"""EP1 v6 shot 2: Sam dozing in an armchair in a top-floor Manhattan apartment. One wall is floor-to-ceiling glass,
the city burns outside. Phone lights up, he wakes and looks at it.
blender -b -P penthouse.py -- (env: SAMBLEND, OUT, RES=540, SPP=48, FRAME, CAMV=a)"""
import bpy, bmesh, math, os, random, sys
from mathutils import Vector, Matrix, noise
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'cast'))
sys.path.insert(0, os.environ.get('CASTLIB', ''))
import castlib as L
C = L.lin
V = Vector
OUT = os.environ.get('OUT', '/tmp/pent.png')
PLATE = os.environ.get('PLATE', '')
CAMV = os.environ.get('CAMV', 'a')
bpy.ops.wm.open_mainfile(filepath=os.environ['SAMBLEND'])
sc = bpy.context.scene
for o in list(sc.objects):
    if o.type in ('LIGHT', 'CAMERA') or o.name == 'floor': bpy.data.objects.remove(o)
rig = [o for o in sc.objects if o.type == 'ARMATURE'][0]
sam_body = [o for o in sc.objects if o.parent == rig and o.type == 'MESH' and 'teeth' not in o.name]
col = bpy.data.collections.new('set'); sc.collection.children.link(col)

def nodes(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; return m, nt, nt.nodes, nt.links, nt.nodes['Principled BSDF']
def noise_t(n, l, scale, detail=4, rough=.55, vec=None, dims='3D'):
    t = n.new('ShaderNodeTexNoise'); t.noise_dimensions = dims; t.inputs['Scale'].default_value = scale
    t.inputs['Detail'].default_value = detail; t.inputs['Roughness'].default_value = rough
    if vec is not None: l.new(vec, t.inputs['Vector'])
    return t
def mr(n, l, v, a, b, c=0., d=1.):
    m = n.new('ShaderNodeMapRange'); m.inputs[1].default_value = a; m.inputs[2].default_value = b
    m.inputs[3].default_value = c; m.inputs[4].default_value = d; l.new(v, m.inputs[0]); return m.outputs[0]
def mth(n, l, op, a, b=0.):
    m = n.new('ShaderNodeMath'); m.operation = op
    for i, v in ((0, a), (1, b)):
        if isinstance(v, (int, float)): m.inputs[i].default_value = v
        else: l.new(v, m.inputs[i])
    return m.outputs[0]
def mixc(n, l, f, a, b):
    m = n.new('ShaderNodeMix'); m.data_type = 'RGBA'
    for inp, v in ((m.inputs[0], f), (m.inputs[6], a), (m.inputs[7], b)):
        if isinstance(v, (int, float)): inp.default_value = v
        elif isinstance(v, tuple): inp.default_value = (*v, 1) if len(v) == 3 else v
        else: l.new(v, inp)
    return m.outputs[2]
def box(name, loc, size, mat, bevel=0., rot=(0, 0, 0)):
    o = L.box(name, loc, tuple(size), col, rot=rot, bevel=bevel); L.setmat(o, mat); return o

# ------------------------------------------------------------------ pose: seated, slumped, phone in right hand
def aim(bn, d):
    pb = rig.pose.bones[bn]; bpy.context.view_layer.update()
    M = rig.matrix_world.to_3x3().normalized()
    cur = pb.matrix.copy(); cd = (cur.to_3x3() @ V((0, 1, 0))).normalized()
    td = (M.inverted() @ V(d)).normalized()
    q = cd.rotation_difference(td)
    pb.matrix = Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ cur.to_3x3().normalized().to_4x4() @ Matrix.Diagonal(cur.to_scale()).to_4x4()
    bpy.context.view_layer.update()
WAKE = float(os.environ.get('WAKE', '1'))      # 0 asleep (head dropped), 1 looking at the phone
def lerpv(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
def pose(WAKE):
    for pb_ in rig.pose.bones: pb_.matrix_basis = Matrix()
    bpy.context.view_layer.update()
    for bn in ('spine05', 'spine04', 'spine03'): aim(bn, (0, .38, .92))
    for bn in ('spine02', 'spine01'): aim(bn, (0, .22, .97))
    nk = [b.name for b in rig.pose.bones if b.name.startswith('neck')]
    for bn in nk: aim(bn, lerpv((-.35, -.25, .9), (0, -.30, .95), WAKE))
    aim('head', lerpv((-.5, -.55, .67), (0, -.52, .85), WAKE))
    for s, sg in (('L', 1), ('R', -1)):
        for bn in ('upperleg01', 'upperleg02'): aim(f'{bn}.{s}', (sg * .16, -1, .06))
        for bn in ('lowerleg01', 'lowerleg02'): aim(f'{bn}.{s}', (sg * .06, -.32, -1))
        aim(f'foot.{s}', (sg * .1, -1, -.45))
    # left arm rests on the armrest
    for bn in ('upperarm01.L', 'upperarm02.L'): aim(bn, (.28, .2, -1))
    for bn in ('lowerarm01.L', 'lowerarm02.L', 'wrist.L'): aim(bn, (.08, -1, -.08))
    # right hand holds the phone up in front of the chest
    for bn in ('upperarm01.R', 'upperarm02.R'): aim(bn, lerpv((-.2, .1, -1), (-.12, -.35, -1), WAKE))
    for bn in ('lowerarm01.R', 'lowerarm02.R'): aim(bn, lerpv((.08, -1, -.05), (.42, -.72, .55), WAKE))
    aim('wrist.R', lerpv((.08, -1, -.1), (.3, -.8, .5), WAKE))
    for f in range(2, 6):                    # loose curl around the phone
        for k in (1, 2, 3):
            b = rig.pose.bones.get(f'finger{f}-{k}.R')
            if b: b.rotation_mode = 'XYZ'; b.rotation_euler = (math.radians(30 if k == 1 else 38), 0, 0)

pose(WAKE)
bpy.context.view_layer.update()
W_ = rig.matrix_world
hip = (W_ @ rig.pose.bones['upperleg02.L'].head + W_ @ rig.pose.bones['upperleg02.R'].head) / 2
heel = W_ @ rig.pose.bones['foot.L'].head
# put the seated hips on the cushion (seat top .46) and the feet on the floor
rig.location += V((0, 0, .47 - hip.z)); bpy.context.view_layer.update()
hip = (W_ @ rig.pose.bones['upperleg02.L'].head + W_ @ rig.pose.bones['upperleg02.R'].head) / 2
hip = (rig.matrix_world @ rig.pose.bones['upperleg02.L'].head + rig.matrix_world @ rig.pose.bones['upperleg02.R'].head) / 2
heel = rig.matrix_world @ rig.pose.bones['foot.L'].head
headp = rig.matrix_world @ rig.pose.bones['head'].tail
print('HIP', hip, 'HEEL', heel, 'HEAD', headp)
SX, SY = hip.x, hip.y

# ------------------------------------------------------------------ materials
def mat_simple(name, colr, rough=.6, metal=0., bump=0., bscale=40.):
    m, nt, n, l, bs = nodes(name)
    bs.inputs['Base Color'].default_value = (*C(colr), 1); bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    if bump:
        t = noise_t(n, l, bscale, 6); b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump
        l.new(t.outputs['Fac'], b.inputs['Height']); l.new(b.outputs[0], bs.inputs['Normal'])
    return m
def mat_fabric(name, colr):
    m, nt, n, l, bs = nodes(name)
    t = noise_t(n, l, 900, 2); t2 = noise_t(n, l, 6, 4)
    l.new(mixc(n, l, mr(n, l, t2.outputs['Fac'], .35, .7, 0, .35), C(colr), C('#1a1714')), bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = .9; bs.inputs['Sheen Weight'].default_value = .3; bs.inputs['Sheen Roughness'].default_value = .5
    b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = .25; l.new(t.outputs['Fac'], b.inputs['Height']); l.new(b.outputs[0], bs.inputs['Normal'])
    return m
def mat_floor():
    m, nt, n, l, bs = nodes('Oak')
    tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 9, 1)
    l.new(tc.outputs['Object'], mp.inputs['Vector'])
    w = n.new('ShaderNodeTexWave'); w.wave_type = 'BANDS'; w.bands_direction = 'X'; w.inputs['Scale'].default_value = 2.
    w.inputs['Distortion'].default_value = 6; w.inputs['Detail'].default_value = 3; l.new(mp.outputs[0], w.inputs['Vector'])
    br = n.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 1.; br.inputs['Mortar Size'].default_value = .004
    br.offset = .37; mp2 = n.new('ShaderNodeMapping'); mp2.inputs['Scale'].default_value = (.55, 4.2, 1); l.new(tc.outputs['Object'], mp2.inputs['Vector'])
    l.new(mp2.outputs[0], br.inputs['Vector'])
    br.inputs['Color1'].default_value = (*C('#3b2a1e'), 1); br.inputs['Color2'].default_value = (*C('#4a3524'), 1); br.inputs['Mortar'].default_value = (*C('#120c08'), 1)
    c = mixc(n, l, mr(n, l, w.outputs['Fac'], .2, .9, 0, .5), br.outputs['Color'], C('#22170f'))
    l.new(c, bs.inputs['Base Color'])
    sm = noise_t(n, l, 3, 6)
    l.new(mr(n, l, sm.outputs['Fac'], .35, .7, .12, .34), bs.inputs['Roughness'])
    b = n.new('ShaderNodeBump'); b.inputs['Strength'].default_value = .08; l.new(br.outputs['Fac'], b.inputs['Height']); l.new(b.outputs[0], bs.inputs['Normal'])
    return m
def mat_glass():
    m = bpy.data.materials.new('WindowGlass'); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; l = nt.links
    n.remove(n['Principled BSDF'])
    tr = n.new('ShaderNodeBsdfTransparent'); tr.inputs[0].default_value = (*C('#c8d2d0'), 1)
    gl = n.new('ShaderNodeBsdfGlossy'); gl.inputs['Roughness'].default_value = .0
    smd = noise_t(n, l, 14, 6); l.new(mr(n, l, smd.outputs['Fac'], .55, .8, 0., .07), gl.inputs['Roughness'])
    lw = n.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = .12
    mx = n.new('ShaderNodeMixShader'); l.new(mth(n, l, 'ADD', lw.outputs['Fresnel'], .05), mx.inputs[0])
    l.new(tr.outputs[0], mx.inputs[1]); l.new(gl.outputs[0], mx.inputs[2])
    l.new(mx.outputs[0], n['Material Output'].inputs['Surface']); return m
def emit(name, colr, s):
    m, nt, n, l, bs = nodes(name)
    bs.inputs['Base Color'].default_value = (0, 0, 0, 1); bs.inputs['Emission Color'].default_value = (*C(colr), 1)
    bs.inputs['Emission Strength'].default_value = s; return m

# ------------------------------------------------------------------ apartment (glass wall at y = GY, facing -Y)
GY = SY - 1.7; RW = 7.; CH = 3.3; BACK = SY + 4.5
oak = mat_floor(); conc = mat_simple('Plaster', '#4c4844', .85, bump=.05, bscale=8)
black = mat_simple('Mullion', '#0c0c0d', .35, metal=.6)
box('floor', (SX, (GY + BACK) / 2, -.05), (RW * 2, BACK - GY, .1), oak)
box('ceiling', (SX, (GY + BACK) / 2, CH + .05), (RW * 2, BACK - GY, .1), conc)
box('wall back', (SX, BACK + .05, CH / 2), (RW * 2, .1, CH), conc)
box('wall L', (SX - RW, (GY + BACK) / 2, CH / 2), (.1, BACK - GY, CH), conc)
box('wall R', (SX + RW, (GY + BACK) / 2, CH / 2), (.1, BACK - GY, CH), conc)
glass = mat_glass()
gp = box('glass', (SX, GY, CH / 2), (RW * 2, .012, CH), glass)
gp.visible_shadow = False
for i in range(-4, 5):
    box('mullion', (SX + i * 1.55, GY + .03, CH / 2), (.06, .09, CH), black)
for z in (.02, CH - .03):
    box('frame h', (SX, GY + .03, z), (RW * 2, .1, .07), black)
box('sill', (SX, GY + .2, .03), (RW * 2, .3, .06), black)
box('soffit', (SX, GY + .25, CH - .12), (RW * 2, .5, .24), conc)
# armchair (low lounge chair, worn charcoal fabric)
fab = mat_simple('Leather', '#231812', .42, bump=.12, bscale=55); wood = mat_simple('Walnut', '#2a1a10', .45, bump=.1, bscale=30)
cy = SY + .12
box('seat', (SX, cy - .05, .32), (.78, .72, .2), fab, bevel=.07)
box('back', (SX, cy + .36, .72), (.78, .18, .72), fab, bevel=.08, rot=(math.radians(-18), 0, 0))
for sg in (-1, 1):
    arm_ = box('arm', (SX + sg * .47, cy, .5), (.16, .84, .3), fab, bevel=.06)
    if CAMV == 'a': arm_.visible_camera = False
    for yy in (-.38, .42): box('leg', (SX + sg * .45, cy + yy, .12), (.05, .05, .24), wood, bevel=.015)
box('chair base', (SX, cy, .24), (1.08, .86, .06), wood, bevel=.02)
# side table with a dead mug, rug, floor lamp turned low
box('table top', (SX + .82, cy - .1, .52), (.42, .42, .03), wood, bevel=.01)
box('table leg', (SX + .82, cy - .1, .26), (.04, .04, .5), black)
box('table foot', (SX + .82, cy - .1, .01), (.3, .3, .02), black)
mug = L.tube('mug', [V((SX + .78, cy - .05, .535)), V((SX + .78, cy - .05, .63))], [.042, .045], col, sides=24)
L.setmat(mug, mat_simple('Ceramic', '#d8d2c8', .25))
box('rug', (SX, cy - .7, .005), (2.4, 1.8, .01), mat_fabric('Rug', '#2c2622'))
lp = V((SX - 2.8, cy + 2.2, 0))
box('lamp base', lp + V((0, 0, .015)), (.28, .28, .03), black)
L.tube('lamp pole', [lp, lp + V((0, 0, 1.55))], [.012, .012], col, sides=10).data.materials.append(black)
shade = L.tube('lamp shade', [lp + V((0, 0, 1.45)), lp + V((0, 0, 1.72))], [.2, .15], col, sides=32, cap=False)
L.setmat(shade, emit('Shade', '#ffb070', 1.2))
ld = bpy.data.lights.new('lamp', 'POINT'); ld.energy = 15; ld.color = C('#ffb070'); ld.shadow_soft_size = .12
lo = bpy.data.objects.new('lamp', ld); col.objects.link(lo); lo.location = lp + V((0, 0, 1.58))

# phone in the right hand, screen facing his face
PHONE_PNG = os.environ.get("PHONE_PNG", "/tmp/phone_screen.png")
if not os.path.exists(PHONE_PNG): os.system(f"python3 {HERE}/phone_screen.py {PHONE_PNG}")
ph = box('phone', (0, 0, 0), (.072, .0085, .152), mat_simple('PhoneBody', '#141416', .3, metal=.7), bevel=.006)
m, nt, n, l, bs = nodes('Screen')
im = n.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(PHONE_PNG)
tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping')
mp.inputs['Location'].default_value = (.5, 0, .5); mp.inputs['Scale'].default_value = (1 / .066, 1, 1 / .144)
l.new(tc.outputs['Object'], mp.inputs['Vector'])
sxz = n.new('ShaderNodeSeparateXYZ'); l.new(mp.outputs[0], sxz.inputs[0]); cxy = n.new('ShaderNodeCombineXYZ')
l.new(sxz.outputs['X'], cxy.inputs[0]); l.new(sxz.outputs['Z'], cxy.inputs[1]); l.new(cxy.outputs[0], im.inputs[0])
bs.inputs['Base Color'].default_value = (0, 0, 0, 1); bs.inputs['Roughness'].default_value = .05
l.new(im.outputs['Color'], bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = 2.2 * float(os.environ.get('SCREEN', '1'))
scr = box('screen', (0, -.0045, 0), (.066, .001, .144), m)
scr.parent = ph
wr = rig.pose.bones['wrist.R']; wm = rig.matrix_world @ wr.matrix
pal = rig.matrix_world @ rig.pose.bones['metacarpal3.R'].tail
eye = headp + V((0, -.06, -.08))
fwd = (eye - pal).normalized()
ph.matrix_world = Matrix.Translation(pal + fwd * .035 + V((0, 0, .03))) @ (fwd.to_track_quat('-Y', 'Z')).to_matrix().to_4x4()
sl = bpy.data.lights.new('screen glow', 'AREA'); sl.size = .07; sl.energy = 1.4 * float(os.environ.get('SCREEN', '1')); sl.color = C('#c9d6ff')
slo = bpy.data.objects.new('screen glow', sl); col.objects.link(slo)
slo.matrix_world = ph.matrix_world @ Matrix.Translation((0, -.02, 0)) @ Matrix.Rotation(math.radians(90), 4, 'X')
print('PHONE', ph.matrix_world.translation, 'EYE', eye)

# ------------------------------------------------------------------ city below: Manhattan grid seen from ~190 m up
if not PLATE:
    ELEV = float(os.environ.get('ELEV', '330'))
    rng = random.Random(7)
    fac = []
    for i, (wall, lit) in enumerate((('#3a3632', .28), ('#2c2e33', .22), ('#4a4038', .3), ('#23262b', .18), ('#55504a', .25))):
        m, nt, n, l, bs = nodes(f'Facade{i}')
        tc = n.new('ShaderNodeTexCoord'); sep = n.new('ShaderNodeSeparateXYZ'); l.new(tc.outputs['Object'], sep.inputs[0])
        fw, fh = (1.6, 3.6) if i % 2 else (2.2, 3.8)
        u = mth(n, l, 'ADD', sep.outputs['X'], sep.outputs['Y'])
        fu = mth(n, l, 'FRACT', mth(n, l, 'DIVIDE', u, fw)); fz = mth(n, l, 'FRACT', mth(n, l, 'DIVIDE', sep.outputs['Z'], fh))
        iu = mth(n, l, 'FLOOR', mth(n, l, 'DIVIDE', u, fw)); iz = mth(n, l, 'FLOOR', mth(n, l, 'DIVIDE', sep.outputs['Z'], fh))
        cid = n.new('ShaderNodeCombineXYZ'); l.new(iu, cid.inputs[0]); l.new(iz, cid.inputs[1]); cid.inputs[2].default_value = i * 3.1
        wn = n.new('ShaderNodeTexWhiteNoise'); l.new(cid.outputs[0], wn.inputs['Vector'])
        # whole floors / blocks dark (power out in patches)
        blk = noise_t(n, l, .012, 2, vec=tc.outputs['Object'])
        on = mr(n, l, blk.outputs['Fac'], .42, .5)
        win = mth(n, l, 'MULTIPLY', mr(n, l, fu, .12, .16), mr(n, l, fu, .88, .84))
        win = mth(n, l, 'MULTIPLY', win, mth(n, l, 'MULTIPLY', mr(n, l, fz, .25, .3), mr(n, l, fz, .9, .86)))
        sid = n.new('ShaderNodeCombineXYZ'); l.new(mth(n, l, 'FLOOR', mth(n, l, 'DIVIDE', u, 37.)), sid.inputs[0]); l.new(iz, sid.inputs[1]); sid.inputs[2].default_value = i + 50
        wf = n.new('ShaderNodeTexWhiteNoise'); l.new(sid.outputs[0], wf.inputs['Vector'])
        flo = mr(n, l, wf.outputs['Value'], .45, .46)          # whole office floors on or off
        litm = mth(n, l, 'MULTIPLY', mth(n, l, 'MULTIPLY', mr(n, l, wn.outputs['Value'], .3, .31), flo), on)
        warm = mixc(n, l, mr(n, l, mth(n, l, 'FRACT', mth(n, l, 'MULTIPLY', wn.outputs['Value'], 13.)), .55, .6), C('#ffb35c'), C('#c8d4f0'))
        l.new(mixc(n, l, win, C(wall), C('#07090c')), bs.inputs['Base Color'])
        l.new(mr(n, l, win, 0, 1, .8, .08), bs.inputs['Roughness'])
        l.new(warm, bs.inputs['Emission Color'])
        l.new(mth(n, l, 'MULTIPLY', mth(n, l, 'MULTIPLY', win, litm), mr(n, l, wf.outputs['Value'], .45, 1, .35, 1.2)), bs.inputs['Emission Strength'])
        fac.append(m)
    for i in range(2):                     # glass curtain-wall towers: dark reflective, faint floor lines
        m, nt, n, l, bs = nodes(f'Curtain{i}')
        tc = n.new('ShaderNodeTexCoord'); sep = n.new('ShaderNodeSeparateXYZ'); l.new(tc.outputs['Object'], sep.inputs[0])
        fz = mth(n, l, 'FRACT', mth(n, l, 'DIVIDE', sep.outputs['Z'], 4.1))
        line = mr(n, l, fz, .0, .08, 1, 0)
        bs.inputs['Base Color'].default_value = (*C(('#0d1318', '#151619')[i]), 1); bs.inputs['Metallic'].default_value = .7
        bs.inputs['Roughness'].default_value = .12
        iz = mth(n, l, 'FLOOR', mth(n, l, 'DIVIDE', sep.outputs['Z'], 4.1))
        cid = n.new('ShaderNodeCombineXYZ'); l.new(iz, cid.inputs[1]); l.new(mth(n, l, 'FLOOR', mth(n, l, 'DIVIDE', mth(n, l, 'ADD', sep.outputs['X'], sep.outputs['Y']), 9.)), cid.inputs[0])
        wn = n.new('ShaderNodeTexWhiteNoise'); l.new(cid.outputs[0], wn.inputs['Vector'])
        bs.inputs['Emission Color'].default_value = (*C(('#cfe0ff', '#ffd9a0')[i]), 1)
        l.new(mth(n, l, 'MULTIPLY', mth(n, l, 'MULTIPLY', mth(n, l, 'SUBTRACT', 1, line), mr(n, l, wn.outputs['Value'], .72, .73)), .7), bs.inputs['Emission Strength'])
        fac.append(m)
    NF = len(fac) - 2
    roof = mat_simple('Roofs', '#1d1c1b', .9)
    street_m = emit('StreetGlow', '#ffa050', 6.)
    bm = bmesh.new(); polys_mat = []
    def add_box(cx, cy, w, d, z0, z1, mi):
        r = bmesh.ops.create_cube(bm, size=1.)
        for v in r['verts']: v.co = V((cx + v.co.x * w, cy + v.co.y * d, z0 + (v.co.z + .5) * (z1 - z0)))
        for f in {f for v in r['verts'] for f in v.link_faces}:
            f.material_index = mi if abs(f.normal.z) < .5 else len(fac)
    fires = []; beacons = []
    BX, BY = 80., 30.                 # NYC: long blocks along x, short along y (looking north up the avenues)
    for gx in range(-14, 15):
        for gy in range(1, 60):
            cx = SX + gx * (BX + 30); cy0 = GY - 40 - gy * (BY + 18)
            dist = -cy0 + GY
            for k in range(rng.randint(4, 7)):
                w = rng.uniform(18, BX / 1.8); d = rng.uniform(16, BY)
                px = cx + rng.uniform(-BX / 2 + w / 2, BX / 2 - w / 2); py = cy0 + rng.uniform(-(BY - d) / 2, (BY - d) / 2)
                mid = 1 - min(1, abs(gx) / 9)          # midtown towers in the middle distance
                hub = math.exp(-((dist - 900) / 450) ** 2) * mid
                h = rng.uniform(18, 55) + (rng.random() ** 4) * 180 * (.4 + hub)
                if rng.random() < .015 + .03 * hub: h = rng.uniform(180, 300)
                if dist < 400: h = min(h, 60 + dist * .5)
                mi = rng.randrange(NF) if h < 110 or rng.random() < .4 else NF + rng.randrange(2); z0 = -ELEV
                add_box(px, py, w, d, z0, z0 + h, mi)
                if h > 110:                             # setbacks
                    add_box(px, py, w * .72, d * .72, z0 + h, z0 + h + h * .12, mi)
                    add_box(px, py, w * .45, d * .45, z0 + h * 1.12, z0 + h * 1.2, mi)
                    if rng.random() < .2: add_box(px, py, 1.2, 1.2, z0 + h * 1.2, z0 + h * 1.2 + 25, mi)
                    beacons.append(V((px, py, z0 + h * 1.2 + 1.5)))
                if 350 < dist < 2200 and abs(px - SX) < 900 and h > 40:
                    fires.append((V((px, py + d / 2 + 2, z0 + h * rng.uniform(.5, .95))), h, w))
    city = bpy.data.meshes.new('city'); bm.to_mesh(city); bm.free()
    co = bpy.data.objects.new('city', city); col.objects.link(co)
    for m in fac + [roof]: city.materials.append(m)
    # avenues glow (sodium + fire light on the street haze)
    for gx in range(-14, 15):
        box('avenue', (SX + gx * (BX + 30) + (BX + 30) / 2 - 15, GY - 1500, -ELEV + .2), (14, 3000, .2), street_m)
    for gy in range(1, 60):
        box('street', (SX, GY - 40 - gy * (BY + 18) + (BY + 18) / 2, -ELEV + .2), (3300, 9, .2), street_m)
    box('ground', (SX, GY - 1500, -ELEV), (4000, 3200, .2), mat_simple('Ground', '#0b0a09', .9))
    print('FIRE CANDIDATES', len(fires))
    red = emit('Beacon', '#ff2a1a', 60.)
    for b in beacons: L.setmat(L.blob('beacon', b, (.9, .9, .9), col, seg=8, ring=6), red)

# ------------------------------------------------------------------ fires + smoke
def vol_mat(name, dens, colr, emit_s, scale, tint):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; l = nt.links
    n.remove(n['Principled BSDF']); pv = n.new('ShaderNodeVolumePrincipled')
    tc = n.new('ShaderNodeTexCoord'); mpn = n.new('ShaderNodeMapping'); mpn.inputs['Location'].default_value = (-1, -1, -1); mpn.inputs['Scale'].default_value = (2, 2, 2)
    l.new(tc.outputs['Generated'], mpn.inputs['Vector'])
    gr = n.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'; l.new(mpn.outputs[0], gr.inputs[0])
    t = noise_t(n, l, scale, 8, .6, vec=mpn.outputs[0]); t.inputs['Distortion'].default_value = .8
    f = mth(n, l, 'MULTIPLY', mr(n, l, t.outputs['Fac'], .45, .75), mr(n, l, gr.outputs[0], 0, .5))
    l.new(mth(n, l, 'MULTIPLY', f, dens), pv.inputs['Density']); pv.inputs['Color'].default_value = (*C(colr), 1)
    pv.inputs['Emission Color'].default_value = (*C(tint), 1)
    l.new(mth(n, l, 'MULTIPLY', mth(n, l, 'POWER', f, 2.), emit_s), pv.inputs['Emission Strength'])
    l.new(pv.outputs[0], n['Material Output'].inputs['Volume']); return m
flame = vol_mat('Flame', 3., '#ff7a20', 120., 7., '#ff5a12')
smoke = vol_mat('Smoke', .4, '#17120f', 0., 3.2, '#000000')
if not PLATE:
    # atmosphere box: distance haze lit orange from below
    hz = L.box('haze', (SX, GY - 1500, -ELEV + 150), (4200, 2990, 300), col)
    hm = bpy.data.materials.new('Haze'); hm.use_nodes = True; hn = hm.node_tree.nodes; hn.remove(hn['Principled BSDF'])
    vs = hn.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = .0006; vs.inputs['Color'].default_value = (*C('#b8a090'), 1); vs.inputs['Anisotropy'].default_value = .4
    hm.node_tree.links.new(vs.outputs[0], hn['Material Output'].inputs['Volume']); L.setmat(hz, hm)

# ------------------------------------------------------------------ sky: low clouds lit by the fires
w = bpy.data.worlds.new('NightFire'); sc.world = w; w.use_nodes = True
n = w.node_tree.nodes; l = w.node_tree.links; bg = n['Background']
tc = n.new('ShaderNodeTexCoord'); sep = n.new('ShaderNodeSeparateXYZ'); l.new(tc.outputs['Generated'], sep.inputs[0])
cl = noise_t(n, l, 4., 12, .66, vec=tc.outputs['Generated'], dims='3D')
hor = mr(n, l, sep.outputs['Z'], .0, .22)
c = mixc(n, l, hor, C('#3a1a0e'), C('#060609'))
c = mixc(n, l, mr(n, l, cl.outputs['Fac'], .42, .68), c, mixc(n, l, hor, C('#8a3a16'), C('#1a0f0b')))
l.new(c, bg.inputs['Color']); bg.inputs['Strength'].default_value = .18 if PLATE else .5

gl_ = bpy.data.lights.new('city glow', 'AREA'); gl_.shape = 'RECTANGLE'; gl_.size = RW * 2; gl_.size_y = CH; gl_.energy = 900; gl_.color = C('#ff8a4a')
glo = bpy.data.objects.new('city glow', gl_); col.objects.link(glo); glo.location = (SX, GY - .3, CH * .4); glo.rotation_euler = (math.radians(80), 0, 0)
glo.visible_camera = False; glo.visible_glossy = False
# ------------------------------------------------------------------ camera: behind his right shoulder, handheld height
cd = bpy.data.cameras.new('cam'); cd.lens = float(os.environ.get('LENS', '30')); cd.sensor_width = 36
cam = bpy.data.objects.new('cam', cd); col.objects.link(cam)
if CAMV == 'a':     # over the shoulder: phone + city
    cam.location = headp + V((-.42, 1.2, .42)); tgt = headp + V((.25, -2.4, -.95))
elif CAMV == 'b':   # wide from the side wall: silhouette in the chair against the burning skyline
    cam.location = V((SX + 3.4, SY + 2.9, 1.25)); tgt = V((SX - .3, GY, 1.05))
else:               # front close: face lit by the screen (reflection in the glass)
    cam.location = ph.matrix_world.translation + V((-.15, -.45, .02)); tgt = headp + V((0, 0, -.08))
cam.rotation_euler = (V(tgt) - cam.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = cam
cd.dof.use_dof = True; cd.dof.aperture_fstop = float(os.environ.get('FSTOP', '5.6'))
cd.dof.focus_distance = (cam.location - (ph.matrix_world.translation if CAMV != 'b' else headp)).length

# fires: pick visible, unoccluded spots spread across the frame
if not PLATE:
    from bpy_extras.object_utils import world_to_camera_view
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    cands = []
    for (p, h, w) in fires:
        v = world_to_camera_view(sc, cam, p)
        if not (.06 < v.x < .94 and .32 < v.y < .78 and v.z > 0): continue
        dvec = (p - cam.location).normalized(); o_ = cam.location + dvec * 6
        for _ in range(6):
            hit, loc, nrm, idx, hob, mx_ = sc.ray_cast(dg, o_, dvec)
            if hit and hob.name.startswith(('haze', 'glass', 'smoke', 'fire')): o_ = loc + dvec * .05; continue
            break
        if hit and (loc - p).length < 12: cands.append((v.x, v.y, p, h, w))
    rng.shuffle(cands); chosen = []
    for c_ in cands:
        if all(abs(c_[0] - o[0]) > .14 or abs(c_[1] - o[1]) > .12 for o in chosen): chosen.append(c_)
        if len(chosen) >= int(os.environ.get('NFIRE', '6')): break
    print('FIRES', len(cands), [(round(a, 2), round(b, 2)) for a, b, *_ in chosen])
    for i, (vx, vy, p, h, w) in enumerate(chosen):
        s = rng.uniform(.8, 1.5)
        fo = L.blob('fire', p + V((0, 4, 0)), (w * .7 * s, 14 * s, 36 * s), col); L.setmat(fo, flame)
        fl = bpy.data.lights.new('fire', 'POINT'); fl.energy = 2.5e6 * s; fl.color = C('#ff7a2a'); fl.shadow_soft_size = 10
        flo = bpy.data.objects.new('fire', fl); col.objects.link(flo); flo.location = p + V((0, 25, 0))
        for k in range(2):
            sm = L.blob('smoke', p + V((20 * k * s, 6, 45 + 100 * k * s)), ((20 + 18 * k) * s, (20 + 14 * k) * s, (60 + 30 * k) * s), col, rot=(0, math.radians(-8 - 6 * k), 0)); L.setmat(sm, smoke)
else:
    # real photo plate: Midtown at night from ~370 m (Empire State Building, CC BY 3.0, panoramio via Wikimedia Commons)
    bpy.context.view_layer.update()
    yaw = cam.matrix_world.to_3x3() @ V((0, 0, -1)); yaw.z = 0; yaw.normalize()
    PP = math.radians(float(os.environ.get('PLATE_PITCH', '-10'))); D = 600.
    dirv = (yaw * math.cos(PP) + V((0, 0, math.sin(PP)))).normalized()
    pw = 2 * D * math.tan(math.radians(float(os.environ.get('PLATE_HFOV', '74')) / 2)); phh = pw * .75
    bpy.ops.mesh.primitive_plane_add(size=1); pl = bpy.context.active_object; pl.name = 'plate'
    pl.scale = (pw, phh, 1); pl.location = cam.location + dirv * D
    pl.rotation_euler = (-dirv).to_track_quat('Z', 'Y').to_euler()
    m, nt, n, l, bs = nodes('Plate'); n.remove(bs)
    im = n.new('ShaderNodeTexImage'); im.image = bpy.data.images.load(PLATE); im.extension = 'EXTEND'
    tcx = n.new('ShaderNodeTexCoord'); l.new(tcx.outputs['UV'], im.inputs[0])
    # power cut patches + fire-orange grade toward the bottom
    pn = noise_t(n, l, 2.2, 3, vec=tcx.outputs['UV']); dark = mr(n, l, pn.outputs['Fac'], .5, .6, 1., .25)
    mm = n.new('ShaderNodeMix'); mm.data_type = 'RGBA'; mm.blend_type = 'MULTIPLY'; mm.inputs[0].default_value = 1.
    l.new(im.outputs['Color'], mm.inputs[6]); mm.inputs[7].default_value = (*C('#ffc896'), 1); col_ = mm.outputs[2]
    col_ = mixc(n, l, mth(n, l, 'SUBTRACT', 1, dark), col_, C('#000000'))
    # burning blocks painted into the plate: ragged flame tongues (stretched noise) inside soft elliptical zones + wide glow
    FIRES_UV = [(.52, .62, 480, 1.0), (.70, .80, 400, 1.1), (.427, .525, 560, .7), (.657, .66, 450, .6), (.32, .60, 520, .8), (.607, .38, 900, .5)][:int(os.environ.get('NFIRE', '7'))]
    sepu = n.new('ShaderNodeSeparateXYZ'); l.new(tcx.outputs['UV'], sepu.inputs[0]); U, Vv = sepu.outputs[0], sepu.outputs[1]
    mpf = n.new('ShaderNodeMapping'); mpf.inputs['Scale'].default_value = (70, 18, 1); l.new(tcx.outputs['UV'], mpf.inputs['Vector'])
    fn = noise_t(n, l, 1., 10, .62, vec=mpf.outputs[0]); fn.inputs['Distortion'].default_value = 1.2
    fn2 = noise_t(n, l, 260., 4, .5, vec=tcx.outputs['UV'])
    tot_f = 0.; tot_g = 0.
    for (u0, v0, dep, sz) in FIRES_UV:
        sx, sy = .03 * sz + .012, .024 * sz; vv = 1 - v0
        du = mth(n, l, 'DIVIDE', mth(n, l, 'SUBTRACT', U, u0), sx)
        dv = mth(n, l, 'DIVIDE', mth(n, l, 'SUBTRACT', Vv, vv), sy)
        up = mth(n, l, 'MAXIMUM', dv, 0.)                                  # tongues reach higher above the base
        dd = mth(n, l, 'ADD', mth(n, l, 'POWER', du, 2.), mth(n, l, 'ADD', mth(n, l, 'POWER', mth(n, l, 'MINIMUM', dv, 0.), 2.) , mth(n, l, 'MULTIPLY', mth(n, l, 'POWER', up, 2.), .35)))
        e = mr(n, l, dd, 1.6, 0.)                                         # 0 outside, 1 at core
        fl = mth(n, l, 'SUBTRACT', mth(n, l, 'MULTIPLY', e, 1.7), mth(n, l, 'MULTIPLY', mth(n, l, 'SUBTRACT', 1, fn.outputs['Fac']), 1.9), use_clamp=True) if False else None
        fl = mr(n, l, mth(n, l, 'SUBTRACT', mth(n, l, 'MULTIPLY', e, 1.5), mth(n, l, 'MULTIPLY', mth(n, l, 'SUBTRACT', 1, fn.outputs['Fac']), 1.6 + (1 - sz) * 1.5)), 0., .5)
        gl = mth(n, l, 'POWER', mr(n, l, dd, 9., 0.), 2.)
        tot_f = fl if tot_f == 0. else mth(n, l, 'MAXIMUM', tot_f, fl)
        tot_g = gl if tot_g == 0. else mth(n, l, 'ADD', tot_g, gl)
    if FIRES_UV:
        fcol = n.new('ShaderNodeValToRGB'); cr = fcol.color_ramp
        cr.elements[0].position = 0.; cr.elements[0].color = (*C('#5a0e02'), 1); cr.elements[1].position = 1.; cr.elements[1].color = (*C('#ffd27a'), 1)
        e2 = cr.elements.new(.45); e2.color = (*C('#ff5a10'), 1)
        l.new(mth(n, l, 'MULTIPLY', tot_f, mr(n, l, fn2.outputs['Fac'], .3, .7, .75, 1.)), fcol.inputs[0])
        fire_e = mixc(n, l, tot_f, C('#000000'), fcol.outputs[0])
        fire_e = mixc(n, l, mth(n, l, 'MINIMUM', mth(n, l, 'MULTIPLY', tot_g, .5), 1.), C('#000000'), C('#ff6a22')) if False else fire_e
        glowc = mixc(n, l, mth(n, l, 'MINIMUM', mth(n, l, 'MULTIPLY', tot_g, .35), .6), C('#000000'), C('#ff6a22'))
        add1 = n.new('ShaderNodeMix'); add1.data_type = 'RGBA'; add1.blend_type = 'ADD'; add1.inputs[0].default_value = 1.
        l.new(col_, add1.inputs[6]); l.new(mixc(n, l, 1., C('#000000'), fire_e), add1.inputs[7])
        sc_f = n.new('ShaderNodeVectorMath'); sc_f.operation = 'SCALE'; l.new(fire_e, sc_f.inputs[0]); sc_f.inputs[3].default_value = float(os.environ.get('FIRE_E', '5'))
        l.new(sc_f.outputs[0], add1.inputs[7])
        add2 = n.new('ShaderNodeMix'); add2.data_type = 'RGBA'; add2.blend_type = 'ADD'; add2.inputs[0].default_value = 1.
        l.new(add1.outputs[2], add2.inputs[6]); l.new(glowc, add2.inputs[7]); col_ = add2.outputs[2]
    es = n.new('ShaderNodeEmission'); l.new(col_, es.inputs[0]); es.inputs[1].default_value = float(os.environ.get('PLATE_E', '.8'))
    l.new(es.outputs[0], n['Material Output'].inputs['Surface']); pl.data.materials.append(m)
    for vis in ('visible_diffuse', 'visible_shadow', 'visible_volume_scatter'): setattr(pl, vis, False)
    for c_ in list(pl.users_collection): c_.objects.unlink(pl)
    col.objects.link(pl); cd.clip_end = 5000
    bpy.context.view_layer.update(); print('PLATE', pl.location, pl.dimensions, cam.location)
    def plate_pt(u, v, depth):          # u,v in plate pixels (0..1, v from top) -> world point at `depth` along that ray
        q = pl.matrix_world @ V((u - .5, .5 - v, 0)); return cam.location + (q - cam.location).normalized() * depth
    for (u, v, dep, s) in FIRES_UV:
        p = plate_pt(u, v, dep)
        fl = bpy.data.lights.new('fire', 'POINT'); fl.energy = 3e6 * s; fl.color = C('#ff6a1a'); fl.shadow_soft_size = 12
        flo = bpy.data.objects.new('fire', fl); col.objects.link(flo); flo.location = p + V((0, 0, 10))
        for k in range(3):
            sm = L.blob('smoke', p + V((18 * k * s, 30, 70 + 85 * k * s)), ((22 + 22 * k) * s, (22 + 16 * k) * s, (55 + 30 * k) * s), col, rot=(0, math.radians(-10 - 8 * k), 0)); L.setmat(sm, smoke)
# ------------------------------------------------------------------ animation: asleep -> phone buzzes/lights -> head lifts, looks at it
ANIM = int(os.environ.get('ANIM', '0'))
if ANIM:
    FPS = 24; NF = int(os.environ.get('NFRAMES', '108')); sc.render.fps = FPS; sc.frame_start = 1; sc.frame_end = NF
    # phone rides the right hand
    wmx = rig.matrix_world @ rig.pose.bones['wrist.R'].matrix
    for o_ in (ph, slo):
        mw = o_.matrix_world.copy(); o_.parent = rig; o_.parent_type = 'BONE'; o_.parent_bone = 'wrist.R'
        bpy.context.view_layer.update(); o_.matrix_world = mw
    BUZZ, LIFT0, LIFT1 = 30, 44, 78
    def ease(t): t = max(0., min(1., t)); return t * t * (3 - 2 * t)
    def wake_at(f):
        w = .55 * ease((f - LIFT0) / 16.) + .45 * ease((f - LIFT0 - 10) / (LIFT1 - LIFT0 - 10))
        if BUZZ <= f < LIFT0: w += .05 * math.sin((f - BUZZ) / 3.)  # small startle twitch on the buzz
        w += .012 * math.sin(f / 19.)                               # breathing
        return max(0., w)
    KF = sorted(set(list(range(1, NF + 1, 3)) + [BUZZ, BUZZ + 2, LIFT0, LIFT1, NF]))
    for f in KF:
        pose(wake_at(f))
        for pb_ in rig.pose.bones:
            if pb_.rotation_mode == 'QUATERNION': pb_.keyframe_insert('rotation_quaternion', frame=f)
            else: pb_.keyframe_insert('rotation_euler', frame=f)
    # screen off while he sleeps, wakes on the buzz
    scrm = scr.data.materials[0]; es_ = scrm.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    for f, v in ((1, 0.), (BUZZ - 1, 0.), (BUZZ + 1, 2.2), (NF, 2.2)):
        es_.default_value = v; es_.keyframe_insert('default_value', frame=f)
        sl.energy = v * .65; sl.keyframe_insert('energy', frame=f)
    # handheld camera drift + firelight flicker (explicit keys from smooth noise)
    r0 = cam.rotation_euler.copy(); l0 = cam.location.copy()
    fls = [o_ for o_ in col.objects if o_.type == 'LIGHT' and o_.name.startswith('fire')]; e0 = [o_.data.energy for o_ in fls]
    for f in range(1, NF + 1, 2):
        t = f / FPS
        rn = noise.noise_vector(V((t * .35, 3.1, 0))); ln = noise.noise_vector(V((t * .3, 7.7, 0)))
        cam.rotation_euler = (r0.x + rn.x * .006, r0.y + rn.y * .004, r0.z + rn.z * .006); cam.keyframe_insert('rotation_euler', frame=f)
        cam.location = l0 + ln * .008; cam.keyframe_insert('location', frame=f)
        for k_, o_ in enumerate(fls):
            o_.data.energy = e0[k_] * (.75 + .5 * (noise.noise(V((t * 2.5, k_ * 5.3, 0))) * .5 + .5)); o_.data.keyframe_insert('energy', frame=f)
    sc.render.filepath = OUT; sc.frame_set(int(os.environ.get('FRAME', '1')))
# ------------------------------------------------------------------ render
r = int(os.environ.get('RES', '540'))
sc.render.resolution_x = r; sc.render.resolution_y = int(r * 16 / 9); sc.render.resolution_percentage = 100
sc.render.engine = 'CYCLES'; sc.cycles.samples = int(os.environ.get('SPP', '48'))
sc.cycles.use_adaptive_sampling = True; sc.cycles.use_denoising = True
sc.cycles.max_bounces = 6; sc.cycles.volume_bounces = 0; sc.cycles.transparent_max_bounces = 12
sc.cycles.volume_step_rate = 4.; sc.cycles.volume_max_steps = 256
sc.cycles.device = os.environ.get('DEVICE', 'CPU')
if sc.cycles.device == 'GPU':
    pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
    for d in pr.devices: d.use = d.type == 'OPTIX'
    sc.cycles.denoiser = 'OPTIX'
sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
sc.view_settings.exposure = float(os.environ.get('EXPO', '1'))
sc.render.film_transparent = False
sc.render.filepath = OUT
if os.environ.get('SAVE'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['SAVE'])
bpy.ops.render.render(animation=bool(int(os.environ.get('RENDER_ANIM', '0'))), write_still=not int(os.environ.get('RENDER_ANIM', '0')))
