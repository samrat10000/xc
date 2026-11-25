import os,sys,math
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import bpy; from mathutils import Vector
import city as K, castlib as L
sc=L.reset(); col=L.collection('Set')
car,parts=K.night_terror(Vector((.4,-2,0)),math.radians(4),col)
bpy.context.view_layer.update()
mn=Vector((1e9,)*3); mx=-mn
for o in parts:
    if o.type!='MESH': continue
    for c in o.bound_box:
        w=o.matrix_world@Vector(c); mn=Vector(map(min,mn,w)); mx=Vector(map(max,mx,w))
print('BBOX',mn,mx)
for o in parts:
    n=o.name.lower()
    if any(k in n for k in ('head','light','lamp','tail')) and o.type=='MESH':
        print('L',o.name,(o.matrix_world@Vector(o.bound_box[0])), (o.matrix_world@Vector(o.bound_box[6])))
