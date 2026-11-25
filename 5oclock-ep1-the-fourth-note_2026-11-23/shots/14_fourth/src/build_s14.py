"""5 O'CLOCK Ep1 "The Fourth Note" - shot 14 "The fourth note" (3.5 s, 84 f @24).
f1-36: ECU of the reflection's mouth inside the glass (shot 13's night-lit mirror-Sam): he breathes in and hums the fourth note.
f37-84: hard cut wide on the curve mirror at 5 PM; at f40 the glass cracks outward in a ring (comp: 4 hand-keyed crack drawings, glints).
Writes ecu_NNN.png (f1-36, 1080x1920 night pass) and cel_NNN.png (f37-84) + meta.json.
usage: blender -b --python build_s14.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math, json
A14 = sys.argv[sys.argv.index('--') + 1:]
H14 = os.path.dirname(os.path.abspath(__file__))
S13 = os.path.normpath(os.path.join(H14, '..', '..', '13_mirrorsam', 'src'))
S11 = os.path.normpath(os.path.join(H14, '..', '..', '11_mirror', 'src'))
_s = open(os.path.join(S13, 'build_s13.py'), encoding='utf-8').read()
_s = _s[:_s.index('\nMETA = {}')]                                 # line-start marker: the text also occurs inside the reused file
_s = _s.replace("H13 = os.path.dirname(os.path.abspath(__file__))", "H13 = %r" % S13)
sys.argv = [sys.argv[0], '--'] + A14
__file__ = os.path.join(S13, 'build_s13.py')
exec(_s)
NF = 84; CUT = 36
for o in SAM: o.hide_render = True                                  # the real Sam is not in this shot
for o in bpy.data.objects:
    if o.name.startswith('Headphone') and o not in MS: o.hide_render = True
bpy.context.view_layer.update()
MOUTH = mrig.matrix_world @ mrig.pose.bones['J_Bip_C_Head'].head + Vector((0.0, -0.075, -0.025))
mrig.pose.bones['J_Bip_R_LowerArm'].constraints[0].influence = 0.0


def ecu_act(f):
    for pb in mrig.pose.bones: pb.matrix_basis = MBASE[pb.name].copy()
    inhale = ease((f - 10) / 8.0) * (1 - ease((f - 18) / 6.0))
    mrot('J_Bip_C_Chest', (1, 0, 0), -3 * inhale); mrot('J_Bip_C_Head', (1, 0, 0), -2 * inhale)
    for v in 'AIUEO': MK['Face.M_F00_000_00_Fcl_MTH_' + v].value = 0.0
    MK['Face.M_F00_000_00_Fcl_MTH_Fun'].value = 0.45 * (1 - ease((f - 8) / 6.0))
    MK['Face.M_F00_000_00_Fcl_MTH_O'].value = 0.22 * inhale                        # breath in through the lips
    if f >= 20:                                                                     # the hum: lips almost closed, trembling
        MK['Face.M_F00_000_00_Fcl_MTH_U'].value = 0.18 + 0.05 * math.sin(f * 2.7)
    MK['Face.M_F00_000_00_Fcl_EYE_Close'].value = 0.0


def cam_wide(f):
    k = ease((f - CUT) / 48.0)
    p = MPOS - FWD * 2.4 + SIDE * 0.55 + Vector((0, 0, -1.35)) + (MPOS - (MPOS - FWD * 2.4)) * 0.03 * k
    return p, (MPOS + Vector((0, 0, -0.25)) - p).to_track_quat('-Z', 'Y')


META = {}
frames = list(range(1, NF + 1)) if FR == 'all' else [int(x) for x in FR.split(',')]
RX, RY = sc.render.resolution_x, sc.render.resolution_y
camE_d = bpy.data.cameras.new('camE'); camE_d.lens = 75; camE_d.sensor_fit = 'VERTICAL'; camE_d.sensor_height = 36
camE_d.dof.use_dof = True; camE_d.dof.aperture_fstop = 11.0   # v4: the whole mouth sharp
camE = bpy.data.objects.new('camE', camE_d); sc.collection.objects.link(camE)
for f in frames:
    sc.frame_set(f)
    if f <= CUT:
        ecu_act(f)
        k = ease((f - 1) / 35.0)
        camE.location = MOUTH + Vector((0.01, -0.34 + 0.05 * k, 0.01)); camE.rotation_mode = 'QUATERNION'
        camE.rotation_quaternion = (MOUTH + Vector((0, 0, 0.01)) - camE.location).to_track_quat('-Z', 'Y')
        camE_d.dof.focus_distance = (MOUTH - camE.location).length
        for o in DAY: o.hide_render = True
        for o in NIGHT: o.hide_render = False
        sc.camera = camE; sc.render.resolution_x, sc.render.resolution_y = RX, RY
        sc.render.filepath = os.path.join(OUT, 'ecu_%03d.png' % f); bpy.ops.render.render(write_still=True)
        for o in DAY: o.hide_render = False
        for o in NIGHT: o.hide_render = True
        META[f] = dict(ecu=True, mx=0.5, my=0.5, mr=0.1, sx=0.885, sy=0.705, leaf=[0, 0, False])   # comp reads sx/sy from the first frame
    else:
        p, q = cam_wide(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
        cam_d.lens = 34; cam_d.dof.use_dof = False
        bpy.context.view_layer.update()
        c = world_to_camera_view(sc, cam, MPOS); e = world_to_camera_view(sc, cam, MPOS + SIDE * R)
        s_ = world_to_camera_view(sc, cam, cam.location + SUN * 100)
        META[f] = dict(mx=c.x, my=1 - c.y, mr=abs(e.x - c.x), sx=s_.x, sy=1 - s_.y, leaf=[0, 0, False])
        sc.camera = cam; sc.render.resolution_x, sc.render.resolution_y = RX, RY
        sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    print('frame', f, flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
k1 = min(k for k in META if 'sx' in META[k]) if any('sx' in v for v in META.values()) else None
if k1: print('SUN', META[k1]['sx'], META[k1]['sy'])
