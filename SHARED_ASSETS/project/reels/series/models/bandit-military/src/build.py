"""Military upgrade of the Bandit armored buggy. usage: python3 build.py -- raw.glb texdir skull.npz out.blend"""
import bpy, bmesh, sys, os, math, random
import numpy as np
from mathutils import Vector as V, Matrix, Euler
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
from npzmesh import npz_mesh
A = sys.argv[sys.argv.index('--') + 1:]
SRC, TX, SKULL, OUT = A[:4]
T = lambda n: os.path.join(TX, n)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=SRC)
sc = bpy.context.scene
OB = bpy.data.objects
ROOT = OB['BANDIT • Armored reconnaissance buggy']
G = {o.name[:2]: o for o in OB if '•' in o.name and o is not ROOT}
def grp(name):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e)
    e.parent = ROOT; e.matrix_parent_inverse = ROOT.matrix_world.inverted(); return e
def kill(o):
    for c in list(o.children_recursive): bpy.data.objects.remove(c, do_unlink=True)
    bpy.data.objects.remove(o, do_unlink=True)
def wbb(o):
    ws = [o.matrix_world @ V(c) for c in o.bound_box]
    return V([min(w[i] for w in ws) for i in range(3)]), V([max(w[i] for w in ws) for i in range(3)])
def meshes(prefix):
    return [o for o in OB if o.type == 'MESH' and o.name.split('.')[0] == prefix]
rnd = random.Random(7)

# ------------------------------------------------------------------ 1. remove what gets rebuilt
kill(G['07'])                                                        # rally wing -> cargo rack
for o in list(OB):
    if o.type != 'MESH': continue
    b = o.name.split('.')[0]
    if b in ('Painted vector graphic on Rear wing main aerofoil', 'Weathered cow skull with true orbital and nasal cavities',
             'Left swept tapered cattle horn', 'Right swept tapered cattle horn', 'Slender premaxillary bone tip',
             'Subtle cattle cranial suture', 'Thin bovine nasal septum', 'Floor anti-slip embossed chevron',
             'Decorative fictional feed link', 'Prop side ammunition style box', 'Prop feed box lid', 'Prop feed box ZC marking',
             'Prop feed box panel fastener hex head', 'Prop feed box panel fastener socket recess',
             'Shaped off-road tire carcass', 'Individual staggered tread block', 'Tire shoulder traction lug',
             'Swept three-blade wheel spoke', 'Spoke machined raised edge', 'Rim forged beadlock lip', 'Beadlock ring bolt hex head',
             'Beadlock ring bolt socket recess', 'Wheel lug nut hex head', 'Wheel lug nut socket recess', 'Hexagonal forged center hub',
             'Hub cap inset', 'Acid lime beadlock paint inlay', 'Inner rim barrel'):
        bpy.data.objects.remove(o, do_unlink=True)
for o in meshes('Exposed suspension helical spring'):            # 144k tris each -> lighter
    d = o.modifiers.new('dec', 'DECIMATE'); d.ratio = .1
print('cleanup done', flush=True)

# ------------------------------------------------------------------ 2. paint scheme
def img_node(m, key=None):
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image and (key is None or key in n.image.name): return n
def set_base_image(mname, path, uvscale=None, key='aged color', metal=None, rough=None):
    m = bpy.data.materials[mname]; nt = m.node_tree; n = img_node(m, key)
    n.image = bpy.data.images.load(path)
    if uvscale:
        mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (uvscale, uvscale, 1)
        uv = nt.nodes.new('ShaderNodeUVMap'); nt.links.new(uv.outputs[0], mp.inputs[0]); nt.links.new(mp.outputs[0], n.inputs[0])
    b = nt.nodes['Principled BSDF']
    if metal is not None:
        b.inputs['Metallic'].default_value = metal
    if rough is not None:
        b.inputs['Roughness'].default_value = rough
set_base_image('Weathered graphite armor', T('camo.png'), uvscale=.25)
set_base_image('Raised ash gray panels', T('olive_panels.png'))
set_base_image('Dark forged tubular chassis', T('chassis.png'))
for k, f in (('zombie-crawler-hood', 'decal_hood.png'), ('zombie-crawler-livery', 'decal_door.png'), ('zombie-crawler-rocker', 'decal_rocker.png')):
    for m in bpy.data.materials:
        if m.use_nodes:
            n = img_node(m, k)
            if n: n.image = bpy.data.images.load(T(f))
def recol(mname, hexc, rough=None, metal=None):
    m = bpy.data.materials.get(mname)
    if not m: return
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*lin(hexc), 1)
    if rough is not None: b.inputs['Roughness'].default_value = rough
    if metal is not None: b.inputs['Metallic'].default_value = metal
recol('Acid lime signal paint', '#b8ad86', .8, 0)
recol('Burnt orange harness webbing', '#4c5131', .9, 0)
recol('Bucket seat woven fabric', '#33372a', .95)
recol('Warm bone stencil ink', '#cfc7aa', .8)
recol('Exposed machined edges', '#6e6c62', .45, .85)
recol('Fictional prop feed-link bronze', '#6a5530', .4, .9)
recol('Cockpit charcoal composite', '#1d1f1a', .7)
print('paint done', flush=True)

# shared materials
M_RIM = pbr('Rim olive drab steel', '#3d4230', .62, .25)
M_BOLT = pbr('Zinc dark hardware', '#5c5d55', .42, .85)
M_RUB = vcmat('Military tyre rubber', .9)
M_BRASS = pbr('Cartridge brass', '#b48a3c', .28, 1.)
M_TIP = pbr('Bullet copper jacket', '#8a4a2a', .3, 1.)
M_BTIP = pbr('Black tip AP paint', '#1a1a18', .5, .3)
M_LINK = pbr('Belt link steel', '#3c3d38', .4, .9)
M_CAN = imgmat('Ammo can stencil', T('ammo_can.png'), .6, .2)
M_OD = pbr('Olive drab enamel', '#3e432f', .6, .15)
M_TAN = pbr('Desert tan enamel', '#8a7a58', .65, .1)
M_STEEL = pbr('Worn bare steel', '#77766d', .38, .9)
M_PERF = imgmat('Perforated steel mesh plate', T('perf_mesh.png'), .5, .7, alpha=True, clip=True)
M_TREAD = imgmat('Diamond tread plate', T('tread_col.png'), .5, .8, nrm=T('tread_nrm.png'), rm=T('tread_rm.png'))
M_BLACK = pbr('Black rubber hose', '#151513', .8)
M_WEB = pbr('Olive cargo strap', '#55583a', .9)
M_TARP = pbr('Canvas tarp', '#5b5a40', .95)
M_RAG = pbr('Rotten rag', '#3a1c16', .95)
M_RED = pbr('Fire extinguisher red', '#8c1a14', .45, .1)
M_WIRE = pbr('Rusted barbed wire', '#5d4331', .6, .8)
M_JW = imgmat('Jerry can water stencil', T('jerry_water.png'), .6, .15)
for m in (M_PERF,):
    m.use_backface_culling = False

# ------------------------------------------------------------------ 3. wheels: military tyres + steel beadlock rims + CTIS
PROF = [(.355, .17), (.39, .198), (.45, .212), (.497, .207), (.52, .19), (.528, .16), (.531, .08), (.532, 0.)]
PROF = PROF + [(r, -a) for r, a in reversed(PROF[:-1])]
pr_a = np.array([a for r, a in PROF[7:]]); pr_r = np.array([r for r, a in PROF[7:]])
def r_at(u):
    u = abs(u); i = np.argsort(np.abs(pr_a))
    return float(np.interp(u, np.abs(pr_a)[i], pr_r[i]))
def tyre_bm(seed=0):
    bm = bmesh.new()
    revolve(bm, PROF, segs=144, axis='Y')
    N = 18; R = .53
    def lug(phi0, u0, u1, w0, w1, h):
        st = 9; rings = []
        for i in range(st):
            t = i / (st - 1); u = u0 + (u1 - u0) * t
            phi = phi0 + math.tan(math.radians(38)) * (u - u0) * (1 if u1 > u0 else -1) / R
            w = (w0 + (w1 - w0) * t) / R
            rb = r_at(u) - .006; hh = h * (1 - .3 * max(0, (abs(u) - .17) / .05))
            ring = []
            for (dp, rr) in ((-w, rb), (w, rb), (w * .82, rb + hh), (-w * .82, rb + hh)):
                ring.append(bm.verts.new(V((rr * math.sin(phi + dp), u, rr * math.cos(phi + dp)))))
            rings.append(ring)
        for i in range(st - 1):
            a, b = rings[i], rings[i + 1]
            for k in range(4):
                bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
        bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    for k in range(N):
        p = 2 * math.pi * k / N
        lug(p, -.214, .035, .03, .022, .034)
        lug(p + math.pi / N, .214, -.035, .03, .022, .034)
        # small sidewall shoulder blocks between lugs (both sides)
        for s in (-1, 1):
            lug(p + math.pi / N * (.5 if s < 0 else 1.5), .2 * s, .214 * s, .014, .012, .02)
    return bm
def sidewall_text(bm, txt, Rt, phi0, size=.034, side=1):
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = txt; cu.size = size; cu.extrude = .0018; cu.align_x = 'CENTER'
    cu.font = bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    to = bpy.data.objects.new('t', cu); sc.collection.objects.link(to)
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(to.evaluated_get(dg))
    bpy.data.objects.remove(to); tb = bmesh.new(); tb.from_mesh(me); bpy.data.meshes.remove(me)
    for v in tb.verts:
        x, y, z = v.co; phi = phi0 - x / Rt; r = Rt + y
        ax = float(np.interp(r, [.355, .39, .45, .497, .52], [.17, .198, .212, .207, .19])) + .0005 + z
        v.co = V((r * math.sin(phi), ax, r * math.cos(phi)))
    me = bpy.data.meshes.new('_t'); tb.to_mesh(me); tb.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
def rim_bm():
    bm = bmesh.new()
    revolve(bm, [(.348, -.19), (.348, .175), (.372, .186), (.372, .198), (.34, .198), (.338, .18), (.338, -.19)], 64, closed=True)
    revolve(bm, [(.262, .197), (.372, .197), (.375, .207), (.37, .214), (.262, .214), (.258, .207)], 64, closed=True)   # beadlock ring
    for k in range(24):
        t = 2 * math.pi * (k + .5) / 24; c = V((.318 * math.sin(t), .214, .318 * math.cos(t))); hexbolt(bm, c, (0, 1, 0), .0105, .009)
    return bm
def disc_obj(name, xf, parent):
    HC = [(.205 * math.sin(2 * math.pi * k / 6), .205 * math.cos(2 * math.pi * k / 6)) for k in range(6)]
    HR = .043
    bm = bmesh.new(); NR, NS = 30, 192
    rs = np.linspace(.112, .345, NR); grid = []
    for i, r in enumerate(rs):
        row = []
        for j in range(NS):
            t = 2 * math.pi * j / NS; row.append(bm.verts.new(V((r * math.sin(t), 0, r * math.cos(t)))))
        grid.append(row)
    for i in range(NR - 1):
        for j in range(NS):
            q = (grid[i][j], grid[i][(j + 1) % NS], grid[i + 1][(j + 1) % NS], grid[i + 1][j])
            c = sum((v.co for v in q), V()) / 4
            if min(math.hypot(c.x - hx, c.z - hz) for hx, hz in HC) < HR: continue
            bm.faces.new(q)
    for v in list(bm.verts):
        if not v.link_faces: bm.verts.remove(v); continue
        d, (hx, hz) = min((math.hypot(v.co.x - hx, v.co.z - hz), (hx, hz)) for hx, hz in HC)
        if v.is_boundary and d < HR + .02:
            f = HR / max(d, 1e-6); v.co.x = hx + (v.co.x - hx) * f; v.co.z = hz + (v.co.z - hz) * f
    for v in bm.verts:
        r = math.hypot(v.co.x, v.co.z); v.co.y = float(np.interp(r, [.112, .2, .265, .345], [.124, .141, .184, .194]))
    ext = bmesh.ops.extrude_face_region(bm, geom=list(bm.faces))
    for g in ext['geom']:
        if isinstance(g, bmesh.types.BMVert): g.co.y -= .006
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return obj(name, bm, M_RIM, parent, xform=xf, sharp=50)
def hub_bm():
    bm = bmesh.new()
    revolve(bm, [(.0, .118), (.112, .118), (.112, .15), (.088, .158), (.086, .2), (.066, .208), (.05, .232), (.03, .24), (.0, .242)], 40)
    for k in range(8):
        t = 2 * math.pi * k / 8; hexbolt(bm, V((.099 * math.sin(t), .15, .099 * math.cos(t))), (0, 1, 0), .0105, .014)
    # CTIS: rotary seal on the cap, valve block on the bead ring, hose between
    cyl(bm, V((0, .25, 0)), (0, 1, 0), .022, .018, 16)
    box(bm, V((0, .262, 0)), (.026, .012, .03), bev=.003)
    return bm
def ctis_hose_bm():
    bm = bmesh.new()
    pts = [V((0, .262, .02)), V((0, .25, .07)), V((.025, .226, .15)), V((.06, .215, .23)), V((.09, .217, .29))]
    tube(bm, pts, .0065, 8)
    box(bm, V((.095, .222, .30)), (.03, .02, .03), bev=.004)                  # valve on bead ring
    cyl(bm, V((.095, .236, .30)), (0, 1, 0), .006, .012, 8)
    return bm
def tyre_colour(o):
    def f(co, nr):
        c = co - co.mean(0)
        rr = np.sqrt(c[:, 0] ** 2 + c[:, 2] ** 2); ax = np.abs(c[:, 1])
        base = np.tile(L('#1f1e1b'), (len(co), 1))
        n1 = fbm(co, 26, 3, 2.); n2 = fbm(co, 60, 2, 5.)
        groove = (rr < .545) & (ax < .2)                              # carcass crown between lugs
        mud = np.clip((n1 - .35) * 3.5, 0, 1) * (.55 + .45 * groove) + groove * .35 * np.clip(n2 * 2 - .4, 0, 1)
        side = (ax > .195)
        mud = np.maximum(mud, side * np.clip((n2 - .55) * 3, 0, 1) * .8)
        top = rr > .556
        base[top] = L('#2b2a27') * (.9 + .2 * n2[top, None])
        mud = mud * .45
        c_ = base * (1 - mud[:, None]) + L('#4d3f2d') * mud[:, None]
        dry = np.clip((n1 - .5) * 3, 0, 1)[:, None] * mud[:, None]
        return c_ * (1 - dry) + L('#7a6a52') * dry
    vcol(o, f)
WHEELS = []
for nm in ('Front left', 'Front right', 'Rear left', 'Rear right'):
    e = OB[nm + ' wheel assembly']
    rot = [o for o in e.children_recursive if o.type == 'MESH' and o.name.startswith('Vented brake rotor')]
    lo, hi = V((1e9,) * 3), V((-1e9,) * 3)
    for o in rot:
        a, b = wbb(o); lo = V(map(min, lo, a)); hi = V(map(max, hi, b))
    c = (lo + hi) / 2; s = -1 if c.y < 0 else 1
    c = V((c.x, s * .8525, c.z))
    for o in [o for o in e.children_recursive if o.type == 'MESH' and (o.name.startswith('Vented brake rotor') or o.name.startswith('Rotor drilled vent'))]:
        a_, b_ = wbb(o)
        if abs((a_.y + b_.y) / 2) > .9: bpy.data.objects.remove(o, do_unlink=True)   # outboard duplicate pokes through the new disc
    xf = Matrix.Translation(c) @ Matrix.Diagonal((1, s, 1, 1))
    WHEELS.append((nm, c, s))
    eg = grp(nm + ' military wheel'); eg.parent = e; eg.matrix_parent_inverse = e.matrix_world.inverted()
    bm = tyre_bm()
    sidewall_text(bm, 'MIL-SPEC  NDT  ALL TERRAIN  ·  RUN-FLAT', .44, 0)
    sidewall_text(bm, '37X12.50R17  LT  LOAD RANGE E  ·  MAX 50 PSI', .44, math.pi)
    if s < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces)
    t = obj(nm + ' NDT military tyre', bm, M_RUB, eg, xform=xf, sharp=40); tyre_colour(t)
    bm = rim_bm()
    if s < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces)
    obj(nm + ' steel beadlock rim', bm, M_RIM, eg, xform=xf)
    d = disc_obj(nm + ' dished wheel disc', xf, eg)
    bm = hub_bm()
    if s < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces)
    obj(nm + ' hub and lug nuts', bm, M_BOLT, eg, xform=xf)
    bm = ctis_hose_bm()
    if s < 0: bmesh.ops.reverse_faces(bm, faces=bm.faces)
    obj(nm + ' CTIS air hose', bm, M_BLACK, eg, xform=xf)
print('wheels done', flush=True)

# ------------------------------------------------------------------ 4. cow skull, horns, barbed wire, rags
SK = grp('12b • Creepy cow skull ornament')
SKO = V((-2.362, 0, 1.245))
sk = npz_mesh(SKULL, 'Weathered cow skull, cracked and blood-stained'); sc.collection.objects.link(sk)
sk.location = SKO; sk.parent = SK; sk.matrix_parent_inverse = SK.matrix_world.inverted()
sk.matrix_world = Matrix.Translation(SKO)
d = sk.modifiers.new('dec', 'DECIMATE'); d.ratio = .22
sk.data.materials.append(vcmat('Weathered bone', .62)); sk.data.shade_smooth()
def horn(side, broken):
    s = side
    P = [V((.085, .2 * s, -.02)), V((.08, .3 * s, .0)), V((.05, .40 * s, .035)), V((.0, .48 * s, .095)), V((-.04, .525 * s, .18)), V((-.06, .535 * s, .27)), V((-.055, .515 * s, .345))]
    pts = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(i - 1, 0)], P[i], P[i + 1], P[min(i + 2, len(P) - 1)]
        for k in range(8):
            t = k / 8
            pts.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    pts.append(P[-1])
    n = len(pts)
    if broken: pts = pts[:int(n * .68)]
    m = len(pts); radii = []
    for i in range(m):
        t = i / (n - 1)
        r = .05 * (1 - t) ** .85 + .004
        if t < .4: r *= 1 + .05 * math.sin(t * 95)          # growth rings
        radii.append(r)
    bm = bmesh.new(); rings = tube(bm, [p + SKO for p in pts], radii, 22, cap=True)
    if broken:   # jagged snapped end
        for v in rings[-1]:
            v.co += (v.co - rings[-1][0].co) * 0 + V((rnd.uniform(-.006, .006), rnd.uniform(-.006, .006), rnd.uniform(-.012, .012)))
    o = obj(('Left' if s < 0 else 'Right') + (' snapped' if broken else '') + ' cattle horn', bm, vcmat('Horn keratin', .45), SK)
    base = pts[0] + SKO; tip = pts[-1] + SKO; L_ = sum((pts[i + 1] - pts[i]).length for i in range(m - 1))
    def f(co, nr):
        dd = np.linalg.norm(co - np.array(base), axis=1) / (L_ * (1.0 if not broken else 1.45))
        t = np.clip(dd, 0, 1)[:, None]
        c = L('#bcae8e') * (1 - t) + L('#6c5a42') * np.clip(t * 1.6, 0, 1) * (1 - t) + L('#231c15') * t ** 1.5
        st = fbm(co, 40, 3, 3.)[:, None]
        c = c * (.75 + .45 * st)
        return c
    vcol(o, f)
    return pts
hp = horn(1, False); hl = horn(-1, True)
# barbed wire wrapped round the right horn root
bm = bmesh.new()
seg = hp[2:14]
def helix(seg, rad_fn, turns, phase):
    out = []
    tot = len(seg) - 1; Nn = 160
    for i in range(Nn + 1):
        t = i / Nn * tot; k = min(int(t), tot - 1); f = t - k
        p = seg[k].lerp(seg[k + 1], f); d = (seg[k + 1] - seg[k]).normalized(); a, b = frame_from(d)
        ang = phase + turns * 2 * math.pi * i / Nn
        out.append(p + SKO + (a * math.cos(ang) + b * math.sin(ang)) * rad_fn(i / Nn))
    return out
rf = lambda u: .052 * (1 - u * .35)
for ph in (0, math.pi):
    strand = helix(seg, rf, 5, 0)
    # twist the two strands around the main helix
    tw = []
    for i, p in enumerate(strand):
        q = strand[min(i + 1, len(strand) - 1)] - strand[max(i - 1, 0)]; a, b = frame_from(q)
        ang = ph + i * .9; tw.append(p + (a * math.cos(ang) + b * math.sin(ang)) * .0022)
    tube(bm, tw, .0014, 5, cap=True)
strand = helix(seg, rf, 5, 0)
for i in range(6, len(strand), 13):
    p = strand[i]
    for dv in (V((1, .3, .2)), V((-.2, 1, .4)), V((.3, -.4, 1))):
        dv = dv.normalized(); tube(bm, [p - dv * .011, p + dv * .011], .0011, 4)
obj('Barbed wire wrapped round horn', bm, M_WIRE, SK, sharp=0)
# hanging rags tied to the snapped horn
for j, (off, ln) in enumerate(((0, .26), (.02, .19))):
    p0 = hl[-6] + SKO + V((0, 0, -.03 + off))
    bm = bmesh.new(); prev = None; rows = []
    for i in range(9):
        t = i / 8; z = -t * ln; wob = .012 * math.sin(t * 7 + j) + rnd.uniform(-.004, .004)
        w = .028 * (1 - .5 * t)
        rows.append([bm.verts.new(p0 + V((wob - .004 * i, -w / 2 + .01 * j, z))), bm.verts.new(p0 + V((wob, w / 2 + .01 * j, z - .004 * (i % 2))))])
    for i in range(8):
        bm.faces.new((rows[i][0], rows[i][1], rows[i + 1][1], rows[i + 1][0]))
    o = obj(f'Tattered rag strip {j + 1}', bm, M_RAG, SK, sharp=0)
    so = o.modifiers.new('s', 'SOLIDIFY'); so.thickness = .002
print('skull done', flush=True)

# ------------------------------------------------------------------ 5. machine gun: ammo can + belt + spent links + brass
GUN = G['11']
GG = grp('11b • Ammo feed and belt'); GG.parent = GUN; GG.matrix_parent_inverse = GUN.matrix_world.inverted()
def cartridge(bm, base, d, fired=False, tip=None):
    d = V(d).normalized()
    prof = [(0, 0), (.0105, 0), (.0105, .004), (.0094, .005), (.0101, .007), (.0101, .084), (.0072, .093), (.007, .099)]
    if fired: prof = prof + [(.0062, .099), (.0062, .09)]
    rings = []
    a, b = frame_from(d)
    segs = 10
    for k in range(segs):
        t = 2 * math.pi * k / segs
        rings.append([bm.verts.new(V(base) + d * ax + (a * math.cos(t) + b * math.sin(t)) * r) for r, ax in prof])
    for k in range(segs):
        A_, B_ = rings[k], rings[(k + 1) % segs]
        for i in range(len(prof) - 1):
            q = [A_[i], B_[i], B_[i + 1], A_[i + 1]]
            if len(set(q)) == 4: bm.faces.new(q)
    return d
def bullet(bm, base, d):
    d = V(d).normalized(); a, b = frame_from(d)
    prof = [(.0068, .098), (.0068, .118), (.0062, .13), (.0045, .142), (.0022, .15), (0, .153)]
    revolve_pts = []
    segs = 10; rings = []
    for k in range(segs):
        t = 2 * math.pi * k / segs
        rings.append([bm.verts.new(V(base) + d * ax + (a * math.cos(t) + b * math.sin(t)) * r) for r, ax in prof])
    for k in range(segs):
        A_, B_ = rings[k], rings[(k + 1) % segs]
        for i in range(len(prof) - 1):
            q = [A_[i], B_[i], B_[i + 1], A_[i + 1]]
            if len(set(q)) == 4: bm.faces.new(q)
def link(bm, base, d, tang, pitch=.026):
    d = V(d).normalized(); tang = V(tang).normalized()
    for ax in (.03, .062):
        c = V(base) + d * ax
        cyl(bm, c, d, .0118, .011, 10)
    box(bm, V(base) + d * .046 + tang * pitch * .5, (.022 if abs(d.x) > .5 else .006, .006, .006) if False else (.02, .004, .004),
        rot=V((1, 0, 0)).rotation_difference(d).to_matrix() if False else None)
def belt(path, cases=True, x0=.505, step=.026, name='Linked belt'):
    # resample path at constant spacing
    P = [V(p) for p in path]; out = []
    acc = 0; i = 0; pos = P[0]; out.append((pos, (P[1] - P[0]).normalized()))
    seglen = [(P[k + 1] - P[k]).length for k in range(len(P) - 1)]
    tot = sum(seglen); n = int(tot / step)
    for j in range(1, n + 1):
        s_ = j * step; k = 0
        while k < len(seglen) - 1 and s_ > seglen[k]: s_ -= seglen[k]; k += 1
        out.append((P[k].lerp(P[k + 1], min(s_ / seglen[k], 1)), (P[k + 1] - P[k]).normalized()))
    bc, bb, bl_, bt = bmesh.new(), bmesh.new(), bmesh.new(), bmesh.new()
    for j, (p, tg) in enumerate(out):
        base = V((x0, p.y, p.z)); d = V((-1, 0, 0))
        if cases:
            cartridge(bc, base + d * -0.0, (1, 0, 0) if False else d * -1 if False else d)
            bullet(bb if j % 5 else bt, base, d)
        for ax in ((.028, .06) if cases else (.03, .062)):
            cyl(bl_, base + d * ax, d, .0116, .011, 10)
        # connecting tab between this link and the next
        tab_c = base + d * .045 + V((0, tg.y, tg.z)) * step * .5
        tb = bmesh.new(); bmesh.ops.create_cube(tb, size=1)
        rot = V((0, 1, 0)).rotation_difference(V((0, tg.y, tg.z)).normalized()).to_matrix().to_4x4()
        bmesh.ops.transform(tb, matrix=Matrix.Translation(tab_c) @ rot @ Matrix.Diagonal((.012, step * .9, .003, 1)), verts=tb.verts)
        me = bpy.data.meshes.new('_t'); tb.to_mesh(me); tb.free(); bl_.from_mesh(me); bpy.data.meshes.remove(me)
    if cases:
        obj(name + ' brass cases', bc, M_BRASS, GG, sharp=0)
        obj(name + ' ball projectiles', bb, M_TIP, GG, sharp=0)
        obj(name + ' black-tip tracer rounds', bt, M_BTIP, GG, sharp=0)
    obj(name + ' steel links', bl_, M_LINK, GG, sharp=0)
# ammo can on the feed side (replaces the plain prop box)
CAN0, CAN1 = V((.455, -.395, 1.905)), V((.80, -.20, 2.17))
cc = (CAN0 + CAN1) / 2; cs = CAN1 - CAN0
bm = bmesh.new(); box(bm, cc, cs, bev=.008)
for z in (.33, .66):     # pressed stiffening ribs
    box(bm, V((cc.x, CAN0.y - .002, CAN0.z + cs.z * z)), (cs.x * .86, .006, .012), bev=.002)
    box(bm, V((cc.x, CAN1.y + .002, CAN0.z + cs.z * z)), (cs.x * .86, .006, .012), bev=.002)
obj('Ammo can body', bm, M_OD, GG)
# stencil decal plane on the outboard side
bm = bmesh.new(); uv = bm.loops.layers.uv.new()
vs = [bm.verts.new(V((CAN0.x + .02, CAN0.y - .0045, CAN0.z + .035))), bm.verts.new(V((CAN1.x - .02, CAN0.y - .0045, CAN0.z + .035))),
      bm.verts.new(V((CAN1.x - .02, CAN0.y - .0045, CAN0.z + .035 + .16))), bm.verts.new(V((CAN0.x + .02, CAN0.y - .0045, CAN0.z + .035 + .16)))]
f = bm.faces.new((vs[1], vs[0], vs[3], vs[2]))
for l, uvv in zip(f.loops, ((1, 0), (0, 0), (0, 1), (1, 1))): l[uv].uv = uvv
obj('Ammo can CAL .50 stencil', bm, M_CAN, GG, smooth=False)
# open lid hinged on the outboard edge, handle, latch
bm = bmesh.new(); lid_h = V((cc.x, CAN0.y, CAN1.z))
box(bm, V((0, 0, 0)), (cs.x + .01, cs.y + .006, .02), bev=.005)
box(bm, V((0, 0, .02)), (.12, .014, .012), bev=.004)
lid_h = V((CAN1.x, cc.y, CAN1.z + .005)); lidM = Matrix.Translation(lid_h) @ Matrix.Rotation(math.radians(100), 4, 'Y') @ Matrix.Translation(V((-cs.x / 2 - .005, 0, .0)))
bmesh.ops.transform(bm, matrix=lidM, verts=bm.verts)
obj('Ammo can hinged lid (open)', bm, M_OD, GG)
bm = bmesh.new(); box(bm, V((CAN1.x + .006, cc.y, CAN1.z - .03)), (.012, .05, .06), bev=.003)
tube(bm, [V((CAN0.x - .004, cc.y - .05, cc.z + .02)), V((CAN0.x - .03, cc.y - .03, cc.z + .02)), V((CAN0.x - .03, cc.y + .03, cc.z + .02)), V((CAN0.x - .004, cc.y + .05, cc.z + .02))], .006, 8)
obj('Ammo can latch and carry handle', bm, M_LINK, GG)
# folded belt inside the can (top layer)
for row in range(2):
    pts = [V((0, CAN0.y + .03, CAN1.z - .03 - row * .03)), V((0, CAN1.y - .02, CAN1.z - .03 - row * .03))]
    belt(pts, x0=.705 - .1, name=f'Folded belt layer {row + 1}') if False else None
belt([V((0, -.33, CAN1.z - .035)), V((0, -.235, CAN1.z - .035))], x0=.55, name='Can top belt layer')
# feed run: out of the can, arcing up into the receiver feed tray
FEED = [V((0, -.215, CAN1.z - .03)), V((0, -.215, 2.24)), V((0, -.2, 2.28)), V((0, -.16, 2.298)), V((0, -.12, 2.285)), V((0, -.095, 2.265))]
belt(FEED, x0=.55, name='Feed belt')
# spent links spilling out of the ejection side
belt([V((0, .1, 2.24)), V((0, .14, 2.22)), V((0, .17, 2.15)), V((0, .18, 2.06)), V((0, .175, 1.98))], cases=False, x0=.55, name='Ejected link chain')
# a spare belt draped over the turret ring
belt([V((0, .05, 1.83)), V((0, .13, 1.82)), V((0, .19, 1.78)), V((0, .22, 1.70))], x0=.62, name='Spare belt over turret ring')
# brass: spent cases everywhere
bm = bmesh.new()
spots = [(V((-.3, 0, 1.4)), .12, .3), (V((.45, 0, 1.4)), .25, .33), (V((.64, 0, 1.80)), .16, .14), (V((-1.2, 0, 1.29)), .3, .3)]
for c0, rx, ry in spots:
    for k in range(10 if c0.z < 1 else 7):
        p = c0 + V((rnd.uniform(-rx, rx), rnd.uniform(-ry, ry), .0105))
        if True:   # ray down so they sit on whatever is there: ray down so they sit on the panels
            hit = sc.ray_cast(bpy.context.evaluated_depsgraph_get(), p + V((0, 0, .5)), V((0, 0, -1)))
            if not hit[0]: continue
            p = hit[1] + V((0, 0, .0105))
        a = rnd.uniform(0, 2 * math.pi)
        cartridge(bm, p - V((math.cos(a), math.sin(a), 0)) * .05, (math.cos(a), math.sin(a), rnd.uniform(-.1, .1)), fired=True)
obj('Spent brass casings', bm, M_BRASS, GG, sharp=0)
print('gun done', flush=True)

# ------------------------------------------------------------------ 6. interior: tread plate floor, perforated mesh plates, radio, extinguisher
IN = grp('05b • Interior plates and kit')
fl = meshes('Cockpit formed floor tray')[0]
fl.data.materials.clear(); fl.data.materials.append(M_TREAD)
uvl = fl.data.uv_layers[0] if fl.data.uv_layers else fl.data.uv_layers.new(name="UVMap")
mw = fl.matrix_world
for poly in fl.data.polygons:
    for li in poly.loop_indices:
        w = mw @ fl.data.vertices[fl.data.loops[li].vertex_index].co
        uvl.data[li].uv = (w.x / .085, w.y / .085)
def plate(name, corners, mat, frame=True, uvscale=.12, backing=True):
    """quad plate from 4 world corners + angle-iron frame + rivets"""
    c = [V(p) for p in corners]
    bm = bmesh.new(); uv = bm.loops.layers.uv.new(); vs = [bm.verts.new(p) for p in c]
    f = bm.faces.new(vs)
    e1 = (c[1] - c[0]); e2 = (c[3] - c[0])
    for l in f.loops:
        q = l.vert.co - c[0]; l[uv].uv = (q.dot(e1.normalized()) / uvscale, q.dot(e2.normalized()) / uvscale)
    o = obj(name, bm, mat, IN, smooth=False)
    nrm = e1.cross(e2).normalized()
    if backing:
        bm = bmesh.new(); vs = [bm.verts.new(p - nrm * .012) for p in c]; bm.faces.new(vs)
        obj(name + ' backing', bm, pbr('Dark backing plate', '#1b1c18', .8, .3), IN, smooth=False)
    if frame:
        bm = bmesh.new()
        for i in range(4):
            a, b = c[i], c[(i + 1) % 4]; m = (a + b) / 2; d = (b - a)
            rot = V((1, 0, 0)).rotation_difference(d.normalized()).to_matrix()
            box(bm, m + nrm * .004, (d.length + .02, .022, .022), rot=rot, bev=.002)
            for k in range(1, int(d.length / .09)):
                hexbolt(bm, a.lerp(b, k / int(d.length / .09)) + nrm * .015, nrm, .006, .004)
        obj(name + ' angle frame', bm, M_OD, IN)
    return o
plate('Perforated mesh firewall', [(.80, -.35, .815), (.80, .35, .815), (.80, .35, 1.25), (.80, -.35, 1.25)], M_PERF)
plate('Diamond tread floor plate', [(-.47, -.345, .814), (.79, -.345, .814), (.79, .345, .814), (-.47, .345, .814)], M_TREAD, frame=True, uvscale=.085, backing=False)
for s in (-1, 1):
    plate(('Left' if s < 0 else 'Right') + ' perforated side liner', [(-.45, .352 * s, .815), (.76, .352 * s, .815), (.76, .352 * s, 1.15), (-.45, .352 * s, 1.15)][::(1 if s > 0 else -1)], M_PERF)
plate('Perforated engine deck mesh', [(1.25, -.27, 1.40), (1.25, .27, 1.40), (.95, .27, 1.40), (.95, -.27, 1.40)], M_PERF, backing=False)
# radio set beside the seat
bm = bmesh.new()
box(bm, V((.24, .30, .915)), (.24, .095, .2), bev=.006)
for k in range(3): cyl(bm, V((.118, .27 + k * .028, .975)), (-1, 0, 0), .009, .016, 12)
for k in range(2): cyl(bm, V((.118, .285 + k * .03, .875)), (-1, 0, 0), .006, .012, 10)
tube(bm, [V((.12, .265, 1.01)), V((.08, .265, 1.035)), V((.08, .335, 1.035)), V((.12, .335, 1.01))], .005, 6)
obj('Field radio set', bm, M_OD, IN)
bm = bmesh.new(); box(bm, V((.1185, .30, .94)), (.002, .05, .03)); obj('Radio display', bm, pbr('Radio display glow', '#9ac46a', .3, 0, 2.5), IN, smooth=False)
bm = bmesh.new(); box(bm, V((-.30, .27, 1.02)), (.03, .05, .1), bev=.008)
tube(bm, [V((.12, .31, .875)), V((0, .33, .835)), V((-.18, .32, .86)), V((-.29, .29, .97))], .0045, 6)
obj('Radio handset and coiled cord', bm, M_BLACK, IN)
# fire extinguisher clamped to the firewall
bm = bmesh.new(); cyl(bm, V((.75, .27, .97)), (0, 0, 1), .045, .3, 18); cyl(bm, V((.75, .27, 1.135)), (0, 0, 1), .022, .03, 12)
obj('Fire extinguisher', bm, M_RED, IN)
bm = bmesh.new()
for z in (.87, 1.07): cyl(bm, V((.75, .27, z)), (0, 0, 1), .049, .02, 18)
box(bm, V((.75, .27, 1.165)), (.07, .015, .012)); obj('Extinguisher clamps and lever', bm, M_STEEL, IN)
print('interior done', flush=True)

# ------------------------------------------------------------------ 7. rear cargo rack (replaces the rally wing)
RK = grp('07b • Rear cargo rack and stores')
bm = bmesh.new()
x0, x1, y0, z0 = 1.76, 2.30, .62, 1.30
for p, q in (((x0, -y0, z0), (x1, -y0, z0)), ((x0, y0, z0), (x1, y0, z0)), ((x0, -y0, z0), (x0, y0, z0)), ((x1, -y0, z0), (x1, y0, z0))):
    tube(bm, [V(p), V(q)], .018, 10)
for xx in (1.94, 2.12): tube(bm, [V((xx, -y0, z0)), V((xx, y0, z0))], .012, 8)
for yy in (-y0, y0):
    for xx in (x0, x1): tube(bm, [V((xx, yy, z0)), V((xx, yy, z0 + .2))], .014, 8)
    tube(bm, [V((x0, yy, z0 + .2)), V((x1, yy, z0 + .2))], .014, 8)
    tube(bm, [V((x0 + .02, yy * .8, z0)), V((1.62, yy * .72, 1.06))], .016, 8)       # struts down to the old wing mounts
    tube(bm, [V((x1, yy * .7, z0)), V((2.02, yy * .62, .92))], .016, 8)
tube(bm, [V((x1, -y0, z0 + .2)), V((x1, y0, z0 + .2))], .014, 8)
obj('Tubular cargo rack frame', bm, pbr('Rack black steel', '#262722', .55, .7), RK)
bm = bmesh.new(); box(bm, V(((x0 + x1) / 2, 0, z0 - .004)), (x1 - x0, 2 * y0, .006))
uvp = bm.loops.layers.uv.new()
for f in bm.faces:
    for l in f.loops: l[uvp].uv = (l.vert.co.x / .12, l.vert.co.y / .12)
obj('Rack perforated floor', bm, M_PERF, RK, smooth=False)
def jerry(c, mat, name, stencil=False):
    bm = bmesh.new(); W, D, H = .165, .345, .47     # W along y
    box(bm, c + V((0, 0, H / 2)), (D, W, H), bev=.012)
    for sx in (-1, 1):     # X emboss on both flanks
        for sg in (-1, 1):
            rot = Matrix.Rotation(sg * math.atan2(H * .7, D * .7), 3, 'Y')
            box(bm, c + V((0, sx * (W / 2 + .002), H / 2)), (math.hypot(D * .7, H * .7), .006, .02), rot=rot, bev=.002)
    for k in (-1, 0, 1):   # three handles
        tube(bm, [c + V((k * .07 - .015 + .06, -.03, H)), c + V((k * .07 - .015 + .06, -.03, H + .035)), c + V((k * .07 - .015 + .06, .03, H + .035)), c + V((k * .07 - .015 + .06, .03, H))], .008, 8)
    cyl(bm, c + V((-.12, 0, H + .015)), (0, 0, 1), .025, .03, 14); box(bm, c + V((-.12, 0, H + .035)), (.05, .016, .01))
    obj(name, bm, mat, RK)
    if stencil:
        bm = bmesh.new(); uv = bm.loops.layers.uv.new(); yy = c.y - W / 2 - .0035
        vs = [bm.verts.new(c + V((-.11, -W / 2 - .0035, .12))), bm.verts.new(c + V((.11, -W / 2 - .0035, .12))), bm.verts.new(c + V((.11, -W / 2 - .0035, .34))), bm.verts.new(c + V((-.11, -W / 2 - .0035, .34)))]
        f = bm.faces.new((vs[1], vs[0], vs[3], vs[2]))
        for l, u in zip(f.loops, ((1, 0), (0, 0), (0, 1), (1, 1))): l[uv].uv = u
        obj(name + ' WATER stencil', bm, M_JW, RK, smooth=False)
for i, yy in enumerate((-.52, -.345, .345, .52)):
    jerry(V((2.03, yy, z0)), M_TAN if i == 1 else M_OD, f'Jerry can {i + 1}', stencil=(i == 0))
# ammo cans stacked in the middle + tarp roll + straps
for k, (yy, zz) in enumerate(((-.09, 0), (.09, 0), (0, .19))):
    bm = bmesh.new(); box(bm, V((2.03, yy, z0 + zz + .095)), (.30, .16, .19), bev=.007)
    box(bm, V((2.03, yy, z0 + zz + .193)), (.31, .17, .016), bev=.004)
    tube(bm, [V((1.97, yy, z0 + zz + .2)), V((1.97, yy, z0 + zz + .225)), V((2.09, yy, z0 + zz + .225)), V((2.09, yy, z0 + zz + .2))], .006, 6)
    obj(f'Stowed ammo can {k + 1}', bm, M_OD, RK)
bm = bmesh.new(); cyl(bm, V((1.84, 0, z0 + .075)), (0, 1, 0), .075, .5, 20)
for yy in (-.17, .17): cyl(bm, V((1.84, yy, z0 + .075)), (0, 1, 0), .079, .03, 20)
obj('Rolled canvas tarp', bm, M_TARP, RK)
bm = bmesh.new()
for yy in (-.43, .43):
    box(bm, V((2.03, yy, z0 + .475)), (.36, .045, .004)); box(bm, V((1.85, yy, z0 + .24)), (.004, .045, .48)); box(bm, V((2.21, yy, z0 + .24)), (.004, .045, .48))
obj('Ratchet tie-down straps', bm, M_WEB, RK, smooth=False)
# whip antennas on the rear corners
for s in (-1, 1):
    bm = bmesh.new(); b0 = V((x1, s * y0, z0 + .2))
    cyl(bm, b0 + V((0, 0, .04)), (0, 0, 1), .018, .08, 12); cyl(bm, b0 + V((0, 0, .11)), (0, 0, 1), .011, .07, 10)
    tube(bm, [b0 + V((0, 0, .14)), b0 + V((.05, 0, .7)), b0 + V((.16, 0, 1.25))], [.004, .003, .0015], 6)
    obj(('Left' if s < 0 else 'Right') + ' whip antenna', bm, M_BLACK, RK)
print('rack done', flush=True)

# ------------------------------------------------------------------ 8. lamp guards + bolt rows on the armour
DET = grp('08b • Armour bolts and lamp guards')
bm = bmesh.new()
for o in meshes('Yellow auxiliary lamp'):
    a, b = wbb(o); c = (a + b) / 2; r = max(b.y - a.y, b.z - a.z) / 2 + .012; x = a.x - .014
    cc_ = V((x, c.y, c.z))
    pts = [cc_ + V((0, r * math.cos(t), r * math.sin(t))) for t in np.linspace(0, 2 * math.pi, 25)]
    tube(bm, pts, .0045, 6, cap=False)
    for k in (-.5, 0, .5):
        tube(bm, [cc_ + V((0, k * r, -math.sqrt(max(r * r - (k * r) ** 2, 0)))), cc_ + V((0, k * r, math.sqrt(max(r * r - (k * r) ** 2, 0))))], .003, 5)
        tube(bm, [cc_ + V((0, -math.sqrt(max(r * r - (k * r) ** 2, 0)), k * r)), cc_ + V((0, math.sqrt(max(r * r - (k * r) ** 2, 0)), k * r))], .003, 5)
# roof fog bar guard
for zz in (1.93, 1.99):
    tube(bm, [V((-.36, -.47, zz)), V((-.36, .47, zz))], .004, 6)
for yy in np.linspace(-.44, .44, 11):
    tube(bm, [V((-.36, yy, 1.875)), V((-.36, yy, 2.05))], .0032, 5)
obj('Wire lamp guards', bm, pbr('Guard black steel', '#1f201c', .5, .7), DET, sharp=0)
dg = bpy.context.evaluated_depsgraph_get()
bm = bmesh.new()
def bolt_row(p0, p1, dirv, n, targets):
    tg = set(targets)
    for k in range(n):
        p = V(p0).lerp(V(p1), k / (n - 1))
        hit, loc, nor, idx, ob, mx = sc.ray_cast(dg, p, V(dirv))
        if hit and ob.name.split('.')[0] in tg:
            hexbolt(bm, loc, nor, .0085, .006)
for s in (-1, 1):
    bolt_row((-1.86, .47 * s, 2), (-.40, .47 * s, 2), (0, 0, -1), 17, ['Long faceted hood top'])
    bolt_row((-1.62, .30 * s, 2), (-.56, .30 * s, 2), (0, 0, -1), 12, ['Raised angular hood insert'])
    bolt_row((-.45, 1.2 * s, 1.19), (.86, 1.2 * s, 1.19), (0, -s, 0), 15, ['Cockpit sill armor'])
    bolt_row((.80, .53 * s, 2), (1.90, .53 * s, 2), (0, 0, -1), 13, ['Rear quarter armored shell'])
    bolt_row((-1.78, 1.2 * s, 1.17), (-.40, 1.2 * s, 1.17), (0, -s, 0), 15, ['Angular long nose side cheek'])
    bolt_row((-1.78, 1.2 * s, .76), (-.40, 1.2 * s, .76), (0, -s, 0), 15, ['Angular long nose side cheek'])
obj('Armour plate bolt rows', bm, M_BOLT, DET, sharp=0)
print('details done', flush=True)
bpy.ops.wm.save_as_mainfile(filepath=OUT)
print('SAVED', OUT, flush=True)
