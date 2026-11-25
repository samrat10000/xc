import sys, math
sys.path.insert(0, '/home/user/w/models')
import bpy, numpy as np
from mathutils import Vector, Euler, Matrix
import anatomy as A
V = A.V
src = open('/home/user/w/models/stalker.py').read().split('\n')
s0 = [i for i, l in enumerate(src) if l.startswith('sk = A.Skel()')][0]; s1 = [i for i, l in enumerate(src) if l.startswith('body = L.skin_body')][0]
ns = {'A': A, 'V': V, 'math': math}; exec('\n'.join(src[s0:s1]), ns); sk = ns['sk']
J = {k: Vector(sk.j[i][0]) for k, i in sk.names.items()}; nm = {i: k for k, i in sk.names.items()}
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/home/user/w/models/stalker-v2.glb')
col = bpy.data.collections.new('Stalker'); bpy.context.scene.collection.children.link(col)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for o in list(bpy.data.objects):
    for c in o.users_collection: c.objects.unlink(o)
    if o.type == 'MESH': col.objects.link(o)
for o in meshes:
    mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
    bpy.context.view_layer.objects.active = o
for o in [o for o in bpy.data.objects if o.type != 'MESH']: bpy.data.objects.remove(o)
# apply transforms
for o in meshes:
    o.data.transform(o.matrix_world); o.matrix_world = Matrix()
arm = bpy.data.armatures.new('Stalker rig'); ao = bpy.data.objects.new('Stalker rig', arm); col.objects.link(ao)
bpy.context.view_layer.objects.active = ao; ao.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
eb = {}
root = arm.edit_bones.new('root'); root.head = J['pel'] + V(0, 0, -.25); root.tail = J['pel']; eb['pel'] = root
for a, b in sk.e:
    na, nb = nm[a], nm[b]
    e = arm.edit_bones.new(nb); e.head = J[na]; e.tail = J[nb]
    if (e.tail - e.head).length < 1e-3: e.tail = e.head + V(0, 0, .02)
    eb[nb] = e
for a, b in sk.e:
    eb[nm[b]].parent = eb[nm[a]]
# head + jaw from the skull geometry
sk_o = bpy.data.objects['Stalker skull']; jw = bpy.data.objects['Stalker jaw']
pts = np.array([v.co[:] for v in sk_o.data.vertices]); jp = np.array([v.co[:] for v in jw.data.vertices])
snout = Vector(pts[pts[:, 1].argmin()]); hinge = Vector(jp[jp[:, 1].argmax()])
h = arm.edit_bones.new('head'); h.head = J['nk2']; h.tail = snout; h.parent = eb['nk2']
j = arm.edit_bones.new('jaw'); j.head = hinge; j.tail = Vector(jp[jp[:, 1].argmin()]); j.parent = h
bpy.ops.object.mode_set(mode='OBJECT')
segs = [(b.name, Vector(b.head_local), Vector(b.tail_local)) for b in arm.bones if b.name not in ('root', 'jaw')]
Aa = np.array([s[1][:] for s in segs]); Bb = np.array([s[2][:] for s in segs]); AB = Bb - Aa; L2 = np.maximum((AB ** 2).sum(1), 1e-8)
RIG = {'Stalker skull', 'Stalker antlers', 'Stalker teeth', 'Stalker eye1', 'Stalker eye-1'}
for o in meshes:
    base = o.name.replace(' hull', '')
    for vg in list(o.vertex_groups): o.vertex_groups.remove(vg)
    if base in RIG or base == 'Stalker jaw':
        g = o.vertex_groups.new(name='jaw' if base == 'Stalker jaw' else 'head'); g.add(list(range(len(o.data.vertices))), 1., 'REPLACE')
    else:
        P = np.array([v.co[:] for v in o.data.vertices])
        groups = {s[0]: o.vertex_groups.new(name=s[0]) for s in segs}
        for c0 in range(0, len(P), 20000):
            Pc = P[c0:c0 + 20000]
            t = np.clip(((Pc[:, None, :] - Aa[None]) * AB[None]).sum(2) / L2[None], 0, 1)
            D = np.linalg.norm(Pc[:, None, :] - (Aa[None] + t[..., None] * AB[None]), axis=2)
            dmin = D.min(1, keepdims=True); Wt = np.exp(-(D - dmin) / .035); Wt[D - dmin > .12] = 0
            Wt /= Wt.sum(1, keepdims=True)
            for bi in range(len(segs)):
                idx = np.nonzero(Wt[:, bi] > .02)[0]
                g = groups[segs[bi][0]]
                for ii in idx: g.add([int(ii + c0)], float(Wt[ii, bi]), 'REPLACE')
    m = o.modifiers.new('rig', 'ARMATURE'); m.object = ao
    # put armature first
    while o.modifiers.find('rig') > 0: bpy.ops.object.modifier_move_up({'object': o}, modifier='rig') if False else o.modifiers.move(o.modifiers.find('rig'), 0)
    o.parent = ao
    if 'hull' in o.name: o.hide_render = True
for pb in ao.pose.bones: pb.rotation_mode = 'XYZ'
print('bones', [b.name for b in arm.bones])
bpy.ops.wm.save_as_mainfile(filepath='/home/user/w/out/stalker/stalker_rig.blend')
