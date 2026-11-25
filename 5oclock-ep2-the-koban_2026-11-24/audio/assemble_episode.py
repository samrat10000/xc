"""Assemble and verify the picture-locked episode and loudness-normalized stereo mix."""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
EPISODE=PROJECT/'shots'
PROD=EPISODE/'production'
OUT=PROJECT/'episode'
OUT.mkdir(exist_ok=True)
CUT=OUT/'5oclock_ep2_the_koban_silent_v1.mp4'
STEMS=ROOT/'stems'
INTRO=[
   ('01_alarm/01_alarm_v1.mp4',72),
   ('02_wrong_room/02_wrong_room_v2.mp4',96),
   ('03_the_crack/03_the_crack_v1.mp4',96),
]
def run(args):
    return subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
def media(path,count=True):
    args=['ffprobe','-v','error']
    if count:args+=['-count_frames']
    args+=['-show_entries','stream=codec_type,width,height,r_frame_rate,nb_read_frames,sample_rate:format=duration','-of','json',str(path)]
    return json.loads(run(args).stdout)
def video(path,expected,has_audio=False):
    record=media(path)
    streams=record['streams']
    assert len(streams)==(2 if has_audio else 1), (path,streams)
    s=streams[0]
    assert (s['codec_type'],s['width'],s['height'],s['r_frame_rate'],int(s['nb_read_frames']))==('video',1080,1920,'24/1',expected), (path,s)
    if has_audio:
        assert streams[1]['codec_type']=='audio'
        assert streams[1]['sample_rate']=='48000'
    assert abs(float(record['format']['duration'])-expected/24)<.052, (path,record)
    return record
def build_picture():
    cards=json.loads((PROD/'shots.json').read_text(encoding='utf-8-sig'))
    cuts=INTRO[:]
    for number,card in sorted(cards.items()):
        key=number+'_'+card['slug']
        ver=2 if number in ('04','05','08','10') else 1
        cuts.append((f'{key}/{key}_v{ver}.mp4',card['frames']))
    manifest=[]
    cursor=0
    for number,(relative,frames) in enumerate(cuts,1):
        clip=EPISODE/relative
        if number>=4:
            assert cards[f'{number:02}']['start']*24==cursor, (number,cursor)
        video(clip,frames)
        manifest.append({'shot':number,'path':relative,'in_frame':cursor,'out_frame':cursor+frames,'in_seconds':cursor/24})
        cursor+=frames
    assert cursor==63*24
    (OUT/'picture_timeline.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    concat=OUT/'concat_picture.txt'
    concat.write_text(''.join("file '"+(EPISODE/info['path']).as_posix()+"'\n" for info in manifest),encoding='utf-8')
    if not CUT.exists():
        run(['ffmpeg','-n','-v','error','-f','concat','-safe','0','-i',str(concat),'-map','0:v:0','-c:v','copy','-an','-movflags','+faststart',str(CUT)])
    video(CUT,1512)
    print('Picture locked: 15 shots and 1512 video frames.',flush=True)
def measure(path):
    token='loudnorm=I=-15:TP=-1.55:LRA=11:print_format=json'
    report=run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-vn','-af',token,'-f','null','-']).stderr
    window=re.search(r'\{\s*"input_i".*?\}',report,re.S)
    assert window, report[-2000:]
    return json.loads(window.group())
def normalize(track):
    original=STEMS/'premaster.wav'
    initial=measure(original)
    gain=-14.85-float(initial['input_i'])
    attempt=track.with_name(track.stem+'_working.wav')
    for _ in range(3):
        filters=f'volume={gain:.4f}dB,aresample=192000,alimiter=limit=0.710:attack=3:release=70:level=false:latency=true,aresample=48000'
        run(['ffmpeg','-y','-v','error','-i',str(original),'-af',filters,'-c:a','pcm_s24le',str(attempt)])
        measured=measure(attempt)
        loudness=float(measured['input_i'])
        if -15.06<=loudness<=-14.64 and float(measured['input_tp'])<=-1.50:
            attempt.rename(track)
            return measured
        gain+=-14.85-loudness
    raise ValueError(f'Mix did not reach the broadcast loudness and peak targets: {measured}')
def finish(version):
    timeline=json.loads((ROOT/'audio_timeline.json').read_text(encoding='utf-8'))
    scored_only=bool(timeline['missing_takes'])
    label=f'score_only_v{version}' if scored_only else f'v{version}'
    final_path=OUT/f'5oclock_ep2_the_koban_{label}.mp4'
    track=OUT/f'5oclock_ep2_the_koban_mix_{label}.wav'
    loud=normalize(track) if not track.exists() else measure(track)
    assert -15.08<=float(loud['input_i'])<=-14.55, loud
    assert float(loud['input_tp'])<=-1.0,loud
    if not final_path.exists():
        run(['ffmpeg','-n','-v','error','-i',str(CUT),'-i',str(track),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-t','63','-movflags','+faststart',str(final_path)])
    final=video(final_path,1512,True)
    loud_final=measure(final_path)
    assert -15.10<=float(loud_final['input_i'])<=-14.50,loud_final
    assert float(loud_final['input_tp'])<=-1.0,loud_final
    (OUT/f'MASTER_QA_{label}.json').write_text(json.dumps({'picture':final,'mix_wav':loud,'final_aac':loud_final},indent=2))
    print('Scored cut:' if scored_only else 'Dialogue master:',final_path)
    print('AAC',loud_final['input_i'],'LUFS,',loud_final['input_tp'],'dBTP.')
if __name__=='__main__':
    if sys.argv[1]=='picture':build_picture()
    elif sys.argv[1]=='finish':finish(int(sys.argv[2]) if len(sys.argv)>2 else 3)



