import numpy as np, wave
from pathlib import Path
sr=44100
mix=np.zeros((15*sr,2))
rng=np.random.default_rng(507)
def put(at,s,pan=.5):
    i=int(at*sr)
    s=s[:len(mix)-i]
    mix[i:i+len(s)]+=s[:,None]*np.sqrt([1-pan,pan])
def axis(d):return np.arange(int(d*sr))/sr
def bell(at,f,pan,level=.42):
    t=axis(2.6)
    for ratio,amp,decay in [(1,1,1.2),(2.01,.35,.7),(2.72,.2,.42),(4.16,.11,.25)]:
        s=level*amp*np.sin(2*np.pi*f*ratio*t)*np.exp(-t/decay)*np.minimum(t/.006,1)*np.minimum((2.6-t)/.06,1)
        put(at,s,pan)
        put(at+.14,s*.19,1-pan)
for at,f in [(0.12,587.33),(1.04,493.88),(1.96,440)]:bell(at,f,.74)
t=axis(6)
put(0,.055*np.sin(2*np.pi*(49*t+.16*np.sin(2*t)))*np.sin(np.pi*t/6),.48)
t=axis(2.8)
noise=np.convolve(rng.normal(size=len(t)),np.ones(19)/19,'same')
put(3.17,(noise*.17+.05*np.sin(2*np.pi*(142*t+22*t*t)))*np.sin(np.pi*t/2.8)**1.6,.25)
t=axis(.22)
put(5.98,.8*rng.normal(size=len(t))*np.exp(-t*65)+.65*np.sin(2*np.pi*(67*t+1-np.exp(-35*t)))*np.exp(-t*24),.51)
t=axis(3.05)
for k in range(1,7):
    put(7.13,.12/k*np.sin(2*np.pi*(54*k*t+2*k*np.sin(t*1.5)))*np.sin(np.pi*t/3.05)**2,.13*k)
bell(10.47,329.63,.5,.56)
t=axis(2.25)
breath=np.convolve(rng.normal(size=len(t)),np.ones(9)/9,'same')
put(12.32,.25*breath*np.sin(np.pi*t/2.25)**2,.52)
for at in (13.17,13.54,13.86):
    t=axis(.32)
    put(at,.46*np.sin(2*np.pi*(57*t+.8*(1-np.exp(-18*t))))*np.exp(-t*15),.5)
mix=np.tanh(mix*1.8)
with wave.open('fourth-note.wav','wb') as w:
    w.setparams((2,2,sr,0,'NONE','not compressed'))
    w.writeframes((mix*(29000/np.max(abs(mix)))).astype('<i2').tobytes())
