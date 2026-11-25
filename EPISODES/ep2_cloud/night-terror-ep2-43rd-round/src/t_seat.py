import sys; sys.path.insert(0, '/home/user/w/sc')
from lib import *
sc = reset(); tc, T = trike(); rc, rig = rider(); seat_rider(rig, T['TRIKE_body'])
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (.05, .05, .06, 1)
for nm, loc, e in (('k', (-3, -5, 5), 3000), ('r', (3, 4, 4), 2000)):
    l = bpy.data.lights.new(nm, 'AREA'); l.energy = e; l.size = 3; lo = bpy.data.objects.new(nm, l); sc.collection.objects.link(lo); lo.location = loc
    lo.rotation_euler = (V(0, 0, 1.5) - V(loc)).to_track_quat('-Z', 'Y').to_euler()
render_setup(sc, .35, 12, 1600, 1200)
for nm, loc in (('side', (0.2, -6, 1.9)), ('q34', (-4, -3.5, 2.8)), ('top', (-1.5, -1.2, 4.5))):
    c = cam(loc, (0.1, 0, 1.6), 40 if nm != 'top' else 30)
    sc.render.filepath = f'/home/user/w/out/probe/seat_{nm}.png'; bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath='/home/user/w/out/probe/seat.blend')
