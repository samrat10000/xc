"""Kitchen, the stove reflection and the offscreen camera feed for the call."""
import math
import numpy as np

def kitchen():
    tile=mapped('Grout and mottled tiles',ASSETS/'tiles.png','aaa2a9','fff4ce')
    wall=mapped('Yellowed kitchen plaster',ASSETS/'kitchen_plaster.png','b1a7bb','fff8e5')
    lino=mapped('Worn linoleum',ASSETS/'rubber_lino.png','aaa9bf','ffdfb4')
    wood=mapped('Kitchen timber grain',ASSETS/'counter.png','9d93ad','fff1d3')
    woodside=paint('Painted cupboard','473b48','8b6653','c18b60')
    dark=paint('Stove graphite','201e2d','42404a')
    enamel=paint('Old stove enamel','67545b','bc9075','ffc994')
    steel=paint('Brushed sink lip','55576b','9597aa','f8caae',.78)
    lightpane=flat('Warm kitchen window','#ffdda6',1.15)
    tilecard=card('Tile splashback',[(-1.85,1.111,.70),(1.85,1.111,.70),(1.85,1.111,1.73),(-1.85,1.111,1.73)],tile)
    card('Upper plaster',[(-2.35,1.14,0),(2.35,1.14,0),(2.35,1.14,2.85),(-2.35,1.14,2.85)],wall)
    card('Floor',[(-2.4,-3.2,0),(2.4,-3.2,0),(2.4,1.25,0),(-2.4,1.25,0)],lino)
    card('Left wall',[(-1.86,-2,0),(-1.86,1.14,0),(-1.86,1.14,2.8),(-1.86,-2,2.8)],wall)
    box('Counter body',(0,.715,.46),(3.57,.65,.89),woodside,.012)
    box('Counter nosing',(0,.69,.89),(3.61,.72,.060),woodside,.013)
    card('Remnant timber countertop',[(-1.80,.33,.921),(1.80,.33,.921),(1.80,1.05,.921),(-1.80,1.05,.921)],wood)
    for x in [-1.47,-.87,-.27,.33,.93,1.53]:
        box('Cabinet door',(x,.377,.435),(.55,.047,.73),woodside,.009)
        box('Metal handle',(x,.338,.645),(.128,.034,.020),steel,.004)
        box('Recessed bevel',(x,.346,.379),(.468,.01,.55),woodside,.010)
    box('Window outer trim',(.97,1.076,1.998),(1.13,.10,.89),woodside,.014)
    card('Window paper',[(.445,1.006,1.60),(1.495,1.006,1.60),(1.495,1.006,2.399),(.445,1.006,2.399)],lightpane)
    for x in (.455,.70,.961,1.216,1.484):
        box('Sliding muntin',(x,.989,2.0),(.021,.039,.808),woodside,.002)
    for z in (1.605,1.874,2.14,2.396):
        box('Horizontal muntin',(.97,.981,z),(1.045,.043,.021),woodside,.002)
    box('Window shelf',(.97,.963,1.59),(1.18,.32,.046),woodside,.012)
    box('Stove enamel case',(.44,.59,.968),(.60,.54,.097),enamel,.024)
    box('Burner top',(.44,.59,1.011),(.564,.494,.012),dark,.014)
    for x in (.283,.594):
        cyl('Burner trim',(x,.606,1.023),.100,.012,steel)
        cyl('Gas burner',(x,.606,1.033),.077,.014,dark)
        for i in range(8):
            a=i*math.tau/8
            o=box('Burner tooth',(x+.094*math.cos(a),.606+.094*math.sin(a),1.04),(.047,.017,.022),dark,.003)
            o.rotation_euler.z=a
        cyl('Stove control knob',(x,.301,.966),.031,.027,steel,(0,-1,0))
    box('Sink',(-1.09,.68,.933),(.66,.437,.041),steel,.035)
    box('Dark recessed bowl',(-1.085,.685,.956),(.535,.330,.005),dark,.025)
    curve('Faucet',[(-1.27,.864,.94),(-1.27,.864,1.16),(-1.25,.817,1.24),(-1.16,.753,1.253),(-1.12,.718,1.22)],.021,steel)
    for i,(x,r,z,m) in enumerate(((-.56,.059,.117,enamel),(-.43,.045,.144,steel),(1.13,.053,.137,enamel),(1.32,.061,.108,steel),(1.49,.04,.182,enamel))):
        cyl('Kitchen jars',(x,.90,.92+z/2),r,z,m)
        cyl('Jar lid',(x,.90,.924+z),r*1.09,.018,woodside)
    # Hanging tools are distinct profiles, with hooks and a rail.
    curve('Utensil rail',[(-1.66,1.059,1.68),(-.46,1.059,1.68)],.014,steel)
    for i,x in enumerate((-1.535,-1.338,-1.16,-.954)):
        curve('Hanging handle',[(x,1.04,1.68),(x+.014,.99,1.64),(x+.011,.946,1.46-i%3*.035)],.007,dark)
        cyl('Ladle bowl',(x+.01,.949,1.42-i%3*.034),.037,.018,steel,(0,-1,0))
    box('Spice shelf',(-.99,.973,1.971),(1.33,.31,.048),woodside,.006)
    for i,x in enumerate((-.60,-.84,-1.015,-1.20,-1.39)):
        cyl('Shelf tin',(x,.947,2.023+i%2*.009),.044,.074+i%2*.02,enamel if i%2 else steel)
    # The worn doorway supplies a dark framing edge.
    box('Door jamb',(-1.49,-.733,1.34),(.151,.176,2.75),woodside,.014)
    return enamel,dark,steel

def kettle(base,steel,dark):
    x,y,z=base
    # Rotate the shared lathe axis into the upright boiler.
    profile=[(0,.061),(.007,.082),(.029,.098),(.062,.097),(.091,.089),(.118,.074),(.132,.059),(.137,.046)]
    chromed=paint('Kettle chrome cool body','494b66','989db2','e9a87e',.70)
    ob=mesh_obj('Chromed kettle',lathe(profile,56,True),chromed,line=.0016)
    ob.rotation_euler.x=math.pi/2
    ob.location=base
    lid=cyl('Kettle lid',(x,y,z+.137),.061,.013,steel)
    cyl('Insulated knob',(x,y,z+.163),.022,.04,dark)
    c=[(x+.066*math.cos(math.pi*i/28),y-.004,z+.073+.139*math.sin(math.pi*i/28)) for i in range(29)]
    curve('Kettle handle arch',c,.011,dark)
    curve('Steam spout',[(x+.086,y-.011,z+.05),(x+.119,y-.013,z+.063),(x+.138,y-.017,z+.098),
                         (x+.153,y-.013,z+.121),(x+.17,y-.010,z+.124)],.019,steel)
    cyl('Spout opening',(x+.168,y-.010,z+.124),.013,.003,dark,(.89,.11,.25))
    def radius(height):
        return np.interp(height,[a for a,b in profile],[b for a,b in profile])
    mat,tex=mapped('Kettle reflection of the original character',ASSETS/'kettle_reflection.png')
    mat.surface_render_method='BLENDED'
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    out=nodes.get('Material Output')
    mix=nodes.new('ShaderNodeMixShader')
    links.new(tex.outputs['Alpha'],mix.inputs[0])
    links.new(nodes.new('ShaderNodeBsdfTransparent').outputs[0],mix.inputs[1])
    links.new(nodes.get('Emission').outputs[0],mix.inputs[2])
    links.new(mix.outputs[0],out.inputs[0])
    verts,uv,faces=[],[],[]
    q=21
    for j in range(q):
        for i in range(q):
            u,v=i/(q-1),j/(q-1)
            dx=.031+(u-.5)*.073+.006*math.sin(v*math.pi)
            hh=.076+(v-.5)*.088
            yy=-math.sqrt(max(.00015,radius(hh)**2-dx**2))-.002
            verts.append((x+dx,y+yy,z+hh))
            uv.append((u,v))
            if i<q-1 and j<q-1:
                a=j*q+i
                faces.append((a,a+1,a+1+q,a+q))
    face=form('Six-frame faceless reflection',verts,faces,mat,uv)
    hairline=face
    return (face,hairline),Vector((x+.168,y-.017,z+.131))

def steam_material():
    m=bpy.data.materials.new('Soft-edged moving steam')
    m.use_nodes=True
    m.surface_render_method='BLENDED'
    nt=m.node_tree
    N,L=nt.nodes,nt.links
    N.clear()
    out=N.new('ShaderNodeOutputMaterial')
    coord=N.new('ShaderNodeTexCoord')
    sep=N.new('ShaderNodeSeparateXYZ')
    L.new(coord.outputs['UV'],sep.inputs[0])
    def node(op,a,b=None):
        n=N.new('ShaderNodeMath')
        n.operation=op
        for i,s in enumerate((a,b)):
            if s is None:continue
            if isinstance(s,(int,float)):n.inputs[i].default_value=s
            else:L.new(s,n.inputs[i])
        return n.outputs[0]
    dist=node('ABSOLUTE',node('SUBTRACT',sep.outputs['X'],.5))
    edge=node('MAXIMUM',node('SUBTRACT',1,node('MULTIPLY',dist,2.2)),0)
    width=node('POWER',edge,2.3)
    env=node('SINE',node('MULTIPLY',sep.outputs['Y'],math.pi))
    alpha=node('MULTIPLY',node('MULTIPLY',width,env),.63)
    transparent=N.new('ShaderNodeBsdfTransparent')
    glow=N.new('ShaderNodeEmission')
    glow.inputs[0].default_value=(.83,.76,.66,1)
    glow.inputs[1].default_value=.84
    mix=N.new('ShaderNodeMixShader')
    L.new(alpha,mix.inputs[0])
    L.new(transparent.outputs[0],mix.inputs[1])
    L.new(glow.outputs[0],mix.inputs[2])
    L.new(mix.outputs[0],out.inputs[0])
    return m

def make_steam(origin):
    mat=steam_material()
    slices=22
    curves=[]
    faces=[(j*2,j*2+1,j*2+3,j*2+2) for j in range(slices)]
    uv=[(i,j/slices) for j in range(slices+1) for i in (0,1)]
    def positions(f,i):
        phase=f*.074+i*2.2
        for j in range(slices+1):
            u=j/slices
            height=(.34+i*.10)*u*(.94+.06*math.sin(phase))
            drift=(.031+u*.025)*math.sin(u*7.8-phase)+.027*u*i
            anchor=origin+Vector((u*drift,-i*.014+math.sin(u*7-phase)*u*.047,height))
            width=.008+(u**.74)*(.097+i*.011)
            for sign in (-1,1):
                yield anchor+Vector((width*.5*sign,0,0))
    for i in range(3):
        curves.append(form('Steam ribbon',list(positions(1,i)),faces,mat,uv))
    def tick(f):
        for i,ob in enumerate(curves):
            for vert,p in zip(ob.data.vertices,positions(f,i)):
                vert.co=p
            ob.data.update()
    return tick

def mom_pose(mom,f,back=False,base=(-.09,.03,0)):
    t=f/24
    yaw=math.pi-.10 if back else .04+.11*math.sin(t*.86)
    mom.pose(base,yaw)
    mom.arms_free()
    mom.primary(mom.b('Chest'),(0,0,1),.05*math.sin(t*2.04))
    mom.primary(mom.b('Neck'),(1,0,0),.07+.041*math.sin(t*.89) if back else .143)
    mom.primary(mom.b('Head'),(0,0,1),-.16 if back else .11*math.cos(t*1.0))
    if back:
        a=Vector((-.235,.225,.989))
        b=Vector((.078+.074*math.sin(t*5),.222+.038*math.cos(t*5),1.008))
        mom.reach('L',a,(-.65,-.32,-.32),(.070,.090,-.012))
        mom.reach('R',b,(.55,-.32,-.30),(.010,.098,-.021))
    mom.blink(f,(23,62,80))
    if not back:
        for key in mom.brow_keys:key.value=.32+.26*interval(f,13,73)
    mom.move_hair(f,.012)

def shot_04():
    enamel,dark,steel=kitchen()
    mom=Actor('mom')
    mom_pose(mom,1,True)
    # An apron tie also reads from the side on the shot-facing back.
    for s in (-1,1):
        twill=paint('Apron neck and waist ties','a19391','e3cc9f')
        tie=curve('Apron shoulder strap',[(-.09+s*.068,-.043,1.402),(-.09+s*.084,-.077,1.311),(-.09+s*.092,-.084,1.191),(-.09+s*.082,-.061,1.083)],.011,twill)
        mom.attach_bone(tie,'UpperChest')
    tie=curve('Apron waist tie',[(-.223,-.034,1.04),(-.09,-.085,1.038),(.051,-.038,1.04)],.012,twill)
    mom.attach_bone(tie,'Spine')
    bowl=cyl('Ceramic mixing bowl',(-.13,.485,.961),.115,.065,enamel)
    spoon=box('Wooden cooking spoon',(.078,.261,1.003),(.032,.211,.015),enamel,.007)
    reflect,origin=kettle((.591,.606,1.044),steel,dark)
    steam=make_steam(origin)
    lamp('Sun coming through back grid',4.3,'#ffe0b0',(-.45,.71,.53))
    lamp('Cool room bounce',.26,'#c7ccec',(.40,-.38,.52))
    area('Window side light',(.34,.27,2.10),(-.30,-.02,1.23),115,'#ffbe87',1)
    def frame(f):
        n=f-(f-1)%2
        mom_pose(mom,n,True)
        spoon.location.x=.076+.073*math.sin(n/24*5)
        spoon.rotation_euler.z=.14*math.sin(n/24*5)
        steam(n)
        for ob in reflect:
            ob.hide_render=not 77<=f<=82
        if f<66:
            k=interval(f,1,65)
            look((.035+.074*k,-1.69+.107*k,1.365+.034*k),(.100,.50,1.357),41)
        else:
            k=interval(f,66,96)
            look((.741-.012*k,-.157+.034*k,1.277),(.645,.595,1.232),47)
    return 96,frame

def make_other_side():
    sam=Actor('sam')
    ghost=Actor('mom')
    sam.pose((-.22,-.15,0),-.12,.95)
    sam.arms_free()
    ghost.pose((.119,.14,0),.14)
    ghost.arms_free(.025)
    dark=paint('Other side plaster','362d46','6e596c')
    box('Empty koban back',(0,.73,1.18),(2.9,.12,2.67),dark,.003)
    box('Other side sill',(0,.59,1.02),(2.9,.154,.045),paint('Sill','3e3549','87616b'),.004)
    lamp('Other-side eerie window bounce',2.1,'#daa0a8',(-.45,-.71,.53))
    area('Faint warm cheek',(.65,-.69,1.93),(0,0,1.4),42,'#f5c6a6',.72)
    look((.092,-1.38,1.49),(-.067,.02,1.44),32)
    return 1,lambda f:None

def make_feed(reveal):
    enamel,dark,steel=kitchen()
    mom=Actor('mom')
    z=1.638
    x=.245
    panel=box('Framed kitchen mirror',(x,1.086,z),(.332,.059,.462),dark,.006)
    content=(ASSETS/'mirror_feed.png') if reveal else ASSETS/'washi_pane.png'
    mat,tex=mapped('Reversed kitchen view',content)
    card('Reflection inside kitchen mirror',
         [(x-.148,1.048,z-.207),(x+.148,1.048,z-.207),(x+.148,1.048,z+.207),(x-.148,1.048,z+.207)],mat,True)
    lamp('Kitchen window light',3.1,'#fce0b7',(.40,-.64,.53))
    lamp('Cool rear wall fill',.35,'#c8c3e1',(-.52,.50,.63))
    area('Face window bounce',(.54,-.61,1.79),(-.24,.38,1.44),42,'#ffd59e',.70)
    tear_mat=flat('Window reflection in tears','#f5c9b5')
    tear=box('Tear catchlight',(0,0,1),(.007,.006,.018),tear_mat,.003)
    face=next(o for o in mom.objects if o.name.startswith('Mom_Face') and 'Outline' not in o.name)
    def tick(f):
        n=f-(f-1)%2
        mom_pose(mom,n,False,(-.205,.22,0))
        eye=mom.world('Head')
        inv=face.matrix_world.inverted()
        probe=eye+Vector((.039,-.41,.070-.037*interval(f,17,81)))
        ev=face.evaluated_get(bpy.context.evaluated_depsgraph_get())
        ok,hit,normal,index=ev.ray_cast(inv@probe,inv.to_3x3()@Vector((0,1,0)))
        tear.hide_render=not ok
        if ok: tear.location=(face.matrix_world@hit)+Vector((0,-.003,0))
        tear.rotation_euler.y=.13
        scale=1+.018*math.sin(n*.12)
        look((.017,-1.34/scale,1.405),(.014,.327,1.382),53)
    return 96,tick

