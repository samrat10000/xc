"""MakeHuman (CC0) base mesh loader: targets -> body + eyes/teeth/tongue, default rig + weights,
posing helpers. Output in Blender metres, Z up, facing -Y."""
import os, json, math
import numpy as np
import bpy, bmesh
from mathutils import Vector, Euler, Quaternion, Matrix

MH = '/tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/mh'
_obj = None

def load_obj():
    global _obj
    if _obj: return _obj
    vs, vts, faces = [], [], []
    g = None
    for ln in open(f'{MH}/base.obj'):
        if ln.startswith('v '): vs.append([float(x) for x in ln.split()[1:4]])
        elif ln.startswith('vt '): vts.append([float(x) for x in ln.split()[1:3]])
        elif ln.startswith('g '): g = ln.split()[1]
        elif ln.startswith('f '):
            idx = [p.split('/') for p in ln.split()[1:]]
            faces.append((g, [int(a[0]) - 1 for a in idx], [int(a[1]) - 1 if len(a) > 1 and a[1] else -1 for a in idx]))
    _obj = (np.array(vs, np.float64), np.array(vts), faces)
    return _obj

def target(name):
    d = []
    for ln in open(f'{MH}/t/{name}.target'):
        if ln.startswith('#') or not ln.strip(): continue
        a = ln.split(); d.append((int(a[0]), float(a[1]), float(a[2]), float(a[3])))
    return d

def apply_targets(V, mix):
    V = V.copy()
    for name, w in mix.items():
        for i, x, y, z in target(name): V[i] += np.array([x, y, z]) * w
    return V

def to_bl(V):  # MH: Y up, +Z front, decimetres -> Blender Z up, -Y front, metres
    return np.stack([V[:, 0], -V[:, 2], V[:, 1]], 1) * .1

def build(name, col, mix, groups=('body',), ground=True):
    V0, VT, F = load_obj()
    V = to_bl(apply_targets(V0, mix))
    if ground:
        V[:, 2] -= ground_offset(V)
    sel = [f for f in F if f[0] in groups]
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in V], [], [f[1] for f in sel])
    uv = me.uv_layers.new(name='UV')
    k = 0
    for f in sel:
        for t in f[2]:
            if t >= 0: uv.data[k].uv = VT[t]
            k += 1
    o = bpy.data.objects.new(name, me); col.objects.link(o)
    return o, V

def drop_loose(o):
    bm = bmesh.new(); bm.from_mesh(o.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.to_mesh(o.data); bm.free()

def ground_offset(V):
    V0, VT, F = load_obj()
    idx = set()
    for f in F:
        if f[0] == 'body': idx.update(f[1])
    return V[list(idx), 2].min()

# ------------------------------------------------------------------ rig
def rig(name, col, V, meshes):
    sk = json.load(open(f'{MH}/default.mhskel'))
    J = {k: Vector(V[v].mean(0)) for k, v in sk['joints'].items()}
    arm = bpy.data.armatures.new(name + ' rig'); ao = bpy.data.objects.new(name + ' rig', arm); col.objects.link(ao)
    bpy.context.view_layer.objects.active = ao
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    ao.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = {}
    # pass 1: create, pass 2: parent
    for bn, b in sk['bones'].items():
        e = arm.edit_bones.new(bn); e.head = J[b['head']]; e.tail = J[b['tail']]
        if (e.tail - e.head).length < 1e-4: e.tail = e.head + Vector((0, 0, .01))
        d = (e.tail - e.head).normalized()
        e.align_roll(Vector((0, 0, 1)) if abs(d.y) > .7 else Vector((0, -1, 0)))
        eb[bn] = e
    for bn, b in sk['bones'].items():
        if b['parent']: eb[bn].parent = eb[b['parent']]
        e = eb[bn]
        if b['parent'] and (eb[b['parent']].tail - e.head).length < 1e-4: e.use_connect = True
    bpy.ops.object.mode_set(mode='OBJECT')
    W = json.load(open(f'{MH}/default_weights.mhw'))['weights']
    for o in meshes:
        for bn, lst in W.items():
            g = o.vertex_groups.get(bn) or o.vertex_groups.new(name=bn)
            for vi, w in lst:
                if vi < len(o.data.vertices): g.add([vi], w, 'ADD')
        m = o.modifiers.new('rig', 'ARMATURE'); m.object = ao
        o.parent = ao
    return ao

def pose(ao, rots):
    """rots: {bone: (x, y, z) degrees in bone-local XYZ euler}"""
    for bn, r in rots.items():
        pb = ao.pose.bones.get(bn)
        if not pb: print('no bone', bn); continue
        pb.rotation_mode = 'XYZ'; pb.rotation_euler = Euler([math.radians(a) for a in r], 'XYZ')
    bpy.context.view_layer.update()

def bake_pose(objs):
    """apply the armature deformation into the meshes (static posed copies)."""
    for o in objs:
        bpy.context.view_layer.objects.active = o
        for o2 in bpy.context.view_layer.objects: o2.select_set(False)
        o.select_set(True)
        for m in list(o.modifiers):
            if m.type == 'ARMATURE': bpy.ops.object.modifier_apply(modifier=m.name)
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw

def joints(V):
    sk = json.load(open(f'{MH}/default.mhskel'))
    return {k: Vector(V[v].mean(0)) for k, v in sk['joints'].items()}
