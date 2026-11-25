import bpy
bpy.ops.wm.open_mainfile(filepath='/home/user/w/out/shots/l2.blend')
sc = bpy.context.scene
sc.world.node_tree.links.clear() if False else None
wo = sc.world.node_tree.nodes['World Output']
for l in list(sc.world.node_tree.links):
    if l.to_socket == wo.inputs['Volume']: sc.world.node_tree.links.remove(l)
vl = sc.view_layers[0]; vl.use_pass_mist = True
ms = sc.world.mist_settings; ms.start = 4; ms.depth = 90; ms.falloff = 'QUADRATIC'
t = bpy.data.node_groups.new('comp', 'CompositorNodeTree'); sc.compositing_node_group = t
n = t.nodes; rl = n.new('CompositorNodeRLayers')
t.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
go = n.new('NodeGroupOutput')
mx = n.new('ShaderNodeMix'); mx.data_type = 'RGBA'
print([s.name for s in mx.inputs])
t.links.new(rl.outputs['Mist'], mx.inputs[0]); t.links.new(rl.outputs['Image'], mx.inputs[6]); mx.inputs[7].default_value = (.05, .06, .08, 1)
t.links.new(mx.outputs[2], go.inputs[0])
sc.frame_set(30); sc.render.filepath = '/home/user/w/out/shots/comp.png'; bpy.ops.render.render(write_still=True)
