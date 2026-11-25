import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT.parent/'SHARED_ASSETS/ep3/v001/assets/buggy-assemblies-v002.blend'))
bpy.context.view_layer.update();report=[]
for o in bpy.data.objects:
 if o.type=='EMPTY' and 'wheel assembly' in o.name.lower():
  points=[child.matrix_world@Vector(v) for child in o.children_recursive if child.type=='MESH' and not child.hide_render for v in child.bound_box]
  center=[(max(p[j] for p in points)+min(p[j] for p in points))/2 for j in range(3)] if points else None
  report.append({'name':o.name,'pivot':list(o.matrix_world.translation),'bounds_center':center,'local_location':list(o.location)})
(ROOT/'audit/wheel-pivots.json').write_text(json.dumps(report,indent=2),encoding='utf8');print(json.dumps(report),flush=True)
