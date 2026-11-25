import sys, os; sys.path.insert(0, '/home/user/w/sc')
from lib import *
sc = reset(); K = city(); import castlib as L
col = L.collection('Set'); K.street(col, length=80, width=16, seed=4); K.sky(sc, fog=.02)
for i, x in enumerate((-2.2, 0, 2.4)):
    rg = walker(V(x, -14 - abs(x) * .8, 0), math.radians(180 + x * 6), seed=i)
    fn, per = shamble(i); act(rg, 1, 60, fn, 2); move_keys(rg, 1, 23 if x == 0 else 60, .55, i, per)
    if x == 0: headshot(rg, 24, i)
h = rg  # unused
spot('beamL', (-.8, 2, 1.4), (0, -14, 1.2), 9000, size=32)
spot('beamR', (.8, 2, 1.4), (0, -14, 1.2), 9000, size=32)
cam(V(0, 0, 1.7), V(0, -14, 1.45), 50)
blood_burst(V(0, -14.1, 1.62), V(0, -1, .2), 24, seed=3)
render_setup(sc, .25, 8); sc.frame_start = 1; sc.frame_end = 48
sc.render.filepath = '/home/user/w/out/probe/walk/f'
bpy.ops.wm.save_as_mainfile(filepath='/home/user/w/out/probe/walk.blend')
bpy.ops.render.render(animation=True)
