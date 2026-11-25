"""Night Terror: Dead Roads - Episode 1 shots. SHOT=1..8 builds one shot and renders its frames.
env: RES (1.0 = 1080x1920), SAMP, FR="a,b" (frame range override), STEP (render every Nth frame), BLEND=1 save .blend"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Euler
import city as K
import castlib as L
V = K.V
HERE = os.path.dirname(os.path.abspath(__file__))
SHOT = int(os.environ.get('SHOT', '2'))
OUT = os.path.join(HERE, 'out', 'shots', f's{SHOT}'); os.makedirs(OUT, exist_ok=True)
FPS = 24
sc = L.reset(); col = L.collection('Set')
sc.render.fps = FPS


# ------------------------------------------------------------------ helpers
def ease(t): return t * t * (3 - 2 * t)

def key(o, f, loc=None, rot=None, interp='BEZIER'):
    if loc is not None: o.location = loc; o.keyframe_insert('location', frame=f)
    if rot is not None: o.rotation_euler = rot; o.keyframe_insert('rotation_euler', frame=f)

def linear(o):
    ad = o.animation_data
    if ad and ad.action:
        for fc in _fcurves(ad.action):
            for k in fc.keyframe_points: k.interpolation = 'LINEAR'

def _fcurves(act):
    if hasattr(act, 'fcurves'):
        try: return list(act.fcurves)
        except Exception: pass
    out = []
    for lay in getattr(act, 'layers', []):
        for st in lay.strips:
            for cb in st.channelbags: out += list(cb.fcurves)
    return out

def key_val(owner, path, f, v, const=False):
    setattr(owner, path, v) if not isinstance(owner, bpy.types.NodeSocket) else None
    owner.keyframe_insert(path, frame=f)

def aim(o, target):
    prev = o.rotation_euler.copy()
    o.rotation_euler = (V(target) - o.location).to_track_quat('-Z', 'Y').to_euler('XYZ', prev)

def camera(lens=30):
    c = bpy.data.cameras.new('shot'); c.lens = lens; c.sensor_width = 36; c.clip_start = .05; c.clip_end = 600
    o = bpy.data.objects.new('shot', c); sc.collection.objects.link(o); sc.camera = o
    return o

def cam_path(o, frames, locs, targets, lenses=None, focus=None):
    """keyframe camera position + aim (as rotation) + optional lens/focus at given frames, smooth"""
    for i, f in enumerate(frames):
        o.location = V(locs[i]); aim(o, targets[i])
        o.keyframe_insert('location', frame=f); o.keyframe_insert('rotation_euler', frame=f)
        if lenses: o.data.lens = lenses[i]; o.data.keyframe_insert('lens', frame=f)
        if focus:
            o.data.dof.use_dof = True; o.data.dof.focus_distance = focus[i]; o.data.dof.keyframe_insert('focus_distance', frame=f)

def rain_anim(r, f0, f1, seed=3):
    """re-scatter the rain sheet every frame (constant keys) so drops never repeat"""
    rng = random.Random(seed)
    base = r.location.copy()
    for f in range(f0, f1 + 1):
        r.location = base + V(rng.uniform(-.6, .6), rng.uniform(-.6, .6), rng.uniform(-.5, .5)); r.keyframe_insert('location', frame=f - .5)
    for fc in _fcurves(r.animation_data.action):
        for k in fc.keyframe_points: k.interpolation = 'CONSTANT'

def dup(root, loc, rot_z, scale=1.):
    """instance of an imported character: copy the empty + children sharing mesh data, with its own skeleton"""
    nr = root.copy(); col.objects.link(nr)
    rig = K.char_rig(root); nrig = None
    if rig:
        nrig = rig.copy(); col.objects.link(nrig); nrig.parent = nr; nrig.animation_data_clear(); nr['rig'] = nrig.name
    for ch in root.children:
        if ch is rig: continue
        c = ch.copy(); col.objects.link(c); c.parent = nr
        for m in c.modifiers:
            if m.type == 'ARMATURE' and nrig: m.object = nrig
    nr.location = loc; nr.rotation_euler = (0, 0, rot_z); nr.scale = (scale,) * 3
    return nr

def flicker(light, f0, f1, base, seed=1, p_off=.12):
    rng = random.Random(seed)
    for f in range(f0, f1 + 1):
        light.energy = base * (0 if rng.random() < p_off else rng.uniform(.8, 1.05)); light.keyframe_insert('energy', frame=f)
    for fc in _fcurves(light.animation_data.action):
        for k in fc.keyframe_points: k.interpolation = 'CONSTANT'

def lightning(sun, f_hits, base=.35, peak=9.0):
    sun.energy = base; sun.keyframe_insert('energy', frame=0)
    for fh in f_hits:
        for df, v in ((-1, base), (0, peak), (1, peak * .3), (2, peak * .8), (5, base)):
            sun.energy = v; sun.keyframe_insert('energy', frame=fh + df)
    for fc in _fcurves(sun.animation_data.action):
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'

def moon_obj():
    return bpy.data.lights.get('moon')

def nt_car(loc, rot_z, lights_on=True, glow=60):
    car, parts = K.night_terror(V(loc), rot_z, col)
    for o in list(parts):
        if o.name in ('Camera', 'Cube', 'Light') or o.name.startswith(('Camera', 'Cube', 'Light')) and o.parent is car:
            bpy.data.objects.remove(o, do_unlink=True); parts.remove(o)
    glowm = bpy.data.materials.new('HeadGlow'); glowm.use_nodes = True
    b = glowm.node_tree.nodes['Principled BSDF']; b.inputs['Emission Color'].default_value = (1, 1, 1, 1)
    b.inputs['Emission Strength'].default_value = glow if lights_on else 0
    for o in parts:
        if o.type == 'MESH' and 'projector lens' in o.name.lower():
            o.data.materials.clear(); o.data.materials.append(glowm)
    # headlight spots parented to the car (car local: nose ~ y -3.4, lamps x -.52 / .98 rel root .4,-2)
    spots = []
    for hx in (-.52, .98):
        hl = bpy.data.lights.new('head', 'SPOT'); hl.energy = 6500 if lights_on else 0; hl.color = K.C('#e8f0ff')
        hl.spot_size = math.radians(34); hl.spot_blend = .3; hl.shadow_soft_size = .06
        ho = bpy.data.objects.new('head', hl); col.objects.link(ho); ho.parent = car
        ho.location = (hx, -3.65, .88); ho.rotation_euler = (math.radians(-88.5), 0, 0); spots.append(hl)
    return car, parts, glowm, spots

def spin_wheels(parts, f0, f1, dist):
    """add a pivot per wheel assembly at its mesh centre and spin rim+tire by distance/radius"""
    bpy.context.view_layer.update()
    for asm in [o for o in parts if o.name.endswith('wheel assembly')]:
        subs = [c for c in asm.children if not c.name.startswith('Brake')]
        meshes = [m for s in subs for m in [s] + list(s.children_recursive) if m.type == 'MESH']
        if not meshes: continue
        pts = [m.matrix_world @ V(c) for m in meshes for c in m.bound_box]
        mn = V((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        mx = V((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        ctr = (mn + mx) / 2; rad = (mx.z - mn.z) / 2
        pv = bpy.data.objects.new('pivot', None); col.objects.link(pv)
        pv.parent = asm; pv.matrix_world = __import__('mathutils').Matrix.Translation(ctr)
        bpy.context.view_layer.update()
        for s in subs:
            mw = s.matrix_world.copy(); s.parent = pv; s.matrix_world = mw
        pv.rotation_mode = 'XYZ'
        r0 = pv.rotation_euler.copy()
        pv.keyframe_insert('rotation_euler', frame=f0)
        pv.rotation_euler = (r0.x - dist / max(rad, .2), r0.y, r0.z); pv.keyframe_insert('rotation_euler', frame=f1)
        linear(pv)


def render(f0, f1, res=None, samp=None):
    fr = os.environ.get('FR')
    if fr: f0, f1 = map(int, fr.split(','))
    sc.frame_start, sc.frame_end = f0, f1; sc.frame_step = int(os.environ.get('STEP', '1'))
    r = float(os.environ.get('RES', res or '.5'))
    K.setup_render(sc, int(1080 * r) // 2 * 2, int(1920 * r) // 2 * 2, int(os.environ.get('SAMP', samp or '16')))
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = .5
    sc.render.image_settings.file_format = 'PNG'
    sc.render.filepath = os.path.join(OUT, 'f')
    sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = .03
    sc.render.use_persistent_data = True
    sc.render.use_overwrite = False
    if os.environ.get('THREADS'): sc.render.threads_mode = 'FIXED'; sc.render.threads = int(os.environ['THREADS'])
    if os.environ.get('BLEND'): bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, f's{SHOT}.blend'))
    bpy.ops.render.render(animation=True)


