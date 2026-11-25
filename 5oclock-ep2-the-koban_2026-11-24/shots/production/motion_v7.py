"""Targeted replacements for the street gait and the station contact actions."""

def walk_strides(actor,frame,origin,speed,cycle,centre):
    # Heel-to-toe support in world coordinates. The two stance phases overlap.
    t=frame-1
    step=speed*cycle/24
    y=origin+t*speed/24
    beat=t*math.tau/cycle
    actor.pose((centre+.024*math.sin(beat),y,.001-.016*math.cos(2*beat)),math.pi)
    actor.primary(actor.b('Hips'),(0,0,1),.057*math.cos(beat))
    actor.primary(actor.b('Spine'),(1,0,0),.072+.017*math.sin(2*beat))
    actor.primary(actor.b('UpperChest'),(0,0,1),-.096*math.cos(beat))
    for side,sign,shift in (('L',1,0),('R',-1,cycle/2)):
        turn=(t+shift)/cycle
        q=turn-math.floor(turn)
        home=origin+(math.floor(turn)*cycle-shift)*speed/24+.43*step/2
        swing=clamp((q-.60)/.40)
        lift=.122*math.sin(math.pi*swing)**1.18
        ankle_x=centre-sign*.083
        # The angle is continuous between stance and the repositioning phase.
        if q<.60:
            heel=1-interval(q,0,.16)
            toe=interval(q,.36,.60)
            pitch=.26*heel-.54*toe
            pivot=-.049 if pitch>=0 else .153
            z=.085*math.cos(pitch)-pivot*math.sin(pitch)
            foot_y=home+pivot*(1-math.cos(pitch))-.085*math.sin(pitch)
        else:
            pitch=-.54+.80*ease(swing)
            foot_y=home+step*ease(swing)+.049*(math.cos(pitch)-1)-.085*math.sin(pitch)
            foot_y+=.202*(1-math.cos(.54))*(1-ease(swing))
            roll_start=.085*math.cos(.54)+.153*math.sin(.54)
            roll_end=.085*math.cos(.26)+.049*math.sin(.26)
            z=(1-ease(swing))*roll_start+ease(swing)*roll_end+lift
        ankle=Vector((ankle_x,foot_y,z))
        actor.chain(actor.b('UpperLeg',side),actor.b('LowerLeg',side),ankle,(-.034*sign,1,.10))
        actor.aim(actor.b('Foot',side),actor.world('Foot',side)+Vector((-.016*sign,math.cos(pitch),math.sin(pitch))))
        if os.environ.get('KOBAN_CONTACT_DEBUG') and frame in (1,5,11,15,19,23,57,73,83,91):
            err=(actor.world('Foot',side)-ankle).length
            print(f'stride {frame} {side} phase {q:.2f} planted {q<.60} ankle error {err*1000:.2f} mm',flush=True)
        # Swing through the shoulder. The elbow bends forward and the wrist follows it.
        sweep=-.238*math.cos(math.tau*q)
        upper=Vector((-.052*sign,sweep,-.263))
        actor.aim(actor.b('UpperArm',side),actor.world('UpperArm',side)+upper)
        bend=Vector((-.022*sign,sweep+.128+.081*max(0,sweep/.238),-.263))
        actor.aim(actor.b('LowerArm',side),actor.world('LowerArm',side)+bend)
        set_hand(actor,side,forearm(actor,side),(sign,-.20,.06),.43,.44)
    actor.move_hair(frame,.027)
    return y

def street_walk_v7():
    horns=street(False)
    cast=townspeople()
    sam=Actor('sam')
    def frame(f):
        n=f-(f-1)%2
        for root,j,side,flip in horns:
            root.rotation_euler.z=flip*.91+side*.99
        for i,(person,x,y,broom) in enumerate(cast):
            sweep(person,(x,y),broom,n,12 if i==0 else 0,i==0)
        walk_strides(sam,n,-1.40,1.88,22,-.29)
        sam.primary(sam.b('Head'),(0,0,1),-.17*(interval(n,20,39)-interval(n,59,74)))
        sam.blink(n,(39,83))
        y=-1.40+(f-1)*1.88/24
        if f<=42:
            look((.48,y-2.11,1.12),(-.22,y+.71,1.02),32)
        else:
            k=interval(f,52,96)
            look((1.70-.11*k,y+1.81,1.21+.08*k),(-.30,y-.10,.94),32.5)
        if os.environ.get('KOBAN_CONTACT_DEBUG') and f in (5,19,35,55,69,87,95):
            limb_diagnostics(sam,'R','street',f)
            limb_diagnostics(sam,'L','street',f)
    return 96,frame

def door_pull(material,door,side):
    # A vertical bar leaves a visible gap for the four fingers behind it.
    y=-1.216+side*.104
    x,z=.285,1.019
    bar=cyl('Vertical door pull', (x,y,z),.012,.151,material)
    attach(bar,door)
    for zz in (z-.062,z+.062):
        post=cyl('Door pull mount',(x,-1.216+side*.062,zz),.012,.090,material,(0,1,0))
        attach(post,door)
    return bar

def pull_door(actor,bar,side,direction,f,engage):
    bpy.context.view_layer.update()
    axes=bar.parent.matrix_world.to_3x3()
    across=axes@Vector((direction,0,0))
    normal=axes@Vector((0,1 if side=='R' else -1,0))
    bar_center=bar.matrix_world.translation
    wrist=bar_center-across*.079-normal*.022+Vector((0,0,-.012))
    rest=actor.world('Hand',side)
    target=rest.lerp(wrist,engage)
    pole=Vector((-.32 if direction>0 else .72,.12,-1))
    error=actor.chain(actor.b('UpperArm',side),actor.b('LowerArm',side),target,pole)
    forward=forearm(actor,side).lerp(across,engage*.58)
    set_hand(actor,side,forward,normal,.31+.68*engage,.26+.61*engage)
    return target,error

def desk_hands(actor):
    # Palms rest against the desk outside the written rules. The elbows carry the lean.
    for side,target,pole in (
        ('L',(.222,.512,.874),(.87,.28,.18)),
        ('R',(-.207,.490,.874),(-.87,.28,.18)),
    ):
        reach_hand(actor,side,target,pole,(0,0,-1),.15,.14,(0,-1,-.13))

def page_hand(actor,edge,frame):
    lift=interval(frame,38,48)
    release=interval(frame,79,93)
    pinch=lift*(1-release)
    theta=math.pi*interval(frame,30,83)
    # Sweep with the page while allowing the wrist and free fingers to follow through.
    angle=.08-.38*math.sin(theta)
    forward=Vector((-.84,.48,angle)).normalized()
    palm=Vector((-.13*math.sin(theta),-.06,-1))
    actor.pose((0,0,0),-.33,.92)
    actor.aim(actor.b('UpperArm','R'),actor.world('UpperArm','R')+Vector((-.28,.15,-.08)))
    actor.aim(actor.b('LowerArm','R'),actor.world('LowerArm','R')+forward)
    set_hand(actor,'R',forward,palm,.29+.10*pinch,.37+.41*pinch)
    index=actor.world('Index3','R',end=True)
    # At load, target the index pad slightly above the paper. The thumb closes toward its underside.
    target=edge+Vector((.001,-.012,.003))+Vector((.079,-.024,.034))*(1-lift)
    target+=Vector((.19,-.14,.084))*release
    actor.arm.matrix_world.translation+=target-index
    bpy.context.view_layer.update()
    if pinch>.12:
        pad=target+Vector((.004,0,-.010))
        thumb_base=actor.world('Thumb2','R')
        available=sum((actor.world(f'Thumb{i}','R',end=True)-actor.world(f'Thumb{i}','R')).length for i in (2,3))
        if (pad-thumb_base).length<available*1.10:
            actor.chain(actor.b('Thumb2','R'),actor.b('Thumb3','R'),pad,(.14,-.57,-.69))
    if os.environ.get('KOBAN_CONTACT_DEBUG') and frame in (39,47,59,67,79,93):
        wrist=actor.world('Hand','R')
        gap=(actor.world('Thumb3','R',end=True)-actor.world('Index3','R',end=True)).length
        print(f'page {frame}: pad separation {gap*1000:.1f} mm',flush=True)

def touch_shoulder(mom,copy,frame):
    load=interval(frame,49,67)
    shoulder=copy.world('UpperArm','L')+Vector((.038,-.136,.043))
    wrist=shoulder+Vector((.103,.044,.037)) + (1-load)*Vector((.020,.058,.082))
    direction=Vector((-.94,-.26,-.24))
    reach_hand(mom,'R',wrist,(.15,.86,-.54),(.08,.91,-.37),.19+.13*load,.30,direction)
    return wrist
