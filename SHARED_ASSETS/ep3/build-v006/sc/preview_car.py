import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(ROOT.parent/'SHARED_ASSETS/ep3/v001/assets/night-terror-import-v001.blend')) as (s,d): d.collections=['NT_ORIGINAL']
bpy.context.scene.collection.children.link(d.collections[0])
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=12; s.render.threads_mode='FIXED'; s.render.threads=4
s.render.resolution_x=800;s.render.resolution_y=600;s.render.resolution_percentage=100;s.view_settings.view_transform='AgX'
w=bpy.data.worlds.new('Studio');w.use_nodes=True;w.node_tree.nodes['Background'].inputs[0].default_value=(.16,.17,.2,1);w.node_tree.nodes['Background'].inputs[1].default_value=.5;s.world=w
bpy.ops.mesh.primitive_plane_add(size=200);floor=bpy.context.object
m=bpy.data.materials.new('Floor');m.diffuse_color=(.09,.10,.11,1);floor.data.materials.append(m)
for p,e,size in [((-4,-4,7),1500,5),((3,4,5),2000,4)]:
 l=bpy.data.lights.new('Studio','AREA');l.energy=e;l.shape='DISK';l.size=size;o=bpy.data.objects.new(l.name,l);s.collection.objects.link(o);o.location=p;o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
c=bpy.data.cameras.new('Camera');o=bpy.data.objects.new('Camera',c);s.collection.objects.link(o);o.location=(-7,-7,4.3);o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler();c.lens=48;s.camera=o
s.render.filepath=str(ROOT/'audit/original-car-check.png');bpy.ops.render.render(write_still=True)
