"""Shot 02. EEVEE cels for the washitsu, the original Sam rig, and a planar phone reflection."""
import json, math, sys
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Quaternion, Vector

HERE=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:]
OUT=Path(args[0]).resolve()
OUT.mkdir(parents=True,exist_ok=True)
SCALE=float(args[1])
frames=range(1,97) if args[2]=='all' else [int(x) for x in args[2].split(',')]
revision=int(args[3])
rig_path=Path(args[4]) if len(args)>4 else HERE.parents[2]/'toon3d'/'sam_toon_003.blend'
exec(compile((HERE/'toonlib.py').read_text(encoding='utf-8-sig'),'toonlib.py','exec'))
sc.eevee.taa_render_samples=16
sc.render.fps=24
sc.frame_end=96
SUNV=tuple(Vector((.73,.64,.36)).normalized())
REFLECT_AT=73

def ease(f,a,b):
    x=max(0,min(1,(f-a)/(b-a)))
    return x*x*(3-2*x)

def color(hexval):
    return tuple(int(hexval[i:i+2],16)/255 for i in (0,2,4))

def paint(name, shadow, lit):
    return toon(name,color(shadow),color(lit))

def texture(name, filename, shadow, lit):
    def layer(nt,ramp):
        n,l=nt.nodes,nt.links
        image=n.new('ShaderNodeTexImage')
        image.image=bpy.data.images.load(str(HERE/(filename+'.png')),check_existing=True)
        node=n.new('ShaderNodeMixRGB')
        node.blend_type='MULTIPLY'
        node.inputs[0].default_value=1
        l.new(image.outputs['Color'],node.inputs[1])
        l.new(ramp.outputs[0],node.inputs[2])
        return node.outputs[0]
    return toon(name,color(shadow),color(lit),tex=layer)

floor_mat=texture('Woven rush floor','igusa','a4a1bf','fff5d3')
wall_mat=texture('Hand-painted plaster','plaster','a4a2bb','fff6e2')
if revision>=3:
    nt=floor_mat.node_tree
    N,L=nt.nodes,nt.links
    emission=next(n for n in N if n.type=='EMISSION')
    old=emission.inputs[0].links[0].from_socket
    pos=N.new('ShaderNodeNewGeometry')
    dot=N.new('ShaderNodeVectorMath')
    dot.operation='DOT_PRODUCT'
    dot.inputs[1].default_value=(.9,-.46,0)
    L.new(pos.outputs['Position'],dot.inputs[0])
    band=N.new('ShaderNodeMapRange')
    band.clamp=True
    band.interpolation_type='SMOOTHERSTEP'
    band.inputs[1].default_value=.18
    band.inputs[2].default_value=.36
    L.new(dot.outputs['Value'],band.inputs[0])
    warmth=N.new('ShaderNodeMixRGB')
    warmth.blend_type='ADD'
    warmth.inputs[2].default_value=(.105,.060,.018,1)
    L.new(band.outputs['Result'],warmth.inputs[0])
    L.new(old,warmth.inputs[1])
    L.new(warmth.outputs[0],emission.inputs[0])

cloth_mat=texture('Quilted indigo cotton','quilt','8d8aa2','c9c4c9')
pillow_mat=paint('Futon slate pillow','53526b','8d8b99')
wood=paint('Stained wood','45343d','9c7250')
trim=paint('Recessed timber','332935','725549')
edge=paint('Indigo heri','2c293e','51464d')
stitch=paint('Warm thread','7a6c70','baaa8c')
sheet=paint('Futon piping','82777f','c6b6ae')
poster=texture('Reversed poster','mirrored_poster','b4a5b2','fff9db')
washi=emis('Glowing washi',(.83,.67,.39),1.22)
washi_low=emis('Soft bottom washi',(.70,.52,.31),1)
glass_mat=emis('Dark sleeping glass',(.012,.011,.019))
sensor=emis('Inlaid earpiece and front sensor',(.004,.004,.009))

env=[]
def mesh(name,vertices,faces,mat,uvs=None):
    me=bpy.data.meshes.new(name)
    me.from_pydata(vertices,[],faces)
    if uvs:
        uv=me.uv_layers.new()
        for loop in me.loops:
            uv.data[loop.index].uv=uvs[loop.vertex_index]
    ob=bpy.data.objects.new(name,me)
    sc.collection.objects.link(ob)
    me.materials.append(mat)
    return ob

def quad(name,points,m):
    return mesh(name,points,[(0,1,2,3)],m,[(0,0),(1,0),(1,1),(0,1)])

def box(name,loc,size,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object
    o.name=name
    o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(mat)
    if bevel:
        b=o.modifiers.new('Soft joinery','BEVEL')
        b.width,b.segments=bevel,3
    return o

def line(name,points,m,radius):
    cu=bpy.data.curves.new(name,'CURVE')
    cu.dimensions='3D'
    cu.bevel_depth,cu.bevel_resolution=radius,2
    spl=cu.splines.new('POLY')
    spl.points.add(len(points)-1)
    for point,xyz in zip(spl.points,points):
        point.co=(*xyz,1)
    obj=bpy.data.objects.new(name,cu)
    sc.collection.objects.link(obj)
    obj.data.materials.append(m)
    return obj

def quilt(name,cx,cy,z,sx,sy,h,m,seed):
    verts,uvs=[],[]
    nx,ny=34,45
    for j in range(ny+1):
        for i in range(nx+1):
            u,v=i/nx,j/ny
            shape=(max(0,math.sin(math.pi*u)*math.sin(math.pi*v)))**.30
            wrinkle=(.070*math.sin(u*28+v*7+seed)+.05*math.cos(v*27+u*9))*shape
            x=cx+sx*(u-.5)+.016*math.sin(v*7+seed)
            y=cy+sy*(v-.5)+.024*math.cos(u*8+seed)
            verts.append((x,y,z+h*(shape+wrinkle)))
            uvs.append((u,v))
    faces=[]
    for j in range(ny):
        for i in range(nx):
            q=j*(nx+1)+i
            faces.append((q,q+1,q+nx+2,q+nx+1))
    ob=mesh(name,verts,faces,m,uvs)
    for poly in ob.data.polygons:
        poly.use_smooth=True
    solid=ob.modifiers.new('Stuffed hem','SOLIDIFY')
    solid.thickness=.022
    border=verts[:nx+1]+[verts[j*(nx+1)+nx] for j in range(1,ny+1)]+list(reversed(verts[ny*(nx+1):ny*(nx+1)+nx]))+[verts[j*(nx+1)] for j in range(ny-1,-1,-1)]
    line(name+' piping',[(x,y,zz+.004) for x,y,zz in border],sheet,.003)
    return ob

for ix in range(4):
    x=-1.75+ix*.91
    for jy in range(3):
        y=-3.15+jy*1.73
        quad('Igusa panel',[(x,y,0),(x+.9,y,0),(x+.9,y+1.72,0),(x,y+1.72,0)],floor_mat)
    box('Bound heri seam',(x, -.82,.0008),(.031,4.73,.002),edge)
    for sx in (-.011,.011):
        line('Stitched heri',[(x+sx,-3.2,.002),(x+sx,1.53,.002)],stitch,.00055)

def wall(name,x0,x1,z0,z1,y=1.13,mat=wall_mat):
    return quad(name,[(x0,y,z0),(x1,y,z0),(x1,y,z1),(x0,y,z1)],mat)

window=(-.20,1.19,.36,1.65)
xl,xr,zb,zt=window
wall('Poster wall',-2.4,xl,0,2.8)
wall('Right pier',xr,2.4,0,2.8)
wall('Below shoji',xl,xr,0,zb)
wall('Above shoji',xl,xr,zt,2.8)
wall('Bright paper underlay',xl,xr,zb,zt,1.165,washi)
# Paper admits the key but the wood casts the shoji shadows.
paper_obj=bpy.data.objects['Bright paper underlay']
node=paper_obj.data.materials[0].node_tree
out=node.nodes.get('Material Output')
em=node.nodes.get('Emission')
geo=node.nodes.new('ShaderNodeLightPath')
trans=node.nodes.new('ShaderNodeBsdfTransparent')
mix=node.nodes.new('ShaderNodeMixShader')
node.links.new(geo.outputs['Is Shadow Ray'],mix.inputs[0])
paper_tex=node.nodes.new('ShaderNodeTexImage')
paper_tex.image=bpy.data.images.load(str(HERE/'washi.png'),check_existing=True)
tint=node.nodes.new('ShaderNodeMixRGB')
tint.blend_type='MULTIPLY'
tint.inputs[0].default_value=.75
tint.inputs[1].default_value=em.inputs[0].default_value
node.links.new(paper_tex.outputs['Color'],tint.inputs[2])
node.links.new(tint.outputs[0],em.inputs[0])
node.links.new(em.outputs[0],mix.inputs[1])
node.links.new(trans.outputs[0],mix.inputs[2])
node.links.new(mix.outputs[0],out.inputs[0])
for i in range(9):
    x=xl+(xr-xl)*i/8
    box('Shoji cedar upright',(x,1.134,(zb+zt)*.5),(.021 if i%4 else .036,.039,zt-zb+.06),wood,.002)
for j in range(7):
    z=zb+(zt-zb)*j/6
    box('Shoji cedar rail',((xl+xr)*.5,1.126,z),(xr-xl+.035,.043,.018 if j not in (0,6) else .033),wood,.002)
box('Window sill',((xl+xr)*.5,1.075,zb-.025),(xr-xl+.15,.177,.035),wood,.005)
box('Kick trim',(-.01,1.099,.072),(4.75,.069,.110),trim,.004)
box('Corner upright',(-1.37,1.08,1.22),(.065,.11,2.44),trim,.005)
box('Poster backing',(-.56,1.111,.96),(.49,.025,.68),trim,.003)
wall('Mirrored Kiriyama print',-.789,-.332,.640,1.283,1.096,poster)
for x,z in ((-.785,1.258),(-.334,1.252),(-.779,.668)):
    box('Poster tape',(x,1.09,z),(.045,.006,.028),sheet,.002)
box('Low book rack',(-1.04,1.015,.183),(.54,.21,.365),wood,.013)
if revision>=3:
    box('Cedar drawer front',(-1.04,.904,.181),(.481,.016,.212),trim,.006)
    box('Recess pull',(-1.03,.892,.182),(.098,.011,.019),edge,.003)
for i,tone in enumerate(('594251','745853','874e43','535064','977c60','685f77','6f504d')):
    h=.109+(i%4)*.027
    box('Used book spine',(-1.24+i*.055,.896,.38+h*.5),(.045,.14,h),paint('Book '+str(i),'463946',tone),.003)
box('Portable radio',(-.85,.925,.434),(.218,.123,.093),trim,.006)
for i in range(6):
    box('Speaker grill',(-.918+i*.012,.861,.422),(.006,.003,.037),edge,.001)

quilt('Cotton futon mattress',-.36,-.54,.030,.94,1.83,.058,cloth_mat,1)
if revision==1:
    quilt('Folded cover',-.35,-.73,.075,.94,1.49,.273,cloth_mat,2)
else:
    quilt('Folded bedding aside',-.66,-.77,.056,.42,1.45,.126,cloth_mat,2)
    quilt('Support roll by hand',.050,.360,.052,.38,.265,.104 if revision>=3 else .084,pillow_mat,9)
quilt('Creased pillow',-.39,.78,.033,.57,.41,.128,pillow_mat,4)
for ix in range(4):
    box('Floorboard at back',(-1.4+ix*.32,1.012,.023),(.318,.201,.045),wood,.003)

# Use the same model and dimensions as Alarm. Disk artwork is absent on sleeping glass.
exec(compile((HERE/'phone.py').read_text(encoding='utf-8-sig'),'phone.py','exec'))
sw,sh,sr=WID-.0062,LENGTH-.0068,RADIUS-.0031
screen_points=loop(sw,sh,sr,.00877)
screen=mesh('Sleeping screen',screen_points,[tuple(range(len(screen_points)))],glass_mat)
screen.parent=phone
inset('Front sensor',(.013,.0025,.00026),(0,.059,.00887),sensor,.00010)
phone.location=(.22,-.48,.022) if revision==1 else ((.16,-.568,.0003) if revision>=3 else (.20,-.48,.0010))
phone.rotation_euler=(0,0,-.25)

env=list(sc.objects)
with bpy.data.libraries.load(str(rig_path),link=False) as (data,rig):
    rig.objects=list(data.objects)
for obj in rig.objects:
    if obj and obj.type not in {'CAMERA','LIGHT'}:
        sc.collection.objects.link(obj)
sam=[obj for obj in rig.objects if obj and obj.type not in {'CAMERA','LIGHT'}]
arm=bpy.data.objects['Sam_Rig']
arm.animation_data_clear()
arm.data.pose_position='POSE'
bones=arm.pose.bones
char_mesh=[obj for obj in sam if obj.type in {'MESH','CURVE'}]
for obj in char_mesh:
    if obj.data.animation_data:
        obj.data.animation_data_clear()
    if obj.name=='Headphone_Cable':
        obj.hide_render=True
for obj in bpy.data.objects:
    if obj.type=='MESH' and obj.data.shape_keys:
        obj.data.shape_keys.animation_data_clear()

root=bones['J_Bip_C_Hips'].bone.head_local.copy()
shapes=[o.data.shape_keys.key_blocks for o in char_mesh if o.type=='MESH' and o.data.shape_keys]
blink_keys=[b for blocks in shapes for b in blocks if b.name.endswith('Fcl_EYE_Close')]
brow_keys=[b for blocks in shapes for b in blocks if b.name.endswith('Fcl_BRW_Surprised')]
hair_bones=[b for b in bones if 'hair' in b.name.lower() and not b.name.endswith('_end')]
head_base=Vector((0,-.080,.093))
def world_head():
    b=bones['J_Bip_C_Head']
    # Eye landmark relative to the head joint, in armature-rest axes.
    v=b.bone.matrix_local.to_quaternion().inverted() @ head_base
    return arm.matrix_world @ (b.matrix @ v)

def reset(b):
    b.rotation_mode='QUATERNION'
    b.rotation_quaternion=Quaternion()
    b.location=(0,0,0)
    b.scale=(1,1,1)
for b in bones:
    reset(b)

def aim(b, target):
    m=arm.matrix_world
    start=m@b.head
    current=m@b.tail-start
    if current.length<1e-6:
        return
    world_delta=current.rotation_difference(target-start)
    q=(m@b.matrix).to_quaternion()
    b.rotation_quaternion=b.rotation_quaternion@(q.inverted()@world_delta@q)
    bpy.context.view_layer.update()

def roll_palm(hand, side, desired_normal):
    prefix='J_Bip_'+side+'_'
    m=arm.matrix_world
    wrist=m@hand.head
    middle=m@bones[prefix+'Middle1'].head
    spread=(m@bones[prefix+'Index1'].head)-(m@bones[prefix+'Little1'].head)
    axis=(middle-wrist).normalized()
    palm=axis.cross(spread).normalized()*(1 if side=='L' else -1)
    goal=(desired_normal-axis*desired_normal.dot(axis)).normalized()
    angle=math.atan2(axis.dot(palm.cross(goal)),palm.dot(goal))
    local=(m@hand.matrix).to_quaternion().inverted()@axis
    hand.rotation_quaternion=hand.rotation_quaternion@Quaternion(local,angle)
    bpy.context.view_layer.update()

def orient_rest(b, global_axis, amount):
    b.rotation_quaternion=Quaternion(b.bone.matrix_local.to_quaternion().inverted()@Vector(global_axis),amount)

def solve_chain(upper,lower,target,pole):
    base=arm.matrix_world@upper.head
    length_a,length_b=upper.bone.length,lower.bone.length
    direction=target-base
    d=max(abs(length_a-length_b)+.003,min(direction.length,length_a+length_b-.004))
    direction.normalize()
    along=(d*d+length_a*length_a-length_b*length_b)/(2*d)
    orth=pole-direction*pole.dot(direction)
    middle=base+direction*along+orth.normalized()*math.sqrt(max(0,length_a*length_a-along*along))
    aim(upper,middle)
    aim(lower,base+direction*d)
    return (arm.matrix_world@lower.tail-target).length

def pose(frame):
    f=frame-(frame-1)%2
    q=ease(f,10,64)
    drift=.009*math.sin(f*.09)
    lean=math.radians(-75+39*q+2*math.sin(f*.11)*q)
    if revision>=2:
        lean+=math.radians(5*q+13*ease(f,65,95))
    yaw=math.radians(-11+24*ease(f,32,63)-13*ease(f,63,80))
    tilt=math.radians((14 if revision>=3 else 9)-15*q)
    R=Matrix.Rotation(yaw,4,'Z')@Matrix.Rotation(tilt,4,'Y')@Matrix.Rotation(lean,4,'X')
    hip=Vector((-.28+.072*q,.08+.045*q,.121+.097*q+drift-.033*ease(f,65,95)))
    arm.matrix_world=Matrix.Translation(hip)@R@Matrix.Translation(-root)
    for name in ('Spine','Chest','UpperChest','Neck','Head'):
        reset(bones['J_Bip_C_'+name])
    glance=ease(f,51,65)-ease(f,65,81)
    orient_rest(bones['J_Bip_C_Neck'],(0,0,1),math.radians(17*glance))
    orient_rest(bones['J_Bip_C_Head'],(1,0,0),math.radians(3+8*q+(12 if revision==1 else (47 if revision>=3 else 32))*ease(f,56,83)))
    for side in ('L','R'):
        for suffix in ('UpperLeg','LowerLeg','Foot','UpperArm','LowerArm','Hand'):
            reset(bones['J_Bip_'+side+'_'+suffix])
    for i,b in enumerate(hair_bones):
        orient_rest(b,(0,1,0),.019*math.sin(f*.17+i*.35)*ease(f,10,26))
    bpy.context.view_layer.update()
    leg_targets=((-.079,-.742,.126),(-.46,-.749,.125)) if revision==1 else ((-.032,-.997,.102),(-.49,-1.001,.106)) if revision>=3 else ((-.045,-.863,.109),(-.49,-.906,.108))
    for i,side in enumerate(('L','R')):
        thigh,shin,foot=[bones['J_Bip_'+side+'_'+n] for n in ('UpperLeg','LowerLeg','Foot')]
        solve_chain(thigh,shin,Vector(leg_targets[i]),Vector((.17 if i==0 else -.28,-.08,1)))
        aim(foot,arm.matrix_world@foot.head+Vector((0,-.15,-.068)))
    left=Vector((.075+.035*q,.413-.10*q,.034))
    right=Vector((-.405+.096*q,-.096+.048*q,.193+.135*q))
    if revision>=2:
        left=Vector((.105,.392,.143))
        right=Vector((-.443+.134*q,.110-.158*q,.175+.105*q))
    if revision>=3:
        left=Vector((.059,.363,.172))
        rest=ease(f,44,67)
        right=Vector((-.425+.057*q,.147-.153*q-.035*rest,.149+.236*q-.092*rest))
    errors=[]
    for side,palm,pole in (('L',left,Vector((.67,.28,-.36))),('R',right,Vector((-.8,.16,-.28)))):
        upper,lower,hand=[bones['J_Bip_'+side+'_'+n] for n in ('UpperArm','LowerArm','Hand')]
        errors.append(solve_chain(upper,lower,palm,pole))
        forward=Vector((-.09,-.11,-.006)) if side=='L' else Vector((.08,-.14,-.02))
        if revision>=3:
            forward=Vector((-.11,-.18,-.024)) if side=='L' else Vector((.046,-.17,.03*q-.03))
        aim(hand,arm.matrix_world@hand.head+forward)
        if revision>=3:
            roll_palm(hand,side,Vector((0,0,-1)) if side=='L' else Vector((.12,.23,-.95)))
    close=1-ease(f,9,22)
    close=max(close,.96*math.exp(-((f-48)/2.1)**2),.96*math.exp(-((f-82)/1.7)**2))
    for key in blink_keys:
        key.value=close
    for key in brow_keys:
        key.value=.36*ease(f,63,80)
    bpy.context.view_layer.update()
    return errors

def camera(name,lens):
    data=bpy.data.cameras.new(name)
    data.lens,data.sensor_fit,data.sensor_height=lens,'VERTICAL',36
    data.clip_start=.025
    obj=bpy.data.objects.new(name,data)
    sc.collection.objects.link(obj)
    return obj

maincam=camera('Floor-level push',45)
phonecam=camera('Phone insert',48 if revision==1 else (60 if revision>=3 else 75))
mirrorcam=camera('Reflected phone optics',48)

def look(cam,pos,target):
    cam.location=pos
    cam.rotation_euler=(Vector(target)-Vector(pos)).to_track_quat('-Z','Y').to_euler()

def lamp(name,power,tint,direction):
    d=bpy.data.lights.new(name,'SUN')
    d.energy,d.color,d.angle=power,tint,.055
    ob=bpy.data.objects.new(name,d)
    sc.collection.objects.link(ob)
    ob.rotation_euler=(-Vector(direction)).to_track_quat('-Z','Y').to_euler()
    return ob

key=lamp('Dawn from off-frame right',3.9,(1,.84,.69),SUNV)
fill=lamp('Cool reflected dawn',.32,(.68,.75,1),(-.31,-.70,.65))
lantern_data=bpy.data.lights.new('Soft wash through paper','AREA')
lantern_data.energy,lantern_data.shape,lantern_data.size=60,'DISK',.75
lantern_data.color=(1,.81,.60)
lantern=bpy.data.objects.new('Soft wash through paper',lantern_data)
sc.collection.objects.link(lantern)
lantern.location=(.74,.87,1.15)
lantern.rotation_euler=(Vector((-.24,-.22,.31))-lantern.location).to_track_quat('-Z','Y').to_euler()
for mat in bpy.data.materials:
    if mat.name.startswith('Sam_') and mat.node_tree:
        for n in mat.node_tree.nodes:
            if n.type=='VECT_MATH' and n.operation=='DOT_PRODUCT' and not n.inputs[1].is_linked:
                n.inputs[1].default_value=SUNV

pose(91)
phone_eye=world_head()
insert=(.325,-.744,.267)
normal=((Vector(insert)-phone.location).normalized()+(phone_eye-phone.location).normalized()).normalized()
# Seat the physical handset on a folded fabric ridge so its underside has support.
top=Vector((-.13,.96,0))
top=(top-normal*top.dot(normal)).normalized()
right=top.cross(normal).normalized()
if revision==1:
    phone.rotation_euler=Matrix((right,top,normal)).transposed().to_euler()
    base_delta=min((phone.rotation_euler.to_matrix()@Vector(p)).z for p in loop(WID,LENGTH,RADIUS,0))
    phone.location.z=.008-base_delta
    quilt('Cloth edge supporting phone',.252,-.435,.010,.30,.163,.026,cloth_mat,8)
    env.extend(o for o in sc.objects if o.name.startswith('Cloth edge'))
else:
    normal=Vector((0,0,1))
    optical_axis=phone_eye-phone.location
    optical_axis.z=-optical_axis.z
    insert=phone.location-optical_axis.normalized()*.41

def reflected(cam, plane, n):
    pos=cam.location
    def vector(v):
        return v-2*n*n.dot(v)
    b=cam.rotation_euler.to_matrix()
    mirrorcam.location=plane+vector(pos-plane)
    forward=vector(b@Vector((0,0,-1)))
    up=vector(b@Vector((0,1,0)))
    right=forward.cross(up).normalized()
    mirrorcam.rotation_euler=Matrix((right,up,-forward)).transposed().to_euler()

def project(cam,obj,p):
    uv=world_to_camera_view(sc,cam,obj.matrix_world@Vector(p))
    return [uv.x,1-uv.y]

def render(name, frame, cam):
    sc.camera=cam
    sc.render.filepath=str(OUT/f'{name}_{frame:03d}.png')
    bpy.ops.render.render(write_still=True)

main_out={}
for f in frames:
    sc.frame_set(f)
    errors=pose(f)
    k=ease(f,1,REFLECT_AT)
    if revision==1:
        start,end=(.83,-1.96,1.06),(.76,-1.80,1.00)
    else:
        start,end=(.31,-1.87,.99),(.29,-1.72,.93)
    maincam.data.lens=45 if revision==1 else (42 if revision==2 else 44)
    target=(-.19+.02*k,-.02,.48+.030*k) if revision==1 else (-.235+.017*k,.015,.59+.03*k)
    look(maincam,Vector(start).lerp(Vector(end),k),target)
    q=ease(f,REFLECT_AT,96)
    look(phonecam,Vector(insert)+Vector((-.004,.010,-.009))*q,phone.location+Vector((0,.007,.003)))
    if revision>=2:
        rot=phonecam.rotation_euler.to_quaternion()
        phonecam.rotation_euler=(rot@Quaternion((0,0,1),(math.pi-.42 if revision>=3 else math.pi))).to_euler()
    camera_now=maincam if f<REFLECT_AT else phonecam
    bpy.context.view_layer.update()
    screen_poly=[project(camera_now,screen,p) for p in screen_points]
    head_pos=world_head()
    hp=world_to_camera_view(sc,camera_now,head_pos)
    main_out[f]={'screen':screen_poly,'head':[hp.x,1-hp.y],'wrist_error_m':errors,
                 'support_wrist':list(arm.matrix_world@bones['J_Bip_L_Hand'].head),
                 'support_finger':list(arm.matrix_world@bones['J_Bip_L_Middle3_end'].head)}
    render('room',f,camera_now)
    if f>=REFLECT_AT:
        plane=screen.matrix_world@Vector((0,0,.00877))
        reflected(phonecam,plane,normal)
        saved={o:o.hide_render for o in env}
        for ob in env:
            ob.hide_render=True
        render('mirror',f,mirrorcam)
        for ob,value in saved.items():
            ob.hide_render=value
(OUT/'frame_meta.json').write_text(json.dumps(main_out),encoding='utf-8')

