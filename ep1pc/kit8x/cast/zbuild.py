"""Shared character construction on the MakeHuman base: body + helpers, rig, subdivision that keeps
weights, garments cut from the body by bone weights, rigid parts bound to one bone."""
import math, random, os
import bpy, bmesh
from mathutils import Vector, noise
import castlib as L, mh

HELPERS = {'eyeL': 'helper-l-eye', 'eyeR': 'helper-r-eye', 'teethU': 'helper-upper-teeth',
           'teethL': 'helper-lower-teeth', 'tongue': 'helper-tongue'}

def V(*a): return Vector(a[0]) if len(a) == 1 else Vector(a)

class Char:
    def __init__(s, name, mix, col):
        s.name = name; s.C = col
        s.body, s.V = mh.build(f'{name} body', col, mix, groups=('body',))
        s.parts = {}
        for k, g in HELPERS.items():
            o, _ = mh.build(f'{name} {k}', col, mix, groups=(g,)); s.parts[k] = o
        s.rig = mh.rig(name, col, s.V, [s.body] + list(s.parts.values()))
        for o in [s.body] + list(s.parts.values()): mh.drop_loose(o); L.smooth(o)
        s.J = mh.joints(s.V)
        s.garments = []; s.rigid = []
    def j(s, k): return s.J[k].copy()

    # ---------------------------------------------------------------- modifiers applied at the bottom of the stack
    def apply_first(s, o, mod):
        bpy.context.view_layer.objects.active = o
        for o2 in bpy.context.view_layer.objects: o2.select_set(False)
        o.select_set(True)
        bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    def subdiv(s, o, n=1):
        m = o.modifiers.new('sub', 'SUBSURF'); m.levels = n; m.render_levels = n; m.uv_smooth = 'PRESERVE_CORNERS'
        s.apply_first(o, m)
    def disp(s, o, **kw):
        m = L.displace(o, **kw); s.apply_first(o, m)

    # ---------------------------------------------------------------- weights helpers
    def wsum(s, o, bones):
        idx = [o.vertex_groups[b].index for b in bones if b in o.vertex_groups]
        out = []
        for v in o.data.vertices:
            out.append(sum(g.weight for g in v.groups if g.group in idx))
        return out

    def garment(s, name, bones, keep=None, push=.012, thick=.004, fold=None, tear=None, ragged=None):
        g = s.body.copy(); g.data = s.body.data.copy(); g.name = f'{s.name} {name}'; s.C.objects.link(g)
        w = s.wsum(g, bones)
        bm = bmesh.new(); bm.from_mesh(g.data); bm.verts.ensure_lookup_table()
        kill = []
        for v in bm.verts:
            p = v.co
            ok = w[v.index] > .5 + (.25 * noise.noise(p * 40) if ragged else 0)
            if keep: ok = ok and keep(p)
            if not ok: kill.append(v)
        bmesh.ops.delete(bm, geom=kill, context='VERTS')
        if tear:
            bm.faces.ensure_lookup_table()
            dk = [f for f in bm.faces if tear(f.calc_center_median())]
            bmesh.ops.delete(bm, geom=dk, context='FACES')
            bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
        bm.normal_update()
        for v in bm.verts:
            d = push + (fold(v.co) if fold else 0)
            v.co += v.normal * d
        bm.to_mesh(g.data); bm.free()
        so = g.modifiers.new('sol', 'SOLIDIFY'); so.thickness = thick; so.offset = -1
        s.apply_first(g, so)
        L.smooth(g); s.garments.append(g)
        return g

    def bind(s, o, bone):
        """rigid part follows one bone"""
        for vg in list(o.vertex_groups): o.vertex_groups.remove(vg)
        g = o.vertex_groups.new(name=bone); g.add([v.index for v in o.data.vertices], 1., 'REPLACE')
        m = o.modifiers.new('rig', 'ARMATURE'); m.object = s.rig; o.parent = s.rig
        s.rigid.append(o); return o

    def cut(s, o, fn):
        L.delete_faces(o, lambda p, n: fn(p))

    def hit(s, o, origin, direction):
        ok, loc, nor, _ = o.ray_cast(V(origin), V(direction))
        return (loc, nor) if ok else (None, None)

    def all_meshes(s):
        return [o for o in s.C.all_objects if o.type == 'MESH']

    def pose_and_bake(s, P):
        mh.pose(s.rig, P)
        meshes = s.all_meshes()
        for o in meshes:
            for m in o.modifiers:
                if m.type == 'ARMATURE': m.object = s.rig
        mh.bake_pose([o for o in meshes if any(m.type == 'ARMATURE' for m in o.modifiers)])
        if not os.environ.get('KEEP_RIG'):
            bpy.data.objects.remove(s.rig); return
        # keep the skeleton: the baked pose becomes its rest pose, meshes get re-bound when the file is saved
        rig = s.rig
        for o2 in bpy.context.view_layer.objects: o2.select_set(False)
        bpy.context.view_layer.objects.active = rig; rig.select_set(True)
        bpy.ops.object.mode_set(mode='POSE'); bpy.ops.pose.armature_apply(selected=False); bpy.ops.object.mode_set(mode='OBJECT')
        rig.name = f'{s.name} RIG'
        for o in meshes:
            if o.parent is rig:
                mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
        # a 4-point reference mesh rides along with every later all_meshes() transform
        bm = bmesh.new()
        for p in ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)): bm.verts.new(p)
        ref = L.mesh_obj('_rigref', bm, s.C); ref.hide_render = True
        src = s.body.copy(); src.data = s.body.data.copy(); src.name = '_rigbody'; s.C.objects.link(src); src.hide_render = True
        s._keep = (rig, ref, src)
        zz = s
        def _finish(*a):
            if getattr(zz, '_done', False): return
            zz._done = True; finish_rig(zz)
        bpy.app.handlers.save_pre.append(_finish)

def _active(o):
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    bpy.context.view_layer.objects.active = o; o.select_set(True)

def finish_rig(s):
    import numpy as np
    from mathutils import Matrix
    rig, ref, src = s._keep
    P = np.array([list(v.co) for v in ref.data.vertices])           # transformed reference frame
    o_, ex, ey, ez = P[0], P[1] - P[0], P[2] - P[0], P[3] - P[0]
    M = Matrix(((ex[0], ey[0], ez[0], o_[0]), (ex[1], ey[1], ez[1], o_[1]), (ex[2], ey[2], ez[2], o_[2]), (0, 0, 0, 1)))
    rig.matrix_world = M @ rig.matrix_world
    bones = set(b.name for b in rig.data.bones)
    for o in [o for o in s.C.all_objects if o.type == 'MESH' and o not in (ref, src)]:
        if len(o.data.vertices) == 0: continue
        has = any(vg.name in bones for vg in o.vertex_groups)
        if not has:
            # weights from the nearest point of the baked body
            for vg in list(o.vertex_groups): o.vertex_groups.remove(vg)
            m = o.modifiers.new('dt', 'DATA_TRANSFER'); m.object = src; m.use_object_transform = True
            m.use_vert_data = True; m.data_types_verts = {'VGROUP_WEIGHTS'}; m.vert_mapping = 'NEAREST'
            m.layers_vgroup_select_src = 'ALL'; m.layers_vgroup_select_dst = 'NAME'
            _active(o)
            try:
                bpy.ops.object.datalayout_transfer(modifier=m.name)
                bpy.ops.object.modifier_move_to_index(modifier=m.name, index=0)
                bpy.ops.object.modifier_apply(modifier=m.name)
            except Exception as e:
                print('weight transfer failed', o.name, e); o.modifiers.remove(m); continue
        am = o.modifiers.new('rig', 'ARMATURE'); am.object = rig
        bpy.ops.object.modifier_move_to_index(modifier=am.name, index=0) if False else None
    for x in (ref, src): bpy.data.objects.remove(x, do_unlink=True)
    if rig.name not in s.C.objects:
        for c in rig.users_collection: c.objects.unlink(rig)
        s.C.objects.link(rig)
    print('RIG KEPT', rig.name)

def shoe(name, col, ankle, toe, flap=0., scale=1.):
    """sneaker built around ankle->toe; returns (upper, sole, laces) in world space"""
    import anatomy as A
    a, t = V(ankle), V(toe)
    sk2 = A.Skel()
    sk2.add('heel', (0, .035, -.045), (.040, .034))
    sk2.add('ank', (0, .005, .01), (.046, .048), 'heel')
    sk2.add('inst', (0, -.07, -.03), (.047, .037), 'heel')
    sk2.add('ball', (0, -.14, -.046), (.050, .029), 'inst')
    sk2.add('toe', (0, -.19, -.052), (.042, .023), 'ball')
    up = L.skin_body(f'{name} shoe', sk2.j, sk2.e, col, branch=.6, subdiv=2)
    L.warp(up, lambda c: V(c.x, c.y, max(c.z, -.07)))
    L.delete_faces(up, lambda p, n: p.z > .022 and n.z > .5)
    sk3 = A.Skel()
    sk3.add('h', (0, .04, -.082), (.048, .03)); sk3.add('m', (0, -.07, -.082), (.051, .03), 'h')
    sk3.add('b', (0, -.15, -.082), (.056, .03), 'm'); sk3.add('t', (0, -.205, -.082), (.047, .03), 'b')
    sole = L.skin_body(f'{name} sole', sk3.j, sk3.e, col, branch=.6, subdiv=2)
    L.warp(sole, lambda c: V(c.x, c.y, min(max(c.z, -.097), -.069)))
    if flap:
        def fl(c):
            if c.y > -.06: return c
            dy, dz = c.y + .06, c.z + .097
            return V(c.x, -.06 + dy * math.cos(flap) - dz * math.sin(flap), -.097 + dy * math.sin(flap) + dz * math.cos(flap))
        L.warp(sole, fl)
    parts = []
    for i in range(6):
        y = .0 - i * .02
        ok, loc, nor, _ = up.ray_cast(V(0, y, .2), V(0, 0, -1))
        if not ok: continue
        parts.append(L.box(f'{name} lace{i}', loc + V(0, 0, .002), (.022, .0035, .0025), col, rot=(0, 0, .35 if i % 2 else -.35), bevel=.001))
        for sx in (1, -1):
            parts.append(L.box(f'{name} eyelet{i}{sx}', loc + V(.022 * sx, 0, -.002), (.0045, .0045, .002), col, bevel=.001))
    parts.append(L.box(f'{name} tongue', (0, .0, .025), (.022, .03, .006), col, rot=(-.7, 0, 0), bevel=.005))
    lc = L.join(parts, f'{name} laces')
    d = (t - a); d.z = 0; d.normalize()
    rot = d.to_track_quat('-Y', 'Z').to_euler()
    for o in (up, sole, lc):
        o.scale = (scale, scale, scale); o.location = a; o.rotation_euler = rot
        L.apply_transform(o); L.smooth(o)
    return up, sole, lc
