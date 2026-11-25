"""5 O'CLOCK Ep1 "The Fourth Note" - shot 06 "4:59" (2 s, 48 f @24). Insert over Sam's right shoulder onto the phone on his handlebar
while he coasts: battery 3%, his thumb skips a song (f14-26), the clock flips 16:59 -> 17:00 on f36 (lands on the first chime note of 07).
Shallow depth of field on the phone. Reuses the approved shot 04 rider + bike (exec of build_s04.py up to its render loop).
usage: blender -b --python build_s06.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math
HERE6 = os.path.dirname(os.path.abspath(__file__))
S04 = os.path.normpath(os.path.join(HERE6, '..', '..', '04_ride', 'src'))
_s = open(os.path.join(S04, 'build_s04.py'), encoding='utf-8').read()
_s = _s[:_s.index('META = {}')]
_s = _s.replace("HERE = os.path.dirname(os.path.abspath(__file__)); D = HERE", "HERE = %r; D = HERE" % S04)
exec(_s)
from mathutils import Quaternion
NF = 48
for o in R2['objs']: o.hide_render = True
for o in bpy.data.objects:
    if o.type == 'MESH' and any(m and m.name.startswith('susuki') for m in o.data.materials): o.hide_render = True


def sam_x(f):
    t = (f - 1) / 24.0; return 30.0 + 3.9 * t


# ---------------- the phone screen (music player lock screen), drawn per state ----------------
TR1 = ('å¤•ç„¼ã‘ã®ã†ãŸ', 'Kiriyama FM', 0.82); TR2 = ('å¸°ã‚Šé“', 'Kiriyama FM', 0.03)
IMGS = {}
for key, args in (('a', ('16:59', False, TR1)), ('b', ('16:59', True, TR1)), ('c', ('16:59', False, TR2)), ('d', ('17:00', False, TR2))):
    c_, pr_, tr_ = args
    IMGS[key] = bpy.data.images.load(os.path.join(HERE6, 'screens', 'screen_%s_%d_%d.png' % (c_.replace(':', ''), int(pr_), int(tr_[2] * 100))))
SCR = bpy.data.materials.new('phone_screen06'); SCR.use_nodes = True
N_ = SCR.node_tree.nodes
for n in list(N_): N_.remove(n)
tx = N_.new('ShaderNodeTexImage'); tx.image = IMGS['a']; em = N_.new('ShaderNodeEmission'); em.inputs[1].default_value = 1.15
SCR.node_tree.links.new(tx.outputs[0], em.inputs[0]); SCR.node_tree.links.new(em.outputs[0], N_.new('ShaderNodeOutputMaterial').inputs[0])

# ---------------- phone + stem mount on the bar ----------------
B = R1['B']; steer = B['steer']
st = HT_T - HT_B + (HT_T - HT_B).normalized() * 0.25
PH = empty('phone_root', steer, st + Vector((0.05, 0.0, 0.07)))
PH.rotation_mode = 'XYZ'; PH.rotation_euler = (0, math.radians(-52), 0)            # tilted back toward the rider
BODY = toon('phone_body06', (0.06, 0.06, 0.08), (0.18, 0.18, 0.22), (1.0, 0.86, 0.62), None, 0.5)
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
bmesh.ops.scale(bm, vec=(0.152, 0.073, 0.009), verts=bm.verts)
bmesh.ops.bevel(bm, geom=list(bm.edges), offset=0.006, segments=4, affect='EDGES')
mesh_obj('phone_body', bm, BODY, PH, 0.0012)
bm = bmesh.new()
x0, x1, y0, y1, z = -0.071, 0.071, -0.0335, 0.0335, 0.0047
uv = bm.loops.layers.uv.new()
f_ = bm.faces.new([bm.verts.new((x0, y0, z)), bm.verts.new((x1, y0, z)), bm.verts.new((x1, y1, z)), bm.verts.new((x0, y1, z))])
for lp, (u, v) in zip(f_.loops, ((1, 0), (1, 1), (0, 1), (0, 0))): lp[uv].uv = (u, v)          # v2: was upside down     # portrait screen: top of the image toward the bar end
scr = mesh_obj('phone_screen', bm, SCR, PH, 0)
CL = toon('mount06', (0.12, 0.12, 0.14), (0.30, 0.30, 0.34), (1.0, 0.86, 0.62), None, 0.5)
for sx_ in (-1, 1):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(0.018, 0.08, 0.02), verts=bm.verts)
    c_ = mesh_obj('mount_jaw', bm, CL, PH, 0.001); c_.location = (sx_ * 0.06, 0, -0.004)
bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(0.03, 0.03, 0.07), verts=bm.verts)
mesh_obj('mount_stalk', bm, CL, PH, 0.001).location = (0, 0, -0.045)

# ---------------- the thumb skips a song: right-hand IK target leaves the grip, taps "next", returns ----------------
hR = IKT['hand_R']; home = hR.location.copy()
bpy.context.view_layer.update()
tap_local = steer.matrix_world.inverted() @ (PH.matrix_world @ Vector((0.035, 0.018, 0.05)))


def thumb(f):
    fp = f - (f - 1) % 2
    k = ease((fp - 12) / 6.0) * (1 - ease((fp - 24) / 6.0))
    hR.location = home.lerp(tap_local, k)
    if 18 <= fp <= 21: tx.image = IMGS['b']
    elif fp < 18: tx.image = IMGS['a']
    elif fp < 36: tx.image = IMGS['c']
    else: tx.image = IMGS['d']


# ---------------- camera: over Sam's right shoulder, riding with him, shallow focus on the phone ----------------
camd.lens = 42; camd.dof.use_dof = True; camd.dof.focus_object = PH; camd.dof.aperture_fstop = 1.6
camd.clip_start = 0.02


def cam06(f):
    root = B['root'].matrix_world
    p = PH.matrix_world @ Vector((-0.20, -0.07, 0.30)) + Vector((0.003 * math.sin(f * 0.9), 0, 0.004 * math.sin(f * 1.3)))
    tgt = PH.matrix_world @ Vector((0.012, 0.0, 0.0))
    return p, (tgt - p).to_track_quat('-Z', 'Y') @ Quaternion((0, 0, 1), math.radians(-4))


META = {}
frames = range(1, NF + 1) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    sc.frame_set(f)
    pose_rider(R1, f); thumb(f); bpy.context.view_layer.update(); pose_strings(R1, f)
    p, q = cam06(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    s_ = proj(cam.location + SUN * 1000); h_ = proj(cam.location + Vector((0, 1, 0)) * 5000)
    META[f] = dict(sx=s_[0], sy=s_[1], hy=h_[1], glass=[(0, 0)] * 4, refl=False, samx=0.5)
    sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    print('frame', f, flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
