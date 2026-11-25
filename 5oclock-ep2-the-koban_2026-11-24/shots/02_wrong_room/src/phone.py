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
for center, length in ((.040, .013), (.022, .012)):
    inset('Volume switch', (.0015, length, .0019), (-WID/2, center, .0052), detail, .00055)
inset('Sleep button', (.0015, .014, .0020), (WID/2, .030, .0052), detail, .00055)
inset('USB-C recess', (.0080, .00040, .00265), (0, -LENGTH/2-.00005, .0045), port, .0002)
for i in (-3, -2, -1, 1, 2, 3):
    inset('Grille aperture', (.00105, .00036, .00103),
          (math.copysign(.0069, i) + i*.0021, -LENGTH/2-.00007, .0046), port, .00015)


