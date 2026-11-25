import bpy
a=bpy.data.objects['Sam_Rig']
for b in a.pose.bones:
 if 'J_Bip_L_' in b.name and any(k in b.name for k in ('Thumb','Index','Middle','Ring','Little')): print(b.name,tuple(b.head))
