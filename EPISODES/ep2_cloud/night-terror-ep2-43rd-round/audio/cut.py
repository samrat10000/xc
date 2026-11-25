import numpy as np, subprocess
sr=48000
x=np.fromfile('/home/user/w/audio/mix/score.f32',np.float32).reshape(-1,2)
segs=[(0,144.0,6.0),(6.0,32.0,1.5),(7.5,33.5,1.0),(8.5,61.5,2.5),(11.0,64.0,6.5),(17.5,148.0,2.5),(20.0,2.0,5.5),(25.5,140.0,3.8)]
out=np.zeros((int(30*sr),2),np.float32); xf=int(.04*sr)
for i,(t,s,d) in enumerate(segs):
    a=x[int(s*sr):int((s+d)*sr)+xf].copy(); n=len(a)
    if i>0: a[:xf]*=np.linspace(0,1,xf)[:,None]**.5
    a[-xf:]*=np.linspace(1,0,xf)[:,None]**.5
    if i==2:  # tape stop on 7.5-8.5
        idx=np.cumsum(np.linspace(1,.15,n)); idx=idx[idx<n-1].astype(int); a=a[idx]; a=np.pad(a,((0,n-len(a)),(0,0))); a*=np.linspace(1,0,n)[:,None]
    o=int(t*sr); out[o:o+len(a)]+=a[:len(out)-o]
cut=int(29.3*sr); out[cut:]=0
# hard stop fade 8ms
out[cut-384:cut]*=np.linspace(1,0,384)[:,None]
out.tofile('/home/user/w/audio/mix/score30.f32')
