"""Night Terror: Dead Roads - Episode 1 shots. SHOT=1..8 builds one shot and renders its frames.
env: RES (1.0 = 1080x1920), SAMP, FR="a,b" (frame range override), STEP (render every Nth frame), BLEND=1 save .blend"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Euler
import city as K
import castlib as L
V = K.V
HERE = os.path.dirname(os.path.abspath(__file__))
SHOT = int(os.environ.get('SHOT', '2'))
OUT = os.path.join(HERE, 'out', 'shots', f's{SHOT}'); os.makedirs(OUT, exist_ok=True)
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
    """add a pivot per wheel assembly at its mesh centre and spin rim+tire by distance/radius"""
    bpy.context.view_layer.update()
    for asm in [o for o in parts if o.name.endswith('wheel assembly')]:
        subs = [c for c in asm.children if not c.name.startswith('Brake')]
        meshes = [m for s in subs for m in [s] + list(s.children_recursive) if m.type == 'MESH']
        if not meshes: continue
        pts = [m.matrix_world @ V(c) for m in meshes for c in m.bound_box]
        mn = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        ctr = (mn + mx) / 2; rad = (mx.z - mn.z) / 2
        pv = bpy.data.objects.new('pivot', None); col.objects.link(pv)
        pv.parent = asm; pv.matrix_world = __import__('mathutils').Matrix.Translation(ctr)
        bpy.context.view_layer.update()
        for s in subs:
            mw = s.matrix_world.copy(); s.parent = pv; s.matrix_world = mw
        pv.rotation_mode = 'XYZ'
        r0 = pv.rotation_euler.copy()
        pv.keyframe_insert('rotation_euler', frame=f0)
        pv.rotation_euler = (r0.x - dist / max(rad, .2), r0.y, r0.z); pv.keyframe_insert('rotation_euler', frame=f1)
        linear(pv)


def render(f0, f1, res=None, samp=None):
    fr = os.environ.get('FR')
    if fr: f0, f1 = map(int, fr.split(','))
    sc.frame_start, sc.frame_end = f0, f1; sc.frame_step = int(os.environ.get('STEP', '1'))
    r = float(os.environ.get('RES', res or '.5'))
    K.setup_render(sc, int(1080 * r) // 2 * 2, int(1920 * r) // 2 * 2, int(os.environ.get('SAMP', samp or '16')))
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = .5
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = os.path.join(OUT, 'f')
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = .03
    sc.render.use_persistent_data = True
    sc.render.use_overwrite = False
    if os.environ.get('THREADS'): sc.render.threads_mode = 'FIXED'; sc.render.threads = int(os.environ['THREADS'])
    if os.environ.get('BLEND'): bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f's{SHOT}.blend'))
    bpy.ops.render.render(animation=True)


# ------------------------------------------------------------------ shots
def shot1():
    """3:12 AM. Aerial descent down the dead avenue in the rain."""
    rng = K.street(col, length=220, seed=11, dead_lamps=(1, 4, 5))
    K.sky(sc, fog=.011)
    paints = ['#4a1a16', '#1e2a3a', '#5a5248', '#22301e', '#6a6a66']
    for i in range(9):
        K.sedan(col, V(rng.uniform(-4, 4), -10 - i * 17 + rng.uniform(-4, 4), 0), rng.uniform(-1.4, 1.4), K.carpaint(f'P{i}', paints[i % 5]), rng)
    roots = [K.char(n, V(0, -400, 0), 0) for n in ('husk', 'runner', 'walker2')]
    for i in range(16):
        dup(roots[i % 3], V(rng.uniform(-5, 5), -30 - rng.uniform(0, 80), 0), rng.uniform(-3, 3))
    r = K.rain(col, w=.007, center= (0, 0, 0), size=(30, 50, 45), count=4000, streak=.6)
    c = camera(24)
    cam_path(c, [1, 96], [(6, 30, 40), (2.5, 14, 13)], [(0, -110, 6), (0, -70, 3)], focus=[70, 50])
    c.data.dof.aperture_fstop = 8
    rain_anim(r, 1, 96)
    sc.view_settings.exposure = 1.9
    return 1, 96

def shot2():
    """The Crawler drags itself out from under a wreck toward the lens."""
    rng = K.street(col, length=140, seed=5)
    K.sky(sc, fog=.018)
    paints = ['#4a1a16', '#1e2a3a', '#5a5248', '#22301e', '#6a6a66']
    for i, (p, rr) in enumerate([((-2.9, -5.2, 0), .3), ((3.6, -20, 0), -.4), ((-1.8, -31, 0), 1.2), ((4.0, -44, 0), .1), ((-3.8, -58, 0), -.2)]):
        K.sedan(col, V(p), rr, K.carpaint(f'Paint{i}', paints[i % 5]), rng)
    K.trash(col, (5.4, -12, .16), rng, 7); K.trash(col, (-5.6, -26, .16), rng, 5)
    hl = bpy.data.lights.new('pool', 'SPOT'); hl.energy = 2600; hl.color = K.C('#ffb060'); hl.spot_size = math.radians(70); hl.spot_blend = .8
    ho = bpy.data.objects.new('pool', hl); col.objects.link(ho); ho.location = (1.2, -24, 7.5)
    flicker(hl, 1, 96, 2600, seed=4, p_off=.08)
    cr = K.char('crawler', V(-.4, -3.2, 0), math.radians(-170))
    key(cr, 1, loc=V(-.6, -3.4, 0)); key(cr, 96, loc=V(-.5, -2.5, 0))
    K.char('husk', V(1.0, -24, 0), math.radians(-10))
    bl = bpy.data.lights.new('far', 'AREA'); bl.energy = 4000; bl.size = 3; bl.color = K.C('#cfe0ff')
    bo = bpy.data.objects.new('far', bl); col.objects.link(bo); bo.location = (0, -70, 1.2); bo.rotation_euler = (math.radians(90), 0, 0)
    fl = bpy.data.lights.new('near', 'SPOT'); fl.energy = 1800; fl.color = K.C('#ffae5a'); fl.spot_size = math.radians(80); fl.spot_blend = .7
    fo = bpy.data.objects.new('near', fl); col.objects.link(fo); fo.location = (2.5, -3, 6.8)
    r = K.rain(col, w=.007, center= (0, -16, 0), size=(16, 34, 12), count=3500)
    c = camera(22)
    cam_path(c, [1, 96], [(.6, 1.9, .62), (.4, .9, .7)], [(-.8, -22, .7), (-.8, -22, .9)], focus=[4.9, 2.9])
    c.data.dof.aperture_fstop = 2.2
    rain_anim(r, 1, 96)
    sc.view_settings.exposure = 1.3
    return 1, 96

def shot3():
    """The Screamer on a rooftop ledge, screaming over the city; lightning."""
    rng = K.street(col, length=160, seed=7)
    K.sky(sc, fog=.012)
    # hero building on +X side whose cornice the Screamer stands on
    mat = K.facade('HeroFacade', '#2e3236', lit=.25, seed=3.3, brick=True)
    K.building(col, 16, -20, 12, 12, 30, mat, rng, 1)
    roof = K.box('roof', col, (16, -20, 30.02), (11.8, 11.8, .04), K.concrete('Roof', '#2a2928'))
    K.box('tank', col, (19, -17, 32), (2.4, 2.4, 3), K.metal('Tank', '#3a2e26', .7))
    ant = L.tube('antenna', [V(18, -24, 30), V(18, -24, 38)], .04, col, sides=6); L.setmat(ant, K.metal('Ant', '#202020'))
    s = K.char('screamer', V(10.2, -20, 30.4), math.radians(-128))
    sun = moon_obj(); lightning(sun, [22, 30, 70], peak=7.0)
    rim = bpy.data.lights.new('rim', 'AREA'); rim.energy = 500; rim.size = 2; rim.color = K.C('#b8c8ff')
    ro = bpy.data.objects.new('rim', rim); col.objects.link(ro); ro.location = (13, -23, 33); aim(ro, (10.2, -20, 31.4))
    key_l = bpy.data.lights.new('key', 'AREA'); key_l.energy = 600; key_l.size = 2; key_l.color = K.C('#9ab0ff')
    ko = bpy.data.objects.new('key', key_l); col.objects.link(ko); ko.location = (7, -18, 33); aim(ko, (10.2, -20, 31.4))
    r = K.rain(col, w=.007, center= (8, -18, 26), size=(14, 14, 14), count=2500)
    c = camera(26)
    cam_path(c, [1, 96], [(6.0, -15.8, 29.4), (7.0, -17.0, 29.8)], [(10.3, -20.1, 32.4), (10.3, -20.1, 32.2)], lenses=[28, 36], focus=[6.0, 4.6])
    c.data.dof.aperture_fstop = 2.8
    rain_anim(r, 1, 96)
    sc.view_settings.exposure = 1.1
    return 1, 96

def shot4():
    """The horde, standing in the fog, listening. Crane up and back reveals how many."""
    rng = K.street(col, length=140, seed=21, dead_lamps=(0, 2, 3, 5))
    K.sky(sc, fog=.024)
    paints = ['#4a1a16', '#1e2a3a', '#5a5248']
    for i, (p, rr) in enumerate([((-4.4, -14, 0), .5), ((4.6, -30, 0), -.2), ((-1.5, -46, 0), 1.0)]):
        K.sedan(col, V(p), rr, K.carpaint(f'P{i}', paints[i]), rng)
    names = ['husk', 'runner', 'walker2', 'brute']
    roots = [K.char(n, V(0, -500 - i * 5, 0), 0) for i, n in enumerate(names)]
    pts = []
    for i in range(46):
        for _ in range(40):
            p = V(rng.uniform(-5.6, 5.6), -9 - rng.uniform(0, 42) ** 1.0, 0)
            if all((p - q).length > 1.0 for q in pts): break
        pts.append(p)
        w = [0, 0, 0, 1, 1, 2, 2, 2][rng.randrange(8)] if i else 0
        dup(roots[w], p, math.radians(180 + rng.uniform(-25, 25)), rng.uniform(.94, 1.06))
    big = dup(roots[3], V(.6, -26, 0), math.radians(178))
    hl = bpy.data.lights.new('pool', 'SPOT'); hl.energy = 3000; hl.color = K.C('#ffb060'); hl.spot_size = math.radians(80); hl.spot_blend = .8
    ho = bpy.data.objects.new('pool', hl); col.objects.link(ho); ho.location = (-1, -12, 8)
    flicker(hl, 1, 96, 3000, seed=9, p_off=.1)
    bl = bpy.data.lights.new('far', 'AREA'); bl.energy = 6000; bl.size = 5; bl.color = K.C('#cfe0ff')
    bo = bpy.data.objects.new('far', bl); col.objects.link(bo); bo.location = (0, -75, 3); bo.rotation_euler = (math.radians(90), 0, 0)
    r = K.rain(col, w=.007, center= (0, -16, 0), size=(18, 40, 16), count=4500)
    c = camera(30)
    cam_path(c, [1, 96], [(.4, -5.5, 1.5), (1.4, 1.5, 6.0)], [(0, -18, 1.6), (0, -24, .8)], focus=[8, 18])
    c.data.dof.aperture_fstop = 3.5
    rain_anim(r, 1, 96)
    sc.view_settings.exposure = 1.95
    return 1, 96

def shot5():
    """Garage. Dark. The Night Terror's headlights ignite."""
    K.sky(sc, moon=False, fog=.008)
    flo = K.box('floor', col, (0, -2, -.05), (14, 20, .1), K.asphalt())
    wall = K.concrete('GarageWall', '#3a3836')
    K.box('wallL', col, (6, -2, 3), (.2, 20, 6), wall); K.box('wallR', col, (-5.5, -2, 3), (.2, 20, 6), wall)
    K.box('back', col, (0, 6, 3), (14, .2, 6), wall); K.box('ceil', col, (0, -2, 6), (14, 20, .2), wall)
    # roll-up door (ribbed) in front of the car, half open
    door = K.metal('Door', '#2a2c2e', .55)
    for k in range(14):
        K.box('slat', col, (0, -12, 2.2 + k * .26), (9, .08, .22), door)
    tube = K.box('tube', col, (.4, -2, 5.85), (.12, 2.6, .06), K.emit('Fluo', '#cfe8ff', 25))
    ft = bpy.data.lights.new('fluo', 'AREA'); ft.shape = 'RECTANGLE'; ft.size = .2; ft.size_y = 2.6; ft.energy = 160; ft.color = K.C('#cfe8ff')
    fo = bpy.data.objects.new('fluo', ft); col.objects.link(fo); fo.location = (.4, -2, 5.75)
    flicker(ft, 1, 72, 160, seed=2, p_off=.35)
    car, parts, glowm, spots = nt_car((.4, -2, 0), 0, lights_on=True)
    em = glowm.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
    for f, v in ((1, 0), (26, 0), (27, 30), (28, 4), (30, 30), (72, 24)):
        em.default_value = v; em.keyframe_insert('default_value', frame=f)
        for s in spots: s.energy = v * 40; s.keyframe_insert('energy', frame=f)
    # tools / clutter
    K.box('bench', col, (-4.5, 2, .45), (1.2, 4, .9), K.metal('Bench', '#3a2a20', .7))
    c = camera(35)
    cam_path(c, [1, 72], [(2.3, -7.6, .55), (1.6, -6.6, .7)], [(.3, -5.3, .9), (.45, -5.3, .95)], focus=[2.3, 1.6])
    c.data.dof.aperture_fstop = 2.0
    sc.view_settings.exposure = 1.0
    return 1, 72

def shot6():
    """The Night Terror tears down the avenue through the infected. Tracking low ahead of the car."""
    rng = K.street(col, length=220, seed=13, dead_lamps=(1, 4))
    K.sky(sc, fog=.009)
    paints = ['#4a1a16', '#1e2a3a', '#5a5248', '#22301e']
    for i in range(7):
        K.sedan(col, V(rng.choice([-1, 1]) * rng.uniform(3.8, 5), -20 - i * 22, 0), rng.uniform(-.6, .6), K.carpaint(f'P{i}', paints[i % 4]), rng)
    roots = [K.char(n, V(0, -600 - i * 5, 0), 0) for i, n in enumerate(['runner', 'husk', 'walker2'])]
    for i in range(22):
        sx = rng.choice([-1, 1])
        dup(roots[i % 3], V(sx * rng.uniform(2.6, 5.2), -10 - i * 6 - rng.uniform(0, 4), 0), math.radians(90 * sx + rng.uniform(-30, 30)))
    car, parts, glowm, spots = nt_car((.4, 14, 0), 0)
    for sp in spots: sp.energy = 2500
    D = 120.
    key(car, 1, loc=V(.4, 14, 0)); key(car, 120, loc=V(.4, 14 - D, 0)); linear(car)
    spin_wheels(parts, 1, 120, D)
    r = K.rain(col, w=.007, center= (0, 0, 0), size=(18, 30, 12), count=4000)
    r.parent = car
    c = camera(24)
    # camera rig rides with the car: low front-left 3/4, slowly swinging round to the side
    for f, off, tgt in ((1, (4.4, -10.5, .55), (0.4, -3.8, .9)), (60, (4.2, -8.0, .7), (0.5, -3.0, .9)), (120, (4.0, -4.2, .8), (0.6, -2.2, 1.0))):
        cy = 14 - D * (f - 1) / 119.
        c.location = V((.4 + off[0], cy + off[1], off[2])); aim(c, V((tgt[0], cy + tgt[1], tgt[2])))
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    linear(c)
    c.data.dof.use_dof = True; c.data.dof.focus_object = car; c.data.dof.aperture_fstop = 4
    rain_anim(r, 1, 120)
    sc.view_settings.exposure = 1.1
    return 1, 120

def shot7():
    """The Night Terror skids to a stop. The Brute walks out of the fog into its headlights."""
    rng = K.street(col, length=140, seed=9, dead_lamps=(0, 1, 2, 3, 5, 6))
    K.sky(sc, fog=.016)
    paints = ['#4a1a16', '#1e2a3a', '#5a5248']
    for i, (p, rr) in enumerate([((4.2, -24, 0), -.5), ((-3.9, -33, 0), .3), ((3.0, -48, 0), 1.4)]):
        K.sedan(col, V(p), rr, K.carpaint(f'Paint{i}', paints[i]), rng)
    car, parts, glowm, spots = nt_car((.4, -2, 0), math.radians(4))
    # skid: arrive fast from behind camera, yaw, settle
    key(car, 1, loc=V(-.6, 22, 0), rot=(0, 0, math.radians(-4))); key(car, 22, loc=V(.4, -1.4, 0), rot=(0, 0, math.radians(7)))
    key(car, 34, loc=V(.4, -2, 0), rot=(0, 0, math.radians(4)))
    spin_wheels(parts, 1, 22, 23.5)
    br = K.char('brute', V(2.0, -12.5, 0), math.radians(188))
    key(br, 30, loc=V(2.1, -13.6, 0)); key(br, 120, loc=V(2.0, -12.2, 0))
    K.char('runner', V(-3.4, -26, 0), math.radians(160)); K.char('husk', V(3.4, -29, 0), math.radians(200))
    rl = bpy.data.lights.new('rim', 'AREA'); rl.energy = 2500; rl.size = 4; rl.color = K.C('#7a9aff')
    ro = bpy.data.objects.new('rim', rl); col.objects.link(ro); ro.location = (0, -30, 6); ro.rotation_euler = (math.radians(70), 0, 0)
    r = K.rain(col, w=.007, center= (0, -10, 0), size=(14, 26, 10), count=3500)
    c = camera(32)
    cam_path(c, [1, 34, 120], [(2.9, .6, .8), (2.9, .6, .8), (2.5, -1.2, .95)], [(1.3, -13, 1.6), (1.3, -13, 1.6), (1.6, -13, 1.9)],
             lenses=[32, 32, 40], focus=[13.8, 13.8, 11.4])
    c.data.dof.aperture_fstop = 2.8
    rain_anim(r, 1, 120)
    sc.view_settings.exposure = .75
    return 1, 120

def shot8():
    """Cliffhanger: the Stalker on the overpass against the moon. Tilt up from the street."""
    rng = K.street(col, length=160, seed=17, dead_lamps=(0, 1, 3, 4, 6))
    K.sky(sc, fog=.016)
    conc = K.concrete('Overpass', '#4a4846')
    K.box('deck', col, (0, -30, 8.6), (40, 7, 1.2), conc)
    for sx in (-1, 1):
        K.box('pier', col, (sx * 5.2, -30, 4), (1.2, 2.2, 8), conc)
    for sy in (-1, 1):
        K.box('rail', col, (0, -30 + sy * 3.35, 9.65), (40, .25, .9), conc)
    # moon disc far behind
    mn = K.box('moondisc', col, (-6, -260, 70), (40, .1, 40), None)
    bpy.ops.object.select_all(action='DESELECT')
    mm = bpy.data.meshes.new('mdisc'); import bmesh; bm = bmesh.new(); bmesh.ops.create_circle(bm, cap_ends=True, radius=7, segments=48); bm.to_mesh(mm)
    bpy.data.objects.remove(mn, do_unlink=True)
    mo = bpy.data.objects.new('moondisc', mm); col.objects.link(mo); mo.location = (-5, -120, 34); mo.rotation_euler = (math.radians(90), 0, 0)
    L.setmat(mo, K.emit('MoonDisc', '#dfe6ff', 40))
    st = K.char('stalker', V(.8, -30, 10.1), math.radians(172))
    sun = moon_obj(); lightning(sun, [64, 70], peak=6.0)
    rl = bpy.data.lights.new('rim', 'AREA'); rl.energy = 3000; rl.size = 4; rl.color = K.C('#9ab0ff')
    ro = bpy.data.objects.new('rim', rl); col.objects.link(ro); ro.location = (0, -40, 16); aim(ro, (.8, -30, 11.5))
    red = bpy.data.lights.new('ember', 'POINT'); red.energy = 40; red.color = K.C('#ff3010'); red.shadow_soft_size = .1
    eo = bpy.data.objects.new('ember', red); col.objects.link(eo); eo.location = (.8, -29.2, 12.6)
    r = K.rain(col, w=.007, center= (0, -14, 0), size=(16, 30, 14), count=3500)
    c = camera(26)
    cam_path(c, [1, 96], [(1.6, 4.0, 1.1), (1.2, 1.5, 1.3)], [(.3, -30, 2.0), (.6, -30, 11.0)], lenses=[24, 60], focus=[30, 31])
    c.data.dof.aperture_fstop = 4
    rain_anim(r, 1, 96)
    sc.view_settings.exposure = .85
    return 1, 96


f0, f1 = globals()[f'shot{SHOT}']()
bpy.context.view_layer.update()
render(f0, f1)
print('SHOT DONE', SHOT)
