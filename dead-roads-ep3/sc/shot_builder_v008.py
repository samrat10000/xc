"""Episode 3 frozen v006 blocking builder. Original buggy, authored movement, resumable shots.

CPU checks: DEVICE=CPU RES=.25 SAMP=4 SHOT=14 FRAMES=36 blender -b -P sc/ep3.py
Scene only: SAVE_ONLY=1. This is blocking, not final-quality character animation.
"""
import ast,bisect,json,math,os,random,sys,types
from pathlib import Path
import bpy
from mathutils import Vector,Matrix,Euler,Quaternion
ROOT=Path(__file__).resolve().parents[1]; XC=ROOT.parent; SHARED=XC/'SHARED_ASSETS'
EP2=XC/'dead-roads-ep2'; os.environ['EP2']=str(EP2);os.environ['EP']='3'
sys.path.insert(0,str(EP2/'sc'))
import lib as L
import shots as S
# Load the existing Ep2 helper module without running its last shot-dispatch expression.
tree=ast.parse((EP2/'sc/ep2.py').read_text(encoding='utf8'))
tree.body=[node for node in tree.body if not (isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Subscript))]
E=types.ModuleType('ep2_helpers');E.__file__=str(EP2/'sc/ep2.py');exec(compile(tree,E.__file__,'exec'),E.__dict__)
PLAN=json.loads((ROOT/'SHOTS.json').read_text(encoding='utf8'))
SHOT=int(os.environ.get('SHOT','14')); SPEC=PLAN['shots'][SHOT-1];N=SPEC['frames'];FPS=24
RES=float(os.environ.get('RES','.25'));SAMPLES=int(os.environ.get('SAMP','4'))
DEVICE=os.environ.get('DEVICE','CPU').upper();VERSION=os.environ.get('VERSION','v001')
OUT=ROOT/'frames'/VERSION/f'shot{SHOT:02d}';OUT.mkdir(parents=True,exist_ok=True)
V=lambda *v:Vector(v[0] if len(v)==1 else v)
RNG=random.Random(300+SHOT)
SHAKES=json.loads((SHARED/'ep3/v001/references/camera-shakify/shake_data.json').read_text()) if (SHARED/'ep3/v001/references/camera-shakify/shake_data.json').exists() else {}

def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)

def key(o,f,loc=None,rot=None,scale=None):
 if loc is not None:o.location=loc;o.keyframe_insert('location',frame=f)
 if rot is not None:o.rotation_euler=rot;o.keyframe_insert('rotation_euler',frame=f)
 if scale is not None:o.scale=scale;o.keyframe_insert('scale',frame=f)

def bone_world_rotation(rig,bone,rotations,frame):
 pb=rig.pose.bones[bone];q=Quaternion();inverse_object=rig.matrix_world.to_3x3().inverted();inverse_bone=pb.bone.matrix_local.to_3x3().inverted()
 for axis,degrees in rotations:
  unit={'X':V((1,0,0)),'Y':V((0,1,0)),'Z':V((0,0,1))}[axis];local=(inverse_bone@inverse_object@unit).normalized();q=Quaternion(local,math.radians(degrees))@q
 pb.rotation_mode='QUATERNION';pb.rotation_quaternion=q;pb.keyframe_insert('rotation_quaternion',frame=frame)

def linear():
 for a in bpy.data.actions:
  for layer in a.layers:
   for strip in layer.strips:
    for bag in strip.channelbags:
     for fc in bag.fcurves:
      for k in fc.keyframe_points:k.interpolation='LINEAR'

def material(name,color,rough=.6,metal=0,emission=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal
 if emission:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
 return m

def cube(name,loc,scale,mat,bevel=.02,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bevel:b=o.modifiers.new('Worn edges','BEVEL');b.width=bevel;b.segments=2
 o.data.materials.append(mat)
 if parent:o.parent=parent
 return o

def tube(name,points,radius,mat,parent=None):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=2
 s=c.splines.new('POLY');s.points.add(len(points)-1)
 for p,co in zip(s.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);SC.collection.objects.link(o);c.materials.append(mat)
 if parent:o.parent=parent
 return o

def light(name,loc,target,power,color=(1,.77,.47),size=3,kind='AREA',parent=None):
 d=bpy.data.lights.new(name,kind);d.energy=power;d.color=color
 if kind=='AREA':d.shape='DISK';d.size=size
 else:d.spot_size=math.radians(42);d.spot_blend=.65;d.shadow_soft_size=.08
 o=bpy.data.objects.new(name,d);SC.collection.objects.link(o);o.location=loc;o.rotation_euler=(V(target)-V(loc)).to_track_quat('-Z','Y').to_euler()
 if parent:o.parent=parent
 o.visible_glossy=False
 return o

def append(path,name):
 with bpy.data.libraries.load(str(path),link=False) as (s,d):d.collections=[name]
 if not d.collections or not d.collections[0]:raise RuntimeError(f'Missing collection {name}: {path}')
 col=d.collections[0];SC.collection.children.link(col)
 if not any(o.type=='MESH' for o in col.all_objects):raise RuntimeError(f'Asset collection has no visible geometry: {path} / {name}')
 for o in list(col.all_objects):
  if o is None:continue
  if o.animation_data:o.animation_data_clear()
  if 'hull' in o.name.lower():o.hide_render=True
 return col

def reset():
 global SC
 bpy.ops.wm.read_factory_settings(use_empty=True);SC=bpy.context.scene;SC.render.engine='CYCLES';SC.cycles.device='CPU';SC.cycles.samples=SAMPLES
 SC.render.resolution_x=1080;SC.render.resolution_y=810 if SHOT in (4,13,16) else 1920;SC.render.resolution_percentage=round(RES*100);SC.render.fps=24;SC.render.threads_mode='FIXED';SC.render.threads=4
 SC.render.image_settings.file_format='PNG';SC.render.image_settings.color_mode='RGB';SC.render.use_file_extension=True
 SC.cycles.max_bounces=4;SC.cycles.diffuse_bounces=2;SC.cycles.glossy_bounces=2;SC.cycles.transmission_bounces=4;SC.cycles.volume_bounces=0
 SC.cycles.use_adaptive_sampling=True;SC.cycles.adaptive_threshold=.08 if RES<1 else .025;SC.cycles.use_denoising=True;SC.cycles.denoiser='OPENIMAGEDENOISE'
 if hasattr(SC.cycles,'denoising_use_gpu'):SC.cycles.denoising_use_gpu=False
 SC.render.use_persistent_data=True;SC.render.use_motion_blur=True;SC.render.motion_blur_shutter=.35
 SC.view_settings.view_transform='AgX';SC.view_settings.look='AgX - Medium High Contrast';SC.view_settings.exposure=1.0
 SC.frame_start=1;SC.frame_end=N
 world=bpy.data.worlds.new('Night air');world.use_nodes=True;world.node_tree.nodes['Background'].inputs[0].default_value=(.035,.052,.09,1);world.node_tree.nodes['Background'].inputs[1].default_value=.18;SC.world=world
 S.sc=SC;E.sc=SC;S.SET=bpy.data.collections.new('Ep3 street');SC.collection.children.link(S.SET);E.SET=S.SET
 if DEVICE=='GPU':
  prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
  available=False
  for d in prefs.devices:d.use=d.type=='OPTIX';available|=d.use
  if not available:raise RuntimeError('No OptiX GPU; explicit CPU checks remain available')
  SC.cycles.device='GPU';SC.cycles.use_denoising=True;SC.cycles.denoiser='OPTIX'

def camera(fn,lens=28,shake=.3,mounted=False):
 c=bpy.data.cameras.new(f'Ep3 shot {SHOT}');o=bpy.data.objects.new(c.name,c);SC.collection.objects.link(o);SC.camera=o;c.lens=lens;c.sensor_width=36;c.clip_start=.04;c.clip_end=600
 data=SHAKES.get('INVESTIGATION');channels={}
 if data:
  for ch in data['channels']:channels[(ch['path'],ch['axis'])]=ch['keys']
 def sample(channel,f):
  pts=channels.get(channel)
  if not pts:return 0
  t=(f+SHOT*19)%(pts[-1][0]-pts[0][0])+pts[0][0];idx=bisect.bisect_left([p[0] for p in pts],t);idx=max(1,min(len(pts)-1,idx));a,b=pts[idx-1:idx+1]
  return a[1]+(b[1]-a[1])*(t-a[0])/max(1,b[0]-a[0])
 aim=None
 for f in range(1,N+1):
  SC.frame_set(f);p,target,mm=fn((f-1)/FPS);p=V(p);target=V(target)
  if aim is None:aim=target.copy()
  aim=target if mounted else aim.lerp(target,.35)
  p+=V([sample(('location',j),f)*shake*.12 for j in range(3)])
  q=(aim-p).to_track_quat('-Z','Y').to_euler()
  for j in range(3):q[j]+=sample(('rotation_euler',j),f)*shake
  key(o,f,p,q);c.lens=mm;c.keyframe_insert('lens',frame=f)
  if SHOT in (6,7,18):
   c.dof.use_dof=True;c.dof.aperture_fstop=4 if SHOT==6 else 2.8;c.dof.focus_distance=(target-p).length;c.dof.keyframe_insert('focus_distance',frame=f)
 o['shake_source']='Camera Shakify CC0 recorded data' if data else 'none';return o

def street():
 S.world(fog=0,length=100,width=30 if SHOT==3 else 18,cy=-40,seed=14)
 # Existing city sky is allowed to add volumes; remove for bounded CPU blocking.
 for w in bpy.data.worlds:
  if w.use_nodes:
   for n in list(w.node_tree.nodes):
    if n.type=='VOLUME_PRINCIPLED':w.node_tree.nodes.remove(n)
 for o in list(bpy.data.objects):
  if o.name.lower().startswith(('fog','mist')):bpy.data.objects.remove(o,do_unlink=True)
 light('Sodium pool',(-5,5,8),(0,5,0),2600)
 light('Cool street rim',(5,22,8),(0,2,1),2200,(.3,.49,.8),5)
 if SHOT not in (6,7):S.rain((0,8),N/FPS+.1,count=500 if RES<1 else 3500,size=(17,48))

def buggy(pos=(0,0,0),damaged=True,path=None):
 col=append(SHARED/'ep3/v001/assets/buggy-assemblies-v002.blend','NT_ORIGINAL');root=next(o for o in col.all_objects if o.name.startswith('NT_EP3_ROOT'))
 # Refit the existing seat and its duplicate before orienting the import.
 bpy.context.view_layer.update()
 seat=[o for o in col.all_objects if o.type=='MESH' and 'seat' in o.name.lower()]
 for o in seat:
  world=o.matrix_world.copy();o.matrix_world=Matrix.Translation((0,-.40,0))@world
  copy=o.copy();copy.data=o.data;col.objects.link(copy);copy.matrix_world=Matrix.Translation((0,.40,0))@world;copy.name='Passenger '+o.name
 for o in col.all_objects:
  if 'steering wheel' in o.name.lower():o.matrix_world=Matrix.Translation((0,-.40,0))@o.matrix_world
 root.location=pos;root.rotation_euler=(0,0,-math.pi/2)
 # Additional reinforcement follows original import coordinates (-X = front).
 steel=material('Cage refit wet steel',(.035,.045,.044),.4,.7)
 for side in (-.65,.65):tube('Refit upper cage',[(-.7,side,1.9),(.6,side,1.95),(1.4,side,1.48)],.035,steel,root)
 tube('Refit crossbar',[(-.7,-.65,1.9),(-.7,.65,1.9)],.035,steel,root)
 crown=tube('Cockpit central cage bar',[(.33,-.65,1.9),(.33,0,1.9),(.33,.65,1.9)],.035,steel,root)
 if SHOT>=13:
  middle=crown.data.splines[0].points[1]
  if SHOT==13:
   for frame,z in ((1,1.9),(9,1.9),(14,1.62),(N,1.62)):middle.co.z=z;middle.keyframe_insert('co',frame=frame)
  else:middle.co.z=1.62
 for sx in (-1,1):
  # Local -Y is driver's left. Dead-side emitter stays zero throughout the damaged shots.
  enabled=not (damaged and sx==-1)
  light('Dead LEFT headlight' if sx==-1 else 'RIGHT headlight',(-2.22,sx*.72,1.05),(-30,sx*1.5,.4),0 if not enabled else 6500,(1,.84,.58),kind='SPOT',parent=root)
 # Original real-time lamps are meshes; suppress the dead bank's actual emissive materials too.
 bpy.context.view_layer.update()
 if damaged:
  for o in col.all_objects:
   if o.type=='MESH' and any(w in o.name.lower() for w in ['lamp','light','lens','led']):
    center=root.matrix_world.inverted()@o.matrix_world.translation
    if center.y<-.12:
     for slot in o.material_slots:
      if slot.material:
       m=slot.material.copy();slot.material=m
       if m.use_nodes:
        for p in m.node_tree.nodes:
         if p.type=='BSDF_PRINCIPLED':p.inputs['Emission Strength'].default_value=0
         elif p.type=='EMISSION':p.inputs['Strength'].default_value=0
 for o in col.all_objects:
  if o.type=='MESH' and 'hood top' in o.name.lower():
   o.data=o.data.copy();o.shape_key_add(name='Basis');damage=o.shape_key_add(name='Nose crumple')
   to_car=root.matrix_world.inverted()@o.matrix_world
   to_mesh=o.matrix_world.to_3x3().inverted()@root.matrix_world.to_3x3()
   for p in damage.data:
    local=to_car@p.co;w=max(0,min(1,(-local.x-.7)/1.3));p.co+=to_mesh@V((.18*w,0,-.16*w))
   damage.value=1 if damaged else 0
   if SHOT in (3,4):
    for f,value in ([(17,0),(21,.45),(32,1)] if SHOT==3 else [(12,0),(16,1)]):damage.value=value;damage.keyframe_insert('value',frame=f)
 if path:
  previous=None;travel=0
  # Imported assembly origins are near the chassis, not the actual axle centers.
  # Insert proper spin pivots without moving source geometry.
  assemblies=[o for o in col.all_objects if o.type=='EMPTY' and 'wheel assembly' in o.name.lower()];wheels=[]
  bpy.context.view_layer.update()
  for assembly in assemblies:
   points=[child.matrix_world@V(v) for child in assembly.children_recursive if child.type=='MESH' and not child.hide_render for v in child.bound_box]
   if not points:continue
   center=V([(min(p[j] for p in points)+max(p[j] for p in points))/2 for j in range(3)])
   local=root.matrix_world.inverted()@center;pivot=L.empty('EP3 axle '+assembly.name,local,root);bpy.context.view_layer.update()
   world=assembly.matrix_world.copy();assembly.parent=pivot;assembly.matrix_world=world;wheels.append(pivot)
  for f in range(1,N+1):
   p,heading=path((f-1)/FPS);key(root,f,p,(0,0,heading-math.pi/2))
   if previous is not None:travel+=(V(p)-previous).dot(V((-math.sin(heading),math.cos(heading),0)))
   previous=V(p)
   for wheel in wheels:
    wheel.rotation_euler.y=-travel/.60;wheel.keyframe_insert('rotation_euler',index=1,frame=f)
 if SHOT not in (1,2,5,6,7,8,9,19):
  seated_human('Sam',root,driver=True)
  seated_human('Rider',root,driver=False)
 return root

def human(name):
 path=SHARED/('blends/wakeup/sam.blend' if name=='Sam' else 'blends/rider.blend')
 col=append(path,'SAM' if name=='Sam' else 'RIDER');rig=next(o for o in col.all_objects if o.type=='ARMATURE')
 for pb in rig.pose.bones:
  for c in list(pb.constraints):pb.constraints.remove(c)
  pb.rotation_mode='XYZ';pb.rotation_euler=(0,0,0)
 L._fixparents(col,rig)
 if name=='Sam':rig.scale=(1.095,)*3
 return rig

def seated_human(name,car,driver=True):
 rig=human(name);side=-.40 if driver else .40
 targets=L.seat_rider(rig,car,seat=V((.33,side,.86)))
 for s in 'LR':
  for digit in range(2,6):
   for segment,angle in ((1,30),(2,42),(3,24)):
    pb=rig.pose.bones.get(f'finger{digit}-{segment}.{s}')
    if pb:pb.rotation_euler=(0,0,-math.radians(angle))
 for s,direction in (('L',-1),('R',1)):
  targets[s]['hand'].location=V((-.09,side+direction*.14,1.14)) if driver else V((-.06,side+direction*.14,1.12))
  targets[s]['elbow'].location=V((.44,side+direction*.40,1.06))
  targets[s]['foot'].location=V((-.60,side+direction*.12,.38))
  targets[s]['knee'].location=V((-.45,side+direction*.17,1.18))
 base={pb.name:tuple(pb.rotation_euler) for pb in rig.pose.bones}
 for f in range(1,N+1):
  t=(f-1)/24
  for bone,amp in [('spine04',1.0),('neck01',.8),('head',1.4)]:
   pb=rig.pose.bones[bone];pb.rotation_euler=base[bone];pb.rotation_euler.x+=math.radians(amp*math.sin(t*2.2));pb.keyframe_insert('rotation_euler',frame=f)
  if SHOT==4:
   k=math.exp(-((f-16)/3)**2);pb=rig.pose.bones['spine04'];pb.rotation_euler.x+=math.radians(12*k);pb.keyframe_insert('rotation_euler',frame=f)
  if SHOT==16 and driver:
   for s in 'LR':
    target=targets[s]['hand'];p=V((-.09,side+(-1 if s=='L' else 1)*.14,1.14));p.z+=.005*math.sin(t*21);key(target,f,p)
  if SHOT==13 and not driver:
   target=targets['R']['hand'];k=ease((f-4)/10);p=V((-.06,side+.14,1.12)).lerp(V((.0,side+.05,1.88)),k)
   recoil=sum(.035*math.exp(-((f-ff)/1.3)**2) for ff in (14,29,45));p.z-=recoil;key(target,f,p)
 if SHOT==13 and not driver:
  metal=material('Pistol worn steel',(.018,.02,.022),.45,.7)
  gun=cube('Rider pistol',(.0,0,.05),(.14,.035,.04),metal,parent=targets['R']['hand']);gun.rotation_euler.y=-math.pi/2
 return rig,targets

def grip_scene():
 sam=human('Sam');rider=human('Rider');sam.location=(-1.85,.6,0);sam.rotation_euler.z=-math.pi/2;rider.location=(-2.65,.6,-.52);rider.rotation_euler.z=math.pi/2
 actors=[(sam,'R',(-2.23,.59,1.15),(-1.75,1.0,1.18)),(rider,'L',(-2.28,.61,1.19),(-2.8,1.15,.75))]
 for s,sy in (('L',1),('R',-1)):
  foot=L.empty('Rider planted foot',V((-2.8,.6+sy*.16,.05)));knee=L.empty('Rider pull-up knee',V((-2.15,.6+sy*.18,.5)));L.ik(rider,'lowerleg02.'+s,foot,knee,4,-90)
 free_hands={}
 bpy.context.view_layer.update()
 for rig,active_side,contact,pole in actors:
  free_side='L' if active_side=='R' else 'R';sign=1 if free_side=='L' else -1
  rest=rig.matrix_world@V((sign*.23,.03,.80));elbow=rig.matrix_world@V((sign*.44,0,1.02))
  target=L.empty(rig.name+' relaxed free hand',rest);pole_obj=L.empty(rig.name+' relaxed elbow',elbow);L.ik(rig,'lowerarm02.'+free_side,target,pole_obj,4,-90);free_hands[rig]=(target,rest,pole_obj,elbow)
  for digit in range(2,6):
   for segment,curl in ((1,8),(2,12),(3,6)):
    pb=rig.pose.bones.get(f'finger{digit}-{segment}.{free_side}')
    if pb:pb.rotation_euler=(0,0,-math.radians(curl))
 for rig,side,contact,pole in actors:
  target=L.empty(name:=rig.name+' forearm contact',V(contact));elbow=L.empty(rig.name+' elbow',V(pole));L.ik(rig,'lowerarm02.'+side,target,elbow,4,-90)
  # Curl articulated fingers around a forearm; keep thumb separate from finger curl.
  for digit in range(2,6):
   for segment,curl in ((1,45),(2,55),(3,30)):
    pb=rig.pose.bones.get(f'finger{digit}-{segment}.{side}')
    if pb:pb.rotation_euler=(0,0,-math.radians(curl))
  for f in range(1,N+1):
   u=ease((f-10)/(N-15));key(target,f,V(contact)+V((0,0,.35*u)))
   if rig==rider:key(rig,f,(-2.65,.6,-.52+.52*u),(0,0,math.pi/2))
   free,rest,free_pole,elbow=free_hands[rig];lift=.52*u if rig==rider else 0;key(free,f,rest+V((0,0,lift)));key(free_pole,f,elbow+V((0,0,lift)))
   for bone in ('spine04','head'):
    pb=rig.pose.bones[bone];pb.rotation_euler.x=math.radians(8*(1-u) if rig==rider else 10*math.sin(u*math.pi));pb.keyframe_insert('rotation_euler',frame=f)
 return sam,rider

def crowd(count=30,y0=18):
 # Linked source meshes, individual rigs/actions for actual limb movement.
 for i in range(count):
  x=(i%6-2.5)*1.8+RNG.uniform(-.3,.3);y=y0+(i//6)*3.2
  rig=L.walker(V((x,y,0)),0,blend=str(SHARED/'blends/walker.blend'),seed=i+300)
  L.zombify(rig,i+300);fn,per=L.shamble(i+300,2.2);L.act(rig,1,N,fn,2);L.move_keys(rig,1,N,2.2,seed=i+300,per=per,bob=.05)

def creature(pos=(0,8,0),motion='idle',path=None,broken=False):
 facing=math.pi if SHOT in (13,14,15) else 0
 rig=L.stalker(V(pos),facing,blend=str(SHARED/'blends/stalker_rig.blend'));rig.scale=(1.25,)*3
 for o in rig.children_recursive:
  if 'hull' in o.name:o.hide_render=True
 def fn(t,f):
  gallop=motion=='gallop';p=V(path(t) if path else pos)
  d=L.stalk_pose(t,gait=1.4 if gallop else .16,gph=t*(10 if gallop else 2),jaw=.55+.12*math.sin(t*3),look=(8*math.sin(t*1.5),8),crouch=.7 if gallop else .1)
  if gallop:
   d['sp0m1']=[('X',35+9*math.sin(t*10))];p.z+=.09*abs(math.sin(t*10))
  d['_root']=(p,(0,0,facing));return d
 L.sact(rig,1,N,fn)
 if broken:
  antler=next((o for o in rig.children_recursive if o.type=='MESH' and o.name=='Stalker antlers'),None)
  if antler:
   antler.data=antler.data.copy()
   # Anatomical left is the rig's +X for a character facing -Y; preview gate required.
   import bmesh
   bm=bmesh.new();bm.from_mesh(antler.data);dead=[v for v in bm.verts if v.co.x>0]
   bmesh.ops.delete(bm,geom=dead,context='VERTS');bm.to_mesh(antler.data);bm.free()
 return rig

def tunnel():
 concrete=L.pbr('Scanned tunnel concrete','concrete_wall_006',tile=3,wet=.3,tint=(.35,.4,.37))
 road=L.pbr('Tunnel asphalt','road_damaged',tile=4.5,wet=.5,puddles=.15)
 cube('Tunnel road',(0,100,-.15),(13,240,.3),road,0)
 # One detailed 10m section, then linked mesh copies down the 200m tunnel.
 tile=material('Dirty cream ceramic tiles',(.24,.27,.23),.38)
 nt=tile.node_tree;bs=nt.nodes.get('Principled BSDF');tex=nt.nodes.new('ShaderNodeTexBrick');tex.inputs['Color1'].default_value=(.32,.34,.28,1);tex.inputs['Color2'].default_value=(.15,.19,.17,1);tex.inputs['Mortar'].default_value=(.022,.026,.021,1);tex.inputs['Mortar Size'].default_value=.012;tex.inputs['Scale'].default_value=7;tex.offset=0
 coord=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(coord.outputs['Object'],tex.inputs['Vector']);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color'])
 bump=nt.nodes.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.025;bump.inputs['Strength'].default_value=.3;nt.links.new(tex.outputs['Fac'],bump.inputs['Height']);nt.links.new(bump.outputs['Normal'],bs.inputs['Normal'])
 parts=[]
 for side in (-1,1):
  parts.append(cube('Tiled tunnel wall',(side*6.1,5,1.45),(.3,10,2.9),tile))
  parts.append(cube('Concrete upper wall',(side*6,5,3.35),(.5,10,.9),concrete))
  parts.append(cube('Lane curb',(side*5.7,5,.12),(.42,10,.24),concrete))
 parts.append(cube('Ceiling underside at 3.81m',(0,5,4.05),(12.5,10,.48),concrete))
 for segment in range(1,20):
  for source in parts:
   o=source.copy();o.data=source.data;SC.collection.objects.link(o);o.location.y+=segment*10
 for y in range(5,201,15):
  for x in (-5.7,5.7):
   cube('Unpowered fluorescent housing',(x,y,3.42),(.18,2.5,.12),steel if (steel:=bpy.data.materials.get('Fixture steel')) else material('Fixture steel',(.025,.03,.032),.8,.6))
   tube('Service conduit',[(x,y-7,2.9),(x,y+7,2.9)],.035,bpy.data.materials['Fixture steel'])
 cube('Clearance concrete lip',(0,-.3,4.25),(13,.8,.88),concrete)
 sign=material('Faded clearance sign',(.52,.43,.2),.9)
 cube('Clearance sign backing',(0,-.73,4.44),(5.3,.04,.45),sign)
 text=bpy.data.curves.new('Physical clearance sign','FONT');text.body='CLEARANCE 12\'6"';text.align_x='CENTER';text.size=.27;text.extrude=.001
 o=bpy.data.objects.new(text.name,text);SC.collection.objects.link(o);o.location=(0,-.758,4.35);o.rotation_euler=(math.pi/2,0,0);text.materials.append(material('Sign black',(.008,.009,.006)))
 # Cold reflected fill, restrained; hero headlight carries the reveal.
 light('Tunnel mouth bounce',(-4,-4,3),(0,15,1),500,(.23,.35,.56),6)
 for y in (18,55,100):light('Distant reflected spill',(5,y,2.8),(0,y+12,1),130,(.32,.40,.44),2)

def truck():return E.truck2(V((.8,12,0)),math.radians(8))

def sparks(at,frame=15):
 E.hit_sparks(V(at),frame,seed=SHOT)

def shot_1_2():
 street();st=creature((0,7,1.4),path=lambda t:(0,9-3*t,1.3+.65*math.sin(t*1.6)))
 if SHOT==1:camera(lambda t:((.2,2,.12),(0,7-2*t,2.1),18),shake=.12)
 else:
  buggy((-7,4,0),False,path=lambda t:(( -8+5*t,4,0),-math.pi/2));camera(lambda t:((.4,1,1.65),(0,5.5,2.4),24),shake=.4)

def shot_3():
 street();tr=E.truck2(V((12,7,0)),math.pi/2);car=buggy(damaged=False,path=lambda t:((-16+min(t,1.25)*19.44,7,0),-math.pi/2))
 def body_x(t):return .4+min(max(0,t-.72),.53)*19.44
 st=creature(path=lambda t:(body_x(t),7,1.5+.6*math.sin(t*2)))
 for f in range(1,N+1):
  t=(f-1)/24;hit=ease((t-.72)/.53);key(st,f,(body_x(t),7,1.65+.45*math.sin(hit*math.pi)),(0,hit*.65,0))
  k=max(0,t-1.25);key(tr,f,rot=(0,.07*math.exp(-k*3)*math.sin(k*15) if k else 0,math.pi/2))
 sparks((10.5,7,1.1),31)
 light('Impact rim',(8,11,6),(6,7,2),5200,(.54,.68,1),4)
 camera(lambda t:((body_x(t)-3.5,.6,1.7),(body_x(t),7,2.6),24),shake=.25)

def antler_break(rig,break_frame=31):
 """Detach anatomical LEFT geometry from the evaluated rig at impact."""
 import bmesh
 source=next(o for o in rig.children_recursive if o.type=='MESH' and o.name=='Stalker antlers')
 def half(left):
  obj=source.copy();obj.data=source.data.copy();SC.collection.objects.link(obj);obj.name='Stalker LEFT antler' if left else 'Stalker RIGHT antler'
  bm=bmesh.new();bm.from_mesh(obj.data);dead=[v for v in bm.verts if (v.co.x<=0 if left else v.co.x>0)];bmesh.ops.delete(bm,geom=dead,context='VERTS');bm.to_mesh(obj.data);bm.free();return obj
 left=half(True);right=half(False)
 SC.frame_set(break_frame-1);bpy.context.view_layer.update();evaluated=left.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=bpy.data.meshes.new_from_object(evaluated);mesh.transform(left.matrix_world)
 points=[v.co.copy() for v in mesh.vertices];center=V([(min(v[j] for v in points)+max(v[j] for v in points))/2 for j in range(3)]);mesh.transform(Matrix.Translation(-center));mesh.name='StalkerLeftAntlerGeometry'
 for modifier in list(left.modifiers):left.modifiers.remove(modifier)
 left.parent=None;left.matrix_world=Matrix();left.data=mesh
 for obj,before,after in ((source,False,True),(right,True,False),(left,True,False)):
  obj.hide_render=before;obj.keyframe_insert('hide_render',frame=1);obj.hide_render=before;obj.keyframe_insert('hide_render',frame=break_frame-1);obj.hide_render=after;obj.keyframe_insert('hide_render',frame=break_frame)
 asset=SHARED/'ep3/v001/assets/stalker-left-antler-v001.blend'
 if not asset.exists():bpy.data.libraries.write(str(asset),{mesh},fake_user=True,compress=True)
 corners=[V((x,y,z)) for x in (min(v.x for v in points)-center.x,max(v.x for v in points)-center.x) for y in (min(v.y for v in points)-center.y,max(v.y for v in points)-center.y) for z in (min(v.z for v in points)-center.z,max(v.z for v in points)-center.z)]
 for f in range(break_frame,N+1):
  t=(f-break_frame)/24;rot=Euler((t*8,t*3,t*5));p=center+V((-.8*t,-6*t,1.3*t-4.9*t*t));floor=-min((rot.to_matrix()@v).z for v in corners)+.025;p.z=max(floor,p.z);key(left,f,p,rot)
 return left

def shot_4_13_16():
 tunnel() if SHOT==16 else street();car=buggy((0,12 if SHOT==16 else 2,0),SHOT!=4)
 y=12 if SHOT==16 else 2
 # Real rig pose/contact is a separate pass. Reserve cabin framing without fake humans.
 camera(lambda t:((0,y+.36,1.55),(0,y-.4,1.38),16),shake=.06,mounted=True)
 if SHOT==13:
  st=creature((0,y-.2,1.55))
  for i,f in enumerate((14,29,45)):
   flash=light('Upward pistol flash',(.48,y-.15,1.6),(.48,y-.15,4),0,(1,.65,.3),kind='SPOT')
   for k,p in ((f-1,0),(f,1100),(f+1,0)):flash.data.energy=p;flash.data.keyframe_insert('energy',frame=k)

def shot_5_6_7():
 street();car=buggy();print('BUILD importing wrecked trike',flush=True)
 trikecol=append(SHARED/'ep3/v001/assets/trike-wreck-source-v001.blend','WRECK_TRIKE');print('BUILD trike imported',flush=True)
 trike=L.empty('Wrecked IVORY',(3,1,1.2))
 for part in trikecol.all_objects:
  if part.parent is None:part.parent=trike
 trike.rotation_euler=(math.pi/2,0,.2);trike.location.z=2.8
 print('BUILD wreck transform set',flush=True)
 if SHOT==5:
  steam=material('Radiator steam placeholder',(.3,.3,.3));nt=steam.node_tree;nt.nodes.clear();output=nt.nodes.new('ShaderNodeOutputMaterial');volume=nt.nodes.new('ShaderNodeVolumePrincipled');volume.inputs['Color'].default_value=(.7,.75,.8,1);nt.links.new(volume.outputs['Volume'],output.inputs['Volume'])
  coord=nt.nodes.new('ShaderNodeTexCoord');dist=nt.nodes.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.5,.5);nt.links.new(coord.outputs['Generated'],dist.inputs[0]);fall=nt.nodes.new('ShaderNodeMath');fall.operation='SUBTRACT';fall.inputs[0].default_value=.48;nt.links.new(dist.outputs['Value'],fall.inputs[1]);fall.use_clamp=True
  noise=nt.nodes.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=5;noise.inputs['Detail'].default_value=3;nt.links.new(coord.outputs['Generated'],noise.inputs['Vector'])
  mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(fall.outputs[0],mul.inputs[0]);nt.links.new(noise.outputs['Fac'],mul.inputs[1]);nt.links.new(mul.outputs[0],volume.inputs['Density'])
  for f,w in ((1,0),(N,1.8)):noise.inputs['W'].default_value=w;noise.inputs['W'].keyframe_insert('default_value',frame=f)
  cube('Bounded radiator steam',(0,1.8,1.8),(.8,.8,1.5),steam,0)
  camera(lambda t:((6-t*.5,-4+t*.4,1.65),(0,1,1.1),32),shake=.4)
 elif SHOT==6:
  grip_scene();rescue_light=light('Rescue soft street bounce',(-3.8,-1.6,1.1),(-2.25,.6,1.3),400,(.72,.79,.84),kind='SPOT');rescue_light.data.spot_size=math.radians(25)
  camera(lambda t:((-3.5,-.8,1.35+t*.02),(-2.25,.6,1.31),65),shake=.23)
 else:
  rig=human('Rider');rig.location=(2.5,.8,0);hand=L.empty('Belt pickup wrist',(2.45,.5,1.15));pole=L.empty('Belt pickup elbow',(2.0,.85,1.05));L.ik(rig,'lowerarm02.R',hand,pole,4,-90)
  brass=material('Cartridge brass',(.39,.23,.06),.4,.65);copper=material('Bullet copper',(.28,.095,.035),.42,.7);link_mat=material('Belt links',(.025,.027,.024),.65,.6)
  bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.0095,depth=.095);shell=bpy.context.object;shell.data.materials.append(brass)
  bpy.ops.mesh.primitive_cone_add(vertices=16,radius1=.0064,radius2=.001,depth=.035,location=(0,0,.065));tip=bpy.context.object;tip.data.materials.append(copper)
  bpy.ops.object.select_all(action='DESELECT');shell.select_set(True);tip.select_set(True);bpy.context.view_layer.objects.active=shell;bpy.ops.object.join();round_mesh=shell.data;bpy.data.objects.remove(shell,do_unlink=True)
  bpy.ops.mesh.primitive_torus_add(major_segments=12,minor_segments=4,major_radius=.011,minor_radius=.002);link=bpy.context.object;link.data.materials.append(link_mat);link_mesh=link.data;bpy.data.objects.remove(link,do_unlink=True)
  for index in range(43):
   u=index/42;round_obj=bpy.data.objects.new('Live belt round %02d'%index,round_mesh);SC.collection.objects.link(round_obj);link_obj=bpy.data.objects.new('Steel belt link %02d'%index,link_mesh);SC.collection.objects.link(link_obj)
   for f in range(1,N+1):
    lift=.45*ease((f-6)/(N-12));p=V((2.45+u*1.12,.5+.05*math.sin(u*math.pi),1.15+(1-u)*lift-.12*math.sin(u*math.pi)))
    key(round_obj,f,p,(math.pi/2,0,.12*math.sin(u*math.pi)));key(link_obj,f,p,(math.pi/2,0,0))
  for f in range(1,N+1):key(hand,f,(2.45,.5,1.15+.45*ease((f-6)/(N-12))))
  for digit in range(2,6):
   for segment,curl in ((1,25),(2,40),(3,20)):rig.pose.bones[f'finger{digit}-{segment}.R'].rotation_euler=(0,0,-math.radians(curl))
  camera(lambda t:((2.6,-1,1.7),(2.55,.5,1.32),85),shake=.25)

def shot_8_9():
 street();tr=truck();st=creature((0,12,-.8),path=lambda t:(0,12,-1+2.4*ease(t/1.8)))
 if SHOT==8:camera(lambda t:((-2,9,.12),(0,12,.42),20),shake=.08)
 else:
  for f in range(1,N+1):key(tr,f,rot=(0,-.25*ease((f-5)/28),.14))
  def camfn(t):
   a=ease((t-.15)/.7);b=ease((t-1.35)/.8);p=V((1,3,1.7)).lerp(V((.3,9,4.7)),a)+V((0,0,1.8*math.sin(a*math.pi)));p=p.lerp(V((1,-3,2.4)),b)
   return p,(0,12,2.2),32+26*a-26*b
  camera(camfn,shake=.14)

def shot_10():
 street();crowd(30,15);col=append(SHARED/'ep3/v001/assets/screamer-rig-v003.blend','EP3_SCREAMER');rig=next(o for o in col.all_objects if o and o.type=='ARMATURE');L._fixparents(col,rig);rig.location=(-9.8,10,12.2);rig.rotation_euler.z=0
 roof=L.pbr('Rooftop concrete','concrete_wall_006',tile=3,wet=.4);cube('Roof parapet platform',(-10.5,10,12),(5,8,.35),roof)
 for f in range(1,N+1):
  t=(f-1)/24;k=ease((f-6)/12)*(1-.15*ease((f-30)/15))
  for bn,pitch in [('spine04',-12*k),('neck01',-18*k),('head',-15*k),('jaw',35*k)]:bone_world_rotation(rig,bn,[('X',pitch)],f)
 camera(lambda t:((1,-3,1.65),(-9.8,10,13.2),35),shake=.35)

def shot_11():
 street();crowd(30,18)
 def path(t):
  if t<.6:return (0,-6*t,0),0
  if t>2.1:return (7,-8-12*(t-2.1),0),math.pi
  u=(t-.6)/1.5;v=1-u
  p=V((0,-3.6,0))*v**3+V((0,-6.6,0))*(3*v*v*u)+V((7,-2,0))*(3*v*u*u)+V((7,-8,0))*u**3
  return p,math.pi*ease(u)
 car=buggy(path=path)
 camera(lambda t:(V(path(t)[0])+V((7*math.cos(t*.5),-6*math.sin(t*.5),1.4)),V(path(t)[0])+V((0,0,1)),28),shake=.12)

def shot_12():
 street();crowd(30,38);car=buggy(path=lambda t:((0,-16*t,0),math.pi));st=creature(motion='gallop',path=lambda t:(0,18-20*t,0))
 camera(lambda t:((0,-16*t+.9,1.5),(0,18-20*t,1.6),35),shake=.32)

def shot_14_15():
 tunnel();light('Tunnel approach sodium',(-5,-7,7),(0,-3,1.2),12000,(1,.68,.36),4);light('Portal rim',(4,-1,5),(0,-2,2.4),6000,(.3,.5,.8),4)
 car=buggy(path=lambda t:((0,-22+17*t,0),0))
 st=creature(path=lambda t:(0,-22+17*t,1.05+.10*ease(t/.9)),broken=SHOT==15)
 if SHOT==14:
  for f in range(1,N+1):
   t=(f-1)/24;impact=1.22
   if t>impact:key(st,f,(0,-1-7*(t-impact),1.15-1.0*ease((t-impact)/.7)),(-2*(t-impact),0,math.pi))
  sparks((0,0,3.81),30)
  antler_break(st,31)
  camera(lambda t:((4.7,-16+17*t,2.0),(0,-22+17*t,2.6),18),shake=.15)
 else:
  for f in range(1,N+1):
   t=(f-1)/24;key(st,f,(0,-4-3*t,max(.1,1-t)),(-2.4*t,0,math.pi+.4*t))
  bone=material('Broken antler charred bone',(.18,.14,.10),.85)
  asset=SHARED/'ep3/v001/assets/stalker-left-antler-v001.blend'
  if not asset.exists():raise RuntimeError('Build shot 14 first to create the real LEFT antler geometry')
  with bpy.data.libraries.load(str(asset),link=False) as (src,dst):dst.meshes=['StalkerLeftAntlerGeometry']
  prop=bpy.data.objects.new('Broken LEFT antler',dst.meshes[0]);SC.collection.objects.link(prop)
  bounds=[v.co.copy() for v in prop.data.vertices]
  for f in range(1,N+1):
   t=(f-1)/24;rot=Euler((t*5,t*.7,t*3));floor=-min((rot.to_matrix()@v).z for v in bounds)+.025;z=max(floor,.08+max(0,.35-t*.18)*abs(math.sin(t*12)));key(prop,f,(-.5,-2+7*t,z),rot)
  camera(lambda t:((1,8,.12),(0,-1,1),20),shake=.06)

def clone_rig(template):
 originals=[template,*template.children_recursive];mapping={}
 for source in originals:
  o=source.copy();SC.collection.objects.link(o);mapping[source]=o
  if o.animation_data:o.animation_data_clear()
 for source,o in mapping.items():
  if source.parent in mapping:o.parent=mapping[source.parent]
  for mod in o.modifiers:
   if mod.type=='ARMATURE' and mod.object==template:mod.object=mapping[template]
 rig=mapping[template]
 for pb in rig.pose.bones:
  for c in list(pb.constraints):
   if c.type=='IK':pb.constraints.remove(c)
 return rig

def shot_17_18():
 tunnel();car=buggy(path=lambda t:((0,6+1.4*min(t,2),0),0))
 prototypes=[]
 for name in ('ToyCar','CarConcept'):
  col=append(SHARED/'ep3/v001/assets/car-props-v002.blend','PROP_'+name);SC.collection.children.unlink(col);prototypes.append(col)
 husks=append(SHARED/'ep3/v001/assets/husk-rig-v003.blend','EP3_HUSK');template=next(o for o in husks.all_objects if o and o.type=='ARMATURE');L._fixparents(husks,template)
 L.zombify(template,731)
 # Finish library loads before editing shared material node trees (Blender 5.0).
 for col in prototypes:
  for obj in col.all_objects:
   if obj.type!='MESH':continue
   glass_object=False
   for material_slot in obj.material_slots:
    mat=material_slot.material
    if not mat or not mat.use_nodes:continue
    if 'glass' in mat.name.lower() and not mat.get('ep3_shadow_transmission'):
     nt=mat.node_tree;output=next(n for n in nt.nodes if n.type=='OUTPUT_MATERIAL');link=next((l for l in nt.links if l.to_node==output and l.to_socket==output.inputs['Surface']),None)
     if link:
      shader=link.from_socket;nt.links.remove(link);path=nt.nodes.new('ShaderNodeLightPath');transparent=nt.nodes.new('ShaderNodeBsdfTransparent');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(path.outputs['Is Shadow Ray'],mix.inputs[0]);nt.links.new(shader,mix.inputs[1]);nt.links.new(transparent.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],output.inputs['Surface']);mat['ep3_shadow_transmission']=True
    if 'glass' in mat.name.lower():
     glass_object=True;bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
     if bs:bs.inputs['IOR'].default_value=1.45;bs.inputs['Roughness'].default_value=.025
    if 'paint' in mat.name.lower():
     bs=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
     if bs:bs.inputs['Roughness'].default_value=.65;bs.inputs['Coat Weight'].default_value=.05
   if glass_object and not any(m.type=='SOLIDIFY' for m in obj.modifiers):
    # These glTF panes are single surfaces. Add the exit surface for proper refraction.
    shell=obj.modifiers.new('Four millimetre window glass','SOLIDIFY');shell.thickness=.004/max(abs(x) for x in obj.matrix_world.to_scale());shell.offset=0
 actor_count=0;first_head=None
 for row in range(9):
  for lane in range(3):
   index=row*3+lane;p=V((-3.7+lane*3.6+RNG.uniform(-.22,.22),22+row*6.4+RNG.uniform(-.4,.4),0));proto=prototypes[index%2]
   instance=L.empty('Abandoned occupied car '+str(index),p);instance.instance_type='COLLECTION';instance.instance_collection=proto;instance.rotation_euler.z=RNG.uniform(-.1,.1)
   if row==0:light('Headlight dashboard bounce',p+V((0,-1.05,1.02)),p+V((0,-.1,1.25)),.5,(.85,.86,.80),.45)
   for passenger in range(2 if index<13 else 1):
    # Set the occupants behind the sloped windscreen, not through its glass plane.
    rig=template if actor_count==0 else clone_rig(template);rig.location=p+V((-.40+passenger*.8,.65,-.24));rig.rotation_euler.z=0;actor_count+=1
    # Foot and wrist targets hold seated occupants in the cabin; eyes/head are animated.
    for s,side in (('L',1),('R',-1)):
     foot=L.empty('Husk foot',rig.location+V((side*.14,-.6,.55)));knee=L.empty('Husk knee',rig.location+V((side*.16,-.7,1.1)));L.ik(rig,'lowerleg02.'+s,foot,knee,4,-90)
     hand=L.empty('Husk wrist',rig.location+V((side*.2,-.28,1.15)));elbow=L.empty('Husk elbow',rig.location+V((side*.45,0,1.20)));L.ik(rig,'lowerarm02.'+s,hand,elbow,4,-90)
    desired=math.atan2(-rig.location.x,rig.location.y-6);offset=index%3
    for f in range(1,N+1):
     turn=ease((f-9-offset)/7) if SHOT==18 else 0;yaw=desired+math.radians(55)*(1-turn)
     bone_world_rotation(rig,'head',[('Z',math.degrees(yaw)*.7),('X',2*math.sin(f*.07))],f);bone_world_rotation(rig,'neck01',[('Z',math.degrees(yaw)*.3)],f)
    if index==1 and passenger==0:first_head=rig
 if SHOT==17:camera(lambda t:((-.9,5.4+min(t,2)*1.4,1.62),(0,24,1.18),32),shake=.18)
 else:
  SC.frame_set(N//2);bpy.context.view_layer.update();target=first_head.matrix_world@first_head.pose.bones['head'].head+V((0,0,.08));camera(lambda t:((.6,18+t*.25,1.4),target,50),shake=.12)
 SC['occupied_cars']=27;SC['seated_husks']=actor_count
 if not any(o.type=='MESH' and 'husk' in o.name.lower() for o in SC.objects):raise RuntimeError('Occupied-car scene is missing Husk meshes')

def shot_19():
 SC.world.node_tree.nodes['Background'].inputs[1].default_value=0
 camera(lambda t:((0,0,0),(0,1,0),35),shake=0)

def build():
 reset()
 if SHOT in (1,2):shot_1_2()
 elif SHOT==3:shot_3()
 elif SHOT in (4,13,16):shot_4_13_16()
 elif SHOT in (5,6,7):shot_5_6_7()
 elif SHOT in (8,9):shot_8_9()
 elif SHOT==10:shot_10()
 elif SHOT==11:shot_11()
 elif SHOT==12:shot_12()
 elif SHOT in (14,15):shot_14_15()
 elif SHOT in (17,18):shot_17_18()
 else:shot_19()
 linear();SC.frame_set(max(1,N//2));bpy.context.view_layer.update()
 SC['episode']=3;SC['shot']=SHOT;SC['stage']='BLOCKING - contact, collision and motion need visual QA';SC['time_start_s']=SPEC['start_s'];SC['time_end_s']=SPEC['end_s']
 SC['source_vehicle']='Sam-authorized buggy refit';SC['storyboard_adaptation']='Open cockpit, two seats, bent cage attack'
 # Preserve only a Blender scene artifact here; finished reusable assets are versioned separately.
 scene_path=ROOT/'assets'/VERSION/f'shot{SHOT:02d}.blend';scene_path.parent.mkdir(parents=True,exist_ok=True)
 bpy.ops.wm.save_as_mainfile(filepath=str(scene_path),compress=True)
 stats={'shot':SHOT,'name':SPEC['name'],'frames':N,'objects':len(SC.objects),'camera':SC.camera.name,'device':DEVICE,'stage':SC['stage'],'scene':str(scene_path),'warnings':[]}
 if SHOT in (4,6,7,13,16,17):stats['warnings'].append('Authored human poses/contact need reference comparison and temporal QA')
 if SHOT in (17,18):stats['warnings'].append('Two licensed car designs repeated; cabin intersections and head turns require visual QA')
 if SHOT in (3,14,15):stats['warnings'].append('Impact mechanics and left-antler split require temporal and spatial QA')
 (OUT/'scene.json').write_text(json.dumps(stats,indent=2),encoding='utf8');print('SCENE',json.dumps(stats),flush=True)
 if os.environ.get('SAVE_ONLY'):return
 frames=[int(f) for f in os.environ.get('FRAMES',str(max(1,N//2))).split(',')]
 if os.environ.get('ANIM'):frames=list(range(1,N+1))
 for frame in frames:
  if frame<1 or frame>N:raise ValueError(f'Frame outside shot: {frame}')
  target=OUT/f'f{frame:04d}.png'
  if target.exists() and not os.environ.get('FORCE'):continue
  SC.frame_set(frame);SC.render.filepath=str(target);bpy.ops.render.render(write_still=True);print('FRAME',SHOT,frame,flush=True)

if __name__=='__main__':build()
