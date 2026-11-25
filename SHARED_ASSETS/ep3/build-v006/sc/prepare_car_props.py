"""Prepare licensed, full-scale linked car props; preserve downloaded source assets."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector,Matrix
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parent/'SHARED_ASSETS/ep3/v001/assets/khronos';report={}
DEST=ROOT.parent/'SHARED_ASSETS/ep3/v001/assets/car-props-v002.blend'
if DEST.exists():raise RuntimeError('Refusing overwrite')
bpy.ops.wm.read_factory_settings(use_empty=True)
for name,length in [('ToyCar',4.4),('CarConcept',4.8)]:
 before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(BASE/name/f'glTF-Binary/{name}.glb'))
 new=[o for o in bpy.data.objects if o not in before]
 for o in list(new):
  if o.type in ('CAMERA','LIGHT') or o.name.lower().startswith('fabric') or any(k in o.name.lower() for k in ('logo','emblem','license plate')):
   bpy.data.objects.remove(o,do_unlink=True);new.remove(o)
 meshes=[o for o in new if o.type=='MESH'];bpy.context.view_layer.update()
 points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
 low=Vector([min(v[i] for v in points) for i in range(3)]);high=Vector([max(v[i] for v in points) for i in range(3)]);dimensions=high-low;factor=length/max(dimensions.x,dimensions.y)
 col=bpy.data.collections.new('PROP_'+name);bpy.context.scene.collection.children.link(col)
 root=bpy.data.objects.new(name+'_root',None);col.objects.link(root)
 transform=Matrix.Rotation(math.pi/2 if dimensions.x>dimensions.y else 0,4,'Z')@Matrix.Scale(factor,4)@Matrix.Translation((-((high.x+low.x)/2),-((high.y+low.y)/2),-low.z))
 matrices={o:o.matrix_world.copy() for o in new}
 for o in new:o.parent=None
 for o in new:o.matrix_world=transform@matrices[o]
 for o in new:
  world=o.matrix_world.copy()
  for c in list(o.users_collection):c.objects.unlink(o)
  col.objects.link(o);o.parent=root;o.matrix_world=world
  if o.animation_data:o.animation_data_clear()
  if o.type=='MESH':
   for mat in o.data.materials:
    if not mat or not mat.use_nodes:continue
    for bs in mat.node_tree.nodes:
     if bs.type=='BSDF_PRINCIPLED':
      bs.inputs['Emission Strength'].default_value=0
      if any(k in mat.name.lower() for k in ('rubber','tire','tyre')):bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.9
 report[name]={'raw_bounds':[list(low),list(high)],'scale':factor,'meshes':len(meshes),'parts':[{'name':o.name,'center':list(o.matrix_world.translation)} for o in meshes if any(k in o.name.lower() for k in ('seat','windshield','glass','window'))]}
bpy.context.view_layer.update();bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True)
(ROOT/'audit/car-props.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('PROP_CACHE',DEST,flush=True)
