import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SHARED=ROOT.parent/'SHARED_ASSETS';DEST=SHARED/'ep3/v001/assets/trike-wreck-source-v001.blend'
if DEST.exists():raise RuntimeError('Refusing overwrite')
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(SHARED/'project/reels/series/models/trike/ivory-dead-roads-trike-v2.glb'))
col=bpy.data.collections.new('WRECK_TRIKE');bpy.context.scene.collection.children.link(col)
visible=[]
for o in list(bpy.context.scene.objects):
 if o.type!='MESH' or 'hull' in o.name.lower():continue
 for old in list(o.users_collection):old.objects.unlink(o)
 col.objects.link(o);visible.append(o)
bpy.ops.object.select_all(action='DESELECT')
for o in visible:o.select_set(True)
bpy.context.view_layer.objects.active=visible[0];bpy.ops.object.join();mesh=bpy.context.object;mesh.name='EP3 Wreck trike mesh';mesh.parent=None
for o in list(bpy.context.scene.objects):
 if o!=mesh:bpy.data.objects.remove(o,do_unlink=True)
for mat in bpy.data.materials:mat.name='EP3_WRECK_'+mat.name
bpy.ops.wm.save_as_mainfile(filepath=str(DEST),compress=True)
print('WRECK CACHE',DEST,flush=True)
