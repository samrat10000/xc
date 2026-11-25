p='rider.py';s=open(p).read()
def rep(a,b):
    global s; assert s.count(a)==1,a; s=s.replace(a,b)
rep("'rider': dict(mix={'universal-female-young-averagemuscle-averageweight': 1.0},",
 "'rider': dict(mix={'universal-female-young-averagemuscle-averageweight': .45, 'universal-female-young-averagemuscle-minweight': .55, 'female-young-averagemuscle-averageweight-idealproportions': .8, 'mouth-upperlip-volume-incr': .6, 'mouth-lowerlip-volume-incr': .7, 'nose-scale-horiz-decr': .35, 'nose-width1-decr': .3, 'chin-width-decr': .4, 'l-cheek-bones-incr': .5, 'r-cheek-bones-incr': .5, 'head-fat-decr': .35, 'neck-scale-horiz-decr': .3, 'torso-vshape-decr': .25},")
rep("(sp.outputs['Green'], '#5a3a34', .45), (sp.outputs['Blue'], '#b0564a', .35)",
    "(sp.outputs['Green'], '#2a1a1c' if RIDER else '#5a3a34', .7 if RIDER else .45), (sp.outputs['Blue'], '#a8343c' if RIDER else '#b0564a', .5 if RIDER else .35)")
rep("jacket = z.garment('jacket', ARMS, keep=jk_keep, push=.014,","jacket = z.garment('jacket', ARMS, keep=jk_keep, push=.02 if RIDER else .014,")
# lashes after brows
rep("brows = L.join(brows, f'{CH} brows'); z.bind(brows, 'head')","""brows = L.join(brows, f'{CH} brows'); z.bind(brows, 'head')
if RIDER:
    lash = []
    for e in (EL, ER):
        sx = 1 if e.x > 0 else -1
        for k in range(16):
            t = k / 15
            q = V(e.x + sx * (-.013 + .027 * t), -.5, e.z + .0035 + .0045 * math.sin(t * math.pi))
            h, n = z.hit(b, q, (0, 1, 0))
            if h is None: continue
            ln = .006 + .004 * t
            lash.append(L.tube(f'{CH} lash', [h + V(0, -.001, 0), h + V(sx * .002 * t, -.005, .002), h + V(sx * .004 * t, -.006, .002 + ln * .6)], [.00045, .0003, .00012], C, sides=3, cap=False))
    lashes = L.join(lash, f'{CH} lashes'); z.bind(lashes, 'head')""")
rep("    L.setmat(collar, M.canvas(f'{CH}_Bandana', '#7a221c'))","""    L.setmat(collar, M.canvas(f'{CH}_Bandana', '#7a221c'))
    def leather_real(name, col, dark, light):
        nb = M.NB(name)
        big = nb.noise(5, 6, .6); wr = nb.noise(28, 8, .72, vec=nb.mapping(scale=(1, 1, 3.5)))
        c = nb.mix(nb.mr(big, .3, .72), M.C(col), M.C(dark))
        geo = nb.node('ShaderNodeNewGeometry')
        wear = nb.math('MULTIPLY', nb.mr(geo.outputs['Pointiness'], .5, .56), nb.mr(nb.noise(60, 4, .6), .4, .6))
        c = nb.mix(wear, c, M.C(light))
        c = nb.mix(nb.math('MULTIPLY', nb.mr(nb.noise(9, 5, .6, vec=nb.mapping(loc=(7, 2, 1))), .58, .72), .55), c, M.C('#2a2018'))   # road dirt
        nb.bump(nb.voronoi(1100), .22, .00025); nb.bump(wr, .35, .0012)
        m = nb.finish(c, rough_sock=nb.mr(big, 0, 1, .32, .62), spec=.5)
        nb.bsdf.inputs['Coat Weight'].default_value = .12; nb.bsdf.inputs['Coat Roughness'].default_value = .35
        return m
    L.setmat(jacket, leather_real(f'{CH}_JacketR', '#86552e', '#4a2c18', '#b88a5e'))
    L.setmat(shafts, leather_real(f'{CH}_BootR', '#8a5a30', '#4a2e18', '#c09468'))
    for up, so_, lc in shoes: L.setmat(up, shafts.data.materials[0])
    L.setmat(pants, leather_real(f'{CH}_ShortsR', '#161618', '#0a0a0b', '#3a3a3e'))
    L.setmat(lashes, M.flat(f'{CH}_Lash', '#141012', .5))
    L.setmat(brows, M.flat(f'{CH}_Brow', '#4a4038', .6))""")
rep("for o in [b, tee, jacket, pants, belt, collar, weapon, cap] + [s for sh in shoes for s in sh[:2]] + ([shafts, gloves, kp, goggles, headset, bando, hol] if RIDER else []):\n    L.hull(o, C, t=.0032)",
"""for o in ([] if RIDER else [b, tee, jacket, pants, belt, collar, weapon, cap] + [s for sh in shoes for s in sh[:2]]):
    L.hull(o, C, t=.0032)
if RIDER:   # real strand hair for renders (cards stay for the GLB)
    from mathutils.bvhtree import BVHTree
    dg = bpy.context.evaluated_depsgraph_get()
    bvh = BVHTree.FromObject(b, dg)
    hair.hide_render = True
    cm = cap.matrix_world; cv = [cm @ v.co for v in cap.data.vertices]
    hc = sum(cv, Vector()) / len(cv); top = max(v.z for v in cv)
    eyez = (sum((o.matrix_world @ v.co for o in (z.parts['eyeL'], z.parts['eyeR']) for v in o.data.vertices), Vector()) / (len(z.parts['eyeL'].data.vertices) * 2))
    rng2 = random.Random(5); K = 10; pos = []; rad = []
    polys = cap.data.polygons; NPER = 6
    for pl in polys:
        n = (cm.to_3x3() @ pl.normal).normalized()
        if n.z < -.3: continue
        vs = [cv[i] for i in pl.vertices]
        for _ in range(NPER):
            w = [rng2.random() for _ in vs]; sw = sum(w); r0 = sum((vv * (wi / sw) for vv, wi in zip(vs, w)), Vector())
            front = (r0 - hc).y < -.035 and r0.z > eyez.z + .05
            nv = noise.noise_vector(r0 * 25)
            chop = .5 + .5 * noise.noise(r0 * 18)
            if front:
                ln = .06 + .03 * chop; d = (n * .4 + V(0, -.5, -1)).normalized()
            else:
                tipz = eyez.z - .085 + .035 * chop - .02 * max(0, (r0 - hc).y) * 10
                ln = max(.03, r0.z - tipz + .03); d = (n * 1.0 + V(0, .05, -.3)).normalized()
            d = (d + nv * .25).normalized()
            q = r0 + n * .002; seg = ln / (K - 1)
            for k in range(K):
                if k:
                    d = (d + V(0, 0, -.55) + nv * .08).normalized(); q = q + d * seg
                    loc, nn, _, dist = bvh.find_nearest(q)
                    if loc is not None and dist < .03:
                        q = loc + nn * .03
                pos += [q.x, q.y, q.z]; rad.append(.00011 * (1 - k / K) + .00002)
    NC = len(pos) // (3 * K)
    hcv = bpy.data.hair_curves.new(f'{CH} strands'); hcv.add_curves([K] * NC)
    hcv.attributes['position'].data.foreach_set('vector', pos)
    ra = hcv.attributes.get('radius') or hcv.attributes.new('radius', 'FLOAT', 'POINT'); ra.data.foreach_set('value', rad)
    ho = bpy.data.objects.new(f'{CH} strands', hcv); C.objects.link(ho)
    hm2 = bpy.data.materials.new(f'{CH}_HairStrand'); hm2.use_nodes = True; nt2 = hm2.node_tree
    for nn_ in list(nt2.nodes):
        if nn_.type == 'BSDF_PRINCIPLED': nt2.nodes.remove(nn_)
    hb_ = nt2.nodes.new('ShaderNodeBsdfHairPrincipled'); hb_.parametrization = 'MELANIN'
    hb_.inputs['Melanin'].default_value = .12; hb_.inputs['Melanin Redness'].default_value = .25
    hb_.inputs['Roughness'].default_value = .28; hb_.inputs['Radial Roughness'].default_value = .35
    if 'Random Roughness' in hb_.inputs: hb_.inputs['Random Roughness'].default_value = .3
    if 'Random Color' in hb_.inputs: hb_.inputs['Random Color'].default_value = .15
    nt2.links.new(hb_.outputs[0], nt2.nodes['Material Output'].inputs['Surface'])
    hcv.materials.append(hm2)
    L.setmat(cap, M.flat(f'{CH}_Scalp', '#9a9288', .8))
    print('strands', NC, flush=True)""")
rep("L.studio(sc); sc.view_settings.exposure = -.2","""L.studio(sc); sc.view_settings.exposure = -.2
if RIDER:
    try:
        sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception as ex: print('look', ex)
    for o in sc.objects:
        if o.type == 'LIGHT':
            if o.name == 'key': o.location = (-1.9, -2.5, 2.6); o.data.energy = 260; o.data.size = 1.1; o.data.color = (1, .9, .78)
            if o.name == 'rim': o.location = (1.9, 1.9, 2.3); o.data.energy = 380; o.data.size = .7; o.data.color = (.7, .82, 1)
            if o.name == 'fill': o.data.energy = 28
    R2 = bpy.data.lights.new('rim2', 'AREA'); R2.energy = 260; R2.size = .6; R2.color = (1, .75, .5)
    r2 = bpy.data.objects.new('rim2', R2); sc.collection.objects.link(r2); r2.location = (-1.8, 1.9, 2.0)
    r2.rotation_euler = (Vector((0, 0, 1.2)) - r2.location).to_track_quat('-Z', 'Y').to_euler()""")
rep("    if n.type == 'BACKGROUND' and n.inputs['Color'].default_value[0] > .5: n.inputs['Color'].default_value = (*L.lin('#30303a'), 1)",
    "    if n.type == 'BACKGROUND' and n.inputs['Color'].default_value[0] > .5: n.inputs['Color'].default_value = (*L.lin('#1a1b21' if RIDER else '#30303a'), 1)")
rep("shots = [('front34', 28, 6, 3.4, .92, 50), ('side', 90, 4, 3.4, .92, 50), ('back34', 205, 10, 3.4, .92, 50), ('face', 20, 2, .6, None, 70)]",
    "shots = [('front34', 28, 6, 3.4, .92, 50), ('side', 90, 4, 3.4, .92, 50), ('back34', 205, 10, 3.4, .92, 50), ('face', 20, 2, .6, None, 70)]\nif RIDER: shots = [('front34', 24, 6, 2.55, .9, 50), ('side', 90, 4, 2.55, .9, 50), ('back34', 205, 10, 2.55, .9, 50), ('face', 22, 3, .62, None, 85)]")
rep("    L.camera(sc, tgt, dist, az, el, lens=lens)","""    camo = L.camera(sc, tgt, dist, az, el, lens=lens)
    if RIDER and nm == 'face': camo.data.dof.use_dof = True; camo.data.dof.focus_distance = dist; camo.data.dof.aperture_fstop = 2.2""")
open(p,'w').write(s)
