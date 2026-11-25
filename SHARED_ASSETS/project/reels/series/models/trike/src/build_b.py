"""Stage B: weld, UV-atlas and bake weathered paint per material. usage: build_b.py -- a.blend texdir out.blend [quick]"""
import bpy, bmesh, sys, os, math
A = sys.argv[sys.argv.index('--') + 1:]; SRC, TX, OUT = A[:3]; QUICK = len(A) > 3
os.makedirs(TX, exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=SRC)
sc = bpy.context.scene; OB = bpy.data.objects
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c) + (1,)
JOBS = [  # material, new name, colour res, scheme
    ('Warm ivory ceramic-coated frame', 'Paint_Ivory_Weathered', 4096, 'ivory'),
    ('Vermilion orange satin monocoque', 'Paint_Vermilion_Weathered', 4096, 'orange'),
    ('Gunmetal structural composite', 'Composite_Gunmetal_Worn', 2048, 'gun'),
    ('Gun steel parkerized', 'Gun_Steel_Parkerized_Worn', 2048, 'gun'),
    ('Ammo can olive drab', 'Paint_AmmoCan_OD_Worn', 1024, 'od'),
]
if QUICK: JOBS = [(a, b, 512, d) for a, b, c, d in JOBS]
S = {
 'ivory':  dict(b0='#ddd5be', b1='#c4b99c', fade='#e9e3d0', grime='#5a5042', mud='#6e5c45', dust='#a8977a', streak='#8a7e68', rim='#9a7350', chip='#3c3d3a', core='#77736b', scr='#6f6b62', r0=.52),
 'orange': dict(b0='#cf4a20', b1='#b53a17', fade='#e0805a', grime='#4a2a1c', mud='#6a5641', dust='#a8977a', streak='#7c3a22', rim='#b9b3a3', chip='#4a4a46', core='#7a766e', scr='#e8c2a8', r0=.42),
 'od': dict(b0='#4f5434', b1='#43482b', fade='#666b48', grime='#23251a', mud='#5a4c3a', dust='#857760', streak='#34371f', rim='#6a6d5e', chip='#3a3b36', core='#8c8f90', scr='#8a8d80', r0=.6),
 'gun':    dict(b0='#2d3236', b1='#24282c', fade='#3b4146', grime='#141618', mud='#5a4c3a', dust='#857760', streak='#1c1f22', rim='#5e6366', chip='#6a6e70', core='#8c8f90', scr='#6b7073', r0=.5),
}
def weld(o):
    o.data = o.data.copy(); me = o.data
    bm = bmesh.new(); bm.from_mesh(me); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces); bm.to_mesh(me); bm.free()
    if me.has_custom_normals:
        with bpy.context.temp_override(object=o, active_object=o, selected_objects=[o], selected_editable_objects=[o]):
            bpy.ops.mesh.customdata_custom_splitnormals_clear()
    me.shade_smooth(); me.set_sharp_from_angle(angle=math.radians(35))
def build_tree(m, s, mode, img):
    nt = m.node_tree; N = nt.nodes; Lk = nt.links.new
    for n in list(N): N.remove(n)
    out = N.new('ShaderNodeOutputMaterial'); em = N.new('ShaderNodeEmission'); Lk(em.outputs[0], out.inputs['Surface'])
    geo = N.new('ShaderNodeNewGeometry')
    def noise(scale, detail=4, rough=.55, vec=None, dist=0.):
        t = N.new('ShaderNodeTexNoise'); t.inputs['Scale'].default_value = scale; t.inputs['Detail'].default_value = detail
        t.inputs['Roughness'].default_value = rough; t.inputs['Distortion'].default_value = dist
        Lk(vec if vec is not None else geo.outputs['Position'], t.inputs['Vector']); return t.outputs['Fac']
    def ramp(fac, a, b, ca=(0, 0, 0, 1), cb=(1, 1, 1, 1)):
        r = N.new('ShaderNodeValToRGB'); e = r.color_ramp.elements; e[0].position = a; e[1].position = b; e[0].color = ca; e[1].color = cb
        Lk(fac, r.inputs['Fac']); return r.outputs['Color']
    def math_(op, a, b=None, clamp=True):
        n = N.new('ShaderNodeMath'); n.operation = op; n.use_clamp = clamp
        for i, v in enumerate((a, b)):
            if v is None: continue
            if isinstance(v, (int, float)): n.inputs[i].default_value = v
            else: Lk(v, n.inputs[i])
        return n.outputs[0]
    def mix(fac, a, b):
        n = N.new('ShaderNodeMix'); n.data_type = 'RGBA'; n.clamp_factor = True
        if isinstance(fac, (int, float)): n.inputs['Factor'].default_value = fac
        else: Lk(fac, n.inputs['Factor'])
        for sock, v in (('A', a), ('B', b)):
            if isinstance(v, str): n.inputs[sock].default_value = lin(v)
            elif isinstance(v, tuple): n.inputs[sock].default_value = v
            else: Lk(v, n.inputs[sock])
        return n.outputs['Result']
    def bw(c):  # colour -> float
        n = N.new('ShaderNodeRGBToBW'); Lk(c, n.inputs[0]); return n.outputs[0]
    def mapv(sx, sy, sz, off=0.):
        mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (sx, sy, sz); mp.inputs['Location'].default_value = (off, off * .7, off * .3)
        Lk(geo.outputs['Position'], mp.inputs['Vector']); return mp.outputs['Vector']
    # masks
    sepz = N.new('ShaderNodeSeparateXYZ'); Lk(geo.outputs['Position'], sepz.inputs[0])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 1.05; mr.inputs['From Max'].default_value = .5; Lk(sepz.outputs['Z'], mr.inputs['Value'])
    low = mr.outputs['Result']
    nsep = N.new('ShaderNodeSeparateXYZ'); Lk(geo.outputs['Normal'], nsep.inputs[0])
    up = math_('MULTIPLY', math_('SUBTRACT', nsep.outputs['Z'], .25), 1.6)
    ao = N.new('ShaderNodeAmbientOcclusion'); ao.inputs['Distance'].default_value = .22; ao.samples = 8
    cav = math_('MULTIPLY', math_('SUBTRACT', 1., ao.outputs['AO']), 1.3)
    bev = N.new('ShaderNodeBevel'); bev.inputs['Radius'].default_value = .018; bev.samples = 6
    dp = N.new('ShaderNodeVectorMath'); dp.operation = 'DOT_PRODUCT'; Lk(bev.outputs[0], dp.inputs[0]); Lk(geo.outputs['Normal'], dp.inputs[1])
    edge = math_('MULTIPLY', math_('SUBTRACT', 1., dp.outputs['Value']), 18.)
    n_big = noise(1.3, 3); n_mid = noise(4.5, 6, .6); n_fine = noise(38, 3, .5)
    chipn = noise(7.5, 10, .72, dist=.15)
    # chips: edge driven + a few random ones
    chipf = math_('ADD', math_('MULTIPLY', edge, .55), chipn)
    chip_rim = bw(ramp(chipf, .74, .76)); chip_core = bw(ramp(chipf, .79, .81)); chip_deep = bw(ramp(chipf, .86, .87))
    # scratches: thin stretched noise lines
    scrn = noise(3., 2, .5, vec=mapv(28, 1.6, 28, 3.1), dist=.6)
    scr = bw(ramp(scrn, .495, .5)); scr2 = bw(ramp(scrn, .5, .505)); scrm = math_('MULTIPLY', math_('SUBTRACT', scr, scr2, False), -1)
    scrm = math_('MULTIPLY', math_('SUBTRACT', scr2, scr, False), 1.0)
    scrm = math_('MULTIPLY', scrm, bw(ramp(noise(2.2, 2), .5, .62)))
    # vertical grime streaks
    stn = noise(1., 3, .5, vec=mapv(14, 14, 1.1, 5.3))
    streak = math_('MULTIPLY', bw(ramp(stn, .55, .72)), .55)
    # mud from below
    mudn = noise(2.6, 8, .65, dist=.3)
    mudm = math_('MULTIPLY', low, 1.0); mud = bw(ramp(math_('ADD', math_('MULTIPLY', mudm, .7), math_('MULTIPLY', mudn, .5)), .78, .82))
    mud_dry = bw(ramp(math_('ADD', mud, math_('MULTIPLY', noise(9, 4), .5)), .95, 1.2))
    splat = bw(ramp(math_('ADD', math_('MULTIPLY', low, .3), noise(11, 6, .7, dist=.4)), .8, .81))
    dustm = math_('MULTIPLY', math_('ADD', math_('MULTIPLY', low, .6), math_('MULTIPLY', up, .35)), bw(ramp(n_mid, .3, .8)))
    if mode == 'col':
        c = mix(bw(ramp(n_big, .3, .75)), s['b0'], s['b1'])
        c = mix(math_('MULTIPLY', math_('MULTIPLY', up, bw(ramp(n_mid, .45, .7))), .55), c, s['fade'])
        c = mix(math_('MULTIPLY', n_fine, .12), c, s['b1'])
        c = mix(math_('MULTIPLY', dustm, .28), c, s['dust'])
        c = mix(streak, c, s['streak'])
        c = mix(math_('MULTIPLY', scrm, .8), c, s['scr'])
        c = mix(chip_rim, c, s['rim']); c = mix(chip_core, c, s['chip']); c = mix(chip_deep, c, s['core'])
        c = mix(math_('MULTIPLY', cav, .85), c, s['grime'])
        c = mix(math_('MAXIMUM', math_('MULTIPLY', mud, .92), math_('MULTIPLY', splat, .8)), c, s['mud'])
        c = mix(math_('MULTIPLY', mud_dry, .7), c, s['dust'])
        Lk(c, em.inputs['Color'])
    else:  # rough in G, metal in B
        r = math_('ADD', s['r0'], math_('MULTIPLY', n_fine, .12))
        r = math_('ADD', r, math_('MULTIPLY', dustm, .35)); r = math_('ADD', r, math_('MULTIPLY', mud, .5)); r = math_('ADD', r, math_('MULTIPLY', cav, .25))
        r = math_('SUBTRACT', r, math_('MULTIPLY', chip_deep, .25)); r = math_('SUBTRACT', r, math_('MULTIPLY', scrm, .15))
        met = math_('MULTIPLY', chip_deep, .85)
        cmb = N.new('ShaderNodeCombineColor'); Lk(r, cmb.inputs[1]); Lk(met, cmb.inputs[2]); Lk(cmb.outputs[0], em.inputs['Color'])
    t = N.new('ShaderNodeTexImage'); t.image = img; N.active = t; t.select = True
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.render.bake.margin = 8; sc.cycles.use_denoising = False
for mname, newname, res, scheme in JOBS:
    m = bpy.data.materials[mname]
    objs = [o for o in OB if o.type == 'MESH' and o.material_slots and o.material_slots[0].material == m]
    print(newname, len(objs), 'objs', flush=True)
    for o in objs: weld(o)
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    sc.view_layers[0].objects.active = objs[0]
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=.002, area_weight=0., correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.pack_islands(rotate=True, margin=.002)
    bpy.ops.object.mode_set(mode='OBJECT')
    s = S[scheme]
    for mode, r, smp in (('col', res, 1 if QUICK else 10), ('rm', res // 2, 1 if QUICK else 6)):
        img = bpy.data.images.new(f'{newname}_{mode}', r, r, alpha=False)
        if mode == 'rm': img.colorspace_settings.name = 'Non-Color'
        build_tree(m, s, mode, img); sc.cycles.samples = smp
        bpy.ops.object.bake(type='EMIT')
        img.filepath_raw = os.path.join(TX, f'{newname}_{mode}.png'); img.file_format = 'PNG'; img.save()
        print('baked', newname, mode, flush=True)
    # final PBR material
    nt = m.node_tree; Nn = nt.nodes
    for n in list(Nn): Nn.remove(n)
    out = Nn.new('ShaderNodeOutputMaterial'); b = Nn.new('ShaderNodeBsdfPrincipled'); nt.links.new(b.outputs[0], out.inputs[0])
    tc = Nn.new('ShaderNodeTexImage'); tc.image = bpy.data.images.load(os.path.join(TX, f'{newname}_col.png')); nt.links.new(tc.outputs['Color'], b.inputs['Base Color'])
    tr = Nn.new('ShaderNodeTexImage'); tr.image = bpy.data.images.load(os.path.join(TX, f'{newname}_rm.png')); tr.image.colorspace_settings.name = 'Non-Color'
    sp = Nn.new('ShaderNodeSeparateColor'); nt.links.new(tr.outputs['Color'], sp.inputs[0]); nt.links.new(sp.outputs['Green'], b.inputs['Roughness']); nt.links.new(sp.outputs['Blue'], b.inputs['Metallic'])
    m.name = newname
bpy.ops.wm.save_as_mainfile(filepath=OUT); print('SAVED', flush=True)
