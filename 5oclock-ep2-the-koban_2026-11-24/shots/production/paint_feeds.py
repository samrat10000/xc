"""Derive stage backdrops and call screens from the rendered footage."""
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

root=Path(__file__).resolve().parent
assets=root/'assets'
p=assets
if len(sys.argv)==1 or sys.argv[1]=='street':
    plates=root.parent/'03_the_crack'/'src'/'plates'
    order=['sky','high_cloud','far','ridge','valley','valley_mist','cedars']
    a=Image.open(plates/'sky.png').convert('RGBA')
    for n in order[1:]:
        a=Image.alpha_composite(a,Image.open(plates/(n+'.png')).convert('RGBA'))
    a=ImageOps.fit(a.convert('RGB'),(1500,995),Image.Resampling.LANCZOS,centering=(.62,.54))
    a.save(assets/'street_dawn.png')
    x=np.asarray(a,dtype=np.float32)/255
    y=np.linspace(0,1,a.height)[:,None]
    late=x*np.array([.94,.73,.79])+np.exp(-((y-.66)/.21)**2)[...,None]*[.17,.060,.026]
    Image.fromarray(np.uint8(np.clip(late,0,1)*255)).save(assets/'street_dusk.png')

def call_images(num):
    src=root/'qa'/f'feed_{num}'
    out=assets/f'call_{num}'
    out.mkdir(exist_ok=True)
    bg=Image.open(assets/'phone_idle.png').convert('RGB')
    rng=np.random.default_rng(627+int(num))
    typeface=ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf',61)
    small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',28)
    for i in range(1,97,2):
        f=(i-1)//4*4+1
        if num=='08' and 45<=i<=55:
            f=45
        im=Image.open(src/f'cel_{f:03d}.png').convert('RGB')
        # Retain the room and Sam's mirrored side in the right of the call frame.
        footage=ImageOps.fit(im,(616,828),Image.Resampling.LANCZOS,centering=(.54,.48))
        photo=Image.new('RGB',footage.size)
        if num=='08' and (24<i<34 or 41<i<48 or 58<i<65):
            photo=ImageOps.posterize(footage,5)
            for j in range(14):
                xx,yy=int(rng.integers(0,570)),int(rng.integers(130,760))
                ww,hh=int(rng.integers(11,91)),int(rng.integers(5,60))
                y2=min(828,yy+hh)
                x2=min(616,xx+ww)
                patch=footage.crop((xx,yy,x2,y2)).resize((max(1,ww//17),max(1,hh//17)),Image.Resampling.BILINEAR)
                patch=patch.resize((x2-xx,y2-yy),Image.Resampling.NEAREST)
                photo.paste(patch,(xx,yy))
        else:
            photo=footage
        frame=bg.copy()
        frame.paste(photo,(22,226))
        d=ImageDraw.Draw(frame)
        d.text((330,145),'MOM',font=typeface,fill='#f0d8c5',anchor='mm')
        d.rounded_rectangle((17,221,642,1060),radius=21,outline='#665966',width=7)
        d.text((330,1117),('RECONNECTING' if num=='08' and 43<=i<=58 else 'VIDEO CALL'),font=small,fill='#bbadad',anchor='mm')
        d.ellipse((290,1167,369,1246),fill='#a44f5f')
        d.arc((307,1193,351,1224),175,348,fill='#efd2c1',width=6)
        d.line((22,224,637,224),fill='#c29a83',width=4)
        frame.save(out/f'{i:03d}.png')
if len(sys.argv)>1 and sys.argv[1]=='calls':
    for num in ('08','09'):
        call_images(num)

