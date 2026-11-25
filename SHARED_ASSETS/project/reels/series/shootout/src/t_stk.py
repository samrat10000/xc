import sys; sys.path.insert(0, '/home/user/w/sc')
from lib import *
sc = reset(); rg = stalker(V(0, 0, 0), 0)
def fn(t, f):
    gph = t * 4.0
    d = stalk_pose(t, gait=1 if t < 1 else 0, gph=gph, jaw=max(0, t - 1.2), tilt=20 * math.sin(t * 2), look=(0, -15 if t > 1.2 else 0))
    d['_root'] = (V(0, -1.3 * min(t, 1), .05 * abs(math.sin(gph)) * (t < 1)), (0, 0, 0)); return d
sact(rg, 1, 48, fn)
w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True; w.node_tree.nodes['Background'].inputs[0].default_value = (.06, .06, .07, 1)
for nm, loc, e in (('k', (-3, -5, 5), 2500), ('r', (3, 4, 4), 2000)):
    l = bpy.data.lights.new(nm, 'AREA'); l.energy = e; l.size = 3; lo = bpy.data.objects.new(nm, l); sc.collection.objects.link(lo); lo.location = loc
    lo.rotation_euler = (V(0, 0, 1.2) - V(loc)).to_track_quat('-Z', 'Y').to_euler()
render_setup(sc, .3, 8, 1200, 1200); cam(V(-5, -6, 1.8), V(0, -.6, 1.3), 40)
for f in (1, 9, 17, 34, 48):
    sc.frame_set(f); sc.render.filepath = f'/home/user/w/out/probe/stk_{f:02d}.png'; bpy.ops.render.render(write_still=True)
