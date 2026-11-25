"""Kiriyama's street, where the sweepers and the loudspeaker horns move in sequence."""
import math
import random

def between(name,a,b,r,material):
    a,b=Vector(a),Vector(b)
    return cyl(name,((a+b)*.5),r,(b-a).length,material,(b-a),verts=12)

def merge_static_street():
    # Keep every roof seam but collapse the many static draw calls.
    groups={}
    bpy.context.view_layer.update()
    for o in list(sc.objects):
        if o.parent or o.type!='MESH' or o.data.uv_layers or len(o.data.materials)!=1:
            continue
        md=tuple(o.modifiers)
        if any(m.type!='BEVEL' for m in md) or len(md)>1:
            continue
        bevel=md[0].width if md else 0
        key=(o.data.materials[0],round(bevel,6))
        groups.setdefault(key,[]).append(o)
    for (material,bevel),obs in groups.items():
        if len(obs)<3:continue
        verts,faces,smooth=[],[],[]
        for o in obs:
            index=len(verts)
            verts.extend(tuple(o.matrix_world@v.co) for v in o.data.vertices)
            faces.extend(tuple(index+i for i in face.vertices) for face in o.data.polygons)
            smooth.extend(face.use_smooth for face in o.data.polygons)
        mesh=form('Batched '+material.name,verts,faces,material)
        for polygon,s in zip(mesh.data.polygons,smooth):
            polygon.use_smooth=s
        if bevel:
            m=mesh.modifiers.new('Merged rounded edges','BEVEL')
            m.width=bevel
            m.segments=3
        for o in obs:
            bpy.data.objects.remove(o,do_unlink=True)

def street(dusk=False):
    rng=random.Random(144)
    wall=[paint('Merchant plaster'+str(i),c,d,'ffd1a1') for i,(c,d) in enumerate([
      ('615362','c0a48c'),('615560','baab97'),('594656','b59177'),('686071','a99c9d')])]
    wood=paint('Aged window frames','37303e','806255','e8a773')
    trim=paint('Eaves boards','312936','725249','dc9a70')
    steel=paint('Painted iron traces','3f3d53','777687')
    tile=paint('Slate kawara tiles','393547','6c6576','ac8293')
    tile_light=paint('Fascia ridge highlight','544155','97808c')
    dark=paint('Window shadow','252536','534d61')
    glass=paint('Frost glass','45465a','9b9c99','d7b7a0')
    concrete=paint('Worn pavement','696075','b9a492')
    road=mapped('Asphalt and pebble patches',ASSETS/'asphalt.png','aaa0b3','eddbbe')
    stripe=paint('Worn road paint','7c7280','cbbda7')
    threads=flat('Utility wire charcoal','#3e3447')
    grass=[paint('Verge grass '+str(i),sh,lit) for i,(sh,lit) in enumerate((('414b4c','827e5d'),('36484a','626a54'),('52645a','a1966b')))]
    card('Street asphalt',[(-3.65,-8,-.03),(3.65,-8,-.03),(3.65,38,-.03),(-3.65,38,-.03)],road)
    for side in (-1,1):
        box('Raised gutter',(side*1.83,12,.007),(.46,42,.069),concrete,.012)
        box('Curb top',(side*1.615,12,.025),(.117,42,.063),concrete,.011)
        box('Sidewalk',(side*2.26,12,.011),(.53,42,.046),concrete,.006)
        for j in range(12):
            y=-5+j*3.55
            box('Drain grate',(side*1.736,y,.046),(.146,.35,.018),steel,.005)
            for k in range(6):
                box('Drain slit',(side*1.736,y-.14+k*.056,.057),(.114,.014,.002),dark)
        for i in range(35):
            x=side*(1.90+rng.uniform(.00,.071))
            y=rng.uniform(-6,30)
            z=rng.uniform(.046,.121)
            form('Irregular grass tuft',[(x-.016,y,.04),(x-.012,y+.016,z*.90),(x,y+.024,.04),
                 (x+.008,y+.041,z),(x+.019,y+.065,.039)],[(0,1,2,3,4)],rng.choice(grass))
    for j in range(14):
        y=-6+j*2.9
        box('Broken street centre strip',(.026,y,-.027),(.048,1.15,.005),stripe,.0014)
    lid=cyl('Street manhole',(.72,1.11,-.024),.207,.012,steel)
    cyl('Manhole inset',(.72,1.11,-.015),.172,.008,dark)
    for j in range(9):
        a=j*math.tau/9
        box('Raised manhole tooth',(.72+.131*math.cos(a),1.11+.132*math.sin(a),-.009),(.05,.024,.005),steel,.002)

    def house(side,y,n):
        front=side*2.61
        depth=rng.uniform(1.88,2.12)
        mid=front+side*depth*.5
        width=rng.uniform(2.63,3.43)
        height=rng.uniform(2.26,2.87)
        box('Merchant house', (mid,y,height*.5),(depth,width,height),wall[n%4],.024)
        face=front-side*.024
        for z in (.20,.43,1.88,height-.18):
            box('Tapered wood belt',(face,y,z),(.07,width+.053,.126 if z>1 else .078),wood,.0028)
        for a in (-1,1):
            box('Cedar facade post',(face,y+a*(width*.5-.04),height*.47),(.102,.139,height*.94),trim,.004)
        for j in (-1,1):
            wy=y+j*.63
            z=1.21+(n%3)*.085
            box('Window depth',(face-side*.049,wy,z),(.067,.85,.92),dark,.009)
            box('Window glazing',(face-side*.086,wy,z),(.019,.77,.83),glass,.004)
            for row in (0,1,2):
                box('Shutter rail',(face-side*.113,wy,z-.275+row*.275),(.044,.8,.044),wood,.001)
            for col in range(4):
                box('Wooden lattice',(face-side*.12,wy-.326+col*.217,z),(.041,.036,.88),wood,.001)
            box('Sill',(face-side*.126,wy,z-.46),(.215,.948,.059),wood,.005)
        between('Drain pipe',(face-side*.11,y+width*.42,.122),(face-side*.11,y+width*.42,height-.085),.022,steel)
        for a in (-1,1):
            edge_x=mid+a*(depth*.5+.24)
            y0,y1=y-width*.5-.24,y+width*.5+.24
            roof_z=height+.11
            peak=height+.63
            pts=[(edge_x,y0,roof_z),(edge_x,y1,roof_z),(mid,y1,peak),(mid,y0,peak)]
            card('Sloped tiled roof',pts,tile)
            for j in range(13):
                yy=y0+(y1-y0)*j/12
                between('Kawara vertical seam',(edge_x,yy,roof_z+.022),(mid,yy,peak+.024),.022,tile_light)
            for j in range(1,7):
                u=j/7
                x=edge_x+(mid-edge_x)*u
                z=roof_z+(peak-roof_z)*u+.026
                between('Overlapping kawara row',(x,y0,z),(x,y1,z),.015,tile)
            between('Gutter facade',(edge_x,y0,roof_z),(edge_x,y1,roof_z),.044,trim)
        between('Roof ridge',(mid,y-width*.5-.24,height+.64),(mid,y+width*.5+.24,height+.64),.053,tile_light)
        if n in (0,4) and side==-1:
            board=mapped('Sideways Kiriyama merchant sign',ASSETS/'shop_sign.png','bdb0ba','fff2d7')
            box('Mounted shop fascia',(face+.11,y,2.02),(.117,2.10,.52),wood,.014)
            dy=.984
            xx=face+.174
            card('Painted reversed shop lettering',[(xx,y-dy,1.805),(xx,y+dy,1.805),(xx,y+dy,2.233),(xx,y-dy,2.233)],board)
        if n%3==1:
            ar=box('Period air conditioner unit',(face-side*.19,y+.907,.94),(.26,.58,.37),concrete,.012)
            for j in range(6):
                box('Air grille',(face-side*.337,y+.907,.806+j*.045),(.017,.449,.009),steel,.002)

    for n,y in enumerate((-2.6,.84,4.32,7.78,11.17,14.60,18.19,21.73)):
        for side in (-1,1):
            house(side,y+(n%3)*(.12*side),n)
    # Mountains and sky share the already-painted depth motifs in the established window shot.
    plate=ASSETS/('street_dusk.png' if dusk else 'street_dawn.png')
    bmat,_=mapped('Distant painted Kiriyama valley',plate)
    card('Far valley plane',[(-38,45,-11),(38,45,-11),(38,45,31),(-38,45,31)],bmat)
    side_points=[(-38,y,z) for z in (-11,34,150) for y in (63,-176)]
    form('Western wrap and overheight sky',side_points,[(0,1,3,2),(2,3,5,4)],bmat,
         [(0,0),(1,0),(0,1),(1,1),(0,1),(1,1)])

    horn_m=paint('Cast blue-grey loudspeaker','5b526d','9a7d85','ffb88c')
    inner=flat('Bell cavity shadow','#302938')
    rusty=paint('Concrete utility poles','625366','a3898a','dfac92')
    horns=[]
    profile=[(.0,.048),(.054,.045),(.119,.051),(.188,.074),(.227,.110),(.258,.141),(.277,.148),(.279,.141),(.265,.132)]
    for j,y in enumerate((-1.49,.74,3.34,6.09,9.24,12.6,15.45,19.1)):
        flip=1 if j%2==0 else -1
        x=flip*1.52
        pole_h=(2.52 if j==0 else 3.18)+.15*math.sin(j)
        cyl('Concrete chime pole',(x,y,pole_h/2),.062,pole_h,rusty)
        between('Two-way horn crossbar',(x-.20,y,pole_h-.13),(x+.20,y,pole_h-.13),.023,steel)
        for side in (-1,0,1):
            z=pole_h-.078+.042*(side==0)
            ax=x+side*.157
            root=pivot('Spinning loudspeaker bracket',(ax,y,z))
            ob=mesh_obj('Cast-metal horn bell',lathe(profile,35,True),horn_m,root,.0030)
            ob.location=(0,0,0)
            bell=cyl('Horn throat',(0,.267,0),.125,.012,inner,(0,1,0),32)
            bell.parent=root
            bell.location=(0,.269,0)
            if side!=0:
                torus_at=between('Horn anchor',(ax,y,z-.056),(ax,y,z-.006),.025,steel)
            horns.append((root,j,side,flip))
    for k in range(3):
        points=[]
        for j in range(42):
            q=j/41
            y=-6+q*37
            x=(-1.68 if k<2 else 1.59)+.11*k-.09*math.sin(q*9)
            z=3.60+k*.095-.17*math.sin(q*math.pi*4)**2
            points.append((x,y,z))
        curve('Sagging overhead power cable',points,.007,threads)
    for k in range(2):
        pts=[(-2.8+j*.144,4.23+k*4.65,3.94-.18*math.sin(math.pi*j/39)) for j in range(40)]
        curve('Crossing service line',pts,.005,threads)
    lamp('Late brass sky' if dusk else 'Low dawn',4.85,'#ffb27c' if dusk else '#ffe2bb',(-.52,.25,.53))
    lamp('Violet street bounce',.35 if dusk else .43,'#cbd0f5',(.48,-.63,.65))
    merge_static_street()
    return horns

class Broom:
    def __init__(self):
        shaft=paint('Sweeping bamboo','745148','b99467','e2b486')
        straw=paint('Dry straw broom','6b5052','aa815e','d6a679')
        binding=paint('Waxed binding','3f3845','87695b')
        self.root=pivot('Broom local axes',(0,0,0))
        ob=cyl('Bamboo handle',(0,0,.53),.012,1.06,shaft)
        ob.parent=self.root
        ob.location=(0,0,.53)
        for i in range(17):
            a=i/16-.5
            ob=curve('Broom straw cluster',[(a*.037,0,.233),(a*.096,.011,.097),(a*.205,.009,-.008*math.sin(i))],.008,straw)
            ob.parent=self.root
        for zz in (.188,.207,.225):
            ob=cyl('Broom cloth binding',(0,0,zz),.032,.023,binding,verts=16)
            ob.parent=self.root
            ob.location=(0,0,zz)
    def pose(self,ground,top):
        d=Vector(top)-Vector(ground)
        self.root.location=ground
        self.root.rotation_euler=d.to_track_quat('Z','Y').to_euler()
        self.root.scale.z=d.length/1.06
        return Vector(ground),d

def townspeople():
    layout=[('grandma',-.84,2.158),('shopkeeper',.92,2.77),('kid_girl',-.96,4.15),('kid_boy',.91,4.69)]
    return [(Actor(asset),x,y,Broom()) for asset,x,y in layout]

def sweep(person,base,broom,n,delay=0,lookat=False):
    x,y=base
    stopped=39<=n<=57 and not lookat
    f=(39 if stopped else (n-18 if n>57 and not lookat else n))
    phase=(f+delay)*.27
    sinus=math.sin(phase)
    a=.12 if x<0 else -.13
    if lookat:a=.04+.10*math.sin(n*.10)
    person.pose((x,y,-.005),a)
    person.arms_free(.042)
    person.primary(person.b('Spine'),(1,0,0),(.020+.024*sinus) if lookat else (.105+.042*sinus))
    person.primary(person.b('Head'),(1,0,0),-.10 if lookat else .17)
    person.primary(person.b('Head'),(0,0,1),.075*math.sin(n*.058) if lookat else a)
    z=person.world('UpperArm','R').z
    tip=(x+.40*sinus+.06,y-.42,.043)
    top=(x+.105-.105*sinus,y-.235,z-.13)
    start,d=broom.pose(tip,top)
    for side,sign,v in [('L',1,.81),('R',-1,.665)]:
        p=start+d*v
        p.x+=.014*sign
        forearm=Vector((.025*sign,-.049,-.073))
        person.reach(side,p,(.82*sign,.31,-.46),forearm)
        for digit,amount in (('Index',.52),('Middle',.63),('Ring',.67),('Little',.76)):
            for segment in (1,2,3):
                bone=person.bones.get(f'J_Bip_{side}_{digit}{segment}')
                if bone is not None:
                    bone.rotation_quaternion=Quaternion((0,0,1),-sign*amount)
    person.blink(n,(24,89))

def sprint(actor,n,f=0):
    speed=2.60
    origin=-1.41
    y=origin+(n-1)*speed/24
    x=-.28+.12*math.sin((n-1)*.033)
    actor.pose((x,y,.003+.035*abs(math.sin(n*math.pi/8))),math.pi+.027)
    actor.arms_free(.049)
    beat=(n-1)*math.tau/16
    actor.primary(actor.b('Hips'),(0,0,1),.105*math.sin(beat-.4))
    actor.primary(actor.b('Spine'),(1,0,0),.307+.061*math.sin(beat*2))
    actor.primary(actor.b('UpperChest'),(0,0,1),-.133*math.sin(beat))
    actor.primary(actor.b('Head'),(0,0,1),-.31*interval(n,24,40)*(1-interval(n,52,70)))
    actor.blink(n,(40,))
    for side,sign,offset in [('L',1,0),('R',-1,8)]:
        cyc=(n-1+offset)/16
        j=int(cyc)
        q=cyc-j
        start=origin+(j*16-offset+2.8)*speed/24
        swing=clamp((q-.45)/.55)
        ty=start+speed*16/24*ease(swing)
        lift=.265*math.sin(math.pi*swing)**1.16
        plant_frame=j*16-offset+2.8
        plant_x=-.28+.12*math.sin(plant_frame*.033)
        next_x=-.28+.12*math.sin((plant_frame+16)*.033)
        foot_x=plant_x+(next_x-plant_x)*ease(swing)
        ankle=Vector((foot_x-sign*.105,ty,.087+lift))
        actor.chain(actor.b('UpperLeg',side),actor.b('LowerLeg',side),ankle,(.06*sign,1,.15))
        push=interval(q,.24,.43)*(1-interval(q,.46,.67))
        actor.aim(actor.b('Foot',side),actor.world('Foot',side)+Vector((0,.158,-.034-.126*push+.062*swing)))
        forward=-.32*math.sin(math.tau*cyc+.19)
        h=actor.world('UpperArm',side)
        target=h+Vector((.09*(-sign),forward,-.301+.088*math.sin(math.tau*cyc)))
        actor.reach(side,target,(-.4*sign,-.98,-.17),(0,.058,-.08))
    actor.move_hair(n,.042)

def shot_05():
    horns=street(False)
    cast=townspeople()
    sam=Actor('sam')
    def frame(f):
        n=f-(f-1)%2
        for root,j,side,flip in horns:root.rotation_euler.z=flip*.91+side*.99
        for i,(person,x,y,broom) in enumerate(cast):
            sweep(person,(x,y),broom,n,12 if i==0 else 0,i==0)
        sprint(sam,n)
        k=interval(f,1,96)
        if f<=42:
            look((.205-.40*k,-3.22+.59*k,1.43-.19*k),(.05-.15*k,2.45+1.25*k,1.28),37.5)
        else:
            follow=interval(f,43,96)
            y=-1.41+(n-1)*2.60/24
            look((1.19-.13*follow,y+1.74,1.45+.05*follow),(-.28,y-.10,1.34),36-3*follow)
    return 96,frame

def shot_12():
    horns=street(True)
    actors=[(Actor(n),x,y) for n,x,y in (('grandma',-.92,2.15),('shopkeeper',.95,3.00),('kid_girl',-.97,5.13),('kid_boy',.95,6.31))]
    def frame(f):
        n=f-(f-1)%2
        k=interval(f,1,120)
        if f<=60:
            part=interval(f,1,60)
            look((.541+.045*part,-2.132+.31*part,1.89),(1.11,2.20,2.29),42)
        else:
            part=interval(f,61,120)
            look((-.02-.07*part,-2.17+.24*part,1.36),(.063,4.10,1.65),42)
        for root,j,side,flip in horns:
            delay=10+j*4+max(0,side)*3
            p=clamp((n-delay)/20)
            overshoot=.13*math.sin(3*math.pi*p)*math.exp(-2*p) if 0<p<1 else 0
            root.rotation_euler.z=(flip*.91+side*.99)*(1-ease(p))+.13*ease(p)+overshoot
            root.rotation_euler.x=.18*ease(p)+overshoot*.45
        for i,(a,x,y) in enumerate(actors):
            turn=interval(n,65+i*2,91+i*2)
            lift=math.sin(math.pi*turn)
            a.pose((x+.13*lift,y-.12*turn,-.01+.026*lift),.48+turn*(math.pi-.39))
            a.arms_free(.035+.074*lift)
            a.blink(n,(63+i*3,101))
            for side,sign in (('L',1),('R',-1)):
                leg=a.b('UpperLeg',side)
                a.primary(leg,(1,0,0),-.13*sign*math.sin(math.tau*turn))
                a.primary(a.b('LowerLeg',side),(1,0,0),.19*max(0,sign*math.sin(math.tau*turn)))
            a.primary(a.b('Neck'),(0,0,1),.28*(interval(n,53+i*3,65+i*3)-turn))
            a.primary(a.b('Spine'),(1,0,0),.07*(1-turn))
    return 120,frame

