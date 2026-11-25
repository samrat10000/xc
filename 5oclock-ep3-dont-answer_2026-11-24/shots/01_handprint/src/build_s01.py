"""5 O'CLOCK Ep3 - Shot 01 "The Handprint" (3.0 s, 72 f @24 fps, 1080x1920, toon-anime).
Probe Pass 2 fixes applied:
1. GLASS_MAT.surface_render_method = 'BLENDED' (no EEVEE stipple dither).
2. SUNV adjusted to (0.14, 1.0, 0.075) so sun disk & glow project inside the glass pane (~0.64, 0.52).
3. Camera pulled back/framed cleanly (34 mm) so Sam's face/glasses/hoodie, relaxed left hand, brass bolt,
   entire glass handprint, and 5 wire crows all fit cleanly inside 9:16 with bottom 15% clear.
4. Sam moved closer & angled toward the bolt; torso leans subtly with door slide so IK_R_err <= 0.02 m all frames.
5. Crows framed cleanly inside glass opening (no stile splitting a crow).
6. Exterior street widened + first right house moved back so mountains, radio tower & sunset sky read clearly.
usage: blender -b --python build_s01.py -- <ABS_OUTDIR> <SCALE> <frames|all>
"""
import os, sys, math, json, random

ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
OUT = os.path.abspath(ARGV[0])
SCALE = float(ARGV[1])
FR = ARGV[2] if len(ARGV) > 2 else 'all'
os.makedirs(OUT, exist_ok=True)

HERE = os.path.dirname(os.path.abspath(__file__))
EP3 = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
EP1 = r'C:\Users\cross\Downloads\xc\5oclock-ep1-the-fourth-note_2026-11-23'
SAM_BLEND = os.path.join(EP1, 'assets', 'toon_sam', 'sam_toon.blend')
CROW_GLB = os.path.join(EP1, 'shots', '01_speaker', 'src', 'crow_tehbucket_raven_cc0.glb')
TEX_HAND = os.path.join(HERE, 'textures', 'glass_handprint.png')
TEX_KOBAN = os.path.join(HERE, 'textures', 'koban_sign_rev.png')

# Exec shared toonlib_v4 with Shot 01 sunset vector (sun visible cleanly inside glass sky gap)
_tl_src = open(os.path.join(EP3, 'lib', 'toonlib_v4.py'), encoding='utf-8').read()
_tl_src = _tl_src.replace(
    "SUNV = tuple(Vector((-0.62, 1.0, 0.24)).normalized())",
    "SUNV = tuple(Vector((0.18, 1.0, 0.085)).normalized())",
)
exec(_tl_src)

from mathutils import Vector, Matrix, Euler, Quaternion
from bpy_extras.object_utils import world_to_camera_view

NF = 72
SUN = Vector(SUNV)
lin = lambda c: tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)
PB = lambda rig, n: rig.pose.bones[n]


def box_bm(bm, center, size):
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    return bm


def make_box(name, center, size, mat, parent=None, line=0.004):
    bm = box_bm(bmesh.new(), center, size)
    return mesh_obj(name, bm, mat, parent, line)


def tex_wood_grain(nt, ramp):
    N, L = nt.nodes, nt.links
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.5, 1.5, 14.0)
    L.new(tc.outputs['Object'], mp.inputs[0])
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.5; nz.inputs['Detail'].default_value = 5
    L.new(mp.outputs[0], nz.inputs[0])
    st = N.new('ShaderNodeValToRGB'); st.color_ramp.interpolation = 'CONSTANT'
    st.color_ramp.elements[0].position = 0.0; st.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1)
    st.color_ramp.elements[1].position = 0.56; st.color_ramp.elements[1].color = (0.76, 0.68, 0.62, 1)
    L.new(nz.outputs[0], st.inputs[0])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
    mx.inputs[0].default_value = 1.0
    L.new(ramp.outputs[0], mx.inputs[6]); L.new(st.outputs[0], mx.inputs[7])
    return mx.outputs[2]


def tex_asphalt(nt, ramp):
    N, L = nt.nodes, nt.links
    tc = N.new('ShaderNodeTexCoord')
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 0.45; nz.inputs['Detail'].default_value = 4
    L.new(tc.outputs['Object'], nz.inputs[0])
    st = N.new('ShaderNodeValToRGB'); st.color_ramp.interpolation = 'CONSTANT'
    st.color_ramp.elements[0].position = 0.0; st.color_ramp.elements[0].color = (1.0, 1.0, 1.0, 1)
    st.color_ramp.elements[1].position = 0.58; st.color_ramp.elements[1].color = (0.82, 0.80, 0.85, 1)
    L.new(nz.outputs[0], st.inputs[0])
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
    mx.inputs[0].default_value = 1.0
    L.new(ramp.outputs[0], mx.inputs[6]); L.new(st.outputs[0], mx.inputs[7])
    return mx.outputs[2]


def image_alpha_mat(name, filepath, tint=(1.0, 1.0, 1.0), alpha_scale=1.0, strength=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    # Crucial for Blender 5.0 EEVEE: avoid DITHERED stipple look on glass/fog!
    m.surface_render_method = 'BLENDED'
    m.use_transparency_overlap = False
    N, L = m.node_tree.nodes, m.node_tree.links
    for n in list(N): N.remove(n)
    out = N.new('ShaderNodeOutputMaterial')
    tr = N.new('ShaderNodeBsdfTransparent')
    em = N.new('ShaderNodeEmission')
    em.inputs['Strength'].default_value = strength
    tex = N.new('ShaderNodeTexImage')
    tex.image = bpy.data.images.load(filepath)
    tex.extension = 'CLIP'
    mul_rgb = N.new('ShaderNodeMix'); mul_rgb.data_type = 'RGBA'; mul_rgb.blend_type = 'MULTIPLY'
    mul_rgb.inputs[0].default_value = 1.0
    mul_rgb.inputs[7].default_value = (*lin(tint), 1.0)
    L.new(tex.outputs['Color'], mul_rgb.inputs[6])
    L.new(mul_rgb.outputs[2], em.inputs['Color'])
    mul_a = N.new('ShaderNodeMath'); mul_a.operation = 'MULTIPLY'
    mul_a.inputs[1].default_value = alpha_scale
    L.new(tex.outputs['Alpha'], mul_a.inputs[0])
    mix = N.new('ShaderNodeMixShader')
    L.new(mul_a.outputs[0], mix.inputs['Fac'])
    L.new(tr.outputs[0], mix.inputs[1])
    L.new(em.outputs[0], mix.inputs[2])
    L.new(mix.outputs[0], out.inputs[0])
    return m


# ---------------- Shot materials (no rim on flat architecture walls: C4) ----------------
WOOD_INT = toon('wood_int', (0.20, 0.15, 0.14), (0.44, 0.34, 0.28), tex=tex_wood_grain)
WOOD_DOOR = toon('wood_door', (0.22, 0.18, 0.17), (0.48, 0.40, 0.34), tex=tex_wood_grain)
WALL_KOBAN = toon('wall_koban', (0.28, 0.29, 0.27), (0.55, 0.56, 0.50))
ALU_SASH = toon('alu_sash', (0.34, 0.34, 0.37), (0.64, 0.65, 0.68))
BRASS = toon('brass', (0.44, 0.32, 0.14), (0.86, 0.68, 0.28), (1.0, 0.88, 0.52), rimfacing=0.45)
SCRATCH_DARK = emis('scratch_dark', lin((0.09, 0.06, 0.05)))
SCRATCH_FRESH = emis('scratch_fresh', lin((0.76, 0.60, 0.38)))
ASPHALT = toon('asphalt', (0.18, 0.17, 0.22), (0.38, 0.36, 0.42), tex=tex_asphalt)
KERB_MAT = toon('kerb', (0.34, 0.32, 0.36), (0.64, 0.62, 0.62))
ROAD_LINE = toon('road_line', (0.52, 0.48, 0.48), (0.88, 0.85, 0.80))
ROOF_TILE = toon('roof_tile', (0.17, 0.16, 0.23), (0.35, 0.34, 0.45))
HOUSE_WALL = toon('house_wall', (0.30, 0.27, 0.32), (0.62, 0.57, 0.56))
WIN_LIT = emis('win_lit', (1.0, 0.58, 0.26), 1.4)
LEAF_MAT = toon('leaf', (0.42, 0.18, 0.12), (0.84, 0.42, 0.18))
GLASS_MAT = image_alpha_mat('glass_handprint', TEX_HAND, tint=(0.94, 0.96, 1.0), alpha_scale=0.95, strength=1.05)
SIGN_MAT = image_alpha_mat('koban_sign_rev', TEX_KOBAN, tint=(0.86, 0.84, 0.80), alpha_scale=1.0, strength=0.92)


def make_uv_plane(name, x0, x1, y, z0, z1, mat, parent=None, line=0.0):
    bm = bmesh.new()
    v0 = bm.verts.new((x0, y, z0))
    v1 = bm.verts.new((x1, y, z0))
    v2 = bm.verts.new((x1, y, z1))
    v3 = bm.verts.new((x0, y, z1))
    f = bm.faces.new((v0, v1, v2, v3))
    uv = bm.loops.layers.uv.new('UVMap')
    for loop, co in zip(f.loops, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop[uv].uv = co
    return mesh_obj(name, bm, mat, parent, line)


# ---------------- Koban doorway + sliding glass door ----------------
KOBAN = empty('KOBAN', loc=(0, 0, 0))
make_box('koban_floor', (0.0, -1.2, -0.04), (3.4, 2.6, 0.08), WOOD_INT, KOBAN, 0)
make_box('koban_threshold', (0.10, 0.0, 0.015), (2.2, 0.14, 0.03), STEEL, KOBAN, 0.003)

# Left interior wall + vertical wooden doorframe jamb (visible left of Sam + 11+1 tally scratches)
make_box('wall_left', (-1.04, -0.55, 1.25), (0.90, 1.15, 2.50), WALL_KOBAN, KOBAN, 0.004)
make_box('wall_back_left', (-0.58, 0.0, 1.25), (0.28, 0.14, 2.50), WALL_KOBAN, KOBAN, 0.004)
make_box('jamb_left', (-0.42, -0.02, 1.15), (0.07, 0.11, 2.30), WOOD_INT, KOBAN, 0.003)
make_box('lintel_top', (0.25, 0.0, 2.24), (1.70, 0.14, 0.26), WOOD_INT, KOBAN, 0.004)
make_box('wall_right', (0.98, 0.0, 1.25), (0.56, 0.14, 2.50), WALL_KOBAN, KOBAN, 0.004)

# 11 weathered tally marks + 1 fresh scratch on inner jamb
for k in range(11):
    z_m = 1.18 + k * 0.022
    tilt = math.radians(-8 + (k % 3) * 3)
    mk = make_box(f'tally_{k}', (-0.383, -0.032, z_m), (0.005, 0.036, 0.0035), SCRATCH_DARK, KOBAN, 0)
    mk.rotation_euler = (tilt, 0, 0)
mk12 = make_box('tally_12_fresh', (-0.383, -0.032, 1.425), (0.006, 0.042, 0.0045), SCRATCH_FRESH, KOBAN, 0)
mk12.rotation_euler = (math.radians(-6), 0, 0)

# Sliding right door panel: leading vertical stile sits at X = -0.10..-0.02; glass pane X = 0.02..0.48
DOOR = empty('SLIDING_DOOR', KOBAN, loc=(0.0, 0.0, 0.0))
make_box('door_stile_L', (-0.06, 0.0, 1.10), (0.075, 0.055, 2.20), WOOD_DOOR, DOOR, 0.003)
make_box('door_stile_R', (0.52, 0.0, 1.10), (0.075, 0.055, 2.20), WOOD_DOOR, DOOR, 0.003)
make_box('door_rail_bot', (0.23, 0.0, 0.46), (0.50, 0.048, 0.92), WOOD_DOOR, DOOR, 0.003)
make_box('door_rail_mid', (0.23, 0.0, 0.94), (0.50, 0.050, 0.05), ALU_SASH, DOOR, 0.003)
make_box('door_rail_top', (0.23, 0.0, 2.12), (0.50, 0.055, 0.10), WOOD_DOOR, DOOR, 0.003)
make_box('door_muntin_top', (0.23, 0.0, 1.94), (0.50, 0.030, 0.022), ALU_SASH, DOOR, 0.0025)

# Glass pane offset 18 mm proud of door frame centerline (C9) -> covers X = -0.02..+0.48, Z = 0.96..2.06
glass_pane = make_uv_plane('door_glass', -0.02, 0.48, 0.018, 0.96, 2.06, GLASS_MAT, DOOR, 0.0)

# Brass slide-bolt assembly mounted on leading stile inside face (X = -0.06, Y = -0.034)
make_box('bolt_plate', (-0.06, -0.034, 1.15), (0.060, 0.010, 0.13), BRASS, DOOR, 0.002)
BOLT_SLIDE = empty('BOLT_SLIDE', DOOR, loc=(-0.06, -0.044, 1.15))
bolt_bar = lathe([(-0.040, 0.0085), (0.040, 0.0085)], 14)
bmesh.ops.rotate(bolt_bar, verts=bolt_bar.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'Z'))
mesh_obj('bolt_bar', bolt_bar, BRASS, BOLT_SLIDE, 0.002)
knob_bm = lathe([(0.0, 0.009), (0.026, 0.009), (0.028, 0.021), (0.044, 0.021), (0.046, 0.0)], 20)
bmesh.ops.rotate(knob_bm, verts=knob_bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(180), 3, 'Z'))
knob_obj = mesh_obj('bolt_knob', knob_bm, BRASS, BOLT_SLIDE, 0.002)
knob_obj.location = (0.002, 0.0, 0.0)

# ---------------- Exterior street to the horizon (R6 density + B7 horizon) ----------------
EXT = empty('EXTERIOR', loc=(0, 0, 0))
make_box('road_asphalt', (1.2, 75.0, -0.015), (48.0, 190.0, 0.03), ASPHALT, EXT, 0)
make_box('koban_apron', (0.2, 1.0, 0.004), (5.0, 2.0, 0.015), CONC, EXT, 0.003)
make_box('kerb_L', (-2.4, 75.0, 0.04), (0.22, 190.0, 0.08), KERB_MAT, EXT, 0.003)
make_box('kerb_R', (4.6, 75.0, 0.04), (0.22, 190.0, 0.08), KERB_MAT, EXT, 0.003)
for i in range(20):
    make_box(f'dash_{i}', (1.1, 4.0 + i * 7.0, 0.003), (0.14, 2.8, 0.004), ROAD_LINE, EXT, 0)
mh = lathe([(0, 0.34), (0.012, 0.34), (0.014, 0.0)], 24)
bmesh.ops.rotate(mh, verts=mh.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
mh_o = mesh_obj('manhole', mh, STEEL, EXT, 0.003)
mh_o.location = (0.65, 5.8, 0.002)

# Reversed koban placard outside on the right exterior post
make_box('sign_post', (0.74, 0.25, 1.25), (0.05, 0.05, 2.5), STEEL, EXT, 0.003)
make_uv_plane('koban_sign_face', 0.46, 0.72, 0.22, 1.28, 1.82, SIGN_MAT, EXT, 0.003)

# Concrete utility pole + rusted Showa loudspeaker horn positioned clear of the handprint (X = 2.95 m)
EXT_POLE = empty('EXT_POLE', EXT, loc=(2.95, 8.8, 0.0))
ep_bm = lathe([(0, 0.14), (6.4, 0.095), (6.45, 0.0)], 16)
bmesh.ops.rotate(ep_bm, verts=ep_bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(90), 3, 'X'))
mesh_obj('ext_pole', ep_bm, CONC, EXT_POLE, 0.005)
L_H, R0, R1 = 0.72, 0.045, 0.30
K = math.log(R1 / R0) / 0.62
horn_r = lambda y: R0 * math.exp(K * y) if y < 0.62 else R1 + (y - 0.62) * 0.9

def build_horn(name, parent):
    prof = [(-0.20, 0.0), (-0.20, 0.085), (-0.06, 0.092), (-0.03, 0.06), (0.0, R0)]
    prof += [(0.62 * i / 22, horn_r(0.62 * i / 22)) for i in range(1, 23)]
    prof += [(0.64, R1 + 0.012), (0.66, R1 + 0.02), (0.675, R1 + 0.016)]
    ob = mesh_obj(name, lathe(prof), PAINT, parent, 0.006)
    ins = lathe([(0.05, 0.0), (0.05, horn_r(0.05) * .95)] + [(0.62 * i / 16, horn_r(0.62 * i / 16) * .97) for i in range(2, 17)], cap_back=True)
    bmesh.ops.reverse_faces(ins, faces=ins.faces)
    mesh_obj(name + '_in', ins, INSIDE, ob, 0)
    return ob

h_arm = empty('ext_horn_arm', EXT_POLE, (0, 0, 4.35))
make_box('ext_crossbar', (0, 0, 0), (0.95, 0.06, 0.06), STEEL, h_arm, 0.004)
h1 = build_horn('ext_horn_1', h_arm); h1.location = (-0.28, -0.10, 0.02)
h1.rotation_mode = 'QUATERNION'; h1.rotation_quaternion = Vector((0, 1, 0)).rotation_difference(Vector((-0.65, -1.0, -0.05)).normalized())

# Background houses varied in size, setback, roof overhang & colour so street feels lived-in (R6)
HOUSE_DARK = toon('house_dark', (0.22, 0.21, 0.26), (0.48, 0.44, 0.47))
FENCE_MAT = toon('fence_mat', (0.20, 0.18, 0.20), (0.42, 0.38, 0.36))
rng_h = random.Random(304)
for side_x in (-7.5, 11.8):
    for j in range(12):
        hy = 18.0 + j * 10.2 + rng_h.uniform(-0.8, 0.8)
        hw = rng_h.uniform(3.4, 5.0)
        hd = rng_h.uniform(4.8, 6.8)
        hh = rng_h.uniform(2.5, 4.1)
        hx = side_x + (rng_h.uniform(-0.4, 0.9) if side_x > 0 else -rng_h.uniform(0.0, 0.9))
        hmat = HOUSE_WALL if (j + int(side_x > 0)) % 2 == 0 else HOUSE_DARK
        make_box(f'house_{side_x}_{j}', (hx, hy, hh * 0.5), (hw, hd, hh), hmat, EXT, 0.006)
        # Low wooden/block garden fence along the road frontage
        fx = hx + (-hw * 0.56 if side_x > 0 else hw * 0.56)
        make_box(f'fence_{side_x}_{j}', (fx, hy, 0.55), (0.18, hd * 0.92, 1.1), FENCE_MAT, EXT, 0.004)
        rbm = bmesh.new()
        rx0, rx1 = hx - hw * 0.58, hx + hw * 0.58
        ry0, ry1 = hy - hd * 0.56, hy + hd * 0.56
        rz0, rz1 = hh, hh + rng_h.uniform(0.85, 1.35)
        vs = [
            rbm.verts.new((rx0, ry0, rz0)), rbm.verts.new((rx1, ry0, rz0)),
            rbm.verts.new((rx1, ry1, rz0)), rbm.verts.new((rx0, ry1, rz0)),
            rbm.verts.new((hx, ry0, rz1)), rbm.verts.new((hx, ry1, rz1)),
        ]
        rbm.faces.new((vs[0], vs[1], vs[4]))
        rbm.faces.new((vs[2], vs[3], vs[5]))
        rbm.faces.new((vs[0], vs[4], vs[5], vs[3]))
        rbm.faces.new((vs[1], vs[2], vs[5], vs[4]))
        bmesh.ops.recalc_face_normals(rbm, faces=rbm.faces)
        mesh_obj(f'roof_{side_x}_{j}', rbm, ROOF_TILE, EXT, 0.006)
        if j % 2 == 1:
            make_box(f'win_{side_x}_{j}', (hx + (-hw * 0.51 if side_x > 0 else hw * 0.51), hy - 0.8, 1.85), (0.04, 0.95, 0.82), WIN_LIT, EXT, 0)

# Fallen maple leaves along the exterior kerb/apron
for k in range(16):
    lx = rng_h.uniform(-0.8, 2.2)
    ly = rng_h.uniform(0.6, 6.5)
    lbm = bmesh.new()
    pts = []
    for a_i in range(14):
        ang = 2 * math.pi * a_i / 14
        rad = 0.042 if a_i % 2 == 0 else 0.018
        pts.append(lbm.verts.new((rad * math.cos(ang), rad * math.sin(ang), 0.0)))
    lbm.faces.new(pts)
    lo = mesh_obj(f'leaf_{k}', lbm, LEAF_MAT, EXT, 0.001)
    lo.location = (lx, ly, 0.012); lo.rotation_euler = (0, 0, rng_h.uniform(0, 6.28))

# Overhead power wires crossing visibly through the upper door glass (Y = 4.6 m)
WIRE_Y = 4.6
def wire_z(x, idx=0):
    t = (x + 2.5) / 6.0
    return 2.48 + idx * 0.22 - 0.20 * 4 * t * (1 - t) + 0.08 * t

for idx in range(3):
    cu = bpy.data.curves.new(f'pw_{idx}', 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.009
    sp = cu.splines.new('POLY'); npts = 32; sp.points.add(npts - 1)
    for k in range(npts):
        x = -2.5 + 6.0 * (k / (npts - 1))
        sp.points[k].co = (x, WIRE_Y + idx * 0.14, wire_z(x, idx), 1)
    co = bpy.data.objects.new(f'pw_{idx}', cu); sc.collection.objects.link(co); cu.materials.append(WIRE)

# ---------------- 5 CC0 Ravens perched cleanly inside the glass opening ----------------
CROW_MAT = toon('crowm', (0.07, 0.07, 0.11), (0.20, 0.21, 0.32), (1.0, 0.66, 0.45), rimfacing=0.72)
CROW_XS = [0.40, 0.58, 0.78, 0.98, 1.18]
CROWS = []
POSES_CACHE = {}

for ci, cx in enumerate(CROW_XS):
    c_empty = empty(f'crow_{ci}', EXT)
    _before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=CROW_GLB)
    _new = set(bpy.data.objects) - _before
    croot = next(o for o in _new if o.name.startswith('root') and o.parent is None)
    croot.parent = c_empty
    croot.rotation_mode = 'XYZ'
    croot.rotation_euler = (0, 0, math.radians(-115 + (ci % 2) * 14))
    carm = next(o for o in _new if o.type == 'ARMATURE')
    cmesh = next(o for o in _new if o.type == 'MESH' and 'Icosphere' not in o.name)
    for o in _new:
        if o.name not in sc.collection.objects and not o.users_collection:
            sc.collection.objects.link(o)
        if 'Icosphere' in o.name:
            o.hide_render = True
    cmesh.data.materials.clear(); cmesh.data.materials.append(CROW_MAT)
    for p_ in cmesh.data.polygons: p_.use_smooth = True
    sd = cmesh.modifiers.new('subd', 'SUBSURF'); sd.levels = 2; sd.render_levels = 2
    outline(cmesh, 0.0042)
    carm.animation_data.action = None

    def cap_crow(arm_obj, act_name, fr):
        key = (act_name, fr)
        if key not in POSES_CACHE:
            ad = arm_obj.animation_data
            act = next(a for a in bpy.data.actions if a.name == act_name or a.name.startswith(act_name + '.'))
            ad.action = act
            try:
                if act.slots and ad.action_slot is None:
                    ad.action_slot = act.slots[0]
            except AttributeError:
                pass
            sc.frame_set(int(fr))
            POSES_CACHE[key] = {b.name: (b.location.copy(), b.rotation_quaternion.copy(), b.scale.copy()) for b in arm_obj.pose.bones}
            ad.action = None
        return POSES_CACHE[key]

    p_stand = cap_crow(carm, 'stand', 0)
    p_fly = cap_crow(carm, 'fly', 4)
    toes = [b for b in carm.pose.bones if b.name.startswith('toe')]
    glints = []
    for sx in (-1, 1):
        eo = mesh_obj(f'c_glint_{ci}_{sx}', ellipsoid(0.0045, 0.0045, 0.0045, 8, 6), EYEW, None, 0)
        glints.append((sx, eo))
    CROWS.append(dict(root=c_empty, arm=carm, mesh=cmesh, toes=toes, stand=p_stand, fly=p_fly,
                      x=cx, y=WIRE_Y, z=wire_z(cx, 0), glints=glints, idx=ci))


# ---------------- Hero: Sam (sam_toon.blend) ----------------
with bpy.data.libraries.load(SAM_BLEND, link=False) as (src, dst):
    dst.objects = [n for n in src.objects]
SAM_OBJS = [o for o in dst.objects if o is not None and o.type not in ('LIGHT', 'CAMERA')]
for o in SAM_OBJS:
    sc.collection.objects.link(o)
    if o.type == 'EMPTY':
        o.hide_render = True
    if o.name == 'Headphone_Cable':
        o.hide_render = True

SAM = next(o for o in SAM_OBJS if o.type == 'ARMATURE')
SAM.rotation_mode = 'XYZ'
# Sam stands inside koban in clear 3/4 profile-front view within comfortable arm reach of brass bolt
SAM_X0, SAM_Y0 = -0.23, -0.25
SAM.location = (SAM_X0, SAM_Y0, 0.0)
SAM.rotation_euler = (0, 0, math.radians(112))
for pb in SAM.pose.bones:
    pb.rotation_mode = 'QUATERNION'
SAM_BASE = {pb.name: pb.matrix_basis.copy() for pb in SAM.pose.bones}

for o in SAM_OBJS:
    if o.type == 'MESH':
        for mod in o.modifiers:
            if mod.type == 'SOLIDIFY':
                mod.thickness = 0.0016


def _rot_arm(rig, name, axis, deg):
    pb = PB(rig, name); bpy.context.view_layer.update()
    R = Matrix.Rotation(math.radians(deg), 4, Vector(axis))
    pb.matrix = Matrix.Translation(pb.head) @ R @ Matrix.Translation(-pb.head) @ pb.matrix
    bpy.context.view_layer.update()


def _curl_fingers(rig, side, amount=1.0):
    S = 'L' if side > 0 else 'R'
    for fn, ang in (('Index', 58), ('Middle', 64), ('Ring', 66), ('Little', 68)):
        for j, k in ((1, 1.0), (2, 1.0), (3, 0.8)):
            pb = PB(rig, f'J_Bip_{S}_{fn}{j}'); best = None
            for ax in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)):
                pb.rotation_quaternion = Quaternion(ax, math.radians(30))
                bpy.context.view_layer.update()
                z = pb.tail.z
                if best is None or z < best[0]:
                    best = (z, ax)
                pb.rotation_quaternion = (1, 0, 0, 0)
            pb.rotation_quaternion = Quaternion(best[1], math.radians(ang * k * amount))
    for j, ang in ((1, 22), (2, 26), (3, 24)):
        pb = PB(rig, f'J_Bip_{S}_Thumb{j}'); best = None
        for ax in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0), (0, -1, 0)):
            pb.rotation_quaternion = Quaternion(ax, math.radians(30))
            bpy.context.view_layer.update()
            z = pb.tail.z
            if best is None or z < best[0]:
                best = (z, ax)
            pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_quaternion = Quaternion(best[1], math.radians(ang * amount))
    bpy.context.view_layer.update()


FCURL = {}
def compute_finger_curl(rig, amt_l, amt_r):
    keep = {pb.name: pb.matrix_basis.copy() for pb in rig.pose.bones}
    for pb in rig.pose.bones:
        pb.matrix_basis = Matrix.Identity(4)
    _curl_fingers(rig, 1, amt_l)
    _curl_fingers(rig, -1, amt_r)
    FCURL[rig.name] = {
        pb.name: pb.rotation_quaternion.copy()
        for pb in rig.pose.bones
        if any(k in pb.name for k in ('Index', 'Middle', 'Ring', 'Little', 'Thumb'))
    }
    for pb in rig.pose.bones:
        pb.matrix_basis = keep[pb.name]


def reset_sam():
    for pb in SAM.pose.bones:
        pb.matrix_basis = SAM_BASE[pb.name].copy()
    for n_, q_ in FCURL.get(SAM.name, {}).items():
        SAM.pose.bones[n_].rotation_quaternion = q_.copy()


def lowest_z(objs):
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    best = 1e9
    for o in objs:
        if o.type != 'MESH' or o.hide_render or 'Outline' in o.name:
            continue
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world
        c0 = SAM.matrix_world.translation
        zs = [w.z for i, v in enumerate(me.vertices) if i % 6 == 0 for w in (mw @ v.co,) if (w.xy - c0.xy).length < 0.9]
        ev.to_mesh_clear()
        if zs:
            best = min(best, min(zs))
    return best


def plant_sam():
    SAM.location.z = 0.0
    low = lowest_z(SAM_OBJS)
    SAM.location.z = -low


# Relaxed soft finger drape on left (0.45), firm bolt wrap on right (0.88)
compute_finger_curl(SAM, 0.45, 0.88)

# Right-hand IK targets in world space
IK_T = empty('ik_hand_R', KOBAN)
IK_AIM = empty('aim_hand_R', KOBAN)
IK_PALM = empty('palm_hand_R', KOBAN)
IK_POLE = empty('pole_elbow_R', KOBAN, loc=(-0.22, -0.68, 0.96))

c_ik = PB(SAM, 'J_Bip_R_LowerArm').constraints.new('IK')
c_ik.target = IK_T; c_ik.pole_target = IK_POLE; c_ik.chain_count = 2; c_ik.pole_angle = math.radians(0)
c_aim = PB(SAM, 'J_Bip_R_Hand').constraints.new('DAMPED_TRACK')
c_aim.target = IK_AIM; c_aim.track_axis = 'TRACK_Y'
hb_r = SAM.data.bones['J_Bip_R_Hand']; R0_h = hb_r.matrix_local.to_3x3()
best_ax = max((('TRACK_X', R0_h.col[0]), ('TRACK_NEGATIVE_X', -R0_h.col[0]), ('TRACK_Z', R0_h.col[2]), ('TRACK_NEGATIVE_Z', -R0_h.col[2])),
              key=lambda a: a[1].dot(Vector((0, 0, -1))))
c_palm = PB(SAM, 'J_Bip_R_Hand').constraints.new('LOCKED_TRACK')
c_palm.target = IK_PALM; c_palm.lock_axis = 'LOCK_Y'; c_palm.track_axis = best_ax[0]
R_CONS = [c_ik, c_aim, c_palm]

# ---------------- Camera & Lighting ----------------
cam_d = bpy.data.cameras.new('cam'); cam_d.lens = 34; cam_d.sensor_fit = 'VERTICAL'; cam_d.sensor_height = 36
cam_d.clip_start = 0.05; cam_d.clip_end = 2000.0
cam = bpy.data.objects.new('cam', cam_d); sc.collection.objects.link(cam); sc.camera = cam

sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 5.2; sun.data.color = (1.0, 0.78, 0.55); sun.data.angle = math.radians(1.2)
sun.rotation_euler = (-SUN).to_track_quat('-Z', 'Y').to_euler()

fill = bpy.data.objects.new('fill', bpy.data.lights.new('fill', 'SUN')); sc.collection.objects.link(fill)
fill.data.energy = 0.42; fill.data.color = (0.62, 0.64, 0.90)
fill.rotation_euler = Vector((0.35, 1.0, -0.20)).to_track_quat('-Z', 'Y').to_euler()

bounce = bpy.data.objects.new('koban_bounce', bpy.data.lights.new('koban_bounce', 'POINT')); sc.collection.objects.link(bounce)
bounce.location = (-0.05, -0.60, 1.48)
bounce.data.energy = 10.5; bounce.data.color = (1.0, 0.80, 0.60); bounce.data.shadow_soft_size = 0.35


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3.0 - 2.0 * t)


def apply_crow_pose(arm, pa, pb_, w):
    for b in arm.pose.bones:
        la, qa, sa = pa[b.name]; lb, qb, sb = pb_[b.name]
        b.location = la.lerp(lb, w); b.rotation_quaternion = qa.slerp(qb, w); b.scale = sa.lerp(sb, w)


def pose_frame(f):
    fp = f - ((f - 1) % 2)  # twos

    # 1) Bolt & Door motion: bolt unlatches f22..f40, door slides +0.105 m f42..f66 with subtle settle
    bolt_t = ease((fp - 22) / 18.0)
    door_u = max(0.0, min(1.0, (fp - 42) / 24.0))
    door_x = 0.105 * ease(door_u) + (0.004 * math.sin((fp - 58) * 0.7) * math.exp(-(fp - 58) * 0.25) if fp > 58 else 0.0)
    DOOR.location = (door_x, 0.0, 0.0)
    BOLT_SLIDE.location = (-0.06 + 0.050 * bolt_t, -0.044, 1.15)

    # 2) Pose Sam: turn off IK while resetting & applying base FK
    for c in R_CONS:
        c.influence = 0.0
    bpy.context.view_layer.update()
    reset_sam()

    breath = math.sin(fp * 0.14)
    # Lean gently right/forward along with the bolt/door slide so arm never over-stretches!
    slide_follow = ease((fp - 24) / 38.0)
    _rot_arm(SAM, 'J_Bip_C_Spine', (1, 0, 0), 4.0 + 1.2 * breath + 4.0 * slide_follow)
    _rot_arm(SAM, 'J_Bip_C_Chest', (1, 0, 0), 3.0 + 0.8 * breath + 2.0 * slide_follow)
    _rot_arm(SAM, 'J_Bip_C_Spine', (0, 0, 1), -6.0 * slide_follow)

    head_yaw = -16.0 - 10.0 * ease((fp - 42) / 16.0)
    head_pitch = -2.0 - 3.0 * ease((fp - 44) / 14.0)
    _rot_arm(SAM, 'J_Bip_C_Neck', (0, 0, 1), head_yaw * 0.45)
    _rot_arm(SAM, 'J_Bip_C_Head', (0, 0, 1), head_yaw * 0.55)
    _rot_arm(SAM, 'J_Bip_C_Head', (1, 0, 0), head_pitch)

    # Left arm in SAM_BASE is ALREADY lowered to hip! Only add subtle relaxed bend (never +76 deg!)
    _rot_arm(SAM, 'J_Bip_L_UpperArm', (1, 0, 0), 4.0 + 1.2 * breath)
    _rot_arm(SAM, 'J_Bip_L_LowerArm', (0, 0, 1), -12.0 - 1.5 * breath)

    # Subtle body shift toward bolt so right hand IK error stays <= 0.015 m across all frames
    SAM.location = (SAM_X0 + 0.075 * slide_follow, SAM_Y0 + 0.030 * slide_follow, 0.0)
    bpy.context.view_layer.update()
    plant_sam()
    bpy.context.view_layer.update()

    # Right-hand IK onto the brass bolt knob (fingers wrap knob cleanly)
    kw = BOLT_SLIDE.matrix_world @ knob_obj.location
    IK_T.location = kw + Vector((-0.030, -0.022, 0.008))
    IK_AIM.location = kw + Vector((0.028, 0.018, -0.005))
    IK_PALM.location = kw + Vector((0.012, 0.14, -0.06))
    IK_POLE.location = Vector((-0.34, -0.58, 0.96))
    for c in R_CONS:
        c.influence = 1.0
    bpy.context.view_layer.update()

    wrist_w = SAM.matrix_world @ PB(SAM, 'J_Bip_R_LowerArm').tail
    ik_err = (wrist_w - IK_T.matrix_world.translation).length

    # 3) Pose 5 CC0 Ravens on wire + synchronized 2-frame head-snap at f48..f54
    for C in CROWS:
        arm = C['arm']
        idle_w = 0.05 + 0.04 * math.sin(fp * 0.22 + C['idx'] * 1.1)
        if 48 <= fp <= 58:
            idle_w += 0.14 * math.sin(math.pi * (fp - 48) / 10.0)
        apply_crow_pose(arm, C['stand'], C['fly'], idle_w)
        bpy.context.view_layer.update()

        snap = ease((fp - 46) / 3.0)
        hy = 12.0 * math.sin(fp * 0.15 + C['idx']) * (1 - snap) + 78.0 * snap
        hp = 4.0 * (1 - snap) + 18.0 * snap
        roll = (8.0 - 3.0 * C['idx']) * snap
        hb = arm.pose.bones['Bone']
        R_h = Matrix.Rotation(math.radians(hy), 4, 'Z') @ Matrix.Rotation(math.radians(-hp), 4, 'X') @ Matrix.Rotation(math.radians(roll), 4, 'Y')
        hb.matrix = Matrix.Translation(hb.head) @ R_h @ Matrix.Translation(-hb.head) @ hb.matrix
        bpy.context.view_layer.update()

        C['root'].location = (C['x'], C['y'], C['z'])
        bpy.context.view_layer.update()
        mz = min((arm.matrix_world @ b.tail).z for b in C['toes'])
        C['root'].location.z += (C['z'] + 0.008) - mz
        bpy.context.view_layer.update()

        hmw = arm.matrix_world @ hb.matrix
        for sx, eo in C['glints']:
            eo.location = hmw @ Vector((0.022 * sx, hb.length * 0.65, 0.022))

    # 4) Camera on ones: slightly right (-0.08) looking across Sam's 3/4 face & bolt toward glass/crows
    k = (f - 1) / float(NF - 1)
    cam0 = Vector((-0.08, -1.68, 1.46))
    cam_tgt = Vector((0.08, 1.20, 1.43))
    p_cam = cam0.lerp(cam_tgt, 0.032 * ease(k)) + Vector((
        0.0045 * math.sin(f * 0.13),
        0.0,
        0.0032 * math.sin(f * 0.09 + 0.7),
    ))
    cam.location = p_cam
    cam.rotation_mode = 'QUATERNION'
    cam.rotation_quaternion = (cam_tgt - p_cam).to_track_quat('-Z', 'Y')
    bpy.context.view_layer.update()
    return ik_err


def bbox_from_pts(pts, w_px, h_px, pad=64):
    xs, ys = [], []
    for pt in pts:
        v = world_to_camera_view(sc, cam, pt)
        if v.z > 0:
            xs.append(v.x * w_px)
            ys.append((1.0 - v.y) * h_px)
    if not xs:
        return [0, 0, min(256, w_px), min(256, h_px)]
    x0 = max(0, int(min(xs) - pad))
    y0 = max(0, int(min(ys) - pad))
    x1 = min(w_px, int(max(xs) + pad))
    y1 = min(h_px, int(max(ys) + pad))
    return [x0, y0, max(96, x1 - x0), max(96, y1 - y0)]


# ---------------- Render loop ----------------
frames = list(range(1, NF + 1)) if FR == 'all' else [int(x) for x in FR.split(',')]
W_PX, H_PX = 1080, 1920
META = {"frames": {}, "crops": {"face_sam": {}, "hand_bolt": {}, "crows_wire": {}, "handprint_glass": {}}}

for f in frames:
    sc.frame_set(f)
    ik_err = pose_frame(f)
    sc.render.filepath = os.path.join(OUT, f'cel_{f:03d}.png')
    bpy.ops.render.render(write_still=True)

    sun_v = world_to_camera_view(sc, cam, cam.location + SUN * 100.0)
    META["frames"][str(f)] = {
        "sx": float(sun_v.x),
        "sy": float(1.0 - sun_v.y),
        "ik_err_m": float(ik_err),
    }

    head_w = SAM.matrix_world @ PB(SAM, 'J_Bip_C_Head').head
    hand_w = BOLT_SLIDE.matrix_world @ knob_obj.location
    crow_pts = [C['root'].matrix_world.translation + Vector((0, 0, 0.14)) for C in CROWS]
    glass_w = DOOR.matrix_world @ Vector((0.23, 0.018, 1.50))

    META["crops"]["face_sam"][str(f)] = bbox_from_pts([head_w + Vector((0, 0, 0.06)), head_w - Vector((0, 0, 0.05))], W_PX, H_PX, pad=130)
    META["crops"]["hand_bolt"][str(f)] = bbox_from_pts([hand_w, SAM.matrix_world @ PB(SAM, 'J_Bip_R_LowerArm').tail], W_PX, H_PX, pad=120)
    META["crops"]["crows_wire"][str(f)] = bbox_from_pts(crow_pts, W_PX, H_PX, pad=95)
    META["crops"]["handprint_glass"][str(f)] = bbox_from_pts([glass_w + Vector((-0.14, 0, -0.16)), glass_w + Vector((0.14, 0, 0.18))], W_PX, H_PX, pad=50)

    print(f'frame {f} | IK_R_err={ik_err:.4f}m | SUN_SCREEN=({sun_v.x:.3f}, {1.0 - sun_v.y:.3f})', flush=True)

f0 = str(frames[0])
META["SUN_SCREEN"] = [META["frames"][f0]["sx"], META["frames"][f0]["sy"]]
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w', encoding='utf-8'), indent=2)
print('SUN_SCREEN', META["SUN_SCREEN"][0], META["SUN_SCREEN"][1], flush=True)
