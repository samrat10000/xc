from pathlib import Path
base=Path(__file__).resolve().parent

def tweak(name, replacements):
    source=(base/f'{name}.py').read_text(encoding='utf-8-sig')
    for old,new in replacements:
        assert old in source, (name,old)
        source=source.replace(old,new,1)
    (base/f'{name}_v6.py').write_text(source,encoding='utf-8')

tweak('station',[
("""        q=interval(f,20,38)-interval(f,47,65)
        turn=interval(n,16,33)-interval(n,49,70)""",
"""        q=.82*(interval(f,18,30)-interval(f,36,54))
        turn=interval(n,14,28)-interval(n,38,57)"""),
("""        reflected=f>=57""","""        reflected=f>=44"""),
("""            copy.pose((.389,1.545,-.013),-.33)
            copy.arms_free(.029)
            mom.pose((.721,1.602,.122),-.38,.96)""",
"""            first=interval(n,56,64)
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
            mom.pose((.695,1.606,.096+.020*first),-.42,.96)"""),
("""            shoulder=copy.world('UpperArm','L')+Vector((.103,-.164,.048))
            miss=mom.reach('R',shoulder,(.77,-.22,-.62),(-.096,.020,-.046))""",
"""            shoulder=copy.world('UpperArm','L')+Vector((.078,-.144,.052))
            approach=1-interval(n,51,61)
            wrist=shoulder+Vector((.010*approach,.039*approach,.105*approach))
            miss=mom.reach('R',wrist,(.91,.43,-.29),(-.101,.023,-.052))"""),
("""        pos=Vector((-.198,-.594,1.508))
        aim=Vector((.564,1.331,1.425))""",
"""        pos=Vector((-.332,-.604+.111*interval(f,61,96),1.492))
        aim=Vector((.431,1.331,1.451))"""),
("""        focus=2*interval(f,68,96)-9*q
        look(pos,aim,43+focus,roll)""",
"""        focus=5*interval(f,56,94)-8*q
        look(pos,aim,39+focus,roll)"""),
("""    card('The Listener turns with the chime',[(-.52,-1.664,1.27),(.36,-1.664,1.27),(.36,-1.664,1.97),(-.52,-1.664,1.97)],crownmat)""",
"""    crown=card('The Listener turns with the chime',[(-.72,-1.664,1.15),(.46,-1.664,1.15),(.46,-1.664,2.12),(-.72,-1.664,2.12)],crownmat)
    glass_mats=[m for m in bpy.data.materials if m.name.startswith('Pitted frosted') and m.node_tree]"""),
("""        c=interval(n,19,48)
        s.pose((-.26,-.594+.121*c,-.010-.445*c),-.08-.50*c)
        s.arms_free(.052)
        s.primary(s.b('Spine'),(1,0,0),.34*c)
        s.primary(s.b('Neck'),(1,0,0),.11*c)""",
"""        c=interval(n,19,48)
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
            material.node_tree.nodes.get('Emission').inputs[1].default_value=.82-.30*brace"""),
("""            if n>=24:
                ears=s.world('Head')+s.arm.matrix_world.to_3x3()@Vector((.105*sign,-.012,.022))
                low=s.world('UpperArm',side)+Vector((.17*sign,-.088,-.228))
                u=interval(n,24,47)
                s.reach(side,low.lerp(ears,u),(.95*sign,-.12,-.28),(0,-.022,.075))
            elif side=='R':
                bpy.context.view_layer.update()
                handle=knob.matrix_world.translation
                low=s.world('UpperArm',side)+Vector((-.08,-.19,-.23))
                s.reach(side,low.lerp(handle,ease_d),(-1,.26,-.28),(.04,-.081,.012))""",
"""            axes=s.arm.matrix_world.to_3x3()
            ears=s.world('Head')+axes@Vector((.103*sign,-.013,.016))
            low=s.world('UpperArm',side)+axes@Vector((.12*sign,-.13,-.23))
            if side=='R':
                bpy.context.view_layer.update()
                low=low.lerp(knob.matrix_world.translation,interval(n,3,16)*(1-interval(n,18,33)))
            u=interval(n,20 if side=='R' else 17,47)
            pole=axes@Vector((.85*sign,-.23,-.31))
            s.reach(side,low.lerp(ears,u),pole,(0,-.013,.076))"""),
("""        look((.597-.067*k,.556+.084*k,1.43-.378*interval(f,20,57)),(-.37,-1.07,1.23-.206*k),41,math.radians(-3*k))""",
"""        look((.627+.105*k,.477-.201*k,1.43-.385*interval(f,20,57)),(-.315,-1.01,1.22-.218*k),41,math.radians(-3*k))"""),
("""        duplicate.pose((-.053+.018*interval(n,35,94),-1.49,-.013),math.pi)""",
"""        lean=interval(n,62,101)
        duplicate.pose((-.053+.056*lean,-1.56+.110*lean,-.013+.008*math.sin(n*.19)),math.pi+.14*lean)"""),
("""        duplicate.primary(duplicate.b('Head'),(1,0,0),-.055-.04*interval(n,56,90))""",
"""        duplicate.primary(duplicate.b('Head'),(1,0,0),-.045-.135*lean)
        duplicate.primary(duplicate.b('Spine'),(1,0,0),.11*lean)"""),
("""        b.tex.image=bpy.data.images.load(str(ASSETS/'book_write'/f'{n:03d}.png'),check_existing=True)""",
"""        ink_frame=min(71,1+2*int((n-1)*.81))
        b.tex.image=bpy.data.images.load(str(ASSETS/'book_write'/f'{ink_frame:03d}.png'),check_existing=True)"""),
])
tweak('street',[
("""    actor.primary(actor.b('Spine'),(1,0,0),.255+.044*math.sin(n*.32))""",
"""    beat=(n-1)*math.tau/16
    actor.primary(actor.b('Hips'),(0,0,1),.105*math.sin(beat-.4))
    actor.primary(actor.b('Spine'),(1,0,0),.307+.061*math.sin(beat*2))
    actor.primary(actor.b('UpperChest'),(0,0,1),-.133*math.sin(beat))
    actor.primary(actor.b('Head'),(0,0,1),-.31*interval(n,24,40)*(1-interval(n,52,70)))
    actor.blink(n,(40,))"""),
("""        lift=.210*math.sin(math.pi*swing)""","""        lift=.265*math.sin(math.pi*swing)**1.16"""),
("""        actor.aim(actor.b('Foot',side),actor.world('Foot',side)+Vector((0,.158,-.070)))""",
"""        push=interval(q,.24,.43)*(1-interval(q,.46,.67))
        actor.aim(actor.b('Foot',side),actor.world('Foot',side)+Vector((0,.158,-.034-.126*push+.062*swing)))"""),
("""        forward=-.29*math.sin(math.tau*cyc)""","""        forward=-.32*math.sin(math.tau*cyc+.19)"""),
("""        look((.205-.48*k,-3.22+.59*k,1.43-.19*k),(.05-.15*k,2.81+1.25*k,1.30),37.5)""",
"""        if f<=42:
            look((.205-.40*k,-3.22+.59*k,1.43-.19*k),(.05-.15*k,2.45+1.25*k,1.28),37.5)
        else:
            follow=interval(f,43,96)
            y=-1.41+(n-1)*2.60/24
            look((1.19-.13*follow,y+1.74,1.45+.05*follow),(-.28,y-.10,1.34),36-3*follow)"""),
])
p=base/'build_reel.py'
s=p.read_text(encoding='utf-8-sig')
if 'revision_scene' not in s:
    s=s.replace('import sys','import sys\nimport os',1)
    s=s.replace("task=args[0]","task=args[0]\nrevision_scene=os.environ.get('KOBAN_PICTURE_REVISION')=='6'\nsuffix='_v6' if revision_scene else ''",1)
    for scene in ('street','station'):
        s=s.replace(f"ROOT/'{scene}.py'",f"ROOT/f'{scene}{{suffix}}.py'")
    p.write_text(s,encoding='utf-8')
