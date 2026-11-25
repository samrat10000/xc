"""SCREAMER (derived from the Husk pipeline): a gaunt woman whose jaw has unhinged into a huge scream, throat swollen with black veins, long wet hair, torn dress.
OLD: mid-stage infected. Original design: a starved, charred-black body of dried sinew stretched over
bone, lipless grin, sunken pinpoint eyes, elongated hands ending in long hooked claws, rags fused into
the skin. Realistic materials + ink hull. Built on the MakeHuman CC0 base."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import bpy, bmesh
from mathutils import Vector, noise
import castlib as L, mh, mats as M
from zbuild import Char, V
OUT = os.environ.get('OUT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out/screamer'))
os.makedirs(OUT, exist_ok=True)
M.STYLE['cavity'] = True; M.STYLE['cav_kw'] = {'dist': .04, 'strength': .6}
sc = L.reset(); C = L.collection('Screamer')
rng = random.Random(11)
LR = ('.L', '.R')
def both(*names): return [n + s for n in names for s in LR]

z = Char('Screamer', {'universal-female-young-minmuscle-minweight': 1.0}, C)
b = z.body
z.subdiv(b, 1)
EL, ER = z.j('eye.L____head'), z.j('eye.R____head')
MZ = EL.z - .092; NZ = EL.z - .045
MOUTH = z.hit(b, (0, -.5, MZ), (0, 1, 0))[0] or V(0, -.11, MZ)
NOSE = z.hit(b, (0, -.5, NZ), (0, 1, 0))[0] or V(0, -.12, NZ)
SP3 = z.j('spine03____head')

# ---------------------------------------------------------------- starvation: sinew strands, rib grooves, hollow face
P = np.array([v.co[:] for v in b.data.vertices]); Nn = np.array([v.normal[:] for v in b.data.vertices])
def g3(p, c, r): return math.exp(-((p - c).length_squared) / (r * r))
crest = np.zeros(len(P)); groove = np.zeros(len(P))
disp = np.zeros(len(P))
for i, (p, n) in enumerate(zip(P, Nn)):
    p = Vector(p)
    # long stringy strands: stretched noise along the body's length
    q = V(p.x * 38, p.y * 38, p.z * 7)
    s1 = max(0, 1 - abs(noise.noise(q)) * 4.5) ** 3
    s2 = max(0, 1 - abs(noise.noise(q * 1.9 + V(4, 2, 7))) * 5) ** 3
    st = min(1, s1 + .6 * s2)
    d = .0065 * st - .0065 + .0018 * noise.noise(p * 60)
    gr = 0.
    # ribs: deep grooves between ribs on the chest and flanks
    if False:
        ph = (p.z - 1.05 + .5 * abs(p.x) ** 1.5) / .034
        rib = (.5 + .5 * math.cos(ph * 2 * math.pi)) ** 2
        w = L.sm(.02, .07, abs(p.x)) * L.sm(1.05, 1.12, p.z) * L.sm(1.36, 1.3, p.z)
        d += .006 * rib * w - .006 * w
        gr = max(gr, (1 - rib) * w)
    # sunken belly under the ribcage
    d -= .014 * g3(V(p.x * .7, p.y, p.z), V(0, -.08, 1.0), .07) * (p.y < 0)
    # hollow face: sockets, cheeks, temples; nose gone
    for e in (EL, ER):
        d -= .006 * g3(p, e + V(0, .004, .003), .024)
        d -= .007 * g3(p, V(e.x * 1.25, e.y + .02, e.z - .05), .022)
        d -= .005 * g3(p, V(e.x * 1.9, e.y + .06, e.z + .015), .02)
        gr = max(gr, g3(p, e, .024))
    d -= .006 * g3(V(p.x, p.y, p.z), NOSE, .012)
    d += .008 * g3(V(p.x * .8, p.y, p.z), V(0, -.05, EL.z - .17), .035) * (p.y < .0)   # swollen throat
    # neck tendons and collarbones stand out
    if EL.z - .2 < p.z < EL.z - .08: d -= .005 * L.sm(.02, .045, abs(abs(p.x) - .025)) * (p.y < -.02)
    disp[i] = d; crest[i] = st; groove[i] = min(1, gr + max(0, -d) * 60)
for i, v in enumerate(b.data.vertices): v.co += v.normal * float(disp[i])
b.data.update()
# relax crumpled folds in the face (eyelids, lips) after the hollowing
FCr = (EL + ER) / 2 + V(0, -.01, -.04)
vg = b.vertex_groups.new(name='facesmooth')
for v in b.data.vertices:
    w = max(math.exp(-((v.co - FCr).length_squared) / (.075 ** 2)), *[math.exp(-((v.co - V(sx * .075, EL.y + .085, EL.z - .02)).length_squared) / (.03 ** 2)) for sx in (1, -1)])
    if w > .02: vg.add([v.index], w, 'REPLACE')
sm = b.modifiers.new('fs', 'SMOOTH'); sm.factor = .8; sm.iterations = 12; sm.vertex_group = 'facesmooth'
z.apply_first(b, sm)
# lipless mouth: cut the lips away so the teeth show; nose tip torn off
def lips(p): return ((p.x / .032) ** 2 + ((p.z - MOUTH.z) / .016) ** 2) < 1 + .25 * noise.noise(p * 300) and p.y < MOUTH.y + .02
def nose(p): return (p - NOSE).length < .011 + .003 * noise.noise(p * 300) and p.y < NOSE.y + .01
def socket(p): return any((p - e).length < .016 + .003 * noise.noise(p * 250) and p.y < e.y - .004 for e in (EL, ER))
# open chest: ribcage exposed through torn skin (rib arcs traced on the skin before cutting)
CHC = V(0, -.005, 1.2)
def chest(p):
    q = V(p.x / (.085 + .015 * noise.noise(p * 30)), 0, (p.z - 1.2) / (.14 + .02 * noise.noise(p * 25)))
    return False
rib_pts = []
for k in range(8):
    zz = 1.08 + k * .033; row = []
    for j in range(17):
        a = math.radians(-95 + j * (190 / 16))
        d = V(math.sin(a), -math.cos(a), -.25 * abs(math.sin(a)))
        loc, nor = z.hit(b, V(0, .0, zz), d.normalized())
        if loc is not None: row.append((loc - nor * .004, a))
    rib_pts.append(row)
z.cut(b, lambda p: lips(p) or nose(p) or socket(p) or chest(p))
bones_ = []
for k, row in enumerate(rib_pts):
    for side in (1, -1):
        seg = [p for p, a in row if side * a > math.radians(8 + 6 * ((k * 7) % 3))]   # sternum gone, ribs snapped at different lengths
        if side < 0: seg = seg[::-1]
        if len(seg) >= 3: bones_.append(L.tube(f'Screamer rib{k}{side}', seg, [.0095] * len(seg), C, sides=8))
# sternum stub and spine column at the back of the cavity
for k in range(9):
    bones_.append(L.box(f'Screamer vert{k}', V(0, .045, 1.04 + k * .034), (.016, .012, .012), C, bevel=.004))
ribs = L.join(bones_, 'Screamer ribs')
inner = L.blob('Screamer cavity', V(0, -.015, 1.2), (.07, .035, .13), C)
strands = []
for k in range(7):
    x0 = rng.uniform(-.07, .07); z0 = rng.uniform(1.1, 1.3)
    a_ = V(x0, -.08, z0); b2 = V(-x0 * .6 + rng.uniform(-.03, .03), -.08, z0 - rng.uniform(.04, .1))
    m_ = a_.lerp(b2, .5) + V(0, -.005, -.04)
    strands.append(L.tube(f'Screamer strand{k}', [a_, m_, b2], [.002, .0035, .002], C, sides=6))
strands = L.join(strands, 'Screamer strands')
for o in (inner, ribs, strands): bpy.data.objects.remove(o)

# ---------------------------------------------------------------- hooked claws on every finger
claws = []
for sd in LR:
    for f in range(1, 6):
        h = z.j(f'finger{f}-3{sd}____head'); t = z.j(f'finger{f}-3{sd}____tail')
        d = (t - h).normalized(); ln = .05 if f > 1 else .04
        # curl direction: toward the palm (down in A-pose, roughly -Z rotated); use a perpendicular
        down = (V(0, 0, -1) - d * d.z).normalized()
        pts = [h + d * .004, t, t + d * ln * .45 + down * ln * .08, t + d * ln * .8 + down * ln * .35, t + d * ln * .95 + down * ln * .7]
        o = L.tube(f'Screamer claw{sd}{f}', pts, [.0058, .0052, .004, .0022, .0004], C, sides=8)
        z.bind(o, f'finger{f}-3{sd}'); claws.append(o)

# ---------------------------------------------------------------- rags fused into the skin
DRESS = ['spine01', 'spine02', 'spine03', 'spine04', 'spine05'] + both('clavicle', 'breast', 'pelvis', 'upperleg01', 'upperleg02')
def dress_keep(p): return .55 + .1 * noise.noise(p * 8) < p.z < 1.38 - .04 * abs(p.x) * 10 * (abs(p.x) > .08)
def rag_tear(p):
    holes = noise.noise(p * 7 + V(2, 7, 1)) + .12 * noise.noise(p * 70) > .4
    hem = abs(math.sin(p.x * 40 + p.y * 30 + 6 * noise.noise(p * 5))) < .35 and p.z < .75
    return holes or hem
def rag_fold(p): return .006 * math.sin(p.z * 40 + 9 * noise.noise(p * 6)) + .003 * noise.noise(p * 30) + .03 * L.sm(.95, .6, p.z) * (1 + .3 * noise.noise(p * 8))
rags = z.garment('dress', DRESS, keep=dress_keep, push=.007, fold=rag_fold, thick=.003)
z.subdiv(rags, 2); L.delete_faces(rags, lambda p, n: rag_tear(p))
LEGW = both('upperleg01', 'upperleg02', 'lowerleg01')
def wrap_keep(p): return False
wraps = z.garment('legwraps', LEGW, keep=wrap_keep, push=.005, fold=lambda p: .003 * math.sin(p.z * 160 + 4 * noise.noise(p * 8)), thick=.003)


# ---------------------------------------------------------------- vertex masks: r = dry sinew crest, g = groove/tar, b = ash
ca = b.data.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
ash = np.array([max(0, noise.noise(Vector(p) * 5 + V(1, 8, 3))) for p in P])
cols = np.stack([crest, groove, ash, np.ones(len(P))], 1).astype(np.float32)
# vertex count unchanged by the cut? cut deletes faces only, vertices of removed faces may be dropped -> recompute by position
if len(b.data.vertices) != len(P):
    from mathutils.kdtree import KDTree
    kd = KDTree(len(P))
    for i, p in enumerate(P): kd.insert(Vector(p) + Vector(Nn[i]) * disp[i], i)
    kd.balance()
    cols = np.array([cols[kd.find(v.co)[1]] for v in b.data.vertices], np.float32)
ca.data.foreach_set('color', cols.ravel())

# ---------------------------------------------------------------- materials
def screamer_skin():
    nb = M.NB('Screamer_Skin')
    vc = nb.node('ShaderNodeVertexColor', layer_name='Mask'); sp = nb.node('ShaderNodeSeparateColor'); nb.link(vc.outputs['Color'], sp.inputs[0])
    cr, gr, ash = sp.outputs['Red'], sp.outputs['Green'], sp.outputs['Blue']
    n1 = nb.noise(6, 8, .6); n2 = nb.noise(30, 8, .65)
    str_ = nb.noise(14, 6, .6, vec=nb.mapping(scale=(3, 3, .5)))
    c = nb.ramp(n1, [(.3, M.C('#6c6650')), (.5, M.C('#8f8a6e')), (.7, M.C('#aaa48a'))])
    c = nb.mix(nb.math('MULTIPLY', cr, .4), c, M.C('#c4bfa4'))                       # dried sinew strands catch light
    c = nb.mix(nb.math('MULTIPLY', nb.mr(str_, .52, .62), .5), c, M.C('#3a2440'))       # raw red-brown fibre
    c = nb.mix(nb.math('MULTIPLY', gr, .85), c, M.C('#1c1016'))                        # tar-black grooves
    c = nb.mix(nb.math('MULTIPLY', nb.mr(ash, .3, .7), .5), c, M.C('#4a3050'))       # ash dust
    nb.bump(n2, .35, .0012); nb.bump(nb.noise(120, 4, .6), .2, .0005); nb.bump(str_, .3, .0015)
    rough = nb.mr(gr, 0, 1, .78, .42)                                                   # wet tar in the grooves
    m = nb.finish(c, spec=.3, rough_sock=rough)
    return m
def rag_mat():
    nb = M.NB('Screamer_Rags')
    n = nb.noise(10, 8, .65); w = nb.noise(160, 3, .5, vec=nb.mapping(scale=(1, 1, 8)))
    c = nb.ramp(n, [(.35, M.C('#2a1c1e')), (.55, M.C('#5a3e40')), (.7, M.C('#7a5a58'))])
    c = nb.mix(nb.mr(nb.noise(4, 5, .6, vec=nb.mapping(loc=(4, 4, 4))), .55, .62), c, M.C('#2a0a0a'))
    nb.bump(w, .3, .0008); nb.bump(n, .3, .002)
    return nb.finish(c, rough=.85, spec=.25)
L.setmat(b, screamer_skin()); db = M.NB('Screamer_Bone'); dn = db.noise(20, 6, .6)
dc = db.ramp(dn, [(.35, M.C('#4a4236')), (.6, M.C('#8a8070')), (.75, M.C('#a89e88'))])
dc = db.mix(db.mr(db.noise(6, 5, .6, vec=db.mapping(loc=(2, 5, 1))), .45, .6), dc, M.C('#2a1410'))
db.bump(dn, .4, .001); pass; 
for g in (rags, wraps): L.setmat(g, rag_mat())
cm = M.NB('Screamer_Claw'); cc = cm.ramp(cm.noise(40, 6, .6), [(.4, M.C('#0a0807')), (.7, M.C('#2c2620'))])
cm.bump(cm.noise(60, 4, .6, vec=cm.mapping(scale=(1, 1, 6))), .3, .0008)
claw_m = cm.finish(cc, rough=.3, spec=.7)
for o in claws: L.setmat(o, claw_m)
eye = M.eye_m('Screamer_Eye', iris='#e8f0ff', glow=3.5)
for k in ('eyeL', 'eyeR'):
    o = z.parts[k]; L.setmat(o, L.mat_flat('Screamer_EyeGlow', L.lin('#cfe0ff'), rough=.1, emit_s=6))
    c0 = sum((v.co for v in o.data.vertices), Vector()) / len(o.data.vertices)
    for v in o.data.vertices: v.co = c0 + (v.co - c0) * .45 + V(0, .006, 0)
tm = M.teeth_m('Screamer_Teeth')
for k in ('teethU', 'teethL'): bpy.data.objects.remove(z.parts.pop(k))
# long uneven exposed teeth along the lipless gums
tt = []
for row, bone, zz, sg in ((0, 'head', MOUTH.z + .006, -1),):
    for i in range(12):
        a = (i / 11 - .5) * 2.0
        h = .011 + rng.uniform(0, .007) - .003 * abs(a)
        pos = V(math.sin(a) * .024, MOUTH.y + .004 + (1 - math.cos(a)) * .022, zz + sg * h / 2)
        o = L.box(f'Screamer tooth{row}{i}', pos, (.0026, .0018, h / 2), C, rot=(rng.uniform(-.15, .15), 0, -a * .9), bevel=.0008)
        L.setmat(o, tm); z.bind(o, bone); tt.append(o)
L.setmat(z.parts['tongue'], M.gore('Screamer_Tongue'))

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
    if p.z < 1.55 or (p.y < -.06 and p.z < 1.68): return False
    return (p - (HC + V(0, .01, .08))).length < .2
def hlen(p, r): return r.uniform(.25, .45) * (.6 + .4 * abs(noise.noise(p * 6)))
def hflow(p): return (V(p.x * 3, .5, -1.2)).normalized()
hair = hair_cards(b, 'Screamer hair', scalp, hlen, .006, hflow, segs=10, droop=.0)
z.bind(hair, 'head')
L.setmat(hair, M.flat('Screamer_Hair', '#0e0b0c', .35))
# ---------------------------------------------------------------- pose: hunched stalk, claws raised, head thrust forward
POSE = {
    'spine05': (-4, 0, 0), 'spine04': (-6, 0, 0), 'spine03': (-8, 0, 0), 'spine02': (-8, 0, 0), 'spine01': (-6, 0, 0),
    'neck01': (-12, 0, 0), 'neck02': (-10, 0, 0), 'head': (-24, 4, 6), 'jaw': (-50, 0, 0),
    'clavicle.L': (0, 0, 8), 'upperarm01.L': (-15, 0, -42), 'lowerarm01.L': (0, 0, 25), 'wrist.L': (-30, 0, 0),
    'clavicle.R': (0, 0, -8), 'upperarm01.R': (-15, 0, 42), 'lowerarm01.R': (0, 0, -25), 'wrist.R': (-30, 0, 0),
    'upperleg01.L': (4, 0, -6), 'lowerleg01.L': (-8, 0, 0),
    'upperleg01.R': (-4, 0, 4), 'lowerleg01.R': (-4, 0, 0), 'foot.R': (6, 0, 0),
}
for sd, curl in (('L', 10), ('R', 14)):
    for f in range(2, 6):
        for k in (1, 2, 3):
            POSE[f'finger{f}-{k}.{sd}'] = (curl + random.Random(f * 5 + k).uniform(-12, 12), 0, (f - 3.5) * 4 if k == 1 else 0)
    POSE[f'finger1-2.{sd}'] = (10, 0, 0)
# elongated limbs and fingers, long neck: supernatural proportions
SCALE = {'neck01': (.85, 1.3, .85), 'lowerarm01.L': (.9, 1.15, .9), 'lowerarm01.R': (.9, 1.15, .9), 'jaw': (1.15, 1.45, 1.2),
         'lowerleg01.L': (.9, 1.1, .9), 'lowerleg01.R': (.9, 1.1, .9), 'head': (.95, 1.05, .98)}
for sd in ('L', 'R'):
    for f in range(1, 6):
        SCALE[f'finger{f}-1.{sd}'] = (.9, 1.3, .9)
for bn, sv in SCALE.items():
    z.rig.pose.bones[bn].scale = sv
z.pose_and_bake(POSE)
mz = min((o.matrix_world @ v.co).z for o in z.all_meshes() for v in list(o.data.vertices)[::5])
for o in z.all_meshes(): o.location.z -= mz; L.apply_transform(o)
# hanging shreds of dried skin and cloth all over (the silhouette that sells the rot)
hb2 = bmesh.new()
verts = []
verts += [v for v in rags.data.vertices if v.co.z > .3 and v.normal.z < .2][::3]
rng.shuffle(verts)
for v in verts[:0]:
    p = v.co.copy(); n = v.normal.copy()
    
    ln = rng.uniform(.025, .12) * (1.4 if p.z < 1.0 else 1); w = rng.uniform(.003, .011)
    side = n.cross(V(0, 0, 1)).normalized(); q = p - n * .002; prev = None
    tw = rng.uniform(-.6, .6)
    for k in range(6):
        t = k / 5; ww = w * (1 - .7 * t) + .0006
        sd_ = (side * math.cos(tw * t) + n * math.sin(tw * t)).normalized()
        pr = (hb2.verts.new(q + sd_ * ww), hb2.verts.new(q - sd_ * ww))
        if prev: hb2.faces.new((prev[0], prev[1], pr[1], pr[0]))
        prev = pr
        q = q + (V(0, 0, -1) + n * (.25 * (1 - t)) + V(rng.uniform(-.15, .15), rng.uniform(-.15, .15), 0)).normalized() * ln / 5
shreds = L.mesh_obj('Screamer shreds', hb2, C); so = shreds.modifiers.new('s', 'SOLIDIFY'); so.thickness = .0015; L.apply_all(shreds); L.smooth(shreds)
L.setmat(shreds, screamer_skin() if False else b.data.materials[0])

# ---------------------------------------------------------------- ink
eyes_c = sum((o.matrix_world @ v.co for o in (z.parts['eyeL'], z.parts['eyeR']) for v in o.data.vertices), Vector()) / (len(z.parts['eyeL'].data.vertices) * 2)
hb_ = L.hull(b, C, t=.0035)
FC = eyes_c + V(0, .0, -.035)
L.delete_faces(hb_, lambda p, n: (p - FC).length < .085 and n.y > -.2)   # no hull inside the hollow face
L.hull(rags, C, t=.003); L.hull(wraps, C, t=.0025); 
for o in claws: L.hull(o, C, t=.0015)

L.studio(sc); sc.view_settings.exposure = .0
for n in sc.world.node_tree.nodes:
    if n.type == 'BACKGROUND' and n.inputs['Color'].default_value[0] > .5: n.inputs['Color'].default_value = (*L.lin('#2a2a30'), 1)
eyes_c = sum((o.matrix_world @ v.co for o in (z.parts['eyeL'], z.parts['eyeR']) for v in o.data.vertices), Vector()) / (len(z.parts['eyeL'].data.vertices) * 2)
shots = [('front34', 25, 6, 3.4, .95, 50), ('side', 90, 4, 3.4, .95, 50), ('back34', 205, 10, 3.4, .95, 50), ('face', 15, 18, .75, None, 60)]
SAMP = int(os.environ.get('SAMP', '40')); RES = float(os.environ.get('RES', '1')); only = os.environ.get('ONLY')
for nm, az, el, dist, tz, lens in shots:
    if only and nm not in only.split(','): continue
    tgt = eyes_c + V(0, .0, -.04) if nm == 'face' else V(0, -.15, tz)
    L.camera(sc, tgt, dist, az, el, lens=lens)
    L.render(sc, f'{OUT}/{nm}.png', w=int(1080 * RES), h=int(1350 * RES), samples=SAMP)
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/screamer.blend')
