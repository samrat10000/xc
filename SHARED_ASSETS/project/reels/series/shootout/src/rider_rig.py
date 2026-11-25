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
 'rider': dict(mix={'universal-female-young-averagemuscle-averageweight': .45, 'universal-female-young-averagemuscle-minweight': .55, 'female-young-averagemuscle-averageweight-idealproportions': .8, 'mouth-upperlip-volume-incr': .6, 'mouth-lowerlip-volume-incr': .7, 'nose-scale-horiz-decr': .35, 'nose-width1-decr': .3, 'chin-width-decr': .4, 'l-cheek-bones-incr': .5, 'r-cheek-bones-incr': .5, 'head-fat-decr': .35, 'neck-scale-horiz-decr': .3, 'torso-vshape-decr': .25, 'l-eye-scale-incr': .45, 'r-eye-scale-incr': .45, 'l-eye-bag-decr': .6, 'r-eye-bag-decr': .6, 'l-eye-corner1-up': .35, 'r-eye-corner1-up': .35, 'l-eye-height1-incr': .3, 'r-eye-height1-incr': .3, 'nose-point-width-decr': .4}, skin='#d4a084', hair='#ebe6dc', hstyle='bob',
             jacket=('leather', '#7e5232'), tee='#1c1a1a', pants=('leather', '#121214'), boots='#8a5a30', iris='#4a3424', weapon='pistol'),
}[CH]
RIDER = CH == 'rider'
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
def jk_keep(p): return (1.02 if RIDER else .86) < p.z < EL.z - .15 and not (abs(p.x) < .06 + .1 * L.sm(1.0, 1.3, p.z) * 0 and p.y < -.03 and p.z < EL.z - .18 and abs(p.x) < .055)
def jk_fold(p): return .004 * math.sin(p.z * 45 + 8 * noise.noise(p * 5)) + .002 * noise.noise(p * 25) + .006 * L.sm(1.0, .88, p.z)
jacket = z.garment('jacket', ARMS, keep=jk_keep, push=.022 if RIDER else .014, fold=(lambda p: 1.5 * jk_fold(p)) if RIDER else jk_fold, thick=.004)
L.delete_faces(jacket, lambda p, n: abs(p.x) > .55 + .0)            # cuffs end at the wrist
z.subdiv(jacket, 1); z.subdiv(tee, 1)
# collar: a raised band around the neck
nk = z.j('neck01____head')
col_pts = [V(math.cos(a) * .075, nk.y + .01 + math.sin(a) * .065, EL.z - .2 + .015 * abs(math.cos(a))) for a in [i / 24 * 2 * math.pi for i in range(25)]]
collar = L.tube(f'{CH} collar', col_pts, .02 if RIDER else .009, C, sides=8); z.bind(collar, 'neck01')
LEGS = both('pelvis', 'upperleg01', 'upperleg02', 'lowerleg01', 'lowerleg02') + ['spine05', 'spine04']
def pants_keep(p): return (.70 if RIDER else .1) < p.z < 1.0
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
def hair_cards(src, name, select, length, width, flow, count_skip=.0, seed=4, segs=4, droop=.5, base=0.):
    rng = random.Random(seed); hb = bmesh.new()
    for v in src.data.vertices:
        p = v.co.copy()
        if not select(p) or rng.random() < count_skip: continue
        n = v.normal.copy()
        ln = length(p, rng)
        if ln <= 0: continue
        d = (flow(p) + V(rng.uniform(-.25, .25), rng.uniform(-.25, .25), rng.uniform(-.1, .1))).normalized()
        d = (d - n * d.dot(n) * .7).normalized()
        q = p + n * (base - .001); side = n.cross(d).normalized()
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
L_ = {'short': (.035, .06), 'buzz': (.008, .014), 'long': (.25, .42), 'bob': (.07, .19) if RIDER else (.12, .17)}[hs]
def hlen(p, r): return r.uniform(*L_)
def hflow(p):
    if hs in ('long', 'bob'): return V(p.x * 3, .4, -1.2).normalized()
    return V(p.x * 1.5, .9, .2).normalized()
hair = hair_cards(b, f'{CH} hair', scalp, hlen, .006 if hs != 'buzz' else .002, hflow, segs=8 if hs in ('long', 'bob') else 4, droop=.0 if hs in ('long', 'bob') else .5)
z.bind(hair, 'head')
if RIDER:   # choppy fringe falling over the forehead + extra volume on the sides
    def fr(p): return p.y < -.02 and p.z > EL.z + .07 and (p - (HC + V(0, .01, .08))).length < .2
    fringe = hair_cards(b, f'{CH} fringe', fr, lambda p, r: r.uniform(.035, .07), .007, lambda p: V(p.x * 2.5, -.8, -1).normalized(), count_skip=.35, segs=6, droop=0., seed=9, base=.026)
    side = hair_cards(b, f'{CH} hair2', scalp, lambda p, r: r.uniform(.09, .17), .007, lambda p: V(p.x * 4, .3, -1).normalized(), segs=8, droop=0., seed=11, base=.02)
    hair = L.join([hair, fringe, side], f'{CH} hair'); hair.modifiers.clear(); hair.parent = None; z.bind(hair, 'head')
    # two fresh scratches on the right cheek
    sc_ = []
    for k in range(2):
        q0 = V(-.035 - k * .008, -.5, EL.z - .045 - k * .01); h0, _ = z.hit(b, q0, (0, 1, 0)); h1, _ = z.hit(b, q0 + V(-.02, 0, -.012), (0, 1, 0))
        if h0 is not None and h1 is not None: sc_.append(L.tube(f'{CH} scratch', [h0 + V(0, -.0008, 0), h1 + V(0, -.0008, 0)], .0011, C, sides=4))
    if sc_: scratch = L.join(sc_, f'{CH} scratches'); z.bind(scratch, 'head'); L.setmat(scratch, M.flat(f'{CH}_Cut', '#6a1a16', .5))
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
thick = {'buzz': .002, 'short': .009, 'bob': .026 if RIDER else .014, 'long': .012}[hs]
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
if RIDER:
    lash = []
    for e in (EL, ER):
        sx = 1 if e.x > 0 else -1
        for k in range(16):
            t = k / 15
            q = V(e.x + sx * (-.013 + .027 * t), -.5, e.z + .0035 + .0045 * math.sin(t * math.pi))
            h, n = z.hit(b, q, (0, 1, 0))
            if h is None: continue
            ln = .006 + .004 * t
            lash.append(L.tube(f'{CH} lash', [h + V(0, -.0005, 0), h + V(sx * .001 * t, -.004, .0008), h + V(sx * .002 * t, -.0065, .0025)], [.0003, .0002, .00008], C, sides=3, cap=False))
    lashes = L.join(lash, f'{CH} lashes'); z.bind(lashes, 'head')

extra = []
if RIDER:
    # torn dark tights under the shorts
    def holes(c): return noise.noise(c * 14 + V(3, 1, 2)) > .38 and .2 < c.z < .7
    tights = z.garment('tights', LEGS, keep=lambda p: .1 < p.z < .74, push=.002, thick=.0015, tear=holes)
    # tall boot shafts with a turned cuff
    shafts = z.garment('bootshaft', both('lowerleg01', 'lowerleg02', 'foot'), keep=lambda p: .1 < p.z < .47, push=.012,
                       fold=lambda p: .003 * math.sin(p.z * 90 + 5 * noise.noise(p * 9)) + .006 * L.sm(.42, .47, p.z), thick=.004)
    # gloves, wrist down
    WX = abs(z.j('wrist.L____head').x) - .035
    allb = [vg.name for vg in b.vertex_groups]
    gloves = z.garment('gloves', allb, keep=lambda p: abs(p.x) > WX and p.z > .6, push=.0035, thick=.002)
    # duct-taped knee pad on the left knee
    kn = z.j('lowerleg01.L____head'); hk, nk_ = z.hit(b, kn + V(0, -.4, 0), (0, 1, 0))
    kp = L.blob(f'{CH} kneepad', (hk or kn) + V(0, -.012, 0), (.055, .025, .065), C); z.bind(kp, 'lowerleg01.L')
    tape = L.box(f'{CH} tape', (hk or kn) + V(0, -.035, .01), (.06, .004, .012), C, rot=(0, .25, 0)); z.bind(tape, 'lowerleg01.L')
    # goggles pushed up on the forehead + strap
    gz = EL.z + .058; lenses = []
    for e in (EL, ER):
        h, n = z.hit(b, (e.x * 1.05, -.5, gz), (0, 1, 0))
        if h is None: continue
        h = h + V(0, -.03, .004)
        rim = L.tube(f'{CH} goggle rim', [h + V(0, .002, 0), h + V(0, -.024, 0)], .023, C, sides=18)
        gl = L.blob(f'{CH} goggle glass', h + V(0, -.026, 0), (.02, .006, .02), C)
        lenses += [rim]; extra.append(gl)
    hc2 = V(HC.x, HC.y + .012, gz + .004)
    ring = []
    for i in range(33):
        a = i / 32 * 2 * math.pi
        h, n = z.hit(b, hc2 + V(math.cos(a) * .35, math.sin(a) * .35, 0), (-math.cos(a), -math.sin(a), 0))
        if h is not None: ring.append(h + V(math.cos(a), math.sin(a), 0) * .04)
    strap = L.tube(f'{CH} goggle strap', ring, .006, C, sides=6)
    goggles = L.join(lenses + [strap], f'{CH} goggles'); z.bind(goggles, 'head')
    glass = L.join(extra, f'{CH} goggle lenses'); z.bind(glass, 'head'); extra = []
    # headset: ear cups + band over the crown
    cups = []
    ey = EL.y + .085
    for sx in (1, -1):
        h, n = z.hit(b, (sx * .4, ey, EL.z - .025), (-sx, 0, 0))
        h = h or V(sx * .075, ey, EL.z - .025)
        cups.append(L.tube(f'{CH} cup', [h + V(sx * .004, 0, 0), h + V(sx * .03, 0, 0)], [.034, .03], C, sides=20))
        cups.append(L.blob(f'{CH} cupcap', h + V(sx * .03, 0, 0), (.006, .026, .026), C))
    band = []
    for i in range(17):
        a = math.pi * i / 16
        dv = V(math.cos(a), 0, math.sin(a))
        h, n = z.hit(b, V(0, ey, EL.z - .02) + dv * .4, -dv)
        if h is not None: band.append(h + dv * .05)
    cups.append(L.tube(f'{CH} band', band, .007, C, sides=8))
    mic = L.tube(f'{CH} mic', [cups[0].location if False else V(.1, ey - .01, EL.z - .04), V(.07, EL.y - .07, EL.z - .085)], .003, C, sides=6)
    headset = L.join(cups + [mic], f'{CH} headset'); z.bind(headset, 'head')
    # bandolier with brass rounds, left shoulder to right hip
    s0 = z.j('shoulder01.L____head'); s1 = z.j('upperleg01.R____head')
    pts = []
    for i in range(15):
        t = i / 14; q = s0.lerp(s1, t) + V(-.02 * t, 0, .03 * (1 - t))
        h, n = z.hit(b, (q.x, -.6, q.z), (0, 1, 0))
        if h is not None: pts.append(h + V(0, -.032, 0))
    bando = L.tube(f'{CH} bandolier', pts, .011, C, sides=6); z.bind(bando, 'spine03')
    shells = []
    for i in range(1, len(pts) - 1, 1):
        d = (pts[i + 1] - pts[i - 1]).normalized()
        shells.append(L.tube(f'{CH} shell', [pts[i] + V(0, -.006, 0) - d.cross(V(0, 1, 0)) * .016, pts[i] + V(0, -.006, 0) + d.cross(V(0, 1, 0)) * .016], .0055, C, sides=8))
    shells = L.join(shells, f'{CH} shells'); z.bind(shells, 'spine03')
    # thigh holster
    th = z.j('upperleg02.R____head')
    h, n = z.hit(b, th + V(-.4, 0, .05), (1, 0, 0))
    hol = L.box(f'{CH} holster', (h or th) + V(-.022, 0, 0), (.02, .055, .1), C, bevel=.006); z.bind(hol, 'upperleg02.R')
    hstrap = L.tube(f'{CH} holster strap', [(h or th) + V(-.03, -.06, .06), (h or th) + V(-.03, .06, .06)], .006, C); z.bind(hstrap, 'upperleg02.R')
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
elif wp == 'pistol':
    slide = L.box(f'{CH} slide', grip - V(0, .05, .045), (.016, .1, .022), C, bevel=.003)
    gp = L.box(f'{CH} grip', grip, (.015, .028, .06), C, rot=(.25, 0, 0), bevel=.004)
    weapon = L.join([slide, gp], f'{CH} weapon'); wmat = M.metal(f'{CH}_Gun', col='#2a2a2c', rust='#4a3a2a')
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
    if RIDER: red = .3 * red + 1.3 * g3(V(p.x * .55, p.y, p.z), V(0, MO.y, EL.z - .068), .009)
    cam.data[v.index].color = (min(1, stub), min(1, sock), min(1, red), 1)
sk_ = human_skin(f'{CH}_Skin', LOOK['skin']); nt = sk_.node_tree; bs = nt.nodes['Principled BSDF']
src_ = bs.inputs['Base Color'].links[0].from_socket
vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Mask'; sp = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(vc.outputs['Color'], sp.inputs[0])
nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 900; nz.inputs['Detail'].default_value = 2
mth = nt.nodes.new('ShaderNodeMath'); mth.operation = 'MULTIPLY'; nt.links.new(sp.outputs['Red'], mth.inputs[0]); nt.links.new(nz.outputs['Fac'], mth.inputs[1])
out = src_
for fac, col, k in ((mth.outputs[0], '#2a1e18', .9), (sp.outputs['Green'], '#2a1a1c' if RIDER else '#5a3a34', .7 if RIDER else .45), (sp.outputs['Blue'], '#a8343c' if RIDER else '#b0564a', .8 if RIDER else .35)):
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
hcol = hm_.mix(hm_.mr(hn, .35, .7), M.C(LOOK['hair']), M.C('#8a857c' if RIDER else '#000000')); hcol = hm_.mix(hm_.math('MULTIPLY', hm_.mr(hn, .6, .75), .35), hcol, M.C('#8a7a6a'))
hm_.bump(hn, .5, .001); hmat = hm_.finish(hcol, rough=.42, spec=.5, cav=False)
L.setmat(hair, hmat); L.setmat(cap, hmat); L.setmat(brows, M.flat(f'{CH}_Brow', '#5e5248', .6) if RIDER else hmat)
L.setmat(weapon, wmat)

if RIDER:
    L.setmat(tights, M.canvas(f'{CH}_Tights', '#1e1c1e')); L.setmat(shafts, M.leather(f'{CH}_BootShaft', LOOK['boots']))
    L.setmat(gloves, M.leather(f'{CH}_Gloves', '#1a1614')); L.setmat(kp, M.rubber(f'{CH}_Pad', col='#2a2826'))
    L.setmat(tape, M.canvas(f'{CH}_Tape', '#8a8a86')); L.setmat(goggles, M.leather(f'{CH}_GoggleRim', '#3a2a1e'))
    L.setmat(glass, M.flat(f'{CH}_Lens', '#5a2e0e', .03)); L.setmat(headset, M.rubber(f'{CH}_Headset', col='#2c2c2e', tread=False))
    L.setmat(bando, M.leather(f'{CH}_Bando', '#3a2a1e')); L.setmat(shells, M.metal(f'{CH}_Brass', col='#b08a3a', rust='#5a4220'))
    L.setmat(hol, M.leather(f'{CH}_Holster', '#2a1e16')); L.setmat(hstrap, M.leather(f'{CH}_Hstrap', '#2a1e16'))
    L.setmat(collar, M.canvas(f'{CH}_Bandana', '#7a221c'))
    def leather_real(name, col, dark, light):
        nb = M.NB(name)
        big = nb.noise(5, 6, .6); wr = nb.noise(28, 8, .72, vec=nb.mapping(scale=(1, 1, 3.5)))
        c = nb.mix(nb.mr(big, .3, .72), M.C(col), M.C(dark))
        geo = nb.node('ShaderNodeNewGeometry')
        wear = nb.math('MULTIPLY', nb.mr(geo.outputs['Pointiness'], .5, .56), nb.mr(nb.noise(60, 4, .6), .4, .6))
        c = nb.mix(wear, c, M.C(light))
        c = nb.mix(nb.math('MULTIPLY', nb.mr(nb.noise(9, 5, .6, vec=nb.mapping(loc=(7, 2, 1))), .58, .72), .55), c, M.C('#2a2018'))   # road dirt
        nb.bump(nb.voronoi(1100), .22, .00025); nb.bump(wr, .35, .0012)
        m = nb.finish(c, rough_sock=nb.mr(big, 0, 1, .32, .62), spec=.5)
        nb.bsdf.inputs['Coat Weight'].default_value = .12; nb.bsdf.inputs['Coat Roughness'].default_value = .35
        return m
    L.setmat(jacket, leather_real(f'{CH}_JacketR', '#6e4628', '#3a2214', '#a07850'))
    L.setmat(shafts, leather_real(f'{CH}_BootR', '#6a4022', '#3a2212', '#9a7048'))
    for up, so_, lc in shoes: L.setmat(up, shafts.data.materials[0])
    L.setmat(pants, leather_real(f'{CH}_ShortsR', '#161618', '#0a0a0b', '#3a3a3e'))
    L.setmat(lashes, M.flat(f'{CH}_Lash', '#141012', .5))
    L.setmat(brows, M.flat(f'{CH}_Brow', '#6a5e54', .7))
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
RIG = z.rig; mh.pose(RIG, {})
mz = min((o.matrix_world @ v.co).z for o in z.all_meshes() for v in list(o.data.vertices)[::5])
RIG.location.z -= mz

for o in ([] if RIDER else [b, tee, jacket, pants, belt, collar, weapon, cap] + [s for sh in shoes for s in sh[:2]]):
    L.hull(o, C, t=.0032)
if RIDER:   # real strand hair for renders (cards stay for the GLB)
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()
    bvh = BVHTree.FromObject(b, dg)
    hair.hide_render = True
    cm = cap.matrix_world; cv = [cm @ v.co for v in cap.data.vertices]
    hc = sum(cv, Vector()) / len(cv); top = max(v.z for v in cv)
    eyez = (sum((o.matrix_world @ v.co for o in (z.parts['eyeL'], z.parts['eyeR']) for v in o.data.vertices), Vector()) / (len(z.parts['eyeL'].data.vertices) * 2))
    rng2 = random.Random(5); K = 10; pos = []; rad = []
    polys = cap.data.polygons; NPER = 6
    for pl in polys:
        n = (cm.to_3x3() @ pl.normal).normalized()
        if n.z < -.3: continue
        vs = [cv[i] for i in pl.vertices]
        for _ in range(NPER):
            w = [rng2.random() for _ in vs]; sw = sum(w); r0 = sum((vv * (wi / sw) for vv, wi in zip(vs, w)), Vector())
            front = (r0 - hc).y < -.035 and r0.z > eyez.z + .05
            nv = noise.noise_vector(r0 * 25)
            chop = .5 + .5 * noise.noise(r0 * 18)
            if front:
                ln = max(.012, (r0.z - (eyez.z + .03 + .012 * chop)) * 1.15); d = (n * .5 + V(0, -.6, -1)).normalized()
            else:
                tipz = eyez.z - .085 + .035 * chop - .02 * max(0, (r0 - hc).y) * 10
                ln = max(.03, r0.z - tipz + .03); d = (n * (.35 if n.z > .6 else .9) + V(0, .12, -.6)).normalized()
            d = (d + nv * .25).normalized()
            q = r0 + n * .002; seg = ln / (K - 1)
            for k in range(K):
                if k:
                    d = (d + V(0, 0, -.55) + nv * .08).normalized(); q = q + d * seg
                    loc, nn, _, dist = bvh.find_nearest(q)
                    if loc is not None and dist < .03:
                        q = loc + nn * .03
                pos += [q.x, q.y, q.z]; rad.append(.00011 * (1 - k / K) + .00002)
    NC = len(pos) // (3 * K)
    hcv = bpy.data.hair_curves.new(f'{CH} strands'); hcv.add_curves([K] * NC)
    hcv.attributes['position'].data.foreach_set('vector', pos)
    ra = hcv.attributes.get('radius') or hcv.attributes.new('radius', 'FLOAT', 'POINT'); ra.data.foreach_set('value', rad)
    ho = bpy.data.objects.new(f'{CH} strands', hcv); C.objects.link(ho)
    hm2 = bpy.data.materials.new(f'{CH}_HairStrand'); hm2.use_nodes = True; nt2 = hm2.node_tree
    for nn_ in list(nt2.nodes):
        if nn_.type == 'BSDF_PRINCIPLED': nt2.nodes.remove(nn_)
    hb_ = nt2.nodes.new('ShaderNodeBsdfHairPrincipled'); hb_.parametrization = 'MELANIN'
    hb_.inputs['Melanin'].default_value = .035; hb_.inputs['Melanin Redness'].default_value = .12
    hb_.inputs['Roughness'].default_value = .28; hb_.inputs['Radial Roughness'].default_value = .35
    if 'Random Roughness' in hb_.inputs: hb_.inputs['Random Roughness'].default_value = .3
    if 'Random Color' in hb_.inputs: hb_.inputs['Random Color'].default_value = .15
    nt2.links.new(hb_.outputs[0], nt2.nodes['Material Output'].inputs['Surface'])
    hcv.materials.append(hm2)
    L.setmat(cap, M.flat(f'{CH}_Scalp', '#9a9288', .8))
    print('strands', NC, flush=True)
    ho.parent = RIG; ho.parent_type = 'BONE'; ho.parent_bone = 'head'
    bpy.context.view_layer.update()
    hb = RIG.pose.bones['head']; ho.matrix_parent_inverse = (RIG.matrix_world @ hb.matrix @ __import__('mathutils').Matrix.Translation((0, hb.length, 0))).inverted()

L.studio(sc); sc.view_settings.exposure = -.75 if RIDER else -.2
if RIDER:
    try:
        sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception as ex: print('look', ex)
    for o in sc.objects:
        if o.type == 'LIGHT':
            if o.name == 'key': o.location = (-1.9, -2.5, 2.6); o.data.energy = 260; o.data.size = 1.1; o.data.color = (1, .9, .78)
            if o.name == 'rim': o.location = (1.9, 1.9, 2.3); o.data.energy = 380; o.data.size = .7; o.data.color = (.7, .82, 1)
            if o.name == 'fill': o.data.energy = 28
    R2 = bpy.data.lights.new('rim2', 'AREA'); R2.energy = 260; R2.size = .6; R2.color = (1, .75, .5)
    r2 = bpy.data.objects.new('rim2', R2); sc.collection.objects.link(r2); r2.location = (-1.8, 1.9, 2.0)
    r2.rotation_euler = (Vector((0, 0, 1.2)) - r2.location).to_track_quat('-Z', 'Y').to_euler()
for n in sc.world.node_tree.nodes:
    if n.type == 'BACKGROUND' and n.inputs['Color'].default_value[0] > .5: n.inputs['Color'].default_value = (*L.lin('#1a1b21' if RIDER else '#30303a'), 1)
eyes_c = sum((o.matrix_world @ v.co for o in (z.parts['eyeL'], z.parts['eyeR']) for v in o.data.vertices), Vector()) / (len(z.parts['eyeL'].data.vertices) * 2)
shots = [('front34', 28, 6, 3.4, .92, 50), ('side', 90, 4, 3.4, .92, 50), ('back34', 205, 10, 3.4, .92, 50), ('face', 20, 2, .6, None, 70)]
if RIDER: shots = [('front34', 24, 6, 2.55, .9, 50), ('side', 90, 4, 2.55, .9, 50), ('back34', 205, 10, 2.55, .9, 50), ('face', 22, 3, .62, None, 85)]
SAMP = int(os.environ.get('SAMP', '40')); RES = float(os.environ.get('RES', '1')); only = os.environ.get('ONLY')
for nm, az, el, dist, tz, lens in shots:
    if only and nm not in only.split(','): continue
    tgt = eyes_c + V(0, .02, -.03) if nm == 'face' else V(0, -.1, tz)
    camo = L.camera(sc, tgt, dist, az, el, lens=lens)
    if False: camo.data.dof.use_dof = True; camo.data.dof.focus_distance = dist; camo.data.dof.aperture_fstop = 5.6
    L.render(sc, f'{OUT}/{nm}.png', w=int(1080 * RES), h=int(1350 * RES), samples=SAMP)
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/{CH}.blend')
