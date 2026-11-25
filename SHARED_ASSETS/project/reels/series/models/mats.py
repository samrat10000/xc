"""Procedural Cycles materials for the cast (colour + bump), and a baker that turns them into
UV textures (base colour + tangent normal + roughness) so the GLB carries the detail."""
import bpy, os
import castlib as L
STYLE = {"cavity": True}

class NB:
    def __init__(s, name):
        s.m = bpy.data.materials.new(name); s.m.use_nodes = True
        s.nt = s.m.node_tree; s.n = s.nt.nodes; s.l = s.nt.links
        s.bsdf = s.n['Principled BSDF']; s.out = s.n['Material Output']
        tc = s.n.new('ShaderNodeTexCoord'); s.co = tc.outputs['Object']
        s.bumps = []
    def node(s, t, **kw):
        nd = s.n.new(t)
        for k, v in kw.items():
            if k in nd.inputs: nd.inputs[k].default_value = v
            else: setattr(nd, k, v)
        return nd
    def link(s, a, b): s.l.new(a, b); return b
    def mapping(s, scale=(1, 1, 1), loc=(0, 0, 0), rot=(0, 0, 0), src=None):
        m = s.node('ShaderNodeMapping'); m.inputs['Scale'].default_value = scale
        m.inputs['Location'].default_value = loc; m.inputs['Rotation'].default_value = rot
        s.link(src or s.co, m.inputs['Vector']); return m.outputs[0]
    def noise(s, scale, detail=4, rough=.55, vec=None, dist=0.):
        nd = s.node('ShaderNodeTexNoise', **{'Scale': scale, 'Detail': detail, 'Roughness': rough, 'Distortion': dist})
        s.link(vec or s.co, nd.inputs['Vector']); return nd.outputs['Fac']
    def voronoi(s, scale, feature='F1', metric='EUCLIDEAN', vec=None, out='Distance', rand=1.):
        nd = s.node('ShaderNodeTexVoronoi', feature=feature, distance=metric)
        nd.inputs['Scale'].default_value = scale
        if 'Randomness' in nd.inputs: nd.inputs['Randomness'].default_value = rand
        s.link(vec or s.co, nd.inputs['Vector']); return nd.outputs[out]
    def wave(s, scale, kind='BANDS', axis='X', profile='SIN', dist=0., detail=2, vec=None, phase=0.):
        nd = s.node('ShaderNodeTexWave', wave_type=kind, bands_direction=axis, wave_profile=profile)
        nd.inputs['Scale'].default_value = scale; nd.inputs['Distortion'].default_value = dist
        nd.inputs['Detail'].default_value = detail
        if 'Phase Offset' in nd.inputs: nd.inputs['Phase Offset'].default_value = phase
        s.link(vec or s.co, nd.inputs['Vector']); return nd.outputs['Fac']
    def ramp(s, fac, stops, interp='LINEAR'):
        r = s.node('ShaderNodeValToRGB'); cr = r.color_ramp; cr.interpolation = interp
        while len(cr.elements) > len(stops): cr.elements.remove(cr.elements[-1])
        while len(cr.elements) < len(stops): cr.elements.new(0)
        for e, (pos, col) in zip(cr.elements, stops):
            e.position = pos; e.color = (*col, 1) if len(col) == 3 else col
        s.link(fac, r.inputs['Fac']); return r.outputs['Color']
    def mix(s, fac, a, b, blend='MIX'):
        m = s.node('ShaderNodeMix', data_type='RGBA', blend_type=blend)
        for inp, v in ((m.inputs[0], fac), (m.inputs[6], a), (m.inputs[7], b)):
            if isinstance(v, (int, float)): inp.default_value = v
            elif isinstance(v, tuple): inp.default_value = (*v, 1) if len(v) == 3 else v
            else: s.link(v, inp)
        return m.outputs[2]
    def math(s, op, a, b=0., clamp=False):
        m = s.node('ShaderNodeMath', operation=op, use_clamp=clamp)
        for inp, v in ((m.inputs[0], a), (m.inputs[1], b)):
            if isinstance(v, (int, float)): inp.default_value = v
            else: s.link(v, inp)
        return m.outputs[0]
    def mr(s, fac, a, b, c=0., d=1.):   # map range
        m = s.node('ShaderNodeMapRange'); m.inputs['From Min'].default_value = a; m.inputs['From Max'].default_value = b
        m.inputs['To Min'].default_value = c; m.inputs['To Max'].default_value = d
        s.link(fac, m.inputs['Value']); return m.outputs[0]
    def bump(s, height, strength=.3, dist=.002):
        b = s.node('ShaderNodeBump'); b.inputs['Strength'].default_value = strength; b.inputs['Distance'].default_value = dist
        s.link(height, b.inputs['Height'])
        if s.bumps: s.link(s.bumps[-1], b.inputs['Normal'])
        s.bumps.append(b.outputs['Normal']); return b
    def cavity(s, color, dist=.025, strength=.5, edge=.0):
        ao = s.node('ShaderNodeAmbientOcclusion', samples=16); ao.inputs['Distance'].default_value = dist
        f = s.mr(ao.outputs['AO'], .25, 1., 1 - strength, 1.)
        return s.mix(1., color, s.color_of(f), 'MULTIPLY')
    def color_of(s, fac):
        cm = s.node('ShaderNodeCombineColor')
        for i in range(3): s.link(fac, cm.inputs[i])
        return cm.outputs[0]
    def finish(s, color, rough=.6, metal=0., sss=0., spec=.4, rough_sock=None, cav=True):
        if cav and STYLE.get('cavity'): color = s.cavity(color, **STYLE.get('cav_kw', {}))
        s.link(color, s.bsdf.inputs['Base Color'])
        if rough_sock is not None: s.link(rough_sock, s.bsdf.inputs['Roughness'])
        else: s.bsdf.inputs['Roughness'].default_value = rough
        s.bsdf.inputs['Metallic'].default_value = metal
        s.bsdf.inputs['Specular IOR Level'].default_value = spec
        if sss:
            s.bsdf.inputs['Subsurface Weight'].default_value = sss
            s.bsdf.inputs['Subsurface Radius'].default_value = (.03, .015, .01)
            s.bsdf.inputs['Subsurface Scale'].default_value = .05
        if s.bumps: s.link(s.bumps[-1], s.bsdf.inputs['Normal'])
        s.color = color
        return s.m

def C(h): return L.lin(h)

# ------------------------------------------------------------------ library
def zombie_skin(name, base='#87927a', dark='#4c5944', light='#aeb095', bruise='#5e3f58', vein='#3b3150',
                blood='#5c1015', rot='#4a3b2c', gore_vec=None):
    b = NB(name)
    big = b.noise(4, 6, .6); mid = b.noise(18, 8, .6); fine = b.noise(90, 4, .5)
    c = b.ramp(big, [(.4, C(dark)), (.5, C(base)), (.6, C(light))])
    c = b.mix(b.mr(mid, .46, .6, 0, .45), c, C(light))
    br = b.mr(b.noise(3.2, 5, .6, vec=b.mapping(loc=(7, 3, 1))), .52, .6)
    c = b.mix(b.math('MULTIPLY', br, .8), c, C(bruise))
    # veins: thin ridges of distorted noise, masked into patches
    vn = b.noise(17, 5, .55, vec=b.mapping(loc=(2, 9, 4)), dist=.6)
    vline = b.mr(b.math('ABSOLUTE', b.math('SUBTRACT', vn, .5)), .0, .006, 1, 0)
    vmask = b.mr(b.noise(4, 3, .5, vec=b.mapping(loc=(5, 1, 8))), .5, .58)
    veins = b.math('MULTIPLY', vline, vmask)
    c = b.mix(b.math('MULTIPLY', veins, .55), c, C(vein))
    # rot patches (cracked, darker, wet)
    cell = b.voronoi(45, 'DISTANCE_TO_EDGE'); rmask = b.mr(b.noise(5, 6, .6, vec=b.mapping(loc=(1, 1, 9))), .54, .6)
    cracks = b.math('MULTIPLY', b.mr(cell, .0, .06, 1, 0), rmask)
    c = b.mix(b.math('MULTIPLY', rmask, .75), c, C(rot))
    c = b.mix(b.math('MULTIPLY', cracks, .9), c, C('#1e1412'))
    c = b.mix(b.math('MULTIPLY', b.mr(fine, .4, .7), .25), c, C(dark))
    # grime layer: dark, blotchy, collects in large noise valleys
    gm = b.mr(b.noise(7, 8, .7, vec=b.mapping(loc=(9, 4, 2))), .5, .6)
    c = b.mix(b.math('MULTIPLY', gm, .55), c, C('#2e2a20'))
    # scratches: thin stretched voronoi edges
    sc_ = b.mr(b.voronoi(30, 'DISTANCE_TO_EDGE', vec=b.mapping(scale=(1, 1, 7), rot=(0, .4, .3))), 0, .02, 1, 0)
    scm = b.math('MULTIPLY', sc_, b.mr(b.noise(3, 2, .5, vec=b.mapping(loc=(2, 2, 2))), .52, .57))
    c = b.mix(b.math('MULTIPLY', scm, .8), c, C('#5a1a18'))
    b.bump(b.math('SUBTRACT', 1, scm), .5, .0015)
    b.bump(b.noise(12, 4, .5, vec=b.mapping(scale=(1, 1, 6))), .35, .003)   # wrinkles
    # bump: pores, wrinkles, veins raised, cracks sunk
    b.bump(fine, .25, .0008)
    b.bump(b.voronoi(160), .15, .0006)
    b.bump(veins, .45, .0015)
    b.bump(b.math('SUBTRACT', 1, cracks), .6, .002)
    b.bump(b.noise(30, 6, .7), .3, .002)
    rough = b.mr(rmask, 0, 1, .62, .3)
    m = b.finish(c, sss=.06, spec=.45, rough_sock=rough)
    return m

def flannel(name, a='#7a2a2c', bnd='#22161c', line='#c9a36a', grime='#3d342a', blood='#4a0c10', scale=22.):
    b = NB(name)
    nz = b.node('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6; b.link(b.co, nz.inputs['Vector'])
    vm = b.node('ShaderNodeVectorMath', operation='MULTIPLY_ADD'); b.link(nz.outputs['Color'], vm.inputs[0])
    vm.inputs[1].default_value = (.012, .012, .012); b.link(b.co, vm.inputs[2]); wv = vm.outputs[0]
    vx = b.wave(scale, 'BANDS', 'X', 'SAW', vec=wv); vz = b.wave(scale, 'BANDS', 'Z', 'SAW', vec=wv)
    bx = b.mr(vx, .45, .5); bz = b.mr(vz, .45, .5)
    tx = b.mr(vx, .82, .84); tz = b.mr(vz, .82, .84)
    c = b.mix(b.math('MAXIMUM', bx, bz), C(a), C(bnd))
    c = b.mix(b.math('MULTIPLY', bx, bz), c, C('#120b10'))
    c = b.mix(b.math('MULTIPLY', b.math('MAXIMUM', tx, tz), .45), c, C(line))
    b.bump(b.noise(14, 4, .5, vec=b.mapping(scale=(1, 1, 5))), .5, .003)
    # twill weave micro bump
    tw = b.wave(900, 'BANDS', 'X', 'SIN', vec=b.mapping(rot=(0, .785, 0)))
    b.bump(tw, .25, .0006)
    b.bump(b.noise(60, 6, .7), .2, .001)
    gr = b.mr(b.noise(6, 6, .6), .45, .75)
    c = b.mix(b.math('MULTIPLY', gr, .6), c, C(grime))
    bl = b.mr(b.noise(3, 6, .7, vec=b.mapping(loc=(4, 4, 2))), .62, .7)
    c = b.mix(bl, c, C(blood))
    return b.finish(c, rough=.88, spec=.2)

def denim(name, base='#2c3650', fade='#5a6684', mud='#3b3025', blood='#4a0c10'):
    b = NB(name)
    tw = b.wave(700, 'BANDS', 'X', 'SIN', vec=b.mapping(rot=(0, .6, 0)))
    c = b.mix(b.math('MULTIPLY', tw, .25), C(base), C(fade))
    f = b.mr(b.noise(5, 6, .6), .45, .75)
    c = b.mix(b.math('MULTIPLY', f, .6), c, C(fade))
    # mud rising from the hem (object z)
    sep = b.node('ShaderNodeSeparateXYZ'); b.link(b.co, sep.inputs[0])
    hz = b.mr(sep.outputs['Z'], .4, .12)
    mudn = b.math('MULTIPLY', hz, b.mr(b.noise(14, 6, .7), .3, .6))
    c = b.mix(mudn, c, C(mud))
    bl = b.mr(b.noise(4, 6, .7, vec=b.mapping(loc=(8, 2, 0))), .64, .72)
    c = b.mix(bl, c, C(blood))
    b.bump(tw, .3, .0006); b.bump(b.noise(40, 6, .7), .25, .0012)
    return b.finish(c, rough=.85, spec=.25)

def rubber(name, col='#d8d1bd', dirt='#3b3025', tread=True):
    b = NB(name)
    d = b.mr(b.noise(12, 6, .6), .4, .7)
    c = b.mix(d, C(col), C(dirt))
    if tread:
        sep = b.node('ShaderNodeSeparateXYZ'); b.link(b.co, sep.inputs[0])
        b.bump(b.wave(120, 'BANDS', 'Y', 'SIN'), .6, .002)
    b.bump(b.noise(80, 4, .6), .2, .0008)
    return b.finish(c, rough=.8)

def canvas(name, col='#8a8d96', dirt='#3b3025'):
    b = NB(name)
    tw = b.wave(1200, 'BANDS', 'X', 'SIN'); tw2 = b.wave(1200, 'BANDS', 'Z', 'SIN')
    c = b.mix(b.mr(b.noise(10, 6, .6), .4, .75), C(col), C(dirt))
    b.bump(b.math('MULTIPLY', tw, tw2), .3, .0005)
    return b.finish(c, rough=.85)

def gore(name):
    b = NB(name)
    n = b.noise(40, 8, .7); v = b.voronoi(80)
    c = b.ramp(n, [(.3, C('#1a0204')), (.55, C('#4a080c')), (.75, C('#8a1c1c'))])
    b.bump(n, .6, .003); b.bump(v, .3, .001)
    return b.finish(c, rough=.22, spec=.6)

def bone(name):
    b = NB(name)
    n = b.noise(30, 6, .6)
    c = b.ramp(n, [(.3, C('#b39f78')), (.6, C('#d9ccaa')), (.8, C('#ece2c8'))])
    c = b.mix(b.mr(b.noise(8, 4, .6, vec=b.mapping(loc=(3, 3, 3))), .55, .7), c, C('#6a1a16'))
    b.bump(n, .3, .001)
    return b.finish(c, rough=.5)

def teeth_m(name):
    b = NB(name)
    n = b.noise(150, 4, .6)
    c = b.ramp(n, [(.3, C('#a88f5c')), (.6, C('#d4c08c')), (.8, C('#e8dcb5'))])
    return b.finish(c, rough=.3, spec=.6)

def eye_m(name, iris='#e8d870', glow=.6):
    b = NB(name)
    c = b.ramp(b.noise(60, 4, .6), [(.3, C('#b8b8a0')), (.7, C('#dcdcc8'))])
    m = b.finish(c, rough=.05, spec=.8)
    b.bsdf.inputs['Emission Color'].default_value = (*C(iris), 1); b.bsdf.inputs['Emission Strength'].default_value = glow
    return m

def leather(name, col='#2b1d16'):
    b = NB(name)
    c = b.mix(b.mr(b.noise(20, 6, .6), .4, .7), C(col), C('#120c09'))
    b.bump(b.voronoi(200), .2, .0006); b.bump(b.noise(15, 6, .7), .2, .001)
    return b.finish(c, rough=.55)

def metal(name, col='#b9b3a2', rust='#6a3a1e'):
    b = NB(name)
    r = b.mr(b.noise(25, 6, .7), .5, .75)
    c = b.mix(r, C(col), C(rust))
    b.bump(b.noise(200, 4, .6), .1, .0004)
    m = b.finish(c, metal=1., rough=.3)
    return m

def flat(name, col, rough=.5, emit=0.):
    return L.mat_flat(name, C(col), rough=rough, emit_s=emit)

# ------------------------------------------------------------------ bake to textures
def bake(o, size=2048, outdir='.', margin=8):
    """smart-UV the object, bake base colour + normal (incl. bump) + roughness, swap in an image material."""
    import bmesh
    sc = bpy.context.scene
    src = o.active_material
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    if not o.data.uv_layers: o.data.uv_layers.new(name='UV')
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=1.15, island_margin=.004)
    bpy.ops.object.mode_set(mode='OBJECT')
    imgs = {}
    nt = src.node_tree
    for kind in ('COL', 'NRM', 'RGH'):
        im = bpy.data.images.new(f'{o.name}_{kind}', size, size, alpha=False, float_buffer=False)
        if kind != 'COL': im.colorspace_settings.name = 'Non-Color'
        tn = nt.nodes.new('ShaderNodeTexImage'); tn.image = im
        for n in nt.nodes: n.select = False
        tn.select = True; nt.nodes.active = tn
        sc.render.bake.margin = margin
        if kind == 'COL':
            sc.cycles.bake_type = 'DIFFUSE'; sc.render.bake.use_pass_direct = False; sc.render.bake.use_pass_indirect = False
            sc.render.bake.use_pass_color = True
        elif kind == 'NRM':
            sc.cycles.bake_type = 'NORMAL'; sc.render.bake.normal_space = 'TANGENT'
        else:
            sc.cycles.bake_type = 'ROUGHNESS'
        sc.cycles.samples = 1
        # metallic surfaces bake black diffuse colour: temporarily zero metallic
        bs = nt.nodes.get('Principled BSDF'); mval = bs.inputs['Metallic'].default_value if bs else 0
        if bs and kind == 'COL': bs.inputs['Metallic'].default_value = 0
        bpy.ops.object.bake(type=sc.cycles.bake_type)
        if bs: bs.inputs['Metallic'].default_value = mval
        im.filepath_raw = os.path.join(outdir, f'{o.name.replace(" ", "_")}_{kind}.png'); im.file_format = 'PNG'; im.save()
        nt.nodes.remove(tn); imgs[kind] = im
    # image material
    m = bpy.data.materials.new(src.name + '_baked'); m.use_nodes = True
    n = m.node_tree.nodes; lk = m.node_tree.links; b = n['Principled BSDF']
    tc = n.new('ShaderNodeTexImage'); tc.image = imgs['COL']; lk.new(tc.outputs[0], b.inputs['Base Color'])
    tr = n.new('ShaderNodeTexImage'); tr.image = imgs['RGH']; lk.new(tr.outputs[0], b.inputs['Roughness'])
    tn = n.new('ShaderNodeTexImage'); tn.image = imgs['NRM']; nm = n.new('ShaderNodeNormalMap')
    lk.new(tn.outputs[0], nm.inputs['Color']); lk.new(nm.outputs[0], b.inputs['Normal'])
    sb = src.node_tree.nodes['Principled BSDF']
    for k in ('Metallic', 'Emission Strength', 'Emission Color', 'Specular IOR Level'):
        b.inputs[k].default_value = sb.inputs[k].default_value
    o.data.materials.clear(); o.data.materials.append(m)
    return m

# ================================================================== stylized (comic-painted) set
def _patch(b, scale, lo, hi, loc=(0, 0, 0), detail=3, dist=.0):
    """graphic blotch mask with hard edges (constant ramp)"""
    n = b.noise(scale, detail, .55, vec=b.mapping(loc=loc), dist=dist)
    return b.mr(n, lo, hi)

def toon_skin(name, base='#8fa07a', shade='#5e7356', hi='#b9c49a', rot='#6d6a3f', bruise='#6a4a6e', vein='#3c2c4c'):
    b = NB(name)
    c = b.ramp(b.noise(3.5, 2, .5), [(0, C(shade)), (.44, C(base)), (.6, C(hi))], 'CONSTANT')
    # bruises and rot as hard-edged painted shapes, each with a darker rim
    for sc_, loc, col, lo in ((2.6, (3, 1, 7), bruise, .66), (4.0, (8, 2, 1), rot, .64)):
        n = b.noise(sc_, 3, .55, vec=b.mapping(loc=loc), dist=.4)
        core = b.mr(n, lo, lo + .005); rim = b.mr(n, lo - .03, lo - .025)
        c = b.mix(b.math('MULTIPLY', rim, .5), c, C('#2e2a2a'))
        c = b.mix(core, c, C(col))
    # bold veins, few and clear
    vn = b.noise(7, 3, .5, vec=b.mapping(loc=(2, 9, 4)), dist=.5)
    vline = b.mr(b.math('ABSOLUTE', b.math('SUBTRACT', vn, .5)), .0, .008, 1, 0)
    vm = b.mr(b.noise(3, 2, .5, vec=b.mapping(loc=(5, 1, 8))), .55, .56)
    veins = b.math('MULTIPLY', vline, vm)
    c = b.mix(veins, c, C(vein))
    # stitched scratches
    sw = b.wave(9, 'BANDS', 'Z', 'SIN', dist=3, detail=2, vec=b.mapping(rot=(.3, .5, .2)))
    sc2 = b.mr(sw, .985, .995)
    scm = b.math('MULTIPLY', sc2, b.mr(b.noise(2.5, 2, .5, vec=b.mapping(loc=(2, 2, 2))), .6, .61))
    c = b.mix(scm, c, C('#5a1418'))
    b.bump(b.math('SUBTRACT', 1, scm), .5, .0015); b.bump(veins, .4, .0015)
    b.bump(b.noise(60, 3, .5), .12, .0006)
    return b.finish(c, rough=.5, sss=.04, spec=.45)

def toon_plaid(name, a='#b03a2e', bnd='#3a1b22', line='#e8c46a', scale=12., stain='#5a3a22'):
    b = NB(name)
    vx = b.wave(scale, 'BANDS', 'X', 'SAW'); vz = b.wave(scale, 'BANDS', 'Z', 'SAW')
    bx = b.mr(vx, .5, .505); bz = b.mr(vz, .5, .505)
    tx = b.mr(vx, .84, .845); tz = b.mr(vz, .84, .845)
    c = b.mix(b.math('MAXIMUM', bx, bz), C(a), C(bnd))
    c = b.mix(b.math('MULTIPLY', bx, bz), c, C('#1a0c12'))
    c = b.mix(b.math('MAXIMUM', tx, tz), c, C(line))
    st = _patch(b, 3, .6, .605, loc=(4, 4, 2), dist=.5)
    c = b.mix(b.math('MULTIPLY', st, .7), c, C(stain))
    b.bump(b.wave(500, 'BANDS', 'X', 'SIN', vec=b.mapping(rot=(0, .785, 0))), .15, .0005)
    b.bump(b.noise(14, 3, .5, vec=b.mapping(scale=(1, 1, 5))), .45, .003)
    return b.finish(c, rough=.85, spec=.2)

def toon_denim(name, base='#3b5a8c', shade='#2a3f66', fade='#7f9cc4', mud='#4a3a26'):
    b = NB(name)
    c = b.ramp(b.noise(4, 2, .5), [(0, C(shade)), (.45, C(base)), (.62, C(fade))], 'CONSTANT')
    sep = b.node('ShaderNodeSeparateXYZ'); b.link(b.co, sep.inputs[0])
    hz = b.mr(b.math('ADD', sep.outputs['Z'], b.math('MULTIPLY', b.noise(9, 2, .5), .08)), .25, .249)
    c = b.mix(hz, c, C(mud))
    st = _patch(b, 3, .67, .675, loc=(8, 2, 0), dist=.5)
    c = b.mix(st, c, C('#5a1418'))
    b.bump(b.wave(500, 'BANDS', 'X', 'SIN', vec=b.mapping(rot=(0, .6, 0))), .2, .0005)
    b.bump(b.noise(12, 3, .5, vec=b.mapping(scale=(1, 1, 4))), .4, .003)
    return b.finish(c, rough=.8, spec=.25)

def toon_flat(name, col, shade=None, rough=.6, metal=0., scale=5., dirt=None):
    b = NB(name)
    shade = shade or tuple(int(x * .7) for x in bytes.fromhex(col[1:]))
    sh = shade if isinstance(shade, str) else '#%02x%02x%02x' % shade
    c = b.ramp(b.noise(scale, 2, .5), [(0, C(sh)), (.5, C(col))], 'CONSTANT')
    if dirt:
        c = b.mix(_patch(b, 4, .6, .605, loc=(3, 7, 1)), c, C(dirt))
    b.bump(b.noise(80, 3, .5), .1, .0005)
    return b.finish(c, rough=rough, metal=metal)
