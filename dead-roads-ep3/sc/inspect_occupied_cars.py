import bpy,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/v006/shot18.blend'))
s=bpy.context.scene;s.frame_set(30);bpy.context.view_layer.update();report=[]
for o in s.objects:
 if o.type=='ARMATURE' and 'husk' in o.name.lower():
  p=o.matrix_world@o.pose.bones['head'].head
  report.append({'rig':o.name,'location':list(o.location),'scale':list(o.scale),'head':list(p),'camera_projection':list(world_to_camera_view(s,s.camera,p))})
  if len(report)==3:break
props=[]
for o in bpy.data.objects:
 if o.type=='MESH' and any(w in o.name for w in ('BodyWindshield','InteriorSeatsColor1','BodyHeadlights')):
  pts=[o.matrix_world@Vector(v) for v in o.bound_box]
  props.append({'name':o.name,'bbox':[[min(v[j] for v in pts),max(v[j] for v in pts)] for j in range(3)]})
print('HUSKS',json.dumps(report),flush=True);print('PROP_PARTS',json.dumps(props[:8]),flush=True)
