import ast, os
D = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(D, 'build_s05.py'); t = open(p, encoding='utf-8').read()
old_plant = t[t.index('def lowest_z(objs):'):t.index('def R(rig, bone, axis, deg):')]
new_plant = '''def lowest_z(objs, report=False):
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get(); best = (1e9, '')
    for o in objs:
        if o.type != 'MESH' or o.hide_render or 'randoseru' in o.name or 'Outline' in o.name: continue
        ev = o.evaluated_get(dg); me = ev.to_mesh(); mw = o.matrix_world
        zs = [(mw @ v.co).z for i, v in enumerate(me.vertices) if i % 5 == 0]; ev.to_mesh_clear()
        if zs and min(zs) < best[0]: best = (min(zs), o.name)
    if report: print('LOWEST', best)
    return best[0]


def plant(rig, objs, x, y):                                                  # feet locked to the road (R3): ABSOLUTE, never cumulative
    gz = (ROAD.matrix_world @ Vector((x, y, 0.0))).z
    rig.location.z = 0.0
    low = lowest_z(objs, bool(os.environ.get('DBG')))
    rig.location.z = (ROAD.matrix_world.inverted() @ Vector((0, 0, gz - low + (ROAD.matrix_world @ Vector((x, y, 0))).z))).z * 0 + (gz - low)


'''
t = t.replace(old_plant, new_plant)
dbg = t[t.index("            if os.environ.get('DBG'): print('DBG'"):]
dbg = dbg[:dbg.index('\n') + 1]
t = t.replace(dbg, "            if os.environ.get('DBG'): print('DBG', fp, rig.name, round(rig.location.z, 3))\n")
ast.parse(t); open(p, 'w', encoding='utf-8').write(t); print('patched')
