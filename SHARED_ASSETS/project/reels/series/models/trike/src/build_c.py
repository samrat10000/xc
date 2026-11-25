"""Stage C: marker-ink crease tubes + inverted-hull silhouettes. usage: build_c.py -- b.blend out.blend"""
import bpy, bmesh, sys, os, math, random
from mathutils import Vector as V
A = sys.argv[sys.argv.index('--') + 1:]
bpy.ops.wm.open_mainfile(filepath=A[0]); sc = bpy.context.scene; OB = bpy.data.objects
ROOT = OB['IVORY • three-wheel concept racer']; rnd = random.Random(5)
ink = bpy.data.materials.new('Ink_Marker_Black'); ink.use_nodes = True
b = ink.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (.008, .008, .009, 1); b.inputs['Roughness'].default_value = .9
hull = bpy.data.materials.new('Ink_Outline_Hull'); hull.use_nodes = True; hull.use_backface_culling = True
b = hull.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (.005, .005, .006, 1); b.inputs['Roughness'].default_value = 1
CREASE_M = ('Paint_Ivory_Weathered', 'Paint_Vermilion_Weathered', 'Composite_Gunmetal_Worn', 'Deep anodized wheel alloy', 'Plastic_Black', 'Paint_JerryCan_Olive', 'Steel_Bracket', 'Gun_Steel_Parkerized_Worn', 'Paint_AmmoCan_OD_Worn')
HULL_M = CREASE_M + ('Rubber_MudTerrain', 'Charcoal seat foam textile', 'Racing red powder-coated spring steel')
def diag(o): return (V(o.bound_box[6]) - V(o.bound_box[0])).length * max(o.matrix_world.to_scale())
INK = {}; nh = 0; nl = 0
for o in [o for o in OB if o.type == 'MESH' and o.material_slots and o.material_slots[0].material]:
    mn = o.material_slots[0].material.name; d = diag(o)
    if d < .12 or len(o.data.polygons) < 12: continue
    bm = bmesh.new(); bm.from_mesh(o.data); bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bm.transform(o.matrix_world)
    if mn in CREASE_M and len(bm.faces) < 40000:
        grp = o.parent.name if o.parent else 'misc'
        tb = INK.setdefault(grp, bmesh.new())
        for e in bm.edges:
            if len(e.link_faces) != 2 or e.calc_length() < .006: continue
            if e.calc_face_angle(0) < math.radians(38): continue
            p0, p1 = e.verts[0].co.copy(), e.verts[1].co.copy(); dv = p1 - p0
            ov = rnd.uniform(0, .25) * min(dv.length, .04)
            p0 -= dv.normalized() * ov * rnd.random(); p1 += dv.normalized() * ov * rnd.random()
            nrm = (e.link_faces[0].normal + e.link_faces[1].normal).normalized()
            p0 += nrm * .002; p1 += nrm * .002
            r = rnd.uniform(.0045, .0065)
            a = dv.normalized().cross(V((0, 0, 1)) if abs(dv.normalized().z) < .9 else V((1, 0, 0))).normalized(); c = dv.normalized().cross(a)
            ring0 = [tb.verts.new(p0 + (a * math.cos(t) + c * math.sin(t)) * r) for t in [k * 2 * math.pi / 5 for k in range(5)]]
            ring1 = [tb.verts.new(p1 + (a * math.cos(t) + c * math.sin(t)) * r) for t in [k * 2 * math.pi / 5 for k in range(5)]]
            for k in range(5): tb.faces.new((ring0[k], ring0[(k + 1) % 5], ring1[(k + 1) % 5], ring1[k]))
            nl += 1
    if mn in HULL_M:
        bm.normal_update(); t = min(.022, max(.006, d * .014))
        for v in bm.verts: v.co += v.normal * t
        bmesh.ops.reverse_faces(bm, faces=bm.faces)
        me = bpy.data.meshes.new(o.name + ' hull'); bm.to_mesh(me); me.materials.append(hull)
        ho = bpy.data.objects.new(o.name + ' hull', me); sc.collection.objects.link(ho)
        ho.parent = o; ho.matrix_parent_inverse = o.matrix_world.inverted(); nh += 1
    bm.free()
for g, tb in INK.items():
    me = bpy.data.meshes.new(g + ' ink'); tb.to_mesh(me); tb.free(); me.materials.append(ink)
    io = bpy.data.objects.new(g.split('•')[-1].strip() + ' ink lines', me); sc.collection.objects.link(io)
    io.parent = OB[g] if g in OB else ROOT; io.matrix_parent_inverse = io.parent.matrix_world.inverted()
print('hulls', nh, 'lines', nl, flush=True)
bpy.ops.wm.save_as_mainfile(filepath=A[1]); print('SAVED', flush=True)
