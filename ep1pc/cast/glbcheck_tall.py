import sys,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import bpy, castlib as L
sc=L.reset(); bpy.ops.import_scene.gltf(filepath=sys.argv[1])
ms=[o for o in bpy.data.objects if o.type=='MESH']
print('meshes',len(ms),'tris',sum(len(o.data.polygons) for o in ms))
for o in ms:
    for m in o.data.materials:
        if m and m.name.startswith('Ink'):
            o.visible_shadow=False; o.visible_diffuse=False; o.visible_glossy=False
            nt=m.node_tree; nt.nodes.clear(); out=nt.nodes.new('ShaderNodeOutputMaterial'); e=nt.nodes.new('ShaderNodeEmission'); e.inputs[0].default_value=(0,0,0,1)
            tr=nt.nodes.new('ShaderNodeBsdfTransparent'); mx=nt.nodes.new('ShaderNodeMixShader'); g=nt.nodes.new('ShaderNodeNewGeometry')
            nt.links.new(g.outputs['Backfacing'],mx.inputs[0]); nt.links.new(e.outputs[0],mx.inputs[1]); nt.links.new(tr.outputs[0],mx.inputs[2]); nt.links.new(mx.outputs[0],out.inputs[0])
L.studio(sc); sc.view_settings.exposure=-.45
L.camera(sc,(0,-.12,1.35),5.0,32,8,lens=45); L.render(sc,sys.argv[2],540,675,16)
