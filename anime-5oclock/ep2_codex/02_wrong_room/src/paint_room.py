"""Paint colour and weave for the washitsu and the reversed poster."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, zoom

OUT=Path(__file__).resolve().parent
rng=np.random.default_rng(114)

def texture(name, width, height, base, weave=None):
    y,x=np.mgrid[0:height,0:width].astype(np.float32)
    patches=zoom(rng.normal(0,1,(17,23)).astype(np.float32),(height/17,width/23),order=3)[:height,:width]
    n=patches*2.8+gaussian_filter(rng.normal(0,2.6,(height,width)),.55)
    if weave:
        warp=(x/weave[0]+.07*patches)%1
        weft=(y/weave[1]+.22*np.floor(x/weave[0])%1+.03*patches)%1
        n+= (np.sin(np.pi*weft)-.6)*15 - np.exp(-((warp-.08)/.11)**2)*6
    a=np.clip(np.array(base)[None,None,:]+n[...,None],0,255).astype(np.uint8)
    Image.fromarray(a).save(OUT / (name+'.png'))

texture('igusa',1024,1536,(126,116,84),(7.5,3.6))
texture('plaster',1024,1024,(118,109,102))
texture('quilt',768,768,(88,93,111),(2.8,3.4))
texture('washi',768,1024,(247,224,174))
im=Image.new('RGB',(500,710),'#d9ae7b')
d=ImageDraw.Draw(im)
d.rectangle((22,24,476,680),fill='#442e42')
d.rectangle((37,40,461,548),fill='#cb795f')
d.ellipse((156,112,348,305),fill='#edaa70')
d.polygon([(37,444),(108,341),(159,374),(232,274),(310,365),(365,309),(462,421),(462,548),(37,548)],fill='#5b4459')
d.polygon([(37,502),(107,415),(159,453),(201,416),(264,457),(323,420),(375,465),(461,429),(462,548),(37,548)],fill='#352f48')
font=ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf',72)
d.text((250,604),'KIRIYAMA',font=font,fill='#ebca91',anchor='mm')
im.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(OUT/'mirrored_poster.png')

