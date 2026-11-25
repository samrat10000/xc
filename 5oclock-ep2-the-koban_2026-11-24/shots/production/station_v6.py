"""Shared koban architecture and close shots, with the actual notebook and recurring doors."""
import math
import random
from types import SimpleNamespace

def station_materials():
    return SimpleNamespace(
       plaster=mapped('Dusty police box paint',ASSETS/'station_plaster.png','958ca9','eee0bb'),
       wood=mapped('Desk wood',ASSETS/'counter.png','8d809a','ffe3bd'),
       lino=mapped('Rubber floor',ASSETS/'rubber_lino.png','8c86a1','eed2b1'),
       oak=paint('Lacquered cedar','493547','957661','e8ae82'),
       dark=paint('Station frame','2a263a','60566a'),
       metal=paint('Brass and metal edges','5c485d','aa897b','f3c68a'),
       leather=paint('Notebook binding','4f3c4a','966957','c29d7e'),
       paper=paint('Page cut edges','89725f','ddbc87'),
       lamp=paint('Rusty shade','4c444e','80716a','ffc58e'),
       glow=flat('Desk lamp bulb','#fbdcb0',1.41),
       pale=flat('Frosted golden light','#f3b98c'),
       black=flat('End blackout','#000000'),
    )

def translucent(name,texture,opacity,glow=1):
    mat,tex=mapped(name,texture)
    mat.surface_render_method='BLENDED'
    nt=mat.node_tree
    n,l=nt.nodes,nt.links
    em=n.get('Emission')
    em.inputs[1].default_value=glow
    mix=n.new('ShaderNodeMixShader')
    mix.inputs[0].default_value=opacity
    l.new(n.new('ShaderNodeBsdfTransparent').outputs[0],mix.inputs[1])
    l.new(em.outputs[0],mix.inputs[2])
    l.new(mix.outputs[0],n.get('Material Output').inputs[0])
    return mat

def architecture(mode='desk'):
    a=station_materials()
    card('Peeling floor',[(-1.85,-2.85,0),(1.85,-2.85,0),(1.85,1.44,0),(-1.85,1.44,0)],a.lino)
    card('Left plaster', [(-1.49,-1.23,0),(-1.49,1.25,0),(-1.49,1.25,2.74),(-1.49,-1.23,2.74)],a.plaster)
    card('Right plaster',[(1.49,1.25,0),(1.49,-1.23,0),(1.49,-1.23,2.74),(1.49,1.25,2.74)],a.plaster)
    for x in (-1.44,1.44):
        box('Lower painted board',(x,.0,.19),(.072,2.49,.333),a.oak,.005)
    xl,xr,lo,hi=.07,1.28,.88,2.22
    def wall(x0,x1,z0,z1):
        return card('Back plaster panel',[(x0,1.225,z0),(x1,1.225,z0),(x1,1.225,z1),(x0,1.225,z1)],a.plaster)
    wall(-1.5,xl,0,2.75)
    wall(xr,1.50,0,2.75)
    wall(xl,xr,0,lo)
    wall(xl,xr,hi,2.75)
    for x in (xl,xr):
        box('Back window jamb',(x,1.196,(lo+hi)*.5),(.043,.088,hi-lo+.11),a.oak,.005)
    for z in (lo,hi):
        box('Back window rail',((xl+xr)*.5,1.183,z),(xr-xl+.065,.18,.037),a.oak,.004)
    box('Back window apron',((xl+xr)*.5,1.139,lo-.069),(xr-xl+.080,.068,.106),a.dark,.004)
    if mode!='mirror':
        plate,tex=mapped('Air outside station',ASSETS/'street_dawn.png')
        card('Exterior behind rear window',[(xl-.12,1.48,lo-.16),(xr+.12,1.48,lo-.16),(xr+.12,1.48,hi+.22),(xl-.12,1.48,hi+.22)],plate)
        for x in (xl+.38,xl+.78):
            box('Back window mullion',(x,1.202,(lo+hi)*.5),(.024,.067,hi-lo),a.oak,.003)
        box('Back window cross rail',((xl+xr)*.5,1.191,1.48),(xr-xl,.054,.022),a.oak,.003)
    date=mapped('Dusty calendar page',ASSETS/'calendar.png','af9eaa','f8e5c0')
    box('Calendar holder',(-.222,1.191,1.61),(.409,.035,.53),a.dark,.005)
    card('Police calendar 1964',[(-.411,1.166,1.36),(-.032,1.166,1.36),(-.032,1.166,1.86),(-.411,1.166,1.86)],date)
    box('Calendar clip',(-.224,1.146,1.844),(.14,.013,.034),a.metal,.003)
    for x,z,w,h in ((-1.24,1.85,.285,.221),(-1.19,1.49,.196,.14)):
        leaf=paint('Station paperwork','a18d78','e3cc9e')
        box('Pinned notice',(x,1.201,z),(w,.014,h),leaf,.001)
        for row in range(5):
            box('Written notice line',(x,1.191,z+.063-row*.032),(w*.63,.003,.006),a.oak)
    # Weathered front with a single full-height door and frosted fixed transom.
    for x,w in ((-1.09,.87),(.98,1.05)):
        box('Entry stucco pier',(x,-1.30,1.314),(w,.185,2.66),a.plaster,.007)
    box('Front header',(-.047,-1.306,2.327),(1.35,.206,.587),a.plaster,.005)
    fascia=mapped('Reversed police station lettering',ASSETS/'koban_sign.png','bfafb9','fff3d8')
    box('Hung koban sign',(-.045,-1.435,2.20),(1.45,.074,.377),a.dark,.006)
    card('Kiriyama police box sign',[(-.735,-1.477,2.035),(.645,-1.477,2.035),(.645,-1.477,2.367),(-.735,-1.477,2.367)],fascia)
    cyl('Old brass wall button',(-.849,-1.405,1.43),.023,.015,a.metal,(0,-1,0))
    box('Threshold',(-.091,-1.275,.048),(1.05,.24,.079),a.dark,.010)
    for x in (-.655,.445):
        box('Entry door jamb',(x,-1.222,1.023),(.059,.092,2.034),a.oak,.006)
    box('Entry door overhead track',(-.106,-1.216,2.013),(1.14,.113,.061),a.oak,.008)
    return a

def door_set(a,trans=True):
    door=pivot('Door on left hinge',(-.608,-1.216,.067))
    pane=translucent('Pitted frosted entry glass',ASSETS/'washi_pane.png',.76,1.02) if trans else a.pale
    for x in (.049,.987):
        o=box('Door side stile',(-.608+x,-1.216,1.03),(.095,.051,1.927),a.oak,.008)
        attach(o,door)
    for z in (.11,.60,1.941):
        o=box('Broad door rail',(-.095,-1.216,z),(1.02,.052,.086),a.oak,.008)
        attach(o,door)
    s=box('Solid cedar lower panel',(-.098,-1.217,.368),(.928,.045,.507),a.dark,.010)
    attach(s,door)
    p=card('Frosted entry glass',[(-.55,-1.218,.649),(.333,-1.218,.649),(.333,-1.218,1.903),(-.55,-1.218,1.903)],pane)
    attach(p,door)
    knob=cyl('Tarnished door knob',(.283,-1.158,.972),.033,.05,a.metal,(0,1,0))
    attach(knob,door)
    return door,knob

def desk(a,y=.38,z=.836):
    box('Desk top',(0,y,z-.040),(1.415,.776,.08),a.oak,.013)
    card('Desk worn working surface',[(-.692,y-.365,z+.0008),(.692,y-.365,z+.0008),(.692,y+.365,z+.0008),(-.692,y+.365,z+.0008)],a.wood)
    for x in (-.618,.618):
        for yy in (y-.342,y+.343):
            box('Tapered desk leg',(x,yy,.389),(.086,.089,.78),a.oak,.007)
    box('Front drawer face',(0,y-.36,.701),(1.261,.11,.216),a.dark,.013)
    box('Brass drawer pull',(0,y-.436,.727),(.148,.045,.026),a.metal,.005)
    for x,yy in ((-.565,.67),(-.498,.652),(-.436,.642)):
        box('Battered paper file',(x,yy,z+.015),(.208,.170,.025),a.paper,.003)
    return z+.004

def book(a,centre=(0,.325,.844),write=False):
    x,y,z=centre
    W,H=.173,.235
    cover=box('Leather cover',(x,y,z-.004),(W*2+.027,H+.024,.020),a.leather,.005)
    # Expose the dark binding between the two stacks of paper.
    for sign in (-1,1):
        box('Notebook page stack',(x+sign*W*.502,y,z+.009),(W-.009,H,.016),a.paper,.0026)
        for k in range(4):
            curve('Individual deckled edge',[(x+sign*.010,y-H*.5-.001,z+.003+k*.003),
                 (x+sign*.080,y-H*.5+.0006,z+.003+k*.003),
                 (x+sign*(W-.001),y-H*.5+.001,z+.003+k*.003)],.0004,a.leather)
    left=mapped('Hand-lettered rules one through three',ASSETS/'v6_book'/'book_left.png','c1abae','fff4d8')
    rightpath=ASSETS/'v6_book'/'book_right.png'
    right=mapped('Hand-lettered rules four through eight',rightpath,'c1abae','fff4d8')
    for sign,mat in ((-1,left),(1,right)):
        x0,x1=(x-W,x-.003) if sign<0 else (x+.003,x+W)
        card('Handwritten notebook leaf',[(x0,y-H*.5,z+.018),(x1,y-H*.5,z+.018),(x1,y+H*.5,z+.018),(x0,y+H*.5,z+.018)],mat)
    curve('Thread cotton spine',[(x,y-H*.5,z+.018),(x,y,z+.015),(x,y+H*.5,z+.019)],.00155,a.leather)
    ring=cyl('Brass chain anchor rivet',(x+W+.011,y+H*.39,z+.016),.011,.007,a.metal)
    return SimpleNamespace(x=x,y=y,z=z,W=W,H=H,tex=next(n for n in right.node_tree.nodes if n.type=='TEX_IMAGE'))

def lamp_chain(a,table,b):
    x,y=.465,.560
    cyl('Desk lamp foot',(x,y,table+.014),.089,.021,a.lamp)
    curve('Bent desk lamp stem',[(x,y,table+.018),(x+.044,y,table+.216),(x+.026,y-.044,table+.288),(x-.064,y-.094,table+.318)],.016,a.metal)
    hood=mesh_obj('Spun metal lamp',lathe([(0,.097),(.014,.096),(.047,.068),(.066,.044),(.072,.044)],42,False),a.lamp,line=.0018)
    hood.rotation_euler.x=math.pi/2
    hood.location=(x-.069,y-.104,table+.268)
    lampbulb=cyl('Pale working shade',(x-.069,y-.104,table+.272),.077,.016,a.glow)
    beam=area('Desk lamp beam',(x-.069,y-.104,table+.246),(b.x-.019,b.y,table),41,'#ffc081',.175)
    loops=[]
    for i in range(16):
        o=curve('Interlocking chain link',[(math.cos(j*math.tau/20)*.011,math.sin(j*math.tau/20)*.0068,0) for j in range(21)],.0015,a.metal)
        o.rotation_euler.x=math.pi/2*(i%2)
        loops.append(o)
    def tick(f):
        flick=.56+.38*math.sin(f*.433)**2 if f in range(56,73) or f in range(92,102) else .92+.06*math.sin(f*.117)
        beam.data.energy=41*flick
        for i,o in enumerate(loops):
            u=i/(len(loops)-1)
            o.location=(b.x+b.W+.011+.32*u,b.y+b.H*.39-.14*u+.029*math.sin(math.pi*u)*math.sin(f*.12),
                        table+.017-u*.015+.046*u**4)
            o.rotation_euler.z=-.44+.27*math.sin(f*.11+u)*math.sin(math.pi*u)
    return tick

def shot_06():
    a=architecture('desk')
    z=desk(a)
    b=book(a,(0,.335,z))
    lampfx=lamp_chain(a,z,b)
    d,knob=door_set(a)
    d.rotation_euler.z=.96
    sam=Actor('sam')
    lamp('Sepia morning wash',3.44,'#fbd6a5',(-.47,-.64,.58))
    lamp('Deep room fill',.28,'#c4bee5',(.52,.47,.57))
    def frame(f):
        n=f-(f-1)%2
        lampfx(n)
        outside=f<=35
        sam.visible(True)
        for child in d.children:
            child.hide_render=not outside
        if outside:
            q=interval(n,1,35)
            sam.pose((-.245,-2.74+1.44*q,-.008),math.pi)
            sam.arms_free(.039)
            sam.primary(sam.b('Spine'),(1,0,0),.13)
            sam.primary(sam.b('UpperLeg','R'),(1,0,0),.44*math.sin(n*.38))
            sam.primary(sam.b('UpperLeg','L'),(1,0,0),-.44*math.sin(n*.38))
            look((.375,-3.72+.38*q,1.52),(-.112,-1.261,1.55),41)
        else:
            q=interval(f,36,112)
            approach=interval(n,38,57)
            notice=interval(n,60,82)
            sam.pose((-.375+.18*approach,.127-.11*approach,-.043),1.44+.42*approach-.45*notice)
            sam.arms_free(.04)
            sam.primary(sam.b('Spine'),(1,0,0),.08+.30*notice)
            sam.primary(sam.b('Head'),(1,0,0),.06+.31*notice)
            sam.blink(n,(63,86))
            for key in sam.brow_keys:
                key.value=.26+.31*notice
            look((.530+.062*q,-.93+.18*q,1.52-.10*q),(-.187,.395,1.274-.061*q),39)
    return 120,frame

def animated_leaf(a,b):
    mat=mapped('Leaf lifted in the notebook',ASSETS/'v6_book'/'book_leaf.png','bca4a9','fff1d3')
    nt=mat.node_tree
    N,L=nt.nodes,nt.links
    emission=next(n for n in N if n.type=='EMISSION')
    front=emission.inputs[0].links[0].from_socket
    tex=N.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(ASSETS/'v6_book'/'book_verso.png'),check_existing=True)
    front_tex=next(n for n in N if n.type=='TEX_IMAGE' and n!=tex)
    front_img=front_tex.image
    geometry=N.new('ShaderNodeNewGeometry')
    blend=N.new('ShaderNodeMixRGB')
    L.new(geometry.outputs['Backfacing'],blend.inputs[0])
    L.new(front,blend.inputs[1])
    L.new(tex.outputs['Color'],blend.inputs[2])
    L.new(blend.outputs[0],emission.inputs[0])
    rows,cols=13,20
    v=[(0,0,0) for i in range((rows+1)*(cols+1))]
    uv=[(i/cols,j/rows) for j in range(rows+1) for i in range(cols+1)]
    faces=[]
    for j in range(rows):
        for i in range(cols):
            q=j*(cols+1)+i
            faces.append((q,q+1,q+cols+2,q+cols+1))
    m=form('Hinged paper with curl and flex',v,faces,mat,uv)
    sm=m.modifiers.new('Paper caliper','SOLIDIFY')
    sm.thickness=.00033
    for face in m.data.polygons:face.use_smooth=True
    def pose(f):
        theta=interval(f,30,83)*math.pi
        front_tex.image=tex.image if theta>math.pi*.514 else front_img
        for j in range(rows+1):
            r=j/rows
            for i in range(cols+1):
                s=i/cols
                bend=math.sin(s*math.pi)*math.sin(theta)*.026
                edge=math.sin(r*math.pi)*.009*math.sin(theta)*s
                m.data.vertices[j*(cols+1)+i].co=(b.x+math.cos(theta)*b.W*s,
                           b.y+(r-.5)*b.H+.011*math.sin(theta)*s,
                           b.z+.021+math.sin(theta)*b.W*s*.76+bend+edge)
        m.data.update()
        return Vector((b.x+math.cos(theta)*b.W*.975,b.y-b.H*.36+.011*math.sin(theta),
                       b.z+.021+math.sin(theta)*b.W*.975*.76+.006))
    return pose

def isolated_hand():
    actor=Actor('sam')
    for o in actor.objects:
        if o.type!='MESH' or not (o.name.startswith('Body') or o.name.startswith('Hoodie_Sleeves')):
            if o.type in ('MESH','CURVE'):
                o.hide_render=True
            continue
        groups={vg.index for vg in o.vertex_groups if vg.name.startswith(('J_Bip_R_Hand','J_Bip_R_Thumb','J_Bip_R_Index','J_Bip_R_Middle','J_Bip_R_Ring','J_Bip_R_Little','J_Bip_R_LowerArm','J_Sec_R_LowerArm','J_Bip_R_UpperArm','J_Sec_R_UpperArm','J_Bip_R_Shoulder'))}
        used={v.index for v in o.data.vertices if any(g.group in groups and g.weight>.38 for g in v.groups)}
        bm=bmesh.new()
        bm.from_mesh(o.data)
        bmesh.ops.delete(bm,geom=[f for f in bm.faces if sum(x.index in used for x in f.verts)<len(f.verts)*.68],context='FACES')
        bm.to_mesh(o.data)
        bm.free()
    return actor

def shot_07():
    # Drive the close insert at practical model scale.
    a=station_materials()
    z=desk(a,.32,.84)
    b=book(a,(0,.30,z))
    hinge=animated_leaf(a,b)
    hand=isolated_hand()
    reader=Actor('sam')
    backdrop=mapped('Rough koban walls',ASSETS/'station_plaster.png','85717d','dac6ad')
    box('Koban wall behind Sam',(0,1.14,1.30),(2.40,.08,2.50),backdrop,.002)
    box('Letter shelf',(-.57,1.02,1.31),(.55,.25,.046),a.oak,.004)
    for i in range(5):
        box('Archive folders',(-.75+i*.074,1.00,1.39),(.039,.12,.15+.021*(i%2)),a.paper,.002)
    hand.shown={o:o.hide_render for o in hand.objects}
    lamp('Desk warm key',2.90,'#fae0aa',(-.50,-.32,.72))
    lamp('Quiet purple bounce',.35,'#bbb9de',(.47,.53,.60))
    area('Lamp pooling light',(.35,.49,1.24),(0,.30,.84),33,'#ffe2a7',.49)
    def frame(f):
        n=f-(f-1)%2
        edge=hinge(n)
        reader.visible(f<35)
        if f<35:
            lean=interval(n,5,29)
            reader.pose((.05,.704,-.226-.06*lean),-.24-.08*lean)
            reader.arms_free(.03)
            reader.primary(reader.b('Spine'),(1,0,0),.26+.22*lean)
            reader.primary(reader.b('Head'),(1,0,0),.15+.12*lean)
            reader.primary(reader.b('Neck'),(0,0,1),.18*interval(n,17,29))
            reader.reach('L',(.195,.389,.888),(.76,.21,-.48),(-.034,-.065,-.015))
            reader.reach('R',(-.139,.402,.878),(-.90,.25,-.32),(.03,-.072,-.010))
            for side,sign in (('L',1),('R',-1)):
                palm=reader.b('Hand',side)
                palm.rotation_quaternion=palm.rotation_quaternion@Quaternion((0,1,0),sign*.76)
                for digit,amount in (('Index',.23),('Middle',.33),('Ring',.38),('Little',.44)):
                    for segment in (1,2,3):
                        bone=reader.bones.get(f'J_Bip_{side}_{digit}{segment}')
                        if bone is not None:
                            bone.rotation_quaternion=Quaternion((0,0,1),-sign*amount)
            reader.blink(n,(18,))
            for key in reader.brow_keys:
                key.value=.28+.37*lean
        hand.visible(35<=n<=111)
        nudge=(1-interval(n,30,42))*.055+interval(n,82,113)*.24
        hand.pose((0,0,0),-.34,.92)
        hand.arms_free()
        hand.aim(hand.b('UpperArm','R'), hand.world('UpperArm','R')+Vector((-.143,.118,-.050)))
        wrist=hand.world('Hand','R')
        # Forearm lies broadside to the page. The index tip moves with its turning edge.
        delta=edge+Vector((.093+nudge,-.061,.038))-wrist
        hand.arm.matrix_world.translation+=delta
        bpy.context.view_layer.update()
        hand.aim(hand.b('LowerArm','R'),hand.world('LowerArm','R')+Vector((-.155,.116,-.074)))
        offset=edge+Vector((.093+nudge,-.061,.037))-hand.world('Hand','R')
        hand.arm.matrix_world.translation+=offset
        bpy.context.view_layer.update()
        hand.aim(hand.b('Hand','R'),hand.world('Hand','R')+Vector((-.086,.064,-.027)))
        if 41<=n<=82:
            # Close actual digit chains around the paper edge, leaving the other fingers relaxed.
            for a,bn,target,pole in (
              ('Index2','Index3',edge+Vector((-.004,.000,.005)),(.03,.16,.97)),
              ('Thumb2','Thumb3',edge+Vector((.006,-.012,-.006)),(.07,-.93,-.07)),
            ):
                hand.chain(hand.b(a,'R'),hand.b(bn,'R'),target,pole
)
        k=interval(f,1,128)
        if f<35:
            look((.576-.111*k,-.702,1.312-.08*k),(.018,.65,1.167),43)
        else:
            look((.079-.057*k,-.146+.071*k,1.482-.021*k),(.007-.029*k,.303,.842),42,math.radians(7-k*3))
    return 128,frame

def shot_10():
    a=architecture('mirror')
    d,knob=door_set(a)
    d.rotation_euler.z=.0
    for mat in bpy.data.materials:
        if mat.name.startswith('Pitted frosted') and mat.node_tree:
            mat.node_tree.nodes.get('Emission').inputs[1].default_value=.65
    sm=Actor('sam')
    copy=Actor('sam')
    mom=Actor('mom')
    def reflected_panel():
        mat=paint('Dark backing beyond window','2c263b','5f4860')
        box('Safe distant backing plate',(.679,2.005,1.49),(1.268,.044,1.344),mat,.002)
        return card('Semi-silvered room reflected in glass',[(.103,1.214,.91),(1.257,1.214,.91),(1.257,1.214,2.20),(.103,1.214,2.20)],
                    translucent('Thin film across station window',ASSETS/'washi_pane.png',.148,.68))
    glass=reflected_panel()
    box('Entry coat pegs',(-.787,-1.173,1.81),(.317,.051,.091),a.oak,.004)
    for i in range(3):
        cyl('Entry coat hook',(-.885+.093*i,-1.133,1.795),.013,.034,a.metal,(0,1,0))
    box('Low empty boot rack',(-.870,-.969,.134),(.37,.275,.245),a.dark,.011)
    lamp('Mirror side sidelight',2.98,'#e4b2a0',(-.57,.60,.56))
    lamp('Stale force in the room',.31,'#bbb4d9',(.52,-.54,.67))
    def frame(f):
        n=f-(f-1)%2
        q=.82*(interval(f,18,30)-interval(f,36,54))
        turn=interval(n,14,28)-interval(n,38,57)
        sm.pose((-.205,.624,-.010),math.pi-.24-2.65*turn)
        sm.arms_free(.036)
        sm.move_hair(n,.044 if .05<turn<.95 else .012)
        reflected=f>=44
        copy.visible(reflected)
        mom.visible(reflected)
        if reflected:
            first=interval(n,56,64)
            settle=interval(n,66,79)
            flinch=first-.68*settle
            gaze=interval(n,60,74)
            breath=.005*math.sin(n*.20)
            copy.pose((.389-.046*flinch,1.545+.022*flinch,-.013+.038*flinch+breath),-.33-.17*flinch)
            copy.arms_free(.029+.046*flinch)
            copy.primary(copy.b('Head'),(0,0,1),.42*gaze)
            copy.primary(copy.b('Neck'),(1,0,0),-.19*flinch+.06*gaze)
            copy.blink(n,(63,84))
            for key in copy.brow_keys:
                key.value=.28+.45*flinch
            mom.pose((.695,1.606,.096+.020*first),-.42,.96)
            mom.arms_free(.048)
            mom.primary(mom.b('Head'),(0,0,1),-1.78)
            shoulder=copy.world('UpperArm','L')+Vector((.048,-.136,.051))
            approach=1-interval(n,51,61)
            wrist=shoulder+Vector((.010*approach,.039*approach,.105*approach))
            miss=mom.reach('R',wrist,(.91,.43,-.29),(-.101,.023,-.052))
            if f in (65,75,93):
                print(f'window frame {f}, right wrist error {miss:.4f} m, wrist {tuple(mom.world("Hand","R"))}, shoulder {tuple(shoulder)}',flush=True)
        pos=Vector((-.332,-.604+.111*interval(f,61,96),1.492))
        aim=Vector((.431,1.331,1.451))
        if q>0:
            angle=-2.60*q
            direction=Matrix.Rotation(angle,4,'Z')@(aim-pos)
            pos.y+=.59*q*q
            pos.x-=.140*q*q
            aim=pos+direction
            aim.z-=.18*q
        roll=.13*(math.sin(math.pi*interval(f,20,38))-math.sin(math.pi*interval(f,47,65)))
        focus=5*interval(f,56,94)-8*q
        look(pos,aim,39+focus,roll)
    return 96,frame

def remove_skin_under_sam_sleeves(actor):
    for ob in actor.objects:
        if ob.type!='MESH' or ob.name.startswith('Body') is False:
            continue
        mats={j for j,m in enumerate(ob.data.materials) if m and m.name.startswith('Sam_Skin_Body')}
        arm_weights={g.index for g in ob.vertex_groups if ('UpperArm' in g.name or 'LowerArm' in g.name)}
        hand_weights={g.index for g in ob.vertex_groups if 'Hand' in g.name or 'Index' in g.name or 'Thumb' in g.name}
        hidden={v.index for v in ob.data.vertices
                if sum(g.weight for g in v.groups if g.group in arm_weights)>.55
                and sum(g.weight for g in v.groups if g.group in hand_weights)<.21}
        bm=bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.delete(bm,geom=[face for face in bm.faces if face.material_index in mats
                         and sum(v.index in hidden for v in face.verts)>=len(face.verts)*.67],
                         context='FACES')
        bm.to_mesh(ob.data)
        bm.free()

def shot_13():
    a=architecture('door')
    d,knob=door_set(a,True)
    s=Actor('sam')
    remove_skin_under_sam_sleeves(s)
    sky,tex=mapped('Dusk reflected through door',ASSETS/'street_dusk.png')
    card('Painted dusk through translucent glass',[(-.62,-1.69,.638),(.43,-1.69,.638),(.43,-1.69,1.99),(-.62,-1.69,1.99)],sky)
    crownmat,crowntex=mapped('Canon crown beyond the frosted door',ASSETS/'chime_crown'/'074.png')
    crownmat.surface_render_method='BLENDED'
    N,L=crownmat.node_tree.nodes,crownmat.node_tree.links
    mix=N.new('ShaderNodeMixShader')
    L.new(crowntex.outputs['Alpha'],mix.inputs[0])
    L.new(N.new('ShaderNodeBsdfTransparent').outputs[0],mix.inputs[1])
    L.new(N.get('Emission').outputs[0],mix.inputs[2])
    L.new(mix.outputs[0],N.get('Material Output').inputs[0])
    crown=card('The Listener turns with the chime',[(-.72,-1.664,1.15),(.46,-1.664,1.15),(.46,-1.664,2.12),(-.72,-1.664,2.12)],crownmat)
    glass_mats=[m for m in bpy.data.materials if m.name.startswith('Pitted frosted') and m.node_tree]
    ring_mat=flat('Cloud pressure ring','#eabc9c',1.15)
    rings=[]
    for i in range(4):
        points=[(.25*math.cos(j*math.tau/49),0,.08*math.sin(j*math.tau/49)) for j in range(50)]
        o=curve('Chime ripple in sky',points,.006,ring_mat)
        o.location=(-.12,-1.57,1.47)
        rings.append(o)
    lamp('Amber doorway nightfall',3.32,'#e6a682',(-.42,-.61,.61))
    lamp('Faded blue room lamp',.49,'#b6b5e0',(.55,.60,.59))
    area('Rim after slam',(1.02,-.83,1.93),(0,-.54,1.06),56,'#e3a98f',.67)
    def frame(f):
        n=f-(f-1)%2
        ease_d=interval(n,5,23)
        d.rotation_euler.z=(1-ease_d)*.96+.028*math.sin(n*1.5)*math.exp(-abs(n-23)/2.7)
        crown_frame=74+2*int(17*interval(n,31,89))
        crowntex.image=bpy.data.images.load(str(ASSETS/'chime_crown'/f'{crown_frame:03d}.png'),check_existing=True)
        c=interval(n,19,48)
        impacts=sum((.25+.1*i)*math.exp(-((n-(35+17*i+2))/3.1)**2) for i in range(4))
        brace=interval(n,45,99)
        s.pose((-.26-.025*impacts,-.594+.121*c,-.010-.414*c-.083*impacts),-.08+.86*c+.31*brace)
        s.arms_free(.052)
        s.primary(s.b('Spine'),(1,0,0),.34*c+.19*impacts)
        s.primary(s.b('Neck'),(1,0,0),.11*c+.21*impacts)
        s.primary(s.b('Head'),(0,0,1),.27*brace)
        s.blink(n,(37,54,70,87))
        for key in s.brow_keys:
            key.value=.24+.52*brace
        crown.location.x=.12*interval(n,36,92)
        for material in glass_mats:
            material.node_tree.nodes.get('Emission').inputs[1].default_value=.82-.30*brace
        for side,sign in (('L',1),('R',-1)):
            anchor=Vector((-.26+.104*sign,-.641,.118))
            s.chain(s.b('UpperLeg',side),s.b('LowerLeg',side),anchor,(.18*sign,-.90,.25))
            s.aim(s.b('Foot',side),s.world('Foot',side)+Vector((.017*sign,-.137,-.07)))
            axes=s.arm.matrix_world.to_3x3()
            ears=s.world('Head')+axes@Vector((.103*sign,-.013,.016))
            low=s.world('UpperArm',side)+axes@Vector((.12*sign,-.13,-.23))
            if side=='R':
                bpy.context.view_layer.update()
                low=low.lerp(knob.matrix_world.translation,interval(n,3,16)*(1-interval(n,18,33)))
            u=interval(n,20 if side=='R' else 17,47)
            pole=axes@Vector((.85*sign,-.23,-.31))
            if n>=19 or side=='R':
                down=Vector((0,-.045,-.062))
                palm=down.lerp(Vector((0,-.013,.076)),u)
                s.reach(side,low.lerp(ears,u),pole,palm)
        for i,r in enumerate(rings):
            phase=(n-(35+i*17))/31
            r.hide_render=not (0<=phase<1)
            r.scale.x=r.scale.z=.11+3*max(0,phase)
        s.move_hair(n,.041*math.exp(-((n-29)/10)**2)+.012)
        k=interval(f,1,120)
        look((.627+.105*k,.477-.201*k,1.43-.385*interval(f,20,57)),(-.315,-1.01,1.22-.218*k),41,math.radians(-3*k))
    return 120,frame

def shot_14():
    a=architecture('door')
    d,k=door_set(a,True)
    duplicate=Actor('sam')
    pane=flat('Amber behind frost','#d48e71',.85)
    for mat in bpy.data.materials:
        if mat.name.startswith('Pitted frosted') and mat.node_tree:
            mat.node_tree.nodes.get('Emission').inputs[1].default_value=.70
    card('Dusk on the far side of the frosted door',[(-.62,-1.88,.649),(.42,-1.88,.649),(.42,-1.88,1.939),(-.62,-1.88,1.939)],pane)
    shadow=flat('An opaque human form behind the door','#231c2b')
    for ob in duplicate.objects:
        if ob.type in ('MESH','CURVE'):
            for i,m in enumerate(ob.data.materials):
                ob.data.materials[i]=shadow
    lamp('Late window bleed',2.51,'#ce9e91',(-.50,.61,.47))
    lamp('Final cool fill',.40,'#bdb3d7',(.45,-.54,.51))
    cut=card('Intentional black cut',[(-2,-.75,-.3),(2,-.75,-.3),(2,-.75,3.3),(-2,-.75,3.3)],a.black)
    def frame(f):
        n=f-(f-1)%2
        slam=math.sin((n-19)*2.3)*.005*math.exp(-abs(n-23)/3.2)
        d.rotation_euler.z=slam
        lean=interval(n,62,101)
        duplicate.pose((-.053+.056*lean,-1.56+.110*lean,-.013+.008*math.sin(n*.19)),math.pi+.14*lean)
        duplicate.arms_free(.039)
        step=interval(n,6,17)-interval(n,27,40)
        if step>0:
            h=duplicate.world('UpperArm','R')
            duplicate.reach('R',h+Vector((.063,.10+.057*step,-.32+.203*step)),(-.89,-.32,-.25),(.023,.063,.067))
        duplicate.primary(duplicate.b('Head'),(1,0,0),-.045-.135*lean)
        duplicate.primary(duplicate.b('Spine'),(1,0,0),.11*lean)
        cut.hide_render=f<114
        q=interval(f,1,120)
        look((.074+.025*q,.691-.129*q,1.412),(-.055,-1.208,1.328),41)
    return 120,frame

def shot_15():
    a=station_materials()
    z=desk(a,.31,.84)
    b=book(a,(0,.306,z))
    tick=lamp_chain(a,z,b)
    lamp('Low rust edge to stinger',3.1,'#edb684',(-.56,-.46,.61))
    lamp('Violet paper fill',.27,'#c9b7d9',(.51,.35,.62))
    def frame(f):
        n=f-(f-1)%2
        ink_frame=min(71,1+2*int((n-1)*.83))
        b.tex.image=bpy.data.images.load(str(ASSETS/'v6_book'/'book_write'/f'{ink_frame:03d}.png'),check_existing=True)
        tick(n+3)
        q=interval(f,1,96)
        target=(.073+.020*q,.268-.044*q,.849)
        look((.109+.005*q,.043-.036*q,1.106-.039*q),target,44,math.radians(-8+1.5*q))
    return 96,frame


