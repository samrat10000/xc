"""Night Terror: Dead Roads - Episode 1 v2 cuts (animated, web-series coverage). CUT=n.
Helpers copied from shots.py. SHOT=1..8 builds one shot and renders its frames.
env: RES (1.0 = 1080x1920), SAMP, FR="a,b" (frame range override), STEP (render every Nth frame), BLEND=1 save .blend"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Euler
import city as K
import anim as A
import castlib as L
V = K.V
HERE = os.path.dirname(os.path.abspath(__file__))
SHOT = int(os.environ.get('CUT', '3'))
OUT = os.path.join(os.environ.get('OUTROOT', os.path.join(HERE, 'out', 'cuts')), f'c{SHOT:02d}' if SHOT < 100 else f'c{SHOT}'); os.makedirs(OUT, exist_ok=True)
FPS = 24
sc = L.reset(); col = L.collection('Set')
sc.render.fps = FPS


# ------------------------------------------------------------------ helpers
def ease(t): return t * t * (3 - 2 * t)

def key(o, f, loc=None, rot=None, interp='BEZIER'):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)

def linear(o):
    ad = o.animation_data
    if ad and ad.action:
        for fc in _fcurves(ad.action):
            for k in fc.keyframe_points: k.interpolation = 'LINEAR'

def _fcurves(act):
    if hasattr(act, 'fcurves'):
        try: return list(act.fcurves)
        except Exception: pass
    out = []
    for lay in getattr(act, 'layers', []):
        for st in lay.strips:
            for cb in st.channelbags: out += list(cb.fcurves)
    return out

def key_val(owner, path, f, v, const=False):
    setattr(owner, path, v) if not isinstance(owner, bpy.types.NodeSocket) else None
    owner.keyframe_insert(path, frame=f)

def aim(o, target):
    prev = o.rotation_euler.copy()
    o.rotation_euler = (V(target) - o.location).to_track_quat('-Z', 'Y').to_euler('XYZ', prev)

def camera(lens=30):
    c = bpy.data.cameras.new('shot'); c.lens = lens; c.sensor_width = 36; c.clip_start = .05; c.clip_end = 600
    o = bpy.data.objects.new('shot', c); sc.collection.objects.link(o); sc.camera = o
    return o

def cam_path(o, frames, locs, targets, lenses=None, focus=None):
    """keyframe camera position + aim (as rotation) + optional lens/focus at given frames, smooth"""
    for i, f in enumerate(frames):
        o.location = V(locs[i]); aim(o, targets[i])
        o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)
        if lenses: o.data.lens = lenses[i]; o.data.keyframe_insert('lens', frame=f)
        if focus:
            o.data.dof.use_dof = True; o.data.dof.focus_distance = focus[i]; o.data.dof.keyframe_insert('focus_distance', frame=f)

def rain_anim(r, f0, f1, seed=3):
    """re-scatter the rain sheet every frame (constant keys) so drops never repeat"""
    rng = random.Random(seed)
    base = r.location.copy()
    for f in range(f0, f1 + 1):
        r.location = base + V(rng.uniform(-.6, .6), rng.uniform(-.6, .6), rng.uniform(-.5, .5)); r.keyframe_insert('location', frame=f - .5)
    for fc in _fcurves(r.animation_data.action):
        for k in fc.keyframe_points: k.interpolation = 'CONSTANT'

def dup(root, loc, rot_z, scale=1.):
    """instance of an imported character: copy the empty + children sharing mesh data, with its own skeleton"""
    nr = root.copy(); col.objects.link(nr)
    rig = K.char_rig(root); nrig = None
    if rig:
        nrig = rig.copy(); col.objects.link(nrig); nrig.parent = nr; nrig.animation_data_clear(); nr['rig'] = nrig.name
    for ch in root.children:
        if ch is rig: continue
        c = ch.copy(); col.objects.link(c); c.parent = nr
        for m in c.modifiers:
            if m.type == 'ARMATURE' and nrig: m.object = nrig
    nr.location = loc; nr.rotation_euler = (0, 0, rot_z); nr.scale = (scale,) * 3
    return nr

def flicker(light, f0, f1, base, seed=1, p_off=.12):
    rng = random.Random(seed)
    for f in range(f0, f1 + 1):
        light.energy = base * (0 if rng.random() < p_off else rng.uniform(.8, 1.05)); light.keyframe_insert('energy', frame=f)
    for fc in _fcurves(light.animation_data.action):
        for k in fc.keyframe_points: k.interpolation = 'CONSTANT'

def lightning(sun, f_hits, base=.35, peak=9.0):
    sun.energy = base; sun.keyframe_insert('energy', frame=0)
    for fh in f_hits:
        for df, v in ((-1, base), (0, peak), (1, peak * .3), (2, peak * .8), (5, base)):
            sun.energy = v; sun.keyframe_insert('energy', frame=fh + df)
    for fc in _fcurves(sun.animation_data.action):
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'

def moon_obj():
    return bpy.data.lights.get('moon')

def nt_car(loc, rot_z, lights_on=True, glow=60):
    car, parts = K.night_terror(V(loc), rot_z, col)
    for o in list(parts):
        if o.name in ('Camera', 'Cube', 'Light') or o.name.startswith(('Camera', 'Cube', 'Light')) and o.parent is car:
            bpy.data.objects.remove(o, do_unlink=True); parts.remove(o)
    glowm = bpy.data.materials.new('HeadGlow'); glowm.use_nodes = True
    b = glowm.node_tree.nodes['Principled BSDF']; b.inputs['Emission Color'].default_value = (1, 1, 1, 1)
    b.inputs['Emission Strength'].default_value = glow if lights_on else 0
    for o in parts:
        if o.type == 'MESH' and 'projector lens' in o.name.lower():
            o.data.materials.clear(); o.data.materials.append(glowm)
    # headlight spots parented to the car (car local: nose ~ y -3.4, lamps x -.52 / .98 rel root .4,-2)
    spots = []
    for hx in (-.52, .98):
        hl = bpy.data.lights.new('head', 'SPOT'); hl.energy = 6500 if lights_on else 0; hl.color = K.C('#e8f0ff')
        hl.spot_size = math.radians(34); hl.spot_blend = .3; hl.shadow_soft_size = .06
        ho = bpy.data.objects.new('head', hl); col.objects.link(ho); ho.parent = car
        ho.location = (hx, -3.65, .88); ho.rotation_euler = (math.radians(-88.5), 0, 0); spots.append(hl)
    return car, parts, glowm, spots

def spin_wheels(parts, f0, f1, dist):
    """v3: pivot per wheel at its true axle, oriented like the car (no wobble when the car yaws), rolling FORWARD
    (car drives toward its local -y), with many motion-blur steps so a fast wheel smears the right way instead of strobing."""
    import mathutils
    bpy.context.view_layer.update()
    for asm in [o for o in parts if o.name.endswith('wheel assembly')]:
        subs = [c for c in asm.children if not c.name.startswith('Brake')]
        meshes = [m for s in subs for m in [s] + list(s.children_recursive) if m.type == 'MESH']
        if not meshes: continue
        R = asm.matrix_world.to_quaternion().to_matrix().to_4x4(); Ri = R.inverted()
        pts = [Ri @ (m.matrix_world @ V(c)) for m in meshes for c in m.bound_box]       # bbox in car-aligned frame
        mn = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        ctr = R @ ((mn + mx) / 2); rad = (mx.z - mn.z) / 2
        pv = bpy.data.objects.new('pivot', None); col.objects.link(pv)
        pv.parent = asm; pv.matrix_world = mathutils.Matrix.Translation(ctr) @ R
        bpy.context.view_layer.update()
        for s in subs:
            mw = s.matrix_world.copy(); s.parent = pv; s.matrix_world = mw
        for m in meshes:
            m.cycles.use_motion_blur = True; m.cycles.motion_steps = 6
        pv.rotation_mode = 'XYZ'; r0 = pv.rotation_euler.copy()
        pv.keyframe_insert('rotation_euler', frame=f0)
        pv.rotation_euler = (r0.x + dist / max(rad, .2), r0.y, r0.z); pv.keyframe_insert('rotation_euler', frame=f1)
        linear(pv)
    pv0 = [o for o in bpy.data.objects if o.name.startswith('pivot')]
    for o in pv0: o.cycles.motion_steps = 6


def suspension(car, f0, f1, amp=.008, pitch=None, seed=3):
    """body floats on springs above the wheels: everything except the wheel assemblies moves on a 'body' empty with a
    small, damped bob and roll; pitch = [(frame, degrees)] for squat under throttle / dive under braking."""
    body = bpy.data.objects.new('body', None); col.objects.link(body); body.parent = car
    body.location = (0, 0, .6); bpy.context.view_layer.update()
    for ch in list(car.children):
        if ch is body or ch.name.endswith('wheel assembly'): continue
        mw = ch.matrix_world.copy(); ch.parent = body; ch.matrix_world = mw
    nz = [A.Noise(seed * 7 + i) for i in range(3)]
    pk = pitch or [(f0, 0), (f1, 0)]
    for f in range(f0, f1 + 1):
        tt = f / 24
        p = 0.
        for (fa, va), (fb, vb) in zip(pk, pk[1:]):
            if fa <= f <= fb: u = (f - fa) / max(1, fb - fa); u = u * u * (3 - 2 * u); p = va + (vb - va) * u
        body.location = (0, 0, .6 + amp * nz[0](tt * 2.3))
        body.rotation_euler = (math.radians(p + .25 * nz[1](tt * 1.9)), math.radians(.35 * nz[2](tt * 1.6)), 0)
        body.keyframe_insert('location', frame=f); body.keyframe_insert('rotation_euler', frame=f)
    return body


def render(f0, f1, res=None, samp=None):
    fr = os.environ.get('FR')
    if fr: f0, f1 = map(int, fr.split(','))
    slow = float(os.environ.get('SLOW', '1'))
    if slow > 1:      # true slow motion: Blender time-remaps the animation, every in-between frame is a real render
        sc.render.frame_map_old = 100; sc.render.frame_map_new = int(100 * slow); f1 = int(f1 * slow)
    sc.frame_start, sc.frame_end = f0, f1; sc.frame_step = int(os.environ.get('STEP', '1'))
    r = float(os.environ.get('RES', res or '.5'))
    K.setup_render(sc, int(1080 * r) // 2 * 2, int(1920 * r) // 2 * 2, int(os.environ.get('SAMP', samp or '16')))
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = float(os.environ.get('MB', '.5'))
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = os.path.join(OUT, 'f')
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = .05
    sc.cycles.volume_step_rate = float(os.environ.get('VSTEP', '6')); sc.cycles.max_bounces = 4; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.transmission_bounces = 4
    sc.render.use_persistent_data = os.environ.get('PERSIST', '1') == '1'
    if os.environ.get('DEVICE') == 'GPU':
        pr = bpy.context.preferences.addons['cycles'].preferences; pr.compute_device_type = 'OPTIX'; pr.get_devices()
        for d in pr.devices: d.use = d.type == 'OPTIX'
        sc.cycles.device = 'GPU'; sc.cycles.denoiser = 'OPTIX'
    sc.render.use_overwrite = False
    sc.render.use_placeholder = True
    if os.environ.get('THREADS'): sc.render.threads_mode = 'FIXED'; sc.render.threads = int(os.environ['THREADS'])
    if os.environ.get('DRY'):    # debug: what does the camera see first toward each target (DRY=x,y,z;x,y,z or 'auto')
        dg = bpy.context.evaluated_depsgraph_get(); f_ = int(os.environ.get('DRYF', f0)); sc.frame_set(f_); dg = bpy.context.evaluated_depsgraph_get()
        cam = sc.camera; co = cam.matrix_world.translation.copy(); fw = (cam.matrix_world.to_3x3() @ Vector((0, 0, -1))).normalized()
        print('DRYCAM', f_, tuple(round(v, 2) for v in co), 'fwd', tuple(round(v, 2) for v in fw), 'lens', round(cam.data.lens, 1))
        tg = [Vector(tuple(map(float, t.split(',')))) for t in os.environ['DRY'].split(';') if t != 'auto']
        tg += [co + fw * 5]
        for o in bpy.data.objects:
            if o.type == 'ARMATURE' or o.name.lower().startswith(('stalker', 'sam')) and o.type == 'EMPTY': tg.append(o.matrix_world.translation.copy())
        for t in tg[:12]:
            ok, loc, nrm, idx, ob, _ = sc.ray_cast(dg, co, (t - co).normalized())
            print('DRYRAY to', tuple(round(v, 2) for v in t), 'hit', ob.name if ok else None, round((loc - co).length, 2) if ok else '-', 'dist', round((t - co).length, 2))
        for o in bpy.data.objects:
            if o.type == 'ARMATURE': print('DRYRIG', o.name, tuple(round(v, 2) for v in o.matrix_world.translation))
        return
    if os.environ.get('BLEND'): bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f'c{SHOT}.blend'))
    bpy.ops.render.render(animation=True)


# ------------------------------------------------------------------ v2 helpers
def bone_w(rootobj, bone, f):
    rig = K.char_rig(rootobj); sc.frame_set(f); bpy.context.view_layer.update()
    return rig.matrix_world @ rig.pose.bones[bone].head


# ------------------------------------------------------------------ v5: real recorded handheld shake (Camera Shakify data, CC0)
import shakify_data as _SK
import numpy as _np
_SKC = {}
def _shake_tab(preset):
    if preset not in _SKC:
        d = _SK.SHAKE_LIST[preset][2]; chans = []
        for key in (('location', 0), ('location', 1), ('location', 2), ('rotation_euler', 0), ('rotation_euler', 1), ('rotation_euler', 2)):
            v = _np.array([p[1] for p in d[key]]); v = v - v.mean(); chans.append(v)
        n = min(len(c) for c in chans); a = _np.stack([c[:n] for c in chans], 1)
        a = _np.concatenate([a, a[::-1]], 0)                    # ping-pong loop, no jump at the seam
        ls = a[:, :3].std() + 1e-9; rs = a[:, 3:].std() + 1e-9
        _SKC[preset] = (a, ls, rs)
    return _SKC[preset]
def real_shake(f, preset, loc_amp, rot_deg, seed=0):
    a, ls, rs = _shake_tab(preset); i = (int(f) + seed * 37) % len(a); v = a[i]
    return V(tuple(v[:3] / ls * loc_amp)), [x / rs * math.radians(rot_deg) for x in v[3:]]
SHAKE_PRESET = os.environ.get('SHAKE', 'WALK_TO_THE_STORE')

def shot_cam(c, keys, f0, f1, shake=.0, rshake=.0, freq=1.6, seed=1):
    """keys: [(frame, loc, target, lens, focus)] interpolated smoothly; handheld noise on top, keyed every frame"""
    nz = [A.Noise(seed * 10 + i) for i in range(6)]
    c.data.dof.use_dof = True
    fr = [k[0] for k in keys]
    for f in range(f0, f1 + 1):
        i = max(0, min(len(keys) - 2, sum(1 for x in fr if x <= f) - 1))
        a, b = keys[i], keys[min(i + 1, len(keys) - 1)]
        t = 0 if b[0] == a[0] else max(0., min(1., (f - a[0]) / (b[0] - a[0]))); t = t * t * (3 - 2 * t)
        lp = lambda u, v: V(u).lerp(V(v), t)
        loc = lp(a[1], b[1]); tgt = lp(a[2], b[2])
        dl, dr = real_shake(f, SHAKE_PRESET, shake, rshake, seed)
        loc = loc + dl
        c.location = loc; aim(c, tgt)
        c.rotation_euler.x += dr[0]; c.rotation_euler.y += dr[1] * .6; c.rotation_euler.z += dr[2]
        c.data.lens = a[3] + (b[3] - a[3]) * t; c.data.dof.focus_distance = a[4] + (b[4] - a[4]) * t
        for p in ('location', 'rotation_euler'): c.keyframe_insert(p, frame=f)
        c.data.keyframe_insert('lens', frame=f); c.data.dof.keyframe_insert('focus_distance', frame=f)

def kick(c, frames, amp=1.5):
    """camera jolt (impact / scream): add decaying shake to existing keys"""
    nz = A.Noise(99)
    for f0 in frames:
        for k in range(10):
            f = f0 + k; sc.frame_set(f); e = amp * math.exp(-k / 3.)
            c.rotation_euler.x += math.radians(e * nz(f * .9)); c.rotation_euler.z += math.radians(e * nz(f * .7 + 5))
            c.keyframe_insert('rotation_euler', frame=f)

def steam(loc, h=4., r=.9, dens=.5, seed=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(loc[0], loc[1], h / 2)); o = bpy.context.object
    o.scale = (r * 2, r * 2, h); bpy.ops.object.transform_apply(scale=True)
    for c_ in o.users_collection: c_.objects.unlink(o)
    col.objects.link(o)
    m = bpy.data.materials.new('Steam'); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; l = nt.links
    for x in list(n): n.remove(x)
    out = n.new('ShaderNodeOutputMaterial'); pv = n.new('ShaderNodeVolumePrincipled'); l.new(pv.outputs[0], out.inputs['Volume'])
    tc = n.new('ShaderNodeTexCoord'); nn = n.new('ShaderNodeTexNoise'); nn.noise_dimensions = '4D'
    nn.inputs['Scale'].default_value = 1.6; nn.inputs['Detail'].default_value = 6
    mp = n.new('ShaderNodeMapping'); l.new(tc.outputs['Object'], mp.inputs['Vector']); l.new(mp.outputs[0], nn.inputs['Vector'])
    dr = mp.inputs['Location'].driver_add('default_value', 2); dr.driver.expression = '-frame / 40.0'
    dw = nn.inputs['W'].driver_add('default_value'); dw.driver.expression = f'frame / 60.0 + {seed}'
    sep = n.new('ShaderNodeSeparateXYZ'); l.new(tc.outputs['Object'], sep.inputs[0])
    rad = n.new('ShaderNodeVectorMath'); rad.operation = 'LENGTH'
    cx = n.new('ShaderNodeCombineXYZ'); l.new(sep.outputs['X'], cx.inputs[0]); l.new(sep.outputs['Y'], cx.inputs[1]); l.new(cx.outputs[0], rad.inputs[0])
    widen = K.math_n(n, l, 'ADD', .15, K.math_n(n, l, 'MULTIPLY', K.math_n(n, l, 'ADD', sep.outputs['Z'], h / 2), .12))
    radial = K.math_n(n, l, 'SUBTRACT', 1., K.math_n(n, l, 'DIVIDE', rad.outputs['Value'], widen))
    fall = K.mrange(n, l, sep.outputs['Z'], -h / 2, h / 2, 1., 0.)
    d = K.math_n(n, l, 'MULTIPLY', K.math_n(n, l, 'MULTIPLY', K.mrange(n, l, nn.outputs['Fac'], .45, .75), K.math_n(n, l, 'MAXIMUM', radial, 0.)), fall)
    l.new(K.math_n(n, l, 'MULTIPLY', d, dens), pv.inputs['Density']); pv.inputs['Color'].default_value = (.8, .82, .85, 1)
    o.data.materials.append(m); o.visible_shadow = False
    K.box('manhole', col, (loc[0], loc[1], .004), (.7, .7, .01), K.metal('Manhole', '#1a1a1a', .5))
    return o

def wires(xs=7.5, y0=10, y1=-90, n=6, seed=3):
    rr = random.Random(seed); m = K.metal('Wire', '#050505', .6)
    for k in range(n):
        y = rr.uniform(y1, y0); z0 = rr.uniform(7, 12); sag = rr.uniform(.6, 1.6)
        pts = [V((-xs + 2 * xs * i / 12, y + rr.uniform(-1, 1) * (i in (0, 12)), z0 - sag * (1 - ((i - 6) / 6) ** 2))) for i in range(13)]
        L.setmat(L.tube('wire', pts, .012, col, sides=5), m)

def debris(y0, y1, nn=60, seed=4):
    rr = random.Random(seed); ms = [K.concrete('Paper', '#8a8478'), K.concrete('Leaf', '#2a2416'), K.concrete('Can', '#5a1a14')]
    for k in range(nn):
        sz = rr.uniform(.08, .3)
        o = K.box('litter', col, (rr.uniform(-5.6, 5.6), rr.uniform(y1, y0), .004), (sz, sz * rr.uniform(.4, 1), .003), rr.choice(ms))
        o.rotation_euler.z = rr.uniform(0, 6.3)

def dress(rng, near_y=0., far_y=-60):
    steam((rng.uniform(-3, 3), near_y - rng.uniform(8, 14)), h=5, seed=1)
    steam((rng.uniform(-3, 3), near_y - rng.uniform(26, 36)), h=6, dens=.35, seed=2)
    wires(y0=near_y + 5, y1=far_y)
    debris(near_y + 4, far_y + 20)

def base_street(seed=5, length=140, fog=.018, dead=(1, 4), near=0., wrecks=True, exposure=1.2):
    rng = K.street(col, length=length, seed=seed, dead_lamps=dead)
    K.sky(sc, fog=fog)
    if wrecks:
        paints = ['#4a1a16', '#1e2a3a', '#5a5248', '#22301e', '#6a6a66']
        for i, (p, rr) in enumerate([((-2.9, -5.2, 0), .3), ((3.6, -20, 0), -.4), ((-1.8, -31, 0), 1.2), ((4.0, -44, 0), .1), ((-3.8, -58, 0), -.2)]):
            K.sedan(col, V(p), rr, K.carpaint(f'Paint{i}', paints[i % 5]), rng)
    dress(rng, near)
    sc.view_settings.exposure = exposure
    return rng

def rain_here(center, size, count, f0=1, f1=120):
    r = K.rain(col, w=.007, center=center, size=size, count=count); rain_anim(r, f0, f1); return r

def lamp_spot(loc, energy=2600, col_='#ffb060', size=70, flick=None):
    hl = bpy.data.lights.new('pool', 'SPOT'); hl.energy = energy; hl.color = K.C(col_); hl.spot_size = math.radians(size); hl.spot_blend = .8
    ho = bpy.data.objects.new('pool', hl); col.objects.link(ho); ho.location = loc
    if flick: flicker(hl, flick[0], flick[1], energy, seed=4, p_off=.08)
    return hl

def area(loc, target, energy, size, col_):
    a = bpy.data.lights.new('a', 'AREA'); a.energy = energy; a.size = size; a.color = K.C(col_)
    o = bpy.data.objects.new('a', a); col.objects.link(o); o.location = loc; aim(o, target); return a

# ------------------------------------------------------------------ cuts
def crawler_set(nf):
    base_street(5); lamp_spot((1.2, -24, 7.5), flick=(1, nf)); lamp_spot((2.5, -3, 6.8), 1800, '#ffae5a', 80)
    area((0, -70, 1.2), (0, 0, 1.2), 4000, 3, '#cfe0ff')
    K.char('husk', V(1.0, -24, 0), math.radians(-10))
    cr = K.char('crawler', V(-.5, -4.2, 0), math.radians(-170))
    A.crawl(K.char_rig(cr), cr, 1, nf, speed=.42)
    rain_here((0, -12, 0), (16, 28, 12), 3500, 1, nf)
    return cr

def cut2():   # macro: hooked hand slaps into a puddle
    nf = 36; cr = crawler_set(nf)
    h = bone_w(cr, 'wrist.R', 20); hd = bone_w(cr, 'head', 20)
    tgt = h.lerp(hd, .3)
    p1 = h + V((.25, 1.25, .1)); p2 = h + V((.2, 1.0, .09))
    lamp_spot(h + V((.6, .8, 2.2)), 220, '#ffc890', 60)
    c = camera(50)
    shot_cam(c, [(1, p1, tgt, 50, (p1 - h).length), (nf, p2, tgt, 50, (p2 - h).length)], 1, nf, shake=.006, rshake=.25, seed=2)
    c.data.dof.aperture_fstop = 2.8; return 1, nf

def cut3():   # low handheld: the Crawler drags itself at the lens
    nf = 48; cr = crawler_set(nf)
    h1 = bone_w(cr, 'head', 1); h2 = bone_w(cr, 'head', nf)
    c = camera(24)
    p1 = h1 + V((.35, 2.3, .12)); p2 = h2 + V((.25, 1.35, .1))
    shot_cam(c, [(1, p1, h1 + V((0, 0, .05)), 24, (p1 - h1).length), (nf, p2, h2 + V((0, 0, .05)), 24, (p2 - h2).length)], 1, nf, shake=.015, rshake=.6, seed=3)
    c.data.dof.aperture_fstop = 2.2; return 1, nf

def cut4():   # ECU of the crawler's face, rack focus
    nf = 24; cr = crawler_set(nf)
    h = bone_w(cr, 'head', 12)
    c = camera(85)
    shot_cam(c, [(1, h + V((.35, .95, .02)), h, 85, 2.2), (nf, h + V((.3, .8, .04)), h, 85, .85)], 1, nf, shake=.004, rshake=.2, seed=4)
    c.data.dof.aperture_fstop = 1.6; return 1, nf

def roof_set(nf, lightning_at=(14,)):
    rng = K.street(col, length=160, seed=7); K.sky(sc, fog=.012)
    mat = K.facade('HeroFacade', '#2e3236', lit=.25, seed=3.3, brick=True)
    K.building(col, 16, -20, 12, 12, 30, mat, rng, 1)
    K.box('roof', col, (16, -20, 30.02), (11.8, 11.8, .04), K.concrete('Roof', '#2a2928'))
    K.box('tank', col, (19, -17, 32), (2.4, 2.4, 3), K.metal('Tank', '#3a2e26', .7))
    ant = L.tube('antenna', [V(18, -24, 30), V(18, -24, 38)], .04, col, sides=6); L.setmat(ant, K.metal('Ant', '#202020'))
    wires(y0=-10, y1=-40, n=5)
    s = K.char('screamer', V(10.2, -20, 30.4), math.radians(-128))
    lightning(moon_obj(), list(lightning_at), peak=7.0)
    area((13, -23, 33), (10.2, -20, 31.4), 500, 2, '#b8c8ff'); area((7, -18, 33), (10.2, -20, 31.4), 600, 2, '#9ab0ff')
    rain_here((8, -18, 26), (14, 14, 14), 2500, 1, nf)
    sc.view_settings.exposure = 1.1
    return s

def cut5():   # rooftop wide, low: she stands still, lightning
    nf = 36; s = roof_set(nf, (16,)); A.idle(K.char_rig(s), 1, nf, amp=.5)
    c = camera(20)
    shot_cam(c, [(1, (4.4, -13.5, 28.6), (10.3, -20.1, 31.6), 34, 8.5), (nf, (4.8, -14.0, 28.8), (10.3, -20.1, 31.6), 38, 8.2)], 1, nf, shake=.03, rshake=.3, seed=5)
    c.data.dof.aperture_fstop = 4; return 1, nf

def cut6():   # CU: head snaps back, the scream, shake
    nf = 36; s = roof_set(nf, (10, 26)); A.scream(K.char_rig(s), 1, nf, f_scream=8, amp=.25)
    h = bone_w(s, 'head', 1)
    c = camera(45)
    shot_cam(c, [(1, h + V((-.95, .75, .6)), h + V((0, 0, .02)), 45, 1.35), (nf, h + V((-.75, .6, .5)), h + V((0, 0, .02)), 52, 1.1)], 1, nf, shake=.01, rshake=.4, seed=6)
    kick(c, [8, 9, 11], 2.2)
    c.data.dof.aperture_fstop = 2.0; return 1, nf

def horde_set(nf, n=40, near=-7., mode='shamble', face=180):
    rng = base_street(21, dead=(0, 2, 3, 5), fog=.024, wrecks=False)
    paints = ['#4a1a16', '#1e2a3a', '#5a5248']
    for i, (p, rr) in enumerate([((-4.4, -14, 0), .5), ((4.6, -30, 0), -.2), ((-1.5, -46, 0), 1.0)]):
        K.sedan(col, V(p), rr, K.carpaint(f'P{i}', paints[i]), rng)
    names = ['husk', 'runner', 'walker2']
    roots = [K.char(nm, V(0, -500 - i * 5, 0), 0) for i, nm in enumerate(names)]
    pts = []; out = []
    for i in range(n):
        for _ in range(40):
            p = V((rng.uniform(-5.4, 5.4), near - rng.uniform(0, 34), 0))
            if all((p - q).length > 1.05 for q in pts): break
        pts.append(p)
        w = [0, 0, 1, 2, 2][rng.randrange(5)]
        d = dup(roots[w], p, math.radians(face + rng.uniform(-22, 22)), rng.uniform(.94, 1.06)); out.append(d)
        rg = K.char_rig(d)
        if mode == 'shamble':
            A.shamble(rg, d, 1, nf, speed=rng.uniform(.45, .8), period=rng.uniform(1.15, 1.6), phase=rng.uniform(0, 6.3),
                      limp=rng.uniform(.1, .6), seed=i, arms='reach' if rng.random() < .3 else 'dangle')
        else:
            A.idle(rg, 1, nf, seed=i)
    for r in roots: r.location.z = -50
    lamp_spot((-1, -12, 8), 3000, size=80, flick=(1, nf)); area((0, -75, 3), (0, 0, 3), 6000, 5, '#cfe0ff')
    rain_here((0, -14, 0), (18, 36, 16), 4500, 1, nf)
    sc.view_settings.exposure = 1.25
    return out

def cut7():   # whip pan onto three husks turning toward the sound
    nf = 24; hs = horde_set(nf, n=14, near=-4.5, mode='idle')
    for k, d in enumerate(hs[:6]):
        rg = K.char_rig(d)
        for f in range(1, nf + 1):           # head + chest snap round to camera after the pan
            u = max(0., min(1., (f - 8 - k) / 6.)); u = u * u * (3 - 2 * u)
            for bn, ax in (('head', 2), ('neck01', 2), ('spine05', 2)):
                pb = rg.pose.bones[bn]; e = pb.rotation_euler.copy(); e[ax] += math.radians(-28 * u * (1 if k % 2 else -1)); pb.rotation_euler = e
                pb.keyframe_insert('rotation_euler', frame=f)
    c = camera(35)
    shot_cam(c, [(1, (.6, -1.2, 1.55), (-12, -8, 1.4), 45, 4.5), (7, (.6, -1.2, 1.55), (0, -7, 1.55), 45, 4.5), (nf, (.5, -1.5, 1.55), (0, -7, 1.55), 50, 4.2)],
             1, nf, shake=.015, rshake=.4, seed=7)
    c.data.dof.aperture_fstop = 2.4; return 1, nf

def cut8():   # long take: the horde shambles at us out of the fog, slow pull back
    nf = 60; horde_set(nf, n=32, near=-6.)
    c = camera(28)
    shot_cam(c, [(1, (.4, -1.5, 1.2), (0, -20, 1.4), 28, 9), (nf, (.6, 1.8, 1.05), (0, -20, 1.3), 28, 9.5)], 1, nf, shake=.03, rshake=.5, seed=8)
    c.data.dof.aperture_fstop = 3.2; return 1, nf

def cut9():   # ground level: feet splashing through puddles, tracking back
    nf = 36; hs = horde_set(nf, n=26, near=-3.2)
    c = camera(30)
    shot_cam(c, [(1, (.3, -.6, .22), (0, -6, .35), 30, 3.0), (nf, (.3, .4, .22), (0, -6, .35), 30, 3.1)], 1, nf, shake=.015, rshake=.5, seed=9)
    c.data.dof.aperture_fstop = 2.2; return 1, nf

def garage_set(nf, ign=6):
    K.sky(sc, moon=False, fog=.008)
    K.box('floor', col, (0, -2, -.05), (14, 20, .1), K.asphalt())
    wall = K.concrete('GarageWall', '#3a3836')
    K.box('wallL', col, (6, -2, 3), (.2, 20, 6), wall); K.box('wallR', col, (-5.5, -2, 3), (.2, 20, 6), wall)
    K.box('back', col, (0, 6, 3), (14, .2, 6), wall); K.box('ceil', col, (0, -2, 6), (14, 20, .2), wall)
    door = K.metal('Door', '#2a2c2e', .55)
    for k in range(14): K.box('slat', col, (0, -12, 2.2 + k * .26), (9, .08, .22), door)
    K.box('tube', col, (.4, -2, 5.85), (.12, 2.6, .06), K.emit('Fluo', '#cfe8ff', 25))
    ft = bpy.data.lights.new('fluo', 'AREA'); ft.shape = 'RECTANGLE'; ft.size = .2; ft.size_y = 2.6; ft.energy = 160; ft.color = K.C('#cfe8ff')
    fo = bpy.data.objects.new('fluo', ft); col.objects.link(fo); fo.location = (.4, -2, 5.75); flicker(ft, 1, nf, 160, seed=2, p_off=.35)
    K.box('bench', col, (-4.5, 2, .45), (1.2, 4, .9), K.metal('Bench', '#3a2a20', .7))
    car, parts, glowm, spots = nt_car((.4, -2, 0), 0, lights_on=True)
    em = glowm.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    for f, v in ((1, 0 if ign > 1 else 30), (ign, 0), (ign + 1, 30), (ign + 2, 4), (ign + 4, 30), (nf, 24)):
        if f < 1: continue
        em.default_value = v; em.keyframe_insert('default_value', frame=f)
        for s_ in spots: s_.energy = v * 40; s_.keyframe_insert('energy', frame=f)
    sc.view_settings.exposure = 1.0
    return car

def cut10():  # garage, dark: the Night Terror's headlights ignite (close, low)
    nf = 36; garage_set(nf, ign=11)
    c = camera(35)
    shot_cam(c, [(1, (2.2, -7.5, .55), (.3, -5.3, .9), 35, 2.3), (nf, (1.7, -6.8, .66), (.42, -5.3, .94), 38, 1.8)], 1, nf, shake=.008, rshake=.25, seed=10)
    kick(c, [11], 1.2); c.data.dof.aperture_fstop = 2.0; return 1, nf

def cut11():  # garage wide: lights blazing, slow dolly at the car, door half open, steam on the floor
    nf = 36; garage_set(nf, ign=-5)
    steam((2.5, -8), h=1.2, r=2.0, dens=.25, seed=5)
    c = camera(24)
    shot_cam(c, [(1, (3.6, -10.8, 1.1), (.4, -2, .9), 24, 7.5), (nf, (3.0, -9.4, 1.0), (.4, -2, .9), 24, 6.4)], 1, nf, shake=.012, rshake=.3, seed=11)
    c.data.dof.aperture_fstop = 2.8; return 1, nf

def chase_set(nf, D, y0=14.):
    rng = K.street(col, length=220, seed=13, dead_lamps=(1, 4)); K.sky(sc, fog=.009)
    paints = ['#4a1a16', '#1e2a3a', '#5a5248', '#22301e']
    for i in range(7):
        K.sedan(col, V((rng.choice([-1, 1]) * rng.uniform(4.9, 5.3), -24 - i * 22, 0)), rng.uniform(-.12, .12), K.carpaint(f'P{i}', paints[i % 4]), rng)
    dress(rng, 0, -120)
    car, parts, glowm, spots = nt_car((.4, y0, 0), 0)
    for sp in spots: sp.energy = 2500
    key(car, 1, loc=V((.4, y0, 0))); key(car, nf, loc=V((.4, y0 - D, 0))); linear(car)
    spin_wheels(parts, 1, nf, D); suspension(car, 1, nf, amp=.012, pitch=[(1, -.7), (nf, -.5)])
    r = K.rain(col, w=.007, center=(0, 0, 0), size=(18, 30, 12), count=4000); r.parent = car; rain_anim(r, 1, nf)
    sc.view_settings.exposure = 1.1
    return rng, car

def runners(rng, nf, n, y_from, y_to, speed_rng=(5.2, 6.4)):
    root = K.char('runner', V(0, -700, 0), 0); out = []
    for i in range(n):
        x = -rng.uniform(1.6, 4.8) if rng.random() < .7 else rng.uniform(2.4, 2.8)
        d = dup(root, V((x, rng.uniform(y_to, y_from), 0)), math.radians(rng.uniform(-8, 8)))
        A.sprint(K.char_rig(d), d, 1, nf, speed=rng.uniform(*speed_rng), phase=rng.uniform(0, 6.3), seed=i); out.append(d)
    return out

def cut12():  # tyre CU smashing through a puddle at speed
    nf = 36; D = 36.; rng, car = chase_set(nf, D)
    c = camera(32); c.parent = car
    for f in range(1, nf + 1):
        tt = f / 24; c.location = V((3.4 + .03 * math.sin(tt * 9), -5.2 + .02 * math.sin(tt * 13), .32 + .015 * math.sin(tt * 17)))
        aim(c, V((1.8, -3.6, .38))); c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 2.2; c.data.dof.aperture_fstop = 2.0
    return 1, nf

def cut13():  # tracking wide: the Night Terror tears through sprinting runners
    nf = 60; D = 60.; rng, car = chase_set(nf, D)
    runners(rng, nf, 9, 6, -40)
    c = camera(24); c.parent = car
    for f in range(1, nf + 1):
        u = (f - 1) / (nf - 1); tt = f / 24
        c.location = V((3.3 - .4 * u, -7.8 + 3.6 * u, .6 + .35 * u)) + V((.04 * math.sin(tt * 7), 0, .03 * math.sin(tt * 11)))
        aim(c, V((.6, -3.2 + 1.2 * u, .95))); c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 5; c.data.dof.aperture_fstop = 4
    return 1, nf

def cut14():  # side tracking: a runner sprints right next to the lens
    nf = 24; D = 26.; rng, car = chase_set(nf, D, y0=30)
    rs = runners(rng, nf, 1, 6, 6, (5.8, 5.8))
    r0 = rs[0]; r0.location = V((-2.6, 6, 0)); K.char_rig(r0)
    r0.animation_data_clear(); A.sprint(K.char_rig(r0), r0, 1, nf, speed=6.0, seed=1)
    c = camera(40)
    for f in range(1, nf + 1):
        tt = f / 24; y = 6 - 6.0 * (f - 1) / 24
        c.location = V((-4.5 + .04 * math.sin(tt * 9), y - .6, 1.25 + .05 * math.sin(tt * 12))); aim(c, V((-2.5, y - .4, 1.15)))
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 2.0; c.data.dof.aperture_fstop = 2.0
    sp = bpy.data.lights.new('camlight', 'SPOT'); sp.energy = 900; sp.color = K.C('#dfe8ff'); sp.spot_size = math.radians(70); sp.spot_blend = .8
    so = bpy.data.objects.new('camlight', sp); col.objects.link(so); so.parent = c; so.location = (.6, .4, 0)
    sc.view_settings.exposure = 1.6
    return 1, nf

def cut15():  # low static camera on the road: the Night Terror bursts out of the fog and blasts past
    nf = 36; D = 46.; rng, car = chase_set(nf, D, y0=14)
    runners(rng, nf, 4, -10, -30)
    for sp in bpy.data.lights:
        if sp.name.startswith('head'): sp.energy = 1800
    c = camera(24)
    shot_cam(c, [(1, (2.6, -27, .35), (.4, 0, .9), 24, 20), (nf, (2.6, -27, .35), (.6, -24, .9), 24, 4)], 1, nf, shake=.01, rshake=.3, seed=15)
    kick(c, [26], 2.5); c.data.dof.aperture_fstop = 4; return 1, nf

def brute_set(nf, car_anim=True):
    rng = K.street(col, length=140, seed=9, dead_lamps=(0, 1, 2, 3, 5, 6)); K.sky(sc, fog=.016)
    paints = ['#4a1a16', '#1e2a3a', '#5a5248']
    for i, (p, rr) in enumerate([((4.2, -24, 0), -.5), ((-3.9, -33, 0), .3), ((3.0, -48, 0), 1.4)]):
        K.sedan(col, V(p), rr, K.carpaint(f'Paint{i}', paints[i]), rng)
    dress(rng, -4, -60)
    car, parts, glowm, spots = nt_car((.4, -2, 0), math.radians(4))
    br = K.char('brute', V(2.0, -14.5, 0), math.radians(188))
    area((0, -30, 6), (0, -10, 0), 2500, 4, '#7a9aff')
    rain_here((0, -10, 0), (14, 26, 10), 3500, 1, nf)
    sc.view_settings.exposure = .8
    return rng, car, parts, br

def cut16():  # skid: the car slides in toward the camera with spray
    nf = 36; rng, car, parts, br = brute_set(nf)
    A.idle(K.char_rig(br), 1, nf, amp=.6)
    for sp in bpy.data.lights:
        if sp.name.startswith('head'): sp.energy = 1600
    key(car, 1, loc=V((-1.2, 16, 0)), rot=(0, 0, math.radians(-6))); key(car, 20, loc=V((.2, -1.0, 0)), rot=(0, 0, math.radians(24)))
    key(car, 30, loc=V((.4, -2, 0)), rot=(0, 0, math.radians(30)))
    spin_wheels(parts, 1, 20, 18); suspension(car, 1, nf, amp=.006, pitch=[(1, 0), (6, 1.8), (20, 2.4), (24, -.8), (28, .4), (32, -.1), (nf, 0)])
    c = camera(26)
    shot_cam(c, [(1, (3.6, -7.5, .45), (.6, 6, .8), 26, 9), (20, (3.6, -7.5, .45), (.4, -1.6, .8), 26, 5.2), (nf, (3.5, -7.3, .5), (.4, -2, .8), 26, 5.2)],
             1, nf, shake=.02, rshake=.4, seed=16)
    kick(c, [20], 2.5); c.data.dof.aperture_fstop = 2.8; return 1, nf

def cut17():  # over the shoulder: the Brute stomps out of the fog into the beams
    nf = 60; rng, car, parts, br = brute_set(nf)
    br.location = V((1.6, -17.5, 0)); A.stomp(K.char_rig(br), br, 1, nf, speed=1.0)
    c = camera(30)
    shot_cam(c, [(1, (1.9, 3.2, 1.75), (1.5, -15, 1.9), 30, 16), (nf, (1.7, 2.2, 1.7), (1.5, -13, 2.1), 34, 13.5)], 1, nf, shake=.02, rshake=.35, seed=17)
    for f in range(20, nf, 25): kick(c, [f], .9)
    c.data.dof.aperture_fstop = 2.8; return 1, nf

def cut18():  # push-in on the Brute's face as it roars
    nf = 24; rng, car, parts, br = brute_set(nf)
    br.location = V((1.7, -11.0, 0)); rg = K.char_rig(br); A.scream(rg, 1, nf, f_scream=6, amp=.35)
    h = bone_w(br, 'head', 1)
    c = camera(55)
    shot_cam(c, [(1, h + V((-.6, 3.4, -.35)), h, 55, 3.4), (nf, h + V((-.5, 2.4, -.3)), h, 60, 2.4)], 1, nf, shake=.008, rshake=.3, seed=18)
    kick(c, [6, 8], 2.0); c.data.dof.aperture_fstop = 2.0; return 1, nf

def cut19():  # reverse: headlights close, the engine revs (body shudder)
    nf = 24; rng, car, parts, br = brute_set(nf)
    bd = suspension(car, 1, nf, amp=.003)
    for f in range(7, nf + 1):           # engine torque rocks the body on its springs, wheels stay planted
        k = math.exp(-(f - 7) / 9.)
        bd.location.z = .6 + .012 * k * math.sin((f - 7) * 1.9); bd.rotation_euler.y = math.radians(-1.4 * k * (1 - math.exp(-(f - 6) / 1.5)))
        bd.rotation_euler.x = math.radians(-.5 * k)
        bd.keyframe_insert('location', frame=f); bd.keyframe_insert('rotation_euler', frame=f)
    c = camera(45)
    shot_cam(c, [(1, (-.9, -8.4, .7), (.3, -5.4, .85), 45, 3.1), (nf, (-.7, -7.6, .72), (.35, -5.4, .88), 50, 2.5)], 1, nf, shake=.01, rshake=.3, seed=19)
    kick(c, [7], 1.4); c.data.dof.aperture_fstop = 2.0; return 1, nf

def overpass_set(nf, hits=(40, 46)):
    rng = K.street(col, length=160, seed=17, dead_lamps=(0, 1, 3, 4, 6)); K.sky(sc, fog=.016)
    conc = K.concrete('Overpass', '#4a4846')
    K.box('deck', col, (0, -30, 8.6), (40, 7, 1.2), conc)
    for sx in (-1, 1): K.box('pier', col, (sx * 5.2, -30, 4), (1.2, 2.2, 8), conc)
    for sy in (-1, 1): K.box('rail', col, (0, -30 + sy * 3.35, 9.65), (40, .25, .9), conc)
    import bmesh as _bm
    mm = bpy.data.meshes.new('mdisc'); bm = _bm.new(); _bm.ops.create_circle(bm, cap_ends=True, radius=7, segments=48); bm.to_mesh(mm)
    mo = bpy.data.objects.new('moondisc', mm); col.objects.link(mo); mo.location = (-5, -120, 34); mo.rotation_euler = (math.radians(90), 0, 0)
    L.setmat(mo, K.emit('MoonDisc', '#dfe6ff', 40))
    dress(rng, 0, -60)
    st = K.char('stalker', V(.8, -30, 10.1), math.radians(172))
    nz = A.Noise(5)
    for f in range(1, nf + 1):            # predator stillness with small sharp head-twitches of the whole body
        tw = 1.0 * (abs(nz(f / 9)) > .6) * nz(f / 2.)
        st.rotation_euler = (math.radians(.8 * math.sin(f / 24 * 2 * math.pi / 2.6)), math.radians(tw * .3), math.radians(172 + tw)); st.keyframe_insert('rotation_euler', frame=f)
    lightning(moon_obj(), list(hits), peak=6.0)
    area((0, -40, 16), (.8, -30, 11.5), 3000, 4, '#9ab0ff')
    red = bpy.data.lights.new('ember', 'POINT'); red.energy = 40; red.color = K.C('#ff3010'); red.shadow_soft_size = .1
    eo = bpy.data.objects.new('ember', red); col.objects.link(eo); eo.location = (.8, -29.2, 12.6)
    rain_here((0, -14, 0), (16, 30, 14), 3500, 1, nf)
    sc.view_settings.exposure = .85
    return st


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
    def pivot(name, loc, parent):
        e = bpy.data.objects.new(name, None); col.objects.link(e); e.parent = st; e.location = loc
        bpy.context.view_layer.update()
        if parent is not st:
            mw = e.matrix_world.copy(); e.parent = parent; e.matrix_world = mw
        bpy.context.view_layer.update(); return e
    neck = pivot('neckpv', mathutils.Vector((sc_.x, sc_.y - front * (smx.y - smn.y) * .35, smn.z + .03)), st)
    hinge_y = jmx.y if front < 0 else jmn.y
    jaw = pivot('jawpv', mathutils.Vector(((jmn.x + jmx.x) / 2, hinge_y, jmx.z - .02)), neck)
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
        K_ = [(1, 6, 8, 4), (5, 0, 10, 0), (21, 0, 11, -3), (24, 2, -14, 0), (30, 0, -42, 2), (nf, 0, -46, 0)]
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

def cut20():  # overpass: tilt up from the wet street to the Stalker against the moon
    nf = 72; st = overpass_set(nf); stalker_alive(st, nf, 'wide')
    c = camera(24)
    shot_cam(c, [(1, (1.6, 4.0, 1.1), (.3, -30, 2.0), 24, 30), (nf, (1.2, 1.5, 1.3), (.6, -30, 11.0), 60, 31)], 1, nf, shake=.02, rshake=.3, seed=20)
    c.data.dof.aperture_fstop = 4; return 1, nf

def cut21():  # CU skull + ember eyes, lightning
    nf = 36; st = overpass_set(nf, hits=(12, 18)); stalker_alive(st, nf, 'close')
    c = camera(85)
    shot_cam(c, [(1, (2.4, -25.0, 11.9), (.8, -30, 12.4), 85, 5.4), (nf, (2.2, -25.8, 12.0), (.8, -30, 12.4), 95, 4.6)], 1, nf, shake=.006, rshake=.15, seed=21)
    c.data.dof.aperture_fstop = 2.0; return 1, nf


def cut22():  # v5 close-up: it stares straight at us, mouth hanging open -> head snaps up to the sky -> the scream
    nf = 54; st = overpass_set(nf, hits=(30, 34)); stalker_alive(st, nf, 'scream')
    c = camera(88)
    shot_cam(c, [(1, (2.2, -25.0, 11.5), (.8, -30, 12.3), 88, 5.3), (22, (2.1, -25.3, 11.5), (.8, -30, 12.35), 96, 5.0),
                 (30, (2.1, -25.3, 11.4), (.8, -30, 12.8), 80, 5.0), (nf, (2.0, -25.4, 11.3), (.8, -30, 13.0), 76, 5.0)], 1, nf, shake=.006, rshake=.15, seed=22)
    kick(c, [30, 31, 33], 1.4)
    c.data.dof.aperture_fstop = 2.2; return 1, nf

# ------------------------------------------------------------------ v3: freeze-time ("bullet time") shots
def freeze_world(ff, keep=()):
    """hold every animated datablock (objects, armatures, lights, materials, shape keys, world) at frame ff:
    rain hangs in the air, the creature is caught mid-scream. Only the camera (and `keep`) still move."""
    def hold(idb):
        ad = getattr(idb, 'animation_data', None)
        if not ad or not ad.action or idb in keep: return
        for fc in _fcurves(ad.action):
            v = fc.evaluate(ff)
            for k in list(fc.keyframe_points)[::-1]: fc.keyframe_points.remove(k)
            fc.keyframe_points.insert(1, v)
    for coll in (bpy.data.objects, bpy.data.lights, bpy.data.materials, bpy.data.cameras, bpy.data.worlds, bpy.data.shape_keys, bpy.data.node_groups):
        for idb in coll:
            if idb in keep: continue
            hold(idb)

def orbit_cam(c, center, r0, r1, a0, a1, z0, z1, nf, lens0, lens1, tgt_off=(0, 0, 0), ease_in=.25):
    """camera glides on an arc around `center` while time is stopped (eased start/stop, slight push-in)"""
    c.animation_data_clear(); c.data.animation_data_clear()
    c.data.dof.use_dof = True
    for f in range(1, nf + 1):
        u = (f - 1) / max(1, nf - 1); u = u * u * (3 - 2 * u)
        a = math.radians(a0 + (a1 - a0) * u); r = r0 + (r1 - r0) * u
        c.location = V(center) + V((r * math.cos(a), r * math.sin(a), z0 + (z1 - z0) * u))
        aim(c, V(center) + V(tgt_off)); c.data.lens = lens0 + (lens1 - lens0) * u
        c.data.dof.focus_distance = (V(center) - c.location).length
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
        c.data.keyframe_insert('lens', frame=f); c.data.dof.keyframe_insert('focus_distance', frame=f)
    sc.render.motion_blur_shutter = .35

def cut61():  # bullet time: the scream frozen at its peak, rain hanging, camera arcs around her face
    cut6(); sc.frame_set(13); bpy.context.view_layer.update()
    s_ = [o for o in bpy.data.objects if o.name.endswith(' root') and 'screamer' in o.name.lower()] or [None]
    h = bone_w(s_[0], 'head', 13) if s_[0] else V((0, 0, 1.7))
    c = sc.camera; freeze_world(13, keep=(c, c.data))
    nf = 51; orbit_cam(c, h, 1.35, 1.15, 195, 95, .35, .15, nf, 40, 48, tgt_off=(0, 0, .0))
    c.data.dof.aperture_fstop = 2.0; return 1, nf

def cut151():  # bullet time: the Night Terror frozen as it blasts out of the fog, spray hanging, camera sweeps the nose
    cut15(); ff = 26; sc.frame_set(ff); bpy.context.view_layer.update()
    car = bpy.data.objects.get('NT root'); ctr = car.matrix_world @ V((.0, -2.4, .7))
    c = sc.camera; freeze_world(ff, keep=(c, c.data))
    nf = 35; orbit_cam(c, ctr, 3.8, 3.3, -55, -125, -.4, -.1, nf, 28, 32)
    c.data.dof.aperture_fstop = 4.0; return 1, nf

def cut161():  # bullet time mid-skid: car sideways, water sheet frozen, camera arcs low across the front
    cut16(); ff = 18; sc.frame_set(ff); bpy.context.view_layer.update()
    car = bpy.data.objects.get('NT root'); ctr = car.matrix_world @ V((0, -1.2, .6))
    c = sc.camera; freeze_world(ff, keep=(c, c.data))
    nf = 31; orbit_cam(c, ctr, 7.0, 6.2, -25, -95, .1, .45, nf, 26, 30)
    c.data.dof.aperture_fstop = 2.8; return 1, nf


def cut900():  # POSTER: worm's-eye view, the Night Terror's headlights in our face, the Brute roaring over it, the Stalker on the overpass under the moon
    st = overpass_set(1, hits=(90,)); stalker_alive(st, 1, 'close')
    car, parts, glowm, spots = nt_car((-1.5, -3.6, 0), math.radians(180 - 28))
    for sp in spots: sp.energy = 9000
    if os.environ.get('POSTER_MONSTER', 'stalker') == 'stalker':
        sg = K.char('stalker', V(1.2, -10.0, 0), math.radians(176)); sg.scale = (4.3, 4.3, 4.3)
        stalker_alive(sg, 36, 'close')
    else:
        br = K.char('brute', V(1.3, -10.2, 0), math.radians(192)); br.scale = (5.3, 5.3, 5.3); A.scream(K.char_rig(br), 1, 2, f_scream=1, amp=.5)
    hd = K.char('husk', V(-2.6, -12.5, 0), math.radians(160)); A.idle(K.char_rig(hd), 1, 2, amp=1.2)
    hd2 = K.char('runner', V(-1.0, -16.0, 0), math.radians(185)); A.idle(K.char_rig(hd2), 1, 2, amp=1.2)
    area((-5, -20, 12), (2.2, -12.5, 7), 9000, 2, '#ff3a18')          # red rim on the Brute from behind-left
    area((7, -19, 11), (2.2, -12.5, 7), 6000, 2, '#4a7cff')
    area((-.5, -2.5, 1.0), (1.6, -10.5, 7.5), 2500, 3, '#a8c0ff')      # cold up-light on the face from the car
    rain_here((0, -12, 0), (14, 14, 14), 2500, 1, 2)
    c = camera(18)
    c.location = V((1.0, 2.4, .25)); aim(c, V((.4, -10, 6.6)))
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 6.0; c.data.dof.aperture_fstop = 8
    for nd in sc.world.node_tree.nodes:
        if nd.bl_idname == 'ShaderNodeVolumeScatter': nd.inputs['Density'].default_value = .0008
    for sp in spots: sp.energy = 4000
    sc.view_settings.exposure = .9
    return (31, 31) if os.environ.get('POSTER_MONSTER', 'stalker') == 'stalker' else (1, 1)


# ------------------------------------------------------------------ v5: ONE-SHOT speed-ramp freeze (no cut, no new camera take)
def warp_shot(base, w0, w1, n_freeze, n_resume, pivot_local, sweep_deg, rad_scale=.85, drift=.03, lift=0., follow=.25, root='NT root', key_hold=0.):
    """Build `base` (a cut function), then retime the WORLD while the camera keeps one unbroken path:
    live (1x) from world frame w0 to w1 -> BOOM: time ramps to `drift` speed in 3 frames (tyres/rain still creep)
    while the camera glides from its live pose around the subject (to its right for +sweep) -> time ramps back to 1x
    and the action continues as seen from wherever the camera ended up. Every output frame is a real render."""
    import mathutils
    base(); c = sc.camera
    L = w1 - w0 + 1
    tmap = [w0 + i for i in range(L)]; t = float(w1); sp = 1.
    for i in range(n_freeze):
        k = min(1., (i + 1) / 3.); sp = 1 + (drift - 1) * (k * k * (3 - 2 * k)); t += sp; tmap.append(t)
    for i in range(n_resume):
        k = min(1., (i + 1) / 5.); sp = drift + (1 - drift) * (k * k * (3 - 2 * k)); t += sp; tmap.append(t)
    N = len(tmap)
    # sample the original camera (live part + pose A) before anything is retimed
    def cam_at(tt):
        sc.frame_set(int(tt), subframe=tt - int(tt)); bpy.context.view_layer.update(); return c.matrix_world.copy(), c.data.lens, c.data.dof.focus_distance
    live = [cam_at(tt) for tt in tmap[:L]]
    MA, lensA, focA = live[-1]
    car = bpy.data.objects.get(root); sc.frame_set(w1); bpy.context.view_layer.update()
    P = car.matrix_world @ V(pivot_local)
    CA = MA.translation.copy(); fwdA = -(MA.to_3x3() @ V((0, 0, 1))); tgtA = CA + fwdA * (P - CA).length
    d0 = CA - P
    def orbit(u):
        e = u * u * (3 - 2 * u); a = math.radians(sweep_deg) * e; r = 1 + (rad_scale - 1) * e
        dd = mathutils.Matrix.Rotation(a, 3, 'Z') @ V((d0.x * r, d0.y * r, d0.z)); dd.z += lift * e
        return P + dd
    poses = []
    for i in range(N):
        if i < L: poses.append(live[i]); continue
        j = i - L
        if j < n_freeze:
            u = (j + 1) / n_freeze; loc = orbit(u); ka = min(1., u / .35); ka = ka * ka * (3 - 2 * ka)
            tgt = tgtA.lerp(P, ka)
        else:
            loc = orbit(1.); sc.frame_set(int(tmap[i]), subframe=tmap[i] - int(tmap[i])); bpy.context.view_layer.update()
            Pn = car.matrix_world @ V(pivot_local); tgt = P.lerp(Pn, follow)
        q = (tgt - loc).to_track_quat('-Z', 'Y'); M = mathutils.Matrix.Translation(loc) @ q.to_matrix().to_4x4()
        poses.append((M, lensA, (tgt - loc).length))
    # keep the glide path clear: hide any creature whose body comes within 1.6 m of the moving camera
    path = [pp[0].translation for pp in poses[L:]]
    for r in [o for o in bpy.data.objects if o.name.endswith(' root') and o.name != root]:
        hit = False
        for tt in tmap[L::3]:
            sc.frame_set(int(tt)); bpy.context.view_layer.update()
            rl = r.matrix_world.translation
            if min(((rl + V((0, 0, 1.0))) - q).length for q in path) < 1.6: hit = True; break
        if hit:
            for o in r.children_recursive: o.hide_render = True
    # static props (parked cars, poles, bins) the glide passes through: hide them
    sc.frame_set(w1); bpy.context.view_layer.update()
    mine = set(car.children_recursive) if car else set()
    for o in bpy.data.objects:
        if o.type not in ('MESH', 'CURVE') or o.hide_render or o in mine or o.name.startswith(('rain', 'road')): continue
        bb = [o.matrix_world @ V(b) for b in o.bound_box]
        mn = V((min(p.x for p in bb), min(p.y for p in bb), min(p.z for p in bb))); mx = V((max(p.x for p in bb), max(p.y for p in bb), max(p.z for p in bb)))
        if (mx - mn).length > 14: continue
        for q in path:
            d = V((max(mn.x - q.x, 0, q.x - mx.x), max(mn.y - q.y, 0, q.y - mx.y), max(mn.z - q.z, 0, q.z - mx.z))).length
            if d < .45: o.hide_render = True; print('HIDE prop', o.name); break
    # retime every animated datablock except the camera
    keep = {c, c.data}
    def warp(idb):
        ad = getattr(idb, 'animation_data', None)
        if not ad or not ad.action or idb in keep: return
        is_rain = getattr(idb, 'name', '').startswith('rain')
        for fc in _fcurves(ad.action):
            if is_rain and fc.data_path == 'location':
                vals = [fc.evaluate(math.floor(tt)) - (.375 * (tt - math.floor(tt)) if fc.array_index == 2 else 0) for tt in tmap]
            else:
                vals = [fc.evaluate(tt) for tt in tmap]
            for k in list(fc.keyframe_points)[::-1]: fc.keyframe_points.remove(k)
            fc.keyframe_points.add(N)
            for i, v in enumerate(vals):
                kp = fc.keyframe_points[i]; kp.co = (i + 1, v); kp.interpolation = 'LINEAR'
            fc.update()
    for coll in (bpy.data.objects, bpy.data.lights, bpy.data.materials, bpy.data.worlds, bpy.data.shape_keys, bpy.data.node_groups):
        for idb in coll: warp(idb)
    c.animation_data_clear(); c.data.animation_data_clear(); c.parent = None
    for i, (M, ln, fd) in enumerate(poses):
        f = i + 1; c.matrix_world = M; c.data.lens = ln; c.data.dof.focus_distance = fd
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
        c.data.keyframe_insert('lens', frame=f); c.data.dof.keyframe_insert('focus_distance', frame=f)
    kl = bpy.data.lights.new('camkey', 'AREA'); kl.size = 1.5; kl.energy = 0; kl.color = K.C('#c8d6ff')
    ko = bpy.data.objects.new('camkey', kl); col.objects.link(ko); ko.parent = c; ko.location = (.8, .5, 0)
    for i in range(N):              # soft camera-side key fades up only while time is frozen, to reveal the car body
        j = i - L; e = 0. if j < 0 else (min(1., j / 6) if j < n_freeze else max(key_hold, 1 - (j - n_freeze) / 6))
        kl.energy = 350 * e; kl.keyframe_insert('energy', frame=i + 1)
    sc.render.motion_blur_shutter = .4
    return 1, N

def cut152():   # car blasts out of the fog -> BOOM freeze on the hit -> camera glides to the right -> it blasts past
    return warp_shot(cut15, 3, 24, 24, 11, (0, -1.6, .75), 62, rad_scale=.36, lift=.35, follow=.6)

def cut162():   # skid: sliding at us -> freeze mid-slide, spray hanging -> camera glides right -> slams to a stop
    return warp_shot(cut16, 1, 17, 26, 18, (0, -1.0, .6), 55, rad_scale=.6, lift=.3, follow=.5, key_hold=.7)

# ------------------------------------------------------------------ v6 found-footage POV cuts (Sam is filming on his phone)
def pov_cam(c, pts, f0, f1, eye=1.62, bob=.035, step_hz=2.6, look=None, seed=7, jolt=None):
    """running POV: piecewise path through pts [(frame, (x,y,floor_z), look_target)], head bob + operator shake every frame"""
    nz = [A.Noise(seed * 10 + i) for i in range(6)]
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = 2.0
    fr = [p[0] for p in pts]
    for f in range(f0, f1 + 1):
        i = max(0, min(len(pts) - 2, sum(1 for x in fr if x <= f) - 1)); a, b = pts[i], pts[i + 1]
        t = max(0., min(1., (f - a[0]) / max(1, b[0] - a[0])))
        loc = V(a[1]).lerp(V(b[1]), t) + V((0, 0, eye))
        tgt = V(a[2]).lerp(V(b[2]), t * t * (3 - 2 * t))
        ph = f / FPS * step_hz * 2 * math.pi
        loc += V((.012 * math.sin(ph / 2), 0, bob * abs(math.sin(ph / 2)) - bob * .5))
        loc += V((nz[0](f * .21) * .02, nz[1](f * .19) * .02, nz[2](f * .23) * .012))
        c.location = loc; aim(c, tgt)
        c.rotation_euler.x += math.radians(nz[3](f * .3) * 2.2 + 1.2 * math.sin(ph))
        c.rotation_euler.y += math.radians(nz[4](f * .25) * 3.5 + 1.6 * math.sin(ph / 2))
        c.rotation_euler.z += math.radians(nz[5](f * .27) * 2.5)
        c.data.dof.focus_distance = max(.6, (tgt - loc).length * .8)
        for pth in ('location', 'rotation_euler'): c.keyframe_insert(pth, frame=f)
        c.data.dof.keyframe_insert('focus_distance', frame=f)
    if jolt: kick(c, jolt, 2.4)
    sc.render.motion_blur_shutter = .6

def phone_light(c, energy=60):
    """the phone's flashlight: a hard narrow cone from just under the lens"""
    pl = bpy.data.lights.new('torch', 'SPOT'); pl.energy = energy; pl.spot_size = math.radians(70); pl.spot_blend = .35
    pl.color = K.C('#f4f0ff'); pl.shadow_soft_size = .01
    po = bpy.data.objects.new('torch', pl); col.objects.link(po); po.parent = c; po.location = (.03, -.04, 0)
    return pl

def stairwell(floors=3, H=3.2):
    """concrete switchback stairwell: flight A (x=+.6) runs down toward -y, mid landing, flight B (x=-.6) back to +y"""
    conc = K.concrete('StairConc', '#55524c'); wallm = K.concrete('StairWall', '#6a665e')
    paint = K.concrete('SafetyYellow', '#8a7020'); steel = K.metal('Rail', '#2a2a2a', .5)
    run, n = .28, 9; rise = H / 2 / n; Lf = run * n
    for k in range(floors):
        z = -k * H
        K.box('landing', col, (0, .65, z - .1), (2.5, 1.3, .2), conc)
        K.box('midlanding', col, (0, -Lf - .65, z - H / 2 - .1), (2.5, 1.3, .2), conc)
        for i in range(n):
            K.box('stepA', col, (.62, -run * (i + .5), z - rise * (i + 1) + rise / 2 - .1), (1.16, run, rise + .2), conc)
            K.box('noseA', col, (.62, -run * i - .02, z - rise * i + .002), (1.1, .04, .01), paint)
            K.box('stepB', col, (-.62, -Lf + run * (i + .5), z - H / 2 - rise * (i + 1) + rise / 2 - .1), (1.16, run, rise + .2), conc)
        # rails: centre rail on both flights + wall handrails
        for x, z0, z1, y0, y1 in ((.04, z, z - H / 2, 0, -Lf), (-.04, z - H / 2, z - H, -Lf, 0)):
            L.setmat(L.tube('rail', [V((x, y0, z0 + .95)), V((x, y1, z1 + .95))], .022, col, sides=8), steel)
            for j in range(5):
                t = j / 4; L.setmat(L.tube('post', [V((x, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t)), V((x, y0 + (y1 - y0) * t, z0 + (z1 - z0) * t + .95))], .012, col, sides=6), steel)
        # emergency light + EXIT sign on each landing (some dead)
        el = K.box('emlight', col, (1.22, .7, z + 2.3), (.06, .3, .12), K.emit('EmLight', '#dfe8ff', 14 if k != 1 else 0))
        if k != 1:
            ll = bpy.data.lights.new('em', 'POINT'); ll.energy = 18; ll.color = K.C('#dfe8ff'); ll.shadow_soft_size = .05
            lo = bpy.data.objects.new('em', ll); col.objects.link(lo); lo.location = (1.1, .7, z + 2.25)
            flicker(ll, 1, 120, 18, seed=k + 3, p_off=.2)
        K.box('exit', col, (-1.22, .7, z + 2.15), (.04, .34, .14), K.emit('Exit', '#ff2a1a', 6))
        xl = bpy.data.lights.new('exit', 'POINT'); xl.energy = 3; xl.color = K.C('#ff2a1a')
        xo = bpy.data.objects.new('exit', xl); col.objects.link(xo); xo.location = (-1.1, .7, z + 2.1)
        K.box('band', col, (1.249, -1.5, z + .9), (.01, 6, .1), paint); K.box('band', col, (-1.249, -1.5, z + .9), (.01, 6, .1), paint)
    zt, zb = 3.2, -floors * H
    K.box('wallE', col, (1.3, -1.25, (zt + zb) / 2), (.1, 5.2, zt - zb), wallm); K.box('wallW', col, (-1.3, -1.25, (zt + zb) / 2), (.1, 5.2, zt - zb), wallm)
    K.box('wallN', col, (0, 1.35, (zt + zb) / 2), (2.7, .1, zt - zb), wallm); K.box('wallS', col, (0, -Lf - 1.35, (zt + zb) / 2), (2.7, .1, zt - zb), wallm)
    K.box('divider', col, (0, -Lf / 2, (zt + zb) / 2), (.06, Lf - .2, .001), wallm).hide_render = True
    return Lf, H

def cut30():   # POV run down the stairwell with the phone torch; at the third turn the Crawler is coming up at us
    nf = 84; K.sky(sc, moon=False, fog=.006)
    Lf, H = stairwell(3)
    c = camera(18); phone_light(c, 90)
    cr = K.char('crawler', V(.55, -Lf - 1.15, -H - H / 2 + .45), math.radians(180))
    A.crawl(K.char_rig(cr), cr, 1, nf, speed=.12)
    m = -Lf - .65
    pts = [(1, (.6, .6, 0), (.6, -3, -1.4)),
           (20, (.6, -Lf + .1, -H / 2 + .05), (.6, m - 1, -H / 2 + 1.2)),
           (26, (0, m, -H / 2), (-1.2, -Lf / 2, -H / 2 + .4)),
           (46, (-.6, -.1, -H + .05), (0, 1.2, -H + 1.2)),
           (53, (0, .65, -H), (.6, -3, -H - 1.4)),
           (62, (.6, -.6, -H - .35), (.6, -Lf - .3, -H - H / 2 + .3)),
           (84, (.6, -.2, -H - .2), (.6, -Lf - .3, -H - H / 2 + .35))]
    pov_cam(c, pts, 1, nf, jolt=[63])
    sc.frame_set(70); bpy.context.view_layer.update()
    for o_ in bpy.data.objects:
        if o_.type == 'MESH' and 'crawl' in o_.name.lower():
            bb = [o_.matrix_world @ V(v) for v in o_.bound_box]; print('CRBB', o_.name, min(b.z for b in bb), max(b.z for b in bb), min(b.y for b in bb), max(b.y for b in bb))
    print('CAM70', c.location)
    sc.view_settings.exposure = 1.3
    return 1, nf

def cut31():   # POV: shove the garage door, run at the Night Terror, the tubes flicker on, the headlights ignite
    nf = 72; garage_set(nf, ign=58)
    c = camera(18); phone_light(c, 40)
    pts = [(1, (4.2, -11.0, 0), (.4, -2, .9)), (40, (2.6, -6.2, 0), (1.3, -2.6, 1.0)), (72, (2.7, -3.6, 0), (1.1, -1.6, 1.0))]
    pov_cam(c, pts, 1, nf, step_hz=2.8, jolt=[58])
    return 1, nf

exec(open(os.path.join(HERE,'v7sets.py')).read())
f0, f1 = globals()[f'cut{SHOT}']()
bpy.context.view_layer.update()
render(f0, f1)
print('CUT DONE', SHOT)
