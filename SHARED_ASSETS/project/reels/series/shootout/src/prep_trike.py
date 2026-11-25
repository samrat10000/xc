import bpy, math
from mathutils import Vector, Matrix
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='/home/user/w/models/trike/ivory-dead-roads-trike-v2.glb')
col = bpy.data.collections.new('TRIKE'); bpy.context.scene.collection.children.link(col)
objs = [o for o in bpy.data.objects]
for o in objs:
    for c in o.users_collection: c.objects.unlink(o)
    col.objects.link(o)
# flatten hierarchy
for o in objs:
    if o.parent:
        mw = o.matrix_world.copy(); o.parent = None; o.matrix_world = mw
for o in objs:
    if o.type == 'EMPTY': bpy.data.objects.remove(o)
ms = [o for o in bpy.data.objects if o.type == 'MESH']
for o in ms:
    if 'hull' in o.name.lower(): o.hide_render = True; o.hide_viewport = True
def ctr(o): return sum((o.matrix_world @ Vector(b) for b in o.bound_box), Vector()) / 8
root = bpy.data.objects.new('TRIKE_root', None); col.objects.link(root)
body = bpy.data.objects.new('TRIKE_body', None); col.objects.link(body); body.parent = root
axles = {'wF': (Vector((-3.32, 0, .94)), .94, .5), 'wRL': (Vector((1.85, 2.084, 1.0)), 1.0, .62), 'wRR': (Vector((1.85, -2.084, 1.0)), 1.0, .62)}
wh = {}
for k, (p, R, hw) in axles.items():
    e = bpy.data.objects.new(k, None); col.objects.link(e); e.location = p; e.parent = root; wh[k] = e
cnt = {k: 0 for k in wh}
bpy.context.view_layer.update()
for o in ms:
    c = ctr(o); dmax = max(o.dimensions)
    got = None
    for k, (p, R, hw) in axles.items():
        dxz = math.hypot(c.x - p.x, c.z - p.z)
        if dxz < R * .97 and abs(c.y - p.y) < hw and dmax < 2 * R + .1:
            # skip parts that do not rotate: names hinting brakes/fork/suspension
            nm = o.name.lower()
            if any(s in nm for s in ('fork', 'caliper', 'susp', 'spring', 'damper', 'arm', 'gun', 'mg', 'barrel', 'ammo', 'fender', 'brake', 'shock', 'upright', 'knuckle', 'brake line', 'mount')):
                continue
            got = k; break
    mw = o.matrix_world.copy()
    if got: o.parent = wh[got]; cnt[got] += 1
    else: o.parent = body
    o.matrix_world = mw
print('wheel parts', cnt)
for k in wh: print(k, sorted({o.name.split('.')[0] for o in wh[k].children})[:40])
bpy.ops.wm.save_as_mainfile(filepath='/home/user/w/sc/trike.blend')
