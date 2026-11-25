from pathlib import Path
p=Path(__file__).resolve().parent
ink=(p/'ink_book.py').read_text(encoding='utf-8-sig')
ink=ink.replace('Image,ImageDraw,ImageFilter','Image,ImageDraw,ImageFilter,ImageFont')
ink=ink.replace("parent/'assets'","parent/'assets'/'v6_book'").replace("root.mkdir(exist_ok=True)","root.mkdir(parents=True,exist_ok=True)")
start=ink.index('def side(')
end=ink.index('\nd=ImageDraw.Draw(right',start)
ink=ink[:start]+"""def japanese_page(phrases):
    mark=Image.new('L',page.size)
    pen=ImageDraw.Draw(mark)
    glyphs=ImageFont.truetype('C:/Windows/Fonts/YuGothM.ttc',36)
    heading=ImageFont.truetype('C:/Windows/Fonts/YuGothM.ttc',43)
    wobble=np.random.default_rng(64)
    pen.text((104,73),'霧山町　五時の規則',font=heading,fill=220)
    for index,paragraph in enumerate(phrases):
        x=107
        y=185+165*index
        for row,line in enumerate(paragraph):
            for column,char in enumerate(line):
                offset=float(wobble.uniform(-2.2,2.2))
                pen.text((x+column*37+offset,y+48*row+offset),char,font=glyphs,fill=int(wobble.integers(191,237)))
    tint=Image.new('RGB',page.size,(68,45,51))
    return Image.composite(tint,page,mark.filter(ImageFilter.GaussianBlur(.48)))

left=japanese_page([
    ('一、五時には家の中で', '　　耳をふさぐこと。'),
    ('二、放送で名前を', '　　呼ばれても返事をするな。'),
    ('三、いなくなった者の', '　　電話には出るな。'),
])
right=japanese_page([
    ('四、バス停の人数を数えるな。','　　いつも一人多い。'),
    ('五、赤いものを外に出すな。',),
    ('六、町の者が手を振っても', '　　振り返すな。'),
])
""" + ink[end:]
(p/'ink_book_v6.py').write_text(ink,encoding='utf-8')
s=(p/'station_v6.py').read_text(encoding='utf-8')
for asset in ('book_leaf.png','book_left.png','book_right.png','book_verso.png','book_write'):
    s=s.replace(f"ASSETS/'{asset}'",f"ASSETS/'v6_book'/'{asset}'")
s=s.replace("""    hand=isolated_hand()
    hand.shown""","""    hand=isolated_hand()
    reader=Actor('sam')
    backdrop=mapped('Rough koban walls',ASSETS/'station_plaster.png','85717d','dac6ad')
    box('Koban wall behind Sam',(0,1.14,1.30),(2.40,.08,2.50),backdrop,.002)
    box('Letter shelf',(-.57,1.02,1.31),(.55,.25,.046),a.oak,.004)
    for i in range(5):
        box('Archive folders',(-.75+i*.074,1.00,1.39),(.039,.12,.15+.021*(i%2)),a.paper,.002)
    hand.shown""",1)
s=s.replace("""        hand.visible(31<=n<=111)
        nudge=""","""        reader.visible(f<35)
        if f<35:
            lean=interval(n,5,29)
            reader.pose((.05,.704,-.226-.06*lean),-.24-.08*lean)
            reader.arms_free(.03)
            reader.primary(reader.b('Spine'),(1,0,0),.26+.22*lean)
            reader.primary(reader.b('Head'),(1,0,0),.15+.12*lean)
            reader.primary(reader.b('Neck'),(0,0,1),.18*(interval(n,17,29))
            reader.reach('L',(.195,.389,.888),(.76,.21,-.48),(-.034,-.065,-.015))
            reader.reach('R',(-.139,.402,.878),(-.90,.25,-.32),(.03,-.072,-.010))
            reader.blink(n,(18,))
            for key in reader.brow_keys:
                key.value=.28+.37*lean
        hand.visible(35<=n<=111)
        nudge=""",1)
s=s.replace("""        look((.079-.057*k,-.146+.071*k,1.482-.021*k),(.007-.029*k,.303,.842),42,math.radians(7-k*3))""","""        if f<35:
            look((.576-.111*k,-.702,1.312-.08*k),(.018,.65,1.167),43)
        else:
            look((.079-.057*k,-.146+.071*k,1.482-.021*k),(.007-.029*k,.303,.842),42,math.radians(7-k*3))""",1)
s=s.replace("Vector((.078,-.144,.052))","Vector((.048,-.136,.051))")
s=s.replace("""            s.reach(side,low.lerp(ears,u),pole,(0,-.013,.076))""","""            if n>=19 or side=='R':
                down=Vector((0,-.045,-.062))
                palm=down.lerp(Vector((0,-.013,.076)),u)
                s.reach(side,low.lerp(ears,u),pole,palm)""",1)
s=s.replace("ink_frame=min(71,1+2*int((n-1)*.81))","ink_frame=min(71,1+2*int((n-1)*.83))")
s=s.replace("f'{ink_frame:03d}.png'","f'{ink_frame:03d}.png'")
(p/'station_v6.py').write_text(s,encoding='utf-8')
s=(p/'street_v6.py').read_text(encoding='utf-8')
old="""    card('Far valley plane',[(-38,45,-11),(38,45,-11),(38,45,31),(-38,45,31)],bmat)"""
assert old in s
s=s.replace(old,old+"""
    card('Western wrap for street tracking view',[(-38,45,-11),(-38,-45,-11),(-38,-45,31),(-38,45,31)],bmat)
    card('Southern wrap for street tracking view',[(-38,-45,-11),(38,-45,-11),(38,-45,31),(-38,-45,31)],bmat)""")
s=s.replace("""        person.reach(side,p,(.82*sign,.31,-.46),(.035*sign,-.052,-.071))""","""        forearm=Vector((.025*sign,-.049,-.073))
        person.reach(side,p,(.82*sign,.31,-.46),forearm)
        for digit,amount in (('Index',.52),('Middle',.63),('Ring',.67),('Little',.76)):
            for segment in (1,2,3):
                bone=person.bones.get(f'J_Bip_{side}_{digit}{segment}')
                if bone is not None:
                    bone.rotation_quaternion=Quaternion((0,0,1),-sign*amount)""")
s=s.replace("""            turn=interval(n,65+i*2,91+i*2)
            a.pose((x,y,-.01),.48+turn*(math.pi-.39))
            a.arms_free(.035)""","""            turn=interval(n,65+i*2,91+i*2)
            lift=math.sin(math.pi*turn)
            a.pose((x+.13*lift,y-.12*turn,-.01+.026*lift),.48+turn*(math.pi-.39))
            a.arms_free(.035+.074*lift)
            a.blink(n,(63+i*3,101))
            for side,sign in (('L',1),('R',-1)):
                leg=a.b('UpperLeg',side)
                a.primary(leg,(1,0,0),-.13*sign*math.sin(math.tau*turn))
                a.primary(a.b('LowerLeg',side),(1,0,0),.19*max(0,sign*math.sin(math.tau*turn)))""",1)
(p/'street_v6.py').write_text(s,encoding='utf-8')
