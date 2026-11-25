def shade(lit, k=0.42, cool=(0.27, 0.25, 0.37)):
    """shadow tone for a lit colour: darker + pulled toward the violet paint shadow"""
    return tuple(l * k + c * (1 - k) * 0.75 for l, c in zip(lit, cool))


def T(name, lit, rim=None, tex=None, k=0.42, rf=0.40):
    return toon(name, shade(lit, k), lit, rim, tex, rf)


def tex_rows(spacing, dark=0.62, axis='Z'):
    """horizontal tile rows / siding boards: thin dark lines every `spacing` m along object Z"""
    def f(nt, ramp):
        N = nt.nodes; L = nt.links
        tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sp.inputs[0])
        m = N.new('ShaderNodeMath'); m.operation = 'MULTIPLY'; m.inputs[1].default_value = 1 / spacing
        L.new(sp.outputs[axis], m.inputs[0])
        fr = N.new('ShaderNodeMath'); fr.operation = 'FRACT'; L.new(m.outputs[0], fr.inputs[0])
        g = N.new('ShaderNodeMath'); g.operation = 'GREATER_THAN'; g.inputs[1].default_value = 0.80; L.new(fr.outputs[0], g.inputs[0])
        mr = N.new('ShaderNodeMapRange'); mr.inputs['To Min'].default_value = 1.0; mr.inputs['To Max'].default_value = dark
        L.new(g.outputs[0], mr.inputs['Value'])
        nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.35; L.new(tc.outputs['Object'], nz.inputs['Vector'])
        wm = N.new('ShaderNodeMapRange'); wm.inputs['From Min'].default_value = 0.35; wm.inputs['From Max'].default_value = 0.65
        wm.inputs['To Min'].default_value = 0.86; wm.inputs['To Max'].default_value = 1.06; L.new(nz.outputs['Fac'], wm.inputs['Value'])
        mm = N.new('ShaderNodeMath'); mm.operation = 'MULTIPLY'; L.new(mr.outputs[0], mm.inputs[0]); L.new(wm.outputs[0], mm.inputs[1])
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1.0
        L.new(ramp.outputs[0], mx.inputs[6]); L.new(mm.outputs[0], mx.inputs[7])
        return mx.outputs[2]
    return f


def tex_paddies(nt, ramp):
    """rice paddies: brick pattern = levees (mortar) + per-field colour variation"""
    N = nt.nodes; L = nt.links
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1 / 34, 1 / 15, 1)
    L.new(tc.outputs['Object'], mp.inputs[0])
    br = N.new('ShaderNodeTexBrick'); L.new(mp.outputs[0], br.inputs['Vector'])
    br.inputs['Color1'].default_value = (1.0, 1.0, 1.0, 1); br.inputs['Color2'].default_value = (0.78, 0.80, 0.70, 1)
    br.inputs['Mortar'].default_value = (0.55, 0.50, 0.55, 1); br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.035; br.inputs['Bias'].default_value = 0.0
    br.inputs['Brick Width'].default_value = 1.0; br.inputs['Row Height'].default_value = 1.0
    br.offset = 0.37; br.squash = 1.0
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1.0
    L.new(ramp.outputs[0], mx.inputs[6]); L.new(br.outputs['Color'], mx.inputs[7])
    return mx.outputs[2]


def tex_bands(period, c2):
    """aviation red/white bands up the tower (object Z)"""
    def f(nt, ramp):
        N = nt.nodes; L = nt.links
        tc = N.new('ShaderNodeTexCoord'); sp = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sp.inputs[0])
        m = N.new('ShaderNodeMath'); m.operation = 'MULTIPLY'; m.inputs[1].default_value = 1 / period; L.new(sp.outputs['Z'], m.inputs[0])
        fr = N.new('ShaderNodeMath'); fr.operation = 'FRACT'; L.new(m.outputs[0], fr.inputs[0])
        g = N.new('ShaderNodeMath'); g.operation = 'GREATER_THAN'; g.inputs[1].default_value = 0.5; L.new(fr.outputs[0], g.inputs[0])
        mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
        L.new(g.outputs[0], mx.inputs[0]); L.new(ramp.outputs[0], mx.inputs[6]); mx.inputs[7].default_value = (*c2, 1)
        return mx.outputs[2]
    return f


def _m(N, L, op, a, b=None, c=None):
    n = N.new('ShaderNodeMath'); n.operation = op
    for i, x in enumerate((a, b, c)):
        if x is None: continue
        if isinstance(x, (int, float)): n.inputs[i].default_value = x
        else: L.new(x, n.inputs[i])
    return n.outputs[0]


def _mul_ramp(N, L, ramp_sock, fac):
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1.0
    L.new(ramp_sock, mx.inputs[6])
    cb = N.new('ShaderNodeCombineXYZ')
    for i in range(3): L.new(fac, cb.inputs[i])
    L.new(cb.outputs[0], mx.inputs[7])
    return mx.outputs[2]


def tex_kawara(row=0.30, col=0.27, tin=False):
    """kawara roof: S-tile columns running down the slope (wavy shading + grooves), tile course lines, weathering"""
    def f(nt, ramp):
        N = nt.nodes; L = nt.links
        tc = N.new('ShaderNodeTexCoord')
        p = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], p.inputs[0])
        n = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Normal'], n.inputs[0])
        colc = _m(N, L, 'ADD', _m(N, L, 'MULTIPLY', p.outputs['X'], _m(N, L, 'ABSOLUTE', n.outputs['Y'])),
                  _m(N, L, 'MULTIPLY', p.outputs['Y'], _m(N, L, 'ABSOLUTE', n.outputs['X'])))
        wave = _m(N, L, 'MULTIPLY_ADD', _m(N, L, 'SINE', _m(N, L, 'MULTIPLY', colc, 2 * math.pi / col)), 0.10, 0.90)
        groove = _m(N, L, 'MULTIPLY_ADD', _m(N, L, 'LESS_THAN', _m(N, L, 'FRACT', _m(N, L, 'MULTIPLY', colc, 1 / col)), 0.10), -0.22, 1.0)
        course = _m(N, L, 'MULTIPLY_ADD', _m(N, L, 'GREATER_THAN', _m(N, L, 'FRACT', _m(N, L, 'MULTIPLY', p.outputs['Z'], 1 / row)), 0.84), -0.38, 1.0)
        nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.55; nz.inputs['Detail'].default_value = 4
        L.new(tc.outputs['Object'], nz.inputs['Vector'])
        weath = _m(N, L, 'MULTIPLY_ADD', nz.outputs['Fac'], 0.45, 0.76)
        fac = _m(N, L, 'MULTIPLY', _m(N, L, 'MULTIPLY', wave if not tin else 1.0, groove), _m(N, L, 'MULTIPLY', course, weath))
        return _mul_ramp(N, L, ramp.outputs[0], fac)
    return f


def tex_patchy(scale=0.06, fine=0.9, lo=0.80, hi=1.12):
    """grass / earth: big soft colour patches + fine speckle (painted look, not flat)"""
    def f(nt, ramp):
        N = nt.nodes; L = nt.links
        tc = N.new('ShaderNodeTexCoord')
        n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = scale; n1.inputs['Detail'].default_value = 3
        L.new(tc.outputs['Object'], n1.inputs['Vector'])
        cr = N.new('ShaderNodeValToRGB'); cr.color_ramp.interpolation = 'CONSTANT'
        e = cr.color_ramp.elements; e[0].position = 0; e[0].color = (lo, lo, lo, 1); e[1].position = 0.46; e[1].color = (1, 1, 1, 1)
        x = e.new(0.60); x.color = (hi, hi, hi, 1)
        L.new(n1.outputs['Fac'], cr.inputs[0])
        n2 = N.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = fine; L.new(tc.outputs['Object'], n2.inputs['Vector'])
        sp = _m(N, L, 'MULTIPLY_ADD', n2.outputs['Fac'], 0.25, 0.88)
        bw = N.new('ShaderNodeRGBToBW'); L.new(cr.outputs[0], bw.inputs[0])
        return _mul_ramp(N, L, ramp.outputs[0], _m(N, L, 'MULTIPLY', bw.outputs[0], sp))
    return f


def tex_rice(rows=0.7, stub=False):
    """paddy surface: planting rows (converge into the distance), per-field tint, soft noise"""
    def f(nt, ramp):
        N = nt.nodes; L = nt.links
        tc = N.new('ShaderNodeTexCoord'); p = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], p.inputs[0])
        r = _m(N, L, 'MULTIPLY_ADD', _m(N, L, 'GREATER_THAN', _m(N, L, 'FRACT', _m(N, L, 'MULTIPLY', p.outputs['X'], 1 / rows)), 0.70),
               -0.20 if stub else -0.12, 1.0)
        n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 0.04; L.new(tc.outputs['Object'], n1.inputs['Vector'])
        t = _m(N, L, 'MULTIPLY_ADD', n1.outputs['Fac'], 0.40, 0.80)
        return _mul_ramp(N, L, ramp.outputs[0], _m(N, L, 'MULTIPLY', r, t))
    return f


ROOF = [T('roof_kawara', (0.38, 0.40, 0.50), tex=tex_kawara()),
        T('roof_kawara2', (0.44, 0.44, 0.52), tex=tex_kawara()),
        T('roof_sekishu', (0.66, 0.33, 0.22), tex=tex_kawara()),
        T('roof_tin', (0.32, 0.45, 0.47), tex=tex_kawara(0.9, 0.45, tin=True))]


EAVE = T('eave_tile', (0.30, 0.31, 0.38))


ANT = T('antenna', (0.70, 0.70, 0.72), rim=(1.0, 0.85, 0.6), rf=0.5)


HEATER = T('heater_tank', (0.86, 0.86, 0.84))


WALLS = [T('wall_cream', (0.86, 0.80, 0.68)), T('wall_white', (0.90, 0.88, 0.84)),
         T('wall_wood', (0.42, 0.30, 0.24), tex=tex_rows(0.22, 0.75)), T('wall_grey', (0.66, 0.66, 0.66), tex=tex_rows(0.35, 0.85))]


GLASS = toon('glass', (0.10, 0.11, 0.17), (0.20, 0.22, 0.32), (1.0, 0.82, 0.55))


FRAME = T('frame', (0.62, 0.60, 0.58))


GROUND = T('ground', (0.48, 0.42, 0.36), rim=None)


ASPH = T('asphalt', (0.40, 0.38, 0.42), rim=None)


LINEW = T('roadpaint', (0.92, 0.90, 0.86), rim=None)


GRASS = T('grass', (0.52, 0.52, 0.28), tex=tex_patchy())


GRASS_D = T('grass_dry', (0.66, 0.60, 0.34), tex=tex_patchy(0.08, 1.4))


GRAVEL = T('gravel', (0.74, 0.66, 0.54), tex=tex_patchy(0.2, 3.0, 0.86, 1.08))


KERB = T('kerb', (0.74, 0.72, 0.70))


GUTTER = T('gutter', (0.56, 0.54, 0.54), tex=tex_rows(0.5, 0.45, 'Y'))


WOOD = T('rack_wood', (0.50, 0.38, 0.28))


BUNDLE = T('rice_bundles', (0.86, 0.66, 0.34), tex=tex_rows(0.22, 0.72, 'X'), rim=(1.0, 0.85, 0.55), rf=0.6)


FIELDS = [toon('paddy_gold', (0.42, 0.30, 0.36), (0.95, 0.70, 0.33), None, tex_rice()),
          toon('paddy_gold2', (0.42, 0.31, 0.34), (0.90, 0.64, 0.30), None, tex_rice()),
          toon('paddy_cut', (0.36, 0.27, 0.32), (0.74, 0.52, 0.32), None, tex_rice(0.5, True)),
          toon('paddy_late', (0.36, 0.32, 0.30), (0.80, 0.70, 0.36), None, tex_rice())]


FIELD = FIELDS[0]


LEVEE = T('levee', (0.66, 0.58, 0.34), tex=tex_patchy(0.08, 1.2), rim=(1.0, 0.86, 0.58), rf=0.55)


BALLAST = T('ballast', (0.50, 0.46, 0.46), rim=None)


RAIL = T('rail', (0.62, 0.60, 0.62))


SLEEPER = T('sleeper', (0.38, 0.32, 0.30), rim=None)


TREE = [T('tree', (0.30, 0.40, 0.22), rim=(0.95, 0.80, 0.45), rf=0.72), T('tree2', (0.24, 0.34, 0.24), rim=(0.95, 0.80, 0.45), rf=0.72),
        T('maple_tree', (0.80, 0.34, 0.14), rim=(1.0, 0.75, 0.45), rf=0.72)]


TOWER = toon('tower', shade((0.92, 0.90, 0.86)), (0.92, 0.90, 0.86), (1.0, 0.80, 0.55), tex_bands(7.0, lin((0.85, 0.22, 0.14))))


RED_ON = emis('tower_red_on', (1.0, 0.10, 0.06), 6.0)


RED_OFF = emis('tower_red_off', (0.25, 0.04, 0.04))


TRAIN = T('train_cream', (0.93, 0.86, 0.70), rim=(1.0, 0.85, 0.6), rf=0.72)


TRAINR = T('train_red', (0.78, 0.17, 0.13))


DARK = T('underframe', (0.20, 0.18, 0.22), rim=(0.8, 0.6, 0.45))


YEL = T('yellow', (0.98, 0.80, 0.16))


BLK = T('black', (0.12, 0.11, 0.13))


LAMP_ON = emis('xlamp_on', (1.0, 0.12, 0.06), 5.0)


LAMP_OFF = emis('xlamp_off', (0.22, 0.05, 0.05))


CLOTH = [toon('cloth_w', (0.80, 0.74, 0.70), (0.98, 0.96, 0.92), (1, 0.9, 0.7)), toon('cloth_b', (0.36, 0.46, 0.66), (0.55, 0.66, 0.86), (1, 0.85, 0.65)),
         toon('cloth_p', (0.80, 0.50, 0.55), (0.96, 0.70, 0.72), (1, 0.85, 0.65)), toon('cloth_y', (0.80, 0.66, 0.30), (0.98, 0.86, 0.46), (1, 0.9, 0.6))]


LEAF = toon('leaf', (0.74, 0.24, 0.07), (0.97, 0.52, 0.16), (1.0, 0.80, 0.45))


BARK = T('bark', (0.30, 0.22, 0.20))


VEND = emis('vending_face', (0.95, 0.96, 1.0), 1.6)


def obj(name, bm, mat, D, flat=True, extra=()):
    """mesh object in TOWN space; outline width scales with its distance D (about 1.5 px)"""
    ob = mesh_obj(name, bm, mat, TOWN, 0)
    for m in extra: ob.data.materials.append(m)
    if flat:
        for p in ob.data.polygons: p.use_smooth = False
    t = max(0.004, 0.00075 * D)
    nm = len(ob.data.materials)
    for _ in range(nm): ob.data.materials.append(ink)
    sm = ob.modifiers.new('ol', 'SOLIDIFY'); sm.thickness = t; sm.offset = 1; sm.use_flip_normals = True
    sm.material_offset = nm; sm.use_rim = False
    return ob


def box(bm, c, s, mi=0, rotz=0.0):
    r = bmesh.ops.create_cube(bm, size=1)
    vs = r['verts']
    bmesh.ops.scale(bm, vec=s, verts=vs)
    if rotz: bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=Matrix.Rotation(rotz, 3, 'Z'))
    bmesh.ops.translate(bm, vec=c, verts=vs)
    for f in {f for v in vs for f in v.link_faces}: f.material_index = mi
    return vs


def beam(bm, p, q, t, mi=0):
    p, q = Vector(p), Vector(q); d = q - p; L = d.length
    r = bmesh.ops.create_cube(bm, size=1); vs = r['verts']
    bmesh.ops.scale(bm, vec=(t, t, L), verts=vs)
    rot = d.normalized().to_track_quat('Z', 'Y').to_matrix()
    bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=rot)
    bmesh.ops.translate(bm, vec=(p + q) / 2, verts=vs)
    for f in {f for v in vs for f in v.link_faces}: f.material_index = mi


def house(cx, cy, w, d, h, roofmat, wallmat, kind, D, balcony=False, r=None):
    r = r or rnd
    bm = bmesh.new()
    box(bm, (0, 0, h / 2), (w, d, h), 0)
    # windows on all four sides: dark glass with a light frame, sliding-door style (two panes)
    floors = 2 if h > 4.5 else 1
    for fl_ in range(floors):
        z = 1.5 + fl_ * 2.8
        for side in (-1, 1):
            n = max(1, int(w / 3.2))
            for i in range(n):
                x = -w / 2 + (i + 0.5) * w / n + r.uniform(-0.3, 0.3)
                if r.random() < 0.25: continue
                ww = r.choice((1.2, 1.6, 0.8))
                box(bm, (x, side * (d / 2 + 0.03), z), (ww + 0.16, 0.05, 1.26), 3)
                box(bm, (x, side * (d / 2 + 0.06), z), (ww, 0.05, 1.1), 2)
                box(bm, (x, side * (d / 2 + 0.085), z), (0.06, 0.02, 1.1), 3)
                if r.random() < 0.5:                         # rain shutter box above some windows
                    box(bm, (x - ww / 2 - 0.25, side * (d / 2 + 0.08), z), (0.35, 0.15, 1.2), 0)
        for side in (-1, 1):
            if r.random() < 0.6:
                box(bm, (side * (w / 2 + 0.03), r.uniform(-d / 4, d / 4), z), (0.05, 1.0, 1.1), 2)
    if floors == 2:                                              # little eave between floors
        box(bm, (0, 0, 2.9), (w + 0.7, d + 0.7, 0.10), 1)
    if balcony:
        box(bm, (0, -d / 2 - 0.55, 2.95), (w * 0.6, 1.1, 0.12), 3)
        box(bm, (0, -d / 2 - 1.07, 3.45), (w * 0.6, 0.05, 0.9), 3)
    # roof
    o = 0.55; rh = 1.6 + 0.12 * w
    x0, x1, y0, y1 = -w / 2 - o, w / 2 + o, -d / 2 - o, d / 2 + o
    zt = h + 0.05
    if kind == 'hip':
        ins = min(w, d) / 2 + o
        a, b, c, e = (bm.verts.new((x0, y0, zt)), bm.verts.new((x1, y0, zt)), bm.verts.new((x1, y1, zt)), bm.verts.new((x0, y1, zt)))
        if w >= d:
            r0, r1 = bm.verts.new((x0 + ins, 0, zt + rh)), bm.verts.new((x1 - ins, 0, zt + rh))
            fs = [(a, b, r1, r0), (c, e, r0, r1), (b, c, r1), (e, a, r0)]
        else:
            r0, r1 = bm.verts.new((0, y0 + ins, zt + rh)), bm.verts.new((0, y1 - ins, zt + rh))
            fs = [(b, c, r1, r0), (e, a, r0, r1), (c, e, r1), (a, b, r0)]
        for fv in fs: bm.faces.new(fv).material_index = 1
        beam(bm, r0.co, r1.co, 0.28, 1)
        RA, RB = r0.co.copy(), r1.co.copy()
    else:   # gable: ridge along the long axis
        if w >= d:
            ra, rb = bm.verts.new((x0, 0, zt + rh)), bm.verts.new((x1, 0, zt + rh))
            q = [bm.verts.new(v) for v in ((x0, y0, zt), (x1, y0, zt), (x1, y1, zt), (x0, y1, zt))]
            bm.faces.new((q[0], q[1], rb, ra)).material_index = 1; bm.faces.new((q[2], q[3], ra, rb)).material_index = 1
            for sx in (-1, 1):
                g = [bm.verts.new((sx * w / 2, -d / 2, h)), bm.verts.new((sx * w / 2, d / 2, h)), bm.verts.new((sx * w / 2, 0, zt + rh - 0.1))]
                bm.faces.new(g).material_index = 0
        else:
            ra, rb = bm.verts.new((0, y0, zt + rh)), bm.verts.new((0, y1, zt + rh))
            q = [bm.verts.new(v) for v in ((x0, y0, zt), (x1, y0, zt), (x1, y1, zt), (x0, y1, zt))]
            bm.faces.new((q[1], q[2], rb, ra)).material_index = 1; bm.faces.new((q[3], q[0], ra, rb)).material_index = 1
            for sy in (-1, 1):
                g = [bm.verts.new((-w / 2, sy * d / 2, h)), bm.verts.new((w / 2, sy * d / 2, h)), bm.verts.new((0, sy * d / 2, zt + rh - 0.1))]
                bm.faces.new(g).material_index = 0
        beam(bm, ra.co, rb.co, 0.26, 1)
        RA, RB = ra.co.copy(), rb.co.copy()
    # eave tile edge (round tile ends) all round + ridge end tiles (onigawara) + ridge cap
    for (pa, pb) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        if kind != 'hip' and ((w >= d and pa[0] == pb[0]) or (w < d and pa[1] == pb[1])): continue
        beam(bm, (pa[0], pa[1], zt + 0.02), (pb[0], pb[1], zt + 0.02), 0.17, 4)
    for e_ in (RA, RB):
        box(bm, (e_.x, e_.y, e_.z + 0.22), (0.42, 0.42, 0.5), 4)
    beam(bm, RA + Vector((0, 0, 0.17)), RB + Vector((0, 0, 0.17)), 0.20, 4)
    if kind != 'hip':                                            # gable barge boards
        for e_, sgn in ((RA, -1), (RB, 1)):
            for side in (-1, 1):
                if w >= d: q0 = Vector((e_.x, side * (d / 2 + o), zt))
                else: q0 = Vector((side * (w / 2 + o), e_.y, zt))
                beam(bm, q0, e_, 0.12, 3)
    # TV antenna (Yagi) on about half the roofs, solar water heater on some
    if rnd2.random() < 0.55 and cy > 22:          # none on the front row: it would stand in front of the laundry
        mc = (RA + RB) / 2 + Vector((rnd2.uniform(-1, 1), 0, 0.2))
        top = mc + Vector((0, 0, rnd2.uniform(1.8, 2.8)))
        beam(bm, mc, top, 0.05, 5)
        yaw = rnd2.uniform(-0.4, 0.4); dvec = Vector((math.sin(yaw), math.cos(yaw), 0))
        beam(bm, top - dvec * 0.9, top + dvec * 0.9, 0.04, 5)
        for j in range(7):
            q = top - dvec * 0.85 + dvec * (j * 0.28); pv = Vector((dvec.y, -dvec.x, 0)) * (0.42 - j * 0.03)
            beam(bm, q - pv, q + pv, 0.022, 5)
        beam(bm, mc, mc + Vector((0.9, -0.6, -1.0)), 0.015, 5)   # guy wire
    if w >= d and rnd2.random() < 0.22:
        ang = math.atan2(rh, abs(y0))
        vs = box(bm, (0, 0, 0), (2.2, 1.3, 0.10), 2)
        bmesh.ops.rotate(bm, verts=vs, cent=(0, 0, 0), matrix=Matrix.Rotation(-ang, 3, 'X'))
        hx = rnd2.uniform(-w / 4, w / 4)
        bmesh.ops.translate(bm, vec=(hx, y0 * 0.45, zt + rh * 0.55 + 0.25), verts=vs)
        beam(bm, (hx - 1.1, y0 * 0.22, zt + rh * 0.78 + 0.35), (hx + 1.1, y0 * 0.22, zt + rh * 0.78 + 0.35), 0.38, 6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    ob = obj('house', bm, wallmat, D, extra=(roofmat, GLASS, FRAME, EAVE, ANT, HEATER))
    ob.location = (cx, cy, 0)
    ob.rotation_euler = (0, 0, math.radians(r.uniform(-2, 2)))
    return ob


def upole(x, y, z0, hgt, D):
    bm = lathe([(0, 0.17), (hgt, 0.12), (hgt + 0.02, 0)], 16)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
    for k, zz in enumerate((hgt - 0.5, hgt - 1.4)):
        box(bm, (0, 0, zz), (1.8, 0.12, 0.12), 0)
    box(bm, (0.32, 0, hgt - 2.6), (0.45, 0.45, 0.8), 0)        # transformer
    ob = obj('upole', bm, CONC, D, flat=False); ob.location = (x, y, z0)
    return ob


def wire(a, b, sag, thick):
    c = bpy.data.curves.new('wire', 'CURVE'); c.dimensions = '3D'; c.bevel_depth = thick
    sp = c.splines.new('POLY'); n = 40; sp.points.add(n - 1)
    a, b = Vector(a), Vector(b)
    for k in range(n):
        t = k / (n - 1); q = a.lerp(b, t); q.z -= sag * 4 * t * (1 - t)
        sp.points[k].co = (*q, 1)
    co = bpy.data.objects.new('wire', c); sc.collection.objects.link(co); c.materials.append(WIRE); co.parent = TOWN
    return co


