"""Finish EEVEE shots with a restrained episode grade and provide QA metadata."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from PIL import Image, ImageFilter
from scipy.ndimage import uniform_filter1d
import numpy as np
import sys

src,out=map(Path,sys.argv[1:3])
out.mkdir(parents=True,exist_ok=True)
shot=int(sys.argv[3])
frames=sorted(src.glob('cel_*.png'))
assert frames
w,h=Image.open(frames[0]).size
s=w/1080
y,x=np.ogrid[:h,:w]
u,v=x/w,y/h
rng=np.random.default_rng(525+shot)
grain=[rng.normal(0,1,(h,w)).astype(np.float32) for _ in range(4)]
vg=(1-.18*np.clip((((u-.51)*1.24)**2+(v-.46)**2)*1.96,0,1))[...,None]
shade=np.array([.085,.067,.102],dtype=np.float32)
motes=[(rng.uniform(.3,.96),rng.uniform(.19,.81),rng.uniform(1.1,2.9),rng.uniform(0,6.28)) for i in range(30)]
haze=np.exp(-((u-.82)/.43)**2-((v-.29)/.29)**2).astype(np.float32)
def image(a):
    return Image.fromarray(np.uint8(np.clip(a,0,1)*255+.5))
def finish_frame(p):
    f=int(p.stem[-3:])
    n=f-(f-1)%2
    a=np.asarray(Image.open(p).convert('RGBA'),dtype=np.float32)/255
    img=a[:,:,:3]*a[:,:,3:]+shade*(1-a[:,:,3:])
    if shot==11:
        tide=min(1,max(0,(f-41)/12))
        rgb0=np.array([.83,1.05,1.30],dtype=np.float32)
        rgb1=np.array([1.38,1.05,.73],dtype=np.float32)
        local=np.clip((.82-img.max(2,keepdims=True))/.54,0,1)
        img+=local*(img*(rgb0*(1-tide)+rgb1*tide-1)+.027)
    if shot==4:
        scale=np.clip((.83-img.max(2,keepdims=True))/.57,0,1)
        img*=1-.18*scale
    if shot==10 and (23<=f<=35 or 50<=f<=63):
        delta=min(abs(f-29.5),abs(f-56.5))
        smear=min(1,max(0,(7-delta)/7))
        pixels=max(3,round(71*s*smear))
        img=img*(1-.78*smear)+uniform_filter1d(img,pixels,axis=1,mode='nearest')*.78*smear
    if not (shot==14 and f>=114):
        if shot in (4,6,10,13):
            img+=np.array([.037,.022,.019],dtype=np.float32)*haze[...,None]
            for ax,ay,r,ph in motes:
                xx=int(w*(ax-.0004*n+.009*np.sin(n*.056+ph)))
                hit=max((np.exp(-((n-k)/3.2)**2) for k in (35,52,69,86)),default=0) if shot==13 else 0
                yy=int(h*((ay-n*.00023-hit*.009)%1))
                rad=max(2,int(r*s*2.4))
                if xx-rad<0 or yy-rad<0 or xx+rad>=w or yy+rad>=h: continue
                xx0,yy0=np.meshgrid(np.arange(-rad,rad+1),np.arange(-rad,rad+1))
                glow=np.exp(-(xx0**2+yy0**2)/(2*max(.4,r*s)**2))*haze[yy,xx]
                img[yy-rad:yy+rad+1,xx-rad:xx+rad+1]+=glow[...,None]*np.array([.22,.14,.081],dtype=np.float32)
        hi=img*np.clip((img.max(2,keepdims=True)-.81)/.19,0,1)
        img+=np.asarray(image(hi).filter(ImageFilter.GaussianBlur(19*s)),dtype=np.float32)*(.186/255)
        img=(img*1.021+np.array([.015,.011,.022],dtype=np.float32))*vg
        img+=grain[f%4][...,None]*.0072*(1.1-img.mean(axis=-1,keepdims=True))
    else:
        img[:,:,:]=0
    image(img).save(out/f'{f:03d}.png',compress_level=3)

# Frame transforms are independent and read the same cached grade arrays.
with ThreadPoolExecutor(max_workers=3) as worker:
    for _ in worker.map(finish_frame,frames):
        pass
