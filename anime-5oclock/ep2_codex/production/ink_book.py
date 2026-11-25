"""Draw the actual notebook lettering from single-stroke paths and grow ink into the fibres."""
from pathlib import Path
import math
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy.ndimage import gaussian_filter,zoom

root=Path(__file__).resolve().parent/'assets'
root.mkdir(exist_ok=True)
w,h=780,1060
alphabet={
 'A':'05 21 45|13 33','B':'05 00 30 41 32 02|32 43 44 35 05','C':'40 10 01 04 15 45','D':'05 00 20 41 44 25 05',
 'E':'40 00 05 45|02 32','F':'05 00 40|02 32','G':'40 10 01 04 15 45 43 23','H':'00 05|40 45|02 42',
 'I':'10 30|20 25|15 35','J':'10 40 44 35 15 04','K':'00 05|40 02 45','L':'00 05 45','M':'05 00 22 40 45',
 'N':'05 00 45 40','O':'10 30 41 44 35 15 04 01 10','P':'05 00 30 41 42 33 03','Q':'10 30 41 44 35 15 04 01 10|33 46',
 'R':'05 00 30 41 42 33 03|23 45','S':'40 10 01 12 33 44 35 05','T':'00 40|20 25','U':'00 04 15 35 44 40',
 'V':'00 25 40','W':'00 15 22 35 40','X':'00 45|40 05','Y':'00 22 40|22 25','Z':'00 40 05 45',
 '0':'10 30 41 44 35 15 04 01 10',':':'21 22|24 25','1':'11 20 25|15 35','2':'01 10 30 41 42 15 45','3':'00 40 22 42 44 35 05','4':'00 03 43|40 45',
 '5':'40 00 02 33 44 35 05','6':'40 11 03 04 15 35 44 43 32 03','7':'00 40 15','8':'12 01 10 30 41 32 12 03 04 15 35 44 43 32',
 '.':'24 25',',':'24 15','!':'20 23|25 26',"'":'20 21','-':'02 42'
}
rules=[
 ('1. BE INDOORS,','WITH YOUR EARS','COVERED, AT 5:00.'),
 ('2. IF THE SPEAKER','SAYS YOUR NAME,','DO NOT ANSWER.'),
 ('3. NEVER PICK UP','A RINGING PHONE','THAT BELONGS TO','ONE OF THE GONE.'),
 ("4. DON'T COUNT THE","PEOPLE AT THE BUS","STOP. THERE IS","ALWAYS ONE MORE."),
 ('5. NOTHING RED','OUTSIDE.'),
 ("6. IF SOMEONE FROM","THE TOWN WAVES AT","YOU, DON'T WAVE BACK.")
]
rng=np.random.default_rng(818)
pulp=zoom(rng.normal(0,1,(33,23)).astype(np.float32),(h/33,w/23),order=3)[:h,:w]
grit=rng.normal(0,1,(h,w)).astype(np.float32)
y,x=np.ogrid[:h,:w]
edge=np.exp(-np.minimum(np.minimum(y,h-1-y),np.minimum(x,w-1-x))/18)
grain=6*pulp+grit*2.9-edge*42
base=np.clip(np.array([215,186,133])+grain[...,None],0,255)
page=Image.fromarray(np.uint8(base))
d=ImageDraw.Draw(page,'RGBA')
for row in range(74,h-35,36):
    d.line((42,row,w-44,row),fill=(104,81,86,37),width=1)
d.line((81,25,79,h-32),fill=(124,61,70,86),width=3)
for _ in range(1500):
    px,py=int(rng.integers(0,w)),int(rng.integers(0,h))
    d.line([(px,py),(px+int(rng.integers(-4,5)),py+int(rng.integers(0,5)))],fill=(102,73,52,20),width=1)

page.save(root/'book_verso.png')

def text_segments(text,x,y,height,seed):
    rn=np.random.default_rng(seed)
    cell=height/5
    xx=float(x)
    for letter in text.upper():
        if letter==' ':
            xx+=cell*3.25
            continue
        strokes=alphabet.get(letter, '')
        stretch=float(rn.uniform(.82,1.07))
        slant=float(rn.uniform(-.20,.22))
        shift=float(rn.uniform(-cell*.39,cell*.39))
        for stroke in strokes.split('|'):
            if not stroke:continue
            yield [(round(xx+int(q[0])*cell*stretch-int(q[1])*slant),
                    round(y+int(q[1])*cell+shift+.003*(xx-x))) for q in stroke.split()]
        xx+=cell*(4.8*stretch if letter not in ".,'" else 2.8)+1.15

def draw_strokes(img,segments,part=1,tint=(68,45,51),width=4):
    layer=Image.new('L',img.size)
    d=ImageDraw.Draw(layer)
    distance=sum(math.dist(p,q) for seg in segments for p,q in zip(seg,seg[1:]))
    allowed=distance*part
    for seg in segments:
        for p,q in zip(seg,seg[1:]):
            if allowed<=0:break
            l=math.dist(p,q)
            end=tuple(int(a+(b-a)*min(1,allowed/max(.01,l))) for a,b in zip(p,q))
            d.line((p,end),fill=237,width=width)
            d.ellipse((end[0]-width/2,end[1]-width/2,end[0]+width/2,end[1]+width/2),fill=223)
            allowed-=l
    if part<=0:return img.copy()
    ink=np.asarray(layer,dtype=np.float32)
    bleed=gaussian_filter(ink,1.31)*(1.0+grit*.20)
    a=Image.fromarray(np.uint8(np.clip(ink*.9+bleed*.37,0,255)))
    out=img.copy()
    out.paste(tint,(0,0,w,h),a)
    return out

def side(rule_list):
    art=page.copy()
    segments=[]
    top=145
    segments.extend(text_segments('TANAKA',111,66,31,174))
    for i,lines in enumerate(rule_list):
        for j,line in enumerate(lines):
            segments.extend(text_segments(line,106+(20 if j else 0),top,26,i*129+j*47+17))
            top+=42
        top+=45
    return draw_strokes(art,segments,1,width=4)

left=side(rules[:3])
right=side(rules[3:])
d=ImageDraw.Draw(right,'RGBA')
strip=[(97,771),(134,765),(157,778),(178,763),(196,773),(228,750),(261,772),(290,756),(321,770),
       (346,749),(373,775),(408,761),(437,769),(467,749),(499,770),(514,755),(550,767),(586,754),(621,776),(655,766),(677,779)]
fine=[]
for i,(x0,y0) in enumerate(strip):
    fine.append((x0,int(771+(y0-771)*.57)))
    if i+1<len(strip):
        x1,y1=strip[i+1]
        for q in (.29,.63,.84):
            fine.append((int(x0+(x1-x0)*q),int(771+(y0+(y1-y0)*q-771)*.49+rng.integers(-8,8))))
strip=fine
d.polygon(strip+[(675,807),(97,806)],fill=(120,91,67,220))
d.line(strip,fill=(242,222,170,227),width=3)
for px,py in strip:
    d.line([(px,py),(px+6,py+8)],fill=(240,217,164,143),width=1)
d.line((103,813,673,819),fill=(151,112,83,150),width=3)
right=draw_strokes(right,list(text_segments('7.',114,733,33,61)),1,width=4)
left.save(root/'book_left.png')
right.save(root/'book_right.png')
leaf=page.copy()
leaf=draw_strokes(leaf,list(text_segments('FIELD RECORD',111,88,35,90)),1,width=4)
leaf=draw_strokes(leaf,list(text_segments('11 DAYS',110,256,56,92)),1,width=5)
leaf.save(root/'book_leaf.png')
segments=list(text_segments("8. DON'T LET YOURSELF",113,880,29,79))
segments+=list(text_segments('IN.',137,936,35,80))
writing=root/'book_write'
writing.mkdir(exist_ok=True)
for f in range(1,73,2):
    t=max(0,min(1,(f-11)/45))
    # Hold after the final stroke long enough to read.
    draw_strokes(right,segments,t,tint=(87,39,50),width=4).save(writing/f'{f:03d}.png')

