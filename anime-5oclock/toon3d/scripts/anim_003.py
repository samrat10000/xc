"""Shot 003: 3 s toon Sam test, keyed on twos. blender -b -P anim_003.py -- [test|full]"""
import bpy, math, os, sys, time, shutil, subprocess
import numpy as np
from mathutils import Vector, Matrix, Quaternion
from bpy_extras.object_utils import world_to_camera_view

ROOT = 'C:/Users/cross/Downloads/xc/anime-5oclock/toon3d/'
MODE = 'full' if 'full' in sys.argv else 'test'
bpy.ops.wm.open_mainfile(filepath=ROOT + 'sam_toon.blend')
sc = bpy.context.scene; rig = bpy.data.objects['Sam_Rig']; P = rig.pose.bones
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'CONSTANT'
FPS, NF = 24, 84   # v2: 3.5 s, action ends at 3.0 s and holds
sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, NF
def upd(): bpy.context.view_layer.update()
def clamp01(x): return max(0.0, min(1.0, x))
def ease(t, a, b):
    x = clamp01((t - a) / (b - a)); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x

def rot_world(name, axis, deg):
    if abs(deg) < 1e-6: return
    upd(); pb = P[name]; h = pb.head.copy()
    pb.matrix = Matrix.Translation(h) @ Matrix.Rotation(math.radians(deg), 4, axis) @ Matrix.Translation(-h) @ pb.matrix
def move_world(name, v):
    upd(); pb = P[name]; pb.matrix = Matrix.Translation(Vector(v)) @ pb.matrix

for pb in P: pb.rotation_mode = 'QUATERNION'
FINGERS = [f'J_Bip_L_{n}{i}' for n in ('Index', 'Middle', 'Ring', 'Little') for i in (1, 2, 3)]
THUMB = ['J_Bip_L_Thumb1', 'J_Bip_L_Thumb2', 'J_Bip_L_Thumb3']

# ---------------------------------------------------------------- controls: cup L, hand target, pole
def base_pose():
    for pb in P: pb.matrix_basis = Matrix.Identity(4)
    upd()
    move_world('J_Bip_L_Shoulder', (-0.008, 0, -0.002)); move_world('J_Bip_R_Shoulder', (0.008, 0, -0.002))
    rot_world('J_Bip_L_UpperArm', 'Y', 72); rot_world('J_Bip_R_UpperArm', 'Y', -72)
    rot_world('J_Bip_L_UpperArm', 'X', -4); rot_world('J_Bip_R_UpperArm', 'X', -4)
    rot_world('J_Bip_L_LowerArm', 'X', -8); rot_world('J_Bip_R_LowerArm', 'X', -8)
    for s in 'LR':
        P[f'J_Bip_{s}_UpperArm'].scale = (0.88, 1, 0.88); P[f'J_Bip_{s}_Hand'].scale = (1 / 0.88, 1, 1 / 0.88)
    rot_world('J_Bip_C_Neck', 'Z', -4); rot_world('J_Bip_C_Head', 'Z', -6)
    upd()

base_pose()
def new_empty(name, mw, parent=None, bone=None):
    e = bpy.data.objects.new(name, None); sc.collection.objects.link(e); e.empty_display_size = 0.02
    if parent is not None:
        e.parent = parent
        if bone: e.parent_type = 'BONE'; e.parent_bone = bone
    upd(); e.matrix_world = mw; upd(); return e
cup = bpy.data.objects['Headphone_Cup_L']
C0 = cup.matrix_world.translation.copy()
ctrl = new_empty('CupL_Ctrl', Matrix.Translation(C0), rig, 'J_Bip_C_Head')
for n in ('Headphone_Cup_L', 'Headphone_Pad_L', 'Headphone_Cap_L'):
    o = bpy.data.objects[n]; mw = o.matrix_world.copy(); o.parent = ctrl; o.parent_type = 'OBJECT'; upd(); o.matrix_world = mw
upd()
ctrl_basis = ctrl.matrix_basis.copy()

# v2: hood at full size (down on the back; was undersized)
HOOD_S = float(os.environ.get('HOOD_S', '1.45'))
pm = bpy.data.objects['Hoodie_HoodBack'].data
for v in pm.vertices:
    v.co.x *= HOOD_S; v.co.z = v.co.z * HOOD_S - 0.045 * (HOOD_S - 1)
rm = bpy.data.objects['Hoodie_HoodRoll'].data
ny = rig.data.bones['J_Bip_C_Neck'].head_local.y
zs = [v.co.z for v in rm.vertices]; zc = (max(zs) + min(zs)) / 2
for v in rm.vertices:
    v.co.x *= 1.10; v.co.y = ny + (v.co.y - ny) * 1.10; v.co.z = zc + (v.co.z - zc) * 1.15
pm.update(); rm.update()

def hook(curve_name, point_ids):
    ob = bpy.data.objects[curve_name]
    md = ob.modifiers.new('HookCup', 'HOOK'); md.object = ctrl
    idx = []
    for i in point_ids: idx += [3 * i, 3 * i + 1, 3 * i + 2]
    md.vertex_indices_set(idx)
    upd(); md.matrix_inverse = ctrl.matrix_world.inverted() @ ob.matrix_world
nb = len(bpy.data.objects['Headphone_Band'].data.splines[0].bezier_points)
hook('Headphone_Band', [nb - 1, nb - 2]); hook('Headphone_Cable', [0])

# hand frame: fingers up-forward, palm on the outer cap facing the head, thumb toward the back
Yl = Vector((0, -0.42, 0.91)).normalized(); Zl = Vector((1, 0, 0)); Xl = Yl.cross(Zl).normalized(); Zl = Xl.cross(Yl)
Rh = Matrix((Xl, Yl, Zl)).transposed().to_4x4()
hand_len = (rig.data.bones['J_Bip_L_Middle1'].head_local - rig.data.bones['J_Bip_L_Hand'].head_local).length
CAP_OUT = 0.026 + 0.007 + 0.006   # cup depth + cap offset (from build_sam)
palm = C0 + Vector((CAP_OUT + 0.016, 0, 0)) - Yl * 0.012
wrist = palm - Yl * hand_len * 0.62
tgt = new_empty('HandL_Target', Matrix.Translation(wrist) @ Rh, ctrl)
pole = new_empty('ElbowL_Pole', Matrix.Translation(Vector((0.34, 0.12, 1.22))), rig)
ik = P['J_Bip_L_LowerArm'].constraints.new('IK'); ik.target = tgt; ik.chain_count = 2; ik.pole_target = pole
ik.pole_angle = math.radians(float(os.environ.get('POLE', '-90'))); ik.influence = 0
cr = P['J_Bip_L_Hand'].constraints.new('COPY_ROTATION'); cr.target = tgt; cr.influence = 0
tgt_basis = tgt.matrix_basis.copy()
print('hand_len', hand_len, 'C0', C0, 'wrist', wrist)

face = bpy.data.objects['Face']; face_line = bpy.data.objects['Face_Outline']
def sk(name, v):
    for o in (face, face_line):
        kb = o.data.shape_keys.key_blocks.get('Face.M_F00_000_00_Fcl_' + name); kb.value = v
def sk_key(name, f):
    for o in (face, face_line): o.data.shape_keys.key_blocks['Face.M_F00_000_00_Fcl_' + name].keyframe_insert('value', frame=f)
SKS = ['BRW_Surprised', 'EYE_Close', 'MTH_A', 'MTH_I']
hair_top = [b.name for b in rig.data.bones if b.name.startswith('HairJoint') and b.parent and b.parent.name == 'J_Bip_C_Head']
CURL = float(os.environ.get('CURL', '1'))  # sign of finger curl axis

# ---------------------------------------------------------------- the performance
def state(t):
    s = {}
    lift = ease(t, 0.85, 1.45)
    s['head_x'] = lerp(7, -7, lift) + 0.6 * math.sin(2 * math.pi * t / 1.5)   # + breath nod
    s['head_z'] = lerp(0, -7, lift)
    dart = 0 if t < 0.58 else (0.5 if t < 0.65 else 1)
    s['eye_x'] = lerp(5, -9, dart); s['eye_z'] = lerp(-1, -10, dart)
    s['brow'] = 0.55 * lift
    s['ik'] = 0.0 if t < 1.20 else (0.5 if t < 1.28 else 1.0)   # one clean in-between
    s['grip'] = ease(t, 1.18, 1.36)
    s['slide'] = ease(t, 1.80, 2.30)
    s['blink'] = {59: 0.5, 61: 1.0, 63: 0.5}.get(round(t * 24) + 1, 0.0)
    s['lips'] = 1.0 if t >= 2.82 else 0.0
    s['breath'] = 0.7 * math.sin(2 * math.pi * t / 1.6)
    a1 = 2.2 * math.exp(-max(0, t - 1.45) * 4) * math.sin(max(0, t - 1.45) * 13) if t > 1.45 else 0
    a2 = 1.2 * math.exp(-max(0, t - 2.3) * 5) * math.sin(max(0, t - 2.3) * 15) if t > 2.3 else 0
    s['hair'] = a1 + a2 + (0.9 * lift if t < 1.45 else 0.9) * 0
    return s

def apply(t):
    s = state(t)
    ik.influence = 0; cr.influence = 0
    base_pose()
    rot_world('J_Bip_C_UpperChest', 'X', s['breath'])
    rot_world('J_Bip_C_Head', 'X', s['head_x']); rot_world('J_Bip_C_Head', 'Z', s['head_z'])
    for e in ('J_Adj_L_FaceEye', 'J_Adj_R_FaceEye'):
        rot_world(e, 'Z', s['eye_z']); rot_world(e, 'X', s['eye_x'])
    for i, h in enumerate(hair_top):
        rot_world(h, 'X', s['hair'] * (1 if i % 2 else 0.7)); rot_world(h, 'Y', s['hair'] * 0.4 * (1 if i % 3 else -1))
    # fingers: relaxed slight curl when hanging, open while reaching, grip on the cup
    g = s['grip']; reach = s['ik'] * (1 - g)
    for n in FINGERS:
        i = int(n[-1]); base = {1: 12, 2: 14, 3: 8}[i]; grip = {1: 38, 2: 52, 3: 34}[i]
        ang = lerp(base * (1 - reach), grip, g)
        P[n].rotation_quaternion = Quaternion((1, 0, 0), math.radians(-ang * CURL))
    for n in THUMB:
        i = int(n[-1]); ang = lerp({1: 4, 2: 8, 3: 6}[i], {1: 10, 2: 22, 3: 18}[i], g)
        P[n].rotation_quaternion = Quaternion((0, 0, 1), math.radians(ang * CURL))
    # cup slide: back off the ear and down onto the neck (in head-relative terms)
    ctrl.matrix_basis = ctrl_basis.copy(); upd()
    W = ctrl.matrix_world.copy()
    hr = P['J_Bip_C_Head'].matrix.to_3x3()  @ rig.data.bones['J_Bip_C_Head'].matrix_local.to_3x3().inverted()
    d = hr @ Vector((-0.022, 0.055, -0.085)) * s['slide']
    R = Matrix.Translation(W.translation) @ (hr.to_4x4() @ Matrix.Rotation(math.radians(24 * s['slide']), 4, 'X') @ hr.to_4x4().inverted()) @ Matrix.Translation(-W.translation)
    ctrl.matrix_world = Matrix.Translation(d) @ R @ W; upd()
    # reach: IK target travels from the real (FK) wrist to the cup along a small outward arc
    upd(); Wf = rig.matrix_world @ P['J_Bip_L_Hand'].matrix
    tgt.matrix_basis = tgt_basis.copy(); upd(); T1 = tgt.matrix_world.copy()
    r = s['ik']
    pole.location = Vector((0.34, 0.12, 1.22))
    ARM = ['J_Bip_L_UpperArm', 'J_Bip_L_LowerArm', 'J_Bip_L_Hand']
    if 0 < r < 1:
        # in-between: hand rises in front of the chest, elbow stays low and back (no sideways jut)
        Wf = rig.matrix_world @ P['J_Bip_L_Hand'].matrix
        pos = Wf.translation.lerp(T1.translation, r) + Vector((-0.05, -0.09, 0.0))
        q = Wf.to_quaternion().slerp(T1.to_quaternion(), r)
        tgt.matrix_world = Matrix.Translation(pos) @ q.to_matrix().to_4x4()
        pole.location = Vector((0.0, -0.4, 1.0)); ik.influence = 1.0; cr.influence = 1.0; upd()
    else:
        ik.influence = 1.0 if r >= 1 else 0.0; cr.influence = ik.influence
    sk('BRW_Surprised', s['brow']); sk('EYE_Close', s['blink']); sk('MTH_A', 0.16 * s['lips']); sk('MTH_I', 0.14 * s['lips'])
    return s

def key(f):
    for pb in P:
        pb.keyframe_insert('location', frame=f); pb.keyframe_insert('rotation_quaternion', frame=f); pb.keyframe_insert('scale', frame=f)
    ik.keyframe_insert('influence', frame=f); cr.keyframe_insert('influence', frame=f)
    pole.keyframe_insert('location', frame=f)
    for o in (ctrl, tgt): o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)
    for n in SKS: sk_key(n, f)

KEYS = list(range(1, NF + 1, 2))   # on twos
for f in KEYS:
    apply(min(f - 1, 70) / FPS); key(f)   # hold the last drawing (f71) to the end
print('keyed', len(KEYS))

# ---------------------------------------------------------------- camera: look-test framing (3/4, head to screen-left)
cam_d = bpy.data.cameras.new('Cam003'); cam = bpy.data.objects.new('Cam003', cam_d); sc.collection.objects.link(cam); sc.camera = cam
cam_d.lens = 85; cam_d.sensor_fit = 'HORIZONTAL'; cam_d.sensor_width = 36
sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
sc.frame_set(1); upd()
dg = bpy.context.evaluated_depsgraph_get()
hairo = bpy.data.objects['Hair']; ev = hairo.evaluated_get(dg); me = ev.to_mesh()
hair_pts = [hairo.matrix_world @ v.co for v in list(me.vertices)[::3]]; ev.to_mesh_clear()
hc = P['J_Bip_C_Head'].head + Vector((0, 0, 0.07))
az = math.radians(38); el = math.radians(-2)
dirv = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
def look(target):
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat('-Z', 'Y').to_euler()
dist, drop = 1.2, 0.0
for it in range(6):
    target = hc + Vector((0, 0, -drop)); cam.location = target + dirv * dist; look(target); upd()
    uv = [world_to_camera_view(sc, cam, p) for p in hair_pts]
    frac = max(u.x for u in uv) - min(u.x for u in uv); cy = (max(u.y for u in uv) + min(u.y for u in uv)) / 2
    dist *= frac / 0.45; drop += (0.64 - cy) * dist * 36 / 85 * 1920 / 1080
print('cam dist', dist)
sc.eevee.taa_render_samples = 64
sc.render.film_transparent = True
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
bpy.ops.wm.save_as_mainfile(filepath=ROOT + 'sam_toon_003.blend')

def render_frame(f, path, pct=100, samples=64):
    sc.frame_set(f); sc.render.resolution_percentage = pct; sc.eevee.taa_render_samples = samples
    sc.render.filepath = path; t0 = time.time(); bpy.ops.render.render(write_still=True); return time.time() - t0

SCR = 'C:/Users/cross/AppData/Local/Temp/claude/2025787e23e4a901/f11d269a-c5f1-40b4-9f86-0161f90ec98f/scratchpad/a003/'
if MODE == 'test':
    os.makedirs(SCR, exist_ok=True)
    for f in (23, 25, 27, 29, 31, 33, 37):
        print('T', f, render_frame(f, SCR + f'f{f:02d}.png', 40, 16))
    # hand close-ups
    cam2_d = bpy.data.cameras.new('HandCam'); cam2 = bpy.data.objects.new('HandCam', cam2_d); sc.collection.objects.link(cam2)
    cam2_d.lens = 85; sc.camera = cam2
    for f in (37, 51):
        sc.frame_set(f); upd(); hp = P['J_Bip_L_Middle1'].head.copy()
        for k, (dx, dy) in enumerate(((0.9, -0.5), (0.2, -1.0), (0.6, 0.8))):
            cam2.location = hp + Vector((dx, dy, 0.1)).normalized() * 0.75
            cam2.rotation_euler = (hp - cam2.location).to_track_quat('-Z', 'Y').to_euler()
            sc.render.resolution_x = sc.render.resolution_y = 700
            render_frame(f, SCR + f'hand_f{f}_{k}.png', 100, 16)
    sys.exit(0)

# ---------------------------------------------------------------- full render (odd frames, held for 2)
A = ROOT + '003_v2_alpha/'
os.makedirs(A, exist_ok=True)
for q_ in os.listdir(A): os.remove(A + q_)
times = []
h, w = 1920, 1080
yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
r2 = ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2
base = np.array([231, 185, 154], np.float32) / 255
bg = base[None, None, :] * (1 - 0.22 * np.clip(r2 - 0.25, 0, None))[..., None]
for f in KEYS:
    p = A + f'{f:04d}.png'; times.append(render_frame(f, p)); print('F', f, f'{times[-1]:.1f}s')
    shutil.copy(p, A + f'{f + 1:04d}.png')
print('RENDERTIMES avg %.2f s/drawing, total %.1f s' % (sum(times) / len(times), sum(times)))
