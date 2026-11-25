"""Generate local dialogue and mix the picture-locked 63-second episode."""
from pathlib import Path
from fractions import Fraction
import functools
import json
import subprocess
import wave

import numpy as np
from scipy import signal, ndimage

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parents[2]
REC=ROOT/'recordings'
OUT=ROOT/'stems'
OUT.mkdir(exist_ok=True)
rate=48000
duration=63
length=rate*duration
LINES=[
 ('Narrator','bm_george',3.4,5.13,.99,'On the other side, everything is the same.'),
 ('Narrator','bm_george',5.2,6.86,.90,'Just turned around.'),
 ('Mirror-Mom','af_nicole',12.6,14.15,.93,"You're late, Sam."),
 ('Narrator','bm_george',25.0,28.68,.96,'Officer Tanaka lasted eleven days. He wrote everything down.'),
 ('Sam','am_puck',30.6,32.92,1.05,"Mom! I'm here! Mom!"),
 ('Narrator','bm_george',42.5,44.80,.93,'Time runs differently on this side.'),
 ('Mirror-Sam','am_puck',56.5,59.61,.92,"Sam. Let me in. It's my turn now."),
 ('Narrator','bm_george',60.5,62.45,.90,'Rule eight.'),
]

def wav(path,array):
    a=np.asarray(array)
    if a.ndim==1:a=a[:,None]
    with wave.open(str(path),'wb') as f:
        f.setnchannels(a.shape[1])
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())

@functools.lru_cache(maxsize=30)
def read(path,seconds=0):
    call=['ffmpeg','-hide_banner','-loglevel','error','-i',str(path)]
    if seconds:call+=['-t',str(seconds)]
    b=subprocess.check_output(call+['-f','f32le','-ac','2','-ar',str(rate),'-'])
    return np.frombuffer(b,dtype='<f4').reshape(-1,2).copy()

def db(d): return 10**(d/20)
def norm(a,target):
    return a*min(25,db(target)/(np.sqrt(np.mean(a*a))+1e-9))
def peak(a,target):
    return a*min(25,db(target)/(np.max(np.abs(a))+1e-9))
def filter_(a,f,kind):
    return signal.sosfilt(signal.butter(2,f,btype=kind,fs=rate,output='sos'),a,axis=0).astype(np.float32)
def band(a,lo,hi):
    return filter_(filter_(a,lo,'highpass'),hi,'lowpass')
def stretch(a,factor):
    ratio=Fraction(factor).limit_denominator(280)
    return signal.resample_poly(a,ratio.numerator,ratio.denominator,axis=0).astype(np.float32)
def clip_fade(a,attack=.012,tail=.07):
    a=a.copy()
    i=min(len(a)//2,max(1,round(attack*rate)))
    j=min(len(a)//2,max(1,round(tail*rate)))
    shape=(np.linspace(0,1,i,dtype=np.float32)**1.5)
    if a.ndim>1:shape=shape[:,None]
    a[:i]*=shape
    gate=np.linspace(1,0,j,dtype=np.float32)
    if a.ndim>1:gate=gate[:,None]
    a[-j:]*=gate
    return a
def take(a,start=.0,end=None):
    return a[round(start*rate):(None if end is None else round(end*rate))]
def place(track,a,t,gain=1,pan=0):
    k=round(t*rate)
    if k<0:
        a=a[-k:]
        k=0
    n=min(len(a),len(track)-k)
    if n<=0:return
    if a.ndim==1:a=np.column_stack([a,a])
    p=np.array([1-max(0,pan),1+min(0,pan)],dtype=np.float32)
    track[k:k+n]+=a[:n]*gain*p
def echo(x,t,decay):
    out=x.copy()
    for j,offset in enumerate((.043,.097,.163,.249,.366)):
        k=round(offset*t*rate)
        if k>=len(x):continue
        out[k:]+=x[:-k,::-1]*decay**(j+1)
    return out
def curve(points):
    x,y=zip(*points)
    return np.interp(np.arange(length)/rate,x,y).astype(np.float32)

def voices():
    from kokoro_onnx import Kokoro
    model=Kokoro(str(ROOT/'models'/'kokoro-v1.0.onnx'),str(ROOT/'models'/'voices-v1.0.bin'))
    track=np.zeros((length,2),dtype=np.float32)
    events=[]
    for i,(role,voice,t,deadline,speed,words) in enumerate(LINES,1):
        selected=None
        for alt in (speed,speed*1.14):
            arr,sr=model.create(words,voice=voice,speed=alt,lang='en-gb' if role=='Narrator' else 'en-us')
            arr=np.asarray(arr,dtype=np.float32)
            idx=np.flatnonzero(np.abs(arr)>max(.002,np.max(np.abs(arr))*.018))
            if len(idx):arr=arr[max(0,idx[0]-round(sr*.023)):idx[-1]+round(sr*.047)]
            a=stretch(arr,rate/sr)
            if role=='Mirror-Sam':
                a=stretch(a,2**(.52/12))
            if len(a)<=round((deadline-t)*rate):
                selected=a
                break
            selected=a
        if len(selected)>round((deadline-t)*rate):
            # Preserve pitch when fitting dialogue within its shot.
            temp=OUT/f'line_{i:02d}_untrimmed.wav'
            wav(temp,selected)
            tempo=len(selected)/((deadline-t)*rate)*1.025
            raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(temp),'-af',f'atempo={min(1.75,tempo):.6f}','-f','f32le','-ar',str(rate),'-ac','1','-'])
            selected=np.frombuffer(raw,dtype='<f4').copy()[:round((deadline-t)*rate)]
        a=band(selected,68,7900)
        warmth=band(a,145,265)*.22
        a=a+warmth
        if role=='Mirror-Mom':
            a=filter_(a,5800,'lowpass')
        if role=='Sam':
            a=band(a,155,5200)
        a=peak(norm(clip_fade(a,.010,.045),-20 if role=='Narrator' else -19),-5)
        target=OUT/f'line_{i:02d}.wav'
        wav(target,a)
        place(track,a,t)
        events.append({'role':role,'start':t,'end':round(t+len(a)/rate,3),'deadline':deadline,'text':words})
        print(i,role,round(len(a)/rate,2),'s',flush=True)
    raw,sr=model.create('Hmm.',voice='af_nicole',speed=.65,lang='en-us')
    raw=stretch(np.asarray(raw,dtype=np.float32),rate/sr)
    return track,events,raw

piano={
 45:'A2v6',48:'C3v6',54:'F#3v6',57:'A3v6',60:'C4v6',
 63:'D#4v6',66:'F#4v6',69:'A4v6',72:'C5v6',
}
vsco=PROJECT/'ep1v2'/'build'/'vsco'/'Percussion'
mar={53:vsco/'Marimba'/'Marimba_hit_Outrigger_F3_loud_01.wav',
     60:vsco/'Marimba'/'Marimba_hit_Outrigger_C4_loud_01.wav',
     67:vsco/'Marimba'/'Marimba_hit_Outrigger_G4_loud_01.wav',
     71:vsco/'Marimba'/'Marimba_hit_Outrigger_B4_loud_01.wav',
     77:vsco/'Marimba'/'Marimba_hit_Outrigger_F5_loud_01.wav',
     84:vsco/'Marimba'/'Marimba_hit_Outrigger_C6_loud_01.wav'}
glock={67:vsco/'Glock'/'glock_medium_G4.wav',72:vsco/'Glock'/'glock_medium_C5.wav',
       79:vsco/'Glock'/'glock_medium_G5.wav',84:vsco/'Glock'/'glock_medium_C6.wav',
       91:vsco/'Glock'/'glock_medium_G6.wav',96:vsco/'Glock'/'glock_medium_C7.wav'}

def note(bank,midi,hold,decay,tag=False):
    key=min(bank,key=lambda k:abs(k-midi))
    path=REC/('piano_'+bank[key]+'.flac') if tag else bank[key]
    a=read(path,6 if tag else 4)
    pitch=2**((key-midi)/12)
    a=stretch(a,pitch)
    a=a[:round((hold+decay)*rate)]
    t=np.arange(len(a),dtype=np.float32)/rate
    damping=np.exp(-np.maximum(0,t-hold)/max(.11,decay*.39))[:,None]
    a=a*damping
    return peak(clip_fade(a,.005 if tag else .002,min(.18,decay*.45)),-7 if tag else -5)

def score():
    out=np.zeros((length,2),np.float32)
    phrases=[
      (.86,[(57,0),(63,.57),(66,1.24)]),
      (7.02,[(54,0),(60,.48),(63,1.00),(69,2.24)]),
      (10.39,[(48,0),(60,.42)]),
      (14.28,[(48,0),(63,.55),(66,1.39),(69,2.07)]),
      (19.42,[(45,0),(54,.58),(57,1.36),(60,3.40)]),
      (23.98,[(48,0),(63,.42)]),
      (28.63,[(45,0),(57,.48),(60,3.70),(63,4.39)]),
      (34.66,[(45,0),(60,.43),(66,.96),(63,1.93),(57,3.03)]),
      (38.53,[(48,0),(63,.55),(66,1.25),(69,2.03)]),
      (43.95,[(45,0),(54,.80),(60,1.59),(63,2.11),(66,3.39),(69,4.68)]),
      (49.13,[(42,0),(54,.43)]),
      (59.96,[(45,0),(57,.49),(63,1.96),(66,2.29)]),
    ]
    for i,(start,melody) in enumerate(phrases):
        for j,(midi,offset) in enumerate(melody):
            if start+offset>61.9:continue
            volume=.139 if j%3==0 else .107
            if midi<50:volume*=.87
            a=filter_(note(piano,midi,.72 if midi<=48 else .37,2.73,True),5100,'lowpass')
            place(out,echo(a,2.4,.33),start+offset,volume,(-.13 if j%2 else .10))
    # Longer felt bass notes are quiet and spaced. They are recorded piano, transposed ≤ 3 semitones.
    for start,key in ((8.35,45),(15.57,48),(20.57,45),(28.32,42),(37.80,45),(46.88,42),(50.45,45)):
        a=filter_(note(piano,key,1.3,3.6,True),700,'lowpass')
        place(out,echo(a,1.8,.31),start,.086)
    return out

def fx(hum):
    fx=np.zeros((length,2),np.float32)
    chime=np.zeros_like(fx)
    def add_sample(name,t,start,end,gain,p=0,lo=55,hi=8000):
        a=take(read(REC/(name+'.mp3')),start,end)
        if not len(a):return
        a=band(a,lo,hi)
        place(fx,peak(clip_fade(a,.012,.06),-4),t,gain,p)
    for t,g in zip((.335,1.166,2.0),(.44,.40,.36)):
        add_sample('buzz',t,.18,.55,g,-.10,85,3450)
    add_sample('kettle',11.18,1.0,4.6,.12,.25,180,5000)
    add_sample('kettle',13.87,5.0,6.06,.20,.19,210,5000)
    for t in (15.16,16.31,17.62,18.38):
        add_sample('broom',t,.31,1.16,.19,-.15 if t<17.2 else .24,170,6400)
    for t,offset in ((15.05,1.01),(16.04,2.40),(17.36,1.32),(18.47,2.61),(19.0,1.55)):
        add_sample('steps',t,offset,offset+.42,.15,.04,70,6000)
    add_sample('hinge',19.70,.14,1.49,.13,.12,100,5400)
    add_sample('paper',25.60,.13,2.23,.15,.03,220,6500)
    add_sample('buzz',29.24,.26,.84,.28,-.06,80,3100)
    add_sample('paper',33.08,3.19,3.85,.075,.10,1350,6400)
    add_sample('hinge',38.13,.89,1.67,.10,-.19,105,3200)
    add_sample('hinge',46.50,.26,1.39,.16,.15,110,4900)
    add_sample('hinge',47.37,2.1,3.12,.16,-.18,110,4700)
    add_sample('door',50.89,0,.77,.59,.04,46,6200)
    add_sample('knock',55.73,0,.69,.73,0,55,6200)
    add_sample('paper',61.18,2.10,3.75,.075,.07,680,7100)
    cue_frames=(35,52,69,86)
    notes=(66,70,73,78)
    for i,(f,m) in enumerate(zip(cue_frames,notes)):
        t=50+(f-1)/24
        a=band(note(mar,m,.48,1.3),290,3550)*.8
        b=band(note(glock,m+12,.22,1.17),400,5000)*.28
        place(chime,echo(a+.0,1.65,.26),t,.43,-.18+i*.11)
        place(chime,echo(b,1.71,.26),t+.008,.37,.18-i*.07)
    # Hum the first three pitch classes in the kitchen using the same voice as Mirror-Mom.
    raw=band(hum,90,2900)
    block=raw[:round(rate*.65)]
    if len(block)>rate//10:
        level=np.abs(block)>max(.003,np.max(np.abs(block))*.16)
        data=block[np.flatnonzero(level)[0]:] if np.any(level) else block
        center=data[len(data)//5:len(data)*4//5]
        corr=signal.correlate(center,center,mode='full')[len(center)-1:]
        lo,hi=round(rate/330),round(rate/117)
        lag=lo+np.argmax(corr[lo:hi])
        root_hz=rate/lag
        for t,m in zip((11.15,11.60,12.04),(54,58,61)):
            pitched=stretch(data,root_hz/(440*2**((m-69)/12)))
            a=peak(clip_fade(pitched[:round(rate*.29)],.043,.092),-10)
            place(fx,a,t,.41,-.21)
    # Use a filtered recording for the broken transmission as the picture freezes.
    flutter=band(read(REC/'kettle.mp3',4),1300,6100)
    for t,a,b,gain in ((29.83,.85,1.04,.055),(30.56,1.58,1.79,.095),(31.31,1.0,1.13,.10),
                       (31.85,2.26,2.50,.11),(32.66,1.2,1.41,.065),(35.20,1.06,1.16,.064)):
        burst=clip_fade(take(flutter,a,b),.005,.030)
        place(fx,peak(burst,-8),t,gain,.13)
    # A recorded wind bed from Episode 1 sits under the close scenes.
    wire=PROJECT/'ep1v2'/'build'/'snd'/'wires'/'0_72e0b9e4.mp3'
    room=filter_(read(wire,13),1000,'lowpass')
    for t in (0,7,15,21,29,37,44,60):
        place(fx,peak(clip_fade(room[:rate*9],.41,1.18),-5),t,.066,-.07)
    return fx,chime,notes,cue_frames

def main():
    picture=ROOT.parent.parent/'episode'/'picture_timeline.json'
    if not picture.exists():
        raise RuntimeError('Assemble and verify the silent cut before rendering voices.')
    cuts=json.loads(picture.read_text(encoding='utf-8'))
    assert len(cuts)==15 and cuts[-1]['out_frame']==duration*24
    voice,events,hum=voices()
    music=score()
    foley,chime,notes,cues=fx(hum)
    duck=np.ones(length,dtype=np.float32)
    for line in events:
        start=max(0,round((line['start']-.17)*rate))
        end=min(length,round((line['end']+.26)*rate))
        real_start=round(line['start']*rate)
        real_end=round(line['end']*rate)
        envelope=np.interp(np.arange(start,end),[start,real_start,real_end,end-1],[1,.36,.35,1])
        duck[start:end]=np.minimum(duck[start:end],envelope)
    musical=curve([(0,1),(49.75,.88),(51.0,.42),(54.75,.39),(55.19,0),(59.75,0),(60.1,.94),(62.64,.68),(63,0)])
    foley_gate=curve([(0,1),(54.90,1),(55.15,.50),(55.48,.720),(56.5,.31),(59.57,.29),(60.0,.69),(62.64,.70),(63.0,0)])
    score_ducked=music*(duck*musical)[:,None]
    fx_ducked=foley*(foley_gate*(.65+.35*duck))[:,None]
    voice*=curve([(0,1),(62.73,1),(63,0)])[:,None]
    mix=score_ducked+fx_ducked+chime+voice
    limiter=np.max(abs(mix))
    if limiter>.96:mix*=.96/limiter
    wav(OUT/'dialogue.wav',voice)
    wav(OUT/'piano.wav',score_ducked)
    wav(OUT/'foley.wav',fx_ducked)
    wav(OUT/'chime.wav',chime)
    wav(OUT/'premaster.wav',mix)
    assert len(events)==8 and all(event['start']<event['end']<=event['deadline'] for event in events)
    assert np.isfinite(mix).all()
    report={'duration':duration,'dialogue':events,'chime_midi':notes,'chime_shot_frames':cues,
            'speech_engine':'Kokoro ONNX, local stock voice styles and a same-voice pitch shift for Mirror-Sam'}
    (ROOT/'audio_timeline.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

if __name__=='__main__':
    main()


