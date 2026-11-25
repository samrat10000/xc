"""Render The Fourth Note at 24 fps from matched animation poses and the approved score."""
import math
import os
import subprocess
import shutil
from pathlib import Path
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont

root=Path(__file__).resolve().parent
fps=24
w,h=540,960
y,x=np.mgrid[:h,:w].astype(np.float32)
def ramp(t,start,end):
    u=np.clip((t-start)/(end-start),0,1)
    return u*u*(3-2*u)

def load_strip(name):
    strip=cv2.imread(str(root/(name+'.png')))
    return [cv2.resize(strip[60:964,i*512+3:(i+1)*512-3],(w,h),interpolation=cv2.INTER_LANCZOS4) for i in range(3)]

def field(a,b):
    dis=cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    dis.setFinestScale(0)
    return dis.calc(cv2.cvtColor(a,cv2.COLOR_BGR2GRAY),cv2.cvtColor(b,cv2.COLOR_BGR2GRAY),None)
frames={name:load_strip(name) for name in ('sam','pull','bell')}
flows={}
for name,strip in frames.items():
    for i in range(2):
        flows[name,i]=(field(strip[i],strip[i+1]),field(strip[i+1],strip[i]))
def sample(name,pose):
    i=min(1,int(pose)); u=pose-i
    a,b=frames[name][i:i+2]
    if u<.001:return a
    if u>.999:return b
    f,g=flows[name,i]
    def warp(im,motion,k):
        return cv2.remap(im,x-k*motion[:,:,0],y-k*motion[:,:,1],cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT101)
    return cv2.addWeighted(warp(a,f,u),1-u,warp(b,g,1-u),u,0)

def camera(im,zoom,cx,cy):
    return cv2.warpAffine(im,np.float32([[zoom,0,w/2-zoom*cx],[0,zoom,h/2-zoom*cy]]),(w,h),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT101)
rng=np.random.default_rng(50)
rain=rng.uniform([0,0,0],[w+24,h+45,1],(65,3))
def shot(t):
    if t<.75:
        return camera(sample('bell',0),2.8,123+2*t,556+t)
    if t<3.17:
        p=.04+.87*ramp(t,1.76,2.32)
        return camera(sample('sam',p),1.28+.08*ramp(t,.75,3.17),282,365)
    if t<5.42:
        p=.02+.9*ramp(t,3.85,4.49)+.08*ramp(t,4.55,5.42)
        return camera(sample('pull',p),1.012+.045*ramp(t,3.17,5.42),270,480)
    if t<5.96:
        return camera(sample('pull',1),2.4,330+6*math.sin(t*23),819)
    if t<7.16:
        p=1+ramp(t,5.96,6.32)
        shock=math.exp(-8*(t-5.96))*math.sin(58*(t-5.96))
        return camera(sample('pull',p),1.07,270+12*shock,485+9*shock)
    if t<10.46:
        p=.04+.96*ramp(t,7.48,9.98)
        return camera(sample('bell',p),1.03+.12*ramp(t,7.16,10.46),272,461)
    if t<13.12:
        p=1+ramp(t,10.46,10.97)
        jitter=math.sin(2*math.pi*9*t)*math.exp(-3*(t-10.46))
        return camera(sample('sam',p),1.54+.12*ramp(t,10.46,13.12),297+1.8*jitter,416)
    p=1+ramp(t,13.12,13.52)
    return camera(sample('bell',p),1.25+.52*ramp(t,13.28,14.36),306+10*p,338-26*p)
def title():
    canvas=Image.new('RGB',(w,h),(15,19,24)); d=ImageDraw.Draw(canvas)
    fonts=Path(os.environ['WINDIR'])/'Fonts'
    for s,n,sz,yy,col in [('5 O\u2019 C L O C K','consola.ttf',18,412,'#ce9581'),('The Fourth Note','georgia.ttf',49,478,'#eae4d4'),('E P I S O D E   0 1','consola.ttf',14,543,'#b7b5a9')]:
        d.text((w/2,yy),s,font=ImageFont.truetype(str(fonts/n),sz),anchor='mm',fill=col)
    return cv2.cvtColor(np.array(canvas),cv2.COLOR_RGB2BGR)
card=title()
def frame(index):
    t=index/fps
    if t>=14.34:return card
    im=shot(t)
    rainlayer=im.copy()
    for rx,ry,depth in rain:
        xx=int((rx-24*t*(1+depth))%(w+24))-12
        yy=int((ry+t*(275+290*depth))%(h+45))-24
        cv2.line(rainlayer,(xx,yy),(xx-2,yy+int(7+11*depth)),(178,180,183),1,cv2.LINE_AA)
    return cv2.addWeighted(im,.87,rainlayer,.13,0)
exe=shutil.which('ffmpeg') or str(next((Path(os.environ['LOCALAPPDATA'])/'Microsoft/WinGet/Packages').glob('yt-dlp.FFmpeg*/**/ffmpeg.exe')))
sound=root.parents[1]/'episode-01-pitch'/'fourth-note.wav'
out=root.parent/'5oclock-the-fourth-note.mp4'
args=[exe,'-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s','540x960','-r','24','-i','pipe:0','-i',str(sound),'-vf','scale=1080:1920:flags=lanczos:out_color_matrix=bt709','-c:v','libx264','-crf','16','-preset','fast','-pix_fmt','yuv420p','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709','-c:a','aac','-b:a','256k','-movflags','+faststart','-t','15',str(out)]
with subprocess.Popen(args,stdin=subprocess.PIPE) as encoder:
    for i in range(360):encoder.stdin.write(frame(i).tobytes())
    encoder.stdin.close()
    if encoder.wait():raise RuntimeError('Export failed')
