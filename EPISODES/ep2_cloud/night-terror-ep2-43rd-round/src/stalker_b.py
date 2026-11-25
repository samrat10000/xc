"""STALKER: final-stage mutation. Original design: pale hunched torso, ribbed wine-dark limbs,
mantis-high elbows ending in black blade stilts, digitigrade hind blades, small hooked chest arms,
dorsal spines, long ribbed neck and an elongated skull. Realistic materials + ink hull."""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import bpy, bmesh
from mathutils import Vector, noise
import castlib as L, mats as M, anatomy as A, skull as SK
from mathutils import Matrix, Euler
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
A.limb(sk, 'nk', 'sp2', [(0, -.31, 2.04), (0, -.42, 2.15), (0, -.52, 2.21)], [(.08, .075, 1.1), (.065, .06, 1.1), (.06, .055)], mids=1)
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
extra = [L.blob('rc', (0, -.06, 1.74), (.24, .2, .26), C), L.blob('ab', (0, .1, 1.52), (.13, .11, .15), C),
         L.blob('bk', (0, .02, 1.86), (.27, .19, .14), C)]
for sx in (1, -1):
    extra.append(L.blob(f'pc{sx}', (.11 * sx, -.2, 1.82), (.12, .08, .1), C))
    extra.append(L.blob(f'tr{sx}', (.17 * sx, -.02, 1.98), (.14, .12, .08), C))
J0 = {k: Vector(sk.j[i][0]) for k, i in sk.names.items()}
def mblob(a, b, t, r, lf, nm):
    a, b = J0[a], J0[b]; d = b - a
    return L.blob(nm, a.lerp(b, t), (r, r * .85, d.length * lf), C, rot=d.to_track_quat('Z', 'Y').to_euler())
for s_, sd in ((1, 'L'), (-1, 'R')):
    extra += [mblob(f'sh{sd}', f'fa{sd}0', .45, .08, .42, 'm1'), mblob(f'fa{sd}0', f'fa{sd}1', .2, .058, .2, 'm2'),
              mblob(f'hp{sd}', f'hl{sd}0', .42, .1, .4, 'm3'), mblob(f'hl{sd}0', f'hl{sd}1', .3, .065, .3, 'm4')]
    for a_, b_, off in ((f'fa{sd}0', f'fa{sd}1', V(.035 * s_, .02, 0)), (f'fa{sd}0', f'fa{sd}1', V(-.02 * s_, -.03, .0)),
                         (f'hl{sd}0', f'hl{sd}1', V(.0, -.045, .0)), (f'hp{sd}', f'hl{sd}0', V(.06 * s_, -.04, 0))):
        A_, B_ = J0[a_], J0[b_]
        extra.append(L.tube('cord', [A_ + off * .5, A_.lerp(B_, .5) + off, B_ + off * .3], [.016, .013, .009], C, sides=10))
    extra.append(L.tube('ncord', [V(.16 * s_, -.24, 1.9), V(.07 * s_, -.36, 2.06), V(.035 * s_, -.5, 2.17)], [.024, .02, .016], C, sides=10))
body = L.join([body] + extra, 'Stalker body')
rm = body.modifiers.new('rm', 'REMESH'); rm.mode = 'VOXEL'; rm.voxel_size = .0055
sm = body.modifiers.new('sm', 'SMOOTH'); sm.factor = .6; sm.iterations = 6
L.apply_all(body); print("BODY VERTS", len(body.data.vertices), flush=True)

# ------------------------------------------------------------------ sinew: long muscle fibres and tendon cords running ALONG each limb (no rings)
J = {k: Vector(sk.j[i][0]) for k, i in sk.names.items()}
R_ = {k: sk.j[i][1][0] for k, i in sk.names.items()}
segs = []
for a_, b_ in sk.e:
    na = [k for k, i in sk.names.items() if i == a_][0]; nb = [k for k, i in sk.names.items() if i == b_][0]
    segs.append((na, nb))
arc = {'pel': 0.}
for na, nb in sorted(segs, key=lambda e: sk.names[e[1]]):
    arc[nb] = arc.get(na, 0.) + (J[nb] - J[na]).length
P = np.array([v.co[:] for v in body.data.vertices]); Nn = np.array([v.normal[:] for v in body.data.vertices])
Aa = np.array([J[a][:] for a, b in segs]); Bb = np.array([J[b][:] for a, b in segs])
AB = Bb - Aa; L2 = (AB ** 2).sum(1); sl = np.sqrt(L2); U = AB / sl[:, None]
k = np.zeros(len(P), int); tt = np.zeros(len(P))
for c0 in range(0, len(P), 40000):
    Pc = P[c0:c0 + 40000]
    t = np.clip(((Pc[:, None, :] - Aa[None]) * AB[None]).sum(2) / L2[None], 0, 1)
    D = np.linalg.norm(Pc[:, None, :] - (Aa[None] + t[..., None] * AB[None]), axis=2)
    kk = D.argmin(1); k[c0:c0 + 40000] = kk; tt[c0:c0 + 40000] = t[np.arange(len(Pc)), kk]
S = np.array([arc.get(a, 0.) for a, b in segs])[k] + tt * sl[k]
Q = Aa[k] + tt[:, None] * AB[k]
Uk = U[k]; ref = np.where(np.abs(Uk[:, :1]) < .9, np.array([[1., 0, 0]]), np.array([[0, 1., 0]]))
e1 = np.cross(Uk, ref); e1 /= np.linalg.norm(e1, axis=1)[:, None]; e2 = np.cross(Uk, e1)
rad = P - Q; th = np.arctan2((rad * e2).sum(1), (rad * e1).sum(1))
Rseg = np.array([R_[a] for a, b in segs]); Nf = np.maximum(8, np.round(2 * np.pi * Rseg / .017))[k]
is_torso = np.array([('sp' in a or a == 'pel') and not b.startswith(('sh', 'hp', 'ca', 'cb')) for a, b in segs])[k]
fn = np.array([noise.noise(Vector(p) * 9) for p in P]); fh = np.array([noise.noise(Vector(p) * 45) for p in P])
fiber = (.5 + .5 * np.cos(Nf * th + 3. * fn + S * 2.)) ** 3
cord = (.5 + .5 * np.cos(5 * th + 1.5 * fn + 1.3)) ** 10 * (1 - is_torso)
disp = .0045 * fiber + .006 * cord + .005 * fn + .0018 * fh
for i, v in enumerate(body.data.vertices):
    v.co += v.normal * float(disp[i])
body.data.update()
# shader masks: r = tendon cord, g = fibre crest, b = limb-ness
ca = body.data.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
cols = np.stack([cord, fiber, 1 - is_torso, np.ones(len(P))], 1).astype(np.float32).ravel()
ca.data.foreach_set('color', cols)
L.smooth(body)

# ------------------------------------------------------------------ head: bare deer-style skull with huge gnarled antlers
skd = SK.build(C)
HS = 1.5; HR = Euler((math.radians(28), 0, math.radians(-6))).to_matrix()
HO = J['nk2'] - HR @ V(0, .095, -.035) * HS
HM = Matrix.Translation(HO) @ HR.to_4x4() @ Matrix.Scale(HS, 4)
for kx in ('skull', 'jaw', 'teeth', 'antlers'):
    skd[kx].matrix_world = HM; L.apply_transform(skd[kx])
skull, jaw, teeth, antlers = skd['skull'], skd['jaw'], skd['teeth'], skd['antlers']
HC = HM @ V(0, -.06, 0)
eyes = []
for sx in (1, -1):
    e = L.blob(f'Stalker eye{sx}', HM @ V(.05 * sx, -.062, .016), (.0055, .0055, .0055), C)
    eyes.append(e)
# exposed ribs wrapping the chest (bone over sinew)
tj = sorted([J[n] for n in J if n == 'pel' or (n.startswith('sp') and 'm' not in n)], key=lambda p: p.z)
def axis_at(z):
    for a_, b_ in zip(tj, tj[1:]):
        if a_.z <= z <= b_.z: return a_.lerp(b_, (z - a_.z) / (b_.z - a_.z))
    return tj[-1]
ribs = []
for i in range(7):
    z = 1.56 + i * .052
    for sx in (1, -1):
        pts = []; rr = []
        for j in range(15):
            ph = math.radians(28 + j * 9.5)
            d = V(math.sin(ph) * sx, math.cos(ph), -.35 * (j / 14)).normalized()
            c0 = axis_at(z)
            ok, loc, nor, _ = body.ray_cast(c0, d)
            if not ok: continue
            pts.append(loc + nor * .009); rr.append(.0125 * (1 - .4 * j / 14))
        if len(pts) > 3:
            ribs.append(L.tube(f'rib{i}{sx}', pts, rr, C, sides=8))
ribs = L.join(ribs, 'Stalker ribs')
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
    cord, fib, limb = sp.outputs['Red'], sp.outputs['Green'], sp.outputs['Blue']
    n1 = b.noise(5, 8, .6); n2 = b.noise(25, 8, .65); n3 = b.noise(2.5, 6, .6, vec=b.mapping(loc=(7, 3, 1)))
    c = b.ramp(n1, [(.3, M.C('#120609')), (.5, M.C('#2c0c12')), (.7, M.C('#4a1219'))])
    c = b.mix(b.math('MULTIPLY', fib, .55), c, M.C('#6e1f26'))                    # wet muscle fibre highlights
    c = b.mix(b.mr(n3, .5, .56), c, M.C('#463a3c'))                               # patches of grey dead hide
    c = b.mix(b.math('MULTIPLY', cord, .85), c, M.C('#9c8276'))                    # pale tendons
    vn = b.noise(9, 5, .6, dist=.8); vl = b.mr(b.math('ABSOLUTE', b.math('SUBTRACT', vn, .5)), 0, .014, 1, 0)
    c = b.mix(b.math('MULTIPLY', vl, .75), c, M.C('#040203'))                      # black veins
    b.bump(n2, .3, .001); b.bump(b.noise(140, 4, .6), .15, .0005); b.bump(vl, .3, .001)
    m = b.finish(c, sss=.05, spec=.45, rough_sock=b.mr(b.mr(n3, .5, .56), 0, 1, .42, .72))
    b.bsdf.inputs['Coat Weight'].default_value = .12
    return m
def antler_mat():
    b = M.NB('Stalker_Antler')
    sep = b.node('ShaderNodeSeparateXYZ'); b.link(b.co, sep.inputs[0])
    n = b.noise(30, 6, .6, vec=b.mapping(scale=(1, 1, .3)))
    c = b.ramp(n, [(.35, M.C('#120c0a')), (.6, M.C('#2e221c'))])
    c = b.mix(b.mr(sep.outputs['Z'], 2.55, 2.95), c, M.C('#8a7a64'))              # bleached tips
    b.bump(b.noise(50, 6, .6, vec=b.mapping(scale=(1, 1, .25))), .5, .002)
    return b.finish(c, rough=.55, spec=.4)
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
bonem = M.bone('Stalker_Bone')
for o in (skull, jaw, ribs): L.setmat(o, bonem)
L.setmat(antlers, antler_mat())
L.setmat(blades, blade_mat()); L.setmat(spines, blades.data.materials[0])
L.setmat(teeth, M.teeth_m('Stalker_Teeth'))
for e in eyes: L.setmat(e, L.mat_flat('Stalker_Eye', L.lin('#ff2a14'), rough=.1, emit_s=7))

# ------------------------------------------------------------------ ink outline
L.hull(body, C, t=.0045)
for o in (skull, jaw, antlers): L.hull(o, C, t=.0022)
L.hull(ribs, C, t=.002); L.hull(blades, C, t=.003); L.hull(spines, C, t=.0025)

# ------------------------------------------------------------------ render (dark studio to suit the creature)
L.studio(sc); sc.view_settings.exposure = -.3
w = sc.world.node_tree.nodes
for n in w:
    if n.type == 'BACKGROUND' and n.inputs['Color'].default_value[0] > .5: n.inputs['Color'].default_value = (*L.lin('#2a2a30'), 1)
shots = [('front34', 35, 6, 5.0, 1.35, 45), ('side', 90, 4, 5.0, 1.35, 45), ('back34', 210, 12, 5.0, 1.35, 45), ('face', 30, 8, 1.6, 2.25, 60)]
SAMP = int(os.environ.get('SAMP', '40')); RES = float(os.environ.get('RES', '1'))
only = os.environ.get('ONLY')
for nm, az, el, dist, tz, lens in shots:
    if only and nm not in only.split(','): continue
    tgt = V(0, -.1, tz) if nm != 'face' else HC
    L.camera(sc, tgt, dist, az, el, lens=lens)
    L.render(sc, f'{OUT}/{nm}.png', w=int(1080 * RES), h=int(1350 * RES), samples=SAMP)
import json
json.dump({'j': sk.j, 'e': sk.e, 'names': sk.names, 'HC': list(HC), 'eyes': [e.name for e in eyes]}, open(f'{OUT}/skel.json', 'w'))
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/stalker.blend')
