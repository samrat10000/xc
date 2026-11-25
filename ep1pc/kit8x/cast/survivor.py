"""SURVIVORS: Sam and the three friends. Realistic humans on the MakeHuman CC0 base with layered
clothing cut from the body, hair cards, boots and a weapon; ink hull to match the cast.
usage: CHAR=sam|f1|f2|f3 python3 survivor.py"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, noise
import castlib as L, mh, mats as M
from zbuild import Char, shoe, V
CH = os.environ.get('CHAR', 'sam')
LOOK = {
 'sam': dict(mix={'universal-male-young-averagemuscle-averageweight': 1.0}, skin='#b98a6a', hair='#1c1410', hstyle='short',
             jacket=('leather', '#1d1916'), tee='#56565c', pants=('denim', '#24304a'), boots='#3a2618', iris='#4a3020', weapon='crowbar'),
 'f1': dict(mix={'universal-female-young-averagemuscle-averageweight': 1.0}, skin='#e0b896', hair='#5a2a18', hstyle='long',
             jacket=('canvas', '#4a5034'), tee='#d8d4c8', pants=('denim', '#3a4c70'), boots='#2a2420', iris='#3a5a3a', weapon='bat'),
 'f2': dict(mix={'universal-male-young-maxmuscle-averageweight': 1.0}, skin='#6a4632', hair='#141010', hstyle='buzz',
             jacket=('canvas', '#7a1e1e'), tee='#222226', pants=('canvas', '#4a4a3c'), boots='#2a2018', iris='#2a1a10', weapon='axe'),
 'f3': dict(mix={'universal-female-young-minmuscle-minweight': 1.0}, skin='#c89a74', hair='#0e0c0c', hstyle='bob',
             jacket=('denim', '#3a4a6a'), tee='#141416', pants=('canvas', '#1c1c20'), boots='#141210', iris='#2a1a10', weapon='pipe'),
}[CH]
OUT = os.environ.get('OUT', os.path.join(os.path.dirname(os.path.abspath(__file__)), f'out/{CH}'))
os.makedirs(OUT, exist_ok=True)
M.STYLE['cavity'] = True; M.STYLE['cav_kw'] = {'dist': .03, 'strength': .35}
sc = L.reset(); C = L.collection(CH.upper())
rng = random.Random(7)
LR = ('.L', '.R')
def both(*names): return [n + s for n in names for s in LR]
z = Char(CH.upper(), LOOK['mix'], C)
b = z.body
z.subdiv(b, 1)
EL, ER = z.j('eye.L____head'), z.j('eye.R____head')

def human_skin(name, tone):
    nb = M.NB(name)
    n1 = nb.noise(5, 6, .55); n2 = nb.noise(40, 6, .6)
    base = M.C(tone)
    c = nb.mix(nb.mr(n1, .4, .65, 0, .25), base, M.C('#7a3a32'))                   # blotchy redness
    c = nb.mix(nb.math('MULTIPLY', nb.mr(n2, .5, .7), .15), c, M.C('#3a2018'))        # freckles / pores
    c = nb.mix(nb.math('MULTIPLY', nb.mr(nb.noise(3, 4, .5, vec=nb.mapping(loc=(4, 4, 4))), .55, .7), .35), c, M.C('#3a2e26'))   # grime of the road
    nb.bump(nb.voronoi(400), .12, .0003); nb.bump(n2, .15, .0006)
    m = nb.finish(c, sss=.22, spec=.4, rough_sock=nb.mr(n1, 0, 1, .5, .66))
    return m
def cloth(kind, col, name):
    if kind == 'leather': return M.leather(name, col)
    if kind == 'denim': return M.denim(name, base=col)
    return M.canvas(name, col)

# ---------------------------------------------------------------- clothing
UPPER = ['spine01', 'spine02', 'spine03', 'spine04', 'spine05', 'neck01'] + both('clavicle', 'shoulder01', 'breast', 'upperarm01', 'upperarm02')
ARMS = UPPER + both('lowerarm01', 'lowerarm02')
def tee_keep(p): return .9 < p.z < EL.z - .17 and not (abs(p.x) < .045 and p.y < -.02 and p.z > EL.z - .21)
tee = z.garment('tee', UPPER, keep=tee_keep, push=.004, fold=lambda p: .002 * math.sin(p.z * 80 + 6 * noise.noise(p * 6)), thick=.002)
def jk_keep(p): return .86 < p.z < EL.z - .15 and not (abs(p.x) < .06 + .1 * L.sm(1.0, 1.3, p.z) * 0 and p.y < -.03 and p.z < EL.z - .18 and abs(p.x) < .055)
def jk_fold(p): return .004 * math.sin(p.z * 45 + 8 * noise.noise(p * 5)) + .002 * noise.noise(p * 25) + .006 * L.sm(1.0, .88, p.z)
jacket = z.garment('jacket', ARMS, keep=jk_keep, push=.014, fold=jk_fold, thick=.004)
L.delete_faces(jacket, lambda p, n: abs(p.x) > .55 + .0)            # cuffs end at the wrist
z.subdiv(jacket, 1); z.subdiv(tee, 1)
# collar: a raised band around the neck
nk = z.j('neck01____head')
col_pts = [V(math.cos(a) * .075, nk.y + .01 + math.sin(a) * .065, EL.z - .2 + .015 * abs(math.cos(a))) for a in [i / 24 * 2 * math.pi for i in range(25)]]
collar = L.tube(f'{CH} collar', col_pts, .009, C, sides=8); z.bind(collar, 'neck01')
LEGS = both('pelvis', 'upperleg01', 'upperleg02', 'lowerleg01', 'lowerleg02') + ['spine05', 'spine04']
def pants_keep(p): return .1 < p.z < 1.0
pants = z.garment('pants', LEGS, keep=pants_keep, push=.008, fold=lambda p: .003 * math.sin(p.z * 70 + 6 * noise.noise(p * 8)) + .002 * noise.noise(p * 40) + .006 * L.sm(.25, .1, p.z), thick=.003)
belt = z.garment('belt', LEGS, keep=lambda p: .955 < p.z < .99, push=.016, thick=.006)
shoes = []
for side in ('L', 'R'):
    a = z.j(f'foot.{side}____head'); t = z.j(f'toe3-1.{side}____head')
    a = V(a.x, a.y + .01, .093 * .9)
    up, so, lc = shoe(f'{CH} {side}', C, a, t, scale=.92)
    for o in (up, so, lc): z.bind(o, f'foot.{side}')
    shoes.append((up, so, lc))
L.delete_faces(b, lambda p, n: p.z < .12)
def hair_cards(src, name, select, length, width, flow, count_skip=.0, seed=4, segs=4, droop=.5):
    rng = random.Random(seed); hb = bmesh.new()
    for v in src.data.vertices:
        p = v.co.copy()
        if not select(p) or rng.random() < count_skip: continue
        n = v.normal.copy()
        ln = length(p, rng)
        if ln <= 0: continue
        d = (flow(p) + V(rng.uniform(-.25, .25), rng.uniform(-.25, .25), rng.uniform(-.1, .1))).normalized()
        d = (d - n * d.dot(n) * .7).normalized()
        q = p - n * .001; side = n.cross(d).normalized()
        prev = None; wid = width * rng.uniform(.6, 1.3)
        for k in range(segs + 1):
            t = k / segs
            w = wid * (1 - t) ** .8 + .0004
            lift = n * (.003 + .004 * t) * (1 - t * droop)
            pts = (hb.verts.new(q + lift + side * w), hb.verts.new(q + lift - side * w))
            if prev: hb.faces.new((prev[0], prev[1], pts[1], pts[0]))
            prev = pts
            d = (d + V(0, 0, -.18) + V(rng.uniform(-.1, .1), rng.uniform(-.1, .1), 0)).normalized()
            q = q + d * ln / segs
    return L.mesh_obj(name, hb, C)
HC = z.j('head____head')
hs = LOOK['hstyle']
def scalp(p):
    if p.z < EL.z + .015 or (p.y < -.07 and p.z < EL.z + .1): return False
    if hs in ('short', 'buzz') and p.z < EL.z + .03 and p.y > .0 and p.z < EL.z - .0: return False
    return (p - (HC + V(0, .01, .08))).length < .2
L_ = {'short': (.035, .06), 'buzz': (.008, .014), 'long': (.25, .42), 'bob': (.12, .17)}[hs]
def hlen(p, r): return r.uniform(*L_)
def hflow(p):
    if hs in ('long', 'bob'): return V(p.x * 3, .4, -1.2).normalized()
    return V(p.x * 1.5, .9, .2).normalized()
hair = hair_cards(b, f'{CH} hair', scalp, hlen, .006 if hs != 'buzz' else .002, hflow, segs=8 if hs in ('long', 'bob') else 4, droop=.0 if hs in ('long', 'bob') else .5)
z.bind(hair, 'head')
def capsel(p):
    if (p - (HC + V(0, .01, .06))).length > .19: return False
    front = p.y < -.04
    if front and p.z < EL.z + .055 + .01 * noise.noise(p * 60): return False
    if not front and p.z < EL.z - (.0 if hs in ('short', 'buzz') else .06): return False
    if abs(p.x) > .07 and p.z < EL.z + .03 and p.y < .03: return False        # keep the ears and temples clear
    return True
cap = b.copy(); cap.data = b.data.copy(); cap.name = f'{CH} haircap'; C.objects.link(cap)
L.delete_faces(cap, lambda p, n: not capsel(p)); z.subdiv(cap, 1)
bmc = bmesh.new(); bmc.from_mesh(cap.data); bmc.normal_update()
thick = {'buzz': .002, 'short': .009, 'bob': .014, 'long': .012}[hs]
for v in bmc.verts: v.co += v.normal * (thick + .003 * noise.noise(v.co * 90))
bmc.to_mesh(cap.data); bmc.free()
so = cap.modifiers.new('s', 'SOLIDIFY'); so.thickness = .003; so.offset = -1; z.apply_first(cap, so)
for vg in list(cap.vertex_groups): pass
brows = []
for e in (EL, ER):
    sx = 1 if e.x > 0 else -1; pts = []
    for k in range(6):
        t = k / 5
        q = V(e.x + sx * (-.016 + .036 * t), e.y - .3, e.z + .017 + .006 * math.sin(t * math.pi) - .004 * t)
        hit, _ = z.hit(b, q, (0, 1, 0))
        if hit is not None: pts.append(hit + V(0, -.0015, 0))
    if len(pts) > 2: brows.append(L.tube(f'{CH} brow{sx}', pts, [.0022, .003, .0032, .003, .0024, .0012][:len(pts)], C, sides=6))
brows = L.join(brows, f'{CH} brows'); z.bind(brows, 'head')
# weapon in the right hand
wr = z.j('wrist.R____head'); hd = z.j('finger3-1.R____head'); dirv = (hd - wr).normalized()
grip = wr + dirv * .06
wp = LOOK['weapon']
if wp == 'crowbar':
    weapon = L.tube(f'{CH} weapon', [grip + V(0, 0, .12), grip, grip - V(0, 0, .55), grip - V(0, .03, .6), grip - V(0, .06, .58)], .011, C, sides=8)
    wmat = M.metal(f'{CH}_Steel', col='#5a1a16', rust='#2a1210')
elif wp == 'bat':
    weapon = L.tube(f'{CH} weapon', [grip + V(0, 0, .1), grip, grip - V(0, 0, .3), grip - V(0, 0, .65)], [.016, .017, .028, .034], C, sides=14)
    wmat = M.leather(f'{CH}_Wood', '#7a5a3a')
elif wp == 'axe':
    shaft = L.tube(f'{CH} shaft', [grip + V(0, 0, .1), grip - V(0, 0, .55)], .014, C, sides=10)
    head_ = L.box(f'{CH} axehead', grip - V(0, .05, .52), (.012, .07, .05), C, bevel=.004)
    weapon = L.join([shaft, head_], f'{CH} weapon'); wmat = M.metal(f'{CH}_Steel')
else:
    weapon = L.tube(f'{CH} weapon', [grip + V(0, 0, .12), grip - V(0, 0, .6)], .015, C, sides=10)
    wmat = M.metal(f'{CH}_Pipe', col='#6a6a66')
z.bind(weapon, 'wrist.R')

# ---------------------------------------------------------------- materials
MALE = 'female' not in list(LOOK['mix'])[0]
MO = z.hit(b, (0, -.5, EL.z - .092), (0, 1, 0))[0] or V(0, -.1, EL.z - .092)
def g3(p, c, r): return math.exp(-((p - c).length_squared) / (r * r))
cam = b.data.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
for v in b.data.vertices:
    p = v.co
    stub = 0.
    if MALE and p.y < .02 and EL.z - .16 < p.z < EL.z - .035 and (p - HC).length < .16:
        stub = L.sm(EL.z - .035, EL.z - .06, p.z) * (1 - g3(V(p.x, 0, p.z), V(0, 0, MO.z), .012)) * min(1, .4 + abs(p.x) * 8 + L.sm(EL.z - .1, EL.z - .13, p.z))
    sock = sum(g3(p, e + V(0, .005, -.006), .02) for e in (EL, ER))
    red = sum(g3(p, V(e.x * 1.4, e.y - .02, e.z - .04), .025) for e in (EL, ER)) + g3(p, V(0, MO.y - .02, EL.z - .04), .015)
    cam.data[v.index].color = (min(1, stub), min(1, sock), min(1, red), 1)
sk_ = human_skin(f'{CH}_Skin', LOOK['skin']); nt = sk_.node_tree; bs = nt.nodes['Principled BSDF']
src_ = bs.inputs['Base Color'].links[0].from_socket
vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Mask'; sp = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(vc.outputs['Color'], sp.inputs[0])
nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 900; nz.inputs['Detail'].default_value = 2
mth = nt.nodes.new('ShaderNodeMath'); mth.operation = 'MULTIPLY'; nt.links.new(sp.outputs['Red'], mth.inputs[0]); nt.links.new(nz.outputs['Fac'], mth.inputs[1])
out = src_
for fac, col, k in ((mth.outputs[0], '#2a1e18', .9), (sp.outputs['Green'], '#5a3a34', .45), (sp.outputs['Blue'], '#b0564a', .35)):
    mm = nt.nodes.new('ShaderNodeMath'); mm.operation = 'MULTIPLY'; nt.links.new(fac, mm.inputs[0]); mm.inputs[1].default_value = k
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; nt.links.new(mm.outputs[0], mx.inputs[0]); nt.links.new(out, mx.inputs[6]); mx.inputs[7].default_value = (*L.lin(col), 1)
    out = mx.outputs[2]
nt.links.new(out, bs.inputs['Base Color'])
L.setmat(b, sk_)
L.setmat(tee, M.canvas(f'{CH}_Tee', LOOK['tee']))
L.setmat(jacket, cloth(*LOOK['jacket'], f'{CH}_Jacket')); L.setmat(collar, jacket.data.materials[0])
L.setmat(pants, cloth(*LOOK['pants'], f'{CH}_Pants'))
L.setmat(belt, M.leather(f'{CH}_Belt'))
for up, so, lc in shoes:
    L.setmat(up, M.leather(f'{CH}_Boot', LOOK['boots'])); L.setmat(so, M.rubber(f'{CH}_Sole', col='#2a2622')); L.setmat(lc, M.flat(f'{CH}_Lace', '#3a3430', .8))
hm_ = M.NB(f'{CH}_Hair'); hn = hm_.noise(220, 4, .6, vec=hm_.mapping(scale=(1, 1, 12)))
hcol = hm_.mix(hm_.mr(hn, .35, .7), M.C(LOOK['hair']), M.C('#000000')); hcol = hm_.mix(hm_.math('MULTIPLY', hm_.mr(hn, .6, .75), .35), hcol, M.C('#8a7a6a'))
hm_.bump(hn, .5, .001); hmat = hm_.finish(hcol, rough=.42, spec=.5, cav=False)
L.setmat(hair, hmat); L.setmat(cap, hmat); L.setmat(brows, hmat)
L.setmat(weapon, wmat)
for k in ('eyeL', 'eyeR'):
    o = z.parts[k]; z.subdiv(o, 2)
    c0 = sum((v.co for v in o.data.vertices), Vector()) / len(o.data.vertices)
    ca = o.data.color_attributes.new('Iris', 'FLOAT_COLOR', 'POINT')
    ir = L.lin(LOOK['iris'])
    for v in o.data.vertices:
        d = (v.co - c0).normalized().y
        col = (.02, .02, .02) if d < -.975 else (ir if d < -.9 else ((.06, .05, .04) if d < -.885 else (.78, .74, .7)))
        ca.data[v.index].color = (*col, 1)
    em = bpy.data.materials.new(f'{CH}_Eye{k}'); em.use_nodes = True; nt = em.node_tree; bs = nt.nodes['Principled BSDF']
    vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Iris'; nt.links.new(vc.outputs['Color'], bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = .05; bs.inputs['Coat Weight'].default_value = 1.; bs.inputs['Coat Roughness'].default_value = .02
    L.setmat(o, em)
tm = M.teeth_m(f'{CH}_Teeth')
for k in ('teethU', 'teethL'): L.setmat(z.parts[k], tm)
L.setmat(z.parts['tongue'], M.flat(f'{CH}_Tongue', '#8a3a3a', .4))

# ---------------------------------------------------------------- pose: ready stance, weapon low in the right hand
POSE = {
    'spine05': (0, 0, -4), 'spine03': (3, 0, -3), 'spine01': (2, 0, 0), 'neck01': (2, 0, 0), 'head': (-4, 0, 10),
    'clavicle.L': (0, 0, -4), 'upperarm01.L': (10, 0, -48), 'lowerarm01.L': (0, 0, 30), 'wrist.L': (0, 0, 0),
    'clavicle.R': (0, 0, 4), 'upperarm01.R': (8, 0, 48), 'lowerarm01.R': (0, 0, -18), 'wrist.R': (0, -20, 0),
    'upperleg01.L': (6, 0, -8), 'lowerleg01.L': (-8, 0, 0), 'foot.L': (2, 0, 0),
    'upperleg01.R': (-4, 0, 6), 'lowerleg01.R': (-4, 0, 0),
}
for side, curl in (('L', 20), ('R', 70)):
    for f in range(2, 6):
        for k in (1, 2, 3):
            POSE[f'finger{f}-{k}.{side}'] = (curl, 0, 0)
    POSE[f'finger1-2.{side}'] = (curl * .6, 0, 0)
z.pose_and_bake(POSE)
mz = min((o.matrix_world @ v.co).z for o in z.all_meshes() for v in list(o.data.vertices)[::5])
for o in z.all_meshes(): o.location.z -= mz; L.apply_transform(o)

for o in [b, tee, jacket, pants, belt, collar, weapon, cap] + [s for sh in shoes for s in sh[:2]]:
    L.hull(o, C, t=.0032)

L.studio(sc); sc.view_settings.exposure = -.2
for n in sc.world.node_tree.nodes:
    if n.type == 'BACKGROUND' and n.inputs['Color'].default_value[0] > .5: n.inputs['Color'].default_value = (*L.lin('#30303a'), 1)
eyes_c = sum((o.matrix_world @ v.co for o in (z.parts['eyeL'], z.parts['eyeR']) for v in o.data.vertices), Vector()) / (len(z.parts['eyeL'].data.vertices) * 2)
shots = [('front34', 28, 6, 3.4, .92, 50), ('side', 90, 4, 3.4, .92, 50), ('back34', 205, 10, 3.4, .92, 50), ('face', 20, 2, .6, None, 70)]
SAMP = int(os.environ.get('SAMP', '40')); RES = float(os.environ.get('RES', '1')); only = os.environ.get('ONLY')
for nm, az, el, dist, tz, lens in shots:
    if only and nm not in only.split(','): continue
    tgt = eyes_c + V(0, .02, -.03) if nm == 'face' else V(0, -.1, tz)
    L.camera(sc, tgt, dist, az, el, lens=lens)
    L.render(sc, f'{OUT}/{nm}.png', w=int(1080 * RES), h=int(1350 * RES), samples=SAMP)
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/{CH}.blend')
