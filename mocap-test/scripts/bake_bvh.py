"""Blender (bpy, background): MediaPipe JSON -> keyed empties -> armature with
track constraints (PosePipe-style) -> baked action -> BVH + FBX.
Usage: blender -b --factory-startup -P bake_bvh.py -- in.json out_basename
"""
import bpy, json, sys, math
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
src, outbase = argv[0], argv[1]
D = json.load(open(src))
fps = D["fps"]; W, H = D["w"], D["h"]
frames = D["frames"]

# fill missed detections with previous frame
last = None
for i, f in enumerate(frames):
    if f is None: frames[i] = last
    else: last = f
first = next(i for i, f in enumerate(frames) if f)
for i in range(first): frames[i] = frames[first]

def w2b(p):  # mediapipe world (x right, y down, z toward camera-ish) -> Blender Z-up
    return Vector((p[0], p[2], -p[1]))

def mid(a, b): return (a + b) * 0.5

def points(f):
    w = [w2b(p) for p in f["world"]]
    pelvis = mid(w[23], w[24]); chest = mid(w[11], w[12]); earm = mid(w[7], w[8])
    return {
        "pelvis": pelvis, "spine": pelvis.lerp(chest, 0.35), "chest": chest,
        "headbase": earm, "nose": w[0],
        "l_hip": w[23], "l_knee": w[25], "l_ankle": w[27], "l_toe": w[31],
        "r_hip": w[24], "r_knee": w[26], "r_ankle": w[28], "r_toe": w[32],
        "l_sh": w[11], "l_elb": w[13], "l_wri": w[15], "l_hand": mid(w[17], w[19]),
        "r_sh": w[12], "r_elb": w[14], "r_wri": w[16], "r_hand": mid(w[18], w[20]),
    }

# root translation: X from image track (scaled to metres), Z so lowest foot sits on floor
def root_offset(f, P):
    im = f["img"]
    px = (im[23][0] + im[24][0]) / 2 * W / H
    sh = Vector(((im[11][0] + im[12][0]) / 2 * W / H, (im[11][1] + im[12][1]) / 2))
    hp = Vector((px, (im[23][1] + im[24][1]) / 2))
    s = (P["chest"] - P["pelvis"]).length / max((sh - hp).length, 1e-4)
    return px, s

P_all = [points(f) for f in frames]
raw = [root_offset(f, P) for f, P in zip(frames, P_all)]
s_med = sorted(r[1] for r in raw)[len(raw) // 2]
x0 = raw[0][0]
offs = []
for P, (px, _) in zip(P_all, raw):
    low = min(P[k].z for k in ("l_ankle", "r_ankle", "l_toe", "r_toe"))
    offs.append(Vector(((px - x0) * s_med, 0, -low + 0.05)))

scn = bpy.context.scene
for o in list(bpy.data.objects): bpy.data.objects.remove(o)
scn.render.fps = round(fps); scn.frame_start = 1; scn.frame_end = len(frames)

# keyed empties (PosePipe keys empties per landmark the same way)
E = {}
for k in P_all[0]:
    e = bpy.data.objects.new("T_" + k, None); scn.collection.objects.link(e); E[k] = e
for i, (P, o) in enumerate(zip(P_all, offs)):
    for k, e in E.items():
        e.location = P[k] + o
        e.keyframe_insert("location", frame=i + 1)

# bones: name, head pt, tail pt, parent
B = [("Hips", "pelvis", "spine", None), ("Spine", "spine", "chest", "Hips"),
     ("Neck", "chest", "headbase", "Spine"), ("Head", "headbase", "nose", "Neck"),
     ("LeftUpLeg", "l_hip", "l_knee", "Hips"), ("LeftLeg", "l_knee", "l_ankle", "LeftUpLeg"),
     ("LeftFoot", "l_ankle", "l_toe", "LeftLeg"),
     ("RightUpLeg", "r_hip", "r_knee", "Hips"), ("RightLeg", "r_knee", "r_ankle", "RightUpLeg"),
     ("RightFoot", "r_ankle", "r_toe", "RightLeg"),
     ("LeftShoulder", "chest", "l_sh", "Spine"), ("LeftArm", "l_sh", "l_elb", "LeftShoulder"),
     ("LeftForeArm", "l_elb", "l_wri", "LeftArm"), ("LeftHand", "l_wri", "l_hand", "LeftForeArm"),
     ("RightShoulder", "chest", "r_sh", "Spine"), ("RightArm", "r_sh", "r_elb", "RightShoulder"),
     ("RightForeArm", "r_elb", "r_wri", "RightArm"), ("RightHand", "r_wri", "r_hand", "RightForeArm")]

# rest pose: mean bone lengths along frame-0 directions
L = {n: sum((P[t] - P[h]).length for P in P_all) / len(P_all) for n, h, t, _ in B}
P0 = {k: v + offs[0] for k, v in P_all[0].items()}
arm = bpy.data.armatures.new("MocapRig"); rig = bpy.data.objects.new("MocapRig", arm)
scn.collection.objects.link(rig); bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
heads = {}
for n, h, t, par in B:
    eb = arm.edit_bones.new(n)
    hd = heads.get(par + "_tail") if par and h == B[[b[0] for b in B].index(par)][2] else None
    eb.head = hd if hd is not None else P0[h]
    eb.tail = eb.head + (P0[t] - P0[h]).normalized() * L[n]
    heads[n + "_tail"] = eb.tail.copy()
    if par:
        eb.parent = arm.edit_bones[par]
        eb.use_connect = (eb.head - arm.edit_bones[par].tail).length < 1e-5
bpy.ops.object.mode_set(mode="POSE")

side = {"Hips": ("l_hip", "r_hip"), "Spine": ("l_sh", "r_sh")}
for n, h, t, par in B:
    pb = rig.pose.bones[n]
    if n == "Hips":
        c = pb.constraints.new("COPY_LOCATION"); c.target = E["pelvis"]
    c = pb.constraints.new("DAMPED_TRACK"); c.target = E[t]
    if n in side:  # recover twist (pelvis/chest yaw) from left/right landmarks
        a, b = side[n]
        xr = rig.data.bones[n].x_axis
        sgn = (P0[a] - P0[b]).dot(xr)
        c = pb.constraints.new("LOCKED_TRACK"); c.target = E[a]
        c.lock_axis = "LOCK_Y"; c.track_axis = "TRACK_X" if sgn > 0 else "TRACK_NEGATIVE_X"

for pb in rig.pose.bones: pb.bone.select = True
bpy.ops.nla.bake(frame_start=1, frame_end=len(frames), only_selected=True, visual_keying=True,
                 clear_constraints=True, use_current_action=True, bake_types={"POSE"})
bpy.ops.object.mode_set(mode="OBJECT")
for e in E.values(): bpy.data.objects.remove(e)

rig.select_set(True); bpy.context.view_layer.objects.active = rig  # rig is the only object left
bpy.ops.export_scene.fbx(filepath=outbase + ".fbx", use_selection=True, object_types={"ARMATURE"},
                         add_leaf_bones=False, bake_anim=True, bake_anim_use_all_actions=False,
                         bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
                         bake_anim_simplify_factor=0.0)
bpy.ops.wm.save_as_mainfile(filepath=outbase + ".blend")
# BVH convention is Y-up and Blender's exporter writes armature space as-is:
# bake a Z-up -> Y-up turn into the rest pose (bone-local channels stay valid)
rig.rotation_euler.x = -math.pi / 2
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
bpy.ops.export_anim.bvh(filepath=outbase + ".bvh", frame_start=1, frame_end=len(frames),
                        rotate_mode="NATIVE", root_transform_only=True)

# jitter: mean |accel| of extremities (world, m/frame^2 -> mm)
def acc(k):
    v = [P[k] for P in P_all]
    a = [(v[i + 1] - 2 * v[i] + v[i - 1]).length for i in range(1, len(v) - 1)]
    return 1000 * sum(a) / len(a)
print("JITTER_mm_per_frame2", {k: round(acc(k), 1) for k in ("l_ankle", "r_ankle", "l_wri", "r_wri", "l_toe", "pelvis")})
print("DONE", len(frames), "frames ->", outbase)
