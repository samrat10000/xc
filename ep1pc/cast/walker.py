import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy, bmesh
from mathutils import Vector, noise, Euler
import castlib as L, anatomy as A
V = A.V
STAGE = os.environ.get('STAGE', 'all')
OUT = os.environ.get('OUT', '/tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/cast/out/walker')
os.makedirs(OUT, exist_ok=True)
sc = L.reset()
C = L.collection('Walker')
rng = random.Random(11)

# ------------------------------------------------------------------ skeleton (posed: hunched shamble)
sk = A.Skel()
sk.add('pelvis', (0, 0, .955), (.150, .105))
A.limb(sk, 'sp', 'pelvis', [(0, -.004, 1.08), (0, -.03, 1.22), (0, -.07, 1.34)],
       [(.128, .088, 1.0), (.148, .098, 1.0), (.165, .105, 1.0)], mids=1)
A.limb(sk, 'nk', 'sp2', [(0, -.11, 1.43), (0, -.14, 1.50), (0, -.155, 1.545)], [(.054, .054), (.047, .049), (.045, .047)], mids=0)
for s, side in ((1, 'A'), (-1, 'B')):
    sk.add(f'cl{side}', (.085 * s, -.065, 1.385), (.06, .055), 'sp2')
    sk.add(f'sh{side}', (.185 * s, -.06, 1.36), (.056, .056), f'cl{side}')
# arm A reaching forward, arm B limp
A.limb(sk, 'aA', 'shA', [(.215, -.30, 1.29), (.205, -.54, 1.255), (.20, -.605, 1.235)],
       [(.039, .037, 1.12), (.025, .019, 1.18), (.032, .013)], mids=2)
A.limb(sk, 'aB', 'shB', [(-.245, -.05, 1.09), (-.255, -.085, .855), (-.257, -.095, .785)],
       [(.038, .037, 1.12), (.025, .019, 1.18), (.032, .013)], mids=2)
A.hand(sk, 1, 'aA1', 'aA2', curl=.9, rng=rng)
A.hand(sk, -1, 'aB1', 'aB2', curl=.5, rng=rng)
for s, side, knee, ank, toe in ((1, 'A', (.105, -.11, .53), (.118, -.06, .105), (.125, -.20, .045)),
                                (-1, 'B', (-.10, .05, .52), (-.112, .17, .125), (-.118, .06, .04))):
    sk.add(f'hp{side}', (.088 * s, 0, .925), (.085, .085), 'pelvis')
    A.limb(sk, f'l{side}', f'hp{side}', [knee, ank, toe], [(.052, .054, 1.18), (.036, .038, 1.12), (.034, .022)], mids=2)
body = L.skin_body('Walker body', sk.j, sk.e, C, branch=.35, subdiv=2)

# body detail: emaciated ribs, veins, skin wrinkles
def ribs_w(p):
    # front/side chest band
    if not (1.12 < p.z < 1.36): return 0
    return L.sm(.0, .03, -(p.y + .02))
L.vgroup_by(body, 'ribs', ribs_w)
mr = body.modifiers.new('ribs', 'DISPLACE')
tex = bpy.data.textures.new('ribtex', 'WOOD'); tex.wood_type = 'BANDS'; tex.noise_basis_2 = 'SIN'; tex.turbulence = 2
mr.texture = tex; mr.texture_coords = 'GLOBAL'; mr.strength = .004; mr.vertex_group = 'ribs'
md = L.displace(body, 'CLOUDS', size=.03, strength=.004, depth=3)
mv = L.displace(body, 'VORONOI', size=.05, strength=-.0015, distance_metric='DISTANCE', noise_intensity=1.0)
L.apply_all(body)
# wound: open the left belly to show ribs inside
WC = V(.095, -.085, 1.17)
L.delete_faces(body, lambda p, n: (V((p - WC).x, (p - WC).y, (p - WC).z * .8)).length < .045 + .012 * noise.noise(p * 70))
L.smooth(body)

# ------------------------------------------------------------------ head
HEAD_LOC = V(0, -.165, 1.6)
hd = A.head('Walker head', C, rx=.086, ry=.102, rz=.118, gaunt=1.05, jaw_open=1.0)
up = A.teeth('Walker teeth up', C, cz=-.042, cy=-.074, w=.03, n=11, missing=(3, 8), seed=2)
lo = A.teeth('Walker teeth low', C, cz=-.071, cy=-.066, w=.026, down=True, n=10, missing=(1, 6), seed=5)
gum = L.tube('Walker gum', [V(math.sin(t * 2.2) * .03, -.072 + (1 - math.cos(t * 2.2)) * .021, -.040) for t in [i / 10 - .5 for i in range(11)]], .0035, C, sides=6)
eyes = []; ears = []
for sx in (1, -1):
    e = L.blob(f'Walker eye {sx}', (.031 * sx, -.056, .013), (.0102, .0102, .0102), C)
    lid = L.tube(f'Walker lid {sx}', [V(.031 * sx + math.cos(a) * .0122, -.060 - math.sin(a) * .004, .013 + math.sin(a) * .0105) for a in [i / 10 * math.pi for i in range(11)]], .0022, C, sides=6)
    lid2 = L.tube(f'Walker lidlow {sx}', [V(.031 * sx + math.cos(a) * .0118, -.059, .012 - math.sin(a) * .0095) for a in [i / 10 * math.pi for i in range(11)]], .0016, C, sides=6)
    ears.append(lid); ears.append(lid2)
    eyes.append(e)
# ears: flattened, one torn

for sx in (1, -1):
    e = L.blob(f'Walker ear {sx}', (.081 * sx, .006, .0), (.007, .016, .026), C, rot=(0, 0, .25 * sx))
    if sx < 0:
        L.apply_transform(e); L.delete_faces(e, lambda p, n: p.z > .006 + .004 * noise.noise(p * 400))
    ears.append(e)
mouth_in = L.blob('Walker mouth', (0, -.038, -.055), (.026, .03, .02), C)
headgrp = [hd, up, lo, gum, mouth_in] + eyes + ears
pivot = bpy.data.objects.new('Walker headpivot', None); C.objects.link(pivot)
for o in headgrp: o.parent = pivot
pivot.location = HEAD_LOC; pivot.rotation_euler = (math.radians(14), math.radians(-11), math.radians(8))
bpy.context.view_layer.update()

# ------------------------------------------------------------------ interior of the wound: cavity + ribs
cav = L.blob('Walker cavity', WC + V(-.012, .02, 0), (.04, .035, .05), C)
rib_objs = []
for k in range(4):
    z = 1.135 + k * .026
    pts = []
    for t in range(9):
        a = -.9 + t * .22
        pts.append(V(.02 + math.cos(a) * .085, -.01 + math.sin(a) * .07 - .02, z + t * .002))
    rib_objs.append(L.tube(f'Walker rib{k}', pts, [.0055 - abs(t - 4) * .0003 for t in range(9)], C, sides=8))
ribs = L.join(rib_objs, 'Walker ribs')

if STAGE == 'body':
    pass

# ================================================================== clothing
SHA, SHB = sk.p('shA'), sk.p('shB')
def sleeve(p):
    return min((p - SHA).length, (p - SHB).length)
shirt = L.dup(body, 'Walker shirt', C)
L.keep_verts(shirt, lambda p: .86 + .03 * noise.noise(p * 30) < p.z < 1.47 and (abs(p.x) < .16 or sleeve(p) < .17 + .03 * noise.noise(p * 25)))
# open collar (V neck)
L.delete_faces(shirt, lambda p, n: p.z > 1.40 - max(0, .06 - abs(p.x) * 1.2) * (1 if p.y < -.1 else 0) and abs(p.x) < .07 and p.z > 1.36 and p.y < -.06 or (p.z > 1.43 and abs(p.x) < .06))
# tears and the wound hole
L.delete_faces(shirt, lambda p, n: ((p - WC).length < .07 + .02 * noise.noise(p * 40)) or
               (noise.noise(p * 16 + V(3, 1, 2)) > .52 and p.z < 1.3) or (p.z < .93 and noise.noise(p * 50) > .25))
def folds(co, n):
    p = co
    f = .015 + .007 * math.sin(p.z * 70 + 10 * noise.noise(p * 6)) * (1 - L.sm(1.25, 1.42, p.z)) + .004 * noise.noise(p * 18)
    f += .003 * noise.noise(p * 40)
    f += .006 * L.sm(1.0, .88, p.z)          # loose hem flares out
    return f
L.push(shirt, folds)
so = shirt.modifiers.new('sol', 'SOLIDIFY'); so.thickness = .004; so.offset = -1
L.apply_all(shirt); L.smooth(shirt)

pants = L.dup(body, 'Walker pants', C)
L.keep_verts(pants, lambda p: .11 + .04 * abs(noise.noise(p * 22)) < p.z < 1.01 and abs(p.x) < .19 and not (p.z > .7 and abs(p.x) > .17))
KNEE = sk.p('lA0')
L.delete_faces(pants, lambda p, n: (p - KNEE - V(0, -.04, .0)).length < .045 + .012 * noise.noise(p * 150) + .01 * noise.noise(p * 40) or (noise.noise(p * 20 + V(9, 9, 9)) + .15 * noise.noise(p * 140) > .6))
def pfold(co, n):
    p = co
    return .009 + .003 * math.sin(p.z * 70 + 6 * noise.noise(p * 10)) + .002 * noise.noise(p * 50) + .004 * L.sm(.25, .12, p.z)
L.push(pants, pfold)
so = pants.modifiers.new('sol', 'SOLIDIFY'); so.thickness = .004; so.offset = -1
L.apply_all(pants); L.smooth(pants)

# belt with buckle
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=48, radius1=1, radius2=1, depth=.035)
belt = L.mesh_obj('Walker belt', bm, C); belt.location = (0, -.004, .985); belt.scale = (.158, .116, 1)
so = belt.modifiers.new('sol', 'SOLIDIFY'); so.thickness = .006
buckle = L.box('Walker buckle', (.0, -.124, .985), (.024, .006, .018), C, bevel=.003)
buckle.rotation_euler = (0, 0, 0)

# ================================================================== shoes (one sole flapping)
def shoe(tag, ankle, toe, flap=0.):
    a, t = V(ankle), V(toe)
    sk2 = A.Skel()
    sk2.add('heel', (0, .035, -.075), (.040, .034))
    sk2.add('ank', (0, .005, -.02), (.044, .046), 'heel')
    sk2.add('inst', (0, -.07, -.058), (.046, .036), 'heel')
    sk2.add('ball', (0, -.14, -.074), (.049, .028), 'inst')
    sk2.add('toe', (0, -.19, -.080), (.041, .022), 'ball')
    up = L.skin_body(f'Walker shoe {tag}', sk2.j, sk2.e, C, branch=.6, subdiv=2)
    L.warp(up, lambda c: V(c.x, c.y, max(c.z, -.098)))
    # collar opening
    L.delete_faces(up, lambda p, n: p.z > -.012 and n.z > .5)
    sk3 = A.Skel()
    sk3.add('h', (0, .04, -.11), (.047, .03)); sk3.add('m', (0, -.07, -.11), (.05, .03), 'h')
    sk3.add('b', (0, -.15, -.11), (.055, .03), 'm'); sk3.add('t', (0, -.205, -.11), (.046, .03), 'b')
    sole = L.skin_body(f'Walker sole {tag}', sk3.j, sk3.e, C, branch=.6, subdiv=2)
    L.warp(sole, lambda c: V(c.x, c.y, min(max(c.z, -.125), -.097)))
    if flap:
        def fl(c):
            if c.y > -.06: return c
            dy, dz = c.y + .06, c.z + .125
            return V(c.x, -.06 + dy * math.cos(flap) - dz * math.sin(flap), -.125 + dy * math.sin(flap) + dz * math.cos(flap))
        L.warp(sole, fl)
    laces = []
    for i in range(6):
        y = -.025 - i * .02
        org = V(0, y, .1)
        ok, loc, nor, _ = up.ray_cast(org, V(0, 0, -1))
        if not ok: continue
        laces.append(L.box(f'Walker lace{tag}{i}', loc + V(0, 0, .002), (.022, .0035, .0025), C, rot=(0, 0, .35 if i % 2 else -.35), bevel=.001))
        for sx in (1, -1):
            laces.append(L.box(f'Walker eyelet{tag}{i}{sx}', loc + V(.021 * sx, 0, -.002), (.004, .004, .002), C, bevel=.001))
    tongue = L.box(f'Walker tongue {tag}', (0, -.012, -.006), (.022, .03, .006), C, rot=(-.6, 0, 0), bevel=.005)
    lc = L.join(laces + [tongue], f'Walker laces {tag}')
    d = (t - a); d.z = d.z * .5; d.normalize()
    rot = d.to_track_quat('-Y', 'Z').to_euler()
    for o in (up, sole, lc):
        o.location = a; o.rotation_euler = rot
        L.apply_transform(o); L.smooth(o)
    return up, sole, lc
shoeA = shoe('A', sk.p('lA1'), sk.p('lA2'))
shoeB = shoe('B', sk.p('lB1'), sk.p('lB2'), flap=-.4)
# hide the skin-modifier foot stumps inside the shoes
L.delete_faces(body, lambda p, n: p.z < .1)

# ================================================================== props: lanyard + badge, watch
dg = bpy.context.evaluated_depsgraph_get()
def hit(origin, direction, obj):
    ok, loc, nor, idx = obj.ray_cast(obj.matrix_world.inverted() @ V(*origin), V(*direction))
    return (obj.matrix_world @ loc, nor) if ok else (None, None)
badge_at, bn = hit((.02, -.6, 1.25), (0, 1, 0), shirt)
badge = L.box('Walker badge', badge_at + V(0, -.012, 0), (.026, .0025, .036), C, rot=(-.25, 0, .12), bevel=.002)
clip = L.box('Walker badgeclip', badge_at + V(.002, -.014, .04), (.008, .003, .008), C, bevel=.001)
neckpts = []
for k in range(13):
    a = k / 12 * math.pi
    neckpts.append(V(math.cos(a) * .065, -.11 + math.sin(a) * .06, 1.45 - math.sin(a) * .012))
lan1 = L.tube('Walker lanyard1', [neckpts[0], V(.05, -.17, 1.37), V(.02, -.19, 1.30), badge_at + V(.002, -.014, .045)], .003, C, sides=4)
lan2 = L.tube('Walker lanyard2', [neckpts[-1], V(-.03, -.18, 1.37), V(0, -.19, 1.30), badge_at + V(.002, -.014, .045)], .003, C, sides=4)
lan3 = L.tube('Walker lanyard3', [neckpts[0] + V(0, .0, 0)] + [V(p.x, p.y + .07, p.z + .02) for p in neckpts[1:-1]] + [neckpts[-1]], .003, C, sides=4)
lanyard = L.join([lan1, lan2, lan3, clip], 'Walker lanyard')
wr = sk.p('aA1'); pa = sk.p('aA2'); dwr = (pa - wr).normalized()
bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=False, segments=32, radius1=.031, radius2=.031, depth=.018)
watch = L.mesh_obj('Walker watch', bm, C); so = watch.modifiers.new('s', 'SOLIDIFY'); so.thickness = .004
watch.location = wr - dwr * .03; watch.rotation_euler = dwr.to_track_quat('Z', 'Y').to_euler(); watch.scale = (1, .75, 1)
face = L.blob('Walker watchface', wr - dwr * .03 + V(0, 0, .024), (.016, .016, .005), C)


# ================================================================== wound rim: torn flesh lips around the hole
rim_pts = []
for k in range(25):
    a = k / 24 * 2 * math.pi
    r = .046 + .01 * noise.noise(V(math.cos(a), math.sin(a), 0) * 3)
    q = WC + V(math.cos(a) * r * .55, -math.sin(a) * r * .55 * .3, math.sin(a) * r * 1.1)
    ok, loc, nor, _ = body.ray_cast(q + V(.1, -.4, 0) * .0 + V(0, -.3, 0), V(0, 1, 0))
    rim_pts.append(loc if ok else q)
rim = L.tube('Walker woundrim', rim_pts, [.006 + .003 * abs(math.sin(k * 1.7)) for k in range(25)], C, sides=8, cap=False)

# ================================================================== masks (r = blood, g = dark, b = dirt) painted per vertex
bpy.context.view_layer.update()
hinv = hd.matrix_world.inverted()
def g3(p, c, r): return math.exp(-((p - c).length_squared) / (r * r))
def m_body(p, n):
    bl = L.sm(.085, .045, (p - WC).length) + L.sm(.5, .8, L.fbm(p, 6)) * .5
    return (min(1, bl), 0, L.sm(.4, .9, L.fbm(p + V(3, 3, 3), 5)))
def m_head(p, n):
    q = hinv @ p
    sock = max(g3(q, V(.032, -.07, .013), .022), g3(q, V(-.032, -.07, .013), .022))
    mouth = math.exp(-(((q.x / .042) ** 2) + ((q.z + .056) / .022) ** 2))
    drip = sum(g3(V(q.x, 0, 0), V(x0, 0, 0), .006) * L.sm(-.04, -.1, q.z) * L.sm(-.03, -.08, q.y) for x0 in (-.022, -.004, .015, .03))
    nose = (q.x > .002) * g3(q, V(.008, -.096, -.012), .012)
    return (min(1, mouth * 1.2 + drip * .9), min(1, sock * .9 + nose), L.sm(.5, .9, L.fbm(p, 8)) * .6)
def m_shirt(p, n):
    bl = L.sm(.13, .07, (p - WC).length) + L.sm(.028, .01, abs(p.x - .01 - .02 * math.sin(p.z * 30))) * L.sm(1.0, 1.42, p.z) * (p.y < -.1)
    return (min(1, bl), 0, L.sm(1.0, .87, p.z))
def m_pants(p, n): return (0, 0, 0)
def paint_mask(o, fn):
    me = o.data
    ca = me.color_attributes.new('Mask', 'FLOAT_COLOR', 'POINT')
    mw = o.matrix_world; nm = mw.to_3x3()
    for v in me.vertices:
        c = fn(mw @ v.co, (nm @ v.normal).normalized()); ca.data[v.index].color = (*c, 1)
import mats as M
def with_mask(mat, blood='#4a080c', dark='#24161c', dirt='#3a2f24'):
    nt = mat.node_tree; b = nt.nodes['Principled BSDF']
    src = b.inputs['Base Color'].links[0].from_socket
    vc = nt.nodes.new('ShaderNodeVertexColor'); vc.layer_name = 'Mask'
    sp = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(vc.outputs['Color'], sp.inputs[0])
    out = src
    for ch, col in (('Blue', dirt), ('Green', dark), ('Red', blood)):
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'
        nt.links.new(sp.outputs[ch], mx.inputs[0]); nt.links.new(out, mx.inputs[6]); mx.inputs[7].default_value = (*L.lin(col), 1)
        out = mx.outputs[2]
    nt.links.new(out, b.inputs['Base Color'])
    return mat
paint_mask(body, m_body); paint_mask(hd, m_head); paint_mask(shirt, m_shirt)

# ================================================================== materials
m_skin = with_mask(M.zombie_skin('Walker_Skin'))
m_head = with_mask(M.zombie_skin('Walker_HeadSkin'))
m_shirt = with_mask(M.flannel('Walker_Flannel', scale=9))
m_jeans = M.denim('Walker_Denim')
m_shoe = M.canvas('Walker_Canvas'); m_sole = M.rubber('Walker_Sole'); m_lace = M.flat('Walker_Lace', '#bdb8a8', .8)
L.setmat(body, m_skin); L.setmat(hd, m_head)
for e in ears: L.setmat(e, m_head)
L.setmat(gum, M.gore('Walker_Gum'))
L.setmat(shirt, m_shirt); L.setmat(pants, m_jeans)
for sh, so_, lc in (shoeA, shoeB): L.setmat(sh, m_shoe); L.setmat(so_, m_sole); L.setmat(lc, m_lace)
L.setmat(up, M.teeth_m('Walker_Teeth')); L.setmat(lo, up.data.materials[0])
for e in eyes: L.setmat(e, M.eye_m('Walker_Eye', glow=.35))
L.setmat(mouth_in, M.gore('Walker_Mouth')); L.setmat(cav, mouth_in.data.materials[0]); L.setmat(rim, M.gore('Walker_Rim'))
L.setmat(ribs, M.bone('Walker_Bone'))
L.setmat(belt, M.leather('Walker_Belt')); L.setmat(buckle, M.metal('Walker_Metal'))
L.setmat(badge, M.flat('Walker_Badge', '#e9e4d6', .3)); L.setmat(lanyard, M.flat('Walker_Lanyard', '#2f6fa8', .7))
L.setmat(watch, buckle.data.materials[0]); L.setmat(face, M.flat('Walker_Glass', '#9fb7c4', .05))
hr = A.hair('Walker hair', C, hd, density=2.2, length=(.008, .022), r=.0011, mask=lambda p: L.sm(-.15, .15, L.fbm(p, 30)), color_mat=M.flat('Walker_Hair', '#1f1a18', .6))

# ================================================================== ink hulls
for o in [body, hd, shirt, pants, shoeA[0], shoeA[1], shoeB[0], shoeB[1], belt]:
    L.hull(o, C, t=.0035 if o is not hd else .0022)

# ================================================================== render
L.studio(sc)
VIEWS = os.environ.get('VIEWS', 'hero')
shots = {'hero': [('front34', 32, 8, 3.0, .92, 50), ('side', 90, 4, 3.0, .92, 50), ('back34', 200, 10, 3.0, .92, 50), ('face', 22, 4, .62, 1.56, 70)],
         'detail': [('face', 22, 4, .62, 1.56, 70), ('wound', 40, 5, .7, 1.2, 70), ('feet', 30, 15, .9, .15, 60), ('hand', 60, 10, .6, 1.25, 70)]}[VIEWS]
SAMP = int(os.environ.get('SAMP', '40')); RES = float(os.environ.get('RES', '1'))
for nm, az, el, d, tz, lens in shots:
    L.camera(sc, (0, -.1, tz), d, az, el, lens=lens)
    L.render(sc, f'{OUT}/{nm}.png', w=int(1080 * RES), h=int(1350 * RES), samples=SAMP)
bpy.ops.wm.save_as_mainfile(filepath=f'{OUT}/walker.blend')
