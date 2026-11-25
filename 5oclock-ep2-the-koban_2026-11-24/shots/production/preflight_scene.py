"""Record scene technical pre-flight numbers alongside the selected-frame renders."""
import json
from bpy_extras.object_utils import world_to_camera_view

def scene_report(scene, camera, duration, task):
    assert scene.render.fps==24
    assert (scene.render.resolution_x,scene.render.resolution_y)==(1080,1920)
    assert .001<=camera.data.clip_start<camera.data.clip_end
    return {
        'shot':task,
        'frames':duration,
        'resolution_percent':scene.render.resolution_percentage,
        'camera_clip_m':[camera.data.clip_start,camera.data.clip_end],
        'light_energy':{o.name:round(o.data.energy,3) for o in scene.objects if o.type=='LIGHT'},
        'key_projections':[],
    }

def record_pose(scene,cam,frame,report):
    figures=[]
    for actor in scene.objects:
        if actor.type!='ARMATURE':
            continue
        head=actor.pose.bones.get('J_Bip_C_Head')
        if head is None:
            continue
        position=actor.matrix_world@head.head
        camera=world_to_camera_view(scene,cam,position)
        figures.append({'actor':actor.name,'head_m':[round(x,3) for x in position],
                        'head_uv_depth':[round(x,3) for x in camera]})
    report['key_projections'].append({'source_frame':frame,'figures':figures})

def write_report(out,report):
    (out/'preflight.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
