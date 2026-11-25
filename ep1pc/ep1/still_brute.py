"""Style frame C: the Night Terror skids to a stop, headlights blazing through fog and rain; the Brute
stands in the beams blocking the road. Camera low behind the car's rear quarter."""
import os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import city as K
import castlib as L
V = K.V
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out'); os.makedirs(OUT, exist_ok=True)
sc = L.reset(); col = L.collection('Set')
rng = K.street(col, length=140, seed=9, dead_lamps=(0, 1, 2, 3, 5, 6))
K.sky(sc, fog=float(os.environ.get('FOG', '.022')))
paints = ['#4a1a16', '#1e2a3a', '#5a5248']
for i, (p, r) in enumerate([((4.2, -24, 0), -.5), ((-3.9, -33, 0), .3), ((3.0, -48, 0), 1.4)]):
    K.sedan(col, V(p), r, K.carpaint(f'Paint{i}', paints[i]), rng)
car, parts = K.night_terror(V(.4, -2, 0), math.radians(4), col)
bpy.context.view_layer.update()
# headlights: two strong spots + a glow card at the car nose
for hx in (-.12, 1.38):
    hl = bpy.data.lights.new('head', 'SPOT'); hl.energy = float(os.environ.get('HE','6500')); hl.color = K.C('#e8f0ff'); hl.spot_size = math.radians(34); hl.spot_blend = .3
    hl.shadow_soft_size = .06
    ho = bpy.data.objects.new('head', hl); col.objects.link(ho); ho.location = (hx, -5.65, .88)
    ho.rotation_euler = (math.radians(-88.5), 0, math.radians(3))
for o in parts:
    if o.type == 'MESH' and 'projector lens' in o.name.lower():
        m = bpy.data.materials.new('HeadGlow'); m.use_nodes = True
        b = m.node_tree.nodes['Principled BSDF']; b.inputs['Emission Color'].default_value = (1, 1, 1, 1); b.inputs['Emission Strength'].default_value = 60
        o.data.materials.clear(); o.data.materials.append(m)
br = K.char('brute', V(2.0, -12.5, 0), math.radians(188), 1.0)
K.char('runner', V(-3.4, -26, 0), math.radians(160), 1.0)
K.char('husk', V(3.4, -29, 0), math.radians(200), 1.0)
K.rain(col, (0, -10, 0), size=(14, 26, 10), count=int(os.environ.get('RAIN', '3500')))
# moonlit rim from behind the Brute
rl = bpy.data.lights.new('rim', 'AREA'); rl.energy = 2500; rl.size = 4; rl.color = K.C('#7a9aff')
ro = bpy.data.objects.new('rim', rl); col.objects.link(ro); ro.location = (0, -30, 6); ro.rotation_euler = (math.radians(70), 0, 0)
cam = K.cam(sc, tuple(map(float, os.environ.get('CAM', '3.7,0.2,1.15').split(','))), (1.3, -13, 1.6), lens=float(os.environ.get('LENS', '26')))
sc.view_settings.exposure = float(os.environ.get('EXP','1.0'))
cam.data.dof.use_dof = True; cam.data.dof.focus_distance = 13.8; cam.data.dof.aperture_fstop = 2.8
K.setup_render(sc, int(1080 * float(os.environ.get('RES', '.5'))), int(1920 * float(os.environ.get('RES', '.5'))), int(os.environ.get('SAMP', '32')))
sc.render.filepath = os.path.join(OUT, os.environ.get('NAME', 'styleC.png'))
bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, 'styleC.blend'))
