"""Shot 17 v2 - the day-side insert for the curve mirror, rendered in 3D (Sam: "the person in the mirror looks like a block of
shapes"). The real Kiriyama at 5 PM, the approved shot-04 street + light: Sam's house (gable, plaster, a lit genkan) and his mother
(Codex's Ep2 mom rig, same cast recipe) on the step, one hand cupped to her mouth, calling up and down the street. She cannot see him.
Characters on twos. Writes day_NNN.png (square, RGBA: sky transparent) for paint_day17.draw().
usage: blender -b --python build_s17_day.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math
H17 = os.path.dirname(os.path.abspath(__file__))
S04 = os.path.normpath(os.path.join(H17, '..', '..', '04_ride', 'src'))
CASTD = os.path.normpath(os.path.join(H17, '..', '..', '..', 'assets', 'cast_v2'))
_s = open(os.path.join(S04, 'build_s04.py'), encoding='utf-8').read()
_s = _s[:_s.index('\nMETA = {}')]
_s = _s.replace("HERE = os.path.dirname(os.path.abspath(__file__)); D = HERE", "HERE = %r; D = HERE" % S04)
exec(_s)
from mathutils import Quaternion, Matrix, Vector
NF = 72
for o in R1['objs'] + R2['objs']: o.hide_render = True
for o in bpy.data.objects:                                                    # no susuki; clear the plot for Sam's house
    if o.type == 'MESH' and any(m and m.name.startswith('susuki') for m in o.data.materials): o.hide_render = True
HX = -14.0                                                                    # the house sits on the near side, uphill of the shop
for o in list(bpy.data.objects):
    if o.parent == ROAD and o.type == 'MESH' and (o.name.startswith('house') or o.name.startswith('tree_ext')) \
            and abs(o.location.x - HX) < 9 and o.location.y < -3:
        o.hide_render = True
    if o.name.startswith('near_wall'): o.hide_render = True                  # the block wall would hide the doorstep
# Sam's house: two floors, gable, plaster; the genkan door glows warm (sliding lattice door, frosted glass)
hs = house(HX, -10.0, 7.6, 6.0, 5.8, ROOF[0], WALLS[0], 'gable', 16, r=random.Random(17))
FY = -10.0 + 3.0                                                              # front face of the house
GEN = emis('genkan_glow', (1.0, 0.80, 0.50), 2.2)
bm = bmesh.new(); box(bm, (HX + 0.6, FY + 0.03, 1.05), (1.7, 0.05, 2.0), 0); g_ = obj('genkan', bm, GEN, 0)
bm = bmesh.new()
for k in range(5): box(bm, (HX + 0.6 - 0.85 + k * 0.425, FY + 0.07, 1.05), (0.05, 0.04, 2.02), 0)
for k in range(6): box(bm, (HX + 0.6, FY + 0.07, 0.05 + k * 0.40), (1.75, 0.04, 0.05), 0)
obj('genkan_frame', bm, T('door_wood', (0.42, 0.28, 0.20)), 4)
bm = bmesh.new(); box(bm, (HX + 0.6, FY + 0.55, 0.09), (2.4, 1.1, 0.18), 0); obj('step', bm, KERB4, 4)   # concrete step
bm = bmesh.new(); box(bm, (HX + 2.3, FY + 0.06, 1.55), (0.30, 0.03, 0.40), 0); obj('nameplate', bm, T('plate_w', (0.90, 0.88, 0.82)), 3)
lp = bpy.data.lights.new('genkan_lamp', 'POINT'); lp.energy = 60; lp.color = (1.0, 0.78, 0.5); lp.shadow_soft_size = 0.3
lo = bpy.data.objects.new('genkan_lamp', lp); sc.collection.objects.link(lo); lo.parent = ROAD; lo.location = (HX + 0.6, FY + 1.0, 2.3)
plane('drive', HX - 3.5, HX + 3.5, -6.2, FY, 0.04, T('drive', (0.62, 0.60, 0.58), tex=tex_patchy(0.4, 5.0, 0.85, 1.06)))


def load_char(name, loc, yaw):
    with bpy.data.libraries.load(os.path.join(CASTD, name + '.blend'), link=False) as (src, dst):
        dst.objects = [n for n in src.objects]
    new = [o for o in dst.objects if o is not None and o.type not in ('LIGHT', 'CAMERA')]
    for o in new: sc.collection.objects.link(o)
    rig = next(o for o in new if o.type == 'ARMATURE' and o.parent is None)
    rig.parent = ROAD; rig.location = loc; rig.rotation_mode = 'XYZ'; rig.rotation_euler = (0, 0, math.radians(yaw))
    for pb in rig.pose.bones: pb.rotation_mode = 'QUATERNION'
    return rig, new


def rot(rig, bone, axis, deg):
    pb = rig.pose.bones.get(bone)
    if pb is None: return
    ax = pb.bone.matrix_local.to_3x3().inverted() @ Vector(axis)
    pb.rotation_quaternion = Quaternion(ax, math.radians(deg)) @ pb.rotation_quaternion


def ease(t):
    t = max(0.0, min(1.0, t)); return t * t * (3 - 2 * t)


MOMP = (HX + 0.6, FY + 0.75, 0.18)
mom, momo = load_char('mom', MOMP, 0)                                         # VRM faces -Y; yaw 180 = faces +Y = the street
mom.rotation_euler.z = math.radians(180)
BASE = {pb.name: pb.matrix_basis.copy() for pb in mom.pose.bones}
for o in momo:                                                                # the Ep2 apron is a flat board: slim it (Codex noted)
    if o.type == 'MESH' and o.name.startswith('Mom_apron'): o.hide_render = True        # home in the evening: no shop apron
# fingers: relaxed curl computed in T-pose, re-applied each frame
keep = {pb.name: pb.matrix_basis.copy() for pb in mom.pose.bones}
for pb in mom.pose.bones: pb.matrix_basis = Matrix.Identity(4)
_curl_fingers(mom, 1, 0.35); _curl_fingers(mom, -1, 0.55)
FING = {pb.name: pb.rotation_quaternion.copy() for pb in mom.pose.bones if any(k in pb.name for k in ('Index', 'Middle', 'Ring', 'Little', 'Thumb'))}
for pb in mom.pose.bones: pb.matrix_basis = keep[pb.name]
# right hand cupped beside her mouth: IK wrist ~9 cm below/in front of the mouth corner (J11), fingers up, palm toward her cheek
tR = empty('mom_ikR', ROAD, (0, 0, 0)); aR = empty('mom_aimR', ROAD, (0, 0, 0)); pR = empty('mom_palmR', ROAD, (0, 0, 0))
poleR = empty('mom_poleR', ROAD, (MOMP[0] - 0.6, MOMP[1] + 0.1, 0.9))
cI = mom.pose.bones['J_Bip_R_LowerArm'].constraints.new('IK'); cI.target = tR; cI.pole_target = poleR; cI.chain_count = 2
cD = mom.pose.bones['J_Bip_R_Hand'].constraints.new('DAMPED_TRACK'); cD.target = aR; cD.track_axis = 'TRACK_Y'
hb = mom.data.bones['J_Bip_R_Hand']; R0 = hb.matrix_local.to_3x3()
best = max((('TRACK_X', R0.col[0]), ('TRACK_NEGATIVE_X', -R0.col[0]), ('TRACK_Z', R0.col[2]), ('TRACK_NEGATIVE_Z', -R0.col[2])), key=lambda a: a[1].dot(Vector((0, 0, -1))))
cL = mom.pose.bones['J_Bip_R_Hand'].constraints.new('LOCKED_TRACK'); cL.target = pR; cL.lock_axis = 'LOCK_Y'; cL.track_axis = best[0]
# v3 (Sam: "I can see only one hand of her mother"): she faces +y, so HER right is +x. The v2 elbow pole sat at -x (her left),
# folding the arm behind her head. Poles now on the correct sides, and BOTH hands cup the mouth (a two-hand call), so both read.
poleR.location = (MOMP[0] + 0.55, MOMP[1] - 0.45, 1.00)                    # v4: elbows out IN FRONT (behind = forearms hidden)
tL = empty('mom_ikL', ROAD, (0, 0, 0)); aL = empty('mom_aimL', ROAD, (0, 0, 0)); pL = empty('mom_palmL', ROAD, (0, 0, 0))
poleL = empty('mom_poleL', ROAD, (MOMP[0] - 0.55, MOMP[1] - 0.45, 1.00))
cIL = mom.pose.bones['J_Bip_L_LowerArm'].constraints.new('IK'); cIL.target = tL; cIL.pole_target = poleL; cIL.chain_count = 2
cDL = mom.pose.bones['J_Bip_L_Hand'].constraints.new('DAMPED_TRACK'); cDL.target = aL; cDL.track_axis = 'TRACK_Y'
hbL = mom.data.bones['J_Bip_L_Hand']; R0L = hbL.matrix_local.to_3x3()
bestL = max((('TRACK_X', R0L.col[0]), ('TRACK_NEGATIVE_X', -R0L.col[0]), ('TRACK_Z', R0L.col[2]), ('TRACK_NEGATIVE_Z', -R0L.col[2])), key=lambda a: a[1].dot(Vector((0, 0, -1))))
cLL = mom.pose.bones['J_Bip_L_Hand'].constraints.new('LOCKED_TRACK'); cLL.target = pL; cLL.lock_axis = 'LOCK_Y'; cLL.track_axis = bestL[0]
MOUTH = {}


def lowest_z(objs):
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); zs = []
    for o in objs:
        if o.type != 'MESH' or 'Outline' in o.name: continue
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world
        zs += [(mw @ v.co).z for i, v in enumerate(me.vertices) if i % 5 == 0]; ev.to_mesh_clear()
    return min(zs)


def act(f):
    fp = f                                                                    # v3: on ones
    for c in (cI, cD, cL, cIL, cDL, cLL): c.influence = 0.0
    for pb in mom.pose.bones: pb.matrix_basis = BASE[pb.name].copy()
    for n_, q_ in FING.items(): mom.pose.bones[n_].rotation_quaternion = q_.copy()
    rot(mom, 'J_Bip_L_UpperArm', (0, 1, 0), 66); rot(mom, 'J_Bip_R_UpperArm', (0, 1, 0), -40)
    rot(mom, 'J_Bip_L_LowerArm', (0, 0, 1), -16)
    # she leans out from the step and looks up the street, then down it; calls twice
    look = math.sin((fp - 1) * 0.075) * 0.9
    rot(mom, 'J_Bip_C_Spine', (1, 0, 0), 6); rot(mom, 'J_Bip_C_Chest', (0, 0, 1), 9 * look)
    rot(mom, 'J_Bip_C_Neck', (0, 0, 1), 16 * look); rot(mom, 'J_Bip_C_Head', (0, 0, 1), 12 * look); rot(mom, 'J_Bip_C_Head', (1, 0, 0), -5)
    rot(mom, 'J_Bip_C_Hips', (0, -1, 0), 3); rot(mom, 'J_Bip_L_UpperLeg', (1, 0, 0), -4); rot(mom, 'J_Bip_L_LowerLeg', (1, 0, 0), 8)
    bpy.context.view_layer.update()
    hm = mom.matrix_world @ mom.pose.bones['J_Bip_C_Head'].matrix
    head = hm.translation; up = (hm.to_3x3() @ Vector((0, 1, 0))).normalized()
    fwd = (hm.to_3x3() @ Vector((0, 0, 1))).normalized()                       # VRoid head bone: local +Z = the face direction
    right = up.cross(fwd).normalized()
    mouth = head + up * 0.02 + fwd * 0.07
    inv = ROAD.matrix_world.inverted()
    tR.location = inv @ (mouth - right * 0.095 + fwd * 0.02 - up * 0.10)          # v3: a funnel beside the mouth, mouth stays visible
    aR.location = inv @ (mouth - right * 0.13 + up * 0.25 + fwd * 0.12)
    pR.location = inv @ (mouth + right * 0.40)
    tL.location = inv @ (mouth + right * 0.095 + fwd * 0.02 - up * 0.10)
    aL.location = inv @ (mouth + right * 0.13 + up * 0.25 + fwd * 0.12)
    pL.location = inv @ (mouth - right * 0.40)
    raise_ = ease((fp - 3) / 6.0); raiseL = ease((fp - 5) / 6.0)          # the second hand follows ~2 frames later
    for c in (cI, cD, cL): c.influence = raise_
    for c in (cIL, cDL, cLL): c.influence = raiseL
    call = max(0.0, math.sin((fp - 9) * math.pi / 14)) if fp >= 9 else 0.0       # "Sam!" ... "Sam!"
    for o in momo:
        ks = o.data.shape_keys if o.type == 'MESH' and o.data.shape_keys else None
        if not ks: continue
        for kb_ in ks.key_blocks:
            if kb_.name.endswith('Fcl_MTH_A'): kb_.value = 0.55 * call
            if kb_.name.endswith('Fcl_BRW_Sorrow'): kb_.value = 0.35
    bpy.context.view_layer.update()
    gz = (ROAD.matrix_world @ Vector((MOMP[0], MOMP[1], 0.18))).z
    mom.location.z -= lowest_z(momo) - gz


# camera: from across the street, at the curve mirror's height, looking down at the doorstep (what the mirror sees)
sc.render.resolution_x = sc.render.resolution_y = int(1200 * SCALE); sc.render.resolution_percentage = 100
camd.lens = 40; camd.dof.use_dof = False                                    # probe 1: 8 m away she was a fifth of the frame
CP = ROAD.matrix_world @ Vector((HX + 1.9, -2.3, 2.05)); TG = ROAD.matrix_world @ Vector((HX + 0.5, FY + 0.75, 1.15))
cam.location = CP; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = (TG - CP).to_track_quat('-Z', 'Y')
frames = range(1, NF + 1) if FR == 'all' else [int(x) for x in FR.split(',')]
done = set()
for f in frames:
    fp = f
    dst = os.path.join(OUT, 'day_%03d.png' % f)
    if fp in done and fp != f:                                                # on twos: copy the held frame
        import shutil; shutil.copyfile(os.path.join(OUT, 'day_%03d.png' % fp), dst); continue
    sc.frame_set(fp); act(fp); bpy.context.view_layer.update()
    sc.render.filepath = dst; bpy.ops.render.render(write_still=True); done.add(fp)
    print('day frame', f, flush=True)
