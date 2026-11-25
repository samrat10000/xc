import bpy,sys,math,os,json
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:]
src,out=args[0],args[1]
if src.endswith('.blend'): bpy.ops.wm.open_mainfile(filepath=src)
else:
    bpy.ops.wm.read_factory_settings(use_empty=True); bpy.ops.import_scene.gltf(filepath=src)
sc=bpy.context.scene
hide=[h for h in os.environ.get('HIDE','').split(',') if h]
for o in list(sc.objects):
    if any(h in o.name for h in hide):
        o.hide_render=True
        for c in o.children_recursive: c.hide_render=True
for o in sc.objects:
    if o.type=='MESH' and (o.name.endswith(' hull') or 'ink lines' in o.name):
        o.visible_shadow=False; o.visible_diffuse=False; o.visible_glossy=False; o.visible_transmission=False
hm=bpy.data.materials.get('Ink_Outline_Hull')
if hm:
    nt=hm.node_tree; b=nt.nodes['Principled BSDF']; mo=nt.nodes['Material Output']
    g=nt.nodes.new('ShaderNodeNewGeometry'); tr=nt.nodes.new('ShaderNodeBsdfTransparent'); mx=nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(g.outputs['Backfacing'],mx.inputs[0]); nt.links.new(b.outputs[0],mx.inputs[1]); nt.links.new(tr.outputs[0],mx.inputs[2]); nt.links.new(mx.outputs[0],mo.inputs[0])
W,H=[int(x) for x in os.environ.get('RES','800x800').split('x')]
sc.render.engine='CYCLES'; sc.cycles.samples=int(os.environ.get('S','16')); sc.cycles.use_denoising=True
sc.render.resolution_x=W; sc.render.resolution_y=H; sc.cycles.max_bounces=6
sc.view_settings.view_transform='Standard'; sc.view_settings.look='None'
w=bpy.data.worlds.new('w'); sc.world=w; w.use_nodes=True; nt=w.node_tree
bg=nt.nodes['Background']; bg.inputs[0].default_value=(.62,.63,.62,1); bg.inputs[1].default_value=.75
lp=nt.nodes.new('ShaderNodeLightPath'); bg2=nt.nodes.new('ShaderNodeBackground'); bg2.inputs[0].default_value=(*[float(x) for x in os.environ.get('BG','0.80,0.80,0.78').split(',')],1)
mx=nt.nodes.new('ShaderNodeMixShader'); nt.links.new(lp.outputs['Is Camera Ray'],mx.inputs[0]); nt.links.new(bg.outputs[0],mx.inputs[1]); nt.links.new(bg2.outputs[0],mx.inputs[2])
nt.links.new(mx.outputs[0],nt.nodes['World Output'].inputs[0])
def light(name,loc,energy,size,col=(1,1,1)):
    L=bpy.data.lights.new(name,'AREA'); L.energy=energy; L.size=size; L.color=col
    o=bpy.data.objects.new(name,L); sc.collection.objects.link(o); o.location=loc
    o.rotation_euler=(Vector((0,0,.8))-Vector(loc)).to_track_quat('-Z','Y').to_euler()
light('key',(-4,-5,6),2600,4,(1,.96,.9)); light('fill',(5,3,3),900,5,(.85,.9,1)); light('rim',(3,-1,5),900,3)
if os.environ.get('FLOOR','1')=='1':
    me=bpy.data.meshes.new('floor'); import bmesh; bm=bmesh.new(); bmesh.ops.create_grid(bm,x_segments=1,y_segments=1,size=30); bm.to_mesh(me)
    fo=bpy.data.objects.new('floor',me); sc.collection.objects.link(fo)
    m=bpy.data.materials.new('floor'); m.use_nodes=True; n=m.node_tree; b=n.nodes['Principled BSDF']
    nz=n.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=3; ramp=n.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(.42,.41,.39,1); ramp.color_ramp.elements[1].color=(.58,.57,.54,1)
    n.links.new(nz.outputs[0],ramp.inputs[0]); n.links.new(ramp.outputs[0],b.inputs['Base Color']); b.inputs['Roughness'].default_value=.9
    me.materials.append(m)
cam=bpy.data.objects.new('cam',bpy.data.cameras.new('cam')); sc.collection.objects.link(cam); sc.camera=cam
for i,v in enumerate(json.loads(os.environ['V'])):
    tx,ty,tz,az,el,d=v[:6]; cam.data.lens=v[6] if len(v)>6 else 50
    a=math.radians(az);e=math.radians(el); t=Vector((tx,ty,tz))
    cam.location=t+Vector((math.cos(a)*math.cos(e),math.sin(a)*math.cos(e),math.sin(e)))*d
    cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler()
    sc.render.filepath=f'{out}_{i}.png'; bpy.ops.render.render(write_still=True)
