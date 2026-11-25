import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import city as K
import castlib as L
sc = L.reset(); col = L.collection('Set')
path = os.environ['BL']
with bpy.data.libraries.load(path, link=False) as (src, dst): dst.objects = list(src.objects)
rig = None
for o in dst.objects:
    if o is None or o.name.startswith('floor'): continue
    if o.type in ('MESH', 'ARMATURE'): col.objects.link(o)
    if o.type == 'ARMATURE': rig = o
print('RIG', rig, [m.object.name if m.object else None for o in dst.objects if o and o.type=='MESH' for m in o.modifiers if m.type=='ARMATURE'][:3])
for bn, r in [('upperleg01.L', (40, 0, 0)), ('upperarm01.L', (40, 0, 0)), ('lowerleg01.R', (40, 0, 0)), ('head', (30, 0, 0)), ('jaw', (20, 0, 0))]:
    pb = rig.pose.bones[bn]; pb.rotation_mode = 'XYZ'; pb.rotation_euler = [math.radians(a) for a in r]
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[1].default_value = 1.5
cam = K.cam(sc, (-4.0, -.2, 1.0), (0, 0, .95), lens=40)
K.setup_render(sc, 360, 480, 8); sc.view_settings.view_transform = 'Standard'
sc.render.filepath = os.environ.get('PNG', '/tmp/rt.png'); bpy.ops.render.render(write_still=True)
