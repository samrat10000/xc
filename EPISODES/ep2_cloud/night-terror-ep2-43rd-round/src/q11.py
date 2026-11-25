import bpy
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/home/user/w/models/trike/ivory-dead-roads-trike-v2.glb')
o=bpy.data.objects['Front mud-terrain knobby tyre']
print(o.matrix_world.translation, o.parent and o.parent.name, o.parent and o.parent.matrix_world.translation, sum((o.matrix_world@Vector(b) for b in o.bound_box),Vector())/8)
