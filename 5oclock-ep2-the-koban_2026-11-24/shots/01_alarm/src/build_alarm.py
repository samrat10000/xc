"""Render a real-scale phone as a transparent EEVEE cel and export camera geometry."""
import json
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view

HERE = Path(__file__).resolve().parent
args = sys.argv[sys.argv.index('--') + 1:]
OUT, SCALE, frame_spec, revision = Path(args[0]).resolve(), float(args[1]), args[2], int(args[3])
OUT.mkdir(parents=True, exist_ok=True)
exec(compile((HERE / 'toonlib.py').read_text(), 'toonlib.py', 'exec'))

sc.render.fps = 24
sc.frame_end = 72
sc.eevee.taa_render_samples = 16
SUNV = tuple(Vector((.93, .32, .51)).normalized())
rail = toon('Graphite aluminium', (.154, .142, .197), (.317, .296, .359))
chamfer = toon('Fine edge', (.29, .264, .31), (.64, .48, .36))
glass = toon('Ceramic glass surround', (.069, .064, .10), (.125, .11, .156))
detail = toon('Side buttons', (.12, .11, .155), (.40, .34, .37))
port = emis('USB and grille inset', (.009, .007, .012))
phone = empty('Phone on the tatami')
WID, LENGTH, RADIUS = .0726, .1495, .0106


def loop(w, h, r, z):
    points = []
    for turn, (x, y) in enumerate(((w / 2 - r, h / 2 - r),
                                     (-w / 2 + r, h / 2 - r),
                                     (-w / 2 + r, -h / 2 + r),
                                     (w / 2 - r, -h / 2 + r))):
        for step in range(9):
            a = (turn + step / 8) * math.pi / 2
            points.append((x + math.cos(a) * r, y + math.sin(a) * r, z))
    return points


def handset_body():
    rings = [(WID-.0024, LENGTH-.0024, RADIUS-.0012, .00025),
             (WID, LENGTH, RADIUS, .0026),
             (WID, LENGTH, RADIUS, .00695),
             (WID-.00115, LENGTH-.00115, RADIUS-.00058, .00825),
             (WID-.0027, LENGTH-.0027, RADIUS-.00135, .00870)]
    verts = [p for ring in rings for p in loop(*ring)]
    n = len(verts) // len(rings)
    faces = [tuple(reversed(range(n)))]
    for ring in range(len(rings) - 1):
        for i in range(n):
            j = (i + 1) % n
            a, b = ring * n, (ring + 1) * n
            faces.append((a+i, a+j, b+j, b+i))
    faces.append(tuple(range((len(rings)-1) * n, len(verts))))
    mesh = bpy.data.meshes.new('Rounded, chamfered rail')
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new(mesh.name, mesh)
    sc.collection.objects.link(obj)
    obj.parent = phone
    for material in (rail, chamfer, glass):
        mesh.materials.append(material)
    for polygon in mesh.polygons:
        polygon.use_smooth = False
        polygon.material_index = 0
        if 1 + 2*n <= polygon.index < 1 + 3*n:
            # A narrow warm highlight along the light-facing edge.
            local_edge = (polygon.index - 1) % n
            light_edge = local_edge >= 30 or local_edge <= 4
            polygon.material_index = 1 if light_edge else 0
        if polygon.index >= 1 + 3*n:
            polygon.material_index = 2
    outline(obj, .00025)


def screen():
    w, h, r = WID - .0062, LENGTH - .0068, RADIUS - .0031
    verts = loop(w, h, r, .00877)
    mesh = bpy.data.meshes.new('Screen geometry')
    mesh.from_pydata(verts, [], [tuple(range(len(verts)))])
    uv = mesh.uv_layers.new()
    for corner in mesh.loops:
        x, y, _ = verts[corner.vertex_index]
        uv.data[corner.index].uv = (x / w + .5, y / h + .5)
    obj = bpy.data.objects.new('Mirrored 6:00 and 3% battery', mesh)
    sc.collection.objects.link(obj)
    obj.parent = phone
    mat = emis('Painted lock screen', (0, 0, 0))
    nodes = mat.node_tree.nodes
    texture = nodes.new('ShaderNodeTexImage')
    texture.image = bpy.data.images.load(str(HERE / 'display.png'))
    texture.image.pack()
    texture.interpolation = 'Linear'
    mat.node_tree.links.new(texture.outputs['Color'], nodes.get('Emission').inputs[0])
    mesh.materials.append(mat)


def inset(name, dimensions, location, material, bevel):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.object
    obj.name, obj.dimensions = name, dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.location, obj.parent = location, phone
    obj.data.materials.append(material)
    mod = obj.modifiers.new('Corner radius', 'BEVEL')
    mod.width, mod.segments = bevel, 4


handset_body()
screen()
for center, length in ((.040, .013), (.022, .012)):
    inset('Volume switch', (.0015, length, .0019), (-WID/2, center, .0052), detail, .00055)
inset('Sleep button', (.0015, .014, .0020), (WID/2, .030, .0052), detail, .00055)
inset('USB-C recess', (.0080, .00040, .00265), (0, -LENGTH/2-.00005, .0045), port, .0002)
for i in (-3, -2, -1, 1, 2, 3):
    inset('Grille aperture', (.00105, .00036, .00103),
          (math.copysign(.0069, i) + i*.0021, -LENGTH/2-.00007, .0046), port, .00015)

camera_data = bpy.data.cameras.new('48 mm insert')
camera_data.lens, camera_data.sensor_fit, camera_data.sensor_height = 48, 'VERTICAL', 36
if revision >= 3:
    camera_data.lens = 46
camera = bpy.data.objects.new('Camera', camera_data)
sc.collection.objects.link(camera)
sc.camera = camera


def lamp(name, energy, color, direction):
    light = bpy.data.lights.new(name, 'SUN')
    light.energy, light.color, light.angle = energy, color, .075
    obj = bpy.data.objects.new(name, light)
    sc.collection.objects.link(obj)
    obj.rotation_euler = (-Vector(direction)).to_track_quat('-Z', 'Y').to_euler()


lamp('Shoji dawn', 4.1, (1, .81, .64), SUNV)
lamp('Cool room fill', .25, (.67, .75, 1), (-.4, -.56, .9))


def ease(t):
    t = min(max(t, 0), 1)
    return t*t*(3 - 2*t)


def contact_pose(f):
    hold = f - (f-1) % 2
    shift, rattle, yaw = 0.0, 0.0, 0.0
    for start, distance, amp in ((9, .0068, .0019), (29, .0092, .0027), (49, .0074, .0023)):
        dt = hold - start
        shift += distance * (1 - (1 - min(1, max(0, dt / 12))) ** 2)
        if 0 <= dt < 12:
            impulse = math.exp(-dt / 4.0) * math.cos(math.pi * dt / 2)
            rattle += amp * impulse
            yaw += math.radians(1.6) * impulse
    if revision == 1:
        shift *= .69
        rattle *= .8
    phone.location = (-.016 + shift + rattle, -.010 + shift * .19, 0)
    phone.rotation_euler.z = math.radians((-27 if revision == 1 else -18) + 77 * shift) + yaw
    if revision >= 3:
        phone.location.y += rattle * .22
        phone.rotation_euler.z += math.radians(.35) * math.sin(hold*.31) * min(1, abs(rattle)*500)


def camera_pose(f):
    k = ease((f - 1) / 71)
    camera.location = (-.001 - .004*k, -.154 + .007*k, .291 - .011*k)
    center_x = -.017 + .014*k if revision >= 3 else -.004 + .006*k
    target = Vector((center_x, -.016 if revision >= 3 else (-.013 if revision == 2 else .016), .003))
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()


def project(point):
    uv = world_to_camera_view(sc, camera, Vector(point))
    return [float(uv.x), float(1 - uv.y)]


frames = range(1, 73) if frame_spec == 'all' else [int(f) for f in frame_spec.split(',')]
metadata = {}
for frame in frames:
    sc.frame_set(frame)
    camera_pose(frame)
    contact_pose(frame)
    bpy.context.view_layer.update()
    corners = [(-.26, .47, 0), (.26, .47, 0), (.26, -.23, 0), (-.26, -.23, 0)]
    footprint = [phone.matrix_world @ Vector(pt) for pt in loop(WID, LENGTH, RADIUS, 0)]
    metadata[frame] = {'floor': [project(v) for v in corners],
                       'footprint': [project(v) for v in footprint],
                       'phone': list(phone.location), 'yaw': phone.rotation_euler.z}
    sc.render.filepath = str(OUT / f'cel_{frame:03d}.png')
    bpy.ops.render.render(write_still=True)
(OUT / 'projection.json').write_text(json.dumps(metadata), encoding='utf-8')
