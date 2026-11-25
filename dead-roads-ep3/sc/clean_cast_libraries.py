"""Round-trip newer character libraries through skinned glTF into native 5.0 files."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT.parent/'SHARED_ASSETS/ep3/v001/assets';report={}
for name in ('husk','runner','screamer'):
 blend=BASE/f'{name}-rig-v003.blend';glb=BASE/f'{name}-rig-v003.glb'
 if blend.exists():continue
 bpy.ops.wm.open_mainfile(filepath=str(BASE/f'{name}-rig-v002.blend'))
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type in ('MESH','ARMATURE') and 'hull' not in o.name.lower():o.hide_set(False);o.hide_render=False;o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_animations=False,export_skins=True,export_cameras=False,export_lights=False)
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glb))
 col=bpy.data.collections.new('EP3_'+name.upper());bpy.context.scene.collection.children.link(col)
 for o in list(bpy.context.scene.objects):
  for old in list(o.users_collection):old.objects.unlink(o)
  col.objects.link(o)
 rigs=[o for o in col.all_objects if o.type=='ARMATURE'];meshes=[o for o in col.all_objects if o.type=='MESH']
 if len(rigs)!=1 or not meshes:raise RuntimeError(f'Invalid cleaned cast: {name}')
 report[name]={'blend':str(blend),'glb':str(glb),'rig':rigs[0].name,'meshes':len(meshes),'bones':[b.name for b in rigs[0].data.bones]}
 bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True);print('CLEAN CAST',name,len(meshes),len(rigs[0].data.bones),flush=True)
(ROOT/'audit/cast-rigs-v003.json').write_text(json.dumps(report,indent=2),encoding='utf8')
