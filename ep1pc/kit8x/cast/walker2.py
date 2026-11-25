"""WALKER v2 on the MakeHuman CC0 anatomy: office-worker zombie in a torn flannel shirt."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, noise
import castlib as L, mh, mats as M, anatomy as A
from zbuild import Char, shoe, V
OUT = os.environ.get('OUT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out/walker2'))
os.makedirs(OUT, exist_ok=True)
sc = L.reset(); C = L.collection('Walker')
LR = ('.L', '.R')
def both(*names): return [n + s for n in names for s in LR]

z = Char('Walker', {'universal-male-young-minmuscle-minweight': 1.0}, C)
b = z.body
# --------------------------------------------------------------- body damage (rest pose)
z.subdiv(b, 1)
z.disp(b, tex_type='CLOUDS', size=.025, strength=.003, depth=4)
z.disp(b, tex_type='VORONOI', size=.04, strength=-.0012, distance_metric='DISTANCE')
WC = None
loc, nor = z.hit(b, (.07, -.5, 1.07), (0, 1, 0)); WC = loc            # belly wound, front-left
CH = z.hit(b, (.032, -.5, 1.468), (0, 1, 0))[0]                      # torn cheek (left)
EAR = V(.078, .0, 1.565)
def wound(p): return (p - WC).length < .042 + .012 * noise.noise(p * 70) + .006 * noise.noise(p * 200)
def cheek(p): return (p - CH).length < .014 + .004 * noise.noise(p * 300) and p.y < -.06
def ear(p): return p.x > .06 and (p - EAR).length < .03 and p.z > 1.555 + .006 * noise.noise(p * 300)
z.cut(b, lambda p: wound(p) or cheek(p))
L.smooth(b)

# wound interior: gore pocket, ribs, intestine loop; torn-flesh rims
inner = WC + V(-.005, .045, 0)
cav = L.blob('Walker cavity', inner, (.05, .045, .055), C)
ribs = []
for k in range(3):
    zz = WC.z + .02 + k * .024
    pts = [V(.005 + math.cos(a) * .085, WC.y + .055 - math.sin(-a) * 0 - (math.cos(a) * .06), zz + t * .001) for t, a in enumerate([.2 + i * .12 for i in range(9)])]
    ribs.append(L.tube(f'Walker rib{k}', pts, [.0055] * 9, C, sides=8))
ribs = L.join(ribs, 'Walker ribs')
gut = L.tube('Walker gut', [WC + V(-.02 + .008 * math.sin(t * 2.1), .02 + .006 * math.cos(t * 1.7), -.02 + t * .007) for t in range(8)], .011, C, sides=10)
def rim(name, centre, rad, normal_axis, n=28, th=.0055):
    pts = []
    for k in range(n + 1):
        a = k / n * 2 * math.pi
        r = rad + .006 * noise.noise(V(math.cos(a), math.sin(a), 0) * 4)
        q = centre + V(math.cos(a) * r, 0, math.sin(a) * r)
        hp, _ = z.hit(b, q + V(0, -.3, 0), (0, 1, 0))
        pts.append(hp if hp is not None else q)
    return L.tube(name, pts, [th * (.7 + .6 * abs(math.sin(k * 1.9))) for k in range(n + 1)], C, sides=8, cap=False)
rims = [rim('Walker woundrim', WC, .044, 'y'), rim('Walker cheekrim', CH, .015, 'y', th=.0028)]
gore_parts = [cav, ribs, gut] + rims
for o in gore_parts: z.bind(o, 'spine03' if o not in rims[1:] else 'head')

# --------------------------------------------------------------- clothing
SPINE = ['spine01', 'spine02', 'spine03', 'spine04', 'spine05'] + both('clavicle', 'shoulder01', 'breast', 'upperarm01', 'upperarm02')
def tee_keep(p): return p.z > .9 + .03 * noise.noise(p * 25)
def shirt_tear(p):
    return (p - WC).length < .075 + .02 * noise.noise(p * 40) or \
           (noise.noise(p * 14 + V(3, 1, 2)) + .12 * noise.noise(p * 120) > .58 and p.z < 1.3) or \
           (p.z > 1.38 and abs(p.x) < .055 and p.y < -.02)   # open collar
def shirt_fold(p):
    return .007 * math.sin(p.z * 70 + 10 * noise.noise(p * 6)) * (1 - L.sm(1.2, 1.36, p.z)) + .004 * noise.noise(p * 18) + .01 * L.sm(1.0, .9, p.z)
shirt = z.garment('shirt', SPINE + both('lowerarm01'), keep=tee_keep, push=.011, fold=shirt_fold, tear=shirt_tear, ragged=True)
# roll the sleeves: drop most of lowerarm01
L.delete_faces(shirt, lambda p, n: abs(p.x) > .29 + .02 * noise.noise(p * 40))
LEGS = both('pelvis', 'upperleg01', 'upperleg02', 'lowerleg01', 'lowerleg02') + ['spine05', 'spine04']
KNEE = z.j('lowerleg01.L____head')
def pants_keep(p): return p.z < 1.0 and p.z > .12 + .05 * abs(noise.noise(p * 22))
def pants_tear(p): return (p - KNEE - V(0, -.045, .0)).length < .045 + .012 * noise.noise(p * 150) or noise.noise(p * 20 + V(9, 9, 9)) + .15 * noise.noise(p * 140) > .62
def pants_fold(p): return .004 * math.sin(p.z * 60 + 6 * noise.noise(p * 10)) + .002 * noise.noise(p * 50) + .006 * L.sm(.3, .12, p.z)
pants = z.garment('pants', LEGS, keep=pants_keep, push=.009, fold=pants_fold, tear=pants_tear)
belt = z.garment('belt', LEGS, keep=lambda p: .955 < p.z < .99, push=.02, thick=.006)
bk = z.hit(belt, (0, -.5, .972), (0, 1, 0))[0]
buckle = L.box('Walker buckle', bk + V(0, -.004, 0), (.024, .005, .018), C, bevel=.003); z.bind(buckle, 'spine05')

# shoes (left sole flapping) bound to the feet
shoes = []
for side, flap in (('L', 0.), ('R', -.4)):
    a = z.j(f'foot.{side}____head'); t = z.j(f'toe3-1.{side}____head')
    a = V(a.x, a.y + .01, .093 * .86)
    up, so, lc = shoe(f'Walker {side}', C, a, t, flap=flap, scale=.86)
    for o in (up, so, lc): z.bind(o, f'foot.{side}')
    shoes.append((up, so, lc))
L.delete_faces(b, lambda p, n: p.z < .12)          # feet hidden in shoes

# lanyard + badge, wristwatch
bad, bn = z.hit(shirt, (.02, -.6, 1.19), (0, 1, 0))
badge = L.box('Walker badge', bad + V(0, -.006, 0), (.026, .0025, .036), C, rot=(0, 0, .1), bevel=.002)
photo = L.box('Walker badgephoto', bad + V(-.009, -.0087, .006), (.008, .0004, .011), C)
clip = L.box('Walker clip', bad + V(0, -.008, .04), (.007, .003, .008), C, bevel=.001)
nk = z.j('neck01____head')
def ring(r, yoff, zz):
    return [V(math.cos(a) * r, nk.y + yoff + math.sin(a) * r * .9, zz - math.sin(a) * .015) for a in [i / 16 * math.pi for i in range(17)]]
lpts = ring(.07, .0, 1.405)
lan = L.join([L.tube('Walker lan1', [lpts[0], V(.05, -.12, 1.33), bad + V(.0, -.009, .045)], .0028, C, sides=5),
              L.tube('Walker lan2', [lpts[-1], V(-.03, -.13, 1.33), bad + V(.0, -.009, .045)], .0028, C, sides=5),
              L.tube('Walker lan3', [V(p.x, -p.y + 2 * nk.y + .03, p.z + .01) for p in lpts], .0028, C, sides=5), clip], 'Walker lanyard')
for o in (badge, photo, lan): z.bind(o, 'spine02')
wr = z.j('wrist.L____head'); la = z.j('lowerarm02.L____head'); d = (wr - la).normalized()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=32, radius1=.03, radius2=.03, depth=.02)
watch = L.mesh_obj('Walker watch', bm, C); so = watch.modifiers.new('s', 'SOLIDIFY'); so.thickness = .004
watch.location = wr - d * .035; watch.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); watch.scale = (1, .72, 1)
L.apply_transform(watch)
wf, _ = z.hit(watch, wr - d * .035 + V(0, 0, .2), (0, 0, -1))
face = L.blob('Walker watchface', (wf or wr) + V(0, 0, .002), (.015, .013, .004), C)
for o in (watch, face): z.bind(o, 'lowerarm02.L')

EL, ER = z.j('eye.L____head'), z.j('eye.R____head')
# hair: matted clumps (tapered strips) with bald patches, plus eyebrows; bound to head
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
def scalp(p):
    if p.z < 1.57 or (p.y < -.075 and p.z < 1.7) or (abs(p.x) > .06 and p.z < 1.6 and p.y < .0): return False
    if (p - (HC + V(0, .01, .08))).length > .2: return False
    return noise.noise(p * 14) > -.45
def hlen(p, r): return r.uniform(.03, .07) * (.4 + .6 * abs(noise.noise(p * 7)))
def hflow(p): return (V(p.x * 2, .6, -.5) + V(0, 0, 0)).normalized()
hair = hair_cards(b, 'Walker hair', scalp, hlen, .0065, hflow, count_skip=.0)
def brow(p):
    for e in (EL, ER):
        q = p - e
        if -.03 < q.y < -.0 and abs(q.z - .019 + .1 * q.x * q.x) < .0035 and abs(q.x) < .02: return True
    return False
brows = hair_cards(b, 'Walker brows', brow, lambda p, r: r.uniform(.005, .008), .0007, lambda p: V(1 if p.x > 0 else -1, 0, .3), seed=9, segs=2, count_skip=.4)
L.delete_faces(brows, lambda p, n: True); hair = L.join([hair, brows], 'Walker hair')
z.bind(hair, 'head')

# --------------------------------------------------------------- masks (rest pose coords): r blood, g dark, b dirt
def g3(p, c, r): return math.exp(-((p - c).length_squared) / (r * r))
MOUTH = z.hit(b, (0, -.5, 1.468), (0, 1, 0))[0] if z.hit(b, (0, -.5, 1.468), (0, 1, 0))[0] is not None else V(0, -.11, 1.468)
def m_body(p, n):
    bl = L.sm(.08, .042, (p - WC).length) + L.sm(.03, .014, (p - CH).length)
    bl += g3(V(p.x * .6, p.y, p.z), V(MOUTH.x, MOUTH.y, MOUTH.z - .01), .03) * .9
    # drool streaks down the chin + neck
    for x0 in (-.016, .0, .02):
        bl += g3(V(p.x, 0, 0), V(x0, 0, 0), .005) * L.sm(1.47, 1.36, p.z) * L.sm(1.3, 1.36, p.z) * (p.y < -.05) * .8
    for x0 in (.07, .11):   # blood runs from the wound
        bl += g3(V(p.x, 0, 0), V(x0, 0, 0), .007) * L.sm(WC.z, WC.z - .12, p.z) * L.sm(WC.z - .2, WC.z - .1, p.z) * (p.y < -.05)
    dk = g3(V(p.x, p.y, p.z * 1.3), V(EL.x, EL.y + .012, EL.z * 1.3), .03) + g3(V(p.x, p.y, p.z * 1.3), V(ER.x, ER.y + .012, ER.z * 1.3), .03)
    dk += g3(V(p.x * .5, p.y, p.z), V(0, MOUTH.y, MOUTH.z), .02) * .6
    dk += sum(g3(V(p.x, p.y, p.z * 2.5), V(e.x, e.y - .005, (e.z + .02) * 2.5), .013) for e in (EL, ER)) * .9   # painted brows
    hands = L.sm(.95, .8, p.z) * (abs(p.x) > .3)
    return (min(1, bl), min(1, dk * .9), min(1, L.sm(.4, .9, L.fbm(p, 5)) * .7 + hands * .6))
def m_shirt(p, n):
    bl = L.sm(.11, .06, (p - WC).length) + L.sm(.022, .008, abs(p.x - .005 - .015 * math.sin(p.z * 30))) * L.sm(1.0, 1.38, p.z) * (p.y < -.06)
    return (min(1, bl), 0, L.sm(1.0, .9, p.z) * .7)
def m_pants(p, n): return (L.sm(.5, .8, L.fbm(p + V(8, 2, 0), 8)) * .5 * (p.z > .6), 0, L.sm(.35, .12, p.z))
def paint_mask(o, fn):
    ca = o.data.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
    for v in o.data.vertices:
        c = fn(o.matrix_world @ v.co, v.normal); ca.data[v.index].color = (*c, 1)
def with_mask(mat, blood='#4a080c', dark='#22141a', dirt='#3a2f24'):
    nt = mat.node_tree; bs = nt.nodes['Principled BSDF']
    src = bs.inputs['Base Color'].links[0].from_socket
    vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Mask'
    sp = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(vc.outputs['Color'], sp.inputs[0])
    out = src
    for ch, col in (('Blue', dirt), ('Green', dark), ('Red', blood)):
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
        nt.links.new(sp.outputs[ch], mx.inputs[0]); nt.links.new(out, mx.inputs[6]); mx.inputs[7].default_value = (*L.lin(col), 1)
        out = mx.outputs[2]
    nt.links.new(out, bs.inputs['Base Color'])
    # wet blood: lower roughness where red mask
    return mat
paint_mask(b, m_body); paint_mask(shirt, m_shirt); paint_mask(pants, m_pants)

# --------------------------------------------------------------- materials
L.setmat(b, with_mask(M.toon_skin('Walker_Skin'), blood='#6a0d12', dark='#1e1420'))
L.setmat(shirt, with_mask(M.toon_plaid('Walker_Flannel'), blood='#5a0a10'))
L.setmat(pants, with_mask(M.toon_denim('Walker_Denim'), blood='#5a0a10'))
L.setmat(belt, M.toon_flat('Walker_Belt', '#4a3020')); L.setmat(buckle, M.metal('Walker_Metal'))
for up, so, lc in shoes: L.setmat(up, M.toon_flat('Walker_Canvas', '#c8452e', dirt='#5a4a36')); L.setmat(so, M.toon_flat('Walker_Sole', '#efe6d0', dirt='#6a5a44')); L.setmat(lc, M.flat('Walker_Lace', '#bdb8a8', .8))
eye = M.eye_m('Walker_Eye', iris='#ffd65a', glow=1.4)
for k in ('eyeL', 'eyeR'): L.setmat(z.parts[k], eye); z.subdiv(z.parts[k], 2)
tm = M.teeth_m('Walker_Teeth')
for k in ('teethU', 'teethL'): L.setmat(z.parts[k], tm); z.subdiv(z.parts[k], 1)
L.setmat(z.parts['tongue'], M.gore('Walker_Tongue'))
g = M.gore('Walker_Gore')
for o in [cav, gut] + rims: L.setmat(o, g)
L.setmat(ribs, M.bone('Walker_Bone'))
L.setmat(badge, M.flat('Walker_Badge', '#e9e4d6', .3)); L.setmat(photo, M.flat('Walker_Photo', '#7a8a9a', .4))
L.setmat(lan, M.flat('Walker_Lanyard', '#2f6fa8', .7))
L.setmat(watch, M.metal('Walker_Steel')); L.setmat(face, M.flat('Walker_Glass', '#9fb7c4', .05))
L.setmat(hair, M.flat('Walker_Hair', '#231b16', .55))

# --------------------------------------------------------------- pose: hunched shamble, one arm reaching, jaw hanging
POSE = {
    'spine05': (4, 0, 0), 'spine04': (6, 0, 2), 'spine03': (8, 0, 3), 'spine02': (8, 0, 0), 'spine01': (6, 0, 0),
    'neck01': (12, 0, 0), 'neck02': (6, 0, 0), 'head': (-14, 8, 14), 'jaw': (-26, 0, 3),
    'clavicle.L': (0, 0, -8), 'upperarm01.L': (62, 0, -12), 'lowerarm01.L': (0, 0, 12), 'wrist.L': (-25, 0, 0),
    'clavicle.R': (0, 0, 6), 'upperarm01.R': (12, 0, 38), 'lowerarm01.R': (0, 0, -22), 'wrist.R': (15, 0, 0),
    'upperleg01.L': (24, 0, -2), 'lowerleg01.L': (-28, 0, 0), 'foot.L': (6, 0, 0),
    'upperleg01.R': (-14, 0, 3), 'lowerleg01.R': (-34, 0, 0), 'foot.R': (30, 0, 0),
}
for side, curl in (('L', 32), ('R', 18)):
    for f in range(2, 6):
        for k in (1, 2, 3):
            POSE[f'finger{f}-{k}.{side}'] = (curl + random.Random(f * 7 + k).uniform(-10, 10), 0, 0)
    POSE[f'finger1-2.{side}'] = (15, 0, 0)
# stylised proportions: bigger head and hands, longer neck and forearms
SCALE = {'head': 1.2, 'jaw': 1.15, 'wrist.L': 1.35, 'wrist.R': 1.35, 'neck01': (.9, 1.2, .9), 'lowerarm01.L': (1, 1.12, 1), 'lowerarm01.R': (1, 1.12, 1), 'foot.L': 1.12, 'foot.R': 1.12}
for bn, sv in SCALE.items():
    pb = z.rig.pose.bones[bn]; pb.scale = (sv, sv, sv) if not isinstance(sv, tuple) else sv
z.pose_and_bake(POSE)
# settle on the floor
mz = min((o.matrix_world @ v.co).z for o in z.all_meshes() for v in list(o.data.vertices)[::7])
for o in z.all_meshes(): o.location.z -= mz

# --------------------------------------------------------------- ink hulls
for o in [b, shirt, pants, belt] + [s for sh in shoes for s in sh[:2]]:
    L.hull(o, C, t=.0042)

L.studio(sc); sc.view_settings.exposure = -.45
VIEWS = os.environ.get('VIEWS', 'hero')
shots = {'hero': [('front34', 32, 8, 3.0, .9, 50), ('side', 90, 4, 3.0, .9, 50), ('back34', 200, 10, 3.0, .9, 50), ('face', 15, -14, .5, 1.46, 70)],
         'face': [('face', 15, -14, .5, 1.46, 70)],
         'detail': [('face', 15, -14, .5, 1.46, 70), ('wound', 35, 5, .7, 1.05, 70), ('feet', 30, 15, .9, .15, 60), ('hand', 70, 10, .7, 1.2, 70)]}[VIEWS]
SAMP = int(os.environ.get('SAMP', '40')); RES = float(os.environ.get('RES', '1'))
EYE = (z.parts['eyeL'].matrix_world @ z.parts['eyeL'].data.vertices[0].co)
eyes_c = sum((o.matrix_world @ v.co for o in (z.parts['eyeL'], z.parts['eyeR']) for v in o.data.vertices), Vector()) / (len(z.parts['eyeL'].data.vertices) * 2)
for nm, az, el, dist, tz, lens in shots:
    tgt = eyes_c + V(0, .03, -.02) if nm == 'face' else V(0, -.12, tz)
    L.camera(sc, tgt, dist, az, el, lens=lens)
    L.render(sc, f'{OUT}/{nm}.png', w=int(1080 * RES), h=int(1350 * RES), samples=SAMP)
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/walker.blend')
