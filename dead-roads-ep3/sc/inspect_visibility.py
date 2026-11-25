import bpy,json,os
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];version=os.environ.get('INSPECT_VERSION','v014');bpy.ops.wm.open_mainfile(filepath=str(ROOT/f'assets/{version}/shot18.blend'));s=bpy.context.scene;s.frame_set(30);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get()
result={'meshes':[],'glass':[],'rigs':[]}
for o in s.objects:
 if o.type=='ARMATURE' and 'husk' in o.name.lower() and abs(o.matrix_world.translation.x)<1 and o.matrix_world.translation.y<25:
  h=o.matrix_world@o.pose.bones['head'].head;origin=s.camera.matrix_world.translation;direction=(h-origin).normalized();hit=s.ray_cast(dg,origin,direction,distance=(h-origin).length)
  result['rigs'].append({'name':o.name,'parent':o.parent.name if o.parent else None,'rotation_mode':o.rotation_mode,'location':list(o.location),'world_location':list(o.matrix_world.translation),'head_world':list(h),'first_ray_hit':hit[4].name if hit[0] else None,'ray_hit_position':list(hit[1]) if hit[0] else None})
for o in s.objects:
 if o.type=='MESH' and 'husk' in o.name.lower() and len(result['meshes'])<6:
  e=o.evaluated_get(dg);pts=[e.matrix_world@Vector(v) for v in e.bound_box]
  result['meshes'].append({'name':o.name,'hidden':o.hide_render,'parent':o.parent.name if o.parent else None,'vertices':len(o.data.vertices),'bounds':[[min(v[j] for v in pts),max(v[j] for v in pts)] for j in range(3)],'materials':[m.name for m in o.data.materials if m]})
for m in bpy.data.materials:
 if 'glass' in m.name.lower() and m.use_nodes:
  bs=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if bs:result['glass'].append({'name':m.name,'transmission':bs.inputs['Transmission Weight'].default_value,'roughness':bs.inputs['Roughness'].default_value,'base':list(bs.inputs['Base Color'].default_value)})
(ROOT/f'audit/visibility-{version}.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result),flush=True)
