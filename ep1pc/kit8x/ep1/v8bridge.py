# v8 bridge: the TEASER Stalker (model v5 + its living motion), ported verbatim from teaser/blender/teaser_v4.py and shots2_v3.py (T13.6)
R = random.Random(11)
def stalker_alive(st, nf, mode='wide'):
    """bring the Stalker to life: the skull+antlers turn on a neck pivot (predator stillness, then sharp re-aims),
    the jaw hinges open, the eyes ignite. mode 'wide' (cut20, scanning) or 'close' (cut21, locks on and opens up)."""
    import mathutils
    bpy.context.view_layer.update()
    kids = {o.name: o for o in st.children_recursive}
    def g(k): return [o for n, o in kids.items() if n.startswith('Stalker ' + k)]
    head_objs = g('skull') + g('antlers') + g('eye') + g('teeth')
    jaw_objs = g('jaw')
    inv = st.matrix_world.inverted()
    def bbl(objs):
        pts = [inv @ (o.matrix_world @ mathutils.Vector(c)) for o in objs for c in o.bound_box]
        mn = mathutils.Vector([min(p[i] for p in pts) for i in range(3)]); mx = mathutils.Vector([max(p[i] for p in pts) for i in range(3)])
        return mn, mx
    smn, smx = bbl(g('skull')); emn, emx = bbl(g('eye')); jmn, jmx = bbl(jaw_objs)
    sc_ = (smn + smx) / 2; front = 1 if (emn.y + emx.y) / 2 > sc_.y else -1
    rigs = [o for o in st.children_recursive if o.type == 'ARMATURE' and 'jaw' in o.data.bones]
    hinge = None
    if rigs:   # the rig knows where the jaw hinges and which way the snout points (the eye-vs-centre guess fails on the long bull skull)
        jb = rigs[0].data.bones['jaw']; hh = inv @ (rigs[0].matrix_world @ jb.head_local); ht = inv @ (rigs[0].matrix_world @ jb.tail_local)
        front = 1 if ht.y > hh.y else -1; hinge = hh
    def pivot(name, loc, parent):
        e = bpy.data.objects.new(name, None); col.objects.link(e); e.parent = st; e.location = loc
        bpy.context.view_layer.update()
        if parent is not st:
            mw = e.matrix_world.copy(); e.parent = parent; e.matrix_world = mw
        bpy.context.view_layer.update(); return e
    neck = pivot('neckpv', mathutils.Vector((sc_.x, sc_.y - front * (smx.y - smn.y) * .35, smn.z + .03)), st)
    hinge_y = jmx.y if front < 0 else jmn.y
    hloc = mathutils.Vector(((jmn.x + jmx.x) / 2, hinge.y, hinge.z)) if hinge is not None else mathutils.Vector(((jmn.x + jmx.x) / 2, hinge_y, jmx.z - .02))
    jaw = pivot('jawpv', hloc, neck)
    for o in head_objs:
        mw = o.matrix_world.copy(); o.parent = neck; o.matrix_world = mw
    for o in jaw_objs:
        mw = o.matrix_world.copy(); o.parent = jaw; o.matrix_world = mw
    # eyes: emissive, animated strength
    eyem = []
    for o in g('eye'):
        for m in o.data.materials:
            if m and m not in eyem: eyem.append(m)
    for m in eyem:
        m.use_nodes = True; b = m.node_tree.nodes.get('Principled BSDF')
        if b: b.inputs['Emission Color'].default_value = (1., .18, .04, 1.)
    nz = [A.Noise(70 + i) for i in range(4)]
    for o in (neck, jaw): o.rotation_mode = 'XYZ'
    # head keys: (frame, yaw deg, pitch deg (down +), roll deg); held between keys, snapped quickly (predator re-aims)
    if mode == 'wide':
        K_ = [(1, -18, 4, 0), (16, -18, 4, 0), (19, 14, -2, 6), (40, 14, -2, 6), (42, 2, 12, -4), (60, 2, 12, -4), (63, -6, 18, 10), (nf, -6, 18, 10)]
        J_ = [(1, 4), (44, 4), (50, 22), (58, 6), (nf, 6)]
        E_ = [(1, 6), (18, 6), (19, 40), (24, 14), (62, 14), (63, 60), (nf, 30)]
    elif mode == 'scream':     # locks eyes on us, mouth hanging open -> rears its head to the sky -> screams
        K_ = [(1, 6, 8, 4), (5, 0, 10, 0), (21, 0, 11, -3), (24, 2, 6, 0), (30, 0, 2, 2), (nf, 0, 0, 0)]   # head thrusts up and at us, face stays readable (it used to point at the sky once the hinge was fixed)
        J_ = [(1, 8), (6, 20), (21, 24), (25, 10), (30, 52), (nf, 54)]
        E_ = [(1, 30), (4, 140), (21, 120), (29, 120), (30, 220), (nf, 180)]
    else:
        K_ = [(1, 22, 2, 8), (9, 22, 2, 8), (12, -4, 6, -6), (22, -4, 8, -14), (28, 0, 16, -4), (nf, 0, 26, 0)]
        J_ = [(1, 3), (12, 3), (16, 12), (24, 20), (29, 30), (33, 44), (nf, 46)]
        E_ = [(1, 4), (11, 4), (12, 120), (15, 45), (27, 45), (30, 160), (nf, 120)]
    def interp(keys, f, snap=4):
        for a, b in zip(keys, keys[1:]):
            if a[0] <= f <= b[0]:
                span = b[0] - a[0]; u = min(1., (f - a[0]) / max(1, min(span, snap)))
                u = u * u * (3 - 2 * u)
                return [x + (y - x) * u for x, y in zip(a[1:], b[1:])]
        return list(keys[-1][1:])
    for f in range(1, nf + 1):
        tt = f / 24
        yaw, pit, rol = interp(K_, f)
        jit = 1.2 * (abs(nz[0](tt * 3)) > .55) * nz[1](tt * 25)          # tiny insect micro-twitches
        if mode == 'scream' and f >= 30: jit = 1.6 * nz[1](tt * 30)       # whole head trembles with the scream
        neck.rotation_euler = (math.radians(-front * (pit + .8 * nz[2](tt * .7)) + jit), math.radians(rol), math.radians(yaw + jit))
        neck.keyframe_insert('rotation_euler', frame=f)
        (jo,) = interp(J_, f, snap=6)
        jaw.rotation_euler = (math.radians(front * -(jo + ((3.5 if mode == 'scream' else 1.5) * nz[3](tt * 18) if jo > 15 else 0))), 0, 0)
        jaw.keyframe_insert('rotation_euler', frame=f)
        (ev,) = interp(E_, f, snap=2)
        for m in eyem:
            b = m.node_tree.nodes.get('Principled BSDF')
            if b: b.inputs['Emission Strength'].default_value = ev * (1 + .15 * nz[0](tt * 9)); b.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)
    for o in g('eye')[:2]:
        pl = bpy.data.lights.new('eyeglow', 'POINT'); pl.color = (1., .2, .05); pl.shadow_soft_size = .01; pl.use_shadow = False
        po = bpy.data.objects.new('eyeglow', pl); col.objects.link(po); po.parent = neck
        mnE, mxE = bbl([o]); po.matrix_world = st.matrix_world @ mathutils.Matrix.Translation((mnE + mxE) / 2 + mathutils.Vector((0, front * .03, 0)))
        for f in range(1, nf + 1):
            (ev,) = interp(E_, f, snap=2); pl.energy = .6 * ev / 40; pl.keyframe_insert('energy', frame=f)
    em = bpy.data.objects.get('ember')
    if em:
        for f in range(1, nf + 1):
            (ev,) = interp(E_, f, snap=2); em.data.energy = 12 + 18 * min(1., ev / 120); em.data.keyframe_insert('energy', frame=f)
    return neck, jaw

def drift(car, keys):
    """keys: [(frame, x, y, yaw_deg)] smooth path; returns travelled distance"""
    d = 0.; prev = None
    for f, x, y, yaw in keys:
        key(car, f, loc=V((x, y, 0)), rot=(0, 0, math.radians(yaw)))
        if prev: d += math.hypot(x - prev[0], y - prev[1])
        prev = (x, y)
    return d

def wheels(parts):
    return [o for o in parts if o.name.endswith('wheel assembly')]

def wpos(o): bpy.context.view_layer.update(); return o.matrix_world.translation.copy()

_drop_mesh = None
def particles(n, birth, pos_fn, vel_fn, life=14, size=.012, mat=None, grav=9.8, tumble=False, shape='drop'):
    """cheap ballistic particles (spray, glass, debris): linked-duplicate objects keyed every 2 frames, scale 0 before birth/after death"""
    global _drop_mesh
    import bmesh
    if shape == 'drop':
        if _drop_mesh is None:
            _drop_mesh = bpy.data.meshes.new('drop'); bm = bmesh.new(); bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1); bm.to_mesh(_drop_mesh)
            wm = bpy.data.materials.new('Water'); wm.use_nodes = True; b = wm.node_tree.nodes['Principled BSDF']
            b.inputs['Base Color'].default_value = (.8, .85, .9, 1); b.inputs['Roughness'].default_value = .05
            b.inputs['Transmission Weight'].default_value = 1.; b.inputs['IOR'].default_value = 1.33; _drop_mesh.materials.append(wm)
        me = _drop_mesh
    else:
        me = bpy.data.meshes.new(shape); bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bm.to_mesh(me)
        if mat: me.materials.append(mat)
    objs = []
    for i in range(n):
        f0 = birth(i); p0 = V(pos_fn(i)); v0 = V(vel_fn(i))
        o = bpy.data.objects.new(f'pt{i}', me); col.objects.link(o)
        s = size * R.uniform(.5, 1.4)
        sc3 = (s, s, s * (2.5 if shape == 'drop' else .15))
        o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=f0 - 1)
        rot0 = V((R.uniform(0, 6), R.uniform(0, 6), R.uniform(0, 6))); w = V((R.uniform(-9, 9), R.uniform(-9, 9), R.uniform(-9, 9)))
        for k in range(0, life + 1, 2):
            t = k / 24; p = p0 + v0 * t + V((0, 0, -.5 * grav * t * t))
            if p.z < 0: p.z = .005
            o.location = p; o.keyframe_insert('location', frame=f0 + k)
            o.scale = sc3; o.keyframe_insert('scale', frame=f0 + k)
            if tumble: o.rotation_euler = rot0 + w * t; o.keyframe_insert('rotation_euler', frame=f0 + k)
        o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=f0 + life + 1)
        for fc in _fcurves(o.animation_data.action):
            if fc.data_path == 'scale':
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
        o.cycles.use_motion_blur = True
        objs.append(o)
    return objs

def spray(wheel, f0, f1, per=10, back=(0, 1, 0), speed=6., up=2.2, size=.012):
    """water thrown off a tyre: sampled at the wheel each frame, flung backward/outward"""
    pts = []
    for f in range(f0, f1 + 1):
        sc.frame_set(f); p = wpos(wheel); bk = wheel.matrix_world.to_quaternion() @ V(back)
        for _ in range(per): pts.append((f, p.copy(), bk.copy()))
    return particles(len(pts), lambda i: pts[i][0],
                     lambda i: pts[i][1] + V((R.uniform(-.25, .25), R.uniform(-.2, .2), R.uniform(-.25, .05))),
                     lambda i: pts[i][2] * speed * R.uniform(.5, 1.2) + V((R.uniform(-1.5, 1.5), R.uniform(-1, 1), up * R.uniform(.3, 1.3))),
                     life=12, size=size)

def glass_mat():
    m = bpy.data.materials.new('Shard'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (.7, .78, .85, 1); b.inputs['Roughness'].default_value = .02
    b.inputs['Transmission Weight'].default_value = .9; b.inputs['IOR'].default_value = 1.5
    return m

def backlight(loc, tgt, energy, size, color=(.75, .85, 1.0), name='backlight'):
    """area light behind a subject aimed back at the lens: lights the fog so the subject reads as a silhouette"""
    ld = bpy.data.lights.new(name, 'AREA'); ld.energy = energy; ld.size = size; ld.color = color
    lo = bpy.data.objects.new(name, ld); sc.collection.objects.link(lo); lo.location = V(loc)
    lo.rotation_euler = (V(tgt) - V(loc)).to_track_quat('-Z', 'Y').to_euler(); lo.visible_camera = False
    return lo

def flash_light(lo, f_hits, base, peak):
    lo.data.energy = base; lo.data.keyframe_insert('energy', frame=0)
    for fh in f_hits:
        for df, v in ((-1, base), (0, peak), (1, peak * .3), (2, peak * .8), (5, base)):
            lo.data.energy = v; lo.data.keyframe_insert('energy', frame=fh + df)

def glass_rain(n, f0, f1, x_rng, y_rng, z_rng, vel=(0, 0, 0), size=.12):
    gm = glass_mat()
    return particles(n, lambda i: R.randint(f0, f1), lambda i: (R.uniform(*x_rng), R.uniform(*y_rng), R.uniform(*z_rng)),
                     lambda i: (vel[0] * R.uniform(.3, 1.2), vel[1] + R.uniform(-.5, .5), vel[2] + R.uniform(-1, 1)),
                     life=40, size=size, mat=gm, tumble=True, shape='shard')

def shift_keys(df, objs):
    """push every keyframe of these datablocks df frames later (used to time stalker_alive's scream)"""
    for ob in objs:
        ad = getattr(ob, 'animation_data', None)
        if not ad or not ad.action: continue
        for fc in _fcurves(ad.action):
            for kp in reversed(fc.keyframe_points):
                kp.co.x += df; kp.handle_left.x += df; kp.handle_right.x += df

def giant(loc, rot_deg, scale=4.3):
    g = K.char('stalker', V(loc), math.radians(rot_deg)); g.scale = (scale,) * 3
    return g

def eye_world(g):
    bpy.context.view_layer.update()
    eyes = [o for o in g.children_recursive if o.name.startswith('Stalker eye')]
    pts = [o.matrix_world @ V(c) for o in eyes for c in o.bound_box]
    return sum(pts, V((0, 0, 0))) / len(pts), eyes

def wet_eye(eyes, emit=2.5):
    for o in eyes:
        for m in o.data.materials:
            if not m: continue
            m.use_nodes = True; b = m.node_tree.nodes.get('Principled BSDF')
            if b:
                b.inputs['Roughness'].default_value = .04; b.inputs['Coat Weight'].default_value = 1.; b.inputs['Coat Roughness'].default_value = .02
                b.inputs['Emission Color'].default_value = (1., .16, .04, 1); b.inputs['Emission Strength'].default_value = emit

def camlight(c, energy=500, size=60, colr='#e6ecff'):
    sp = bpy.data.lights.new('camlight', 'SPOT'); sp.energy = energy; sp.color = K.C(colr); sp.spot_size = math.radians(size); sp.spot_blend = .9
    so = bpy.data.objects.new('camlight', sp); col.objects.link(so); so.parent = c; so.location = (.05, -.05, 0)
    return sp

def eye_saccades(eyes, keys, front, seed=910):
    """eyeballs dart like a real eye: hold a fixation, snap to the next in ~2 frames with a small overshoot, micro-tremor
    while holding. keys: [(frame, yaw deg, pitch deg)]. Each eye turns about its own centre (origin is off-centre, so via a pivot)."""
    from mathutils import Quaternion, Matrix
    nz = [A.Noise(seed + i) for i in range(2)]
    up = V((0, 0, 1)); side = up.cross(V(front)).normalized()
    nf_ = keys[-1][0]
    def at(f):
        for (fa, ya, pa), (fb, yb, pb) in zip(keys, keys[1:]):
            if fa <= f <= fb:
                u = min(1., (f - fa) / 2.)                                   # saccade lasts ~2 frames
                k = 1 - (1 - u) ** 3 + (.12 * math.sin(math.pi * min(1., (f - fa) / 4.)) if f - fa <= 4 and fb - fa > 4 else 0)
                return ya + (yb - ya) * k, pa + (pb - pa) * k
        return keys[-1][1], keys[-1][2]
    bpy.context.view_layer.update()
    for o in eyes:
        c = sum((o.matrix_world @ V(b) for b in o.bound_box), V((0, 0, 0))) / 8
        pv = bpy.data.objects.new(f'{o.name} pivot', None); col.objects.link(pv)
        pv.parent = o.parent; pv.matrix_world = Matrix.Translation(c); bpy.context.view_layer.update()
        mw = o.matrix_world.copy(); o.parent = pv; o.matrix_world = mw
        pv.rotation_mode = 'QUATERNION'; base = pv.matrix_world.copy()
        for f in range(1, nf_ + 1):
            tt = f / 24; y, p = at(f)
            y += .5 * nz[0](tt * 14); p += .4 * nz[1](tt * 16)                # fixation tremor
            q = Quaternion(up, math.radians(y)) @ Quaternion(side, math.radians(p))
            pv.matrix_world = Matrix.Translation(c) @ q.to_matrix().to_4x4() @ Matrix.Translation(-c) @ base
            pv.keyframe_insert('location', frame=f); pv.keyframe_insert('rotation_quaternion', frame=f)

def stalker_body(sg, nf, slam=60):
    """a living creature, not a machine (Sam 2026-11-22): never mirrored, the head leads and the body follows, every limb
    bends along its whole segment chain with follow-through (spring lag that grows toward the tip), the weight shifts
    between the stilts, the two front stilts rise at different times and heights and slam down one after the other,
    raised limbs tremble under the strain, the hind legs take each impact."""
    from mathutils import Quaternion
    rig = bpy.data.objects[sg['rig']] if 'rig' in sg else [o for o in sg.children_recursive if o.type == 'ARMATURE'][0]
    nzs = [A.Noise(300 + i) for i in range(24)]
    N = nf + 1
    def curve(keys):
        out = [0.] * N
        for f in range(N):
            if f <= keys[0][0]: out[f] = keys[0][1]; continue
            out[f] = keys[-1][1]
            for (fa, va), (fb, vb) in zip(keys, keys[1:]):
                if fa <= f <= fb: u = (f - fa) / max(1, fb - fa); u = u * u * (3 - 2 * u); out[f] = va + (vb - va) * u; break
        return out
    def spring(sig, hz, zeta=.5):
        """second-order follow: lags, overshoots on hard stops, settles (overlap and follow-through)"""
        w = 2 * math.pi * hz; x, v = sig[0], 0.; out = []; sub = 8; dt = 1 / 24 / sub
        for t in sig:
            for _ in range(sub):
                a = w * w * (t - x) - 2 * zeta * w * v; v += a * dt; x += v * dt
            out.append(x)
        return out
    keyed = {}
    def acc(bn, ax, arr):
        if rig.pose.bones.get(bn) is None: return
        keyed.setdefault(bn, []).append((V(ax).normalized(), arr))
    def chain(bones, ax, sig, hz0, hz_step=.55, zeta=.48, w=None):
        """spread one motion along a limb chain: each segment takes a share and lags a bit more than the one before"""
        w = w or [1. / len(bones)] * len(bones)
        hz = hz0
        for bn, wk in zip(bones, w):
            sp = spring(sig, hz, zeta); acc(bn, ax, [wk * x for x in sp]); hz *= hz_step if hz_step < 1 else 1
    def seg(side, part):
        base = f'{part}{side}'
        return [base + 'm1', base + 'm2', base + 'm3', base] if rig.pose.bones.get(base + 'm1') else [base]
    tt = [f / 24 for f in range(N)]
    S0 = slam - 30
    # ---- spine: slow heavy breathing (not a sine metronome: noise-modulated rate), rear-up led by the neck, compression on impacts
    breath = [1.4 * math.sin(2 * math.pi * (t / 1.7 + .12 * nzs[0](t * .3))) * (1 if f < S0 else 1.7) for f, t in enumerate(tt)]
    rear = curve([(1, 0), (S0 - 2, 0), (S0 + 8, -5), (S0 + 18, -10), (slam - 3, -11), (slam, -6), (slam + 4, 1.5), (slam + 8, -3), (slam + 20, -1), (nf, -1)])
    for k, bn in enumerate(['sp0', 'sp1', 'sp2', 'nk0', 'nk1']):      # wave travels from the neck back down the spine
        lag = (4 - k) * 2
        sig = [(.25 + .15 * k) * breath[max(0, f - lag)] + (.12 + .05 * k) * (1 if k < 3 else -.6) * rear[max(0, f - lag)] for f in range(N)]   # the neck counters the rear-up so the face stays on the car
        acc(bn, (1, 0, 0), spring(sig, 2.2 + .3 * k, .55))
    # weight shift: the body leans onto one stilt, then the other (root roll), the feet stay planted (hips counter)
    lean = curve([(1, -1.2), (14, -1.6), (26, 1.4), (S0 + 10, .4), (slam - 2, -2.0), (slam + 3, 1.8), (slam + 12, -.6), (90, .8), (115, -.8), (nf, .3)])
    lean = [l + .4 * nzs[1](t * .6) for l, t in zip(lean, tt)]
    acc('root', (0, 1, 0), spring(lean, 1.1, .7))
    for sd, sx in (('L', 1), ('R', -1)): acc(f'hp{sd}', (0, 1, 0), [-x for x in spring(lean, 1.1, .7)])
    # ---- front blade-stilts: LEFT leads (big, wide, reaching), RIGHT follows late (lower, tighter), slams staggered L then R
    plans = {'L': dict(up0=S0 + 3, peak=S0 + 19, hi=13, fwd=-30, down=slam, step=(8, 19)),      # the claws rise IN FRONT of the body, toward the lens
             'R': dict(up0=S0 + 10, peak=S0 + 25, hi=8, fwd=-21, down=slam + 5, step=(4, 13))}
    for sd, sx in (('L', 1), ('R', -1)):
        P = plans[sd]; u0, pk, dn = P['up0'], P['peak'], P['down']
        # a creeping step before the scream: lift a few degrees, re-plant
        st0, st1 = P['step']
        stepk = [(1, 0), (st0, 0), (st0 + 3, 5), (st1 - 3, 3), (st1, 0)]
        lift = curve(stepk + [(u0, 0), (u0 + 6, P['hi'] * .55), (pk, P['hi']), (dn - 10, P['hi'] * 1.1), (dn - 5, P['hi'] * .6), (dn - 2, P['hi'] * .15), (dn, -3.), (dn + 4, .8), (dn + 9, 0), (nf, 0)])
        reach = curve([(1, 0), (u0 + 2, 0), (pk, P['fwd']), (dn - 10, P['fwd'] * 1.35), (dn - 4, P['fwd'] * .9), (dn - 1, P['fwd'] * .35), (dn, 2), (dn + 5, 0), (nf, 0)])
        strain = [1 if u0 + 6 < f < dn - 2 else 0 for f in range(N)]
        trem = [1.3 * strain[f] * nzs[2 + (sx > 0)](t * 9) for f, t in enumerate(tt)]
        drift_ = [.9 * nzs[4 + (sx > 0)](t * .45) for t in tt]           # never perfectly still
        sh = [(-sx) * (.3 * l) for l in lift]
        acc(f'sh{sd}', (0, 1, 0), spring(sh, 2.6, .5))
        chain(seg(sd, 'fa') [:4], (0, 1, 0), [(-sx) * (l + t_ + d) for l, t_, d in zip(lift, trem, drift_)], 3.4, .85, .45, [.4, .3, .2, .1])
        chain(seg(sd, 'fa')[:4], (1, 0, 0), reach, 3.0, .85, .45, [.4, .3, .2, .1])
        # the lower blade folds in as it rises (like a mantis rearing), whips straight on the way down
        fold = curve([(1, 0), (u0 + 2, 0), (u0 + 9, -12 if sd == 'L' else -8), (pk + 3, -6), (dn - 6, -3), (dn - 1, 3), (dn + 3, -2), (dn + 10, 0), (nf, 0)])
        fold = [x + 1.5 * nzs[6 + (sx > 0)](t * .7) for x, t in zip(fold, tt)]
        b1 = [f'fa{sd}1m1', f'fa{sd}1m2', f'fa{sd}1m3', f'fa{sd}1']
        chain(b1, (1, 0, 0), fold, 2.6, .8, .42, [.35, .3, .2, .15])
        # late in the shot one blade drags and scrapes forward (R only), the other just twitches
        if sd == 'R':
            scrape = curve([(1, 0), (96, 0), (104, -7), (112, -5), (120, 0), (nf, 0)])
            chain(b1, (1, 0, 0), scrape, 1.6, .9, .6, [.2, .3, .3, .2])
        # ---- hands (v4 rig): limp droop as the hand leaves the road, claws splay and reach at the top with trembling
        # fingers, spread wide on the way down, then dig in and grip on the impact; idle fingers tap one at a time
        if rig.pose.bones.get(f'hd{sd}'):
            sgn = lambda f_: 1 if f_ else 0
            wrist = curve([(1, 0), (u0, 0), (u0 + 4, 10), (u0 + 10, 26), (pk, -12), (dn - 10, -18), (dn - 4, -6), (dn - 1, -10), (dn, 4), (dn + 4, -2), (dn + 10, 0), (nf, 0)])
            wrist = [w_ + 2.2 * strain[f] * nzs[14 + (sx > 0)](tt[f] * 7) for f, w_ in enumerate(wrist)]
            chain([f'wa{sd}', f'hd{sd}'], (1, 0, 0), wrist, 3.2, .9, .45, [.35, .65])
            curl0 = curve([(1, 0), (u0, 0), (u0 + 5, 34), (u0 + 12, 42), (pk - 2, -14), (dn - 10, -22), (dn - 4, -26), (dn - 1, -18), (dn, 8), (dn + 3, 30), (dn + 8, 18), (dn + 16, 12), (nf, 12)])
            splay = curve([(1, 0), (u0 + 6, -4), (pk - 2, 14), (dn - 10, 18), (dn - 2, 20), (dn, 12), (dn + 6, 6), (nf, 6)])
            # late in the shot: the planted hand slowly clenches on the asphalt during the scream, claws scraping
            clench = curve([(1, 0), (dn + 20, 0), (dn + 32, 16 if sd == 'L' else 10), (dn + 46, 4), (dn + 60, 14 if sd == 'L' else 20), (nf, 8)])
            for k in range(5):
                bb = rig.data.bones.get(f'fi{sd}{k}0')
                if bb is None: continue
                d = (bb.tail_local - bb.head_local); d.z = 0; d.normalize()
                cax = V((0, 0, 1)).cross(d)                                   # curl axis: tip goes down/in
                ph = 1.7 * k + (0 if sd == 'L' else 4.1)
                lag = k * 1.2 + (0 if sd == 'L' else .6)                       # fingers close one after another, not as a block
                # idle tapping: each finger lifts and taps at its own time before the scream
                tap = [0.] * N
                for t0 in (R_tap := [6 + 5 * k + (3 if sd == 'R' else 0), 17 + 3 * ((k * 7) % 5) + (2 if sd == 'R' else 0)]):
                    for f in range(N):
                        x = (f - t0) / 2.5
                        if -1 < x < 2: tap[f] += -14 * math.exp(-x * x) if t0 < u0 else 0
                trem = [3.2 * strain[f] * nzs[16 + (k % 4)](tt[f] * 8 + ph) for f in range(N)]
                base = [curl0[max(0, int(f - lag))] + tap[f] + trem[f] + clench[f] * (1 + .2 * k) for f in range(N)]
                if k == 4: base = [.7 * x for x in base]                         # the thumb moves less
                chain([f'fi{sd}{k}0', f'fi{sd}{k}1', f'fi{sd}{k}2'], tuple(cax), base, 5.0, .8, .4, [.3, .36, .34])
                so = (k - 1.5) / 1.5 * (1 if k < 4 else -1)                     # outer fingers spread most
                acc(f'fi{sd}{k}0', (0, 0, 1), spring([sx * so * x for x in splay], 4.0, .5))
        if rig.pose.bones.get(f'hc{sd}'):
            crh = curve([(1, 0), (dn - 2, 0), (dn + 2, 6), (dn + 10, 2.5), (dn + 26, .8), (nf, .5)])
            acc(f'hc{sd}', (1, 0, 0), spring([.6 * c for c in crh], 3.0, .5)); acc(f'hv{sd}', (1, 0, 0), spring([-.9 * c for c in crh], 3.0, .5))
        # hind legs: crouch hardest on their own side's impact, small idle shifts
        cr = curve([(1, 0), (dn - 2, 0), (dn + 2, 6), (dn + 10, 2.5), (dn + 26, .8), (nf, .5)])
        cr = [c + .6 * nzs[8 + (sx > 0)](t * .5) for c, t in zip(cr, tt)]
        chain(seg(sd, 'hl')[:4], (1, 0, 0), cr, 3.0, .9, .5)
        chain([f'hl{sd}1m1', f'hl{sd}1m2', f'hl{sd}1m3', f'hl{sd}1'], (1, 0, 0), [-1.5 * c for c in cr], 3.0, .9, .5)
        # hooked chest arms: they never move together (different rhythm per side), clench in the scream, claw at the air
        scr = curve([(1, 0), (S0 + 6, 0), (S0 + 12, 1), (slam + 40, 1), (slam + 55, .3), (nf, .3)])
        rate = 1.0 if sd == 'L' else 1.37
        ca0 = [6 * nzs[10 + (sx > 0)](t * rate * (1 + 4 * s)) * (1 + 2.5 * s) - 16 * s for t, s in zip(tt, scr)]
        ca1 = [10 * nzs[12 + (sx > 0)](t * rate * 1.3 * (1 + 5 * s)) * (1 + 2 * s) - 28 * s for t, s in zip(tt, scr)]
        chain([f'ca{sd}0m1', f'ca{sd}0'], (1, .3 * sx, 0), ca0, 4.0, .85, .4, [.5, .5])
        chain([f'ca{sd}1m1', f'ca{sd}1'], (1, 0, 0), ca1, 4.5, .85, .4, [.5, .5])
    for bn, parts in keyed.items():
        pb = rig.pose.bones[bn]; pb.rotation_mode = 'QUATERNION'; ml = pb.bone.matrix_local.to_quaternion()
        for f in range(1, N):
            q = Quaternion((1, 0, 0, 0))
            for ax, arr in parts: q = Quaternion(ax, math.radians(arr[f])) @ q
            pb.rotation_quaternion = ml.inverted() @ q @ ml; pb.keyframe_insert('rotation_quaternion', frame=f)
    return rig

def eye_scale(sg, k=.03):
    """stalker_alive keys eye emission for the old flat eye (100-200); the ember-vein eye needs far less"""
    for o in sg.children_recursive:
        if not o.name.startswith('Stalker eye'): continue
        for m in o.data.materials:
            if not m or not m.node_tree.animation_data or not m.node_tree.animation_data.action: continue
            for fc in _fcurves(m.node_tree.animation_data.action):
                if 'Emission Strength' in fc.data_path or 'inputs[28]' in fc.data_path or 'default_value' in fc.data_path:
                    for kp in fc.keyframe_points: kp.co.y *= k; kp.handle_left.y *= k; kp.handle_right.y *= k


# ------------------------------------------------------------------ v8 Act 4: the car PARKED under the overpass, the teaser Stalker on top
PARK = V((.4, -7.0, 0))      # 23 m short of the overpass, so the thing on the rail is in view from the car
def bridge_set(nf, hits=(9999,), car_in=None, door_open=False):
    st = overpass_set(nf, hits=hits)
    car, parts, glowm, spots = nt_car(tuple(PARK), 0, lights_on=True)
    for sp in spots: sp.energy = 3200
    if car_in:                                                           # roll up and stop (nose dives on the stop, settles)
        f0, f1, y0 = car_in
        key(car, 1, loc=V((PARK.x, y0, 0)), rot=(0, 0, 0)); key(car, f0, loc=V((PARK.x, y0, 0)), rot=(0, 0, 0)); key(car, f1, loc=PARK, rot=(0, 0, 0))
        spin_wheels(parts, f0, f1, abs(y0 - PARK.y))
        suspension(car, 1, nf, amp=.004, pitch=[(1, 0), (f1 - 6, 0), (f1, -2.4), (f1 + 6, 1.0), (f1 + 12, -.3), (nf, 0)])
    else:
        suspension(car, 1, nf, amp=.0025)                                 # idling on its springs
    wipers(parts, nf)
    if door_open:
        for o_ in parts:
            if o_.type == 'MESH' and 'door' in o_.name.lower():
                bb = [o_.matrix_world @ V(cn) for cn in o_.bound_box]
                if sum(v.x for v in bb) / 8 > PARK.x + .3: o_.hide_render = True
    return st, car, parts

def wipers(parts, nf, period=30):
    """the wipers sweep (parked, engine idling): each wiper blade turns about its own pivot"""
    bpy.context.view_layer.update()
    piv = [o for o in parts if o.name.startswith('NT windshield wiper pivot') and 'hull' not in o.name and 'ink' not in o.name]
    blades = [o for o in parts if o.name.startswith('NT windshield wiper') and 'pivot' not in o.name and 'hull' not in o.name and 'ink' not in o.name]
    for k, bl in enumerate(blades):
        if not piv: break
        bc = sum((bl.matrix_world @ V(c) for c in bl.bound_box), V((0, 0, 0))) / 8
        pv = min(piv, key=lambda p: (p.matrix_world.translation - bc).length)
        e = bpy.data.objects.new('wiper hinge', None); col.objects.link(e); e.matrix_world = Matrix.Translation(pv.matrix_world.translation)
        for o_ in [bl] + [x for x in parts if x.name.startswith(bl.name + ' ')]:
            mw = o_.matrix_world.copy(); o_.parent = e; o_.matrix_world = mw
        ax = (bl.matrix_world.to_3x3() @ V((0, 0, 1))).normalized()
        e.rotation_mode = 'AXIS_ANGLE'
        for f in range(1, nf + 1, 2):
            u = ((f + k * 2) % period) / period; a = math.radians(92) * (math.sin(u * math.pi) ** 1.4)
            e.rotation_axis_angle = (a, 0, -.45, 1); e.keyframe_insert('rotation_axis_angle', frame=f)

def teaser_stalker(st, nf, mode, slam=None, eye_emit=6):
    neck, jaw = stalker_alive(st, nf, mode)
    if slam: stalker_body(st, nf, slam=slam)
    eye_scale(st); eye, eyes = eye_world(st); wet_eye(eyes, emit=eye_emit)
    return eye

def cut530():   # v8 130: the car rolls up under the overpass and STOPS; parked, wipers, idle; up there in the fog, something stands on the rail
    nf = 72; st, car, parts = bridge_set(nf, car_in=(1, 40, 9.0)); teaser_stalker(st, nf, 'wide')
    relight_overpass()
    c = camera(26)
    shot_cam(c, [(1, (2.9, 4.0, 1.0), (.4, -3, 1.2), 26, 8), (40, (2.7, 2.6, 1.05), (.4, -8, 1.6), 28, 10.5), (nf, (2.6, 2.0, 1.1), (.4, -25, 5.5), 30, 13)],
             1, nf, shake=.018, rshake=.35, seed=530)
    kick(c, [40], 1.0); c.data.dof.aperture_fstop = 4
    return 1, nf

def cut535():   # v8 135: the dashcam through the wet windscreen: up on the overpass, the teaser Stalker stands in the headlight glow
    nf = 60; st, car, parts = bridge_set(nf); eye = teaser_stalker(st, nf, 'wide', eye_emit=5)
    relight_overpass(); stalker_cu_light()
    for o_ in parts:   # the dashcam sits behind the glass: hide the tinted pane (it renders as a grey slab), keep beads of rain on it
        if 'windshield' in o_.name and 'wiper' not in o_.name: o_.hide_render = True
    glass_rain(70, 1, nf, (PARK.x - .35, PARK.x + .75), (PARK.y - .78, PARK.y - .74), (1.3, 1.62), size=.012)
    c = camera(50); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    base = PARK + V((.06, -.66, 1.31)); nz = A.Noise(535)
    for f in range(1, nf + 1):
        c.location = base + V((0, 0, nz(f * 2.3) * .0009)); aim(c, V((.8, -29, 11.4)) + V((0, 0, .2 * (f / nf))))
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 11.5; c.data.dof.aperture_fstop = 5.6
    return 1, nf

def cut540():   # v8 140: teaser 909-style crash zoom from the car roof up into the skull: bull skull, ember-vein eyes, the skull tilt + eye saccades
    nf = 48; st, car, parts = bridge_set(nf, hits=(30,)); eye = teaser_stalker(st, nf, 'close', eye_emit=8)
    relight_overpass(); stalker_cu_light()
    P = PARK + V((.9, .6, 2.1))
    c = camera(18)
    shot_cam(c, [(1, P, (.6, -30, 9.0), 18, 12), (9, P, tuple(eye), 135, (eye - P).length), (nf, P + V((0, -.05, 0)), tuple(eye + V((0, 0, .05))), 150, (eye - P).length)],
             1, nf, shake=.01, rshake=.35, seed=540)
    kick(c, [9], 1.4); c.data.dof.aperture_fstop = 4
    return 1, nf

def cut550():   # v8 150: the scream. it locks on, the head snaps to the sky, the front blade-stilts rise and slam (teaser body), lightning
    nf = 60; st, car, parts = bridge_set(nf, hits=(30, 34)); eye = teaser_stalker(st, nf, 'scream', slam=52, eye_emit=7)
    relight_overpass(); stalker_cu_light()
    c = camera(70)
    shot_cam(c, [(1, (2.2, -25.0, 11.5), (.8, -30, 12.3), 70, 5.3), (22, (2.1, -25.3, 11.5), (.8, -30, 12.35), 80, 5.0),
                 (30, (2.1, -25.3, 11.4), (.8, -30, 12.8), 62, 5.0), (nf, (2.0, -25.6, 11.3), (.8, -30, 13.0), 55, 5.2)], 1, nf, shake=.006, rshake=.15, seed=550)
    kick(c, [30, 31, 33, 52], 1.4); c.data.dof.aperture_fstop = 2.8
    return 1, nf

BWATCH = V((5.2, 34.0, 8.5))    # the hidden camera far behind, up a fire escape down the avenue
def cut552():   # v8 152: the hidden long lens far away: the parked car small, the Stalker drops off the overpass toward it, the focus is lost
    nf = 36; st, car, parts = bridge_set(nf); teaser_stalker(st, nf, 'wide')
    relight_overpass()
    p0 = st.location.copy()
    for f, d in ((1, V((0, 0, 0))), (8, V((0, .3, .4))), (14, V((0, 2.0, -3.0))), (19, V((0, 3.2, -10.0))), (nf, V((0, 3.4, -10.0)))):
        st.location = p0 + d; st.keyframe_insert('location', frame=f)
    tg = PARK + V((0, -5, 4))
    watcher_cam(nf, [(1, BWATCH, tg, 210), (19, BWATCH, tg + V((0, 0, -2)), 210), (nf, BWATCH, tg + V((0, 1, -2.6)), 190)], seed=552, hunt=((17, nf, 14.0),))
    kick(sc.camera, [19], 2.2)
    return 1, nf

def cut565():   # v8 165: the hidden camcorder's view from far away: the car, its driver door open, nobody; REC blinks; tape stop (in the grade)
    nf = 36; st, car, parts = bridge_set(nf, door_open=True)
    st.hide_render = True
    for o_ in st.children_recursive: o_.hide_render = True
    relight_overpass()
    tg = PARK + V((0, 0, 1.0))
    watcher_cam(nf, [(1, BWATCH, tg, 150), (nf, BWATCH, tg + V((0, 0, .1)), 175)], seed=565, hunt=((1, 14, 6.0),))
    return 1, nf

def cut495():   # v8 095: the hidden camera again, from a dark window up the street: the car fishtails past below, the zoom follows it
    nf = 60; rng = base_street(seed=12, length=160, fog=.01, dead=(1, 3), wrecks=True, exposure=1.0)
    car, parts, glowm, spots = nt_car((.6, 20, 0), 0, lights_on=True)
    keys = [(1, .6, 20, 0), (18, 1.4, 4, 14), (26, .2, -4, -16), (34, -.6, -12, 8), (44, .2, -22, -4), (nf, .4, -38, 0)]
    D = drift(car, keys); spin_wheels(parts, 1, nf, D)
    suspension(car, 1, nf, amp=.008, pitch=[(1, 0), (18, 1.0), (26, -1.2), (34, .8), (nf, 0)])
    rain_here((0, -6, 0), (16, 50, 14), 5000, 1, nf)
    W = V((-9.6, -24.0, 9.5)); trail = []
    for f in range(1, nf + 1): sc.frame_set(f); trail.append(car.matrix_world.translation.copy())
    keys_c = [(f, W, trail[max(0, f - 3)] + V((0, 0, .8)), 55 + 75 * (f / nf)) for f in range(1, nf + 1, 6)] + [(nf, W, trail[-4] + V((0, 0, .8)), 130)]
    watcher_cam(nf, keys_c, seed=495, hunt=((1, 20, 5.0),))
    return 1, nf
