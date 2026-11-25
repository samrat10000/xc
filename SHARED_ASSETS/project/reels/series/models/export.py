"""Open a character .blend, bake procedural materials to textures, swap hull ink to a
backface-culled black material and export a GLB. usage: python3 export.py in.blend out.glb"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import castlib as L, mats as M
src, dst = sys.argv[1], sys.argv[2]
bpy.ops.wm.open_mainfile(filepath=src)
sc = bpy.context.scene; sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
texdir = os.path.splitext(dst)[0] + '_tex'; os.makedirs(texdir, exist_ok=True)
ink = bpy.data.materials.new('Ink_Outline'); ink.use_nodes = True; ink.use_backface_culling = True
bs = ink.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value = (0.01, 0.008, 0.012, 1); bs.inputs['Roughness'].default_value = 1
BIG = ('body', 'shirt', 'pants', 'jacket', 'hoodie', 'vest', 'gown', 'skirt', 'coat')
done = {}
for o in list(bpy.data.objects):
    if o.type != 'MESH' or o.name == 'floor': continue
    if o.get('hull'):
        o.data.materials.clear(); o.data.materials.append(ink); continue
    m = o.active_material
    if not m or not m.use_nodes: continue
    kinds = {n.type for n in m.node_tree.nodes}
    if not kinds & {'TEX_NOISE', 'TEX_VORONOI', 'TEX_WAVE', 'VERTEX_COLOR', 'AMBIENT_OCCLUSION'}: continue
    size = 1024 if any(k in o.name.lower() for k in BIG) else 256
    print('bake', o.name, size, flush=True)
    M.bake(o, size=size, outdir=texdir)
for o in bpy.data.objects:
    if o.name == 'floor' or o.type in ('LIGHT', 'CAMERA'): o.select_set(False)
# lighten for phone viewers: decimate heavy meshes (hulls harder)
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name != 'floor' and len(o.data.polygons) > 8000:
        d = o.modifiers.new('dec', 'DECIMATE'); d.ratio = .35 if o.get('hull') else .55
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name != 'floor': o.select_set(True)
bpy.ops.export_scene.gltf(filepath=dst, use_selection=True, export_apply=True, export_format='GLB',
                          export_image_format='JPEG', export_jpeg_quality=85)
print('exported', dst, os.path.getsize(dst) // 1024, 'KB')
