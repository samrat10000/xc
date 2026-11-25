"""CPU-only asset inspection. No render, GPU setup, or shared-asset mutation."""
import bpy, json, os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
SHARED=ROOT.parent/'SHARED_ASSETS'
files={
 'night_terror':SHARED/'originals_from_sam/Night_Terror_Fastback_v2.glb',
 'sam':SHARED/'blends/wakeup/sam.blend',
 'rider':SHARED/'blends/rider.blend',
 'stalker':SHARED/'blends/stalker_rig.blend',
 'trike':SHARED/'blends/trike.blend',
 'walker':SHARED/'blends/walker.blend',
}
report={'blender':bpy.app.version_string,'rendered':False,'assets':{}}
for name,p in files.items():
 info={'path':str(p),'exists':p.exists()}
 report['assets'][name]=info
 if not p.exists(): continue
 bpy.ops.wm.read_factory_settings(use_empty=True)
 try:
  if p.suffix=='.glb': bpy.ops.import_scene.gltf(filepath=str(p))
  else:
   with bpy.data.libraries.load(str(p),link=False) as (src,dst): dst.collections=list(src.collections)
   for col in dst.collections:
    if col and col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
  bpy.context.view_layer.update()
  objects=list(bpy.context.scene.objects)
  meshes=[o for o in objects if o.type=='MESH']
  points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box]
  info.update(objects=len(objects),meshes=len(meshes),vertices=sum(len(o.data.vertices) for o in meshes),collections=[c.name for c in bpy.data.collections],mesh_names=[o.name for o in meshes],rigs=[{'name':o.name,'bones':[b.name for b in o.data.bones]} for o in objects if o.type=='ARMATURE'],actions=[a.name for a in bpy.data.actions],missing_external_images=[i.filepath for i in bpy.data.images if i.source=='FILE' and not i.packed_file and i.filepath and not Path(bpy.path.abspath(i.filepath,library=i.library)).exists()])
  if points: info['bounds']={a:[min(v[j] for v in points),max(v[j] for v in points)] for j,a in enumerate('xyz')}
 except Exception as exc:
  info['error']=repr(exc)
 (ROOT/'audit').mkdir(exist_ok=True)
 (ROOT/'audit/asset-audit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
 print('AUDIT',name,json.dumps({k:v for k,v in info.items() if k not in ('mesh_names','rigs','actions','collections')}),flush=True)
