import bpy
from mathutils import Vector
a=bpy.data.objects.get('Sam_Rig')
print('RIG', a.matrix_world, a.animation_data)
for b in a.pose.bones:
    if any(fragment in b.name.lower() for fragment in ('hips','spine','chest','neck','head','arm','hand','leg','foot','toe')) and 'thumb' not in b.name.lower():
        print('BONE',b.name, tuple(round(x,3) for x in b.head),tuple(round(x,3) for x in b.tail))
for o in bpy.context.scene.objects:
    if o.type in ('MESH','CURVE','CAMERA','LIGHT'):
        print('OBJ',o.name,o.type,o.hide_render,o.parent and o.parent.name,o.parent_bone, [m.name for m in o.data.materials if m] if hasattr(o.data,'materials') else '',list(o.data.shape_keys.key_blocks.keys())[:25] if o.type=='MESH' and o.data.shape_keys else '')
