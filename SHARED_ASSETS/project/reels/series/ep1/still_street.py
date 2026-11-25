"""Style frame A: low camera on the wet avenue at 3:12 AM. A Crawler drags itself out from under a
wrecked car toward the lens; a Husk waits under the only working lamp; fog and rain down the street."""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import city as K
import castlib as L
V = K.V
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'); os.makedirs(OUT, exist_ok=True)
sc = L.reset(); col = L.collection('Set')
rng = K.street(col, length=140, seed=5)
K.sky(sc, fog=float(os.environ.get('FOG', '.018')))
# wrecks along the street
paints = ['#4a1a16', '#1e2a3a', '#5a5248', '#22301e', '#6a6a66']
wr = [((-2.9, -5.2, 0), .3), ((3.6, -20, 0), -.4), ((-1.8, -31, 0), 1.2), ((4.0, -44, 0), .1), ((-3.8, -58, 0), -.2)]
for i, (p, r) in enumerate(wr):
    K.sedan(col, V(p), r, K.carpaint(f'Paint{i}', paints[i % len(paints)]), rng)
K.trash(col, (5.4, -12, .16), rng, 7); K.trash(col, (-5.6, -26, .16), rng, 5)
# hero lamp near the Husk, extra warm pool
hl = bpy.data.lights.new('pool', 'SPOT'); hl.energy = 2600; hl.color = K.C('#ffb060'); hl.spot_size = math.radians(70); hl.spot_blend = .8
ho = bpy.data.objects.new('pool', hl); col.objects.link(ho); ho.location = (1.2, -24, 7.5)
# cast
cr = K.char('crawler', V(-.4, -3.0, 0), math.radians(-170), 1.0)       # head toward camera, body under the car
hk = K.char('husk', V(1.0, -24, 0), math.radians(-10), 1.0)
# headlight glow of a far car through the fog (rim light on everything)
bl = bpy.data.lights.new('far', 'AREA'); bl.energy = 4000; bl.size = 3; bl.color = K.C('#cfe0ff')
bo = bpy.data.objects.new('far', bl); col.objects.link(bo); bo.location = (0, -70, 1.2); bo.rotation_euler = (math.radians(90), 0, 0)
K.rain(col, (0, -16, 0), size=(16, 34, 12), count=int(os.environ.get('RAIN', '3000')))
cam = K.cam(sc, (.5, 1.6, .9), (-.8, -22, .9), lens=22)
fl = bpy.data.lights.new('near', 'SPOT'); fl.energy = 1800; fl.color = K.C('#ffae5a'); fl.spot_size = math.radians(80); fl.spot_blend = .7
fo = bpy.data.objects.new('near', fl); col.objects.link(fo); fo.location = (2.5, -3, 6.8)
sc.view_settings.exposure = 1.3
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 3.6; cam.data.dof.aperture_fstop = 2.2
K.setup_render(sc, int(1080 * float(os.environ.get('RES', '.5'))), int(1920 * float(os.environ.get('RES', '.5'))), int(os.environ.get('SAMP', '32')))
sc.render.filepath = os.path.join(OUT, os.environ.get('NAME', 'styleA.png'))
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'styleA.blend'))
