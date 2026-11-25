import numpy as np, subprocess, scipy.signal as ss, json
SR=48000; T=31.0; N=int(T*SR)
D='/home/user/w/audio/ov/'
def load(f,a=None,b=None,rate=1.0):
    cmd=['ffmpeg','-v','error']+(['-ss',str(a)] if a is not None else [])+(['-to',str(b)] if b is not None else [])+['-i',D+f]
    af=[] if rate==1.0 else ['-af',f'asetrate={int(SR*rate)},aresample={SR}']
    x=np.frombuffer(subprocess.run(cmd+af+['-ac','2','-ar',str(SR),'-f','f32le','-'],capture_output=True).stdout,np.float32).reshape(-1,2).copy()
    n=min(len(x),int(.006*SR)); x[:n]*=np.linspace(0,1,n)[:,None]
    m=min(len(x),int(.03*SR)); x[-m:]*=np.linspace(1,0,m)[:,None]
    pk=np.abs(x).max()+1e-9; return x/pk
L={k:np.zeros((N,2),np.float32) for k in ['fx','amb','fol']}
def put(bus,x,t,db=0,pan=0.0,lp=None,hp=None):
    if lp: x=ss.sosfilt(ss.butter(4,lp,'low',fs=SR,output='sos'),x,axis=0)
    if hp: x=ss.sosfilt(ss.butter(2,hp,'high',fs=SR,output='sos'),x,axis=0)
    g=10**(db/20); x=x*g*np.array([np.sqrt(.5-pan/2)*1.414,np.sqrt(.5+pan/2)*1.414])
    o=int(t*SR); 
    if o>=N: return
    n=min(len(x),N-o); L[bus][o:o+n]+=x[:n]
gun=load('gun/0_446277fa.mp3',.94,1.64)
mg=load('mg/1_734e80d6.mp3',0,1.02); mg2=load('mg/1_734e80d6.mp3',1.14,2.48)
hmg=load('hmg/0_f7ac6a73.mp3',0.04,1.97); hmg2=load('hmg/0_f7ac6a73.mp3',4.12,5.64)
rack=load('cock/0_bb3db3ad.mp3',0.10,0.60)
dry=load('empty/5_26306e05.mp3',8.79,9.19)
brass=load('brass/0_129ed95f.mp3',29.77,30.28); brass2=load('brass/0_129ed95f.mp3',41.49,42.74)
splat=load('splat/1_62e14da4.mp3',0,1.08); splat2=load('splat/1_62e14da4.mp3',1.47,1.84)
ric=load('ricochet/1_7747df52.mp3',0.01,.89)
boom=load('boom/4_4eefa3d1.mp3',0,1.03)
growl=load('growl/7_79331cd9.mp3',21.10,25.78,.85)
roarA=load('roar/6_708234ec.mp3',rate=.62); roarB=load('roar/2_5a7b5bed.mp3',rate=.7)
steps=load('flow_roar.m4a',53.98,55.98); steps2=load('flow_roar.m4a',5.98,7.92)
eng=load('engine/1_a32f8111.mp3',22.5,50.0)
wind=load('wind/0_b343c4c6.mp3',20,52)
zomb=load('zombie/0_54474c0a.mp3',0,4); zomb2=load('zombie/3_6150bb54.mp3',0,3)
# beds
put('amb',wind,0,-24,lp=6000)
w2=load('wind/2_5ddf823b.mp3',30,33.4); w2[:int(.5*SR)]*=np.linspace(0,1,int(.5*SR))[:,None]; w2[-int(.8*SR):]*=np.linspace(1,0,int(.8*SR))[:,None]; put('amb',w2,17.3,-13,lp=1800)
e=eng[:int(21.5*SR)].copy(); e[-int(2*SR):]*=np.linspace(1,0,int(2*SR))[:,None]**2
put('amb',e,0.0,-21,lp=3500,hp=40)
put('amb',zomb,2.6,-26,pan=-.5,lp=4000); put('amb',zomb2,5.2,-25,pan=.4,lp=4000)
# s3 kills (shot3 starts 5.0, frames 13/37 from frame 3)
for t,p in [(5.0+10/24,-.2),(5.0+34/24,.25)]:
    put('fx',gun,t-.06,-3,pan=p); put('fx',splat2,t+.02,-9,pan=p); put('fol',brass,t+.35,-20,pan=-p)
# s4 bullet time: fire at out-frame 19, impact frame 70
tf=7.5+18/24; ti=7.5+69/24
put('fx',gun,tf,0); 
slow=load('gun/0_446277fa.mp3',.94,1.64,.35); put('fx',slow,tf+.08,-8,lp=2500)
put('fx',splat,ti,-2); put('fx',boom,ti,-9,lp=900)
# s5 four drift kills
for i,t in enumerate([12.0,12.5,13.0,13.5]):
    p=[-.4,-.1,.2,.45][i]; put('fx',gun,t-.05,-3,pan=p); put('fx',splat2,t+.03,-10,pan=p)
put('fol',brass2,12.3,-18,pan=-.3)
# s6 goggles ECU: bolt rack
put('fol',rack,16.1,-6,pan=.15)
# s8 antlers: growl
put('fx',growl,20.1,-7,lp=5000)
# s9 empty the belt 22.6-24.9
t=22.6
for seg in [hmg,mg,hmg2,mg2]:
    put('fx',seg,t,-2,pan=.05); t+=len(seg)/SR-.06
    if t>24.9: break
k=int(24.92*SR); L['fx'][k:k+int(.6*SR)]*=np.linspace(0,1,int(.6*SR))[:,None]**3
for tt in np.arange(22.7,24.9,.31): put('fx',ric if int(tt*10)%2 else splat2,tt,-14,pan=np.sin(tt*7)*.4)
put('fol',brass2,23.0,-16,pan=-.2); put('fol',brass2,24.2,-17,pan=.2)
for tt in [25.0,25.22,25.42]: put('fol',dry,tt,0,pan=.1,hp=300)
# s10 roar slow-mo
put('fx',roarA,25.55,0); put('fx',roarB,25.6,-5)
# s11 charge
put('fx',steps,27.5,-4); put('fx',steps2,28.4,-3)
put('fx',boom,29.3,0); put('fx',ss.sosfilt(ss.butter(4,120,'low',fs=SR,output='sos'),boom,axis=0)*1.5,29.3,0)
put('fol',dry,29.82,-6)
# reverb send (night street slap)
ir=np.random.RandomState(1).randn(int(1.4*SR),2)*np.exp(-np.linspace(0,7,int(1.4*SR)))[:,None]; ir[:int(.03*SR)]=0
fx=L['fx']; wet=ss.fftconvolve(fx,ir,axes=0)[:N]*.035
sfx=fx+wet+L['fol']+L['amb']
sc=np.fromfile('/home/user/w/audio/mix/score30.f32',np.float32).reshape(-1,2)
score=np.zeros((N,2),np.float32); score[:len(sc)]=sc
# duck score under gunfire (sidechain)
env=np.abs(fx).max(1); env=ss.sosfilt(ss.butter(1,8,'low',fs=SR,output='sos'),env); duck=1-np.clip(env*1.2,0,.45)
g=np.ones(N); a,b=int(24.9*SR),int(25.5*SR); g[a:b]=.04; g=ss.sosfiltfilt(ss.butter(1,20,'low',fs=SR,output='sos'),g)
mix=score*.7*duck[:,None]*g[:,None]+sfx*.55
mix[int(29.3*SR):]=sfx[int(29.3*SR):]*.55
import pyloudnorm as pyln
m=pyln.Meter(SR); l=m.integrated_loudness(mix[:int(29.5*SR)]); mix*=10**((-14-l)/20)
pk=np.abs(mix).max()
thr=.6; a=np.abs(mix); mix=np.where(a>thr,np.sign(mix)*(thr+(1-thr)*np.tanh((a-thr)/(1-thr))),mix)*.86
print('LUFS before',l,'peak',pk)
mix[int(30.0*SR):] *= 1
mix=mix[:int(30*SR)]
import soundfile as sf; sf.write('/home/user/w/audio/sfxmix/mix_v1.wav',mix,SR,subtype='PCM_24')
sf.write('/home/user/w/audio/sfxmix/sfx_only.wav',(sfx*.55)[:int(30*SR)],SR,subtype='PCM_24')
