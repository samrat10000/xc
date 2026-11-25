"""5 O'CLOCK Ep1 "The Fourth Note" - shot 12 "Closer" (3.5 s, 84 f @24). From the mirror (shot 11's set and camera), a whip pan right to the
real sunset street: the townsfolk stand frozen, backs to us, nobody looking. Whip back to the mirror: inside, the crowd is now much closer
and fills the glass. Smear frames on both whips (comp). META carries 'whip' (pan speed) and 'close' (how near the mirror crowd is).
usage: blender -b --python build_s12.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math, json
A12 = sys.argv[sys.argv.index('--') + 1:]
H12 = os.path.dirname(os.path.abspath(__file__))
S11 = os.path.normpath(os.path.join(H12, '..', '..', '11_mirror', 'src'))
_s = open(os.path.join(S11, 'build_s11.py'), encoding='utf-8').read()
_s = _s[:_s.index('META = {}')]
_s = _s.replace("H11 = os.path.dirname(os.path.abspath(__file__))", "H11 = %r" % S11)
sys.argv = [sys.argv[0], '--'] + A12
__file__ = os.path.join(S11, 'build_s11.py')                        # toonlib/paths resolve next to shot 11
exec(_s)
from mathutils import Quaternion
NF = 84
CASTD = os.path.normpath(os.path.join(H12, '..', '..', '..', 'assets', 'cast_v2'))


def load_char(name, loc, face_dir):
    with bpy.data.libraries.load(os.path.join(CASTD, name + '.blend'), link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    new = [o for o in dst.objects if o is not None and o.type not in ('LIGHT', 'CAMERA')]
    for o in new: sc.collection.objects.link(o)
    r = next(o for o in new if o.type == 'ARMATURE' and o.parent is None)
    r.location = loc; r.rotation_mode = 'XYZ'
    r.rotation_euler = (0, 0, math.atan2(face_dir.y, face_dir.x) + math.pi / 2)        # rig front (-Y) -> face_dir
    for pb in r.pose.bones: pb.rotation_mode = 'QUATERNION'
    for s_, sg in (('L', 1), ('R', -1)):
        pb = r.pose.bones['J_Bip_%s_UpperArm' % s_]; b = r.data.bones['J_Bip_%s_UpperArm' % s_]
        pb.rotation_quaternion = Quaternion((b.matrix_local.to_3x3().inverted() @ Vector((0, 1, 0))).normalized(), math.radians(80 * sg)) @ pb.rotation_quaternion
    bpy.context.view_layer.update()
    low = min((o.matrix_world @ v.co).z for o in new if o.type == 'MESH' and o.name.endswith('Body') for v in o.data.vertices)
    r.location.z += 0.0 - low
    return r



# ---------------- the real street the whip lands on (E1: never a bare plane) ----------------
import bmesh as _bm
ASPH = toon('asph12', (0.20, 0.18, 0.24), (0.40, 0.37, 0.42))
WHITE = toon('paint12', (0.62, 0.60, 0.62), (0.92, 0.90, 0.86))
WALL = toon('wall12', (0.38, 0.36, 0.42), (0.70, 0.68, 0.66), (1.0, 0.82, 0.6))
JOINT = toon('joint12', (0.26, 0.24, 0.30), (0.46, 0.44, 0.48))
HOUSE = toon('house12', (0.36, 0.30, 0.36), (0.72, 0.62, 0.56), (1.0, 0.8, 0.58))
ROOF = toon('roof12', (0.17, 0.17, 0.26), (0.34, 0.34, 0.46))
AX = SIDE.normalized(); AY = FWD.normalized(); Z = Vector((0, 0, 1))
BASIS = Matrix((AX, AY, Z)).transposed().to_4x4()


def sbox(name, c, size, mat, line=0.01):
    bm = _bm.new(); _bm.ops.create_cube(bm, size=1.0)
    _bm.ops.scale(bm, vec=size, verts=bm.verts)
    ob = mesh_obj(name, bm, mat, None, line); ob.matrix_world = Matrix.Translation(SPOS + AX * c[0] + AY * c[1] + Z * c[2]) @ BASIS
    return ob


# v4 (Sam: "the road looked broken, like it is going to the sky... a single pole, no light"): the street now runs 400 m to a dark
# hill, with houses on BOTH sides, poles every 11 m carrying lit street lamps and wires.
LN = 400.0
sbox('road12', (LN / 2, 0.2, -0.02), (LN, 7.0, 0.04), ASPH, 0)
for k in range(int(LN / 3.6)):
    sbox('dash12_%d' % k, (3 + k * 3.6, 0.2, 0.005), (1.8, 0.12, 0.01), WHITE, 0)
for s_ in (-1, 1):
    sbox('kerb12_%d' % s_, (LN / 2, 0.2 + s_ * 3.55, 0.06), (LN, 0.15, 0.14), WHITE, 0.006)
sbox('wall12', (LN / 2, 4.1, 0.75), (LN, 0.16, 1.5), WALL, 0.01)
for k in range(60):
    sbox('wj12_%d' % k, (0.5 + k, 4.0, 0.75), (0.02, 0.02, 1.5), JOINT, 0)
for k in range(5):
    sbox('wjh12_%d' % k, (LN / 2, 4.0, 0.25 + k * 0.3), (LN, 0.02, 0.02), JOINT, 0)
WIN = toon('win12', (0.30, 0.34, 0.44), (0.62, 0.70, 0.82)); WLIT = emis('win12lit', (1.0, 0.66, 0.34), 1.0)
import random as _r; _rr = _r.Random(12)
for side_, y0 in ((1, 8.0), (-1, -9.2)):                          # both sides of the street
    x = 4.0 if side_ > 0 else 6.0
    while x < LN - 10:
        w = _rr.uniform(5.5, 8.0); h = _rr.uniform(4.6, 6.2)
        sbox('hs12', (x, y0, h / 2), (w, 6.0, h), HOUSE, 0.02)
        sbox('hr12', (x, y0, h + 0.4), (w + 0.8, 6.6, 0.9), ROOF, 0.02)
        sbox('win12', (x - 1.2, y0 - side_ * 3.05, h * 0.62), (1.4, 0.05, 0.9), WLIT if _rr.random() < 0.45 else WIN, 0.006)
        x += w + _rr.uniform(1.0, 2.6)
LAMP = emis('lamp12', (1.0, 0.80, 0.52), 3.0)
PX = [3 + k * 11 for k in range(int(LN / 11))]
for k, x in enumerate(PX):
    sbox('pole12_%d' % k, (x, -3.9, 4.0), (0.26, 0.26, 8.0), CONC, 0.012)
    sbox('arm12_%d' % k, (x, -3.2, 6.6), (0.08, 1.4, 0.08), CONC, 0.004)
    sbox('lamp12_%d' % k, (x, -2.55, 6.5), (0.32, 0.22, 0.10), LAMP, 0.003)
for xa, xb in zip(PX, PX[1:]):
    for dz in (7.4, 7.0):
        sbox('wire12', ((xa + xb) / 2, -3.9, dz - 0.15), (xb - xa, 0.02, 0.02), JOINT, 0)
HM = emis('hill12', (0.075, 0.045, 0.085), 1.0)                                   # closes the end of the street: rounded hills, not a wall
for hx_, hy_, rx_, ry_, rz_ in ((LN + 70, -40, 90, 160, 46), (LN + 140, 110, 110, 150, 62), (LN + 120, -190, 120, 140, 38)):
    hob = mesh_obj('hill12', ellipsoid(rx_, ry_, rz_, 32, 16), HM, None, 0); hob.matrix_world = Matrix.Translation(SPOS + AX * hx_ + AY * hy_ - Z * 4) @ BASIS
# the real street to the right of the mirror: townsfolk frozen, facing away down the street (nobody looks at him)
away = (SIDE * 0.85 + FWD * 0.5).normalized()
for name, off in (('shopkeeper', SIDE * 4.6 + FWD * 1.4), ('grandma', SIDE * 7.4 - FWD * 0.6), ('kid_girl', SIDE * 3.4 - FWD * 1.3), ('kid_boy', SIDE * 9.6 + FWD * 0.9)):
    p_ = SPOS + off; p_.z = 0.0
    load_char(name, p_, away)


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


def whip_w(f):
    return ease((f - 20) / 6.0) * (1 - ease((f - 50) / 6.0))


P0 = HEADW - FWD * 0.42 - side * 0.12 + Vector((0, 0, 0.02))
Q_M = ((MPOS + (HEADW - MPOS) * 0.10) - P0).to_track_quat('-Z', 'Y')
Q_S = ((SPOS + SIDE * 6.0 + FWD * 0.3 + Vector((0, 0, 1.45))) - P0).to_track_quat('-Z', 'Y')


def cam12(f):
    w = whip_w(f)
    p = P0.lerp(MPOS - FWD * 1.15, 0.55 * ease((f - 56) / 24.0)) + Vector((0.004 * math.sin(f * 0.23), 0, 0.003 * math.sin(f * 0.37)))   # past his head onto the glass
    cam_d.lens = 40 if f < 50 else 40 + 12 * ease((f - 56) / 24.0)          # after the whip back, a creeping push on the glass
    cam_d.dof.focus_distance = (MPOS - p).length if w < 0.5 else 5.5
    return p, Q_M.slerp(Q_S, w)


META = {}
frames = list(range(1, NF + 1)) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    sc.frame_set(f)
    p, q = cam12(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    c = world_to_camera_view(sc, cam, MPOS); e = world_to_camera_view(sc, cam, MPOS + SIDE * R)
    s_ = world_to_camera_view(sc, cam, cam.location + SUN * 100)
    META[f] = dict(mx=c.x, my=1 - c.y, mr=abs(e.x - c.x), sx=s_.x, sy=1 - s_.y, leaf=[0, 0, False],
                   whip=abs(whip_w(f + 1) - whip_w(f - 1)) / 2.0, close=0.12 if f < 38 else 1.0)
    sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    print('frame', f, flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
print('SUN', META[frames[0]]['sx'], META[frames[0]]['sy'])
