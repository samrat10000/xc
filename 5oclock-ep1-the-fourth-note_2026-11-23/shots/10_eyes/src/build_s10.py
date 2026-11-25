"""5 O'CLOCK Ep1 "The Fourth Note" - shot 10 "Grandma's eyes" (3.5 s, 84 f @24). The frozen town of shot 08 (exact continuity: Grandma
mid-watering, the water hanging in the air). Slow telephoto push in on her face from across the road while Sam passes between us,
out of focus in the foreground. Her body never moves; only her eyes slide to follow him (on ones). Her lips do not move.
Line (V.O., no lip movement): "Don't look at the mirror, Sam." at 32.4 s = f22 of this shot.
Known deviation from the plan: Sam coasts slowly past instead of walking the bike (walk cycle beside a bike not built yet).
usage: blender -b --python build_s10.py -- <ABS outdir> <scale> <frames|all>"""
import os, sys, math
H10 = os.path.dirname(os.path.abspath(__file__))
S08 = os.path.normpath(os.path.join(H10, '..', '..', '08_frozen', 'src'))
_s = open(os.path.join(S08, 'build_s08.py'), encoding='utf-8').read()
_s = _s[:_s.index('# ---------------- the glide')]
_s = _s.replace("HERE8 = os.path.dirname(os.path.abspath(__file__))", "HERE8 = %r" % S08)
exec(_s)
NF = 84
for o in bpy.data.objects:
    if o.type == 'MESH' and any(m and m.name.startswith('susuki') for m in o.data.materials): o.hide_render = True


def sam_x(f):                                                   # Sam passes between the lens and Grandma at f40, slowly
    return 7.2 + 1.8 * (f - 40) / 24.0


# ---------------- her eyes follow him (eye bones only, on ones) ----------------
EYES = [b for b in gm.pose.bones if 'FaceEye' in b.name]
print('eye bones', [b.name for b in EYES])
for b in EYES: b.rotation_mode = 'QUATERNION'
E0 = {b.name: b.rotation_quaternion.copy() for b in EYES}


def eyes(f):
    head = gm.matrix_world @ PB(gm, 'J_Bip_C_Head').head
    sam = R1['B']['root'].matrix_world.translation + Vector((0, 0, 1.45))
    d_w = (sam - head).normalized()
    d_l = (gm.matrix_world.to_3x3().inverted() @ d_w).normalized()      # into her armature space (her front = -Y)
    yaw = math.degrees(math.atan2(d_l.x, -d_l.y)); pitch = math.degrees(math.asin(max(-1, min(1, d_l.z))))
    yaw = max(-28, min(28, yaw)); pitch = max(-12, min(10, pitch))
    for b in EYES:
        b.rotation_quaternion = E0[b.name]
        _rot_arm(gm, b.name, (0, 0, 1), yaw * 0.9)
        _rot_arm(gm, b.name, (1, 0, 0), -pitch * 0.7)


# ---------------- camera: across the road, telephoto, slow push to her face, focus on her eyes ----------------
camd.dof.use_dof = True; camd.dof.aperture_fstop = 2.0; camd.clip_start = 0.05
HEADW = gm.matrix_world @ PB(gm, 'J_Bip_C_Head').head
# v4: the telephoto sees every frozen leaf between the lens and her face as a frame-filling blur - clear that corridor
_c0 = road_pt(7.45, -0.15, 1.30); _ax = (HEADW - _c0); _L = _ax.length; _ax.normalize()
for o in bpy.data.objects:
    if o.name.startswith('leaf08'):
        v = o.matrix_world.translation - _c0; t_ = max(0.0, min(_L, v.dot(_ax)))
        if (v - _ax * t_).length < 0.9: o.hide_render = True


def cam10(f):
    k = ease((f - 1) / 83.0)
    camd.lens = 85 + 115 * k
    p = road_pt(7.45 - 0.05 * k, -0.15, 1.30) + Vector((0.004 * math.sin(f * 0.21), 0, 0.003 * math.sin(f * 0.33)))
    tgt = HEADW + Vector((0, 0, 0.05 - 0.20 * (1 - k)))
    camd.dof.focus_distance = (tgt - p).length
    return p, (tgt - p).to_track_quat('-Z', 'Y')


META = {}
frames = range(1, NF + 1) if FR == 'all' else [int(x) for x in FR.split(',')]
for f in frames:
    sc.frame_set(f)
    pose_rider(R1, f); pour(f + 120); bpy.context.view_layer.update(); pose_strings(R1, f)   # v4: the water keeps pouring (continues 08)
    eyes(f)
    p, q = cam10(f); cam.location = p; cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = q
    bpy.context.view_layer.update()
    s_ = proj(cam.location + SUN * 1000); h_ = proj(cam.location + Vector((0, 1, 0)) * 5000)
    gpoly, vis = glass_proj()
    META[f] = dict(sx=s_[0], sy=s_[1], hy=h_[1], glass=gpoly, refl=bool(vis), samx=0.5)
    sc.render.filepath = os.path.join(OUT, 'cel_%03d.png' % f); bpy.ops.render.render(write_still=True)
    if vis:
        for o in FAR: o.visible_camera = False
        pm, qm = mirror_cam(p, q); cam.location = pm; cam.rotation_quaternion = qm
        bpy.context.view_layer.update()
        sc.render.filepath = os.path.join(OUT, 'refl_%03d.png' % f); bpy.ops.render.render(write_still=True)
        for o in FAR: o.visible_camera = True
        cam.location = p; cam.rotation_quaternion = q
    print('frame', f, flush=True)
json.dump(META, open(os.path.join(OUT, 'meta.json'), 'w'))
