"""Window shot. Reuse the locked bedroom and artist-made Sam rig, with a new blocking pose."""
from pathlib import Path
import sys
import math
import bpy

SITE=Path(__file__).resolve().parent
argv=sys.argv[sys.argv.index('--')+1:]
OUT=Path(argv[0]).resolve()
SCALE=float(argv[1])
run_frames=argv[2]
pass_number=int(argv[3])
source=SITE.parents[1]/'02_wrong_room'/'src'/'build_wrong_room.py'
room=source.read_text(encoding='utf-8-sig').split('\npose(91)\n',1)[0]
# Room scene definitions share the original script's material and prop assets.
ctx={'__file__':str(source),'__name__':'room_assets'}
exec(compile(room,str(source),'exec'),ctx)
sc=ctx['sc']
OUT.mkdir(parents=True,exist_ok=True)
arm=ctx['arm']
bones=ctx['bones']
maincam=ctx['maincam']
Vector,Matrix,Quaternion=ctx['Vector'],ctx['Matrix'],ctx['Quaternion']
orient_rest,reset=ctx['orient_rest'],ctx['reset']
box,line,mesh=ctx['box'],ctx['line'],ctx['mesh']
paint=ctx['paint']
def hide(*prefixes):
    for obj in sc.objects:
        if obj.name.startswith(prefixes):
            obj.hide_render=True
hide('Bright paper','Shoji cedar','Cotton futon','Folded','Support roll','Creased pillow','Phone on','Inlaid','Front sensor',
     'Volume','Sleep button','USB-C','Grille','Sleeping screen','Rounded, chamfered rail')
wood=ctx['wood']; trim=ctx['trim']; paper=ctx['washi_low']
quad=ctx['quad']; wall=ctx['wall']
if pass_number>=2:
    upper=bpy.data.objects['Above shoji']
    for v in upper.data.vertices:
        if v.co.z<2:
            v.co.z=2.43 if pass_number>=3 else 2.095
    upper.data.update()
top_z=1.65 if pass_number==1 else (2.43 if pass_number>=3 else 2.095)
for x in (-.198,1.177):
    box('Window opening cedar jamb',(x,1.124,(.36+top_z)*.5),(.038,.065,top_z-.36+.052),wood,.003)
box('Lintel and track',(.491,1.106,top_z+.013),(1.44,.083,.048),wood,.004)
box('Inner track',(.485,1.085,.391),(1.36,.060,.025),trim,.003)
# The shoji has slid aside. Keep a narrow panel to frame the left edge.
wall('Slid shoji',-.198,.065,.396,top_z-.003,1.17,paper)
for iz in range(7):
    box('Left shoji rail',(-.069,1.146,.398+iz*(top_z-.39)/6),(.26,.034,.016),wood,.001)
box('Visible shoji edge',(.071,1.146,(top_z+.39)*.5),(.026,.046,top_z-.39),wood,.001)

def dyed_weave(nt,ramp):
    N,L=nt.nodes,nt.links
    uv=N.new('ShaderNodeTexCoord')
    separate=N.new('ShaderNodeSeparateXYZ')
    L.new(uv.outputs['UV'],separate.inputs[0])
    freq=N.new('ShaderNodeMath')
    freq.operation='MULTIPLY'
    freq.inputs[1].default_value=math.tau*3.5
    L.new(separate.outputs['X'],freq.inputs[0])
    wave=N.new('ShaderNodeMath')
    wave.operation='SINE'
    L.new(freq.outputs[0],wave.inputs[0])
    remap=N.new('ShaderNodeMapRange')
    remap.inputs[1].default_value=-1
    remap.inputs[2].default_value=1
    remap.inputs[3].default_value=.26
    remap.inputs[4].default_value=.84
    L.new(wave.outputs[0],remap.inputs[0])
    dye=N.new('ShaderNodeMixRGB')
    dye.blend_type='MULTIPLY'
    dye.inputs[2].default_value=(.26,.24,.32,1)
    L.new(remap.outputs['Result'],dye.inputs[0])
    L.new(ramp.outputs[0],dye.inputs[1])
    return dye.outputs[0]
Curtain=ctx['toon']('Sheer washed indigo',ctx['color']('8c8294'),ctx['color']('c3a2a0'),tex=dyed_weave)
if pass_number>=3:
    for obj in ctx['sam']:
        if obj.type=='EMPTY':
            obj.animation_data_clear()
CurtainEdge=paint('Hem thread','62576d','e0b49b')
nu,nv=24,32
def fabric(u,v,t):
    stretch=math.sin(t*1.75-v*1.7)*.042+math.sin(t*2.1+v*2.6)*.017
    swing=(stretch+.027*math.sin(u*11-v*7+t*3))*v**1.62
    x=1.168-.275*u+swing*(.7+.3*u)
    y=1.011+.034*math.sin(u*math.tau*3.5+.23*v)+.42*swing
    z=top_z+.002-(top_z-.681)*v+.019*math.sin(u*math.tau*2+v*6)*v
    return x,y,z
grid=[fabric(i/nu,j/nv,0) for j in range(nv+1) for i in range(nu+1)]
faces=[]
for j in range(nv):
    for i in range(nu):
        q=j*(nu+1)+i
        faces.append((q,q+1,q+nu+2,q+nu+1))
curtain=mesh('Breathing curtain',grid,faces,Curtain,[(i/nu,j/nv) for j in range(nv+1) for i in range(nu+1)])
for face in curtain.data.polygons:
    face.use_smooth=True
solid=curtain.modifiers.new('Woven thickness','SOLIDIFY')
solid.thickness=.0013
hem=line('Stitched curtain edge',[grid[j*(nu+1)+nu] for j in range(nv+1)],CurtainEdge,.0021)
bottom=line('Weighted hem',grid[-nu-1:],CurtainEdge,.002)
rod=line('Curtain rod',[(.846,1.061,top_z+.03),(1.205,1.061,top_z+.03)],wood,.012)
for i in range(7):
    box('Curtain rod loop',(.90+.044*i,1.036,top_z+.01),(.011,.016,.037),CurtainEdge,.003)

def cloth_frame(t):
    for j in range(nv+1):
        for i in range(nu+1):
            curtain.data.vertices[j*(nu+1)+i].co=fabric(i/nu,j/nv,t)
    for j,p in enumerate(hem.data.splines[0].points):
        p.co=(*fabric(1,j/nv,t),1)
    for i,p in enumerate(bottom.data.splines[0].points):
        p.co=(*fabric(i/nu,1,t),1)
    curtain.data.update()

def sam_pose(f):
    # Fixed foot position. Only weight transfer through chest, neck and hair.
    for b in bones:
        reset(b)
    discover=ctx['ease'](f,14,34)
    turn=ctx['ease'](f,36,67)
    recoil=discover*(1-ctx['ease'](f,29,51))
    arm.matrix_world=Matrix.Translation(Vector((.357-.037*turn,.673-.028*recoil,-.157+.034*recoil)))@Matrix.Rotation(math.radians(166-91*turn),4,'Z')
    settle=ctx['ease'](f,9,64)
    orient_rest(bones['J_Bip_C_Spine'],(1,0,0),.019*math.sin(f*.052))
    orient_rest(bones['J_Bip_C_Chest'],(0,0,1),math.radians(-4+5*settle-13*turn))
    orient_rest(bones['J_Bip_C_Neck'],(1,0,0),math.radians(-7-11*discover+22*turn))
    orient_rest(bones['J_Bip_C_Head'],(0,0,1),math.radians(-5-26*turn))
    for obj in ctx['sam']:
        shapes=obj.data.shape_keys if obj.type=='MESH' else None
        if shapes:
            for name,value in (('Fcl_EYE_Close',.84*math.exp(-((f-49)/2.8)**2)),('Fcl_BRW_Sorrow',.48*discover)):
                block=shapes.key_blocks.get(name)
                if block:
                    block.value=value
    for i,b in enumerate(ctx['hair_bones']):
        orient_rest(b,(0,1,0),.025*math.sin(f*.131+i*.42))
    bpy.context.view_layer.update()
    if pass_number>=3:
        for side,sign in (('L',1),('R',-1)):
            thigh,shin,foot=(bones['J_Bip_'+side+'_'+n] for n in ('UpperLeg','LowerLeg','Foot'))
            ctx['solve_chain'](thigh,shin,Vector((.363+.111*sign,.598,.112)),Vector((-.15*sign,.92,-.08)))
            ctx['aim'](foot,arm.matrix_world@foot.head+Vector((.034,.143,-.068)))
    if pass_number>=2:
        for side,sign in (('L',1),('R',-1)):
            upper=bones['J_Bip_'+side+'_UpperArm']
            lower=bones['J_Bip_'+side+'_LowerArm']
            hand=bones['J_Bip_'+side+'_Hand']
            axes=arm.matrix_world.to_3x3()
            for bone,off in ((upper,(.070*sign,-.016,-.231)),(lower,(.012*sign,-.068,-.212)),(hand,(.005*sign,-.021,-.092))):
                start=arm.matrix_world@bone.head
                ctx['aim'](bone,start+axes@Vector(off))

key=ctx['key']; fill=ctx['fill']; lantern=ctx['lantern']
key.data.energy=4.8
fill.data.energy=.21
lantern.location=(.78,.79,1.48)
lantern.data.energy=71
lantern.rotation_euler=(Vector((.20,.65,1.52))-lantern.location).to_track_quat('-Z','Y').to_euler()
sc.camera=maincam
maincam.data.lens=40 if pass_number==1 else 43
frames=range(1,97) if run_frames in ('all','resume') else [int(s) for s in run_frames.split(',')]
for f in frames:
    sc.frame_set(f)
    k=ctx['ease'](f,1,96)
    sam_pose(f-(f-1)%2)
    cloth_frame((f-(f-1)%2-1)/24)
    if pass_number==1:
        start,end=(.408,-.824,1.50),(.436,-.686,1.50)
        aim=Vector((.542,1.139,1.335))
    else:
        start,end=(.336,-.980,1.40),(.389,-.811,1.432)
        aim=Vector((.559,1.139,1.365))
    if pass_number>=3:
        start,end=(.394,-1.086,1.532),(.432,-.956,1.556)
        aim=Vector((.631,1.139,1.668))
        maincam.data.lens=42
    ctx['look'](maincam,Vector(start).lerp(Vector(end),k),aim)
    path=OUT/f'cel_{f:03d}.png'
    if run_frames!='resume' or not path.exists():
        sc.render.filepath=str(path)
        bpy.ops.render.render(write_still=True)


