"""5 O'CLOCK Ep1 "The Fourth Note" - shot 07 "Three notes" (4.5 s, 108 f @24). Low angle up at the loudspeaker pole against the sunset.
Note 1 (f6): the crows on the first wire lift off in a wave; note 2 (f30): the second wire; note 3 (f54): the third wire and a ring through the clouds.
The fourth note (f78) never comes; the horn keeps trembling in the silence. Each note = one visible ring in the sky (comp).
Reuses the LOCKED shot 01 v4 build (horns, pole, materials, the CC0 raven) up to its camera; crows are re-imported copies of the same raven.
usage: blender -b --python build_s07.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math, random, json
A7 = sys.argv[sys.argv.index('--') + 1:]
HERE7 = os.path.dirname(os.path.abspath(__file__))
S01 = os.path.normpath(os.path.join(HERE7, '..', '..', '01_speaker', 'src'))
os.environ['CROW_GLB'] = os.path.join(S01, 'crow_tehbucket_raven_cc0.glb')
_s = open(os.path.join(S01, 'build_s01_v4.py'), encoding='utf-8').read()
_s = _s[:_s.index('# ---------------- animation')]
_s = _s.replace("OUT = sys.argv[1]; SCALE = float(sys.argv[2]); FR = sys.argv[3] if len(sys.argv) > 3 else 'all'",
                "OUT = %r; SCALE = %r; FR = %r" % (A7[0], float(A7[1]), A7[2] if len(A7) > 2 else 'all'))
exec(_s)
from mathutils import Quaternion
NF = 108
NOTES = [6, 30, 54]; FOURTH = 78
for c in list(cam.constraints): cam.constraints.remove(c)
crow.hide_render = True
for o in crow.children_recursive: o.hide_render = True
random.seed(7)

# ---------------- three power lines across the sky, behind the pole ----------------
WIRES = []
for i, (y, z0) in enumerate(((9.0, 3.4), (10.6, 4.2), (12.4, 5.1))):
    cu = bpy.data.curves.new('w07_%d' % i, 'CURVE'); cu.dimensions = '3D'; cu.bevel_depth = 0.014
    sp = cu.splines.new('POLY'); n = 40; sp.points.add(n - 1)
    for k in range(n):
        t = k / (n - 1); x = -16 + 32 * t
        sp.points[k].co = (x, y, z0 - 0.9 * 4 * t * (1 - t) + 0.25 * t, 1)
    co = bpy.data.objects.new('w07_%d' % i, cu); sc.collection.objects.link(co); cu.materials.append(WIRE)
    WIRES.append((y, z0))


def wire_z(i, x):
    y, z0 = WIRES[i]; t = (x + 16) / 32.0
    return z0 - 0.9 * 4 * t * (1 - t) + 0.25 * t


# ---------------- the flock: copies of the CC0 raven, perched, then lifting in a wave per note ----------------
CROWM = CMESH.data.materials[0]
FLOCK = []
for i in range(3):
    xs = sorted(random.uniform(-9.5, 9.5) for _ in range(14))
    for x in xs:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=os.environ['CROW_GLB'])
        new = [o for o in bpy.data.objects if o not in before]
        for o in new:
            if not o.users_collection: sc.collection.objects.link(o)
        root = next(o for o in new if o.parent is None and o.name.startswith('root'))
        arm_ = next(o for o in new if o.type == 'ARMATURE'); mesh_ = next(o for o in new if o.type == 'MESH' and 'raven' in o.name)
        for o in new:
            if o.name.startswith('Icosphere'): o.hide_render = True
        mesh_.data.materials.clear(); mesh_.data.materials.append(CROWM)
        for p_ in mesh_.data.polygons: p_.use_smooth = True
        sd = mesh_.modifiers.new('subd', 'SUBSURF'); sd.levels = 1; sd.render_levels = 2
        outline(mesh_, 0.0035)
        if arm_.animation_data: arm_.animation_data.action = None
        holder = empty('perch_%d_%d' % (i, len(FLOCK)))
        root.parent = holder; root.rotation_mode = 'XYZ'; root.rotation_euler = (0, 0, math.radians(random.choice((-90, 90)) + random.uniform(-25, 25)))
        lift = NOTES[i] + (x + 9.5) / 19.0 * 14 + random.uniform(-1.5, 1.5)        # the wave runs along the wire
        FLOCK.append(dict(h=holder, arm=arm_, x=x, wire=i, lift=lift, ph=random.uniform(0, 34),
                          vx=random.uniform(-1.6, 1.6), vy=random.uniform(0.8, 2.6), vz=random.uniform(2.4, 3.6), turn=random.uniform(-40, 40)))


def apply_to(arm_, P):
    for b in arm_.pose.bones:
        if b.name in P:
            l, q, s_ = P[b.name]; b.rotation_mode = 'QUATERNION'; b.location = l; b.rotation_quaternion = q; b.scale = s_


STAND = capture('stand', 0)
FLY = [capture('fly', k) for k in range(0, 34)]
for c in FLOCK: c['arm'].animation_data_clear() if c['arm'].animation_data else None


def flock(f):
    fp = f - (f - 1) % 2                                              # birds on twos
    for c in FLOCK:
        k = fp - c['lift']
        x0 = c['x']; z0 = wire_z(c['wire'], x0); y0 = WIRES[c['wire']][0]
        if k < 0:
            c['h'].location = (x0, y0, z0 + 0.02)
            apply_to(c['arm'], STAND)
        else:
            t = k / 24.0
            c['h'].location = (x0 + c['vx'] * t, y0 + c['vy'] * t, z0 + 0.02 + c['vz'] * t + 0.6 * math.sin(min(t, 0.3) * 10))
            c['h'].rotation_mode = 'XYZ'; c['h'].rotation_euler = (math.radians(-25 * min(1, k / 4)), 0, math.radians(c['turn'] * min(1, k / 8)))
            apply_to(c['arm'], FLY[int(c['ph'] + k * 1.5) % 34])


# ---------------- the horn: each note shakes the bracket; after the missing fourth it keeps trembling ----------------
def horn_shake(f):
    a = 0.0
    for n in NOTES:
        if f >= n: a += 1.1 * math.exp(-(f - n) / 9.0) * math.sin((f - n) * 2.9)
    if f >= FOURTH - 2: a += 0.30 * math.sin(f * 3.7) * min(1, (f - FOURTH + 2) / 6.0)
    arm.rotation_mode = 'XYZ'; arm.rotation_euler = (math.radians(a * 0.6), math.radians(a), 0)


# ---------------- camera: low angle up at the pole, a slow push on ones ----------------
cam_d.lens = 26
HORN_C = hA.matrix_world.translation.copy()


def cam07(f):
    k = (f - 1) / (NF - 1); kk = k * k * (3 - 2 * k)
    p = Vector((-0.75 + 0.10 * kk, -2.9 + 0.12 * kk, -1.55)) + Vector((0.004 * math.sin(f * 0.37), 0, 0.003 * math.sin(f * 0.61)))
    tgt = Vector((0.35, 6.0, 2.6))
    return p, (tgt - p).to_track_quat('-Z', 'Y')


from bpy_extras.object_utils import world_to_camera_view
META = {}
frames = list(range(1, NF + 1)) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    sc.frame_set(f)
    flock(f); horn_shake(f)
    p, q = cam07(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    sv = world_to_camera_view(sc, cam, cam.location + Vector((-0.62, 1.0, 0.24)).normalized() * 1000)
    hv = world_to_camera_view(sc, cam, hA.matrix_world @ Vector((0, 0.67, 0)))
    META[f] = dict(sx=sv.x, sy=1 - sv.y, hx=hv.x, hy=1 - hv.y)
    sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    print('frame', f, flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
print('SUN_SCREEN', META[frames[0]]['sx'], META[frames[0]]['sy'])
