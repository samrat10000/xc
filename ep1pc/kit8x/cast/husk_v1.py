"""HUSK: mid-stage infected. Original design: a starved, charred-black body of dried sinew stretched over
bone, lipless grin, sunken pinpoint eyes, elongated hands ending in long hooked claws, rags fused into
the skin. Realistic materials + ink hull. Built on the MakeHuman CC0 base."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import bpy, bmesh
from mathutils import Vector, noise
import castlib as L, mh, mats as M
from zbuild import Char, V
OUT = os.environ.get('OUT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out/husk'))
os.makedirs(OUT, exist_ok=True)
M.STYLE['cavity'] = True; M.STYLE['cav_kw'] = {'dist': .04, 'strength': .6}
sc = L.reset(); C = L.collection('Husk')
rng = random.Random(11)
LR = ('.L', '.R')
def both(*names): return [n + s for n in names for s in LR]

z = Char('Husk', {'universal-male-young-minmuscle-minweight': 1.0}, C)
b = z.body
z.subdiv(b, 1)
EL, ER = z.j('eye.L____head'), z.j('eye.R____head')
MOUTH = z.hit(b, (0, -.5, 1.468), (0, 1, 0))[0] or V(0, -.11, 1.468)
NOSE = z.hit(b, (0, -.5, 1.515), (0, 1, 0))[0] or V(0, -.12, 1.515)
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
    if 1.05 < p.z < 1.36 and p.y < .04:
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
    # neck tendons and collarbones stand out
    if 1.36 < p.z < 1.48: d -= .005 * L.sm(.02, .045, abs(abs(p.x) - .025)) * (p.y < -.02)
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
# torn flank: hole in the right side showing ribs
FL = z.hit(b, (-.5, -.02, 1.12), (1, 0, 0))[0]
def flank(p): return (p - FL).length < .05 + .012 * noise.noise(p * 70) + .006 * noise.noise(p * 200)
def socket(p): return any((p - e).length < .016 + .003 * noise.noise(p * 250) and p.y < e.y - .004 for e in (EL, ER))
z.cut(b, lambda p: lips(p) or nose(p) or socket(p))
inner = L.blob('Husk cavity', FL + V(.055, 0, 0), (.045, .045, .06), C)
ribs = []
for k in range(4):
    zz = FL.z - .05 + k * .032
    pts = [V(FL.x + .008 + (1 - math.cos(a)) * .06, FL.y - math.sin(a) * .09 + .02, zz - abs(math.sin(a)) * .01) for a in [-.9 + i * .2 for i in range(10)]]
    ribs.append(L.tube(f'Husk rib{k}', pts, [.0065] * 10, C, sides=8))
ribs = L.join(ribs, 'Husk ribs')
for o in (inner, ribs): bpy.data.objects.remove(o)

# ---------------------------------------------------------------- hooked claws on every finger
claws = []
for sd in LR:
    for f in range(1, 6):
        h = z.j(f'finger{f}-3{sd}____head'); t = z.j(f'finger{f}-3{sd}____tail')
        d = (t - h).normalized(); ln = .075 if f > 1 else .06
        # curl direction: toward the palm (down in A-pose, roughly -Z rotated); use a perpendicular
        down = (V(0, 0, -1) - d * d.z).normalized()
        pts = [h + d * .004, t, t + d * ln * .45 + down * ln * .08, t + d * ln * .8 + down * ln * .35, t + d * ln * .95 + down * ln * .7]
        o = L.tube(f'Husk claw{sd}{f}', pts, [.0062, .0058, .0045, .0025, .0004], C, sides=8)
        z.bind(o, f'finger{f}-3{sd}'); claws.append(o)

# ---------------------------------------------------------------- rags fused into the skin
TORSO = ['spine01', 'spine02', 'spine03', 'spine04', 'spine05', 'neck01'] + both('clavicle', 'shoulder01', 'breast', 'upperarm01', 'pelvis', 'upperleg01')
def rag_keep(p): return .78 + .12 * noise.noise(p * 9) < p.z < 1.42 and (p - FL).length > .09
def rag_tear(p):
    strips = abs(math.sin(p.x * 55 + 6 * noise.noise(p * 5))) < .45 and p.z < 1.0       # hanging strips at the hem
    holes = noise.noise(p * 9 + V(2, 7, 1)) + .12 * noise.noise(p * 70) > .42
    chest = p.z > 1.08 and p.y < -.03 and abs(p.x) < .1 + .04 * noise.noise(p * 20)         # torn open over the ribs
    return strips or holes or chest
def rag_fold(p): return .004 * math.sin(p.z * 55 + 9 * noise.noise(p * 6)) + .003 * noise.noise(p * 30) + .008 * L.sm(.9, .7, p.z)
rags = z.garment('rags', TORSO, keep=rag_keep, push=.006, fold=rag_fold, ragged=True, thick=.003)
z.subdiv(rags, 2); L.delete_faces(rags, lambda p, n: rag_tear(p))
LEGW = both('upperleg01', 'upperleg02', 'lowerleg01')
def wrap_keep(p): return .3 < p.z < .55 + .05 * noise.noise(p * 20)
wraps = z.garment('legwraps', LEGW, keep=wrap_keep, push=.005, fold=lambda p: .003 * math.sin(p.z * 160 + 4 * noise.noise(p * 8)), thick=.003)
z.subdiv(wraps, 2); L.delete_faces(wraps, lambda p, n: noise.noise(p * 16) > .35)

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
def husk_skin():
    nb = M.NB('Husk_Skin')
    vc = nb.node('ShaderNodeVertexColor', layer_name='Mask'); sp = nb.node('ShaderNodeSeparateColor'); nb.link(vc.outputs['Color'], sp.inputs[0])
    cr, gr, ash = sp.outputs['Red'], sp.outputs['Green'], sp.outputs['Blue']
    n1 = nb.noise(6, 8, .6); n2 = nb.noise(30, 8, .65)
    str_ = nb.noise(14, 6, .6, vec=nb.mapping(scale=(3, 3, .5)))
    c = nb.ramp(n1, [(.3, M.C('#040303')), (.5, M.C('#0b0909')), (.7, M.C('#151110'))])
    c = nb.mix(nb.math('MULTIPLY', cr, .7), c, M.C('#3a281e'))                       # dried sinew strands catch light
    c = nb.mix(nb.math('MULTIPLY', nb.mr(str_, .52, .62), .4), c, M.C('#4a1c18'))       # raw red-brown fibre
    c = nb.mix(nb.math('MULTIPLY', gr, .9), c, M.C('#020102'))                        # tar-black grooves
    c = nb.mix(nb.math('MULTIPLY', nb.mr(ash, .35, .7), .3), c, M.C('#4e4a46'))       # ash dust
    nb.bump(n2, .35, .0012); nb.bump(nb.noise(120, 4, .6), .2, .0005); nb.bump(str_, .3, .0015)
    rough = nb.mr(gr, 0, 1, .78, .42)                                                   # wet tar in the grooves
    m = nb.finish(c, spec=.3, rough_sock=rough)
    return m
def rag_mat():
    nb = M.NB('Husk_Rags')
    n = nb.noise(10, 8, .65); w = nb.noise(160, 3, .5, vec=nb.mapping(scale=(1, 1, 8)))
    c = nb.ramp(n, [(.35, M.C('#0e0b09')), (.55, M.C('#2a231c')), (.7, M.C('#3e3428'))])
    c = nb.mix(nb.mr(nb.noise(4, 5, .6, vec=nb.mapping(loc=(4, 4, 4))), .55, .62), c, M.C('#2a0a0a'))
    nb.bump(w, .3, .0008); nb.bump(n, .3, .002)
    return nb.finish(c, rough=.85, spec=.25)
L.setmat(b, husk_skin())
for g in (rags, wraps): L.setmat(g, rag_mat())
cm = M.NB('Husk_Claw'); cc = cm.ramp(cm.noise(40, 6, .6), [(.4, M.C('#0a0807')), (.7, M.C('#2c2620'))])
cm.bump(cm.noise(60, 4, .6, vec=cm.mapping(scale=(1, 1, 6))), .3, .0008)
claw_m = cm.finish(cc, rough=.3, spec=.7)
for o in claws: L.setmat(o, claw_m)
eye = M.eye_m('Husk_Eye', iris='#e8f0ff', glow=3.5)
for k in ('eyeL', 'eyeR'):
    o = z.parts[k]; L.setmat(o, L.mat_flat('Husk_EyeGlow', L.lin('#cfe0ff'), rough=.1, emit_s=5))
    c0 = sum((v.co for v in o.data.vertices), Vector()) / len(o.data.vertices)
    for v in o.data.vertices: v.co = c0 + (v.co - c0) * .45 + V(0, .006, 0)
tm = M.teeth_m('Husk_Teeth')
for k in ('teethU', 'teethL'): L.setmat(z.parts[k], tm); z.subdiv(z.parts[k], 1)
# long uneven exposed teeth along the lipless gums
tt = []
for row, bone, zz, sg in ((0, 'head', MOUTH.z + .006, -1), (1, 'jaw', MOUTH.z - .008, 1)):
    for i in range(12):
        a = (i / 11 - .5) * 2.0
        h = .011 + rng.uniform(0, .007) - .003 * abs(a)
        pos = V(math.sin(a) * .024, MOUTH.y + .004 + (1 - math.cos(a)) * .022, zz + sg * h / 2)
        o = L.box(f'Husk tooth{row}{i}', pos, (.0026, .0018, h / 2), C, rot=(rng.uniform(-.15, .15), 0, -a * .9), bevel=.0008)
        L.setmat(o, tm); z.bind(o, bone); tt.append(o)
L.setmat(z.parts['tongue'], M.gore('Husk_Tongue'))

# ---------------------------------------------------------------- pose: hunched stalk, claws raised, head thrust forward
POSE = {
    'spine05': (8, 0, 0), 'spine04': (10, 0, -3), 'spine03': (16, 0, -3), 'spine02': (14, 0, 0), 'spine01': (6, 0, 0),
    'neck01': (-4, 0, 0), 'neck02': (-10, 0, 0), 'head': (-22, -6, 10), 'jaw': (-20, 0, -2),
    'clavicle.L': (0, 0, 10), 'upperarm01.L': (70, 0, -30), 'lowerarm01.L': (0, 0, 55), 'wrist.L': (-30, 0, 10),
    'clavicle.R': (0, 0, -6), 'upperarm01.R': (58, 0, 12), 'lowerarm01.R': (0, 0, -50), 'wrist.R': (-15, 0, 0),
    'upperleg01.L': (30, 0, -6), 'lowerleg01.L': (-40, 0, 0), 'foot.L': (10, 0, 0),
    'upperleg01.R': (-6, 0, 6), 'lowerleg01.R': (-30, 0, 0), 'foot.R': (24, 0, 0),
}
for sd, curl in (('L', 18), ('R', 30)):
    for f in range(2, 6):
        for k in (1, 2, 3):
            POSE[f'finger{f}-{k}.{sd}'] = (curl + random.Random(f * 5 + k).uniform(-12, 12), 0, (f - 3.5) * 4 if k == 1 else 0)
    POSE[f'finger1-2.{sd}'] = (10, 0, 0)
# elongated limbs and fingers, long neck: supernatural proportions
SCALE = {'neck01': (.85, 1.3, .85), 'lowerarm01.L': (.9, 1.22, .9), 'lowerarm01.R': (.9, 1.22, .9), 'upperarm01.L': (.9, 1.1, .9), 'upperarm01.R': (.9, 1.1, .9),
         'lowerleg01.L': (.9, 1.1, .9), 'lowerleg01.R': (.9, 1.1, .9), 'head': (.95, 1.05, .98)}
for sd in ('L', 'R'):
    for f in range(1, 6):
        SCALE[f'finger{f}-1.{sd}'] = (1, 1.35, 1)
for bn, sv in SCALE.items():
    z.rig.pose.bones[bn].scale = sv
z.pose_and_bake(POSE)
mz = min((o.matrix_world @ v.co).z for o in z.all_meshes() for v in list(o.data.vertices)[::5])
for o in z.all_meshes(): o.location.z -= mz; L.apply_transform(o)

# ---------------------------------------------------------------- ink
eyes_c = sum((o.matrix_world @ v.co for o in (z.parts['eyeL'], z.parts['eyeR']) for v in o.data.vertices), Vector()) / (len(z.parts['eyeL'].data.vertices) * 2)
hb_ = L.hull(b, C, t=.0035)
FC = eyes_c + V(0, .0, -.035)
L.delete_faces(hb_, lambda p, n: (p - FC).length < .085 and n.y > -.2)   # no hull inside the hollow face (flipped normals point inward); L.hull(rags, C, t=.003); L.hull(wraps, C, t=.0025)
for o in claws: L.hull(o, C, t=.0015)

L.studio(sc); sc.view_settings.exposure = .15
for n in sc.world.node_tree.nodes:
    if n.type == 'BACKGROUND' and n.inputs['Color'].default_value[0] > .5: n.inputs['Color'].default_value = (*L.lin('#2a2a30'), 1)
eyes_c = sum((o.matrix_world @ v.co for o in (z.parts['eyeL'], z.parts['eyeR']) for v in o.data.vertices), Vector()) / (len(z.parts['eyeL'].data.vertices) * 2)
shots = [('front34', 32, 6, 3.4, .95, 50), ('side', 90, 4, 3.4, .95, 50), ('back34', 205, 10, 3.4, .95, 50), ('face', 20, -8, .62, None, 70)]
SAMP = int(os.environ.get('SAMP', '40')); RES = float(os.environ.get('RES', '1')); only = os.environ.get('ONLY')
for nm, az, el, dist, tz, lens in shots:
    if only and nm not in only.split(','): continue
    tgt = eyes_c + V(0, .0, -.04) if nm == 'face' else V(0, -.15, tz)
    L.camera(sc, tgt, dist, az, el, lens=lens)
    L.render(sc, f'{OUT}/{nm}.png', w=int(1080 * RES), h=int(1350 * RES), samples=SAMP)
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/husk.blend')
