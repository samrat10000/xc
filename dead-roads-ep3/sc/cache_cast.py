import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SHARED=ROOT.parent/'SHARED_ASSETS';report={}
for name in ('husk','runner','screamer'):
 source=ROOT.parent/f'cast/out/rig/{name}/{name}.blend';dest=SHARED/f'ep3/v001/assets/{name}-rig-v002.blend'
 if dest.exists():continue
 bpy.ops.wm.open_mainfile(filepath=str(source));rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
 if not rigs:raise RuntimeError('No rig: '+name)
 rig=rigs[0];col=bpy.data.collections.new('EP3_'+name.upper());bpy.context.scene.collection.children.link(col)
 keep={rig,*rig.children_recursive}
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and (any(m.type=='ARMATURE' and m.object in rigs for m in o.modifiers) or o.name.lower().startswith(name)):
   keep.add(o)
 mesh_count=sum(o.type=='MESH' for o in keep)
 if not mesh_count:raise RuntimeError('No character geometry associated with rig: '+name)
 for o in list(bpy.context.scene.objects):
  if o not in keep:bpy.data.objects.remove(o,do_unlink=True);continue
  for old in list(o.users_collection):old.objects.unlink(o)
  col.objects.link(o)
  if o.animation_data:o.animation_data_clear()
  if 'hull' in o.name.lower():o.hide_render=True
 report[name]={'source':str(source),'output':str(dest),'bones':[b.name for b in rig.data.bones],'objects':len(keep),'meshes':mesh_count}
 bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
 print('CAST',name,len(keep),len(rig.data.bones),flush=True)
(ROOT/'audit/cast-rigs-v002.json').write_text(json.dumps(report,indent=2),encoding='utf8')
