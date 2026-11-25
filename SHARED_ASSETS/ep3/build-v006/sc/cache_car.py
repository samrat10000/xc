"""Import Sam's untouched original once; preserve hierarchy in a reusable copy."""
import bpy,json,math,logging
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SHARED=ROOT.parent/'SHARED_ASSETS'
DEST=SHARED/'ep3/v001/assets/night-terror-import-v001.blend'
if DEST.exists(): raise RuntimeError('Version already exists; refusing overwrite')
bpy.ops.wm.read_factory_settings(use_empty=True)
logging.getLogger('io_scene_gltf2').setLevel(logging.WARNING)
bpy.ops.import_scene.gltf(filepath=str(SHARED/'originals_from_sam/Night_Terror_Fastback_v2.glb'))
bpy.context.view_layer.update()
col=bpy.data.collections.new('NT_ORIGINAL'); bpy.context.scene.collection.children.link(col)
objects=list(bpy.context.scene.objects)
root=bpy.data.objects.new('NT_EP3_ROOT',None); col.objects.link(root)
for o in objects:
 for old in list(o.users_collection): old.objects.unlink(o)
 col.objects.link(o)
 if o.parent is None: o.parent=root
 if 'hull' in o.name.lower(): o.hide_render=True; o.hide_viewport=True
 if o.type=='MESH' and any(w in o.name.lower() for w in ['tire','tyre','traction lug']):
  for m in o.data.materials:
   if m and m.use_nodes:
    bs=m.node_tree.nodes.get('Principled BSDF')
    if bs: bs.inputs['Metallic'].default_value=0; bs.inputs['Roughness'].default_value=.88
details=[]
for o in objects:
 if o.type!='MESH': continue
 if any(w in o.name.lower() for w in ['hood top','tire carcass','headlamp','headlight','windshield','windscreen','steering wheel','seat cushion']):
  p=[o.matrix_world@Vector(v) for v in o.bound_box]
  details.append({'name':o.name,'center':[sum(v[j] for v in p)/8 for j in range(3)],'parent':o.parent.name if o.parent else None})
root['source']='SHARED_ASSETS/originals_from_sam/Night_Terror_Fastback_v2.glb'
root['status']='Imported original; axes and headlight identities must be visually verified'
DEST.parent.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True)
(ROOT/'audit/car-parts.json').write_text(json.dumps(details,indent=2),encoding='utf8')
print('CAR_CACHE',DEST,flush=True)
