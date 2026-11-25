from pathlib import Path
p=Path(__file__).resolve().parent

def write(file,text):
    compile(text,str(file),'exec')
    file.write_text(text,encoding='utf-8')

base=(p/'kitchen.py').read_text(encoding='utf-8-sig')
s=base.replace("""        mom_pose(mom,n,True)
        spoon.location.x=.076+.073*math.sin(n/24*5)
        spoon.rotation_euler.z=.14*math.sin(n/24*5)""","""        caught=interval(n,35,43)*(1-interval(n,56,65))
        held=min(n,39) if n<60 else n-18
        mom_pose(mom,held,True)
        mom.primary(mom.b('Neck'),(1,0,0),.068+.088*caught+.020*math.sin(n*.19))
        mom.primary(mom.b('Head'),(0,0,1),-.11-.15*caught)
        spoon.location.x=.076+.073*math.sin(held/24*5)
        spoon.rotation_euler.z=.14*math.sin(held/24*5)""",1)
s=s.replace('ob.hide_render=not 77<=f<=82','ob.hide_render=not 75<=f<=83',1)
write(p/'kitchen_v6.py',s)
base=(p/'phone_inserts.py').read_text(encoding='utf-8-sig')
s=base.replace("""    dusk=area('After time jump',(-.40,.22,.52),(0,0,0),14,'#e0815e',.54)
    def frame(f):""","""    dusk=area('After time jump',(-.40,.22,.52),(0,0,0),14,'#e0815e',.54)
    sam=Actor('sam')
    wall=mapped('Koban station wall',ASSETS/'station_plaster.png','80665d','bca08c')
    box('Koban clock reaction background',(0,1.25,1.28),(2.65,.071,2.38),wall,.005)
    key=area('Dusk after the jump',(-.32,-.13,1.72),(.04,.59,1.40),38,'#f5ad82',.33)
    def frame(f):""",1)
s=s.replace("""        look((.038-.014*k,-.144+.024*k,.259-.015*k),(0,.011,.002),61)""","""        sam.visible(f>=63)
        if f>=63:
            caught=interval(n,63,76)
            sam.pose((.01,.48,-.015),-.26+.46*caught)
            sam.arms_free(.04)
            sam.primary(sam.b('Head'),(1,0,0),.29-.43*caught)
            sam.primary(sam.b('Neck'),(0,0,1),.31*caught)
            sam.move_hair(n,.021+.047*math.sin(math.pi*caught))
            sam.blink(n,(67,))
            for shape in sam.brow_keys:
                shape.value=.47+.32*caught
            look((.166-.11*caught,-.39+.08*caught,1.44),(.037,.483,1.504),53)
        else:
            look((.038-.014*k,-.144+.024*k,.259-.015*k),(0,.011,.002),61)""",1)
write(p/'phone_inserts_v6.py',s)

f=p/'station_v6.py'
s=f.read_text(encoding='utf-8')
s=s.replace("""        sam.visible(outside)
        for child in d.children:""","""        sam.visible(True)
        for child in d.children:""",1)
s=s.replace("""            q=interval(f,36,120)
            look((.076+.063*q,-.96+.23*q,1.51-.14*q),(.024,.48,1.153-.075*q),42)""","""            q=interval(f,36,112)
            approach=interval(n,38,57)
            notice=interval(n,60,82)
            sam.pose((-.375+.18*approach,.127-.11*approach,-.043),1.44+.42*approach-.45*notice)
            sam.arms_free(.04)
            sam.primary(sam.b('Spine'),(1,0,0),.08+.30*notice)
            sam.primary(sam.b('Head'),(1,0,0),.06+.31*notice)
            sam.blink(n,(63,86))
            for key in sam.brow_keys:
                key.value=.26+.31*notice
            look((.522+.062*q,-.84+.21*q,1.52-.12*q),(-.121,.395,1.176-.071*q),41)""",1)
write(f,s)

creative=p/'build_reel.py'
s=creative.read_text(encoding='utf-8')
for name in ('kitchen','phone_inserts'):
    s=s.replace(f"ROOT/'{name}.py'",f"ROOT/f'{name}{{suffix}}.py'")
write(creative,s)
