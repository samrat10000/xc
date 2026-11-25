"""Night Terror teaser (Stalker poster finale). Reuses the Ep1 v5 kit (shots2.py helpers, city.py, cast, car).
Run from xc/ep1:  blender -b -P teaser.py   env CUT=901..912 (one shot each), OUTROOT=...\\teaser\\out, RES, SAMP, FR, DEVICE=GPU
Shots (24 fps):
 901 puddle macro (24f)  902 tyre cam drift (36)  903 windshield POV, lamps die (41)  904 bystander camcorder (34)
 905 monster POV (29)    906 glass rain side-follow (14)  907 lightning, Brute on a roof (10)
 908 facade chunk falls, swerve (19)  909 crash zoom to the skull (19)  910 ECU eye socket, car reflected (48)
 911 HERO: poster frame, drift in, scream, car passes lens (139)  912 stinger, skull at the lens (4)"""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ.setdefault('CUT', '911')
_src = open(os.path.join(HERE, 'shots2.py'), encoding='utf-8').read()
exec(compile(_src[:_src.index("f0, f1 = globals()[f'cut{SHOT}']()")], 'shots2.py', 'exec'))
import bpy
from mathutils import Vector, Matrix

R = random.Random(11)

# ------------------------------------------------------------------ helpers
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

def own_lens_mats():
    """every street-lamp lens gets its own emissive material, so lamps can die one by one"""
    out = []
    for o in bpy.data.objects:
        if o.name.startswith('lamp lens') and o.data.materials and o.data.materials[0]:
            m = o.data.materials[0].copy(); o.data.materials[0] = m; out.append((o, m))
    return out

def kill_lamps_wave(f_of_y):
    """lamps die as a wave travels along the street: f_of_y(y) -> frame the lamp at that y dies (None = never)"""
    lens = own_lens_mats()
    for o, m in lens:
        f = f_of_y(o.location.y)
        if f is None: continue
        b = m.node_tree.nodes.get('Emission') or next((n for n in m.node_tree.nodes if n.type == 'EMISSION'), None)
        if b is None: continue
        s0 = b.inputs['Strength'].default_value
        for ff, v in ((f - 1, s0), (f, s0 * 2.2), (f + 1, 0)):
            b.inputs['Strength'].default_value = v; b.inputs['Strength'].keyframe_insert('default_value', frame=ff)
    for lo in [o for o in bpy.data.objects if o.name.startswith('sodium')]:
        f = f_of_y(lo.location.y)
        if f is None: continue
        e = lo.data.energy
        for ff, v in ((f - 1, e), (f, e * 2.2), (f + 1, 0)):
            lo.data.energy = v; lo.data.keyframe_insert('energy', frame=ff)

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

def hero_set(nf):
    """the poster set (cut900, Stalker version), without the car (each shot adds its own)"""
    st = overpass_set(nf, hits=(int(os.environ.get('HIT', '9999')),))
    sg = giant((1.2, -10.0, 0), 176)
    hd = K.char('husk', V(-2.6, -12.5, 0), math.radians(160)); A.idle(K.char_rig(hd), 1, nf, amp=1.2)
    hd2 = K.char('runner', V(-1.0, -16.0, 0), math.radians(185)); A.idle(K.char_rig(hd2), 1, nf, amp=1.2)
    area((-5, -20, 12), (2.2, -12.5, 7), 9000, 2, '#ff3a18')
    area((7, -19, 11), (2.2, -12.5, 7), 6000, 2, '#4a7cff')
    area((-.5, -2.5, 1.0), (1.6, -10.5, 7.5), 2500, 3, '#a8c0ff')
    rain_here((0, -12, 0), (14, 14, 14), 2500, 1, nf)
    for nd in sc.world.node_tree.nodes:
        if nd.bl_idname == 'ShaderNodeVolumeScatter': nd.inputs['Density'].default_value = .0008
    sc.view_settings.exposure = .9
    return st, sg

POSTER_CAM = ((1.0, 2.4, .25), (.4, -10, 6.6))

# ------------------------------------------------------------------ shots
def cut901():   # puddle macro: rings in time with two giant steps, then a tyre smashes through
    nf = 24; base_street(seed=21, fog=.02); px, py = .9, -20.
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=220, y_subdivisions=220, size=2.6, location=(px, py, .012))
    pud = bpy.context.active_object; pud.name = 'puddle'
    for o_ in list(pud.users_collection): o_.objects.unlink(pud)
    col.objects.link(pud)
    for t0 in (1, 12):
        w = pud.modifiers.new('step', 'WAVE'); w.time_offset = t0; w.height = .0035; w.width = .07; w.narrowness = 1.6
        w.speed = .03; w.start_position_x = 0; w.start_position_y = .25; w.use_normal = False; w.damping_time = 16; w.falloff_radius = 1.25
    wm = bpy.data.materials.new('Puddle'); wm.use_nodes = True; b = wm.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (.004, .004, .006, 1); b.inputs['Roughness'].default_value = .015; b.inputs['IOR'].default_value = 1.33
    pud.data.materials.append(wm)
    bpy.ops.object.shade_smooth()
    giant((1.0, -52, 0), 176)                                   # far out of focus, a stilt leg in the fog
    car, parts, glowm, spots = nt_car((0, -60, 0), math.radians(180))
    sc.frame_set(1); fw = min(wheels(parts), key=lambda o: wpos(o).y); dx = px - wpos(fw).x + .05
    drift(car, [(1, dx, -62, 180), (24, dx, py + 2.6, 182)]); linear(car)
    spin_wheels(parts, 1, nf, 42); suspension(car, 1, nf, amp=.01)
    spray(fw, 19, 24, per=40, back=(0, 1, 0), speed=4, up=3.5, size=.01)
    c = camera(100)
    shot_cam(c, [(1, (px - .05, py + 1.25, .1), (px, py + .1, 0), 100, 1.15), (nf, (px - .05, py + 1.22, .11), (px, py + .05, .02), 100, 1.15)],
             1, nf, shake=.002, rshake=.08, seed=901)
    kick(c, [1, 12], .5); c.data.dof.aperture_fstop = 2.8
    return 1, nf

def cut902():   # tyre cam: 20 mm low on the car, the rear wheel sliding sideways at the lens, spray sheeting off
    nf = 36; D = 40.; rng, car = chase_set(nf, D, y0=14)
    parts = [o for o in car.children_recursive]
    car.animation_data_clear()
    drift(car, [(1, .4, 14, 22), (18, .2, -4, 30), (nf, -.4, -26, 26)])
    rw = max(wheels(parts), key=lambda o: (car.matrix_world.inverted() @ wpos(o)).y)
    c = camera(20); c.parent = car
    for f in range(1, nf + 1):
        tt = f / 24; c.location = V((2.2 + .03 * math.sin(tt * 9), 1.9 + .02 * math.sin(tt * 13), .22 + .012 * math.sin(tt * 17)))
        aim(c, V((1.0, .8, .45))); c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 1.4; c.data.dof.aperture_fstop = 2.8
    spray(rw, 1, nf, per=14, back=(.6, 1, 0), speed=7, up=2.0)
    return 1, nf

def cut903():   # windshield POV: the street lamps die block by block toward us; far down the street, a thin antlered shape in the fog
    nf = 41; D = 30.; rng, car = chase_set(nf, D, y0=10)
    giant((.5, -68, 0), 178)
    backlight((.5, -92, 14), (.5, -10, 6), 7000, 14, name='giantback')   # cold glow in the fog behind it
    car.animation_data_clear(); drift(car, [(1, .4, 10, 0), (20, .1, -4, 3), (nf, .5, -20, -2)])
    kill_lamps_wave(lambda y: (int(6 + (-y - 80) / -4.5)) if y < -10 else None)   # wave runs from y=-80 toward the car
    c = camera(24); c.parent = car
    for f in range(1, nf + 1):
        tt = f / 24; c.location = V((-.15 + .01 * math.sin(tt * 11), -.55 + .006 * math.sin(tt * 7), 1.42 + .012 * math.sin(tt * 23)))
        aim(c, V((-.1, -30, 1.1))); c.rotation_euler.y += math.radians(2.5 * math.sin(tt * 2.4))
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 25; c.data.dof.aperture_fstop = 4
    return 1, nf

def cut904():   # bystander camcorder on the kerb: the car drifts past almost on top of us, a flinch and a late pan
    nf = 34; base_street(seed=33, fog=.016)
    rain_here((4, -20, 0), (16, 30, 12), 3500, 1, nf)
    car, parts, glowm, spots = nt_car((1, -50, 0), math.radians(180))
    for sp in spots: sp.energy = 3000
    drift(car, [(1, 1.2, -52, 180), (14, 1.8, -30, 205), (24, 2.6, -16, 214), (nf, 2.2, -2, 200)])
    spin_wheels(parts, 1, nf, 52); suspension(car, 1, nf, amp=.01, pitch=[(1, 0), (14, 1.5), (nf, 1.0)])
    for w_ in wheels(parts)[:2]: spray(w_, 8, nf, per=6, back=(0, 1, 0), speed=5, up=1.6)
    c = camera(28); keys = []
    for f in (1, 10, 18, 24, 30, nf):
        sc.frame_set(max(1, f - 4)); tp = car.matrix_world.translation.copy() + V((0, 0, .9))     # operator lags ~4 frames
        keys.append((f, (7.2, -21.5, 1.55), tuple(tp), 28, max(2., (tp - V((7.2, -21.5, 1.55))).length)))
    shot_cam(c, keys, 1, nf, shake=.035, rshake=.9, seed=904)
    kick(c, [21], 4.0); c.data.dof.aperture_fstop = 2.8
    camlight(c, 0)
    return 1, nf

def cut905():   # its eyes: 15 m up between the towers, looking down at the tiny car, slow breathing sway
    nf = 29; rng, car = chase_set(nf, 30, y0=-6)
    car.animation_data_clear(); drift(car, [(1, .4, -8, 180), (nf, .8, -38, 186)])
    c = camera(35)
    for f in range(1, nf + 1):
        tt = f / 24; br = math.sin(tt * 2 * math.pi / 2.2)
        c.location = V((-2.2 + .25 * math.sin(tt * 1.1), -4.0 + .1 * br, 15.2 + .12 * br)); aim(c, V((.2, -22 - 6 * tt, 0)))
        c.rotation_euler.y += math.radians(3 * math.sin(tt * .9)); c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 22; c.data.dof.aperture_fstop = 5.6
    return 1, nf

def cut906():   # low side-follow: the car slides sideways while window glass rains down on it from the facade above
    nf = 14; D = 14.; rng, car = chase_set(nf, D, y0=-10)
    car.animation_data_clear(); drift(car, [(1, .4, -10, 20), (nf, -.2, -24, 26)])
    c = camera(24)
    for f in range(1, nf + 1):
        sc.frame_set(f); p = car.matrix_world.translation
        c.location = p + V((4.6, .8, .55)) + V((.03 * math.sin(f), 0, .02 * math.sin(f * 1.7))); aim(c, p + V((.2, 0, 1.4)))
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 4.5; c.data.dof.aperture_fstop = 4
    backlight((-1.5, -14, 16), (0, -18, 3), 1200, 3, (1, .82, .6), 'glasskey')
    backlight((-6, -26, 9), (0, -16, 6), 1000, 2, (.6, .75, 1), 'glassrim')
    glass_rain(260, -30, 10, (-3.5, 2.5), (-27, -10), (6, 13), vel=(1.2, 0, -2), size=.14)
    return 1, nf

def cut907():   # lightning: the Brute hunched on a roof edge, a silhouette for four frames
    nf = 10; base_street(seed=44, fog=.012)
    K.box('block', col, (13, -44, 11), (12, 12, 22), K.concrete('Blk', '#2a2828'))
    br = K.char('brute', V(7.6, -44, 22.05), math.radians(250)); br.scale = (1.6,) * 3; A.idle(K.char_rig(br), 1, nf, amp=1.0)
    lightning(moon_obj(), [2, 6], peak=14)
    c = camera(24)
    shot_cam(c, [(1, (-3, -4, 1.3), (7.6, -44, 24.4), 80, 46), (nf, (-2.95, -4.1, 1.32), (7.6, -44, 24.7), 84, 46)], 1, nf, shake=.02, rshake=.5, seed=907)
    bk = backlight((11, -64, 30), (-3, -4, 2), 400, 18, (.7, .8, 1), 'flashback'); flash_light(bk, [2, 6], 30, 9000)
    return 1, nf

def cut908():   # windshield POV: a slab of facade sheared off by the antlers drops onto the road ahead, hard swerve
    nf = 19; D = 18.; rng, car = chase_set(nf, D, y0=6)
    car.animation_data_clear(); drift(car, [(1, .4, 6, 0), (8, .3, -2, 0), (14, -1.2, -7.5, -16), (nf, -1.8, -11, -22)])
    slab = K.box('slab', col, (1.6, -22, 30), (5.5, 1.2, 4.5), K.facade('SlabF', '#3a3532', seed=3.3))
    slab.data.transform(Matrix.Translation(-V((1.6, -22, 30)))); slab.location = V((1.6, -22, 30))   # origin back to the slab centre
    backlight((-3, -8, 15), (1.6, -22, 2), 1500, 4, (1, .85, .7), 'slabkey')
    for f, z, rx in ((1, 30, 0), (6, 18, 14), (9, 1.9, 24), (11, 1.4, 28), (nf, 1.3, 29)):
        key(slab, f, loc=V((1.6, -22, z)), rot=(math.radians(rx), math.radians(rx * .4), 0))
    dm = K.concrete('Rubble', '#4a4642')
    particles(160, lambda i: 9, lambda i: (1.6 + R.uniform(-2.5, 2.5), -22 + R.uniform(-1, 1), .4),
              lambda i: (R.uniform(-5, 5), R.uniform(-2, 6), R.uniform(2, 7)), life=12, size=.22, mat=dm, tumble=True, shape='rubble')
    c = camera(24); c.parent = car
    for f in range(1, nf + 1):
        tt = f / 24; c.location = V((-.15, -.55, 1.42 + .012 * math.sin(tt * 23))); aim(c, V((-.1, -30, 1.6)))
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    kick(c, [9], 3.5); c.data.dof.use_dof = True; c.data.dof.focus_distance = 14; c.data.dof.aperture_fstop = 4
    return 1, nf

def cut909():   # crash zoom from roof height into the dark, up the leg to the skull: two red points
    nf = 19; st, sg = hero_set(nf)
    eye, eyes = eye_world(sg); wet_eye(eyes, emit=8)
    c = camera(18)
    shot_cam(c, [(1, (1.0, 2.0, 1.5), (.6, -10, 2.5), 18, 12), (7, (1.0, 2.0, 1.5), tuple(eye), 135, (eye - V((1, 2, 1.5))).length),
                 (nf, (1.0, 2.0, 1.5), tuple(eye + V((0, 0, .05))), 140, (eye - V((1, 2, 1.5))).length)], 1, nf, shake=.01, rshake=.35, seed=909)
    kick(c, [7], 1.2); c.data.dof.aperture_fstop = 4
    return 1, nf

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

def cut910():   # ECU of the eye: the Stalker's eyes sit on the sides of the skull (deer-like), so shoot the right eye side-on; car lights slide across it
    nf = 48; st, sg = hero_set(nf)
    _, eyes = eye_world(sg); wet_eye(eyes, emit=1.6)
    car, parts, glowm, spots = nt_car((-6, -3, 0), math.radians(120))
    drift(car, [(1, -6, -2.0, 118), (nf, 6, -3.2, 150)]); linear(car); spin_wheels(parts, 1, nf, 13)
    sc.frame_set(1); dg = bpy.context.evaluated_depsgraph_get()
    eo = [o for o in eyes if o.name.startswith('Stalker eye-1')][0].evaluated_get(dg); m = eo.to_mesh()
    eye = sum((eo.matrix_world @ v.co for v in m.vertices), V((0, 0, 0))) / len(m.vertices); eo.to_mesh_clear()
    front = V((.866, .5, 0))
    if os.environ.get('EYEMOVE', '1') == '1':     # the eye looks around for 2 s, then locks onto the car lights
        eye_saccades(eyes, [(1, 0, 0), (9, 0, 0), (10, -16, 4), (19, -16, 4), (20, 10, -6), (27, 10, -6), (28, -6, 9),
                            (34, -6, 9), (35, 18, 2), (41, 18, 2), (42, 4, -3), (nf, 4, -3)], front)
    c = camera(135)
    shot_cam(c, [(1, tuple(eye + front * 4.2), tuple(eye), 135, 4.2), (nf, tuple(eye + front * 3.2), tuple(eye), 150, 3.2)], 1, nf, shake=.002, rshake=.05, seed=910)
    c.data.dof.aperture_fstop = 5.6
    return 1, nf


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
    plans = {'L': dict(up0=S0 + 3, peak=S0 + 19, hi=24, fwd=-16, down=slam, step=(8, 19)),
             'R': dict(up0=S0 + 10, peak=S0 + 25, hi=15, fwd=-9, down=slam + 5, step=(4, 13))}
    for sd, sx in (('L', 1), ('R', -1)):
        P = plans[sd]; u0, pk, dn = P['up0'], P['peak'], P['down']
        # a creeping step before the scream: lift a few degrees, re-plant
        st0, st1 = P['step']
        stepk = [(1, 0), (st0, 0), (st0 + 3, 5), (st1 - 3, 3), (st1, 0)]
        lift = curve(stepk + [(u0, 0), (u0 + 6, P['hi'] * .55), (pk, P['hi']), (dn - 5, P['hi'] * 1.06), (dn - 1, P['hi'] * .2), (dn, -3.5), (dn + 3, 0), (nf, 0)])
        reach = curve([(1, 0), (u0 + 2, 0), (pk, P['fwd']), (dn - 5, P['fwd'] * 1.2), (dn - 1, P['fwd'] * .3), (dn, 3), (dn + 4, 0), (nf, 0)])
        strain = [1 if u0 + 6 < f < dn - 2 else 0 for f in range(N)]
        trem = [1.3 * strain[f] * nzs[2 + (sx > 0)](t * 9) for f, t in enumerate(tt)]
        drift_ = [.9 * nzs[4 + (sx > 0)](t * .45) for t in tt]           # never perfectly still
        sh = [(-sx) * (.3 * l) for l in lift]
        acc(f'sh{sd}', (0, 1, 0), spring(sh, 2.6, .5))
        chain(seg(sd, 'fa') [:4], (0, 1, 0), [(-sx) * (l + t_ + d) for l, t_, d in zip(lift, trem, drift_)], 3.4, .85, .45, [.4, .3, .2, .1])
        chain(seg(sd, 'fa')[:4], (1, 0, 0), reach, 3.0, .85, .45, [.4, .3, .2, .1])
        # the lower blade folds in as it rises (like a mantis rearing), whips straight on the way down
        fold = curve([(1, 0), (u0 + 2, 0), (u0 + 9, -26 if sd == 'L' else -18), (pk + 3, -14), (dn - 4, -6), (dn - 1, 6), (dn + 2, -4), (dn + 9, 0), (nf, 0)])
        fold = [x + 1.5 * nzs[6 + (sx > 0)](t * .7) for x, t in zip(fold, tt)]
        b1 = [f'fa{sd}1m1', f'fa{sd}1m2', f'fa{sd}1m3', f'fa{sd}1']
        chain(b1, (1, 0, 0), fold, 2.6, .8, .42, [.35, .3, .2, .15])
        # late in the shot one blade drags and scrapes forward (R only), the other just twitches
        if sd == 'R':
            scrape = curve([(1, 0), (96, 0), (104, -7), (112, -5), (120, 0), (nf, 0)])
            chain(b1, (1, 0, 0), scrape, 1.6, .9, .6, [.2, .3, .3, .2])
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

def cut911():   # HERO: the poster frame. car drifts out from between the legs onto its mark, the Stalker screams, the car tears past the lens
    nf = 139; st, sg = hero_set(nf)
    neck, jaw = stalker_alive(sg, 60, 'scream')
    shift_keys(10, [neck, jaw] + [o for o in bpy.data.objects if o.name.startswith(('eyeglow', 'ember'))] +
               [o.data for o in bpy.data.objects if o.name.startswith(('eyeglow', 'ember'))] +
               [m.node_tree for o in sg.children_recursive if o.name.startswith('Stalker eye') for m in o.data.materials if m])
    car, parts, glowm, spots = nt_car((1.0, -40, 0), math.radians(180))
    for sp in spots: sp.energy = 4000
    # v2 skid: the rear steps out and over-rotates (yaw 144), then swings back and settles onto the poster mark; the slide
    # bleeds speed over 24 frames instead of stopping dead; body rolls to the outside, dives, then rocks on its springs
    D = drift(car, [(1, 1.2, -42, 180), (12, 1.0, -16, 182), (19, .35, -8.6, 173), (25, -.7, -5.3, 155), (30, -1.35, -4.05, 144),
                    (35, -1.58, -3.62, 149), (40, -1.52, -3.58, 153), (46, -1.5, -3.6, 152),
                    (100, -1.5, -3.6, 152), (106, -1.2, -2.2, 160), (118, 2.2, 3.6, 178), (128, 3.4, 16, 182)])
    spin_wheels(parts, 1, 40, 40); spin_wheels(parts, 100, 128, 24)
    body = suspension(car, 1, nf, amp=.01, pitch=[(1, 0), (19, 1.2), (27, 2.8), (33, 1.6), (37, -1.6), (41, .9), (46, -.4), (52, .15), (100, .2), (104, -1.8), (128, -.6)])
    roll = [(1, 0), (18, 0), (24, 3.2), (30, 4.0), (35, 1.0), (39, -1.8), (44, .7), (50, -.2), (56, 0), (nf, 0)]
    for f in range(1, nf + 1):
        rv = 0.
        for (fa, va), (fb, vb) in zip(roll, roll[1:]):
            if fa <= f <= fb: u = (f - fa) / max(1, fb - fa); u = u * u * (3 - 2 * u); rv = va + (vb - va) * u
        sc.frame_set(f); body.rotation_euler.y += math.radians(rv); body.keyframe_insert('rotation_euler', frame=f)
    for w_ in wheels(parts): spray(w_, 14, 42, per=5, back=(.4, 1, 0), speed=6, up=1.8)
    stalker_body(sg, nf, slam=60); eye_scale(sg)
    for w_ in wheels(parts)[:2]: spray(w_, 102, 124, per=7, back=(0, 1, 0), speed=6, up=2.2)
    glass_rain(220, 44, 96, (-9, 9), (-18, -6), (5, 18), vel=(0, 3, -1), size=.12)     # windows blown out by the scream
    c = camera(18)
    shot_cam(c, [(1, POSTER_CAM[0], POSTER_CAM[1], 18, 6.0), (nf, POSTER_CAM[0], POSTER_CAM[1], 18, 6.0)], 1, nf, shake=.006, rshake=.22, seed=911)
    kick(c, [32, 40, 48, 60, 116], 2.2); c.data.dof.aperture_fstop = 8
    return 1, nf

def cut912():   # stinger: the camcorder clicks on, the skull is right at the lens
    nf = 4; st, sg = hero_set(nf)
    neck, jaw = stalker_alive(sg, nf, 'close'); eye_scale(sg)
    eye, eyes = eye_world(sg); wet_eye(eyes, emit=4)
    front = (V((1.0, 2.4, .25)) - eye).normalized()
    # face-on: the snout, the blade teeth and both burning sockets fill the camcorder frame (v1 looked up under the jaw)
    c = camera(20); p = eye + front * 2.3 + V((0, 0, -.35)); tg = eye + front * .6 + V((0, 0, -.25))
    shot_cam(c, [(1, tuple(p), tuple(tg), 20, (tg - p).length), (nf, tuple(p + V((0, .04, .01))), tuple(tg), 20, (tg - p).length)], 1, nf, shake=.01, rshake=.6, seed=912)
    camlight(c, 220, 70)
    return 1, nf

f0, f1 = globals()[f'cut{SHOT}']()
bpy.context.view_layer.update()
if os.environ.get('NOFOG') == '1':
    for _l in list(sc.world.node_tree.links):
        if _l.to_node.bl_idname == 'ShaderNodeOutputWorld' and _l.to_socket.name == 'Volume': sc.world.node_tree.links.remove(_l); print('NOFOG: world volume unlinked')
if os.environ.get('LIGHTPATHS') == '1':
    # render() sets bounces itself, so apply these at render start (after render()'s settings)
    def _lightpaths(scene, *a):
        c = scene.cycles; c.max_bounces = 3; c.glossy_bounces = 1; c.transmission_bounces = 2; c.volume_bounces = 0
        c.caustics_reflective = False; c.caustics_refractive = False
        print('LIGHTPATHS applied:', c.max_bounces, c.diffuse_bounces, c.glossy_bounces, c.transmission_bounces, c.volume_bounces)
    bpy.app.handlers.render_init.append(_lightpaths)

# ---- VRAM: the RTX 3050 has 4 GB and these scenes fill it (3.9/4.0 GB, GPU at 34 W = waiting on system RAM).
# Cap texture size at render time (env TEXLIM, default 2048): no visible change at 720x1280, frees a lot of VRAM.
if os.environ.get('TEXLIM', '2048') != '0':
    sc.render.use_simplify = True; sc.cycles.texture_limit_render = os.environ.get('TEXLIM', '2048')
    sc.render.simplify_subdivision_render = 6; sc.render.simplify_child_particles_render = 1.
# ---- diagnostics (read-only): which Cycles devices are on, and a GPU log from nvidia-smi while this chunk renders
if os.environ.get('DEVICE') == 'GPU' and os.name == 'nt':
    import subprocess, atexit
    _od = os.environ.get('OUTROOT', '.'); _tag = f"{SHOT}_{os.environ.get('FR', 'all').replace(',', '-')}"
    def _devlog(scene, *a):
        pr = bpy.context.preferences.addons['cycles'].preferences
        with open(os.path.join(_od, f'diag_{_tag}.txt'), 'a') as fh:
            fh.write(f"device={scene.cycles.device} type={pr.compute_device_type} res={scene.render.resolution_x}x{scene.render.resolution_y}*{scene.render.resolution_percentage}% samp={scene.cycles.samples}\n")
            for d in pr.devices: fh.write(f"  {d.type} {d.name} use={d.use}\n")
    bpy.app.handlers.render_init.append(_devlog)
    try:
        _smi = subprocess.Popen([r'C:\Windows\System32\nvidia-smi.exe', '--query-gpu=timestamp,utilization.gpu,memory.used,memory.total,temperature.gpu,clocks.sm,clocks.max.sm,power.draw,clocks_throttle_reasons.active',
                                 '--format=csv', '-l', '20', '-f', os.path.join(_od, f'gpu_{_tag}.csv')])
        atexit.register(_smi.kill)
    except Exception as _e: print('nvidia-smi failed', _e)
render(f0, f1)
print('CUT DONE', SHOT)
