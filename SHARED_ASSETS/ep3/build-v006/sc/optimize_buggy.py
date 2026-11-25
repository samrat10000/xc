"""Merge static mesh details inside their existing assembly. Keep original intact."""
import bpy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SHARED=ROOT.parent/'SHARED_ASSETS';DEST=SHARED/'ep3/v001/assets/buggy-assemblies-v002.blend'
if DEST.exists():raise RuntimeError('Refusing overwrite')
bpy.ops.wm.open_mainfile(filepath=str(SHARED/'ep3/v001/assets/night-terror-import-v001.blend'))
col=bpy.data.collections['NT_ORIGINAL'];groups={};keep=[]
for o in list(col.all_objects):
 if o.type!='MESH':continue
 if 'hull' in o.name.lower():o.hide_render=True;continue
 # Keep seat, steering, lamps and hood independently editable for the refit.
 if any(n in o.name.lower() for n in ('seat','steering','lamp','light','lens','led','hood top')):keep.append(o.name);continue
 assembly=o.parent
 while assembly and assembly.parent and assembly.parent.name!='NT_EP3_ROOT':assembly=assembly.parent
 label=assembly.name if assembly else 'Loose parts';groups.setdefault(label,[]).append(o)
before=len(bpy.context.scene.objects)
for label,objects in groups.items():
 if len(objects)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0]
 bpy.ops.object.join();bpy.context.object.name='Merged '+label
bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True)
print('MERGED',before,'objects to',len(bpy.context.scene.objects),flush=True)
(ROOT/'audit/buggy-optimization.json').write_text(json.dumps({'source':'night-terror-import-v001.blend','output':str(DEST),'objects_before':before,'objects_after':len(bpy.context.scene.objects),'preserved':keep},indent=2),encoding='utf8')
