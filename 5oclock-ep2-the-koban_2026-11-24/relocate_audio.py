from pathlib import Path

root=Path(__file__).resolve().parent
audio=root/'audio'
prod=root/'shots'/'production'
p=audio/'mix_episode.py'
s=p.read_text(encoding='utf-8-sig')
s=s.replace("PROJECT=ROOT.parents[2]","PROJECT=ROOT.parent")
s=s.replace("vsco=PROJECT/'ep1v2'/'build'/'vsco'/'Percussion'", "vsco=REC")
s=s.replace("vsco/'Marimba'","vsco/'marimba'").replace("vsco/'Glock'","vsco/'glock'")
s=s.replace("wire=PROJECT/'ep1v2'/'build'/'snd'/'wires'/'0_72e0b9e4.mp3'", "wire=REC/'wind.mp3'")
s=s.replace("picture=ROOT.parent.parent/'episode'/'picture_timeline.json'", "picture=PROJECT/'episode'/'picture_timeline.json'")
for voice,prefix in (("bm_george','3",""),):
    pass
for voice,prefix in [('bm_george','N1'),('bm_george','N2'),('af_nicole','MM1'),('bm_george','N3'),
                     ('am_puck','S1'),('bm_george','N4'),('am_puck','M1'),('bm_george','N5')]:
    s=s.replace(f"'{voice}'",f"'{prefix}'",1)
start=s.index('def voices():')
end=s.index('\npiano=',start)
replacement="""def take_file(prefix):
    for letter in ('A','B'):
        path=ROOT/f'{prefix}_take{letter}.mp3'
        if path.is_file() and path.stat().st_size:
            return path
    return None

def trim(arr):
    idx=np.flatnonzero(np.abs(arr)>max(.002,np.max(np.abs(arr))*.018))
    if len(idx)==0:
        raise ValueError('The selected audio take has no audible signal.')
    return arr[max(0,idx[0]-round(rate*.023)):idx[-1]+round(rate*.047)]

def compress_to_fit(source,max_frames,index):
    if len(source)<=max_frames:
        return source
    tempo=len(source)/max_frames*1.025
    temp=OUT/f'line_{index:02d}_untrimmed.wav'
    wav(temp,source)
    stages=[]
    while tempo>1.65:
        stages.append('atempo=1.65')
        tempo/=1.65
    stages.append(f'atempo={tempo:.6f}')
    data=subprocess.check_output(['ffmpeg','-v','error','-i',str(temp),'-af',','.join(stages),
        '-f','f32le','-ar',str(rate),'-ac','1','-'])
    fitted=np.frombuffer(data,dtype='<f4').copy()
    if len(fitted)>max_frames:
        raise ValueError(f'Line {index} still exceeds the authored cut after fitting')
    return fitted

def voices():
    track=np.zeros((length,2),dtype=np.float32)
    takes={prefix:take_file(prefix) for _,prefix,*_ in LINES}
    missing=[prefix for prefix,path in takes.items() if path is None]
    if missing:
        print('Scoring the picture. Awaiting ElevenLabs takes: '+', '.join(missing),flush=True)
        return track,[],None,missing
    events=[]
    for i,(role,prefix,t,deadline,_,words) in enumerate(LINES,1):
        path=takes[prefix]
        selected=trim(read(path).mean(axis=1))
        if role=='Mirror-Sam':
            selected=stretch(selected,2**(.52/12))
        selected=compress_to_fit(selected,round((deadline-t)*rate),i)
        a=band(selected,68,7900)
        a=a+band(a,145,265)*.22
        if role=='Mirror-Mom':
            a=filter_(a,5800,'lowpass')
        if role=='Sam':
            a=band(a,155,5200)
        a=peak(norm(clip_fade(a,.010,.045),-20 if role=='Narrator' else -19),-5)
        wav(OUT/f'line_{i:02d}.wav',a)
        place(track,a,t)
        events.append({'role':role,'start':t,'end':round(t+len(a)/rate,3),
                       'deadline':deadline,'text':words,'take':path.name})
        print(i,role,round(len(a)/rate,2),'s',path.name,flush=True)
    hum=take_file('H1')
    return track,events,trim(read(hum).mean(axis=1)) if hum else None,missing
"""
s=s[:start]+replacement+s[end:]
s=s.replace('    raw=band(hum,90,2900)\n    block=raw[:round(rate*.65)]','    block=np.zeros(0) if hum is None else band(hum,90,2900)[:round(rate*.65)]')
s=s.replace('voice,events,hum=voices()','voice,events,hum,missing=voices()')
s=s.replace("    assert len(events)==8 and all(event['start']<event['end']<=event['deadline'] for event in events)",
"""    assert len(events)==(0 if missing else 8)
    assert all(event['start']<event['end']<=event['deadline'] for event in events)""")
s=s.replace("'speech_engine':'Kokoro ONNX, local stock voice styles and a same-voice pitch shift for Mirror-Sam'",
"'missing_takes':missing,'optional_hum_present':hum is not None,'speech_source':'ElevenLabs named takes'")
p.write_text(s,encoding='utf-8')
p=audio/'assemble_episode.py'
s=p.read_text(encoding='utf-8-sig')
s=s.replace("PROD=ROOT.parent\nEPISODE=PROD.parent\nOUT=EPISODE/'episode'","PROJECT=ROOT.parent\nEPISODE=PROJECT/'shots'\nPROD=EPISODE/'production'\nOUT=PROJECT/'episode'")
s=s.replace("ver=2 if number in ('04','08') else 1","ver=2 if number in ('04','05','08') else 1")
s=s.replace("FINAL=OUT/'5oclock_ep2_the_koban_v1.mp4'\n","")
s=s.replace("TRACK=OUT/'5oclock_ep2_the_koban_mix_v1.wav'\n","")
s=s.replace("def normalize():","def normalize(track):")
s=s.replace("str(TRACK)","str(track)").replace("measure(TRACK)","measure(track)")
s=s.replace("    loud=normalize() if not TRACK.exists() else measure(track)",
"""    timeline=json.loads((ROOT/'audio_timeline.json').read_text(encoding='utf-8'))
    scored_only=bool(timeline['missing_takes'])
    label='score_only_v1' if scored_only else 'v1'
    final_path=OUT/f'5oclock_ep2_the_koban_{label}.mp4'
    track=OUT/f'5oclock_ep2_the_koban_mix_{label}.wav'
    loud=normalize(track) if not track.exists() else measure(track)""")
s=s.replace('if not FINAL.exists()','if not final_path.exists()').replace('str(FINAL)','str(final_path)').replace('video(FINAL','video(final_path').replace('measure(FINAL)','measure(final_path)')
s=s.replace("(OUT/'MASTER_QA.json')","(OUT/f'MASTER_QA_{label}.json')")
s=s.replace("print('Final episode:',FINAL)", "print('Scored cut:' if scored_only else 'Dialogue master:',final_path)")
p.write_text(s,encoding='utf-8')
p=prod/'qa_reel.py'
s=p.read_text(encoding='utf-8-sig').replace("OUT=ROOT/'episode'","OUT=ROOT.parent/'episode'")
p.write_text(s,encoding='utf-8')

