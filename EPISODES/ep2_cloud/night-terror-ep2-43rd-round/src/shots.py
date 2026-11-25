"""The 43rd Round - shot builder. usage: SHOT=1 RES=.25 SAMP=8 STEP=1 python shots.py"""
import sys, os, math, random
sys.path.insert(0, '/home/user/w/sc')
from lib import *
import bmesh
SHOT = int(os.environ.get('SHOT', '1')); RES = float(os.environ.get('RES', '.25')); SAMP = int(os.environ.get('SAMP', '8'))
STEP = int(os.environ.get('STEP', '1')); ONLY = os.environ.get('FRAMES')
OUT = os.environ.get('OUT', f'/home/user/w/out/shots/s{SHOT:02d}')
FPS = 24
MUZ = {'L': V(-4.62, -.80, 1.36), 'R': V(-4.62, .80, 1.36)}   # trike-local muzzle points (front = -X)

sc = reset(); K = city(); import castlib as L
SET = L.collection('Set')

def C(h): return L.lin(h)
def mat(name, col, rough=.5, metal=0., emit=None, es=0.):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*C(col), 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (*C(emit), 1); b.inputs['Emission Strength'].default_value = es
    return m

def world(fog=.007, length=170, seed=4, width=16, cy=0.):
    K.street(SET, length=length, width=width, seed=seed, lamp_every=22)
    off = cy + length / 2 - 10
    for o in SET.objects:
        if o.parent is None: o.location.y += off
    K.sky(sc, fog=fog)
    sc.view_settings.exposure = float(os.environ.get('EXPO', '1.6'))
    mo = bpy.data.objects.get('moon')
    if mo: mo.data.energy = float(os.environ.get('MOON', '1.6'))

def rain(center, dur, count=6000, size=(18, 40), clear=()):
    fall = 11 * dur + 2
    r = K.rain(SET, (center[0], center[1], 0), size=(size[0], size[1], 12 + fall), count=count, streak=.22)
    if clear:
        bm = bmesh.new(); bm.from_mesh(r.data)
        dead = [f for f in bm.faces if any((V(f.calc_center_median().x, f.calc_center_median().y) - V(c[0], c[1])).length < c[2] for c in clear)]
        bmesh.ops.delete(bm, geom=dead, context='FACES'); bm.to_mesh(r.data); bm.free()
    r.location.z = 0; r.keyframe_insert('location', frame=1)
    r.location.z = -fall * (dur * FPS) / (dur * FPS); r.location.z = -11 * dur; r.keyframe_insert('location', frame=1 + int(dur * FPS))
    for fc in r.animation_data.action.fcurves if hasattr(r.animation_data.action, 'fcurves') else []:
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
    _linear(r)
    return r

def _linear(o):
    ad = o.animation_data
    if not ad or not ad.action: return
    act_ = ad.action
    fcs = []
    try: fcs = list(act_.fcurves)
    except Exception:
        for ly in act_.layers:
            for st in ly.strips:
                for cb in st.channelbags: fcs += list(cb.fcurves)
    for fc in fcs:
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'

# ------------------------------------------------------------------ trike + rider
def ride(pos_fn, f0, f1, bob=1., rider_on=True):
    """pos_fn(t) -> (Vector xy, heading radians, lean). keys the trike root, wheels and body suspension."""
    tc, T = trike()
    root, body = T['TRIKE_root'], T['TRIKE_body']
    dist = 0.; prev = None; r = random.Random(3)
    for f in range(f0, f1 + 1):
        t = (f - f0) / FPS; p, hd, ln = pos_fn(t)
        root.location = (p.x, p.y, 0); root.rotation_euler = (0, 0, hd)
        root.keyframe_insert('location', frame=f); root.keyframe_insert('rotation_euler', frame=f)
        if prev is not None: dist += (p - prev).length
        prev = p.copy()
        for w, R_ in (('wF', .94), ('wRL', 1.0), ('wRR', 1.0)):
            T[w].rotation_euler = (0, -dist / R_, 0); T[w].keyframe_insert('rotation_euler', frame=f)
        n1 = math.sin(t * 13.1) * .5 + math.sin(t * 7.3 + 1) * .5
        body.location = (0, 0, bob * (.018 * n1 + .01 * math.sin(t * 29)))
        body.rotation_euler = (ln + bob * .006 * math.sin(t * 9.7), bob * .008 * math.sin(t * 6.1 + 2), 0)
        body.keyframe_insert('location', frame=f); body.keyframe_insert('rotation_euler', frame=f)
    rig = None; tg = None
    if rider_on:
        rc, rig = rider(os.environ.get('RIDER', f'{W}/out/rider/rider.blend'))
        tg = seat_rider(rig, body)
        rig['base'] = {pb.name: list(pb.rotation_euler) for pb in rig.pose.bones}
        def breathe(rg, t, f):
            return {'spine03': (1.2 * math.sin(t * 2.2), 0, 0), 'neck01': (0, 0, 2 * math.sin(t * .9)),
                    'head': (1.5 * math.sin(t * 1.7), 1.0 * math.sin(t * 3.1), 3 * math.sin(t * .7)),
                    'spine05': (.6 * math.sin(t * 2.2 + .5), 0, 0)}
        act(rig, f0, f1, breathe, 2)
    # headlights
    for s in (-1, 1):
        spot(f'head{s}', V(-1.2, .35 * s, 1.35), V(-30, .35 * s * 4, .4), 16000, color=(1, .93, .8), size=38, blend=.5, parent=body)
    # follow key: sodium overhead pool + cool back rim, riding with the trike (street-lamp motivated)
    root = T['TRIKE_root']
    for nm, loc, e, c, sz in (('fkey', V(-1, 5, 7), 5000, (1, .72, .42), 4), ('frim', V(6, -4, 4), 3500, (.6, .75, 1), 3)):
        l = bpy.data.lights.new(nm, 'AREA'); l.energy = e; l.color = c; l.size = sz
        lo = bpy.data.objects.new(nm, l); sc.collection.objects.link(lo); lo.parent = root; lo.location = loc
        lo.rotation_euler = (V(0, 0, 1.2) - loc).to_track_quat('-Z', 'Y').to_euler()
    spot('bar', V(.6, 0, 2.78), V(-30, 0, 0), 9000, color=(1, .96, .9), size=55, blend=.6, parent=body)
    em = mat('LEDglow', '#fff6dc', emit='#fff6dc', es=40)
    for o in tc.all_objects:
        if o.type == 'MESH' and ('LED pod lenses' in o.name or 'light bar LEDs' in o.name):
            o.data.materials.clear(); o.data.materials.append(em)
    return T, rig, tg

def world_of(T, f, local):
    sc.frame_set(f); return T['TRIKE_body'].matrix_world @ V(local)

def dir_of(T, f, local_dir=V(-1, 0, 0)):
    sc.frame_set(f); return (T['TRIKE_body'].matrix_world.to_3x3() @ V(local_dir)).normalized()

# ------------------------------------------------------------------ guns
FLASHM = None
def flash_mesh():
    global FLASHM
    if FLASHM: return FLASHM
    bm = bmesh.new()
    for k in range(5):
        a = k * math.pi / 5
        ax = V(0, math.cos(a), math.sin(a))
        vs = [bm.verts.new(p) for p in (V(0, 0, 0) + ax * .05, V(-.55, 0, 0), V(0, 0, 0) - ax * .05, V(.05, 0, 0))]
        bm.faces.new(vs)
    me = bpy.data.meshes.new('flash'); bm.to_mesh(me); bm.free()
    me.materials.append(mat('Flash', '#ffd36b', emit='#ffc860', es=60)); FLASHM = me
    return me

def fire(T, side, f, target=None, tracer=True, light=True):
    """muzzle flash + light + tracer + brass at frame f (scene frame)."""
    body = T['TRIKE_body']
    fo = bpy.data.objects.new(f'flash{side}{f}', flash_mesh()); sc.collection.objects.link(fo)
    fo.parent = body; fo.location = MUZ[side]
    r = random.Random(f * 7 + (side == 'L'))
    for ff, s in ((f - 1, 0), (f, 1.0 + r.random() * .4), (f + 1, .45), (f + 2, 0)):
        fo.scale = (s, s * (.8 + r.random() * .5), s * (.8 + r.random() * .5)); fo.rotation_euler = (r.random() * 3, 0, 0)
        fo.keyframe_insert('scale', frame=ff); fo.keyframe_insert('rotation_euler', frame=ff)
    if light:
        l = bpy.data.lights.new(f'mf{side}{f}', 'POINT'); l.color = (1, .75, .4); l.shadow_soft_size = .1
        lo = bpy.data.objects.new(l.name, l); sc.collection.objects.link(lo); lo.parent = body; lo.location = MUZ[side] + V(-.3, 0, 0)
        for ff, e in ((f - 1, 0), (f, 9000), (f + 1, 2500), (f + 2, 0)):
            l.energy = e; l.keyframe_insert('energy', frame=ff)
    if tracer and target is not None:
        tr = tracer_obj(f'tr{side}{f}')
        a = world_of(T, f, MUZ[side]); b = V(target); a = a + (b - a).normalized() * min(4., (b - a).length * .3)
        d = (b - a); n = max(2, int(d.length / 45) + 1)
        tr.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        tr.scale = (0, 0, 0); tr.location = a; tr.keyframe_insert('scale', frame=f - 1); tr.keyframe_insert('location', frame=f - 1)
        for k in range(n + 1):
            tr.location = a + d * (k / n); tr.scale = (1, 1, 1) if k < n else (0, 0, 0)
            tr.keyframe_insert('location', frame=f + k); tr.keyframe_insert('scale', frame=f + k)
    brass(T, side, f)

TRM = None
def tracer_obj(name):
    global TRM
    if not TRM:
        p = prim('cylinder', vertices=6, radius=.012, depth=3.5, location=(0, 0, -1.75)); bpy.ops.object.transform_apply(location=True)
        TRM = p.data; TRM.materials.append(mat('Tracer', '#ffb050', emit='#ff9a40', es=80)); bpy.data.objects.remove(p)
    o = bpy.data.objects.new(name, TRM); sc.collection.objects.link(o); o.visible_shadow = False; return o

BRM = None
def brass(T, side, f, n=1):
    global BRM
    if not BRM:
        p = prim('cylinder', vertices=8, radius=.007, depth=.05)
        BRM = p.data; BRM.materials.append(mat('Brass', '#c9a050', .25, 1.)); bpy.data.objects.remove(p)
    r = random.Random(f * 13 + len(side))
    a = world_of(T, f, MUZ[side] + V(.9, 0, .08)); m3 = T['TRIKE_body'].matrix_world.to_3x3()
    v = m3 @ V(r.uniform(.5, 1.5), r.uniform(1.5, 3) * (1 if side == 'R' else -1), r.uniform(1.5, 3))
    o = bpy.data.objects.new(f'brass{side}{f}', BRM); sc.collection.objects.link(o)
    o.scale = (0, 0, 0); o.keyframe_insert('scale', frame=f - 1)
    z0 = 0.
    for k in range(0, 30):
        t = k / FPS; p = a + v * t + V(0, 0, -4.9 * t * t)
        if p.z < .01: p.z = .01 + abs(math.sin(k)) * .01
        o.location = p; o.rotation_euler = (k * .9, k * 1.3, 0); o.scale = (1, 1, 1)
        o.keyframe_insert('location', frame=f + k); o.keyframe_insert('rotation_euler', frame=f + k); o.keyframe_insert('scale', frame=f + k)

def head_of(rig, f):
    sc.frame_set(f); dg = bpy.context.evaluated_depsgraph_get()
    eyes = [o for o in rig.children if 'eyeL' in o.name or 'eyeR' in o.name]
    if not eyes:
        pb = rig.pose.bones['head']; return rig.matrix_world @ (pb.head + (pb.tail - pb.head) * .45)
    pts = []
    for o in eyes:
        oe = o.evaluated_get(dg); me = oe.to_mesh(); pts += [oe.matrix_world @ me.vertices[i].co for i in range(0, len(me.vertices), 4)]; oe.to_mesh_clear()
    return sum(pts, V(0, 0, 0)) / len(pts) + V(0, 0, .035)

def kill(rig, f, gun_from, seed=0):
    """headshot at frame f: snap + fall + blood spray away from the gun"""
    h = head_of(rig, f)
    headshot(rig, f, seed)
    blood_burst(h, (h - V(gun_from)).normalized(), f, seed=seed + f)
    return h

# ------------------------------------------------------------------ camera helpers
def cam_keys(co, f0, f1, fn):
    """fn(t) -> (loc, target, lens). keyed every frame, plus subtle handheld noise"""
    for f in range(f0, f1 + 1):
        t = (f - f0) / FPS; loc, tgt, lens = fn(t)
        n = V(math.sin(t * 5.3) + .5 * math.sin(t * 11.7 + 2), math.sin(t * 4.1 + 1) * .4, math.sin(t * 6.7 + 4) + .4 * math.sin(t * 13.3)) * float(os.environ.get('SHAKE', '1'))
        co.location = V(loc) + n * .006
        q = (V(tgt) - co.location).to_track_quat('-Z', 'Y').to_euler('XYZ', co.rotation_euler)
        q.y += math.radians(.25) * math.sin(t * 3.3)
        co.rotation_euler = q; co.data.lens = lens
        co.keyframe_insert('location', frame=f); co.keyframe_insert('rotation_euler', frame=f); co.data.keyframe_insert('lens', frame=f)

def mistfog(k=.4, col=(.004, .005, .008), start=3, depth=70):
    wt = sc.world.node_tree; wo = wt.nodes['World Output']
    for l in list(wt.links):
        if l.to_socket == wo.inputs['Volume']: wt.links.remove(l)
    sc.view_layers[0].use_pass_mist = True
    ms = sc.world.mist_settings; ms.start = start; ms.depth = depth; ms.falloff = 'QUADRATIC'
    t = bpy.data.node_groups.new('comp', 'CompositorNodeTree'); sc.compositing_node_group = t
    n = t.nodes; rl = n.new('CompositorNodeRLayers')
    t.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor'); go = n.new('NodeGroupOutput')
    mm = n.new('ShaderNodeMath'); mm.operation = 'MULTIPLY'; mm.inputs[1].default_value = k
    mx = n.new('ShaderNodeMix'); mx.data_type = 'RGBA'
    t.links.new(rl.outputs['Mist'], mm.inputs[0]); t.links.new(mm.outputs[0], mx.inputs[0])
    t.links.new(rl.outputs['Image'], mx.inputs[6]); mx.inputs[7].default_value = (*col, 1)
    t.links.new(mx.outputs[2], go.inputs[0])

def finish(f0, f1, mb=True, warp=None, camfn=None, volume=False):
    if not volume: mistfog(float(os.environ.get('FOGK', '.4')))
    render_setup(sc, RES, SAMP)
    sc.render.use_motion_blur = mb; sc.render.motion_blur_shutter = .45
    sc.cycles.light_sampling_threshold = .02
    sc.frame_start = f0; sc.frame_end = f1
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}.blend')
    frames = list(range(f0, f1 + 1, STEP))
    if ONLY: frames = [int(x) for x in ONLY.split(',')]
    for i, f in enumerate(frames):
        path = f'{OUT}/f{f:04d}.png'
        if os.path.exists(path) and not os.environ.get('FORCE'): continue
        if warp:
            wf = warp(f); sc.frame_set(int(math.floor(wf)), subframe=wf - math.floor(wf))
            if camfn: camfn(f, wf)
        else:
            sc.frame_set(f)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print('FRAME', f, flush=True)

# ================================================================== SHOTS
def shot1():   # Road kiss: lens on the asphalt, feet shuffle past, IVORY rolls over the camera
    world(fog=.01, cy=-20); N = 60
    v = 21.; th = 2.2
    T, rig, _ = ride(lambda t: (V(0, -3.32 - v * (th - t) + 0, 0) * 0 + V(0, v * (t - th) - 3.32, 0), math.radians(-90), 0), 1, N, rider_on=True)
    rain((0, -10), 2.6, count=5000, size=(14, 36), clear=((.5, .6, 1.6),))
    w = walker(V(.55, -1.0, 0), math.radians(-90 + 8), seed=11); fn, per = shamble(11, .8); act(w, 1, N, fn, 2); move_keys(w, 1, N, .5, 11, per)
    w2 = walker(V(-2.2, -9, 0), math.radians(170), seed=12); fn, per = shamble(12); act(w2, 1, N, fn, 2); move_keys(w2, 1, N, .45, 12, per)
    spot('pool1', V(2.5, -2, 7.5), V(0, -2.5, 0), 7000, color=(1, .7, .4), size=70, blend=.8)
    co = cam(V(.5, .6, .2), V(0, -20, .9), 16)
    cam_keys(co, 1, N, lambda t: (V(.5, .6, .2), V(0, -20, .1 + .02 * t), 16))
    co.data.dof.use_dof = True; co.data.dof.focus_distance = 1.8; co.data.dof.aperture_fstop = 2.8
    finish(1, N)

def shot2():   # Saddle up: tracking alongside, crane from the front tyre up to the rider's face; bolt rack on the bar
    world(fog=.006, cy=60); N = 60; v = 17.
    T, rig, tg = ride(lambda t: (V(0, 40 + v * t, 0), math.radians(-90), 0), 1, N)
    rain((3, 60), 2.6, count=6000, size=(16, 60))
    # right hand leaves the yoke, grabs the charging lever and racks it on the bar (t=1.5 s)
    h = tg['R']['hand']; h0 = h.location.copy(); lever = V(-.2, .42, 1.78)
    for f, p in ((1, h0), (20, h0), (28, lever), (36, lever), (40, lever + V(.32, 0, 0)), (46, lever + V(.32, 0, .02)), (54, h0)):
        h.location = p; h.keyframe_insert('location', frame=f)
    def cf(t):
        k = ease(min(1, t / 2.3))
        y = 40 + v * t
        loc = V(6.6 - 2.0 * k, y - 4.5 + 4.4 * k, .6 + 2.8 * k)
        sc.frame_set(1 + int(t * FPS)); pb = rig.pose.bones['head']; hh = rig.matrix_world @ pb.head
        tgt = V(0, y + 3.32, .9).lerp(hh + V(0, 0, .08), k)
        return loc, tgt, 35 + 50 * k
    co = cam(V(4, 0, 1), V(0, 0, 1), 35); cam_keys(co, 1, N, cf)
    finish(1, N)

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)

def shot3():   # Over the barrels: walkers in the beam, centre one dropped on the downbeat, then a second
    world(fog=.009, cy=125); N = 60; v = 7.
    T, rig, _ = ride(lambda t: (V(0, 100 + v * t, 0), math.radians(-90), 0), 1, N)
    rain((0, 115), 2.6, count=6000, size=(16, 40))
    ws = []
    for i, (x, y) in enumerate(((0, 124), (2.4, 129), (-3.0, 127), (1.2, 139), (-1.6, 145))):
        w = walker(V(x, y, 0), math.radians(x * -3), seed=20 + i); fn, per = shamble(20 + i); act(w, 1, N, fn, 2)
        ws.append((w, fn, per))
    kf = (13, 37)
    for i, (w, fn, per) in enumerate(ws):
        end = kf[i] if i < 2 else N
        move_keys(w, 1, end, .5, 20 + i, per)
    gunpos = lambda f: world_of(T, f, V(-4.6, 0, 1.36))
    for i in (0, 1):
        tgt = kill(ws[i][0], kf[i], gunpos(kf[i]), seed=30 + i)
        for k, s in enumerate('LR'):
            fire(T, s, kf[i] + k, tgt)
    # camera on the hood, slight pan to centre each target at its kill frame
    h0 = head_of(ws[0][0], kf[0] - 1); h1 = head_of(ws[1][0], kf[1] - 1)
    def cf(t):
        f = 1 + t * FPS; y = 100 + v * t
        loc = V(0, y + 2.2, 2.4)
        k = ease((f - kf[0] - 2) / (kf[1] - kf[0] - 6))
        tgt = h0.lerp(h1, k)
        return loc, tgt + V(0, 0, -.12), 65
    co = cam(V(0, 0, 2), V(0, 10, 2), 50); cam_keys(co, 1, N, cf)
    finish(1, N)

def shot5():   # Domino drift: high crane, IVORY slides sideways, four walkers on four beats
    world(fog=.004, width=18, cy=215); N = 96
    def pf(t):
        tt = min(t, 2.7); y = 205 + 12 * tt - 2.2 * tt * tt
        return V(-1.5 * ease(t / 2.7), y, 0), math.radians(-90 + 70 * ease(t / 1.9)), 0
    T, rig, _ = ride(pf, 1, N, bob=1.4)
    rain((0, 215), 4.1, count=6000, size=(20, 40))
    beats = (13, 25, 37, 49); side = ['R', 'L', 'R', 'L']
    for i, fk in enumerate(beats):
        m = world_of(T, fk, MUZ[side[i]]); d = dir_of(T, fk); d.z = 0; d.normalize()
        hp = m + d * (5.0 + i * .6)
        w = walker(V(hp.x, hp.y, 0), math.atan2(-d.x, d.y) + math.radians(random.Random(i).uniform(-15, 15)), seed=40 + i)
        fn, per = shamble(40 + i); act(w, 1, N, fn, 2)
        hh = head_of(w, fk); w.location += V(hp.x - hh.x, hp.y - hh.y, 0)
        kill(w, fk, m, seed=50 + i); fire(T, side[i], fk, head_of(w, fk))
        fire(T, side[i], fk + 2, head_of(w, fk + 1), light=False)
    def cf(t):
        sc.frame_set(1 + int(t * FPS)); c = T['TRIKE_root'].matrix_world.translation.copy()
        k = ease(t / 4)
        return c + V(7 - 1.5 * k, -6 + 1 * k, 11 - 3 * k), c + V(-3, 5, 0), 24
    co = cam(V(0, 0, 12), V(0, 1, 0), 24); cam_keys(co, 1, N, cf)
    finish(1, N)

def shot6():   # Goggles: extreme close-up, flashes reflected
    world(fog=.006, cy=305); N = 48; v = 9.
    T, rig, _ = ride(lambda t: (V(0, 300 + v * t, 0), math.radians(-90), 0), 1, N, bob=.5)
    rain((0, 310), 2.1, count=3000, size=(10, 20))
    for i, fk in enumerate((1, 13, 25, 37)):
        for s in 'LR': fire(T, s, fk + (s == 'R'), None, tracer=False)
    def cf(t):
        sc.frame_set(1 + int(t * FPS)); pb = rig.pose.bones['head']
        hm = rig.matrix_world @ pb.matrix
        e = hm @ V(0, .1, -.1)   # forward of face in head bone space ~ -Z? approximate below
        hc = rig.matrix_world @ (pb.head + (pb.tail - pb.head) * .55)
        fwd = (T['TRIKE_body'].matrix_world.to_3x3() @ V(-1, 0, 0)).normalized()
        tgt = hc + fwd * .09 + V(0, 0, .02)
        return tgt + fwd * (.75 - .04 * t) + V(.05, 0, -.01), tgt, 100
    co = cam(V(0, 0, 0), V(0, 1, 0), 100); cam_keys(co, 1, N, cf)
    co.data.dof.use_dof = True; co.data.dof.focus_distance = .72; co.data.dof.aperture_fstop = 2.0
    finish(1, N)

def shot7():   # The quiet: high wide, trike idling, bodies in the headlights, last walker tips over
    world(fog=.012, cy=405); N = 60
    T, rig, _ = ride(lambda t: (V(0, 400, 0), math.radians(-90), 0), 1, N, bob=.25)
    rain((0, 412), 2.6, count=6000, size=(20, 40))
    r = random.Random(5)
    for i in range(7):
        w = walker(V(r.uniform(-5, 5), 410 + r.uniform(0, 14), 0), r.uniform(-3, 3), seed=60 + i)
        fn, per = shamble(60 + i); act(w, -40, -20, fn, 4); headshot(w, -40, 60 + i)
    kn = walker(V(.6, 413, 0), math.radians(170), seed=70); kn['base']['lowerleg01.L'] = [math.radians(-95), 0, 0]
    def kneel(rg, t, f): return {'upperleg01.L': (40, 0, 0), 'upperleg01.R': (40, 0, 0), 'lowerleg01.L': (-100, 0, 0), 'lowerleg01.R': (-100, 0, 0), 'spine04': (10 + 4 * math.sin(t * 3), 0, 0), 'head': (25, 0, 8 * math.sin(t * 2))}
    act(kn, 1, 30, kneel, 2); kn.location.z -= .35; kn.keyframe_insert('location', frame=1)
    act(kn, 31, 31, kneel, 1)
    kn.keyframe_insert('location', frame=30)
    headshot(kn, 31, 71, back=-0.8, dur=16)
    co = cam(V(0, 0, 0), V(0, 1, 0), 24)
    cam_keys(co, 1, N, lambda t: (V(2.5, 382 + .5 * t, 8.5 - .15 * t), V(0, 406, 0), 24))
    finish(1, N)


def shot4():   # The bullet line: one take, time ramps to 2 %, camera rides behind the round, snaps back on impact
    world(fog=.008, cy=170); N = 96; v = 8.
    def spd(f):
        if f <= 10: return 1.
        if f <= 20: return 1 - .98 * ease((f - 10) / 10)
        if f <= 72: return .02
        if f <= 77: return .02 + .98 * ease((f - 72) / 5)
        return 1.
    WT = [0.]
    for f in range(1, N + 2): WT.append(WT[-1] + spd(f) / FPS)
    wt = lambda f: WT[int(f)] + (WT[min(len(WT) - 1, int(f) + 1)] - WT[int(f)]) * (f - int(f))
    wf = lambda f: 1 + wt(f) * FPS
    F_FIRE, F_IMP = 19, 70
    T, rig, _ = ride(lambda t: (V(0, 150 + v * t, 0), math.radians(-90), 0), 1, 40, rider_on=False)
    rain((0, 168), 2, count=9000, size=(10, 40))
    tf, ti = wt(F_FIRE), wt(F_IMP)
    sf_fire = 1 + tf * FPS; sf_imp = 1 + ti * FPS
    mz = world_of(T, int(round(sf_fire)), MUZ['R'])
    fwd = dir_of(T, int(round(sf_fire)))
    D = 400 * (ti - tf)
    w = walker(V(mz.x - .1, mz.y + D - .2, 0), math.radians(-2), seed=80)
    fn, per = shamble(80, .7); act(w, 1, 40, fn, 1); move_keys(w, 1, int(sf_imp), .25, 80, per)
    fi = int(round(sf_imp))
    head = head_of(w, fi); dirv = (head - mz).normalized(); vel = (head - mz).length / (ti - tf)
    fire(T, 'R', int(round(sf_fire)), None, tracer=False)
    kill(w, fi, mz, seed=81)
    # the round
    b1 = prim('cylinder', vertices=16, radius=.0065, depth=.03, location=(0, 0, -.015))
    b2 = prim('cone', vertices=16, radius1=.0065, radius2=.0005, depth=.02, location=(0, 0, .01))
    bul = L.join([b1, b2], 'round'); bul.scale = (1.5, 1.5, 1.5); L.apply_transform(bul); bul.data.materials.clear(); bul.data.materials.append(mat('Copper', '#b8733a', .22, 1.))
    for o in list(bul.users_collection): o.objects.unlink(bul)
    sc.collection.objects.link(bul)
    bul.rotation_euler = dirv.to_track_quat('Z', 'Y').to_euler()
    glow = bpy.data.lights.new('bglow', 'POINT'); glow.energy = .8; glow.color = (1, .6, .3); glow.shadow_soft_size = .02
    go = bpy.data.objects.new('bglow', glow); sc.collection.objects.link(go); go.parent = bul; go.location = (.05, .03, .02)
    def bpos(t): return mz + dirv * vel * max(0., t - tf)
    # shock rings left behind the round (glassy, expand slowly in world time)
    ringm = bpy.data.materials.new('Ring'); ringm.use_nodes = True; rb = ringm.node_tree.nodes['Principled BSDF']
    rb.inputs['Transmission Weight'].default_value = 1; rb.inputs['Roughness'].default_value = .05; rb.inputs['IOR'].default_value = 1.05
    for i, dd in enumerate((.6, 2.2, 4.5, 7.5, 11.)):
        ro = prim('torus', major_radius=.05, minor_radius=.006, major_segments=32, minor_segments=8); ro.data.materials.append(ringm)
        ro.location = mz + dirv * dd; ro.rotation_euler = dirv.to_track_quat('Z', 'Y').to_euler()
        tb = tf + dd / vel; fb = 1 + tb * FPS
        ro.scale = (0, 0, 0); ro.keyframe_insert('scale', frame=int(fb))
        ro.scale = (1, 1, 1); ro.keyframe_insert('scale', frame=int(fb) + 1)
        ro.scale = (5, 5, 1); ro.keyframe_insert('scale', frame=int(fb) + 40)
    co = cam(V(0, 0, 0), V(0, 1, 0), 35)
    co.data.dof.use_dof = True; co.data.dof.aperture_fstop = 5.6
    right = V(dirv.y, -dirv.x, 0).normalized()
    state = {}
    def camfn(f, sf):
        t = wt(f)
        bp = bpos(t)
        bul.location = bp if t >= tf else mz - dirv * .2
        drift = right * (.05 + .2 * ease((f - F_FIRE) / (F_IMP - F_FIRE))) + V(0, 0, .02)
        if f < F_FIRE:
            loc = mz - dirv * .3 + right * .16 + V(0, 0, .07); tgt = head; fd = (head - loc).length
        else:
            stop = head - dirv * 1.0
            along = min((bp - mz).length - .42, (stop - mz).length)
            loc = mz + dirv * along + drift
            tgt = (bp + dirv * min(3., (head - bp).length)).lerp(head, ease((f - F_FIRE - 34) / 14))
            fd = (bp - loc).length if f < F_IMP - 10 else (head - loc).length
        if f > F_IMP: loc = state.get('last', loc); tgt = head
        state['last'] = loc
        co.location = loc; co.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
        co.data.dof.focus_distance = max(.15, fd)
    finish(1, N, mb=False, warp=wf, camfn=camfn)

SK_S = 1.25
def eyes_glow(rig, keys):
    """keys: [(frame, strength)] on the Stalker eye material emission"""
    ms = {m for o in rig.children for m in o.data.materials if m and 'Eye' in m.name}
    for m in ms:
        b = [n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'][0]
        b.inputs['Emission Color'].default_value = (1, .16, .05, 1)
        for f, e in keys:
            b.inputs['Emission Strength'].default_value = e; b.inputs['Emission Strength'].keyframe_insert('default_value', frame=f)

def truck(loc, rotz):
    paint = mat('TruckPaint', '#5a5a52', .55); dark = mat('TruckDark', '#141414', .7); rust = mat('Rust', '#4a2a18', .9)
    root = bpy.data.objects.new('truck', None); sc.collection.objects.link(root); root.location = loc; root.rotation_euler = (0, 0, rotz)
    def bx(nm, p, sz, m):
        o = prim('cube', size=1, location=p); o.scale = sz; o.name = nm
        bpy.ops.object.transform_apply(scale=True)
        bv = o.modifiers.new('b', 'BEVEL'); bv.width = .04; bv.segments = 2
        o.data.materials.append(m); o.parent = root; return o
    bx('trailer', (0, 0, 1.75), (11, 2.5, 2.6), paint)
    bx('chassis', (0, 0, .35), (11, 2.2, .3), dark)
    bx('cab', (6.6, -1.2, 1.5), (2.4, 2.5, 2.4), rust)
    root2 = bpy.data.objects['cab']; root2.rotation_euler = (0, 0, math.radians(-38))
    for x in (-4.5, -3.2, 3.5):
        for y in (-1.1, 1.1):
            o = prim('cylinder', radius=.5, depth=.35, location=(x, y, .5), rotation=(math.pi / 2, 0, 0)); o.data.materials.append(dark); o.parent = root
    return root

def fogbank(center, size, dens=.08):
    o = prim('cube', size=1, location=center); o.scale = size; o.name = 'fogbank'
    m = bpy.data.materials.new('Fog'); m.use_nodes = True; nt = m.node_tree; n = nt.nodes
    for x in list(n):
        if x.type == 'BSDF_PRINCIPLED': n.remove(x)
    vs = n.new('ShaderNodeVolumePrincipled'); vs.inputs['Color'].default_value = (.6, .65, .75, 1)
    nz = n.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = .35; nz.inputs['Detail'].default_value = 3
    tc = n.new('ShaderNodeTexCoord'); mp = n.new('ShaderNodeMapping'); nt.links.new(tc.outputs['Object'], mp.inputs[0]); nt.links.new(mp.outputs[0], nz.inputs['Vector'])
    mp.inputs['Location'].default_value = (0, 0, 0); mp.inputs['Location'].keyframe_insert('default_value', frame=1)
    mp.inputs['Location'].default_value = (.5, 0, .1); mp.inputs['Location'].keyframe_insert('default_value', frame=80)
    mr = n.new('ShaderNodeMapRange'); mr.inputs[1].default_value = .4; mr.inputs[2].default_value = .75; mr.inputs[4].default_value = dens
    nt.links.new(nz.outputs['Fac'], mr.inputs[0]); nt.links.new(mr.outputs[0], vs.inputs['Density'])
    nt.links.new(vs.outputs[0], n['Material Output'].inputs['Volume'])
    o.data.materials.append(m); return o

def shot8():   # Antlers in the fog: over the shoulder, rack focus, it rises over the truck, eyes ignite
    world(fog=.012, cy=480); N = 60  # fog bank thin
    T, rig, _ = ride(lambda t: (V(0, 470, 0), math.radians(-90), 0), 1, N, bob=.25)
    truck(V(.5, 503, 0), math.radians(78))
    fogbank(V(0, 511, 2.5), (30, 9, 5), .012)
    rain((0, 485), 2.6, count=5000, size=(16, 36))
    st = stalker(V(-.8, 506.5, -3.2), math.radians(4)); st.scale = (SK_S,) * 3
    def fn(t, f):
        k = ease((t - .25) / 1.7)
        d = stalk_pose(t, gait=.25, gph=t * 2.5, tilt=18 * math.sin(t * 1.3) * k, look=(8 * math.sin(t * .9), -10 + 14 * k), crouch=1 - k)
        d['_root'] = (V(-.8, 506.5, -3.2 + 3.2 * k), (0, 0, math.radians(4))); return d
    sact(st, 1, N, fn)
    eyes_glow(st, [(1, 0), (40, 0), (44, 60), (60, 30)])
    sc.frame_set(1); pb = rig.pose.bones['head']; hp = rig.matrix_world @ pb.head
    co = cam(V(0, 0, 0), V(0, 1, 0), 85)
    cam_keys(co, 1, N, lambda t: (hp + V(.7, -.45, .5), V(-.6, 506.5, 2.6), 65))
    co.data.dof.use_dof = True; co.data.dof.aperture_fstop = 2.0
    fd = co.data.dof
    for f, dd in ((1, .9), (16, .9), (30, (V(-.6, 506.5, 2.6) - hp).length), (N, (V(-.6, 506.5, 2.6) - hp).length)):
        fd.focus_distance = dd; fd.keyframe_insert('focus_distance', frame=f)
    finish(1, N)

def shot9():   # Empty the belt: push in, sparks and bone chips, it staggers, keeps coming; three dry clicks
    world(fog=.009, cy=560); N = 72
    T, rig, _ = ride(lambda t: (V(0, 540, 0), math.radians(-90), 0), 1, N, bob=.6)
    truck(V(5, 590, 0), math.radians(70))
    rain((0, 560), 3.1, count=6000, size=(16, 40))
    st = stalker(V(0, 568, 0), 0); st.scale = (SK_S,) * 3
    def fn(t, f):
        hit = math.exp(-((f - 30) / 3.) ** 2) + .4 * math.exp(-((f - 48) / 2.5) ** 2)
        d = stalk_pose(t, gait=.8, gph=t * 3.4, tilt=25 * math.sin(t * 1.6), look=(10 * math.sin(t * 2.1), 0), hit=hit)
        d['_root'] = (V(0, 568 - 2.2 * t + .5 * hit, .04 * abs(math.sin(t * 3.4))), (0, 0, math.radians(6 * hit))); return d
    sact(st, 1, N, fn)
    eyes_glow(st, [(1, 30)])
    r = random.Random(9)
    sparkm = mat('Spark', '#ffd080', emit='#ffb050', es=120)
    for f in range(2, 60, 2):
        for s_ in 'LR':
            sc.frame_set(f)
            tgt = st.matrix_world @ V(r.uniform(-.3, .3), r.uniform(-.2, .1), r.uniform(1.2, 2.6) / SK_S)
            fire(T, s_, f + (s_ == 'R'), tgt, light=(f % 4 == 2))
            if r.random() < .55:   # spark burst
                for k in range(4):
                    sp = prim('cylinder', vertices=4, radius=.006, depth=.18); sp.data.materials.append(sparkm)
                    vv = V(r.uniform(-1, 1), r.uniform(-1.4, .2), r.uniform(-.2, 1.2)).normalized() * r.uniform(3, 7)
                    sp.rotation_euler = vv.to_track_quat('Z', 'Y').to_euler()
                    sp.scale = (0, 0, 0); sp.location = tgt; sp.keyframe_insert('scale', frame=f + 1); sp.keyframe_insert('location', frame=f + 1)
                    for kk in range(1, 6):
                        sp.location = tgt + vv * kk / FPS + V(0, 0, -4.9 * (kk / FPS) ** 2); sp.scale = (1, 1, 1) if kk < 5 else (0, 0, 0)
                        sp.keyframe_insert('location', frame=f + 1 + kk); sp.keyframe_insert('scale', frame=f + 1 + kk)
    sc.frame_set(1); gp = world_of(T, 1, V(-1.9, 0, 3.0))
    def cf(t):
        k = ease(t / 3.); sc.frame_set(1 + int(t * FPS))
        rec = (math.sin(t * 75) * .012 if t < 2.45 else 0)
        return gp + V(rec, 3.2 * k, rec * .6 - .2 * k), st.matrix_world @ V(0, 0, 1.8 / SK_S), 50
    co = cam(V(0, 0, 0), V(0, 1, 0), 50); cam_keys(co, 1, N, cf)
    finish(1, N)

def shot10():  # The roar: real slow-mo close-up (world at 25 %), jaw unhinges, eyes flare
    world(fog=.01, cy=640); N = 48; SL = .25
    rain((0, 640), 1.2, count=5000, size=(10, 16))
    st = stalker(V(0, 640, 0), 0); st.scale = (SK_S,) * 3
    NW = int(N * SL) + 4
    def fn(t, f):
        j = ease((t - .05) / .25)
        d = stalk_pose(t, gait=0, jaw=j * 1.35, tilt=-14 * j + 4 * math.sin(t * 9), look=(0, 22 * j), hit=.3 * j)
        d['_root'] = (V(0, 640, 0), (0, 0, 0)); return d
    sact(st, 1, NW, fn)
    eyes_glow(st, [(1, 30), (4, 30), (7, 140), (NW, 90)])
    # shockwave ring from the mouth
    sc.frame_set(6); hd = st.matrix_world @ (st.pose.bones['jaw'].head)
    ringm = bpy.data.materials.new('Ring2'); ringm.use_nodes = True; rb = ringm.node_tree.nodes['Principled BSDF']
    rb.inputs['Transmission Weight'].default_value = 1; rb.inputs['Roughness'].default_value = .02; rb.inputs['IOR'].default_value = 1.08
    ro = prim('torus', major_radius=.2, minor_radius=.03, major_segments=48, minor_segments=8)
    ro.data.materials.append(ringm); ro.location = hd + V(0, -.2, 0); ro.rotation_euler = (math.radians(90), 0, 0)
    ro.scale = (0, 0, 0); ro.keyframe_insert('scale', frame=6); ro.scale = (1, 1, 1); ro.keyframe_insert('scale', frame=7)
    ro.scale = (30, 30, 3); ro.location = hd + V(0, -6, 0); ro.keyframe_insert('scale', frame=12); ro.keyframe_insert('location', frame=12)
    hc = st.matrix_world @ st.pose.bones['head'].head
    co = cam(V(0, 0, 0), V(0, 1, 0), 65)
    key = bpy.data.lights.new('rk', 'AREA'); key.energy = 900; key.size = 2; key.color = (1, .7, .45)
    ko = bpy.data.objects.new('rk', key); sc.collection.objects.link(ko); ko.location = hc + V(-2.5, -2.5, 1.5); ko.rotation_euler = (hc - ko.location).to_track_quat('-Z', 'Y').to_euler()
    rim = bpy.data.lights.new('rr', 'AREA'); rim.energy = 1200; rim.size = 1.5; rim.color = (.6, .7, 1)
    rio = bpy.data.objects.new('rr', rim); sc.collection.objects.link(rio); rio.location = hc + V(2.5, 2.5, 1); rio.rotation_euler = (hc - rio.location).to_track_quat('-Z', 'Y').to_euler()
    def camfn(f, wf):
        t = (f - 1) / FPS
        co.location = hc + V(.35, -2.6 - .25 * t, -.55); co.rotation_euler = (hc + V(0, 0, .05) - co.location).to_track_quat('-Z', 'Y').to_euler()
    co.data.dof.use_dof = True; co.data.dof.focus_distance = 2.6; co.data.dof.aperture_fstop = 2.8
    finish(1, N, mb=True, warp=lambda f: 1 + (f - 1) * SL, camfn=camfn)

def shot11():  # The charge + black: road camera, it gallops down the lens and leaps into it
    world(fog=.01, cy=700); N = 56
    rain((0, 700), 2.4, count=5000, size=(14, 40), clear=((.0, 700, 1.5),))
    st = stalker(V(0, 670, 0), math.pi); st.scale = (SK_S,) * 3
    LEAP = 40
    def fn(t, f):
        if f < LEAP:
            d = stalk_pose(t, gait=1.7, gph=t * 11, stride=1.2, look=(0, 10), jaw=.6, crouch=.5, breathe=0)
            d['_root'] = (V(0, 670 + 14.5 * t * min(1, .55 + t * .4), .12 * abs(math.sin(t * 11))), (math.radians(12), 0, math.pi))
        else:
            k = (f - LEAP) / 10
            d = stalk_pose(t, gait=.3, gph=t * 11, look=(0, 25), jaw=1.3, hit=-.5)
            y0 = 670 + 14.5 * (LEAP - 1) / FPS * min(1, .55 + (LEAP - 1) / FPS * .4)
            d['_root'] = (V(0, y0 + 7 * k, 1.6 * math.sin(min(1, k) * 2.2)), (math.radians(12 + 20 * k), 0, math.pi))
        return d
    sact(st, 1, N, fn)
    eyes_glow(st, [(1, 80)])
    spot('trikeL', V(-.9, 709, 1.4), V(0, 680, 1.5), 30000, size=30)
    spot('trikeR', V(.9, 709, 1.4), V(0, 680, 1.5), 30000, size=30)
    co = cam(V(0, 0, 0), V(0, 1, 0), 18)
    cam_keys(co, 1, N, lambda t: (V(.2, 702, .12), V(0, 680, 1.6), 18))
    co.data.dof.use_dof = True; co.data.dof.focus_distance = 8; co.data.dof.aperture_fstop = 4
    finish(1, N)

{8: shot8, 9: shot9, 10: shot10, 11: shot11, 4: shot4, 1: shot1, 2: shot2, 3: shot3, 5: shot5, 6: shot6, 7: shot7}[SHOT]()
