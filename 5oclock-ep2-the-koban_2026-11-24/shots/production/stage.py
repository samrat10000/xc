"""Shared EEVEE stage, approved cast loading, rig poses and practical props for Episode 2."""
from pathlib import Path
import math
import sys
import bpy

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
ASSETS=ROOT/'assets'
args=sys.argv[sys.argv.index('--')+1:]
SCALE=float(args[2])
OUT=Path(args[1]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
exec(compile((ROOT/'toonlib.py').read_text(encoding='utf-8-sig'),'toonlib.py','exec'))
sc.eevee.taa_render_samples=16
sc.render.fps=24
sc.render.image_settings.color_mode='RGBA'
sc.world.node_tree.nodes.get('Background').inputs[0].default_value=(.17,.13,.22,1)
sc.world.node_tree.nodes.get('Background').inputs[1].default_value=.12
SUNV=tuple(Vector((-.56,.62,.65)).normalized())

def clamp(x): return min(1,max(0,x))
def ease(x):
    x=clamp(x)
    return x*x*(3-2*x)
def interval(f,start,end): return ease((f-start)/(end-start))
def rgb(hexv):
    h=hexv.lstrip('#')
    return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def paint(n,sh,lit,rim=None,facing=.69):
    return toon(n,rgb(sh),rgb(lit),rgb(rim) if rim else None,rimfacing=facing)
def flat(n,h,luminance=1):
    colors=[k/12.92 if k<.04045 else ((k+.055)/1.055)**2.4 for k in rgb(h)]
    return emis(n,colors,luminance)

def mapped(name,path,sh=None,lit=None,flip=False):
    file=bpy.data.images.load(str(path),check_existing=True)
    if sh is None:
        mat=emis(name,(0,0,0))
        n=mat.node_tree.nodes
        l=mat.node_tree.links
        texture=n.new('ShaderNodeTexImage')
        texture.image=file
        l.new(texture.outputs['Color'],n.get('Emission').inputs[0])
        return mat,texture
    def color(nt,ramp):
        n,l=nt.nodes,nt.links
        texture=n.new('ShaderNodeTexImage')
        texture.image=file
        blend=n.new('ShaderNodeMixRGB')
        blend.blend_type='MULTIPLY'
        blend.inputs[0].default_value=1
        l.new(texture.outputs['Color'],blend.inputs[1])
        l.new(ramp.outputs[0],blend.inputs[2])
        return blend.outputs[0]
    return toon(name,rgb(sh),rgb(lit),tex=color)

def form(name,vertices,faces,mat,uvs=None):
    data=bpy.data.meshes.new(name)
    data.from_pydata(vertices,[],faces)
    data.update()
    if uvs is not None:
        mapping=data.uv_layers.new()
        for lp in data.loops:
            mapping.data[lp.index].uv=uvs[lp.vertex_index]
    obj=bpy.data.objects.new(name,data)
    sc.collection.objects.link(obj)
    if mat:
        data.materials.append(mat)
    return obj
def card(name,points,mat,mirror=False):
    uv=[(0,0),(1,0),(1,1),(0,1)]
    if mirror:
        uv=[(1-u,v) for u,v in uv]
    return form(name,points,[(0,1,2,3)],mat,uv)
def box(name,loc,size,mat,bevel=0):
    x,y,z=(dimension*.5 for dimension in size)
    v=[(-x,-y,-z),(x,-y,-z),(x,y,-z),(-x,y,-z),(-x,-y,z),(x,-y,z),(x,y,z),(-x,y,z)]
    faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    o=form(name,v,faces,mat)
    o.location=loc
    if bevel:
        m=o.modifiers.new('Round physical edges','BEVEL')
        m.width=bevel
        m.segments=3
    return o
def curve(name,points,r,mat):
    data=bpy.data.curves.new(name,'CURVE')
    data.dimensions='3D'
    data.bevel_depth=r
    data.bevel_resolution=2
    data.use_fill_caps=True
    s=data.splines.new('POLY')
    s.points.add(len(points)-1)
    for q,pos in zip(s.points,points):
        q.co=(*pos,1)
    o=bpy.data.objects.new(name,data)
    sc.collection.objects.link(o)
    o.data.materials.append(mat)
    return o
def curve_update(obj,points):
    for v,p in zip(obj.data.splines[0].points,points):
        v.co=(*p,1)
def cyl(name,loc,r,depth,mat,axis=(0,0,1),verts=28):
    points=[(r*math.cos(i*math.tau/verts),r*math.sin(i*math.tau/verts),z*depth*.5)
            for z in (-1,1) for i in range(verts)]
    faces=[tuple(reversed(range(verts))),tuple(range(verts,verts*2))]
    faces.extend((i,(i+1)%verts,(i+1)%verts+verts,i+verts) for i in range(verts))
    o=form(name,points,faces,mat)
    o.location=loc
    o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
    for f in o.data.polygons:
        f.use_smooth=len(f.vertices)==4
    return o
def connect_cyl(o,a,b):
    d=Vector(b)-Vector(a)
    o.location=(Vector(a)+Vector(b))*.5
    o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
    o.scale.z=d.length/o.data.vertices[0].co.z/2 if o.data.vertices[0].co.z>0 else d.length/(-2*o.data.vertices[0].co.z)
def pivot(name,loc):
    obj=empty(name)
    obj.location=loc
    return obj
def attach(obj,parent):
    bpy.context.view_layer.update()
    m=obj.matrix_world.copy()
    obj.parent=parent
    obj.matrix_world=m
def parent_all(objects,parent):
    for ob in objects: attach(ob,parent)
def camera(name='Shot camera'):
    d=bpy.data.cameras.new(name)
    d.sensor_fit,d.sensor_height='VERTICAL',36
    d.clip_start=.015
    o=bpy.data.objects.new(name,d)
    sc.collection.objects.link(o)
    sc.camera=o
    return o
cam=camera()
def look(location,aim,lens=42,roll=0):
    cam.data.lens=lens
    cam.location=location
    q=(Vector(aim)-Vector(location)).to_track_quat('-Z','Y')
    cam.rotation_euler=(q@Quaternion((0,0,1),roll)).to_euler()
def lamp(name,energy,color,direction):
    global SUNV
    data=bpy.data.lights.new(name,'SUN')
    data.energy,data.color,data.angle=energy,rgb(color),.067
    obj=bpy.data.objects.new(name,data)
    sc.collection.objects.link(obj)
    obj.rotation_euler=(-Vector(direction)).to_track_quat('-Z','Y').to_euler()
    return obj
def area(name,loc,aim,power,color,size=1):
    data=bpy.data.lights.new(name,'AREA')
    data.energy,data.color,data.size=power,rgb(color),size
    obj=bpy.data.objects.new(name,data)
    sc.collection.objects.link(obj)
    obj.location=loc
    obj.rotation_euler=(Vector(aim)-obj.location).to_track_quat('-Z','Y').to_euler()
    return obj

class Actor:
    def __init__(self,asset):
        if asset=='sam':
            filepath=ASSETS/'sam_toon.blend'
        elif asset=='mom':
            filepath=ASSETS/'mom.blend'
        else:
            filepath=ASSETS/'cast'/(asset+'.blend')
        with bpy.data.libraries.load(str(filepath),link=False) as (source,data):
            data.objects=list(source.objects)
        self.objects=[o for o in data.objects if o and o.type not in ('LIGHT','CAMERA')]
        for o in self.objects:
            sc.collection.objects.link(o)
            o.animation_data_clear()
            if o.type=='MESH' and o.data.shape_keys:
                o.data.shape_keys.animation_data_clear()
            if 'Headphone_Cable' in o.name:
                o.hide_render=True
        self.arm=next(o for o in self.objects if o.type=='ARMATURE')
        self.bones=self.arm.pose.bones
        self.arm.data.pose_position='POSE'
        for bone in self.bones:
            bone.rotation_mode='QUATERNION'
            for constraint in bone.constraints:
                if constraint.type=='IK':
                    constraint.influence=0
        self.cast_basis=None
        if asset not in ('sam','mom'):
            self.cast_basis={bone.name:bone.matrix_basis.copy() for bone in self.bones}
            if asset.startswith('kid'):
                for bone in self.arm.data.bones:
                    bone.inherit_scale='FIX_SHEAR'
        self.scale=self.arm.matrix_world.to_scale().x
        self.name=asset
        self.rest_scales={b.name:Vector(b.scale) for b in self.bones}
        self.blink_keys=[k for o in self.objects if o.type=='MESH' and o.data.shape_keys for k in o.data.shape_keys.key_blocks if k.name.endswith('Fcl_EYE_Close')]
        self.brow_keys=[k for o in self.objects if o.type=='MESH' and o.data.shape_keys for k in o.data.shape_keys.key_blocks if k.name.endswith('Fcl_BRW_Sorrow')]
        self.shown={o:o.hide_render for o in self.objects}
        for material in (m for o in self.objects if o.type in ('MESH','CURVE') for m in o.data.materials if m and m.node_tree):
            for node in material.node_tree.nodes:
                if node.type=='VECT_MATH' and node.operation=='DOT_PRODUCT' and not node.inputs[1].is_linked:
                    node.inputs[1].default_value=SUNV
    def visible(self,state):
        for o in self.objects:
            o.hide_render=(not state) or self.shown[o]
    def b(self,label,side='C'):
        return self.bones['J_Bip_'+side+'_'+label]
    def pose(self,loc,yaw,scale=1):
        self.arm.matrix_world=Matrix.Translation(Vector(loc))@Matrix.Rotation(yaw,4,'Z')@Matrix.Scale(self.scale*scale,4)
        for b in self.bones:
            b.rotation_mode='QUATERNION'
            if self.cast_basis is None:
                b.matrix_basis=Matrix.Diagonal((*self.rest_scales[b.name],1))
            else:
                b.matrix_basis=self.cast_basis[b.name]
        bpy.context.view_layer.update()
    def world(self,label,side='C',end=False):
        b=self.b(label,side)
        return self.arm.matrix_world@(b.tail if end else b.head)
    def primary(self,b,axis,angle):
        rotation=Quaternion(b.bone.matrix_local.to_quaternion().inverted()@Vector(axis),angle)
        if self.cast_basis is not None:
            rotation=self.cast_basis[b.name].to_quaternion()@rotation
        b.rotation_quaternion=rotation
        bpy.context.view_layer.update()
    def aim(self,b,goal):
        m=self.arm.matrix_world
        start=m@b.head
        d=m@b.tail-start
        if d.length<1e-8 or (Vector(goal)-start).length<1e-8:
            return
        delta=d.rotation_difference(Vector(goal)-start)
        local=(m@b.matrix).to_quaternion()
        b.rotation_quaternion=b.rotation_quaternion@(local.inverted()@delta@local)
        bpy.context.view_layer.update()
    def chain(self,a,b,target,pole):
        m=self.arm.matrix_world
        start=m@a.head
        target=Vector(target)
        ar=(m@a.tail-start).length
        br=(m@b.tail-m@b.head).length
        d=target-start
        n=d.normalized()
        distance=min(ar+br-.002,max(abs(ar-br)+.002,d.length))
        x=(distance**2+ar**2-br**2)/(2*distance)
        z=math.sqrt(max(.000001,ar**2-x**2))
        bend=Vector(pole)-n*Vector(pole).dot(n)
        if bend.length<1e-4:bend=Vector((0,0,1))
        self.aim(a,start+n*x+bend.normalized()*z)
        self.aim(b,start+n*distance)
        return (self.arm.matrix_world@b.tail-target).length
    def arms_free(self,spread=.048):
        axes=self.arm.matrix_world.to_3x3()
        for side,sign in (('L',1),('R',-1)):
            for label,v in (('UpperArm',(sign*spread,-.01,-.24)),('LowerArm',(sign*.018,-.041,-.21)),('Hand',(sign*.008,-.014,-.098))):
                self.aim(self.b(label,side),self.world(label,side)+axes@Vector(v))
    def reach(self,side,target,pole,point):
        e=self.chain(self.b('UpperArm',side),self.b('LowerArm',side),target,pole)
        self.aim(self.b('Hand',side),self.world('Hand',side)+Vector(point))
        return e
    def blink(self,f,centres=(37,72)):
        val=max((math.exp(-((f-c)/2.6)**2) for c in centres),default=0)
        for key in self.blink_keys: key.value=max(val,.28 if self.name=='grandma' else 0)
    def move_hair(self,f,amp=.012):
        for i,b in enumerate(b for b in self.bones if 'hair' in b.name.lower() and not b.name.endswith('_end')):
            axes=b.bone.matrix_local.to_quaternion().inverted()@Vector((0,1,0))
            b.rotation_quaternion=Quaternion(axes,amp*math.sin(f*.13+i*.31))
        bpy.context.view_layer.update()
    def attach_bone(self,obj,label='Head'):
        bpy.context.view_layer.update()
        m=obj.matrix_world.copy()
        obj.parent=self.arm
        obj.parent_type='BONE'
        obj.parent_bone=self.b(label).name
        bpy.context.view_layer.update()
        obj.matrix_world=m

# Device shape and case dimensions are identical to the first two shots.
def handset(screen_image,loc=(0,0,0),rotation=(0,0,0)):
    scene_helpers=globals().copy()
    stream=(PROJECT/'02_wrong_room'/'src'/'phone.py').read_text(encoding='utf-8-sig')
    before=set(sc.objects)
    exec(compile(stream,'phone.py','exec'),scene_helpers)
    mount=scene_helpers['phone']
    w=scene_helpers['WID']-.0062
    h=scene_helpers['LENGTH']-.0068
    points=scene_helpers['loop'](w,h,scene_helpers['RADIUS']-.0031,.00877)
    mat,tex=mapped('Phone glass image',screen_image)
    obj=form('Display behind bezel',points,[tuple(range(len(points)))],mat,[(x/w+.5,y/h+.5) for x,y,z in points])
    obj.parent=mount
    mount.location=loc
    mount.rotation_euler=rotation
    return mount,tex,[o for o in sc.objects if o not in before]

def render(path,camera=None):
    sc.camera=camera or cam
    sc.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)

