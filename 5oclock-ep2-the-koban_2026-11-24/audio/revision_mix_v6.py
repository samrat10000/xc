"""Build and verify the revised episode mix without altering the earlier master."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import math
import subprocess

import numpy as np
from scipy import signal

import assemble_episode as original_master
import mix_episode as m
from revision_cut_v6 import OUT, count, run

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
MASTER=PROJECT/'episode'/'5oclock_ep2_the_koban_v6.mp4'
WAVE=PROJECT/'episode'/'5oclock_ep2_the_koban_mix_v6.wav'
CUT=OUT/'5oclock_ep2_the_koban_silent_v6.mp4'
STEMS=OUT/'stems'
rate=48000

def gain(db):
    return 10**(db/20)

def room_voice(x):
    mono=m.band(x,112,5750)
    present=mono+m.band(mono,320,665)*.12
    stereo=np.stack((present*.96,present),axis=1)
    for seconds,weights in ((.018,(.17,.11)),(.041,(.08,.15)),(.067,(.035,.044))):
        lag=round(seconds*rate)
        stereo[lag:]+=present[:-lag,None]*np.asarray(weights)[None,:]
    return stereo

def load_dialogue(length,start):
    voice=np.zeros((length,2),np.float32)
    records=[]
    placements={'N1':2.25,'N2':5.18,'MM1':start['04']+1.60,'N3':start['07']+.14,
                'S1':start['08']+1.0,'M1':start['14']+1.34,'N5':start['15']+1.51}
    endings={'N1':placements['N2']-.13,'N2':start['03']+1.0,'MM1':start['05']-.12,
             'N3':start['08']-.06,'S1':start['10']-.35,'M1':start['15']-7/24-.035,'N5':length/rate-.22}
    for role,prefix,_,_,_,text in m.LINES:
        if prefix not in placements:
            continue
        file=m.take_file(prefix)
        if file is None:
            raise FileNotFoundError(prefix)
        raw=m.trim(m.read(file).mean(axis=1))
        natural=len(raw)/rate
        filtered=m.band(raw,78,7600)
        if prefix=='M1':
            # Through-door filtering and early reflections preserve the original timing.
            filtered=room_voice(filtered)
        elif prefix=='S1':
            filtered=m.band(filtered,120,7100)
        elif prefix=='MM1':
            filtered=m.band(filtered,106,6900)
        else:
            filtered=filtered+m.band(filtered,148,265)*.17
        filtered=m.peak(m.norm(m.clip_fade(filtered,.012,.046),-21.0),-6.2)
        begin=placements[prefix]
        end=begin+len(filtered)/rate
        assert end<=endings[prefix],(prefix,begin,end,endings[prefix])
        m.place(voice,filtered,begin)
        records.append({'id':prefix,'role':role,'start':round(begin,4),'end':round(end,4),'text':text,
                        'take':file.name,'source_trimmed_seconds':round(natural,4),'tempo':1.0})
    return voice,records

def create_score(length,s):
    track=np.zeros((length,2),np.float32)
    # Legible motifs that return at the climax instead of playing continuously over action.
    motifs=[
        (.05,[(54,0),(61,.47)]),
        (s['02']+.15,[(45,0),(54,1.12)]),
        (s['03']+.66,[(42,0),(49,.72),(54,1.6),(63,2.52)]),
        (s['05']+.24,[(42,0),(48,.82),(54,1.51),(48,2.72)]),
        (s['06']+.10,[(49,0),(59,1.08),(61,2.56)]),
        (s['07']+.18,[(42,0),(48,2.61)]),
        (s['08']+.20,[(57,0),(61,.57)]),
        (s['09']+.45,[(49,0),(56,.81)]),
        (s['10']+.82,[(42,0),(49,1.18),(54,2.32)]),
        (s['11']+1.03,[(45,0),(54,.53)]),
        (s['12']+.29,[(42,0),(49,.85),(54,1.68),(56,2.63),(61,3.44),(66,4.27)]),
        (s['13']-.03,[(37,0),(49,.70)]),
        (s['15']+.19,[(45,0),(54,.76),(61,1.50),(54,2.67)]),
    ]
    for start,phrase in motifs:
        for i,(pitch,offset) in enumerate(phrase):
            note=m.note(m.piano,pitch,.63 if pitch<55 else .48,2.2,True)
            note=m.filter_(note,4300 if pitch>=54 else 2350,'lowpass')
            amp=.146 if pitch<53 else .098
            m.place(track,m.echo(note,1.6,.23),start+offset,amp,(-.085 if i%2==0 else .11))
    return track

def shared_theme(length,s,listener):
    folder=ROOT/'series_theme_v6'
    cues=json.loads((folder/'theme_cues.json').read_text(encoding='utf-8'))['cues']
    score=np.zeros((length,2),np.float32)
    opening=m.take(m.read(folder/'theme_intro.wav'),0,5.24)
    m.place(score,m.norm(m.clip_fade(opening,.045,.68),-28.5),.02)
    movement=m.take(m.read(folder/'theme_bed_loop.wav'),0,3.45)
    m.place(score,m.norm(m.clip_fade(movement,.15,.31),-28.8),s['05']+.12)
    melody_in=cues['theme'][0]
    sound=m.take(m.read(folder/'theme_full.wav'),melody_in,cues['cut'])
    sound=m.band(sound,43,6800)
    m.place(score,m.norm(m.clip_fade(sound,.39,.012),-26.8),listener-(cues['hit']-melody_in))
    silence_start=listener+cues['cut']-cues['hit']
    silence_end=silence_start+cues['fourth_note']-cues['cut']
    return score,(silence_start,silence_end)


def sound_effects(length,s,third,fourth):
    foley=np.zeros((length,2),np.float32)
    beds=np.zeros_like(foley)
    chime=np.zeros_like(foley)
    raw=m.read(m.REC/'wind.mp3',29)
    def ambience(start,end,offset,lo,hi,level,pan=0):
        target=round((end-start)*rate)
        if target<=0:
            return
        clip=raw[round(offset*rate):]
        if not len(clip):
            clip=raw
        reps=(target+len(clip)-1)//len(clip)
        piece=np.tile(clip,(reps,1))[:target]
        piece=m.norm(m.band(piece,lo,hi),level)
        m.place(beds,m.clip_fade(piece,.28,.46),start,1,pan)
    ambience(0,1.04,4.7,120,1200,-32)
    ambience(.73,s['03']+.24,1.5,145,760,-36,-.10)
    ambience(s['03']-.1,s['04']+.13,4.3,130,1650,-32,.07)
    ambience(s['04']-.06,s['05']+.06,5.2,155,860,-35)
    ambience(s['05']-.2,s['06']+.15,2.1,110,1750,-31,-.08)
    ambience(s['06']-.1,s['11']+.15,3.4,135,890,-36)
    ambience(s['11']-.08,s['12']+.12,7.3,115,1050,-33)
    ambience(s['12']-.13,s['14']+.1,0,95,1600,-31,.12)
    ambience(s['14']+.22,s['15'],8.3,145,530,-39)
    ambience(s['15']-.08,length/rate,5.0,150,900,-35)
    def effect(name,t,a,b,db,pan=0,lo=65,hi=7200):
        sample=m.take(m.read(m.REC/f'{name}.mp3'),a,b)
        if not len(sample):
            return
        sample=m.peak(m.norm(m.clip_fade(m.band(sample,lo,hi),.009,.052),db),db+13)
        m.place(foley,sample,t,1,pan)
    effect('buzz',.82,.18,.54,-19,-.10,115,2700)
    effect('buzz',1.49,.19,.48,-23,-.10,115,2700)
    effect('kettle',s['04']+.33,1.25,4.30,-35,.22,230,4800)
    for t,pan,db in ((.22,-.22,-27),(1.13,.20,-29),(1.70,-.42,-34),(2.73,.19,-28),(3.35,-.21,-30)):
        effect('broom',s['05']+t,.35,.80,db,pan,240,5900)
    for j,(t,source) in enumerate(((.12,1.01),(.53,2.40),(.94,1.32),(1.33,2.61),
                                     (1.71,1.55),(2.09,2.40),(2.49,1.32),(2.90,2.61),(3.28,1.01),(3.47,1.55))):
        effect('steps',s['05']+t,source,source+.24,-24+(j%2)*1.7,.10-j*.013,95,5100)
    effect('hinge',s['06']+.76,.14,1.06,-28,.13,140,4200)
    effect('paper',s['07']+1.67,.13,2.11,-28,.04,230,4900)
    effect('buzz',s['08']+.22,.27,.72,-24,-.03,120,2900)
    for t,a,b,db in ((.89,.64,.83,-29),(1.55,1.46,1.60,-32),(2.11,2.27,2.47,-32),(2.53,1.75,1.85,-34)):
        effect('kettle',s['08']+t,a,b,db,.10,1550,5800)
    effect('hinge',s['10']+1.02,.89,1.49,-30,-.12,115,3000)
    effect('paper',s['10']+2.20,.49,.84,-33,.17,130,3100)
    effect('hinge',s['12']+.71,.26,1.37,-26,.24,65,4550)
    effect('hinge',s['12']+1.66,2.00,3.08,-27,-.21,65,4150)
    effect('hinge',s['12']+3.53,1.09,1.88,-30,.10,110,2500)
    effect('door',s['14']-.29,0,.67,-17,.08,57,6000)
    effect('knock',s['14']+.73,0,.58,-17,.07,75,5300)
    effect('steps',s['14']+3.23,1.32,1.62,-29,.06,145,2800)
    effect('paper',s['15']+.74,2.20,3.54,-33,.06,455,6900)
    hum=m.take_file('H1')
    if hum is None:
        raise FileNotFoundError('H1')
    sample=m.band(m.trim(m.read(hum).mean(axis=1)),115,2500)
    center=sample[int(rate*.065):int(rate*.38)]
    corr=signal.correlate(center,center,'full')[len(center)-1:]
    lo,hi=round(rate/328),round(rate/115)
    hz=rate/(lo+np.argmax(corr[lo:hi]))
    for j,(t,pitch) in enumerate(zip((.11,.55,.99),(54,58,61))):
        note=m.stretch(sample,hz/(440*2**((pitch-69)/12)))[:round(rate*(.37+.024*j))]
        m.place(foley,m.norm(m.clip_fade(note,.045,.11),-30.2-j),s['04']+t,1,-.24)
    for i,(time,midi) in enumerate(zip((s['13']+34/24,s['13']+51/24,third,fourth),(66,70,73,78))):
        note=m.band(m.note(m.mar,midi,.54,1.15),220,3700)
        sparkle=m.band(m.note(m.glock,midi+12,.27,1.01),450,5500)
        amp=(.29,.32,.34,.40)[i]
        m.place(chime,m.echo(note,1.85,.30),time,amp,-.16+.10*i)
        m.place(chime,m.echo(sparkle,1.6,.28),time+.014,amp*.24,.20-.11*i)
    return foley,beds,chime

def mix_and_master():
    timeline=json.loads((OUT/'picture_timeline_v6.json').read_text(encoding='utf-8'))
    assert CUT.exists()
    frames=timeline[-1]['out_frame']
    duration=frames/24
    length=frames*2000
    s={row['id']:row['in_frame']/24 for row in timeline}
    s['05']=s['05a']
    s['13']=s['13a']
    STEMS.mkdir(exist_ok=True)
    voice,records=load_dialogue(length,s)
    piano=create_score(length,s)*.69
    theme,theme_silence=shared_theme(length,s,s['13b'])
    fx,beds,chime=sound_effects(length,s,s['13b'],s['13c']+1/24)
    time=np.arange(length)/rate
    duck=np.ones(length,np.float32)
    for line in records:
        e=np.interp(time,[line['start']-.19,line['start'],line['end'],line['end']+.25],[1,.70,.66,1])
        np.minimum(duck,e,out=duck)
    turn=np.interp(time,[0,s['14']-.42,s['14']+.15,s['15']-.20,s['15']+.11,duration-.48,duration],
                   [1,1,.085,.085,.91,.91,0])
    piano*=(duck*turn)[:,None]
    theme*=(duck*turn)[:,None]
    fx*=(.84+.16*duck)[:,None]
    gap_start,gap_end=theme_silence
    assert all(line['end']<=gap_start or line['start']>=gap_end for line in records)
    attenuate=1-np.interp(time,[gap_start-.012,gap_start,gap_end,gap_end+.012],[0,1,1,0])
    for track in (piano,theme,fx,beds,chime):
        track*=attenuate[:,None]
    bed=piano+theme+fx+beds+chime+voice
    bed*=np.interp(time,[0,duration-.26,duration],[1,1,0])[:,None]
    for label,track in (('dialogue',voice),('piano',piano),('series_theme',theme),('foley',fx),('rooms',beds),('chime',chime),('premaster',bed)):
        m.wav(STEMS/f'{label}.wav',track)
    report={'duration':duration,'dialogue':records,'cut_line_ids':['N4'],'theme':'SERIES_THEME recorded stems, Claude arrangement',
            'insert_for_third_note':s['13b'],'fourth_note':s['13c']+1/24,'theme_silence':theme_silence}
    (OUT/'audio_timeline_v6.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    original=STEMS/'premaster.wav'
    level=-14.78-float(original_master.measure(original)['input_i'])
    if not WAVE.exists():
        temp=WAVE.with_name(WAVE.stem+'_working.wav')
        balance=None
        for _ in range(9):
            filt=(f'volume={level:.5f}dB,acompressor=threshold=0.155:ratio=1.55:attack=14:release=170:makeup=1,'
                  'aresample=192000,alimiter=limit=0.708:attack=2:release=64:level=false:latency=true,aresample=48000')
            run(['ffmpeg','-y','-v','error','-i',str(original),'-af',filt,'-c:a','pcm_s24le',str(temp)])
            balance=original_master.measure(temp)
            lufs=float(balance['input_i'])
            if -15.18<=lufs<=-14.50 and float(balance['input_tp'])<=-1.35:
                temp.rename(WAVE)
                break
            level+=1.35*(-14.79-lufs)
        assert WAVE.exists(),balance
    if not MASTER.exists():
        run(['ffmpeg','-n','-v','error','-i',str(CUT),'-i',str(WAVE),'-map','0:v:0','-map','1:a:0',
             '-c:v','copy','-c:a','aac','-b:a','320k','-movflags','+faststart',str(MASTER)])
    assert count(MASTER)==frames,(MASTER,frames)
    loud=original_master.measure(MASTER)
    assert -15.22<=float(loud['input_i'])<=-14.47 and float(loud['input_tp'])<=-1.0,loud
    report['aac_loudness']=loud
    (OUT/'MASTER_QA_v6.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(f"Master v6: {duration:.3f}s, {loud['input_i']} LUFS, {loud['input_tp']} dBTP, {loud['input_lra']} LU range.",flush=True)

if __name__=='__main__':
    mix_and_master()

