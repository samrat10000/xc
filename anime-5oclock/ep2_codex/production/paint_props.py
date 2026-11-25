"""Create the repeatable, hand-authored surface textures used by the remaining shots."""
from pathlib import Path
import math
import random
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from scipy.ndimage import gaussian_filter, zoom

root=Path(__file__).resolve().parent
assets=root/'assets'
assets.mkdir(exist_ok=True)
project=root.parents[1]
rng=np.random.default_rng(342)

def paper(name,base,size=(768,768),amplitude=6):
    w,h=size
    broad=zoom(rng.normal(0,1,(21,29)).astype(np.float32),(h/21,w/29),order=3)[:h,:w]
    tone=amplitude*(broad*.58+gaussian_filter(rng.normal(0,1,(h,w)),.55)*.30)
    color=np.clip(np.array(base)[None,None,:]+tone[...,None],0,255)
    im=Image.fromarray(np.uint8(color))
    im.save(assets/(name+'.png'))
    return im

paper('kitchen_plaster',(137,125,109))
paper('station_plaster',(132,131,123),amplitude=13)
paper('rubber_lino',(105,110,99),amplitude=9)
paper('asphalt',(116,106,111),amplitude=28)
paper('station_wood',(99,67,60),amplitude=9)
paper('washi_pane',(217,192,178),amplitude=8)
paper('paper_covers',(108,72,63),amplitude=11)

tiles=paper('tiles',(154,147,111),size=(900,880),amplitude=4)
d=ImageDraw.Draw(tiles,'RGBA')
for y in range(0,900,86):
    for x in range(0,900,89):
        g=int(rng.integers(-11,12))
        d.rounded_rectangle((x+2,y+2,x+87,y+84),radius=3,fill=(159+g,155+g,121+g,93),outline=(70,61,53,170),width=2)
        d.line([(x+7,y+6),(x+83,y+6)],fill=(242,216,158,48),width=2)
for x,y in [(240,296),(720,514),(414,711),(160,450)]:
    d.line([(x,y),(x+11,y+8),(x+8,y+12),(x+18,y+27)],fill=(68,54,45,110),width=1)
tiles.save(assets/'tiles.png')

wood=paper('counter',(105,73,65),size=(1152,768),amplitude=8)
d=ImageDraw.Draw(wood,'RGBA')
for _ in range(320):
    x,y=int(rng.integers(0,1150)),int(rng.integers(0,766))
    d.line([(x,y),(x+76,y+int(rng.integers(-2,3))),(x+136,y)],
           fill=(238,164,101,24) if _%3 else (42,34,45,68),width=int(rng.integers(1,4)))
wood.save(assets/'counter.png')

def font(size,jp=False):
    return ImageFont.truetype('C:/Windows/Fonts/'+('YuGothM.ttc' if jp else 'bahnschrift.ttf'),size)
def text(img,x,y,message,size,tint,mirror=False,jp=False, anchor='mm'):
    layer=Image.new('RGBA',img.size)
    ImageDraw.Draw(layer).text((x,y),message,font=font(size,jp),anchor=anchor,fill=tint)
    if mirror:layer=ImageOps.mirror(layer)
    img.paste(layer,(0,0),layer.getchannel('A'))

sign=Image.new('RGB',(820,280),'#cbc0a1')
d=ImageDraw.Draw(sign)
d.rectangle((8,8,809,268),outline='#554956',width=9)
text(sign,410,108,'桐山交番',95,'#323541',True,True)
text(sign,410,202,'KIRIYAMA  KOBAN',49,'#42394b',True)
sign.save(assets/'koban_sign.png')
sign=Image.new('RGB',(820,240),'#ded0a4')
d=ImageDraw.Draw(sign)
d.rectangle((12,12,807,227),outline='#654951',width=5)
text(sign,410,95,'山田商店',105,'#773f46',True,True)
text(sign,410,190,'酒  ·  たばこ',48,'#533a45',True,True)
sign.save(assets/'shop_sign.png')
cal=paper('calendar',(223,201,156),size=(440,530),amplitude=7)
d=ImageDraw.Draw(cal)
d.rectangle((0,0,440,101),fill='#574050')
text(cal,220,48,'1964',71,'#eadbc2',True)
text(cal,220,147,'11 月',53,'#5d444d',True,True)
for row in range(5):
    for col in range(7):
        num=row*7+col+1
        x=40+col*59;y=247+row*49
        d.rectangle((x-22,y-22,x+22,y+20),outline='#a9937d')
        if num<=30:text(cal,x,y,str(num),21,'#6d414e' if col in (0,6) else '#49404b',True)
cal.save(assets/'calendar.png')

default=Image.new('RGB',(660,1420),'#1f2330')
d=ImageDraw.Draw(default)
d.rounded_rectangle((245,45,415,72),radius=12,fill='#10151d')
d.rounded_rectangle((260,1340,400,1346),radius=3,fill='#938894')
default.save(assets/'phone_idle.png')
for clock in ('7:12','16:59'):
    image=default.copy()
    d=ImageDraw.Draw(image)
    d.rectangle((40,300,620,1090),fill='#24293b')
    text(image,333,504,clock,187,'#f4dbc6',True)
    text(image,338,192,'3%',53,'#e58c78',True)
    image.save(assets/('clock_'+clock.replace(':','')+'.png'))
image=default.copy()
text(image,330,420,'MOM',145,'#f6dfc7',True)
d=ImageDraw.Draw(image)
d.ellipse((252,1000,410,1158),fill='#739381')
d.arc((285,1033,377,1122),0,170,fill='#f5dec5',width=11)
image.save(assets/'phone_ring.png')


