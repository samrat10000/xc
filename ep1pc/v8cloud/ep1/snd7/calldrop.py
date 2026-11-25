# Turn a phone line into a real call drop: clean start, choppy packet loss + stutter, cut mid-word, click, dead line. No beeps.
import numpy as np, subprocess, sys
SR=48000; src, dst = sys.argv[1], sys.argv[2]; T_CHOP=float(sys.argv[3]); T_CUT=float(sys.argv[4])
a=np.frombuffer(subprocess.run(['ffmpeg','-v','quiet','-i',src,'-ac','1','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,np.float32).copy()
rng=np.random.default_rng(7); out=a[:int(T_CUT*SR)].copy(); i=int(T_CHOP*SR)
while i<len(out):
    seg=int(rng.uniform(.04,.11)*SR); r=rng.random()
    if r<.38: out[i:i+seg]=rng.normal(0,.002,len(out[i:i+seg]))            # packet lost: near silence
    elif r<.55 and i>int(.06*SR):                                          # stutter: repeat last grain
        g=int(.05*SR); gr=out[i-g:i]; n=min(seg,len(out)-i); out[i:i+n]=np.resize(gr,n)*.8
    else: out[i:i+seg]=np.round(out[i:i+seg]*24)/24                        # crunchy low-bitrate
    k=int(.003*SR); out[i:i+k]*=np.linspace(0,1,len(out[i:i+k])); i+=seg
f=int(.004*SR); out[-f:]*=np.linspace(1,0,f)                               # hard cut mid-word
click=np.zeros(int(.02*SR),np.float32); click[:40]=np.hanning(40)*.25
tail=rng.normal(0,.003,int(.12*SR)).astype(np.float32)*np.linspace(1,0,int(.12*SR))
res=np.concatenate([out,click,tail,np.zeros(int(.3*SR),np.float32)]).astype(np.float32)
subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar',str(SR),'-ac','1','-i','-',dst],input=res.tobytes(),check=True); print('ok',dst)
