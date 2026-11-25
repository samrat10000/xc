"""STALKER: final-stage mutation. Original design: pale hunched torso, ribbed wine-dark limbs,
mantis-high elbows ending in black blade stilts, digitigrade hind blades, small hooked chest arms,
dorsal spines, long ribbed neck and an elongated skull. Realistic materials + ink hull."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import bpy, bmesh
from mathutils import Vector, noise
import castlib as L, mats as M, anatomy as A
V = A.V
OUT = os.environ.get('OUT', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out/stalker'))
os.makedirs(OUT, exist_ok=True)
M.STYLE['cavity'] = True; M.STYLE['cav_kw'] = {'dist': .05, 'strength': .55}
sc = L.reset(); C = L.collection('Stalker')
rng = random.Random(5)

# ------------------------------------------------------------------ skeleton (built posed)
sk = A.Skel(); chains = []          # chains: lists of joint names for rib arc-length
sk.add('pel', (0, .25, 1.36), (.17, .13))
A.limb(sk, 'sp', 'pel', [(0, .10, 1.56), (0, -.08, 1.76), (0, -.20, 1.90)], [(.18, .15, 1.0), (.3, .25, 1.0), (.33, .23, 1.0)], mids=1)
A.limb(sk, 'nk', 'sp2', [(0, -.31, 2.04), (0, -.42, 2.15), (0, -.52, 2.21)], [(.065, .06), (.052, .05), (.048, .046)], mids=1)
for s, sd in ((1, 'L'), (-1, 'R')):
    sk.add(f'sh{sd}', (.27 * s, -.15, 1.92), (.13, .12), 'sp2')
    A.limb(sk, f'fa{sd}', f'sh{sd}', [(.44 * s, -.36, 2.06), (.54 * s, -.62, 1.22)], [(.075, .07, 1.3), (.042, .038, 1.15)], mids=3)
    sk.add(f'hp{sd}', (.12 * s, .28, 1.31), (.085, .085), 'pel')
    A.limb(sk, f'hl{sd}', f'hp{sd}', [(.26 * s, .03, .86), (.33 * s, .36, .56)], [(.075, .07, 1.35), (.045, .042, 1.15)], mids=3)
    # small hooked chest arms
    sk.add(f'cb{sd}', (.11 * s, -.24, 1.70), (.03, .03), 'sp2')
    A.limb(sk, f'ca{sd}', f'cb{sd}', [(.17 * s, -.36, 1.55), (.09 * s, -.42, 1.63)], [(.02, .02, 1.2), (.016, .015)], mids=1)
body = L.skin_body('Stalker body', sk.j, sk.e, C, branch=.35, subdiv=2)
# heavier torso: ribcage, pecs, back muscle and belly blobs, fused with a voxel remesh (kills skin-junction artifacts)
extra = [L.blob('rc', (0, -.06, 1.74), (.24, .2, .26), C), L.blob('ab', (0, .08, 1.52), (.17, .15, .16), C),
         L.blob('bk', (0, .02, 1.86), (.27, .19, .14), C)]
for sx in (1, -1):
    extra.append(L.blob(f'pc{sx}', (.11 * sx, -.2, 1.82), (.12, .08, .1), C))
    extra.append(L.blob(f'tr{sx}', (.17 * sx, -.02, 1.98), (.14, .12, .08), C))
body = L.join([body] + extra, 'Stalker body')
rm = body.modifiers.new('rm', 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = .0055
sm = body.modifiers.new('sm', 'SMOOTH'); sm.factor = .6; sm.iterations = 6
L.apply_all(body); print("BODY VERTS", len(body.data.vertices), flush=True)

# ------------------------------------------------------------------ ribbing: displacement banded along each limb's arc length
J = {k: Vector(sk.j[i][0]) for k, i in sk.names.items()}
R_ = {k: sk.j[i][1][0] for k, i in sk.names.items()}
segs = []
for a_, b_ in sk.e:
    na = [k for k, i in sk.names.items() if i == a_][0]; nb = [k for k, i in sk.names.items() if i == b_][0]
    segs.append((na, nb))
# cumulative arc length along parent chains
arc = {'pel': 0.}
order = sorted(segs, key=lambda e: sk.names[e[1]])
for na, nb in order:
    arc[nb] = arc.get(na, 0.) + (J[nb] - J[na]).length
P = np.array([v.co[:] for v in body.data.vertices]); Nn = np.array([v.normal[:] for v in body.data.vertices])
Aa = np.array([J[a][:] for a, b in segs]); Bb = np.array([J[b][:] for a, b in segs])
AB = Bb - Aa; L2 = (AB ** 2).sum(1)
t = np.clip(((P[:, None, :] - Aa[None]) * AB[None]).sum(2) / L2[None], 0, 1)
Q = Aa[None] + t[..., None] * AB[None]
D = np.linalg.norm(P[:, None, :] - Q, axis=2)
k = D.argmin(1); tt = t[np.arange(len(P)), k]
s0 = np.array([arc.get(a, 0.) for a, b in segs]); sl = np.sqrt(L2)
S = s0[k] + tt * sl[k]
seg_names = [a + '>' + b for a, b in segs]
is_torso = np.array([('sp' in a or a == 'pel') and not b.startswith(('sh', 'hp', 'ca', 'cb')) for a, b in segs])[k]
up = Nn[:, 2]
# pale zone: top/back of torso and shoulders; ribbed elsewhere
# pale = closeness to the spine/neck axis (whole torso pale, fading into dark limbs; no hard band)
tm = np.array([('sp' in a or a in ('pel',)) and not b.startswith(('sh', 'hp', 'ca', 'cb')) for a, b in segs])
Dt = np.where(tm[None], D, 9).min(1)
pale = np.clip((.40 - Dt) / .13, 0, 1) ** 1.5 * np.clip((P[:, 2] - 1.22) / .2, 0, 1)
# exposed ribcage on the torso sides/front
side = np.clip(np.abs(Nn[:, 0]) * 1.3 + np.clip(-Nn[:, 1], 0, 1) * .6, 0, 1)
rib = (.5 + .5 * np.cos(2 * np.pi * (P[:, 2] - 1.5 + .25 * np.abs(P[:, 0])) / .05)) ** 3
ribmask = side * np.clip((P[:, 2] - 1.5) / .06, 0, 1) * np.clip((1.95 - P[:, 2]) / .06, 0, 1) * pale
period = .02
ridge = (.5 + .5 * np.cos(2 * np.pi * S / period)) ** 5
fib = np.array([noise.noise(Vector(p) * 40) for p in P])
depth = .0055 * (1 - pale) * (1 + .3 * fib)
disp = depth * ridge + .0025 * fib * pale + .007 * rib * ribmask - .004 * ribmask
for i, v in enumerate(body.data.vertices):
    v.co += v.normal * float(disp[i])
body.data.update()
# store masks for the shader: r = pale, g = ridge crest, b = limb-ness (0 torso .. 1 limb)
ca = body.data.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
for i in range(len(P)): ca.data[i].color = (float(pale[i]), float(ridge[i]), float(1 - is_torso[i]), 1)
L.smooth(body)

# ------------------------------------------------------------------ head: elongated skull, pits for eyes, lipless mouth
HC = J['nk2'] + V(0, -.09, .07)
bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=72, radius=1)
head = L.mesh_obj('Stalker head', bm, C)
def hf(p):
    x, y, z = p.x * .095, p.y * .115, p.z * .125
    q = V(x, y, z)
    if y > 0: q.y *= 1.4; q.z *= 1 + .15 * (y / .115)          # long back of skull
    if z < 0: q.x *= 1 + z / .125 * .5; q.y *= 1 - .1 * (z < -.06)
    n = q.normalized(); d = 0
    def g(c, r): return math.exp(-((q - c).length_squared) / (r * r))
    d += .01 * g(V(0, -.09, .055), .05)                           # brow dome
    for sx in (1, -1):
        d -= .042 * g(V(.031 * sx, -.104, .008), .021)           # deep eye sockets
        d += .008 * g(V(.034 * sx, -.1, .033), .014)             # brow ridge over each socket
        d -= .018 * g(V(.052 * sx, -.07, -.05), .024)            # hollow cheeks
        d += .011 * g(V(.05 * sx, -.088, -.018), .012)           # sharp cheekbones
        d -= .012 * g(V(.074 * sx, .0, .045), .03)               # sunken temples
        d -= .016 * g(V(.008 * sx, -.112, -.022), .006)          # nasal slits
        d += .006 * g(V(.03 * sx, -.09, -.08), .02)              # jaw corners
    # wide lipless mouth: a deep horizontal gash
    mo = math.exp(-((q.x / .042) ** 2 + ((q.z + .062) / .009) ** 2)) * (q.y < -.05)
    d -= .03 * mo
    # bony ridges running back over the cranium
    if q.z > .02: d += .004 * max(0, math.cos(q.x * 140)) ** 8 * min(1, (q.z - .02) * 30)
    d += .003 * noise.noise(q * 50) + .0015 * noise.noise(q * 140)
    # vertical skull ridges (veins under thin skin)
    d += .0018 * max(0, 1 - abs(noise.noise(q * 18)) * 9)
    r_ = (q + n * d) * 1.32
    return V(r_.x * .86, r_.y * 1.05, r_.z * 1.22)
L.warp(head, hf); L.smooth(head)
head.location = HC + V(0, .02, .03); head.rotation_euler = (math.radians(-14), 0, math.radians(-8))
L.apply_transform(head)
# eye glints deep in the pits + teeth
eyes = []
hm = head.matrix_world
for sx in (1, -1):
    e = L.blob(f'Stalker eye{sx}', (0, 0, 0), (.007, .007, .007), C)
    loc = HC + (V(.032 * sx, -.082, .005)); e.location = loc; e.rotation_euler = (math.radians(28), 0, 0)
    # recompute from head transform
    from mathutils import Euler, Matrix
    rot = Euler((math.radians(-14), 0, math.radians(-8))).to_matrix()
    e.location = HC + V(0, .02, .03) + rot @ V(.042 * .86 * sx, -.112 * 1.05, .007 * 1.22)
    eyes.append(e)
teeth = []
for i in range(14):
    a = (i / 13 - .5) * 1.6
    x = math.sin(a) * .05; y = -.13 + (1 - math.cos(a)) * .05
    for row, zz in ((0, -.076), (1, -.088)):
        h = .009 + rng.uniform(0, .006)
        o = L.box(f'Stalker tooth{i}{row}', (0, 0, 0), (.0028, .0022, h / 2), C, rot=(0, 0, -a * .8), bevel=.0008)
        o.location = HC + V(0, .02, .03) + rot @ V(x * .86, y * 1.05, (zz + (-h / 2 if row == 0 else h / 2)) * 1.22)
        o.rotation_euler = (math.radians(-14) + rng.uniform(-.2, .2), rng.uniform(-.2, .2), -a * .8 + math.radians(-8))
        teeth.append(o)
teeth = L.join(teeth, 'Stalker teeth')

# ------------------------------------------------------------------ blades (stilts) and dorsal spines
def blade(name, base, tip, r0, bend=V(0, 0, 0), sides=5, n=24):
    base, tip = V(base), V(tip)
    pts = []
    for i in range(n + 1):
        t = i / n
        p = base.lerp(tip, t) + bend * math.sin(t * math.pi)
        pts.append(p)
    radii = [r0 * (1 - t) ** .9 * (1 + .25 * math.exp(-((t - .06) / .05) ** 2)) + .0006 for t in [i / n for i in range(n + 1)]]
    o = L.tube(name, pts, radii, C, sides=sides)
    for p_ in o.data.polygons: p_.use_smooth = False
    return o
blades = []
for s, sd in ((1, 'L'), (-1, 'R')):
    blades.append(blade(f'Stalker foreblade{sd}', J[f'fa{sd}1'] + V(0, -.01, .03), (.62 * s, -.98, 0.0), .05, bend=V(.03 * s, -.04, 0)))
    blades.append(blade(f'Stalker hindblade{sd}', J[f'hl{sd}1'] + V(0, .0, .02), (.44 * s, .78, 0.0), .045, bend=V(.02 * s, .05, 0)))
    # elbow spur and knee spur
    blades.append(blade(f'Stalker elbowspur{sd}', J[f'fa{sd}0'], J[f'fa{sd}0'] + V(.12 * s, .05, .32), .022, sides=5, n=10))
    blades.append(blade(f'Stalker kneespur{sd}', J[f'hl{sd}0'], J[f'hl{sd}0'] + V(.04 * s, -.18, -.1), .018, sides=5, n=10))
    # chest-arm claws: three hooked fingers
    hand = J[f'ca{sd}1']
    for f in range(3):
        d0 = V((f - 1) * .012 * s, -.03, -.01)
        pts = [hand, hand + d0 + V(0, -.02, -.0), hand + d0 * 1.6 + V(0, -.035, -.03), hand + d0 * 1.8 + V(0, -.03, -.06)]
        blades.append(L.tube(f'Stalker claw{sd}{f}', pts, [.007, .006, .004, .0008], C, sides=5))
spines = []
spine_pts = [J['pel'] + V(0, .05, .0), J['sp0'], J['sp1'], J['sp2'], J['nk0'], J['nk1']]
for i in range(26):
    t = i / 25 * (len(spine_pts) - 1); a_ = int(min(t, len(spine_pts) - 2)); f = t - a_
    p = spine_pts[a_].lerp(spine_pts[a_ + 1], f)
    ok, loc, nor, _ = body.ray_cast(p + V(0, .6, .6), (p - (p + V(0, .6, .6))).normalized())
    if not ok: continue
    ln = (.08 + .2 * math.sin(i / 25 * math.pi)) * rng.uniform(.7, 1.2)
    out = (nor + V(0, .5, .2)).normalized()
    spines.append(blade(f'Stalker spine{i}', loc - nor * .01, loc + out * ln, .012 + ln * .06, bend=V(0, .015, -.01), n=8))
    # paired side spines on the shoulders
    if 9 < i < 20 and i % 2:
        for sx in (1, -1):
            q = loc + V(.05 * sx, 0, 0)
            spines.append(blade(f'Stalker sspine{i}{sx}', q, q + (out + V(.4 * sx, 0, 0)).normalized() * ln * .6, .008 + ln * .04, n=6))
blades = L.join(blades, 'Stalker blades'); spines = L.join(spines, 'Stalker spines')

# ------------------------------------------------------------------ materials (realistic)
def stalker_skin():
    b = M.NB('Stalker_Skin')
    vc = b.node('ShaderNodeVertexColor', layer_name='Mask'); sp = b.node('ShaderNodeSeparateColor'); b.link(vc.outputs['Color'], sp.inputs[0])
    pale, crest, limb = sp.outputs['Red'], sp.outputs['Green'], sp.outputs['Blue']
    n1 = b.noise(6, 8, .6); n2 = b.noise(30, 8, .65); n3 = b.noise(120, 4, .6)
    palec = b.ramp(n1, [(.35, M.C('#9e958a')), (.5, M.C('#d4ccbe')), (.65, M.C('#e8e1d3'))])
    palec = b.mix(b.math('MULTIPLY', b.mr(n2, .4, .7), .35), palec, M.C('#8a7d78'))
    # veins showing through pale skin
    vn = b.noise(10, 5, .6, dist=.8); vl = b.mr(b.math('ABSOLUTE', b.math('SUBTRACT', vn, .5)), 0, .012, 1, 0)
    palec = b.mix(b.math('MULTIPLY', vl, .6), palec, M.C('#6a4a66'))
    dark = b.ramp(n1, [(.3, M.C('#1c0b14')), (.5, M.C('#3e1528')), (.7, M.C('#5e2238'))])
    dark = b.mix(b.math('MULTIPLY', crest, .7), dark, M.C('#8a3a4e'))            # lit crests of the ribs
    dark = b.mix(b.math('MULTIPLY', limb, b.mr(n2, .45, .7)), dark, M.C('#7a1c2c'))
    # blend zone: purple bruising between pale and dark
    mid = b.mix(.5, palec, M.C('#6e5470'))
    c = b.mix(b.mr(pale, .0, .5), dark, mid); c = b.mix(b.mr(pale, .5, 1.), c, palec)
    b.bump(n3, .2, .0006); b.bump(b.noise(18, 6, .6, vec=b.mapping(scale=(1, 1, 4))), .45, .002)
    b.bump(vl, .35, .001); b.bump(b.voronoi(90), .15, .0006)
    rough = b.mr(pale, 0, 1, .32, .55)
    m = b.finish(c, sss=.08, spec=.6, rough_sock=rough)
    b.bsdf.inputs['Coat Weight'].default_value = .25
    return m
def blade_mat():
    b = M.NB('Stalker_Blade')
    sep = b.node('ShaderNodeSeparateXYZ'); b.link(b.co, sep.inputs[0])
    zf = b.mr(sep.outputs['Z'], .2, 1.2)
    c = b.mix(zf, M.C('#08060a'), M.C('#5a0f1c'))
    c = b.mix(b.math('MULTIPLY', b.mr(b.noise(25, 6, .6), .5, .7), .6), c, M.C('#1a1016'))
    b.bump(b.noise(40, 4, .5, vec=b.mapping(scale=(1, 1, 8))), .2, .001)
    m = b.finish(c, rough=.14, spec=.8, cav=False)
    b.bsdf.inputs['Coat Weight'].default_value = .8; b.bsdf.inputs['Coat Roughness'].default_value = .05
    return m
L.setmat(body, stalker_skin())
hs = M.NB('Stalker_Head')
n1 = hs.noise(7, 8, .6); hc = hs.ramp(n1, [(.35, M.C('#a59c90')), (.5, M.C('#d8d0c2')), (.65, M.C('#ece6d8'))])
vn = hs.noise(12, 5, .6, dist=.8); vl = hs.mr(hs.math('ABSOLUTE', hs.math('SUBTRACT', vn, .5)), 0, .01, 1, 0)
hc = hs.mix(hs.math('MULTIPLY', vl, .55), hc, M.C('#6a4a66'))
hs.bump(hs.noise(120, 4, .6), .2, .0006); hs.bump(vl, .35, .001); hs.bump(hs.noise(20, 6, .6, vec=hs.mapping(scale=(1, 1, 3))), .35, .0015)
L.setmat(head, hs.finish(hc, sss=.1, spec=.55, rough=.42))
L.setmat(blades, blade_mat()); L.setmat(spines, blades.data.materials[0])
L.setmat(teeth, M.teeth_m('Stalker_Teeth'))
for e in eyes: L.setmat(e, L.mat_flat('Stalker_Eye', L.lin('#ff3020'), rough=.1, emit_s=6))

# ------------------------------------------------------------------ ink outline
for o in (body, head):
    L.hull(o, C, t=.0045)
L.hull(blades, C, t=.003); L.hull(spines, C, t=.0025)

# ------------------------------------------------------------------ render (dark studio to suit the creature)
L.studio(sc); sc.view_settings.exposure = -.3
w = sc.world.node_tree.nodes
for n in w:
    if n.type == 'BACKGROUND' and n.inputs['Color'].default_value[0] > .5: n.inputs['Color'].default_value = (*L.lin('#2a2a30'), 1)
shots = [('front34', 35, 6, 4.4, 1.15, 45), ('side', 90, 4, 4.4, 1.15, 45), ('back34', 210, 12, 4.4, 1.15, 45), ('face', 25, 0, 1.2, 2.25, 70)]
SAMP = int(os.environ.get('SAMP', '40')); RES = float(os.environ.get('RES', '1'))
only = os.environ.get('ONLY')
for nm, az, el, dist, tz, lens in shots:
    if only and nm not in only.split(','): continue
    tgt = V(0, -.1, tz) if nm != 'face' else HC + V(0, -.02, -.02)
    L.camera(sc, tgt, dist, az, el, lens=lens)
    L.render(sc, f'{OUT}/{nm}.png', w=int(1080 * RES), h=int(1350 * RES), samples=SAMP)
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/stalker.blend')
