"""Render passes for the reel.
usage: python3 render.py OUTDIR [GLB|-] [start end]
passes: col (full car), nrm (normals, full car), xcol (body hidden: engine cutaway)
"""
import bpy, sys, math, os
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T

args = sys.argv[1:]
OUT = args[0]
GLB = args[1] if len(args) > 1 and args[1] != "-" else None
START, END = (int(args[2]), int(args[3])) if len(args) > 3 else (0, T.N - 1)
W, H = 540, 960
for p in ("col", "nrm", "xcol"): os.makedirs(f"{OUT}/{p}", exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def lin(hexc): return [((int(hexc[i:i+2], 16) / 255) ** 2.2) for i in (0, 2, 4)] + [1]

def mat(name, hexc, emit=0, rough=.45, metal=0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(hexc)
    b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = lin(hexc)
        b.inputs["Emission Strength"].default_value = emit
    return m

def box(name, loc, scale, m, bevel=0.0, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.object
    o.name = name; o.scale = scale; o.data.materials.append(m)
    if bevel:
        bv = o.modifiers.new("b", "BEVEL"); bv.width = bevel; bv.segments = 2
    if parent: o.parent = parent
    return o

def cyl(name, loc, r, d, m, rot=(0, 0, 0), verts=24):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.object; o.name = name; o.data.materials.append(m); return o

# ---------------------------------------------------------------- car
CAR = []          # body meshes (hidden in cutaway)
WHEELS = []       # (object, axis) spun by distance

def placeholder():
    body = mat("Paint", "1c1e27", rough=.3, metal=.4); glass = mat("Glass", "3a4a6e", rough=.1)
    rub = mat("Rubber", "16161a", rough=.8); rim = mat("Chrome", "c0c6d0", rough=.2, metal=1)
    CAR.append(box("Body", (0, 0, .62), (4.4, 1.8, .55), body, .12))
    CAR.append(box("Cabin", (-.3, 0, 1.1), (2.0, 1.45, .45), glass, .18))
    CAR.append(box("ScannerBar", (2.21, 0, .55), (.05, 1.1, .07), mat("ScanDark", "300806", 2)))
    for i, (x, y) in enumerate([(1.4, .92), (1.4, -.92), (-1.45, .92), (-1.45, -.92)]):
        w = cyl(f"Wheel{i}", (x, y, .38), .38, .34, rub, rot=(math.pi / 2, 0, 0), verts=32)
        r = cyl(f"Rim{i}", (0, 0, 0), .25, .36, rim, verts=6); r.parent = w
        WHEELS.append(w)

before = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath=GLB)
new = [o for o in bpy.data.objects if o not in before]
bpy.context.view_layer.update()

def top_group(o):
    while o.parent is not None: o = o.parent
    return o.name

def in_wheel(o):
    p = o
    while p is not None:
        if "wheel assembly" in p.name.lower() or "wheel spacer" in p.name.lower() or "spacer stud" in p.name.lower(): return True
        p = p.parent
    return False

HULLS = [o for o in new if o.type == "MESH" and o.name.endswith("hull")]
for o in HULLS: o.hide_render = True
# hulls are inverted-hull outlines for real-time viewers; our stylizer draws its own ink
ENG_KEEP_HIDE = ("cylinder head", "crankcase", "engine side mount", "radiator", "intake plenum", "fin")
XRAY_KEEP = []; CUTAWAY = []   # CUTAWAY: engine casings shown as see-through shells in x-ray
for o in new:
    if o.type != "MESH" or o in HULLS: continue
    g = top_group(o)
    if in_wheel(o): WHEELS.append(o); continue
    if g.startswith("NT 10"):
        if any(k in o.name.lower() for k in ENG_KEEP_HIDE): CUTAWAY.append(o)
        else: XRAY_KEEP.append(o)
        continue
    if g.startswith("NT 01"):
        if any(k in o.name.lower() for k in ("coilover", "damper", "spring", "antiroll")): XRAY_KEEP.append(o)
        else: CAR.append(o)
        continue
    CAR.append(o)

# car: length along -Y (front) in file. Root rotates it so front points +X, scales to 4.4 m.
meshes = [o for o in new if o.type == "MESH" and o not in HULLS]
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
mn = Vector([min(p[i] for p in pts) for i in range(3)]); mx = Vector([max(p[i] for p in pts) for i in range(3)])
root = bpy.data.objects.new("CarRoot", None); sc.collection.objects.link(root)
for o in new:
    if o.parent is None: o.parent = root
k = 4.4 / (mx.y - mn.y)
root.scale = (k, k, k); root.rotation_euler = (0, 0, math.pi / 2)
cy = (mn.y + mx.y) / 2; cx = (mn.x + mx.x) / 2
root.location = (cy * k, -cx * k, -mn.z * k)
ROOT0 = root.location.copy()
bpy.context.view_layer.update()

# wheel pivots (spin about native X = axle)
PIVOTS = []
for a in [o for o in new if o.name.lower().endswith("wheel assembly")]:
    ms = [d for d in a.children_recursive if d.type == "MESH"]
    wp = [d.matrix_world @ Vector(c) for d in ms for c in d.bound_box]
    cw = sum(wp, Vector()) / len(wp)
    pv = bpy.data.objects.new("Pivot_" + a.name, None); sc.collection.objects.link(pv)
    pv.parent = root; pv.matrix_world = __import__("mathutils").Matrix.Translation(cw) @ root.matrix_world.to_3x3().to_4x4()
    bpy.context.view_layer.update()
    mw = a.matrix_world.copy(); a.parent = pv; a.matrix_world = mw
    PIVOTS.append(pv)
WHEEL_R = 0.0
for pv in PIVOTS: WHEEL_R = max(WHEEL_R, pv.matrix_world.translation.z)

# roof LED scanner: 15 columns x 3 rows, one emission material per column
LEDS = [o for o in new if "individual roof led diode" in o.name.lower() and not o.name.endswith(("hull", "ink"))]
xs = sorted(set(round((o.matrix_world.translation.y), 3) for o in LEDS))
LED_COLS = []
for i, xv in enumerate(xs):
    m = mat(f"LED{i}", "ff3a2a", emit=0)
    for o in LEDS:
        if abs(round(o.matrix_world.translation.y, 3) - xv) < 1e-3:
            o.data = o.data.copy(); o.data.materials.clear(); o.data.materials.append(m)
    LED_COLS.append(m)

# ---------------------------------------------------------------- V6 internals (native coords, parented to root)
YS = [-2.125, -1.74, -1.338]          # cylinder stations along the crank (front -> back)
CZ = 0.60                              # crank axis height
R, L = 0.05, 0.21                      # throw, rod length
DH = 0.37                              # head face distance from crank axis
BANK = {+1: Vector((0.31, 0, 0.836 - CZ)).normalized(), -1: Vector((-0.31, 0, 0.836 - CZ)).normalized()}
CYLS = {}                              # cyl number -> (y, side)
for i, y in enumerate(YS): CYLS[i + 1] = (y, +1); CYLS[i + 4] = (y, -1)
# see-through shell: front faces transparent, inside (back faces) solid -> instant cutaway from any angle
CUTM = bpy.data.materials.new("Cutaway"); CUTM.use_nodes = True
_n = CUTM.node_tree.nodes; _l = CUTM.node_tree.links
_b = _n["Principled BSDF"]; _b.inputs["Base Color"].default_value = lin("5a5a78"); _b.inputs["Roughness"].default_value = .45
_b.inputs["Metallic"].default_value = .5
_g = _n.new("ShaderNodeNewGeometry"); _t = _n.new("ShaderNodeBsdfTransparent"); _m = _n.new("ShaderNodeMixShader")
_l.new(_g.outputs["Backfacing"], _m.inputs[0]); _l.new(_t.outputs[0], _m.inputs[1]); _l.new(_b.outputs[0], _m.inputs[2])
_l.new(_m.outputs[0], _n["Material Output"].inputs[0])
for o in CUTAWAY:
    o["orig_mats"] = [m.name if m else "" for m in o.data.materials]
def cutaway(on):
    for o in CUTAWAY:
        for i in range(len(o.data.materials)):
            o.data.materials[i] = CUTM if on else bpy.data.materials.get(o["orig_mats"][i])
m_pist = mat("Piston", "e6e8ee", rough=.25, metal=1); m_rod = mat("Rod", "ffc23a", rough=.35, metal=.6)
m_crank = mat("Crank", "ff8a2a", rough=.35, metal=.6); m_liner = mat("Liner", "48506a", rough=.5)
ENG = []
def nat(o, loc, rot=None, scale=None):
    o.parent = root; o.location = loc
    if rot is not None: o.rotation_euler = rot
    if scale is not None: o.scale = scale
    ENG.append(o); return o
nat(cyl("CrankShaft", (0, 0, 0), .03, 1.25, m_crank, verts=14), (0, -1.73, CZ), rot=(math.pi / 2, 0, 0))
PIST, ROD, PIN, GAS, PLUG, WEB = {}, {}, {}, {}, {}, {}
VALVES, FLAME = {}, {}
m_ring = mat("Ring", "2a2a34", rough=.4, metal=.8); m_vin = mat("ValveIn", "50d8ff", rough=.3, metal=.7)
m_vex = mat("ValveEx", "ff5a3a", rough=.3, metal=.7)
gas_mats = {}; plug_mats = {}
for c, (y, s) in CYLS.items():
    u = BANK[s]; q = Vector((0, 0, 1)).rotation_difference(u).to_euler()
    yoff = y + (0.045 if s > 0 else -0.045)
    nat(cyl(f"Liner{c}", (0, 0, 0), .118, .2, m_liner, verts=28), Vector((0, yoff, CZ)) + u * .2, rot=q)
    PIST[c] = nat(cyl(f"Piston{c}", (0, 0, 0), .105, .15, m_pist, verts=24), (0, yoff, CZ), rot=q)
    PIN[c] = nat(cyl(f"Pin{c}", (0, 0, 0), .028, .05, m_crank, verts=12), (0, yoff, CZ), rot=(math.pi / 2, 0, 0))
    ROD[c] = nat(cyl(f"Rod{c}", (0, 0, 0), .022, 1.0, m_rod, verts=10), (0, yoff, CZ))
    WEB[c] = nat(box(f"Web{c}", (0, 0, 0), (.035, .03, 1), m_crank), (0, yoff, CZ))
    gm = mat(f"Gas{c}", "60e0f0", emit=2); gas_mats[c] = gm
    gm.node_tree.nodes["Principled BSDF"].inputs["Alpha"].default_value = .5     # see valves + flame through the charge
    GAS[c] = nat(cyl(f"Gas{c}", (0, 0, 0), .104, 1.0, gm, verts=24), (0, yoff, CZ), rot=q)
    pm = mat(f"Plug{c}", "ffe070", emit=0); plug_mats[c] = pm
    PLUG[c] = nat(box(f"Plug{c}", (0, 0, 0), (.03, .03, .07), pm), Vector((0, yoff, CZ)) + u * (DH + .04), rot=q)
    # piston rings (dark bands near the crown) and a domed crown
    for k_, zo in enumerate((.055, .038, .021)):
        rg = cyl(f"Ring{c}_{k_}", (0, 0, 0), .1075, .007, m_ring, verts=24); rg.parent = PIST[c]; rg.location = (0, 0, zo); ENG.append(rg)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.1, segments=20, ring_count=10); cr = bpy.context.object; cr.name = f"Crown{c}"
    cr.data.materials.append(m_pist); cr.parent = PIST[c]; cr.location = (0, 0, .075); cr.scale = (1.04, 1.04, .12); ENG.append(cr)
    # two valves per cylinder (intake = cyan, exhaust = red), lifted by their strokes
    for nm_, off, vm_ in (("In", .045, m_vin), ("Ex", -.045, m_vex)):
        vh = cyl(f"Valve{nm_}{c}", (0, 0, 0), .032, .008, vm_, verts=16); vs_ = cyl(f"Stem{nm_}{c}", (0, 0, 0), .006, .09, m_ring, verts=6)
        vs_.parent = vh; vs_.location = (0, 0, .045)
        nat(vh, (0, 0, 0), rot=q); ENG.append(vs_); VALVES[(c, nm_)] = (vh, off)
    # flame kernel that grows from the plug at ignition
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1, subdivisions=2); fk = bpy.context.object; fk.name = f"Flame{c}"
    fm = mat(f"FlameM{c}", "fff2b0", emit=40); fk.data.materials.append(fm); FLAME[c] = nat(fk, (0, 0, 0))


ENG = [o for o in ENG if not o.name.startswith("Flame")]
for _f in FLAME.values(): _f["nocut"] = 1.0
def q_of(u): return Vector((0, 0, 1)).rotation_difference(u).to_euler()
GAS_COL = {0: ("3ab8ff", 1.2), 1: ("7ae0ff", 2.0), 2: ("ff6a20", 8), 3: ("6a6a78", .4)}
def setc(m, hexc, e):
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(hexc); b.inputs["Emission Color"].default_value = lin(hexc)
    b.inputs["Emission Strength"].default_value = e

def pose_engine(f):
    a = T.crank(f)
    for c, (y, s) in CYLS.items():
        u = BANK[s]; yoff = y + (0.045 if s > 0 else -0.045)
        ang_u = math.atan2(u.z, u.x)
        # pin is aligned with the bank axis (TDC) when the crank reaches this cylinder's firing angle
        th = ang_u + math.radians(a - T.FIRE[c])
        p = Vector((R * math.cos(th), 0, R * math.sin(th)))
        along = p.dot(u); perp = (p - u * along).length
        sdist = along + math.sqrt(L * L - perp * perp)
        C0 = Vector((0, yoff, CZ)); pin = C0 + p; wp = C0 + u * sdist
        PIN[c].location = pin
        PIST[c].location = wp + u * .005
        d = wp - pin; ROD[c].location = (pin + wp) / 2; ROD[c].scale = (1, 1, d.length)
        ROD[c].rotation_euler = Vector((0, 0, 1)).rotation_difference(d).to_euler()
        WEB[c].location = C0 + p / 2; WEB[c].scale = (.06, .045, R + .07)
        WEB[c].rotation_euler = Vector((0, 0, 1)).rotation_difference(Vector((p.x, 0, p.z))).to_euler()
        crown = sdist + .08; gh = max(.008, DH - crown)
        GAS[c].location = C0 + u * (crown + gh / 2); GAS[c].scale = (1, 1, gh)
        st = T.stroke(c, f); hexc, e = GAS_COL[st]
        cc = (a - T.FIRE[c]) % 720
        if st == 2: e = 2.5 + 12 * max(0, 1 - cc / 120)
        setc(gas_mats[c], hexc, e)
        setc(plug_mats[c], "fff0a0", 30 if (cc < 25 or cc > 712) else 0)
        side = Vector((0, 1, 0))
        for nm_ in ("In", "Ex"):
            vh, off = VALVES[(c, nm_)]
            lo_, hi_ = (360, 540) if nm_ == "In" else (180, 360)
            lift = .028 * math.sin(math.pi * (cc - lo_) / (hi_ - lo_)) if lo_ <= cc < hi_ else 0.0
            vh.location = C0 + u * (DH - .004 - lift) + side * off
        fr_ = FLAME[c]
        if cc < 70:
            r_ = .015 + .085 * min(1, cc / 30); fr_.hide_render = False
            fr_.location = C0 + u * (DH - r_ * .6); fr_.scale = (r_, r_, r_ * .7)
            fr_.rotation_euler = q_of(u)
            setc(fr_.data.materials[0], "fff2b0" if cc < 25 else "ffb040", 40 * max(.15, 1 - cc / 70))
        else:
            fr_.hide_render = True

def pose_scanner(tau):
    """tau: scene time in seconds (slows down with the speed ramp)."""
    n = len(LED_COLS)
    ph = (tau / 1.3) % 2; pos = ph if ph < 1 else 2 - ph; pos *= (n - 1)
    for i, m in enumerate(LED_COLS):
        d = abs(i - pos); e = 18 * math.exp(-d * d / 1.2)
        setc(m, "ff3a2a", e + 0.3)

# ---------------------------------------------------------------- road + world (night street)
def node_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links

# wet asphalt: noise-driven roughness -> puddle reflections of the neon and lamps
road, n, l = node_mat("WetAsphalt")
b = n["Principled BSDF"]; b.inputs["Base Color"].default_value = lin("1c1a28")
tc_ = n.new("ShaderNodeTexCoord"); nz = n.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = .35
nz.inputs["Detail"].default_value = 4
ramp = n.new("ShaderNodeValToRGB"); ramp.color_ramp.elements[0].position = .45; ramp.color_ramp.elements[1].position = .6
ramp.color_ramp.elements[0].color = (.06, .06, .06, 1); ramp.color_ramp.elements[1].color = (.55, .55, .55, 1)
l.new(tc_.outputs["Object"], nz.inputs["Vector"]); l.new(nz.outputs["Fac"], ramp.inputs["Fac"]); l.new(ramp.outputs["Color"], b.inputs["Roughness"])
bpy.ops.mesh.primitive_plane_add(size=1); g = bpy.context.object; g.scale = (400, 60, 1); g.data.materials.append(road); g.name = "Ground"
ROAD_TEX = g   # scrolled with distance so puddles slide past
dash_m = mat("Dash", "e8dcc0", emit=.35)
DASH = [box(f"Dash{i}", (0, -2.0, .004), (1.6, .12, .008), dash_m) for i in range(16)]
curb_m = mat("Curb", "3a3550", rough=.6); edge_m = mat("CurbEdge", "d8c8a8", emit=.15)
for s_ in (-1, 1):
    box(f"Curb{s_}", (0, s_ * 4.2, .07), (400, .35, .14), curb_m)
    box(f"CurbLine{s_}", (0, s_ * 3.85, .004), (400, .1, .008), edge_m)

# street lamps with real lights: their pools sweep over the car at speed
POSTS = []
lamp_m = mat("Lamp", "ffb060", emit=14); post_m = mat("Post", "2a2640", rough=.5, metal=.6)
for i in range(6):
    side = 1 if i % 2 == 0 else -1
    p = box(f"Post{i}", (0, side * 4.7, 2.4), (.14, .14, 4.8), post_m)
    arm = box(f"Arm{i}", (0, 0, 0), (.08, 1.6 / .14, .08 / 4.8), post_m); arm.parent = p; arm.location = (0, -side * .8 / .14, .5)
    head = box(f"LampHead{i}", (0, 0, 0), (.5 / .14, .9 / .14, .08 / 4.8), lamp_m); head.parent = p; head.location = (0, -side * 1.5 / .14, .48)
    ld = bpy.data.lights.new(f"Lamp{i}", "SPOT"); ld.energy = 2600; ld.color = (1, .62, .32); ld.spot_size = math.radians(110)
    ld.spot_blend = .6; ld.shadow_soft_size = .4
    lo = bpy.data.objects.new(f"LampL{i}", ld); sc.collection.objects.link(lo); lo.parent = p
    lo.location = (0, -side * 1.5 / .14, .45); lo.rotation_euler = (0, 0, 0)
    POSTS.append(p)

# skyline: two scrolling rows of towers with lit windows
win, n, l = node_mat("Windows")
b = n["Principled BSDF"]; b.inputs["Base Color"].default_value = lin("15122a"); b.inputs["Roughness"].default_value = .8
tc_ = n.new("ShaderNodeTexCoord"); br = n.new("ShaderNodeTexBrick")
br.inputs["Scale"].default_value = 1.0; br.inputs["Mortar Size"].default_value = .35
br.inputs["Color1"].default_value = (1, .7, .35, 1); br.inputs["Color2"].default_value = (.25, .6, 1, 1)
br.inputs["Mortar"].default_value = (0, 0, 0, 1); br.offset = 0; br.squash = 1
mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1.4, 1.4, 2.2)
rnd = n.new("ShaderNodeTexNoise"); rnd.inputs["Scale"].default_value = 3.0
mul = n.new("ShaderNodeMixRGB"); mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1
thr = n.new("ShaderNodeValToRGB"); thr.color_ramp.elements[0].position = .52; thr.color_ramp.elements[1].position = .56
l.new(tc_.outputs["Object"], mp.inputs["Vector"]); l.new(mp.outputs["Vector"], br.inputs["Vector"])
l.new(mp.outputs["Vector"], rnd.inputs["Vector"]); l.new(rnd.outputs["Fac"], thr.inputs["Fac"])
l.new(br.outputs["Color"], mul.inputs[1]); l.new(thr.outputs["Color"], mul.inputs[2])
l.new(mul.outputs["Color"], b.inputs["Emission Color"]); b.inputs["Emission Strength"].default_value = 3.0
TOWERS = []
r_ = __import__("random").Random(4)
for side in (-1, 1):
    x = -90.0
    while x < 90:
        w_ = r_.uniform(5, 11); h_ = r_.uniform(10, 38); dpt = r_.uniform(6, 10)
        t_ = box(f"Tower", (x, side * r_.uniform(22, 30), h_ / 2), (w_, dpt, h_), win)
        t_["x0"] = x; TOWERS.append(t_); x += w_ + r_.uniform(1, 4)

# sky: navy zenith -> magenta horizon glow (camera rays only, soft fill for lighting)
sc.world = bpy.data.worlds.new("W"); sc.world.use_nodes = True
wn = sc.world.node_tree.nodes; wl = sc.world.node_tree.links
bgn = wn["Background"]; bgn.inputs[1].default_value = 1.0
tcw = wn.new("ShaderNodeTexCoord"); sep = wn.new("ShaderNodeSeparateXYZ"); rp = wn.new("ShaderNodeValToRGB")
rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = lin("5a2a6a")
rp.color_ramp.elements[1].position = 0.35; rp.color_ramp.elements[1].color = lin("0e0c22")
wl.new(tcw.outputs["Generated"], sep.inputs[0]); wl.new(sep.outputs["Z"], rp.inputs["Fac"]); wl.new(rp.outputs["Color"], bgn.inputs[0])
for loc, e, col in [((5, -6, 7), 900, (1, .82, .66)), ((-6, 5, 5), 600, (.45, .5, 1)), ((0, 0, 8), 200, (1, 1, 1)),
                    ((-5, 3, 2.5), 1300, (.3, .9, 1.0)), ((4, 5, 1.5), 600, (1, .3, .6))]:
    ld = bpy.data.lights.new("L", "AREA"); ld.energy = e; ld.size = 5; ld.color = col
    lo = bpy.data.objects.new("L", ld); lo.location = loc; sc.collection.objects.link(lo)
    lo.rotation_euler = Vector((0, 0, 1)).rotation_difference(Vector(loc)).to_euler()

# ---------------------------------------------------------------- section cut (shader mask on every car material)
CG = bpy.data.node_groups.new("CutMask", "ShaderNodeTree")
CG.interface.new_socket("Mask", in_out="OUTPUT", socket_type="NodeSocketFloat")
CG.interface.new_socket("Section", in_out="OUTPUT", socket_type="NodeSocketFloat")
gn = CG.nodes; gl = CG.links
go = gn.new("NodeGroupOutput"); geo_ = gn.new("ShaderNodeNewGeometry"); sx = gn.new("ShaderNodeSeparateXYZ")
gl.new(geo_.outputs["Position"], sx.inputs[0])
CUTV = {}
for k_, v_ in dict(EN=0, X0=.5, X1=2.5, YC=0.0, ZH=.12, ZT=.42, MH=1, MT=0, MF=0, XF=1.2).items():
    vn = gn.new("ShaderNodeValue"); vn.outputs[0].default_value = v_; vn.label = k_; CUTV[k_] = vn
def M(op, a, b_):
    m_ = gn.new("ShaderNodeMath"); m_.operation = op
    for i_, x_ in enumerate((a, b_)):
        if isinstance(x_, (int, float)): m_.inputs[i_].default_value = x_
        else: gl.new(x_, m_.inputs[i_])
    return m_.outputs[0]
V_ = lambda k_: CUTV[k_].outputs[0]
inx = M("MULTIPLY", M("GREATER_THAN", sx.outputs["X"], V_("X0")), M("LESS_THAN", sx.outputs["X"], V_("X1")))
half = M("MULTIPLY", M("MULTIPLY", M("LESS_THAN", sx.outputs["Y"], V_("YC")), M("GREATER_THAN", sx.outputs["Z"], V_("ZH"))), V_("MH"))
top = M("MULTIPLY", M("GREATER_THAN", sx.outputs["Z"], V_("ZT")), V_("MT"))
att = gn.new("ShaderNodeAttribute"); att.attribute_type = "OBJECT"; att.attribute_name = "nocut"
keep = M("SUBTRACT", 1.0, att.outputs["Fac"])
inx = M("MULTIPLY", inx, keep)
front = M("MULTIPLY", M("MULTIPLY", M("GREATER_THAN", sx.outputs["X"], V_("XF")), M("GREATER_THAN", sx.outputs["Z"], V_("ZH"))), V_("MF"))
mask = M("MULTIPLY", M("MULTIPLY", inx, M("MAXIMUM", M("MAXIMUM", half, top), front)), V_("EN"))
gl.new(mask, go.inputs["Mask"])
gl.new(M("MULTIPLY", M("MULTIPLY", geo_.outputs["Backfacing"], inx), V_("EN")), go.inputs["Section"])


def add_cut(m):
    if m is None or m.get("cut") or not m.use_nodes: return
    nt_ = m.node_tree; out_ = [x for x in nt_.nodes if x.type == "OUTPUT_MATERIAL"]
    if not out_ or not out_[0].inputs["Surface"].links: return
    out_ = out_[0]; src = out_.inputs["Surface"].links[0].from_socket
    grp = nt_.nodes.new("ShaderNodeGroup"); grp.node_tree = CG
    em_ = nt_.nodes.new("ShaderNodeBsdfPrincipled"); em_.inputs["Base Color"].default_value = lin("c27080"); em_.inputs["Emission Color"].default_value = lin("c27080")
    em_.inputs["Emission Strength"].default_value = .35
    em_.inputs["Metallic"].default_value = .35; em_.inputs["Roughness"].default_value = .5
    tr = nt_.nodes.new("ShaderNodeBsdfTransparent")
    m1 = nt_.nodes.new("ShaderNodeMixShader"); m2 = nt_.nodes.new("ShaderNodeMixShader")
    nt_.links.new(grp.outputs["Section"], m1.inputs[0]); nt_.links.new(src, m1.inputs[1]); nt_.links.new(em_.outputs[0], m1.inputs[2])
    nt_.links.new(grp.outputs["Mask"], m2.inputs[0]); nt_.links.new(m1.outputs[0], m2.inputs[1]); nt_.links.new(tr.outputs[0], m2.inputs[2])
    nt_.links.new(m2.outputs[0], out_.inputs["Surface"])
    m["cut"] = 1
for o in CAR + CUTAWAY + XRAY_KEEP + [x for x in ENG if x.name.startswith("Liner")]:
    for m in o.data.materials: add_cut(m)
def set_cut(**kw):
    for k_, v_ in kw.items(): CUTV[k_].outputs[0].default_value = v_
sc.cycles.transparent_max_bounces = 32
for o in WHEELS + [x for x in ENG if not x.name.startswith("Liner")]: o["nocut"] = 1.0

# ---------------------------------------------------------------- camera
cd = bpy.data.cameras.new("C"); cam = bpy.data.objects.new("C", cd); sc.collection.objects.link(cam)
sc.camera = cam
tgt = bpy.data.objects.new("T", None); sc.collection.objects.link(tgt)
tc = cam.constraints.new("TRACK_TO"); tc.target = tgt

def sm(t): t = min(1, max(0, t)); return t * t * (3 - 2 * t)
def lerp(a, b, t): return a + (b - a) * t
def V(*a): return Vector(a)

# shot list: (f0, f1, pos0, pos1, tgt0, tgt1, lens0, lens1). Hard cuts between shots.
SHOTS = [
    (0,   58,  V(5.6, -4.1, 1.05), V(4.9, -3.5, .95), V(.45, 0, .55), V(.5, 0, .55), 34, 36),    # hook wide, slow push
    (58,  82,  V(2.5, -1.35, 1.55), V(2.0, -1.0, 1.35), V(1.0, 0, .5), V(1.02, 0, .44), 34, 40),  # punch-in on bonnet
    (82,  164, V(3.3, -.08, .66), V(3.1, -.05, .64), V(1.0, 0, .45), V(1.0, 0, .45), 70, 76),  # end-on: V cross-section
    (164, 245, V(.80, -.06, 2.05), V(.84, -.03, 1.95), V(1.04, 0, .38), V(1.04, 0, .38), 48, 52),  # top-down: firing order
    (245, 300, V(2.6, -1.2, 1.0), V(2.35, -1.45, 1.05), V(1.0, 0, .42), V(1.0, 0, .42), 52, 50), # 3/4 high orbit
    (300, 330, V(2.35, -1.45, 1.05), V(3.6, -3.2, 1.1), V(1.0, 0, .42), V(.4, 0, .6), 50, 30),    # pull out
    (330, 384, V(-4.2, -2.4, .55), V(-4.6, -2.0, .5), V(-.4, 0, .62), V(-.2, 0, .62), 28, 28),    # rear 3/4 low launch
]
def cam_at(f):
    for f0, f1, p0, p1, t0, t1, l0, l1 in SHOTS:
        if f0 <= f < f1:
            u = (f - f0) / (f1 - f0); u = sm(u) * .6 + u * .4
            return p0.lerp(p1, u), t0.lerp(t1, u), lerp(l0, l1, u)
    s = SHOTS[-1]; return s[3], s[5], s[7]

# distance travelled (m) for road / wheels, real speed 24 m/s
_dist = [0.0]; _tau = [0.0]
for i in range(T.N): _dist.append(_dist[-1] + 24.0 / T.FPS * T.speed(i)); _tau.append(_tau[-1] + T.speed(i) / T.FPS)

# ---------------------------------------------------------------- render setup
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.max_bounces = 6
if os.environ.get("THREADS"): sc.render.threads_mode = "FIXED"; sc.render.threads = int(os.environ["THREADS"])
sc.view_settings.view_transform = "Standard"

nm = bpy.data.materials.new("NRM"); nm.use_nodes = True
nt = nm.node_tree; nt.nodes.clear()
geo = nt.nodes.new("ShaderNodeNewGeometry"); vm = nt.nodes.new("ShaderNodeVectorMath"); vm.operation = "MULTIPLY_ADD"
vm.inputs[1].default_value = (.5, .5, .5); vm.inputs[2].default_value = (.5, .5, .5)
em = nt.nodes.new("ShaderNodeEmission"); out = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(geo.outputs["Normal"], vm.inputs[0]); nt.links.new(vm.outputs[0], em.inputs[0]); nt.links.new(em.outputs[0], out.inputs[0])
_g2 = nt.nodes.new("ShaderNodeGroup"); _g2.node_tree = CG; _tr2 = nt.nodes.new("ShaderNodeBsdfTransparent"); _mx2 = nt.nodes.new("ShaderNodeMixShader")
nt.links.new(_g2.outputs["Mask"], _mx2.inputs[0]); nt.links.new(em.outputs[0], _mx2.inputs[1]); nt.links.new(_tr2.outputs[0], _mx2.inputs[2])
nt.links.new(_mx2.outputs[0], out.inputs[0])

def set_vis(car, eng):
    for o in CAR: o.hide_render = not car
    for o in ENG: o.hide_render = not eng

def shot(path, samples, override=None, half=False):
    sc.render.resolution_percentage = 50 if half else 100
    sc.view_layers[0].material_override = override
    sc.cycles.samples = samples; sc.cycles.use_denoising = override is None
    sc.render.filepath = path; bpy.ops.render.render(write_still=True)

from bpy_extras.object_utils import world_to_camera_view
import json
PTS = {}
POINTS_ONLY = os.environ.get("POINTS_ONLY") == "1"
if os.environ.get("PREVIEW"):
    for j_, (f, pp, tt, ll, mode) in enumerate(json.load(open(os.environ["PREVIEW"]))):
        cam.location = V(*pp); tgt.location = V(*tt); cd.lens = ll
        d = _dist[f]; pose_engine(f); pose_scanner(_tau[f]); sc.frame_set(f)
        set_cut(EN=1, MH=1 if mode == "half" else 0, MT=1 if mode == "top" else 0, MF=1 if mode == "front" else 0)
        set_vis(True, True); shot(f"{OUT}/prev_{j_:02d}.png", 8, half=True)
    sys.exit(0)
FR = [int(x) for x in os.environ['FRAMES'].split(',')] if os.environ.get('FRAMES') else range(START, END + 1)
for f in FR:
    p, tl, lens = cam_at(f)
    # car motion: suspension chatter at real speed, launch away from the camera at the end
    rs = T.speed(f); ts = f / T.FPS
    bob = .006 * rs * math.sin(ts * 37) + .004 * rs * math.sin(ts * 23 + 1)
    lx = 0.0; pitch = 0.0
    if f >= T.F_END[0]:
        tl_ = (f - T.F_END[0]) / T.FPS; lx = .5 * 9.0 * tl_ * tl_; pitch = -.035 * math.exp(-tl_ * 2.5) * min(1, tl_ * 6)
        tl = tl + Vector((lx * .55, 0, 0))
    root.location = ROOT0 + Vector((lx, 0, bob)); root.rotation_euler = (pitch, 0, math.pi / 2)   # native X = lateral axis -> pitch
    # handheld drift on every shot (hand-operated feel), stronger at real speed
    p = p + Vector((.012 * math.sin(ts * 1.7), .01 * math.sin(ts * 2.3 + 2), .008 * math.sin(ts * 3.1) + .01 * rs * math.sin(ts * 29)))
    cam.location = p; tgt.location = tl; cd.lens = lens
    d = _dist[f]
    for i, dsh in enumerate(DASH): dsh.location.x = ((i * 3.0 - d) % 42) - 21
    for i, po in enumerate(POSTS): po.location.x = ((i * 12.0 - d) % 72) - 36
    for t_ in TOWERS: t_.location.x = ((t_["x0"] - d * .35 + 90) % 180) - 90
    ROAD_TEX.location.x = -(d % 100)
    for pv in PIVOTS: pv.rotation_euler.x = -d / max(.2, WHEEL_R)
    pose_engine(f); pose_scanner(_tau[f])
    sc.frame_set(f)
    bpy.context.view_layer.update()
    PTS[f] = {k: list(world_to_camera_view(sc, cam, o.matrix_world.translation))[:2] for k, o in
              [("piston", PIST[1]), ("rod", ROD[1]), ("crank", PIN[2]), ("plug", PLUG[1])] +
              [(f"cyl{i}", PLUG[i]) for i in range(1, 7)]}
    if POINTS_ONLY: continue
    xray = T.C_RAMP[0] <= f < T.E_RAMP[1]
    set_vis(True, False); set_cut(EN=0)
    if not (T.D_SLOW[0] <= f < T.E_RAMP[0]): shot(f"{OUT}/col/{f:04d}.png", 12 if f >= 58 else 10, half=f >= 58)
    if xray:
        topdown = 164 <= f < 245; frontcut = 82 <= f < 164
        set_cut(EN=1, MH=0 if (topdown or frontcut) else 1, MT=1 if topdown else 0, MF=1 if frontcut else 0)
        set_vis(True, True)
    shot(f"{OUT}/nrm/{f:04d}.png", 1, nm)
    if xray:
        shot(f"{OUT}/xcol/{f:04d}.png", 16, half=True)
        set_cut(EN=0)

json.dump(PTS, open(f"{OUT}/points_{START}_{END}.json", "w"))
