"""Compare bounded finger-flex directions against the opposing forearm, no mesh edits."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/v008/shot06.blend'));s=bpy.context.scene;s.frame_set(30);bpy.context.view_layer.update()
sam=next(o for o in s.objects if o.type=='ARMATURE' and o.name.startswith('SAM'));rider=next(o for o in s.objects if o.type=='ARMATURE' and o.name.startswith('RIDER'));results={}
for rig,side,other,other_side in ((sam,'R',rider,'L'),(rider,'L',sam,'R')):
 a=other.matrix_world@other.pose.bones['lowerarm01.'+other_side].head;b=other.matrix_world@other.pose.bones['wrist.'+other_side].head;axis=(b-a).normalized();tests=[]
 for rot_axis in (0,2):
  for sign in (-1,1):
   for factor in (.55,.8,1.0):
    for digit in range(2,6):
     for segment,curl in ((1,45),(2,55),(3,30)):
      pb=rig.pose.bones[f'finger{digit}-{segment}.{side}'];pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0);pb.rotation_euler[rot_axis]=math.radians(sign*factor*curl)
    bpy.context.view_layer.update();score=0;distances=[]
    for digit in range(2,6):
     point=rig.matrix_world@rig.pose.bones[f'finger{digit}-3.{side}'].tail;along=max(0,min((b-a).length,(point-a).dot(axis)));distance=(point-(a+axis*along)).length;distances.append(round(distance,4));score+=(distance-.045)**2
    tests.append({'axis':rot_axis,'sign':sign,'factor':factor,'score':round(score,7),'tip_distances_m':distances})
 results[rig.name]=sorted(tests,key=lambda d:d['score'])
(ROOT/'audit/hand-curl-candidates.json').write_text(json.dumps(results,indent=2),encoding='utf8');print(json.dumps({k:v[:3] for k,v in results.items()}),flush=True)
