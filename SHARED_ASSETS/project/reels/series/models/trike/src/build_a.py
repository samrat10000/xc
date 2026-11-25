"""Stage A: remove slick tyres, build knobby M/T tyres, add lamps, tail lights, jerry can rack. usage: build_a.py -- in.glb out.blend"""
import bpy, bmesh, sys, os, math, random
import numpy as np
from mathutils import Vector as V, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import *
A = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=A[0])
sc = bpy.context.scene; OB = bpy.data.objects
ROOT = OB['IVORY • three-wheel concept racer']
def grp(name, parent=ROOT):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.parent = parent; return e
KILL = ('grooved slick tire', 'Inset molded tire screw slot', 'Molded tread circular inset', 'Recessed circular molded tread boundary',
        'Molded sidewall shoulder ridge', 'Raised sidewall rating dash', 'Inner bead witness line', 'Front tread small ivory identification tab')
n = 0
for o in list(OB):
    if o.type == 'MESH' and any(k in o.name for k in KILL): bpy.data.objects.remove(o, do_unlink=True); n += 1
print('removed', n, flush=True)
# ------------------------------------------------------------------ stretch the body: longer nose / wheelbase
D = float(os.environ.get('STRETCH', '.8')); X0, X1 = -1.55, -.45; F = (X1 - X0 + D) / (X1 - X0)
def xm(x): return x - D if x < X0 else (X1 + (x - X1) * F if x < X1 else x)
FWA = OB['Front • wheel assembly']; fw_set = set(FWA.children_recursive)
for o in [o for o in OB if o.type == 'MESH']:
    if o.data.users > 1: o.data = o.data.copy()
    mw = o.matrix_world; mi = mw.inverted(); me = o.data
    co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    w = np.c_[co, np.ones(len(co))] @ np.array(mw).T
    cx = (w[:, 0].min() + w[:, 0].max()) / 2; diag_ = np.linalg.norm(w[:, :3].max(0) - w[:, :3].min(0))
    if o in fw_set or diag_ < .2: w[:, 0] += xm(cx) - cx
    else: w[:, 0] = np.where(w[:, 0] < X0, w[:, 0] - D, np.where(w[:, 0] < X1, X1 + (w[:, 0] - X1) * F, w[:, 0]))
    loc = (w @ np.array(mi).T)[:, :3].astype(np.float32); me.vertices.foreach_set('co', loc.ravel()); me.update()
FX = -2.52 - D
print('stretched', D, flush=True)
M_RUB = vcmat('Rubber_MudTerrain', .88)
M_BLK = pbr('Plastic_Black', '#151617', .55)
M_STEEL = pbr('Steel_Bracket', '#3a3d40', .45, .85)
M_LENS = pbr('Lamp_LED_White', '#fff4dc', .1, 0, 12)
M_REFL = pbr('Lamp_Reflector', '#c8ccd0', .15, 1)
M_TAIL = pbr('Lamp_Tail_Red', '#ff2a14', .2, 0, 8)
M_CAN = pbr('Paint_JerryCan_Olive', '#4a4f33', .6, .3)
M_STRAP = pbr('Strap_Webbing_Orange', '#c04a1a', .85)

# ------------------------------------------------------------------ knobby tyres
def tyre(R, hw, rim, h, N, name, c, parent, seed):
    rnd = random.Random(seed)
    rc = R - h                          # carcass crown radius
    half = [(rim + .03, .84 * hw), (rim + .10 * (rc - rim), .97 * hw), ((rim + rc) * .5, 1.0 * hw), (rc - .16 * (rc - rim), .985 * hw),
            (rc - .05 * (rc - rim), .93 * hw), (rc - .01, .78 * hw), (rc, .45 * hw), (rc, 0.)]
    PROF = half + [(r, -a) for r, a in reversed(half[:-1])]
    pa = np.array([a for r, a in half]); pr = np.array([r for r, a in half]); o_ = np.argsort(pa)
    r_at = lambda u: float(np.interp(abs(u), pa[o_], pr[o_]))
    bm = bmesh.new(); revolve(bm, PROF, segs=160, axis='Y')
    def lug(phi0, u0, u1, w0, w1, hh0, ang=34):
        st = 7; rings = []
        for i in range(st):
            t = i / (st - 1); u = u0 + (u1 - u0) * t
            phi = phi0 + math.tan(math.radians(ang)) * (u - u0) * (1 if u1 > u0 else -1) / R
            w = (w0 + (w1 - w0) * t) / R
            rb = r_at(u) - .01
            over = max(0., (abs(u) - .8 * hw) / (.2 * hw))      # wraps down the shoulder
            top = rc + hh0 * (1 - .35 * over) - over * .12 * (rc - rim)
            ring = [bm.verts.new(V((rr * math.sin(phi + dp), u, rr * math.cos(phi + dp))))
                    for dp, rr in ((-w, rb), (w, rb), (w * .8, top), (-w * .8, top))]
            rings.append(ring)
        for i in range(st - 1):
            a, b = rings[i], rings[i + 1]
            for k in range(4): bm.faces.new((a[k], a[(k + 1) % 4], b[(k + 1) % 4], b[k]))
        bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    for k in range(N):
        p = 2 * math.pi * k / N; j = rnd.uniform(-.004, .004); q2 = math.pi / N
        lug(p + j, 1.03 * hw, .40 * hw, .085 * R, .07 * R, h, 16)          # shoulder blocks wrap the edge
        lug(p + q2 + j, -1.03 * hw, -.40 * hw, .085 * R, .07 * R, h, 16)
        lug(p + q2 + j, .30 * hw, -.10 * hw, .07 * R, .06 * R, h, 16)      # centre blocks, staggered
        lug(p + j, -.30 * hw, .10 * hw, .07 * R, .06 * R, h, 16)
        for s in (-1, 1):
            ph = p + (0 if s > 0 else q2)
            r0, r1 = rc - .34 * (rc - rim), rc - .10 * (rc - rim); w = .05 * R / ((r0 + r1) / 2)
            ax0 = s * .99 * hw; ax1 = ax0 + s * .02 * R
            vs = [bm.verts.new(V((rr * math.sin(ph + dp), aa, rr * math.cos(ph + dp)))) for rr in (r0, r1) for dp in (-w, w) for aa in (ax0 - s * .01, ax1)]
            # vs index: (r, dp, a) -> 4*r+2*dp+a
            q = lambda *ix: bm.faces.new([vs[i] for i in ix])
            try:
                q(1, 3, 7, 5); q(0, 1, 5, 4); q(2, 6, 7, 3); q(0, 2, 3, 1); q(4, 5, 7, 6)
            except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for side in (-1, 1):
        for txt, ph in (('DEAD ROADS  M/T  ·  MUD TERRAIN', 0.), ('LT 37X14.50R18  ·  LOAD RANGE E', math.pi)):
            cu = bpy.data.curves.new('t', 'FONT'); cu.body = txt; cu.size = .045 * R; cu.extrude = .003; cu.align_x = 'CENTER'
            cu.font = bpy.data.fonts.load('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
            to = bpy.data.objects.new('t', cu); sc.collection.objects.link(to)
            dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(to.evaluated_get(dg))
            bpy.data.objects.remove(to); tb = bmesh.new(); tb.from_mesh(me); bpy.data.meshes.remove(me)
            Rt = rim + .38 * (rc - rim)
            for v in tb.verts:
                x, y, z = v.co; phi = ph - side * x / Rt; r = Rt + y
                ax = side * (r_at(hw * .999) if r > half[1][0] else hw) * 1.0
                ax = side * (float(np.interp(r, [pr[0], pr[1], pr[2], pr[3]], [pa[0], pa[1], pa[2], pa[3]])) + .001 + z)
                v.co = V((r * math.sin(phi), ax, r * math.cos(phi)))
            if side < 0: bmesh.ops.reverse_faces(tb, faces=tb.faces)
            me = bpy.data.meshes.new('_t'); tb.to_mesh(me); tb.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    t = obj(name, bm, M_RUB, parent, xform=Matrix.Translation(c), sharp=40)
    def f(co, nr):
        q = co - np.array(c, np.float32); rr = np.sqrt(q[:, 0] ** 2 + q[:, 2] ** 2); ax = np.abs(q[:, 1])
        base = np.tile(L('#1c1c1b'), (len(co), 1)); n1 = fbm(co, 9, 3, 2.); n2 = fbm(co, 30, 2, 5.)
        groove = (rr < rc + .01) & (ax < .8 * hw)
        mud = groove * np.clip((n1 - .3) * 2.5, 0, 1) * .8 + np.clip((n1 - .62) * 3, 0, 1) * .4
        side = ax > .9 * hw
        mud = np.maximum(mud, side * np.clip((n2 - .5) * 3, 0, 1) * np.clip((rc - rr) / (rc - rim) * 1.4, 0, 1) * .8)
        top = rr > rc + h * .7
        base[top] = L('#2c2b29') * (.9 + .2 * n2[top, None]); mud[top] *= .3
        mud = mud * .75
        out = base * (1 - mud[:, None]) + L('#4a3c2a') * mud[:, None]
        dry = np.clip((n1 - .5) * 3, 0, 1)[:, None] * mud[:, None]
        return out * (1 - dry) + L('#857257') * dry
    vcol(t, f); return t
FW = OB['Front • wheel assembly']; RL = OB['Rear left • wheel assembly']; RR = OB['Rear right • wheel assembly']
tyre(.94, .45, .69, .075, 18, 'Front mud-terrain knobby tyre', V((FX, 0, .94)), FW, 1)
tyre(1.0, .59, .733, .085, 18, 'Rear left mud-terrain knobby tyre', V((1.85, -2.084, 1.0)), RL, 2)
tyre(1.0, .59, .733, .085, 18, 'Rear right mud-terrain knobby tyre', V((1.85, 2.084, 1.0)), RR, 3)
print('tyres done', flush=True)

# ------------------------------------------------------------------ helpers for placement
dg = bpy.context.evaluated_depsgraph_get()
def hit(o, d):
    r = sc.ray_cast(dg, V(o), V(d).normalized())
    return (r[1], r[2], r[4].name) if r[0] else (None, None, None)
LT = grp('11 • Lamps and lighting'); DT = grp('12 • Field kit and straps')

def lamp_pod(bm_body, bm_lens, bm_refl, c, fwd, rad, depth):
    f = V(fwd).normalized()
    revolve_body = [(0, -depth), (rad * .7, -depth), (rad * .95, -depth * .7), (rad, -depth * .2), (rad * 1.06, 0), (rad * 1.06, depth * .12), (rad * .93, depth * .12)]
    tmp = bmesh.new(); revolve(tmp, revolve_body, 32, axis='Z')
    q = f.to_track_quat('Z', 'Y').to_matrix().to_4x4(); bmesh.ops.transform(tmp, matrix=Matrix.Translation(c) @ q, verts=tmp.verts)
    me = bpy.data.meshes.new('_'); tmp.to_mesh(me); tmp.free(); bm_body.from_mesh(me); bpy.data.meshes.remove(me)
    cyl(bm_refl, c + f * depth * .02, f, rad * .9, depth * .06, 32)
    tmp = bmesh.new(); revolve(tmp, [(0, depth * .1), (rad * .5, depth * .09), (rad * .9, depth * .07)], 32, axis='Z')
    bmesh.ops.transform(tmp, matrix=Matrix.Translation(c) @ q, verts=tmp.verts)
    me = bpy.data.meshes.new('_'); tmp.to_mesh(me); tmp.free(); bm_lens.from_mesh(me); bpy.data.meshes.remove(me)
    # guard: cross bars
    a, b = frame_from(f)
    for d in (a, b):
        tube(bm_body, [c + f * depth * .16 - d * rad * 1.05, c + f * depth * .2 - d * rad * .5, c + f * depth * .22, c + f * depth * .2 + d * rad * .5, c + f * depth * .16 + d * rad * 1.05], rad * .06, 6)

# front fog pods on the fork blades
bb, bl, br = bmesh.new(), bmesh.new(), bmesh.new()
for s in (-1, 1):
    p, nrm, nm = hit((-1.15, .9 * s, 4), (0, 0, -1)); print('pod base', p, nm)
    if p is None: continue
    c = p + V((0, 0, .2))
    lamp_pod(bb, bl, br, c, (-1, .12 * s, -.05), .13, .16)
    tube(bb, [p + V((0, 0, -.01)), p + V((.01, 0, .09)), c + V((.04, 0, -.04))], .022, 8)     # stalk
    box(bb, p + V((0, 0, .008)), (.14, .1, .02), bev=.005)                                   # foot plate
    for dx in (-.045, .045): hexbolt(bb, p + V((dx, 0, .018)), (0, 0, 1), .011, .01)
obj('Front LED pods with guards', bb, M_BLK, LT); obj('Front LED pod reflectors', br, M_REFL, LT, sharp=0); obj('Front LED pod lenses', bl, M_LENS, LT)

# roof light bar on the orange crown
cr = OB['Broad orange racing roof crown']; mi = cr.matrix_world.inverted(); best = None
for i in range(40):
    x = .5 + i * .02; o_ = mi @ V((x, 0, 5)); d_ = (mi.to_3x3() @ V((0, 0, -1))).normalized()
    ok, loc, nn, fi = cr.ray_cast(o_, d_)
    if ok:
        w_ = cr.matrix_world @ loc
        if best is None or w_.z > best.z: best = w_
p, nrm, nm = best, None, 'crown'; print('crown', p)
bb, bl, br = bmesh.new(), bmesh.new(), bmesh.new()
if p is not None:
    top = p.z; x0 = p.x
    box(bb, V((x0 - .04, 0, top + .12)), (.16, .78, .15), bev=.02)
    for i in range(6):
        y = -.32 + i * .128; cc = V((x0 - .125, y, top + .12))
        cyl(br, cc, (-1, 0, 0), .05, .012, 24); cyl(bl, cc + V((-.008, 0, 0)), (-1, 0, 0), .043, .01, 24)
    for s in (-1, 1):
        tube(bb, [V((x0 - .02, .33 * s, top + .05)), V((x0 + .02, .34 * s, top - .02)), V((x0 + .05, .34 * s, top - .08))], .02, 8)
        hexbolt(bb, V((x0 - .04, .395 * s, top + .12)), (0, s, 0), .016, .012)
    tube(bb, [V((x0 + .04, .3, top + .1)), V((x0 + .12, .2, top + .02)), V((x0 + .2, .05, top - .05))], .012, 6)  # power lead
obj('Roof LED light bar', bb, M_BLK, LT); obj('Roof light bar reflectors', br, M_REFL, LT, sharp=0); obj('Roof light bar LEDs', bl, M_LENS, LT)

# tail lights on the back of the rear spats
bb, bl = bmesh.new(), bmesh.new()
for s in (-1, 1):
    p, nrm, nm = hit((5, 1.33 * s, .84), (-1, 0, 0)); print('spat rear', p, nrm, nm)
    if p is None: continue
    box(bb, p + V((.02, 0, 0)), (.05, .2, .09), bev=.012)
    box(bl, p + V((.048, 0, 0)), (.012, .17, .06), bev=.006)
obj('Tail lamp housings', bb, M_BLK, LT); obj('Tail lamp lenses', bl, M_TAIL, LT)

# jerry can + rack behind the headrest
p, nrm, nm = hit((1.9, 0, 4), (0, 0, -1)); print('rear deck', p, nm)
if p is not None:
    z0 = p.z; c = V((1.9, 0, z0 + .03))
    bb = bmesh.new()
    for s in (-1, 1):
        tube(bb, [V((1.68, .3 * s, z0 - .02)), V((1.68, .3 * s, z0 + .05)), V((1.68, .3 * s, z0 + .05)), V((2.12, .3 * s, z0 + .05)), V((2.12, .3 * s, z0 - .02))], .016, 8)
    for x in (1.68, 2.12): tube(bb, [V((x, -.3, z0 + .05)), V((x, .3, z0 + .05))], .016, 8)
    obj('Jerry can tube rack', bb, M_STEEL, DT, sharp=30)
    # jerry can lying flat, long axis along X
    jc = bmesh.new(); W, Hh, D = .47, .17, .35
    box(jc, c + V((0, 0, Hh / 2 + .05)), (W, D, Hh), bev=.025)
    for s in (-1, 1):   # pressed X ribs
        for t in (-1, 1):
            box(jc, c + V((0, 0, Hh + .05)) + V((t * .1, s * .08, .005)), (.17, .02, .01), rot=Matrix.Rotation(math.radians(30 * s * t), 3, 'Z'), bev=.004)
    # triple handle at the +X end
    for yy in (-.1, 0, .1): tube(jc, [c + V((W / 2 - .02, yy, Hh + .05)), c + V((W / 2 + .03, yy, Hh + .09)), c + V((W / 2 + .08, yy, Hh + .05))], .012, 6)
    cyl(jc, c + V((W / 2 + .03, .13, Hh / 2 + .1)), (1, .4, .4), .03, .07, 12)   # spout
    obj('Olive jerry can', jc, M_CAN, DT, sharp=30)
    st = bmesh.new()
    for xx in (-.12, .12):
        pts = [V((1.9 + xx, -.33, z0 + .03)), V((1.9 + xx, -.2, z0 + Hh + .085)), V((1.9 + xx, .2, z0 + Hh + .085)), V((1.9 + xx, .33, z0 + .03))]
        for i in range(3):
            a, b = pts[i], pts[i + 1]; box(st, (a + b) / 2, ((b - a).length + .01, .05, .008), rot=(b - a).to_track_quat('X', 'Z').to_matrix(), bev=0)
        box(st, V((1.9 + xx, -.21, z0 + Hh + .09)), (.07, .05, .012), bev=.004)  # buckle
    obj('Ratchet straps', st, M_STRAP, DT, sharp=0)
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guns.py')).read())
bpy.ops.wm.save_as_mainfile(filepath=A[1]); print('SAVED', flush=True)
