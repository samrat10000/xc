import bpy, math, os, sys
from mathutils import Vector, Matrix, Euler
sys.path.insert(0, '/home/user/w/models')
W = '/home/user/w'
def V(*a): return Vector(a[0]) if len(a) == 1 else Vector(a)

def prim(kind, **kw):
    """add a mesh primitive and return exactly the new object (never trust context.object)"""
    for o in bpy.context.view_layer.objects: o.select_set(False)
    before = set(bpy.data.objects)
    getattr(bpy.ops.mesh, f'primitive_{kind}_add')(**kw)
    new = [o for o in bpy.data.objects if o not in before]
    o = new[0]; bpy.context.view_layer.objects.active = o; o.select_set(True)
    return o

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.render.fps = 24
    return sc

def append(blend, colname):
    with bpy.data.libraries.load(blend, link=False) as (src, dst):
        dst.collections = [c for c in src.collections if c == colname]
    c = dst.collections[0]
    bpy.context.scene.collection.children.link(c)
    return c

def trike():
    c = append(f'{W}/sc/trike.blend', 'TRIKE')
    o = {k: bpy.data.objects[k] for k in ('TRIKE_root', 'TRIKE_body', 'wF', 'wRL', 'wRR')}
    return c, o

def rider(blend=f'{W}/out/rider/rider.blend'):
    c = append(blend, 'RIDER')
    rig = [o for o in c.all_objects if o.type == 'ARMATURE'][0]
    return c, rig

def empty(name, loc, parent=None):
    e = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(e)
    e.location = loc
    if parent: e.parent = parent
    return e

def ik(rig, bone, target, pole=None, chain=4, pole_angle=0.):
    pb = rig.pose.bones[bone]; c = pb.constraints.new('IK'); c.target = target; c.chain_count = chain
    if pole: c.pole_target = pole; c.pole_angle = math.radians(pole_angle)
    return c

def pose(rig, rots):
    for bn, r in rots.items():
        pb = rig.pose.bones[bn]; pb.rotation_mode = 'XYZ'; pb.rotation_euler = Euler([math.radians(a) for a in r])

def seat_rider(rig, trike_body, seat=V(0.42, 0, 1.30)):
    """place the rider in the trike cockpit, facing -X, with IK hands on the yoke and feet forward"""
    rig.parent = trike_body; rig.matrix_parent_inverse = Matrix()
    rig.location = (0, 0, 0); rig.rotation_euler = (0, 0, math.radians(-90))
    bpy.context.view_layer.update()
    inv = trike_body.matrix_world.inverted()
    hl = inv @ rig.matrix_world @ rig.pose.bones['upperleg01.L'].head; hr = inv @ rig.matrix_world @ rig.pose.bones['upperleg01.R'].head
    hip = (hl + hr) / 2
    rig.location = seat - hip
    ts = {}
    for s, sy in (('L', 1), ('R', -1)):
        # character left (+X local) becomes world -Y after the -90 turn? local +X -> world (0,-1)? compute
        side = (rig.matrix_basis.to_3x3() @ V(1, 0, 0)).normalized() * (1 if s == 'L' else -1)
        hand = empty(f'hand.{s}', V(-0.36, 0, 1.66) + side * .17, trike_body)
        ep = empty(f'elbow.{s}', V(0.3, 0, 1.45) + side * .55, trike_body)
        foot = empty(f'foot.{s}', V(-0.75, 0, 1.12) + side * .2, trike_body)
        kp = empty(f'knee.{s}', V(-0.6, 0, 2.2) + side * .25, trike_body)
        ik(rig, f'lowerarm02.{s}', hand, ep, 4, -90)
        ik(rig, f'lowerleg02.{s}', foot, kp, 4, -90)
        ts[s] = dict(hand=hand, elbow=ep, foot=foot, knee=kp)
    pose(rig, {'spine04': (6, 0, 0), 'spine03': (4, 0, 0), 'neck01': (-6, 0, 0), 'head': (-4, 0, 0)})
    for s in 'LR':
        for f in range(2, 6):
            for k in (1, 2, 3): pose(rig, {f'finger{f}-{k}.{s}': (55, 0, 0)})
    return ts

def cam(loc, tgt, lens=35, name='cam'):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36; cd.clip_start = .008; cd.clip_end = 600
    co = bpy.data.objects.new(name, cd); bpy.context.scene.collection.objects.link(co)
    co.location = loc; co.rotation_euler = (V(tgt) - V(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = co
    return co

def render_setup(sc, res=.4, samp=16, w=1080, h=1920):
    sc.render.resolution_x = int(w * res); sc.render.resolution_y = int(h * res); sc.render.resolution_percentage = 100
    sc.cycles.samples = samp; sc.cycles.use_denoising = True
    try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc.cycles.max_bounces = 6; sc.cycles.diffuse_bounces = 2; sc.cycles.glossy_bounces = 2; sc.cycles.transparent_max_bounces = 8
    sc.render.image_settings.file_format = 'PNG'
    sc.view_settings.view_transform = 'AgX'
    try: sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception: pass

# ------------------------------------------------------------------ cast loaders + procedural acting
import random
def _fixparents(c, rig, bone='head'):
    for o in c.all_objects:
        if o is rig or o.parent is not None: continue
        if o.type in ('LIGHT', 'CAMERA') or o.name.startswith('floor'): bpy.data.objects.remove(o); continue
        mw = o.matrix_world.copy(); o.parent = rig; o.parent_type = 'OBJECT'; o.matrix_world = mw

def walker(loc, rotz=0., seed=0, blend=f'{W}/out/walker/walker.blend'):
    c = append(blend, 'Walker')
    rig = [o for o in c.all_objects if o.type == 'ARMATURE'][0]
    _fixparents(c, rig)
    for o in list(c.all_objects):
        if o.name.startswith(('fill', 'floor', 'key', 'rim')) and o.type != 'MESH' or o.name.startswith('floor'):
            bpy.data.objects.remove(o)
    rig.location = loc; rig.rotation_euler = (0, 0, rotz)
    rig['seed'] = seed
    rig['base'] = {pb.name: list(pb.rotation_euler) for pb in rig.pose.bones if pb.rotation_mode == 'XYZ'}
    s = 1 + random.Random(seed).uniform(-.06, .06); rig.scale = (s, s, s)
    return rig

def _key(pb, f, rot):
    pb.rotation_mode = 'XYZ'; pb.rotation_euler = rot; pb.keyframe_insert('rotation_euler', frame=f)

def act(rig, f0, f1, fn, step=1):
    """fn(rig, t_seconds, frame) -> dict bone: (dx,dy,dz) degrees offset on top of the base pose; keys every `step`"""
    base = rig['base']
    fps = bpy.context.scene.render.fps
    for f in range(f0, f1 + 1, step):
        d = fn(rig, (f - f0) / fps, f)
        for bn, off in d.items():
            if bn.startswith('_'): continue
            pb = rig.pose.bones[bn]
            b = base.get(bn, [0, 0, 0])
            _key(pb, f, Euler([b[i] + math.radians(off[i]) for i in range(3)]))

def shamble(seed, speed=1.):
    r = random.Random(seed); per = r.uniform(1.25, 1.6) / speed; ph0 = r.uniform(0, 6.28); lean = r.uniform(-4, 6)
    def fn(rig, t, f):
        p = ph0 + t / per * 6.283; s = math.sin(p); c = math.cos(p)
        return {'upperleg01.L': (16 * s, 0, 0), 'upperleg01.R': (-16 * s, 0, 0),
                'lowerleg01.L': (-22 * max(0, math.sin(p + 1.3)), 0, 0), 'lowerleg01.R': (-22 * max(0, math.sin(p + 1.3 + 3.14)), 0, 0),
                'foot.L': (8 * max(0, -s), 0, 0), 'foot.R': (8 * max(0, s), 0, 0),
                'spine04': (lean + 2 * math.sin(2 * p), 0, 6 * s), 'spine02': (1.5 * math.sin(2 * p + 1), 3 * c, 0),
                'neck01': (0, 5 * math.sin(p * .5 + 1), 4 * math.sin(p * .37)), 'head': (6 * math.sin(p * .7 + 2), 7 * math.sin(p * .5), 8 * math.sin(p * .31 + seed)),
                'jaw': (-6 * (.5 + .5 * math.sin(p * .9 + seed)), 0, 0),
                'upperarm01.L': (8 * -s, 0, 4 * c), 'upperarm01.R': (8 * s, 0, -4 * c),
                'lowerarm01.L': (0, 0, 6 * math.sin(p + .8)), 'lowerarm01.R': (0, 0, -6 * math.sin(p + .8)),
                'wrist.L': (10 * math.sin(p * 1.3), 0, 0), 'wrist.R': (10 * math.sin(p * 1.1 + 1), 0, 0)}
    return fn, per

def move_keys(rig, f0, f1, speed, seed=0, per=1.4, bob=.025):
    """root travel along the facing direction plus a heavy-footed bob and side sway"""
    fps = bpy.context.scene.render.fps
    fwd = (rig.matrix_world.to_3x3() @ V(0, -1, 0)).normalized(); side = V(-fwd.y, fwd.x, 0)
    p0 = rig.location.copy(); r0 = rig.rotation_euler.copy()
    for f in range(f0, f1 + 1):
        t = (f - f0) / fps; ph = t / per * 6.283
        rig.location = p0 + fwd * speed * t + side * .03 * math.sin(ph) + V(0, 0, -bob * abs(math.cos(ph)))
        rig.rotation_euler = (r0.x, r0.y + math.radians(3) * math.sin(ph), r0.z)
        rig.keyframe_insert('location', frame=f); rig.keyframe_insert('rotation_euler', frame=f)

def headshot(rig, fh, seed=0, back=1., walkfn=None, dur=18):
    """head snaps back on the hit, knees fold, body topples backwards and settles on the road"""
    r = random.Random(seed + 99); side = r.choice((-1, 1)); fps = bpy.context.scene.render.fps
    fwd = (rig.matrix_world.to_3x3() @ V(0, -1, 0)).normalized()
    p0 = rig.location.copy(); r0 = rig.rotation_euler.copy()
    for f in range(fh, fh + dur + 12):
        k = min(1, (f - fh) / dur); g = k * k   # gravity ease-in
        snap = min(1, (f - fh) / 2.)
        rig.location = p0 - fwd * (.35 * back * k) + V(0, 0, -.12 * math.sin(min(1, k * 1.6) * 1.57))
        rig.rotation_euler = (r0.x - math.radians(84) * g * back, r0.y + math.radians(10 * side) * g, r0.z + math.radians(14 * side) * k)
        # local X rotation of object: topple about the feet. Object X axis is the character's side axis.
        rig.keyframe_insert('location', frame=f); rig.keyframe_insert('rotation_euler', frame=f)
        fl = math.exp(-((f - fh - dur) / 2.5) ** 2) if f > fh + dur - 4 else 0   # bounce on landing
        base = rig['base']
        d = {'head': (-38 * snap + 10 * k + 6 * fl, 6 * side * snap, 0), 'neck01': (-18 * snap, 0, 0), 'jaw': (-22 * snap, 0, 0),
             'lowerleg01.L': (-50 * min(1, k * 2) * (1 - g * .6), 0, 0), 'lowerleg01.R': (-38 * min(1, k * 2) * (1 - g * .6), 0, 0),
             'upperleg01.L': (30 * min(1, k * 2) * (1 - g * .5), 0, 0), 'upperleg01.R': (20 * min(1, k * 2) * (1 - g * .5), 0, 0),
             'upperarm01.L': (-25 * k, 0, 25 * k), 'upperarm01.R': (-25 * k, 0, -25 * k), 'spine04': (-12 * k, 0, 0), 'spine02': (-8 * k - 6 * fl, 0, 0)}
        for bn, off in d.items():
            b = base.get(bn, [0, 0, 0]); _key(rig.pose.bones[bn], f, Euler([b[i] + math.radians(off[i]) for i in range(3)]))

_bloodm = None
def blood_mat():
    global _bloodm
    if _bloodm: return _bloodm
    m = bpy.data.materials.new('Blood'); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (.12, .004, .006, 1); b.inputs['Roughness'].default_value = .15
    b.inputs['Coat Weight'].default_value = .6
    _bloodm = m; return m

def blood_burst(at, direction, f0, n=36, seed=0, speed=4., size=.018, col=None):
    """ballistic droplets from the exit wound: keyed spheres, stretched along velocity"""
    r = random.Random(seed); fps = bpy.context.scene.render.fps; col = col or bpy.context.scene.collection
    proto = prim('ico_sphere', subdivisions=1, radius=1)
    me = proto.data; me.materials.append(blood_mat()); bpy.data.objects.remove(proto)
    d0 = V(direction).normalized()
    for i in range(n):
        o = bpy.data.objects.new(f'drop{seed}_{i}', me); col.objects.link(o)
        v = (d0 + V(r.gauss(0, .45), r.gauss(0, .45), r.gauss(.15, .4))).normalized() * speed * r.uniform(.4, 1.3)
        s = size * r.uniform(.4, 1.4)
        o.scale = (0, 0, 0); o.location = at; o.keyframe_insert('scale', frame=f0 - 1); o.keyframe_insert('location', frame=f0 - 1)
        for k in range(0, 22):
            t = k / fps; p = V(at) + v * t + V(0, 0, -4.9 * t * t)
            if p.z < .01: p.z = .01
            vel = v + V(0, 0, -9.8 * t)
            o.location = p; o.rotation_euler = vel.to_track_quat('Z', 'Y').to_euler()
            st = 1 + min(3, vel.length * .6)
            o.scale = (s, s, s * st) if p.z > .02 else (s * 1.8, s * 1.8, s * .3)
            for path in ('location', 'rotation_euler', 'scale'): o.keyframe_insert(path, frame=f0 + k)

# ------------------------------------------------------------------ set
def city():
    sys.path.insert(0, '/mnt/project-files/reels/series/ep1')
    import city as K
    return K

def spot(name, loc, tgt, energy, color=(1, .85, .6), size=40, blend=.4, radius=.1, parent=None):
    l = bpy.data.lights.new(name, 'SPOT'); l.energy = energy; l.color = color; l.spot_size = math.radians(size); l.spot_blend = blend
    l.shadow_soft_size = radius
    o = bpy.data.objects.new(name, l); bpy.context.scene.collection.objects.link(o)
    if parent: o.parent = parent   # loc/tgt are in the parent's space
    o.location = loc; o.rotation_euler = (V(tgt) - V(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o

# ------------------------------------------------------------------ Stalker
from mathutils import Quaternion
def stalker(loc, rotz=0., blend=f'{W}/out/stalker/stalker_rig.blend'):
    c = append(blend, 'Stalker')
    rig = [o for o in c.all_objects if o.type == 'ARMATURE'][0]
    rig.location = loc; rig.rotation_euler = (0, 0, rotz)
    for pb in rig.pose.bones: pb.rotation_mode = 'QUATERNION'
    return rig

def arm_rot(pb, rots):
    """rots: list of (axis 'X'|'Y'|'Z' in armature space, degrees) -> local quaternion"""
    M = pb.bone.matrix_local.to_3x3()
    q = Quaternion()
    for ax, d in rots:
        a = {'X': V(1, 0, 0), 'Y': V(0, 1, 0), 'Z': V(0, 0, 1)}[ax]
        q = Quaternion(M.inverted() @ a, math.radians(d)) @ q
    return q

def sact(rig, f0, f1, fn, step=1):
    fps = bpy.context.scene.render.fps
    for f in range(f0, f1 + 1, step):
        d = fn((f - f0) / fps, f)
        for bn, rots in d.items():
            if bn == '_root':
                rig.location, rig.rotation_euler = rots[0], rots[1]
                rig.keyframe_insert('location', frame=f); rig.keyframe_insert('rotation_euler', frame=f); continue
            pb = rig.pose.bones[bn]; pb.rotation_quaternion = arm_rot(pb, rots); pb.keyframe_insert('rotation_quaternion', frame=f)

def stalk_pose(t, gait=0., gph=0., stride=1., jaw=0., tilt=0., look=(0, 0), breathe=1., hit=0., crouch=0.):
    """gait 0 = stand, 1 = full walk; gph phase radians; jaw 0..1 (1 = unhinged); tilt head roll deg; look (yaw, pitch) deg; hit = recoil 0..1"""
    s = math.sin(gph); c = math.cos(gph); g = gait * stride
    b = math.sin(t * 2.4) * breathe
    d = {
        'sp0m1': [('X', -2 * b - 10 * hit + 6 * crouch)], 'sp1m1': [('X', -1.5 * b - 8 * hit), ('Z', 4 * g * s)], 'sp2m1': [('X', 2 * b - 6 * hit), ('Y', 3 * g * c)],
        'nk0m1': [('X', look[1] * .4 - 5 * hit), ('Z', look[0] * .4)], 'nk1m1': [('X', look[1] * .3), ('Z', look[0] * .3)],
        'head': [('X', look[1] * .3 + 12 * hit), ('Z', look[0] * .3), ('Y', tilt)],
        'jaw': [('X', 48 * jaw + 3 * math.sin(t * 6) * jaw)],
    }
    for sd, ph in (('L', 0.), ('R', math.pi)):
        p = gph + ph; sp = math.sin(p); lift = max(0, math.sin(p + 1.4))
        d[f'hl{sd}0m1'] = [('X', -22 * g * sp + 14 * crouch)]
        d[f'hl{sd}1m1'] = [('X', 26 * g * lift - 10 * crouch)]
        d[f'fa{sd}0m1'] = [('X', 24 * g * math.sin(p + math.pi * .5)), ('Y', (4 if sd == 'L' else -4) * b)]
        d[f'fa{sd}1m1'] = [('X', -18 * g * max(0, math.sin(p + math.pi * .5 + 1.4)))]
        d[f'ca{sd}0m1'] = [('X', 25 * math.sin(t * 7 + ph) * (.3 + gait)), ('Z', 15 * math.sin(t * 5 + ph))]
    return d
