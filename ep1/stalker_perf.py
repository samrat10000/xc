"""Stalker performance for the 911 hero shot (v3).

Why v3: stalker_alive() guessed the head's front from the eye position vs the skull centre. The Stalker's deer-set eyes
sit just behind the skull's midpoint, so the guess flipped: the jaw hinge and the neck pivot landed at the SNOUT TIP and
the mouth swung open backwards. The rig already has 'head' and 'jaw' bones (jaw hinge at the back of the jaw, all head
meshes skinned to them), so v3 drives the bones directly and never re-parents meshes.

Body: v2 rotated only the last bone of each chain with one shared curve, so both blades rose and fell together like a
machine. v3 spreads every bend along the whole bendy chain (m1..m3 + main bone), gives each limb its own timing, and
runs every channel through a damped spring so parts lag, overshoot and settle (spine leads the rear-up, neck and head
follow; the head leads attention shifts and the body follows).

Rig space: the creature faces -Y. +X rotation pitches a forward-pointing bone down (jaw: opens). +Z yaw turns toward +X.
"""
import math, random
import bpy
from mathutils import Vector as V, Quaternion, Matrix


class Noise:
    def __init__(s, seed): r = random.Random(seed); s.v = [r.uniform(-1, 1) for _ in range(512)]
    def __call__(s, t):
        i = math.floor(t); f = t - i; f = f * f * (3 - 2 * f)
        return s.v[i % 512] * (1 - f) + s.v[(i + 1) % 512] * f


def curve(keys, f, ease=True):
    """piecewise smoothstep through (frame, value) keys"""
    if f <= keys[0][0]: return keys[0][1]
    for (fa, va), (fb, vb) in zip(keys, keys[1:]):
        if fa <= f <= fb:
            u = (f - fa) / max(1e-6, fb - fa)
            if ease: u = u * u * (3 - 2 * u)
            return va + (vb - va) * u
    return keys[-1][1]


def spring(sig, w=12., z=.6, sub=8):
    """critically-ish damped follower (w rad/s, z damping) over a per-frame signal: lag + overshoot + settle"""
    x = sig[0]; v = 0.; out = []; dt = 1 / 24 / sub
    for t in sig:
        for _ in range(sub):
            a = w * w * (t - x) - 2 * z * w * v; v += a * dt; x += v * dt
        out.append(x)
    return out


def car_path(keys):
    """keys from drift(): [(frame, x, y, yaw)] -> f -> world Vector (cabin height)"""
    def at(f):
        return V((curve([(k[0], k[1]) for k in keys], f), curve([(k[0], k[2]) for k in keys], f), 1.1))
    return at


def perform(root, nf, car_keys, cam_loc=(1.0, 2.4, .25), seed=911):
    rig = bpy.data.objects[root['rig']] if 'rig' in root else [o for o in root.children_recursive if o.type == 'ARMATURE'][0]
    bpy.context.view_layer.update()
    inv = rig.matrix_world.inverted()
    F = list(range(1, nf + 1))
    nz = [Noise(seed * 7 + i) for i in range(40)]
    bones = rig.pose.bones
    rest = {b.name: b.bone.matrix_local.to_quaternion() for b in bones}
    for b in bones: b.rotation_mode = 'QUATERNION'

    def chain(prefix):
        names = [prefix + f'm{i}' for i in (1, 2, 3)] + [prefix]
        return [n for n in names if n in bones]

    SPINE = [n for n in ('sp0m1', 'sp0', 'sp1m1', 'sp1', 'sp2m1', 'sp2') if n in bones]
    SPW = [.08, .10, .14, .18, .22, .28]                     # upper spine bends more
    NECK = [n for n in ('nk0m1', 'nk0', 'nk1m1', 'nk1', 'nk2m1', 'nk2') if n in bones]
    NKW = [.12, .14, .16, .18, .19, .21]

    # ---------------------------------------------------------------- attention: where the head wants to look
    car = car_path(car_keys)
    hj = V((0, -.52, 2.21))                                   # head joint, armature space
    def aim_at(pw):
        d = inv @ V(pw) - hj
        hyp = math.hypot(d.x, d.y)
        return math.degrees(math.atan2(d.x, -d.y)), math.degrees(math.atan2(-d.z, hyp)), d.y < -.15
    cam = tuple(cam_loc)
    cy, cp, _ = aim_at(cam)
    # before the car shows: stares at the lens, a curious head-tilt, then turns an ear to the engine noise behind it
    pre = [(1, cy, cp + 4, 0), (7, cy, cp + 4, 0), (9, cy + 4, cp + 2, 11), (13, cy + 4, cp + 2, 12),
           (15, cy + 30, cp - 4, -6)]
    held = None; since = 0; AY, AP, AR = [], [], []
    for f in F:
        if f <= 16:
            y, p, r = curve([(k[0], k[1]) for k in pre], f, False), curve([(k[0], k[2]) for k in pre], f, False), curve([(k[0], k[3]) for k in pre], f, False)
            y = [k for k in pre if k[0] <= f][-1][1]; p = [k for k in pre if k[0] <= f][-1][2]; r = [k for k in pre if k[0] <= f][-1][3]
            held = None
        else:
            ty, tp, front = aim_at(car(f + 2))                # leads the car slightly: a predator reads where it's going
            if not front: ty, tp = cy, cp
            ty = max(-65, min(65, ty)); tp = max(-30, min(58, tp))
            if held is None or abs(ty - held[0]) + abs(tp - held[1]) > 7 or since > 9:   # hold, then re-aim in a snap
                held = (ty, tp, 4 * nz[0](f / 13)); since = 0
            since += 1; y, p, r = held
        AY.append(y); AP.append(p); AR.append(r)

    # ---------------------------------------------------------------- the acting beats (degrees)
    L0, R0 = 60, 63                                           # left blade slams first, right 3 frames later
    spine_p = [(1, 0), (33, 0), (38, 5), (46, -12), (54, -15), (58, -17), (L0, 4), (R0 + 1, 6), (68, -2), (76, 1), (86, 0),
               (102, 0), (108, 3), (120, 1), (nf, 0)]
    spine_y = [(1, 0), (24, 0), (30, -4), (40, -2), (60, 0), (100, 0), (110, 7), (122, 11), (nf, 9)]       # body turns after the car
    spine_r = [(1, 0), (21, 0), (25, 3.5), (32, -1), (38, 0), (L0, -3), (R0, 2), (70, 0), (106, 0), (112, -3), (nf, -1)]
    # head/neck acting on top of attention (scream: neck extends, head throws up, then whips down on the slam)
    scream = [(1, 0), (34, 0), (38, 1), (44, 1), (48, 1), (82, 1), (90, 0), (nf, 0)]          # 1 = scream overrides attention
    neck_p = [(1, 0), (33, 0), (38, 9), (43, 4), (47, -14), (56, -18), (L0, -6), (R0 + 2, 10), (70, 2), (84, 0), (nf, 0)]
    head_p = [(1, 0), (34, 0), (39, 10), (44, 2), (48, -20), (57, -24), (L0 + 1, -4), (R0 + 3, 12), (72, 4), (86, 0), (nf, 0)]
    jaw = [(1, 4), (16, 4), (18, 9), (22, 6), (34, 6), (40, 16), (44, 20), (46, 50), (56, 52), (L0, 58), (R0 + 4, 46),
           (80, 40), (86, 22), (89, 25), (93, 8), (106, 6), (109, 34), (116, 30), (126, 14), (nf, 10)]
    # front blades: forward raise Fw, spread Ab, elbow fold El. The right blade paws once (weight shift) at f22-31.
    LFw = [(1, 0), (36, 0), (42, 14), (47, 30), (53, 34), (58, 40), (L0, -3), (L0 + 3, 2), (L0 + 8, 0), (112, 0), (116, 9), (121, 0), (nf, 0)]
    RFw = [(1, 0), (22, 0), (25, 13), (28, 11), (31, 0), (40, 0), (46, 12), (51, 27), (56, 30), (61, 35), (R0, -3), (R0 + 3, 2), (R0 + 9, 0), (nf, 0)]
    LAb = [(1, 0), (38, 0), (48, 16), (58, 20), (L0, 3), (L0 + 10, 0), (nf, 0)]
    RAb = [(1, 0), (22, 0), (26, 5), (31, 0), (42, 0), (52, 11), (61, 15), (R0, 2), (R0 + 10, 0), (nf, 0)]
    LEl = [(1, 0), (38, 0), (47, -24), (57, -30), (L0 - 1, -8), (L0, 4), (L0 + 6, 0), (112, 0), (116, -10), (121, 0), (nf, 0)]
    REl = [(1, 0), (22, 0), (25, -12), (29, -4), (31, 0), (42, 0), (51, -20), (60, -27), (R0 - 1, -8), (R0, 4), (R0 + 6, 0), (nf, 0)]
    # hind legs: coil before the rear-up, push through it, absorb each slam
    LCr = [(1, 0), (32, 0), (37, 7), (45, -3), (56, -4), (L0, 4), (L0 + 3, 9), (L0 + 12, 2), (84, 0), (104, 0), (108, 4), (118, 1), (nf, 0)]
    RCr = [(1, 0), (24, 2), (30, 0), (34, 0), (39, 7), (47, -3), (58, -4), (R0, 5), (R0 + 3, 8), (R0 + 12, 2), (86, 0), (nf, 0)]
    # chest hook-arms: claw open during the scream, left and right out of step
    Cla = [(1, 0), (40, 0), (46, 1), (82, 1), (90, 0), (106, 0), (109, .6), (118, .4), (128, 0), (nf, 0)]

    def sig(keys, shift=0): return [curve(keys, f - shift) for f in F]

    # breathing: irregular rhythm (rate wanders), deeper and faster after the scream
    ph = 0.; BR = []
    for f in F:
        post = curve([(1, 0), (60, 0), (66, 1), (110, .6), (nf, .5)], f)
        rate = (1 / 1.9 + .25 * nz[1](f / 30)) * (1 + .7 * post)
        ph += 2 * math.pi * rate / 24
        BR.append(math.sin(ph) * (1 + .3 * nz[2](f / 20)) * (1 + 1.2 * post) * (0 if 46 <= f <= 82 else 1))
    SCR = sig(scream)
    trem = [(1.3 * nz[3](f * .9) + .8 * nz[4](f * 1.7)) * curve([(1, 0), (45, 0), (47, 1), (84, .8), (92, 0), (nf, 0)], f) for f in F]

    # attention, distributed body -> neck -> head with different spring speeds (head snaps first, body follows)
    def mix(a, s, v): return [x * (1 - k) + v * k for x, k in zip(a, s)]
    AYs = mix(AY, SCR, 0.); APs = mix(AP, SCR, 0.); ARs = mix(AR, SCR, 0.)
    spY = spring([.15 * y for y in AYs], 5, .8); nkY = spring([.40 * y for y in AYs], 10, .65); hdY = spring([.45 * y for y in AYs], 20, .55)
    spP = spring([.10 * p for p in APs], 5, .8); nkP = spring([.35 * p for p in APs], 10, .65); hdP = spring([.55 * p for p in APs], 20, .55)
    hdR = spring(ARs, 14, .6)

    # acting channels through springs (spine slowest, extremities fastest -> overlap / follow-through)
    S_p = spring(sig(spine_p), 9, .5); S_y = spring(sig(spine_y), 6, .7); S_r = spring(sig(spine_r), 8, .55)
    N_p = spring(sig(neck_p), 12, .5); H_p = spring(sig(head_p), 16, .45)
    J = spring(sig(jaw), 34, .5)
    LF = spring(sig(LFw), 22, .45); RF = spring(sig(RFw), 21, .45); LA = spring(sig(LAb), 14, .6); RA = spring(sig(RAb), 14, .6)
    LE = spring(sig(LEl), 26, .45); RE = spring(sig(REl), 25, .45)
    LC = spring(sig(LCr), 18, .45); RC = spring(sig(RCr), 18, .45)
    CL = spring(sig(Cla), 10, .6); CR = spring(sig(Cla, 3), 10, .6)

    def setq(name, f, rots):
        pb = bones.get(name)
        if pb is None: return
        q = Quaternion()
        for ax, deg in rots:
            if deg: q = q @ Quaternion(V(ax).normalized(), math.radians(deg))
        ml = rest[name]; pb.rotation_quaternion = ml.inverted() @ q @ ml
        pb.keyframe_insert('rotation_quaternion', frame=f)

    for i, f in enumerate(F):
        t = f / 24; br = BR[i]
        # micro-life: tiny independent twitches so nothing is ever perfectly still
        tw = lambda k, a, s: a * nz[k](t * s)
        sp_pitch = S_p[i] + spP[i] + 1.4 * br
        for n, w in zip(SPINE, SPW):
            setq(n, f, [((0, 0, 1), w * (S_y[i] + spY[i])), ((1, 0, 0), w * sp_pitch), ((0, 1, 0), w * S_r[i])])
        nk_pitch = N_p[i] + nkP[i] - .6 * br + .4 * trem[i]
        for n, w in zip(NECK, NKW):
            setq(n, f, [((0, 0, 1), w * (nkY[i] + .3 * trem[i])), ((1, 0, 0), w * nk_pitch)])
        setq('head', f, [((0, 0, 1), hdY[i] + tw(5, .8, 2.3) + .7 * trem[i]), ((1, 0, 0), hdP[i] + H_p[i] + tw(6, .7, 1.9) + trem[i]),
                         ((0, 1, 0), hdR[i] + tw(7, 1.0, 1.1))])
        jv = J[i] + (2.6 * nz[8](t * 22) if J[i] > 18 else .6 * nz[8](t * 4))      # jaw shudders while it screams
        setq('jaw', f, [((1, 0, 0), max(0., jv))])
        for sd, sx, Fw, Ab, El, Cr, Cw, k0 in (('L', 1, LF, LA, LE, LC, CL, 10), ('R', -1, RF, RA, RE, RC, CR, 20)):
            # shoulder rides the breath; the blade chain bends along all four segments
            setq(f'sh{sd}', f, [((0, 1, 0), -sx * (.25 * Ab[i] + .8 * br + tw(k0, .5, .7)))])
            fw = -Fw[i] + tw(k0 + 1, .8, .5); ab = -sx * (.75 * Ab[i] + tw(k0 + 2, .6, .4))
            for n in chain(f'fa{sd}0'): setq(n, f, [((1, 0, 0), fw / 4), ((0, 1, 0), ab / 4)])
            el = El[i] + tw(k0 + 3, .8, .6)
            for n in chain(f'fa{sd}1'): setq(n, f, [((1, 0, 0), el / 4)])
            c = Cr[i] + tw(k0 + 4, .5, .45) - .4 * br
            for n in chain(f'hl{sd}0'): setq(n, f, [((1, 0, 0), c / 4)])
            for n in chain(f'hl{sd}1'): setq(n, f, [((1, 0, 0), -1.4 * c / 4)])
            # hooked chest arms: restless finger-like twitching at rest, claw wide during the scream
            sc_ = Cw[i]
            rest_tw = 5 * nz[k0 + 5](t * (1.1 + 4 * sc_)) * (1 + 2.5 * sc_)
            setq(f'ca{sd}0m1', f, [((1, .3 * sx, 0), .4 * (rest_tw - 16 * sc_))])
            setq(f'ca{sd}0', f, [((1, .3 * sx, 0), .6 * (rest_tw - 16 * sc_))])
            curl = 9 * nz[k0 + 6](t * (1.4 + 6 * sc_)) * (1 + 1.8 * sc_) - 28 * sc_
            setq(f'ca{sd}1m1', f, [((1, 0, 0), .45 * curl)])
            setq(f'ca{sd}1', f, [((1, 0, 0), .55 * curl)])

    # eyes: ignite when it notices the car, blaze through the scream and the snarl
    E_ = [(1, 30), (16, 30), (18, 110), (40, 120), (45, 230), (84, 170), (106, 150), (109, 230), (nf, 180)]
    eyes = [o for o in root.children_recursive if o.name.startswith('Stalker eye')]
    mats = []
    for o in eyes:
        for m in o.data.materials:
            if m and m not in mats: mats.append(m)
    for m in mats:
        m.use_nodes = True; b = m.node_tree.nodes.get('Principled BSDF')
        if not b: continue
        b.inputs['Emission Color'].default_value = (1., .18, .04, 1.)
        for i, f in enumerate(F):
            b.inputs['Emission Strength'].default_value = curve(E_, f, False) * (1 + .15 * nz[9](f / 24 * 9))
            b.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)
    bpy.context.view_layer.update()
    for o in eyes[:2]:
        pts = [o.matrix_world @ V(c) for c in o.bound_box]; ctr = sum(pts, V((0, 0, 0))) / 8
        pl = bpy.data.lights.new('eyeglow', 'POINT'); pl.color = (1., .2, .05); pl.shadow_soft_size = .01; pl.use_shadow = False
        po = bpy.data.objects.new('eyeglow', pl); bpy.context.scene.collection.objects.link(po)
        po.parent = rig; po.parent_type = 'BONE'; po.parent_bone = 'head'
        bpy.context.view_layer.update(); po.matrix_world = Matrix.Translation(ctr + (rig.matrix_world.to_quaternion() @ V((0, -.03, 0))))
        for f in F: pl.energy = .6 * curve(E_, f, False) / 40; pl.keyframe_insert('energy', frame=f)
    em = bpy.data.objects.get('ember')
    if em:
        for f in F: em.data.energy = 12 + 18 * min(1., curve(E_, f, False) / 120); em.data.keyframe_insert('energy', frame=f)
    return rig, (L0, R0)
