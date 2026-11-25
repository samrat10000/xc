"""Shared helpers for the Dead Roads cast: skin-modifier bodies, vertex-colour painting,
ink hull, materials, preview renders and GLB export. Character faces -Y, Z up, metres."""
import bpy, bmesh, math, random
from mathutils import Vector, noise, Matrix

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s = bpy.context.scene
    s.render.engine = 'CYCLES'; s.cycles.device = 'CPU'
    s.view_settings.view_transform = 'Standard'
    return s

def lin(h):
    h = h.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + .055) / 1.055) ** 2.4 if x > .04045 else x / 12.92 for x in c)

def lerp(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))
def sm(e0, e1, x):
    t = max(0., min(1., (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t)

# ------------------------------------------------------------------ objects
def collection(name):
    c = bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); return c

def link(o, col):
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o)

def mesh_obj(name, bm, col):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); col.objects.link(o); return o

def apply_all(o):
    bpy.context.view_layer.objects.active = o
    for o2 in bpy.context.view_layer.objects: o2.select_set(False)
    o.select_set(True)
    for m in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)

def skin_body(name, joints, edges, col, branch=0.3, subdiv=2):
    """joints: list of (pos, (rx, ry)); edges: index pairs."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([j[0] for j in joints], edges, [])
    o = bpy.data.objects.new(name, me); col.objects.link(o)
    m = o.modifiers.new('skin', 'SKIN'); m.branch_smoothing = branch
    sv = me.skin_vertices[0].data
    for i, (_, r) in enumerate(joints): sv[i].radius = r
    sv[0].use_root = True
    s = o.modifiers.new('sub', 'SUBSURF'); s.levels = subdiv; s.render_levels = subdiv
    apply_all(o)
    return o

def displace(o, tex_type='CLOUDS', size=.05, strength=.01, mid=.5, vgroup=None, depth=2, basis='BLENDER_ORIGINAL', **kw):
    t = bpy.data.textures.new(o.name + tex_type, tex_type)
    if hasattr(t, 'noise_scale'): t.noise_scale = size
    if hasattr(t, 'noise_depth'): t.noise_depth = depth
    if hasattr(t, 'noise_basis'): t.noise_basis = basis
    for k, v in kw.items(): setattr(t, k, v)
    m = o.modifiers.new('disp', 'DISPLACE'); m.texture = t; m.strength = strength; m.mid_level = mid
    m.texture_coords = 'GLOBAL'
    if vgroup: m.vertex_group = vgroup
    return m

def smooth(o, auto=None):
    for p in o.data.polygons: p.use_smooth = True

def vgroup_by(o, name, fn):
    g = o.vertex_groups.new(name=name)
    for v in o.data.vertices:
        w = fn(o.matrix_world @ v.co)
        if w > 0: g.add([v.index], min(1, w), 'REPLACE')
    return g

def delete_faces(o, fn):
    """delete faces whose centre satisfies fn(world_pos, normal)"""
    bm = bmesh.new(); bm.from_mesh(o.data)
    kill = [f for f in bm.faces if fn(o.matrix_world @ f.calc_center_median(), f.normal)]
    bmesh.ops.delete(bm, geom=kill, context='FACES')
    loose = [v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(o.data); bm.free()

def keep_verts(o, fn):
    bm = bmesh.new(); bm.from_mesh(o.data)
    kill = [v for v in bm.verts if not fn(o.matrix_world @ v.co)]
    bmesh.ops.delete(bm, geom=kill, context='VERTS')
    bm.to_mesh(o.data); bm.free()

def push(o, fn):
    """move each vertex along its normal by fn(pos, normal)"""
    me = o.data
    for v in me.vertices:
        d = fn(v.co, v.normal)
        if d: v.co += v.normal * d
    me.update()

def warp(o, fn):
    me = o.data
    for v in me.vertices: v.co = fn(v.co.copy())
    me.update()

def dup(o, name, col):
    o2 = o.copy(); o2.data = o.data.copy(); o2.name = name; col.objects.link(o2)
    o2.modifiers.clear(); return o2

# ------------------------------------------------------------------ paint
def paint(o, fn, name='Col'):
    """fn(world_pos, normal) -> linear rgb; written per face-corner."""
    me = o.data
    if name in me.color_attributes: me.color_attributes.remove(me.color_attributes[name])
    ca = me.color_attributes.new(name, 'FLOAT_COLOR', 'POINT')
    mw = o.matrix_world; nm = mw.to_3x3()
    for v in me.vertices:
        c = fn(mw @ v.co, (nm @ v.normal).normalized())
        ca.data[v.index].color = (c[0], c[1], c[2], 1)
    me.color_attributes.active_color = ca
    return ca

def fbm(p, s=1., oct=4):
    return noise.fractal(Vector(p) * s, 1.0, 2.0, oct, noise_basis='PERLIN_NEW')

def ridge(p, s=1.):
    """thin vein-like lines where noise crosses 0"""
    n = noise.noise(Vector(p) * s, noise_basis='PERLIN_NEW')
    return max(0., 1 - abs(n) * 14)

# ------------------------------------------------------------------ materials
def mat_vc(name, rough=.6, metal=0., spec=.4, sss=0., emit=None, emit_s=0.):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    a = nt.nodes.new('ShaderNodeVertexColor'); a.layer_name = 'Col'
    nt.links.new(a.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if 'Specular IOR Level' in b.inputs: b.inputs['Specular IOR Level'].default_value = spec
    if sss: b.inputs['Subsurface Weight'].default_value = sss; b.inputs['Subsurface Radius'].default_value = (.04, .02, .015)
    if emit:
        b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = emit_s
    return m

def mat_flat(name, col, rough=.5, metal=0., emit_s=0., alpha=1.):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit_s: b.inputs['Emission Color'].default_value = (*col, 1); b.inputs['Emission Strength'].default_value = emit_s
    if alpha < 1: b.inputs['Alpha'].default_value = alpha
    return m

def setmat(o, m):
    o.data.materials.clear(); o.data.materials.append(m)

def ink_mat():
    if 'Ink' in bpy.data.materials: return bpy.data.materials['Ink']
    m = bpy.data.materials.new('Ink'); m.use_nodes = True; m.use_backface_culling = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (.004, .003, .006, 1)
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mix = nt.nodes.new('ShaderNodeMixShader')
    g = nt.nodes.new('ShaderNodeNewGeometry')
    nt.links.new(g.outputs['Backfacing'], mix.inputs[0])
    nt.links.new(e.outputs[0], mix.inputs[1]); nt.links.new(tr.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return m

def hull(o, col, t=.004):
    """inverted-hull ink outline: copy pushed out along normals, faces flipped, black backface-culled."""
    h = dup(o, o.name + ' hull', col)
    bm = bmesh.new(); bm.from_mesh(h.data)
    bm.normal_update()
    for v in bm.verts: v.co += v.normal * t
    bmesh.ops.reverse_faces(bm, faces=bm.faces)
    bm.to_mesh(h.data); bm.free()
    setmat(h, ink_mat())
    h.visible_shadow = False; h.visible_diffuse = False; h.visible_glossy = False; h.visible_transmission = False
    h['hull'] = 1
    return h

# ------------------------------------------------------------------ primitives
def tube(name, pts, radii, col, sides=6, cap=True):
    """polyline tube with per-point radius"""
    bm = bmesh.new(); rings = []
    pts = [Vector(p) for p in pts]
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        up = Vector((0, 0, 1)) if abs(d.z) < .9 else Vector((1, 0, 0))
        a = d.cross(up).normalized(); b = d.cross(a).normalized()
        r = radii[i] if hasattr(radii, '__len__') else radii
        rings.append([bm.verts.new(p + (a * math.cos(t) + b * math.sin(t)) * r) for t in [k / sides * 2 * math.pi for k in range(sides)]])
    for i in range(len(rings) - 1):
        for k in range(sides):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % sides], rings[i + 1][(k + 1) % sides], rings[i + 1][k]))
    if cap:
        bm.faces.new(list(reversed(rings[0]))); bm.faces.new(rings[-1])
    o = mesh_obj(name, bm, col); smooth(o); return o

def blob(name, loc, scale, col, seg=24, ring=16, rot=(0, 0, 0)):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=ring, radius=1)
    o = mesh_obj(name, bm, col); o.location = loc; o.scale = scale; o.rotation_euler = rot
    smooth(o); return o

def box(name, loc, size, col, rot=(0, 0, 0), bevel=0., segs=2):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1)
    for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    o = mesh_obj(name, bm, col); o.location = loc; o.rotation_euler = rot
    if bevel:
        b = o.modifiers.new('bev', 'BEVEL'); b.width = bevel; b.segments = segs
    return o

def join(objs, name):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        apply_transform(o)
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join(); objs[0].name = name
    return objs[0]

def apply_transform(o):
    bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active = o
    for m in list(o.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# ------------------------------------------------------------------ render
def studio(scene, floor=True):
    w = bpy.data.worlds.new('W'); scene.world = w; w.use_nodes = True
    nt = w.node_tree; bg = nt.nodes['Background']
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    bg2 = nt.nodes.new('ShaderNodeBackground'); bg2.inputs['Color'].default_value = (*lin('#efe8da'), 1)
    bg.inputs['Color'].default_value = (*lin('#9aa0b4'), 1); bg.inputs['Strength'].default_value = .25
    out = nt.nodes['World Output']
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0])
    nt.links.new(bg.outputs[0], mix.inputs[1]); nt.links.new(bg2.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    def light(n, loc, e, size, col=(1, 1, 1)):
        L = bpy.data.lights.new(n, 'AREA'); L.energy = e; L.size = size; L.color = col
        o = bpy.data.objects.new(n, L); scene.collection.objects.link(o); o.location = loc
        d = Vector((0, 0, 1.0)) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    light('key', (-2.2, -2.6, 3.2), 210, 1.6, (1, .96, .9))
    light('rim', (2.4, 2.2, 2.6), 200, 1.2, (.75, .85, 1))
    light('fill', (2.6, -2.4, 1.2), 45, 2.5)
    if floor:
        bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=6)
        f = mesh_obj('floor', bm, scene.collection)
        m = mat_flat('floor', lin('#e6dfcf'), rough=.9); setmat(f, m)
        f.is_shadow_catcher = True

def camera(scene, target, dist, az, el, lens=60, name='cam'):
    c = bpy.data.cameras.new(name); c.lens = lens
    o = bpy.data.objects.new(name, c); scene.collection.objects.link(o)
    t = Vector(target); a = math.radians(az); e = math.radians(el)
    o.location = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    o.rotation_euler = (t - o.location).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = o; return o

def render(scene, path, w=1080, h=1350, samples=48):
    scene.render.resolution_x = w; scene.render.resolution_y = h
    scene.cycles.samples = samples; scene.cycles.use_denoising = True
    scene.render.film_transparent = False
    scene.render.filepath = path; bpy.ops.render.render(write_still=True)

def export(col_name, path):
    bpy.ops.object.select_all(action='DESELECT')
    for o in bpy.data.collections[col_name].all_objects: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, use_selection=True, export_apply=True, export_format='GLB',
                              export_vertex_color='ACTIVE' if False else 'MATERIAL')
