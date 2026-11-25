import bpy, numpy as np
def npz_mesh(path, name, mat=None):
    d = np.load(path); v = d['verts']; f = d['faces']; c = d['cols']
    me = bpy.data.meshes.new(name)
    me.vertices.add(len(v)); me.vertices.foreach_set('co', v.ravel())
    me.loops.add(f.size); me.loops.foreach_set('vertex_index', f.ravel())
    me.polygons.add(len(f)); me.polygons.foreach_set('loop_start', np.arange(0, f.size, 3)); me.polygons.foreach_set('loop_total', np.full(len(f), 3))
    me.update(); me.validate()
    # marching cubes winding: flip if needed (normals inward)
    me.flip_normals()
    ca = me.color_attributes.new('Col', 'FLOAT_COLOR', 'POINT')
    rgba = np.concatenate([c, np.ones((len(c), 1), np.float32)], 1)
    ca.data.foreach_set('color', rgba.ravel())
    o = bpy.data.objects.new(name, me)
    me.shade_smooth() if hasattr(me, 'shade_smooth') else None
    return o
