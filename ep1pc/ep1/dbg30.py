import os
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots2.py')).read()
src = src.replace("render(f0, f1)\n", """
for f in (1, 68):
    sc.frame_set(f)
    for n in ('exit pivot', 'EXIT door', 'door PH-C', 'tvlight'):
        o = bpy.data.objects.get(n); print(f, n, o and tuple(round(x, 2) for x in o.matrix_world.translation), o and tuple(round(x, 2) for x in o.matrix_world.to_euler()), o and o.parent and o.parent.name)
raise SystemExit
""")
__file__ = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shots2.py')
exec(compile(src, __file__, 'exec'))
