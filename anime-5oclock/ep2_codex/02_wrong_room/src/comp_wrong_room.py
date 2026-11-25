"""Composite aligned planar reflection, dawn veiling glare, bloom, and grain."""
import json, math, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def as_image(a):
    return Image.fromarray(np.uint8(np.clip(a*255+.5,0,255)))

def px(image):
    return np.asarray(image,dtype=np.float32)/255

def blur(image,sigma):
    return px(image.filter(ImageFilter.GaussianBlur(sigma)))

inp,out=map(Path,sys.argv[1:3])
out.mkdir(parents=True,exist_ok=True)
revision=int(sys.argv[3])
meta=json.loads((inp/'frame_meta.json').read_text())
sample=Image.open(next(inp.glob('room_*.png')))
w,h=sample.size
s=w/1080
y,x=np.ogrid[0:h,0:w]
u,v=x/w,y/h
rng=np.random.default_rng(15)
grain=[rng.normal(0,1,(h,w)).astype(np.float32) for _ in range(5)]
motes=[(rng.uniform(.42,.98),rng.uniform(.10,.73),rng.uniform(1.1,2.8),rng.uniform(0,6.28)) for _ in range(41)]
vignette=(1-.22*np.clip((((u-.50)*1.2)**2+(v-.43)**2)*2.35,0,1))[...,None]
dawn=np.exp(-(((u-.84)/.36)**2+((v-.29)/.37)**2)).astype(np.float32)
haze=np.array([.095,.052,.021],dtype=np.float32)
purple=np.array([.018,.012,.032],dtype=np.float32)
for f,d in sorted((int(k),v) for k,v in meta.items()):
    main=Image.open(inp/f'room_{f:03d}.png').convert('RGBA')
    c=px(main)
    img=c[:,:,:3]*c[:,:,3:]+np.array([.071,.053,.089],dtype=np.float32)*(1-c[:,:,3:])
    if f>=73:
        reflection=np.flip(px(Image.open(inp/f'mirror_{f:03d}.png').convert('RGBA')),axis=1)
        mask=Image.new('L',(w,h))
        poly=[(px0*w,py0*h) for px0,py0 in d['screen']]
        ImageDraw.Draw(mask).polygon(poly,fill=255)
        mask=blur(mask,.75*s)[...,None]
        src=reflection[:,:,:3]*np.array([.60,.65,.74],dtype=np.float32)+[.019,.020,.033]
        # Soft flare stays anchored to the phone glass and brightens one edge only.
        sheen=np.maximum(0,1-np.abs((u-.5)*.86-(v-.55)+.17)/.14).astype(np.float32)[...,None]
        img=(img+(src-img)*mask*reflection[:,:,3:]*.93).astype(np.float32)
        img+=mask*sheen*np.array([.057,.049,.047],dtype=np.float32)
        img*=.951
    else:
        img+=dawn[...,None]*haze*(1 if revision>=2 else .84)
        if revision>=3:
            img*=1-.165*np.clip((.80-img.max(axis=2,keepdims=True))/.56,0,1)
        for a,b,rad,phase in motes:
            xp=int(w*(a+.012*math.sin(f*.065+phase)-f*.00031))
            yp=int(h*(b-f*.00032))
            r=max(2,int(rad*s*3))
            if xp-r<0 or yp-r<0 or xp+r>=w or yp+r>=h:
                continue
            q=np.arange(-r,r+1)
            dot=np.exp(-(q[None,:]**2+q[:,None]**2)/(2*max(.45,rad*s)**2))
            intensity=dawn[yp,xp]*(.7+.3*math.sin(f*.115+phase))
            img[yp-r:yp+r+1,xp-r:xp+r+1]+=dot[...,None]*intensity*np.array([.30,.20,.102],dtype=np.float32)
    bright=img*np.clip((img.max(2,keepdims=True)-.80)/.20,0,1)
    img+=blur(as_image(bright),22*s)*.21
    img=(img*1.025+purple)*vignette
    img+=grain[f%5][...,None]*.0078*(1.13-img.mean(2,keepdims=True))
    as_image(img).save(out/f'{f:03d}.png',compress_level=3)
    print(f'comp {f:03d}',flush=True)

