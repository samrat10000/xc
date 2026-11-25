"""Night city kit for Dead Roads EP1: a rain-soaked avenue with procedural facades (lit / dark /
broken windows), wet asphalt with puddles, curbs, street lamps (sodium, some dead or flickering),
abandoned cars, debris, neon signs, fog volume, rain streaks, a moonlit cloudy sky.
Also: import of cast characters from their .blend files and of the Night Terror car GLB."""
import os, sys, math, random
HERE = os.path.dirname(os.path.abspath(__file__))
CAST = os.path.join(HERE, '..', 'cast')
sys.path.insert(0, CAST)
import bpy, bmesh
from mathutils import Vector, Matrix, Euler, noise
import castlib as L

def V(*a): return Vector(a[0]) if len(a) == 1 else Vector(a)
C = L.lin

# ------------------------------------------------------------------ materials
def nodes(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; return m, nt, nt.nodes, nt.links, nt.nodes['Principled BSDF']

def coord(n, kind='Object'):
    tc = n.new('ShaderNodeTexCoord'); return tc.outputs[kind]

def noise_n(n, l, vec, scale, detail=4, rough=.55, dist=0.):
    t = n.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value = scale; t.inputs['Detail'].default_value = detail
    t.inputs['Roughness'].default_value = rough; t.inputs['Distortion'].default_value = dist
    l.new(vec, t.inputs['Vector']); return t.outputs['Fac']

def mrange(n, l, v, a, b, c=0., d=1.):
    m = n.new('ShaderNodeMapRange'); m.inputs[1].default_value = a; m.inputs[2].default_value = b
    m.inputs[3].default_value = c; m.inputs[4].default_value = d; l.new(v, m.inputs[0]); return m.outputs[0]

def mixc(n, l, f, a, b):
    m = n.new('ShaderNodeMix'); m.data_type = 'RGBA'
    for inp, v in ((m.inputs[0], f), (m.inputs[6], a), (m.inputs[7], b)):
        if isinstance(v, (int, float)): inp.default_value = v
        elif isinstance(v, tuple): inp.default_value = (*v, 1) if len(v) == 3 else v
        else: l.new(v, inp)
    return m.outputs[2]

def math_n(n, l, op, a, b=0.):
    m = n.new('ShaderNodeMath'); m.operation = op
    for inp, v in ((m.inputs[0], a), (m.inputs[1], b)):
        if isinstance(v, (int, float)): inp.default_value = v
        else: l.new(v, inp)
    return m.outputs[0]

def asphalt():
    m, nt, n, l, bs = nodes('Wet_Asphalt')
    co = coord(n, 'Object')
    grain = noise_n(n, l, co, 220, 6, .7); big = noise_n(n, l, co, .9, 5, .6); mid = noise_n(n, l, co, 6, 6, .6)
    col = mixc(n, l, mrange(n, l, grain, .35, .7), C('#0c0c0e'), C('#2a2a2e'))
    col = mixc(n, l, math_n(n, l, 'MULTIPLY', mrange(n, l, mid, .45, .65), .5), col, C('#18161a'))
    # puddles: big noise valleys become mirror-smooth and darker
    pud = mrange(n, l, big, .52, .56)
    col = mixc(n, l, pud, col, C('#050506'))
    l.new(col, bs.inputs['Base Color'])
    l.new(mrange(n, l, pud, 0, 1, .32, .02), bs.inputs['Roughness'])
    bs.inputs['Specular IOR Level'].default_value = .6
    bp = n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = .25; bp.inputs['Distance'].default_value = .003
    l.new(math_n(n, l, 'MULTIPLY', grain, math_n(n, l, 'SUBTRACT', 1., pud)), bp.inputs['Height']); l.new(bp.outputs[0], bs.inputs['Normal'])
    return m

def paint_lines():
    m, nt, n, l, bs = nodes('Road_Paint')
    co = coord(n); wear = noise_n(n, l, co, 30, 6, .7)
    col = mixc(n, l, mrange(n, l, wear, .4, .6), C('#c8b26a'), C('#3a3830'))
    l.new(col, bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = .25
    return m

def concrete(name='Concrete', col='#4a4846'):
    m, nt, n, l, bs = nodes(name)
    co = coord(n); a = noise_n(n, l, co, 3, 6, .6); b = noise_n(n, l, co, 40, 6, .7)
    c = mixc(n, l, mrange(n, l, a, .35, .7), C(col), C('#222020'))
    c = mixc(n, l, math_n(n, l, 'MULTIPLY', mrange(n, l, b, .55, .7), .4), c, C('#141212'))
    l.new(c, bs.inputs['Base Color']); l.new(mrange(n, l, a, 0, 1, .55, .9), bs.inputs['Roughness'])
    bp = n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = .3; bp.inputs['Distance'].default_value = .004
    l.new(b, bp.inputs['Height']); l.new(bp.outputs[0], bs.inputs['Normal'])
    return m

def facade(name, wall='#3a3532', fw=3.2, fh=3.4, lit=.32, seed=0., brick=False):
    """axis-aligned building facade: window grid in world space (u = x + y works on every face),
    each window independently lit warm / cold / flickering-dark / broken."""
    m, nt, n, l, bs = nodes(name)
    wp = coord(n, 'Object')
    sep = n.new('ShaderNodeSeparateXYZ'); l.new(wp, sep.inputs[0])
    u = math_n(n, l, 'ADD', sep.outputs['X'], sep.outputs['Y']); zc = sep.outputs['Z']
    fu = math_n(n, l, 'FRACT', math_n(n, l, 'DIVIDE', u, fw)); fz = math_n(n, l, 'FRACT', math_n(n, l, 'DIVIDE', zc, fh))
    iu = math_n(n, l, 'FLOOR', math_n(n, l, 'DIVIDE', u, fw)); iz = math_n(n, l, 'FLOOR', math_n(n, l, 'DIVIDE', zc, fh))
    cid = n.new('ShaderNodeCombineXYZ'); l.new(iu, cid.inputs[0]); l.new(iz, cid.inputs[1]); cid.inputs[2].default_value = seed
    wn = n.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions = '3D'; l.new(cid.outputs[0], wn.inputs['Vector'])
    rnd = wn.outputs['Value']; rcol = wn.outputs['Color']
    inu = math_n(n, l, 'MULTIPLY', mrange(n, l, fu, .28, .3), mrange(n, l, fu, .72, .7))
    inu = math_n(n, l, 'MULTIPLY', inu, math_n(n, l, 'SUBTRACT', 1., math_n(n, l, 'MULTIPLY', mrange(n, l, fu, .49, .495), mrange(n, l, fu, .51, .505))))   # mullion
    inz = math_n(n, l, 'MULTIPLY', mrange(n, l, fz, .28, .3), mrange(n, l, fz, .86, .84))
    win = math_n(n, l, 'MULTIPLY', inu, inz)
    ground = mrange(n, l, zc, fh * .95, fh * 1.05)        # no windows on the ground floor band
    win = math_n(n, l, 'MULTIPLY', win, ground)
    # wall: grime streaks running down from sills, + optional brick courses
    a = noise_n(n, l, wp, 1.5, 6, .6); st = noise_n(n, l, wp, 3, 4, .5)
    wallc = mixc(n, l, mrange(n, l, a, .35, .7), C(wall), C('#141212'))
    streak = n.new('ShaderNodeMapping'); streak.inputs['Scale'].default_value = (6, 6, .4); l.new(wp, streak.inputs['Vector'])
    sk = noise_n(n, l, streak.outputs[0], 4, 4, .6)
    wallc = mixc(n, l, math_n(n, l, 'MULTIPLY', mrange(n, l, sk, .5, .7), .55), wallc, C('#0c0b0b'))
    if brick:
        br = n.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 1.0
        br.inputs['Mortar Size'].default_value = .012; br.inputs['Color1'].default_value = (*C('#5a2e24'), 1)
        br.inputs['Color2'].default_value = (*C('#3e221c'), 1); br.inputs['Mortar'].default_value = (*C('#2a2622'), 1)
        mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (4, 4, 8); l.new(wp, mp.inputs['Vector']); l.new(mp.outputs[0], br.inputs['Vector'])
        wallc = mixc(n, l, .75, wallc, br.outputs['Color']); wallc = mixc(n, l, mrange(n, l, a, .4, .7), wallc, C('#1a1210'))
    # glass: lit warm/cold, dark, with curtains (inner noise), cracked
    litm = mrange(n, l, rnd, 1 - lit, 1 - lit + .01)
    warm = mixc(n, l, mrange(n, l, math_n(n, l, 'FRACT', math_n(n, l, 'MULTIPLY', rnd, 7.)), .45, .55), C('#ff9a40'), C('#8aa0d0'))
    curt = noise_n(n, l, wp, 8, 3, .5)
    warm = mixc(n, l, math_n(n, l, 'MULTIPLY', mrange(n, l, curt, .45, .6), .6), warm, C('#5a3018'))
    glass = mixc(n, l, .0, C('#06080c'), C('#06080c'))
    base = mixc(n, l, win, wallc, glass)
    l.new(base, bs.inputs['Base Color'])
    l.new(mixc(n, l, win, (.85, .85, .85), (.06, .06, .06)), bs.inputs['Roughness'])
    em = math_n(n, l, 'MULTIPLY', win, litm)
    bs.inputs['Emission Color'].default_value = (1, 1, 1, 1)
    l.new(warm, bs.inputs['Emission Color'])
    l.new(math_n(n, l, 'MULTIPLY', em, 1.1), bs.inputs['Emission Strength'])
    bp = n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = .5; bp.inputs['Distance'].default_value = .02
    l.new(math_n(n, l, 'SUBTRACT', 1., win), bp.inputs['Height']); l.new(bp.outputs[0], bs.inputs['Normal'])
    return m

def emit(name, col, s):
    m, nt, n, l, bs = nodes(name)
    bs.inputs['Base Color'].default_value = (*C(col), 1); bs.inputs['Emission Color'].default_value = (*C(col), 1)
    bs.inputs['Emission Strength'].default_value = s; return m

def metal(name, col='#2a2a2c', rough=.4):
    m, nt, n, l, bs = nodes(name)
    co = coord(n); r = noise_n(n, l, co, 8, 6, .7)
    l.new(mixc(n, l, mrange(n, l, r, .5, .7), C(col), C('#4a2a18')), bs.inputs['Base Color'])
    bs.inputs['Metallic'].default_value = .8; l.new(mrange(n, l, r, 0, 1, rough, .8), bs.inputs['Roughness'])
    return m

def carpaint(name, col):
    m, nt, n, l, bs = nodes(name)
    co = coord(n); d = noise_n(n, l, co, 4, 6, .65); s = noise_n(n, l, co, 60, 4, .6)
    c = mixc(n, l, mrange(n, l, d, .5, .62), C(col), C('#2a2018'))       # dirt & rust patches
    c = mixc(n, l, math_n(n, l, 'MULTIPLY', mrange(n, l, s, .6, .7), .5), c, C('#5a3018'))
    l.new(c, bs.inputs['Base Color']); bs.inputs['Metallic'].default_value = .5
    l.new(mrange(n, l, d, .5, .62, .25, .8), bs.inputs['Roughness']); bs.inputs['Coat Weight'].default_value = .5
    return m

def glass_dark():
    m, nt, n, l, bs = nodes('Car_Glass')
    bs.inputs['Base Color'].default_value = (*C('#05070a'), 1); bs.inputs['Roughness'].default_value = .03
    bs.inputs['Specular IOR Level'].default_value = .9; return m

# ------------------------------------------------------------------ geometry helpers
def box(name, col, loc, size, mat=None, bevel=0.):
    o = L.box(name, loc, tuple(size), col, bevel=bevel)
    L.apply_transform(o)
    if mat: L.setmat(o, mat)
    return o

def building(col, x0, y0, w, d, h, mat, rng, side):
    """block with a cornice, ledges every floor, a roof parapet, rooftop boxes and a fire escape."""
    parts = [box('bld', col, (x0, y0, h / 2), (w, d, h), mat)]
    trim = BTRIM
    for zz in [3.4 * k for k in range(1, int(h / 3.4))]:
        parts.append(box('ledge', col, (x0, y0, zz - .02), (w + .12, d + .12, .1), trim))
    parts.append(box('cornice', col, (x0, y0, h + .2), (w + .4, d + .4, .4), trim))
    for _ in range(rng.randint(1, 3)):
        parts.append(box('roofbox', col, (x0 + rng.uniform(-w / 3, w / 3), y0 + rng.uniform(-d / 3, d / 3), h + .9), (rng.uniform(1, 3), rng.uniform(1, 3), rng.uniform(1, 2)), trim))
    if rng.random() < .55:          # fire escape on the street face
        fx = x0 - side * (w / 2 + .45)
        for zz in [3.4 * k + .2 for k in range(1, int(h / 3.4))]:
            parts.append(box('fe', col, (fx, y0, zz), (.9, 3.0, .05), FE))
            parts.append(box('fer', col, (fx - side * .42, y0, zz + .5), (.03, 3.0, .03), FE))
            parts.append(box('fes', col, (fx, y0 + .6, zz - 1.5), (.8, .06, 3.2), FE))
    return parts

def lamp(col, loc, side, power=900, color='#ffb46a', dead=False):
    pole = L.tube('lamp pole', [V(loc), V(loc) + V(0, 0, 6.2), V(loc) + V(-side * .3, 0, 6.8), V(loc) + V(-side * 1.6, 0, 6.9)], .07, col, sides=10)
    L.setmat(pole, LAMPMETAL)
    head = box('lamp head', col, V(loc) + V(-side * 1.7, 0, 6.82), (.7, .32, .18), LAMPMETAL, bevel=.04)
    lens = box('lamp lens', col, V(loc) + V(-side * 1.7, 0, 6.72), (.55, .24, .03), emit('LampLens' + color, color, 0 if dead else 40))
    if not dead:
        ld = bpy.data.lights.new('sodium', 'SPOT'); ld.energy = power; ld.color = C(color); ld.spot_size = math.radians(110); ld.spot_blend = .6
        ld.shadow_soft_size = .3
        lo = bpy.data.objects.new('sodium', ld); col.objects.link(lo); lo.location = V(loc) + V(-side * 1.7, 0, 6.6)
    return [pole, head, lens]

def sedan(col, loc, rot, paint, rng, wrecked=True):
    """abandoned car: skin-modifier body, cabin, glass, wheels; some doors open/smashed."""
    import anatomy as A
    sk = A.Skel()
    sk.add('r', (0, 2.1, .62), (.86, .42)); sk.add('m', (0, .0, .66), (.92, .46), 'r'); sk.add('f', (0, -2.15, .6), (.86, .38), 'm')
    body = L.skin_body('sedan', sk.j, sk.e, col, branch=.2, subdiv=2)
    L.warp(body, lambda c: V(c.x * 1.0, c.y, max(c.z, .3)))
    cab = L.skin_body('cabin', [((0, .55, 1.05), (.78, .34)), ((0, -.35, 1.05), (.8, .34))], [(0, 1)], col, branch=.2, subdiv=2)
    L.warp(cab, lambda c: V(c.x * .95, c.y, max(c.z, .95)))
    L.setmat(body, paint); L.setmat(cab, GLASS)
    parts = [body, cab]
    for sx in (1, -1):
        for sy in (1.35, -1.4):
            w = L.tube('wheel', [V(sx * .78, sy, .34), V(sx * .98, sy, .34)], .34, col, sides=18)
            L.setmat(w, RUBBER); parts.append(w)
    # lights
    for sx in (1, -1):
        parts.append(box('hl', col, (sx * .6, -2.55, .72), (.32, .05, .12), GLASS))
        parts.append(box('tl', col, (sx * .62, 2.5, .76), (.3, .05, .1), emit('Tail', '#ff2010', 0.0 if wrecked else 6)))
    o = L.join(parts, 'sedan')
    o.location = loc; o.rotation_euler = (0, 0, rot); L.apply_transform(o)
    if wrecked:
        for v in o.data.vertices:
            v.co += V(0, 0, -.06 * max(0, noise.noise(v.co * .9 + V(rng.random() * 9, 0, 0))))
    return o

def trash(col, loc, rng, n=6):
    out = []
    for i in range(n):
        p = V(loc) + V(rng.uniform(-.8, .8), rng.uniform(-.8, .8), 0)
        r = rng.uniform(.18, .32)
        o = L.blob('bag', p + V(0, 0, r * .8), (r, r * .9, r * .8), col)
        for v in o.data.vertices: v.co += v.normal * .05 * noise.noise(v.co * 6 + V(i, 0, 0))
        L.setmat(o, BAG); out.append(o)
    return out

# ------------------------------------------------------------------ the street
def street(col, length=120, width=12, seed=3, lamp_every=18, dead_lamps=(1, 4), flicker=(2,)):
    global BTRIM, FE, LAMPMETAL, GLASS, RUBBER, BAG
    rng = random.Random(seed)
    BTRIM = concrete('Trim', '#2e2c2a'); FE = metal('FireEscape', '#1a1a1c'); LAMPMETAL = metal('LampMetal', '#2a2c2e', .5)
    GLASS = glass_dark(); RUBBER = concrete('Rubber', '#0e0e0e'); BAG = concrete('Bag', '#0a0a0c')
    BAG.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .2
    road = box('road', col, (0, -length / 2 + 20, -.05), (width, length + 40, .1), asphalt())
    swm = concrete('Sidewalk', '#3a3836')
    for sx in (1, -1):
        box('sidewalk', col, (sx * (width / 2 + 2), -length / 2 + 20, .08), (4, length + 40, .16), swm)
        box('curb', col, (sx * (width / 2 + .06), -length / 2 + 20, .08), (.14, length + 40, .2), BTRIM)
    pm = paint_lines()
    for k in range(int((length + 40) / 6)):
        box('dash', col, (0, 20 - k * 6, .002), (.14, 3, .004), pm)
    for sx in (1, -1):
        box('edge line', col, (sx * (width / 2 - .4), -length / 2 + 20, .002), (.12, length + 40, .004), pm)
    # buildings on both sides
    walls = ['#3a3532', '#2e3236', '#463a32', '#33302e', '#2a2a30']
    for sx in (1, -1):
        y = 20.
        while y > -length - 10:
            w = rng.uniform(9, 16); h = rng.choice([12, 15, 18, 22, 28, 34, 45])
            mat = facade(f'Facade{sx}{int(y)}', rng.choice(walls), lit=rng.uniform(.18, .38), seed=rng.random() * 100, brick=rng.random() < .4)
            building(col, sx * (width / 2 + 4 + 6), y - w / 2, 12, w - .3, h, mat, rng, sx)
            # shopfront: dark glass + some neon
            box('shop', col, (sx * (width / 2 + 3.98), y - w / 2, 1.6), (.1, w - 1.2, 2.6), GLASS)
            if rng.random() < .45:
                ncol = rng.choice(['#ff2a6a', '#2affd0', '#ff7a1a', '#7a4aff'])
                box('neon', col, (sx * (width / 2 + 3.9), y - w / 2 + rng.uniform(-2, 2), rng.uniform(3.4, 4.6)), (.08, rng.uniform(1.5, 3), .35), emit('Neon' + ncol, ncol, rng.choice([0, 12, 18])))
            y -= w
    # lamps
    k = 0
    for y in range(10, -length, -lamp_every):
        for sx in (1, -1):
            lamp(col, (sx * (width / 2 + .5), y + (sx * 4), .16), sx, dead=(k % 7) in dead_lamps)
            k += 1
    return rng

def sky(scene, moon=True, fog=.012):
    w = bpy.data.worlds.new('Night'); scene.world = w; w.use_nodes = True
    nt = w.node_tree; n = nt.nodes; l = nt.links; bg = n['Background']
    tc = n.new('ShaderNodeTexCoord'); sep = n.new('ShaderNodeSeparateXYZ'); l.new(tc.outputs['Generated'], sep.inputs[0])
    gen = tc.outputs['Generated']
    sk = n.new('ShaderNodeValToRGB'); cr = sk.color_ramp
    cr.elements[0].position = .5; cr.elements[0].color = (*C('#2a1e22'), 1)
    cr.elements[1].position = .62; cr.elements[1].color = (*C('#070a14'), 1)
    l.new(sep.outputs['Z'], sk.inputs[0])
    cl = n.new('ShaderNodeTexNoise'); cl.inputs['Scale'].default_value = 3; cl.inputs['Detail'].default_value = 8
    l.new(gen, cl.inputs['Vector'])
    mx = n.new('ShaderNodeMix'); mx.data_type = 'RGBA'; l.new(cl.outputs['Fac'], mx.inputs[0])
    l.new(sk.outputs[0], mx.inputs[6]); mx.inputs[7].default_value = (*C('#1c1e2a'), 1)
    l.new(mx.outputs[2], bg.inputs['Color']); bg.inputs['Strength'].default_value = .6
    if moon:
        ml = bpy.data.lights.new('moon', 'SUN'); ml.energy = .35; ml.color = C('#9ab0ff'); ml.angle = math.radians(1.5)
        mo = bpy.data.objects.new('moon', ml); scene.collection.objects.link(mo); mo.rotation_euler = (math.radians(55), 0, math.radians(150))
    if fog:
        vs = n.new('ShaderNodeVolumeScatter'); vs.inputs['Density'].default_value = fog; vs.inputs['Anisotropy'].default_value = .5
        l.new(vs.outputs[0], n['World Output'].inputs['Volume'])
    scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.cycles.volume_step_rate = 4; scene.cycles.max_bounces = 6; scene.cycles.volume_bounces = 0

def rain(col, center, size=(14, 40, 14), count=2500, seed=1, streak=.35):
    rng = random.Random(seed); bm = bmesh.new()
    for i in range(count):
        p = V(center) + V(rng.uniform(-size[0] / 2, size[0] / 2), rng.uniform(-size[1] / 2, size[1] / 2), rng.uniform(0, size[2]))
        ln = streak * rng.uniform(.6, 1.2); w = .004
        a = bm.verts.new(p + V(-w, 0, 0)); b = bm.verts.new(p + V(w, 0, 0)); c = bm.verts.new(p + V(w + .02, 0, -ln)); d = bm.verts.new(p + V(-w + .02, 0, -ln))
        bm.faces.new((a, b, c, d))
    o = L.mesh_obj('rain', bm, col)
    m, nt, n, l, bs = nodes('Rain'); bs.inputs['Base Color'].default_value = (.8, .85, 1, 1); bs.inputs['Roughness'].default_value = 0
    bs.inputs['Transmission Weight'].default_value = 1.; bs.inputs['Alpha'].default_value = .35
    bs.inputs['Emission Color'].default_value = (.7, .8, 1, 1); bs.inputs['Emission Strength'].default_value = .15
    L.setmat(o, m); o.visible_shadow = False
    return o

# ------------------------------------------------------------------ cast + car import
def char(name, loc, rot_z=0., scale=1., col=None):
    """append every mesh of cast/out/<name>/<name>.blend under one empty."""
    path = os.path.join(CAST, 'out', name, f'{name}.blend')
    with bpy.data.libraries.load(path, link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    root = bpy.data.objects.new(f'{name} root', None); (col or bpy.context.scene.collection).objects.link(root)
    for o in dst.objects:
        if o is None or o.type != 'MESH' or o.name.startswith('floor'): continue
        (col or bpy.context.scene.collection).objects.link(o); o.parent = root
    root.location = loc; root.rotation_euler = (0, 0, rot_z); root.scale = (scale,) * 3
    return root

def night_terror(loc, rot_z=0., col=None):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(HERE, 'car', 'nt.glb'))
    new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new('NT root', None); (col or bpy.context.scene.collection).objects.link(root)
    for o in new:
        if o.parent is None: o.parent = root
        if 'hull' in o.name.lower(): o.hide_render = True
    root.location = loc; root.rotation_euler = (0, 0, rot_z)
    return root, new

def cam(scene, loc, target, lens=35, name='shot'):
    c = bpy.data.cameras.new(name); c.lens = lens; c.sensor_width = 36
    o = bpy.data.objects.new(name, c); scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (V(target) - V(loc)).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = o; return o

def setup_render(scene, w=1080, h=1920, samples=64):
    scene.render.resolution_x = w; scene.render.resolution_y = h
    scene.cycles.samples = samples; scene.cycles.use_denoising = True
    scene.cycles.denoiser = 'OPENIMAGEDENOISE'
    scene.cycles.light_sampling_threshold = .02
