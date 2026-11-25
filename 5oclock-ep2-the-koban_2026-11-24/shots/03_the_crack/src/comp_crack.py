"""Composite eight painted exterior planes behind the animated bedroom cel."""
import json,math,sys
from pathlib import Path
from PIL import Image,ImageFilter
import numpy as np

here=Path(__file__).resolve().parent
inp,out=map(Path,sys.argv[1:3])
out.mkdir(parents=True,exist_ok=True)
revision=int(sys.argv[3])
files=sorted(inp.glob('cel_*.png'))
assert files
w,h=Image.open(files[0]).size
sx=w/1080
yy,xx=np.ogrid[:h,:w]
u,v=xx/w,yy/h
def px(im):
    return np.asarray(im,dtype=np.float32)/255
def rgb(x):
    return Image.fromarray(np.uint8(np.clip(x,0,1)*255+.5))
def resize_crop(image,zoom,pan_x,pan_y):
    iw,ih=image.size
    ww,hh=iw/1.10/zoom,ih/1.10/zoom
    cx,cy=iw/2+pan_x,ih/2+pan_y
    return image.resize((w,h),Image.Resampling.BICUBIC,(cx-ww/2,cy-hh/2,cx+ww/2,cy+hh/2))

# Coefficients are authored per depth. Wind moves cloud layers independently of the camera.
layers=[
 ('sky',.004,.12,.08,0,0),('fissure',.008,.21,.12,0,0),
 ('high_cloud',.012,.32,.14,7,12),('listener',.013,.36,.16,0,0),
 ('crown_cloud',.020,.44,.21,34,22),('far',.024,.59,.24,0,0),
 ('ridge',.033,.71,.29,0,0),('valley',.041,.80,.39,0,0),
 ('valley_mist',.046,.92,.46,14,7),('cedars',.057,1.0,.57,0,0)]
plates={name: Image.open(here/'plates'/f'{name}.png').convert('RGBA') for name,*_ in layers}
rng=np.random.default_rng(329)
grain=[rng.normal(0,1,(h,w)).astype(np.float32) for _ in range(4)]
motes=[(rng.uniform(.49,.99),rng.uniform(.16,.92),rng.uniform(1.1,2.3),rng.uniform(0,6.28)) for _ in range(38)]
vignette=(1-.19*np.clip((((u-.52)*1.15)**2+(v-.48)**2)*1.93,0,1)).astype(np.float32)[...,None]
glare=np.exp(-(((u-.95)/.48)**2+((v-.36)/.24)**2)).astype(np.float32)
metrics=[]
for path in files:
    f=int(path.stem[-3:])
    t=(f-1)/95
    k=t*t*(3-2*t)
    bg=None
    scale_md={}
    for name,z,dx,dy,windx,windy in layers:
        move_x=(13*dx)*k+windx*t
        move_y=(-17*dy)*k+windy*t
        if revision>=2 and name=='crown_cloud':
            move_x+=8*t
            move_y+=5*t
        if revision>=3 and name=='crown_cloud':
            move_y+=22*t
        if revision>=3 and name=='high_cloud':
            move_x+=4*t
        clip=resize_crop(plates[name],1+z*k,move_x,move_y)
        bg=clip if bg is None else Image.alpha_composite(bg,clip)
        scale_md[name]=[1+z*k,move_x,move_y]
    wall=Image.open(path).convert('RGBA')
    cel=px(wall)
    b=px(bg)[...,:3]
    a=cel[...,3:]
    a_dilate=px(wall.getchannel('A').filter(ImageFilter.GaussianBlur(4*sx)))[...,None]
    edge=np.clip(a-a_dilate,0,1)
    if revision>=3:
        warm_window=np.exp(-(((u-.90)/.52)**2+((v-.43)/.32)**2)).astype(np.float32)[...,None]
        b=np.clip(b+warm_window*np.array([.116,.111,.092],dtype=np.float32),0,1)
    if revision>=4:
        horizon=np.exp(-(((u-.54)/.38)**2+((v-.423)/.089)**2)).astype(np.float32)[...,None]
        b=np.clip(b*np.array([.95,.951,.978],dtype=np.float32)+horizon*np.array([.194,.160,.113],dtype=np.float32),0,1)
        cel[:,:,:3]*=np.array([.827,.844,.905],dtype=np.float32)
    img=cel[...,:3]*a+b*(1-a)
    img+=edge*glare[...,None]*np.array([.32,.222,.16],dtype=np.float32)
    img+=glare[...,None]*np.array([.056,.034,.018],dtype=np.float32)
    for ax,ay,size,phase in motes:
        x=int(w*(ax+.008*math.sin(t*4+phase)-t*.021))
        y=int(h*(ay-t*.022))
        r=max(2,int(size*sx*2.5))
        if x-r<0 or y-r<0 or x+r>=w or y+r>=h: continue
        q=np.arange(-r,r+1)
        dot=np.exp(-(q[:,None]**2+q[None,:]**2)/(2*(max(.42,size*sx)**2)))
        # Particles read in the interior sun beam, including against the dark shoulder.
        dot*=float(glare[y,x])*(.68+.32*math.sin(t*10+phase))
        img[y-r:y+r+1,x-r:x+r+1]+=dot[...,None]*np.array([.20,.143,.079],dtype=np.float32)
    hi=img*np.clip((img.max(axis=-1,keepdims=True)-.81)/.19,0,1)
    img+=px(rgb(hi).filter(ImageFilter.GaussianBlur(19*sx)))*.18
    img=(img*1.016+np.array([.016,.012,.025],dtype=np.float32))*vignette
    img+=grain[f%4][...,None]*.0076*(1.08-img.mean(axis=-1,keepdims=True))
    rgb(img).save(out/f'{f:03d}.png',compress_level=3)
    metrics.append({'frame':f,'planes':scale_md,'opening_fraction':float((a<.5).mean())})
    print(f'composite {f:03d}',flush=True)
(out.parent/(out.name+'_layers.json')).write_text(json.dumps(metrics),encoding='utf-8')

