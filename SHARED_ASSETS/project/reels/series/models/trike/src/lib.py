import bpy, bmesh, math, random
import numpy as np
from mathutils import Vector, Matrix
V = Vector
def lin(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c)
_M = {}
def pbr(name, hexc, rough=.5, metal=0., emit=0.):
    if name in _M: return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*lin(hexc), 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if emit: b.inputs['Emission Color'].default_value = (*lin(hexc), 1); b.inputs['Emission Strength'].default_value = emit
    _M[name] = m; return m
def vcmat(name, rough=.6, metal=0.):
    if name in _M: return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    a = nt.nodes.new('ShaderNodeVertexColor'); a.layer_name = 'Col'; nt.links.new(a.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    _M[name] = m; return m
def imgmat(name, img, rough=.6, metal=0., alpha=False, clip=False, nrm=None, rm=None, uvscale=None):
    if name in _M: return _M[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    def tex(path, colorspace='sRGB'):
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path); t.image.colorspace_settings.name = colorspace
        if uvscale:
            mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (uvscale, uvscale, 1)
            uv = nt.nodes.new('ShaderNodeUVMap'); nt.links.new(uv.outputs[0], mp.inputs[0]); nt.links.new(mp.outputs[0], t.inputs[0])
        return t
    t = tex(img); nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    if alpha:
        if clip:
            r = nt.nodes.new('ShaderNodeMath'); r.operation = 'ROUND'
            nt.links.new(t.outputs['Alpha'], r.inputs[0]); nt.links.new(r.outputs[0], b.inputs['Alpha'])
        else:
            nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if nrm:
        tn = tex(nrm, 'Non-Color'); nm = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs[0], b.inputs['Normal'])
    if rm:
        tr = tex(rm, 'Non-Color'); sp = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(tr.outputs['Color'], sp.inputs[0])
        nt.links.new(sp.outputs['Green'], b.inputs['Roughness']); nt.links.new(sp.outputs['Blue'], b.inputs['Metallic'])
    _M[name] = m; return m

PARENT = {}
def obj(name, bm, mat, parent=None, smooth=True, sharp=35, xform=None):
    if xform is not None: bmesh.ops.transform(bm, matrix=xform, verts=bm.verts)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    if mat: me.materials.append(mat)
    if smooth:
        me.shade_smooth()
        if sharp: me.set_sharp_from_angle(angle=math.radians(sharp))
    if parent is not None:
        o.parent = parent; o.matrix_parent_inverse = parent.matrix_world.inverted()
    return o

def revolve(bm, prof, segs=48, axis='Y', closed=False, c=V((0, 0, 0)), phase=0.):
    """prof: list of (r, a) in order. axis: revolve axis. returns rings"""
    rings = []
    for k in range(segs):
        t = phase + 2 * math.pi * k / segs; ct, st = math.cos(t), math.sin(t)
        ring = []
        for r, a in prof:
            if axis == 'Y': p = V((r * st, a, r * ct))
            elif axis == 'X': p = V((a, r * st, r * ct))
            else: p = V((r * ct, r * st, a))
            ring.append(bm.verts.new(c + p))
        rings.append(ring)
    n = len(prof)
    for k in range(segs):
        A, B = rings[k], rings[(k + 1) % segs]
        for i in range(n - 1 + (1 if closed else 0)):
            j = (i + 1) % n
            q = [A[i], B[i], B[j], A[j]]
            if len(set(q)) == 4:
                try: bm.faces.new(q)
                except ValueError: pass
    return rings

def frame_from(d):
    d = d.normalized(); up = V((0, 0, 1)) if abs(d.z) < .9 else V((1, 0, 0))
    a = d.cross(up).normalized(); b = d.cross(a).normalized(); return a, b
def tube(bm, pts, radii, sides=8, cap=True, ends_r=None):
    pts = [V(p) for p in pts]; rings = []
    for i, p in enumerate(pts):
        d = pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]
        a, b = frame_from(d)
        r = radii[i] if hasattr(radii, '__len__') else radii
        rings.append([bm.verts.new(p + (a * math.cos(t) + b * math.sin(t)) * r) for t in [k / sides * 2 * math.pi for k in range(sides)]])
    for i in range(len(rings) - 1):
        for k in range(sides):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % sides], rings[i + 1][(k + 1) % sides], rings[i + 1][k]))
    if cap:
        bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    return rings
def cyl(bm, c, d, r, h, segs=16, r2=None):
    """cylinder centred at c along direction d"""
    d = V(d).normalized(); a, b = frame_from(d); r2 = r if r2 is None else r2
    bot = [bm.verts.new(V(c) - d * h / 2 + (a * math.cos(t) + b * math.sin(t)) * r) for t in [k / segs * 2 * math.pi for k in range(segs)]]
    top = [bm.verts.new(V(c) + d * h / 2 + (a * math.cos(t) + b * math.sin(t)) * r2) for t in [k / segs * 2 * math.pi for k in range(segs)]]
    for k in range(segs):
        bm.faces.new((bot[k], bot[(k + 1) % segs], top[(k + 1) % segs], top[k]))
    bm.faces.new(list(reversed(bot))); bm.faces.new(top)
def box(bm, c, s, rot=None, bev=0.):
    tmp = bmesh.new(); bmesh.ops.create_cube(tmp, size=1)
    for v in tmp.verts: v.co = V((v.co.x * s[0], v.co.y * s[1], v.co.z * s[2]))
    if bev > 0:
        bmesh.ops.bevel(tmp, geom=list(tmp.edges), offset=bev, segments=2, affect='EDGES', profile=.5)
    M = (rot.to_4x4() if rot is not None else Matrix.Identity(4)); M = Matrix.Translation(V(c)) @ M
    bmesh.ops.transform(tmp, matrix=M, verts=tmp.verts)
    me = bpy.data.meshes.new('_t'); tmp.to_mesh(me); tmp.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
def hexbolt(bm, c, n, r=.011, h=.008):
    n = V(n).normalized()
    cyl(bm, V(c) + n * .0015, n, r * 1.35, .003, 12)          # washer
    cyl(bm, V(c) + n * (.003 + h / 2), n, r, h, 6)            # hex head
def merge(bm, dist=1e-5): bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=dist)

def vcol(o, fn, name='Col'):
    me = o.data; ca = me.color_attributes.new(name, 'FLOAT_COLOR', 'POINT')
    co = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
    nr = np.empty(len(me.vertices) * 3, np.float32); me.vertices.foreach_get('normal', nr); nr = nr.reshape(-1, 3)
    c = fn(co, nr); rgba = np.concatenate([c, np.ones((len(c), 1), np.float32)], 1).astype(np.float32)
    ca.data.foreach_set('color', rgba.ravel())

TAB = np.random.default_rng(3).random(1 << 18).astype(np.float32)
def vnoise(p, s, off=0.):
    q = p * s + off; i = np.floor(q).astype(np.int64); f = q - i; f = f * f * (3 - 2 * f)
    def h(dx, dy, dz): return TAB[(((i[:, 0] + dx) * 73856093) ^ ((i[:, 1] + dy) * 19349663) ^ ((i[:, 2] + dz) * 83492791)) & ((1 << 18) - 1)]
    x0 = h(0,0,0)*(1-f[:,0]) + h(1,0,0)*f[:,0]; x1 = h(0,1,0)*(1-f[:,0]) + h(1,1,0)*f[:,0]
    x2 = h(0,0,1)*(1-f[:,0]) + h(1,0,1)*f[:,0]; x3 = h(0,1,1)*(1-f[:,0]) + h(1,1,1)*f[:,0]
    y0 = x0*(1-f[:,1]) + x1*f[:,1]; y1 = x2*(1-f[:,1]) + x3*f[:,1]
    return y0*(1-f[:,2]) + y1*f[:,2]
def fbm(p, s, oct=3, off=0.):
    t = 0; a = 1; n = 0
    for k in range(oct): t += a * vnoise(p, s * 2 ** k, off + 7.1 * k); n += a; a *= .5
    return t / n
def L(h): return np.array(lin(h), np.float32)
