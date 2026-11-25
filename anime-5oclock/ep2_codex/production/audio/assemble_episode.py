"""Assemble and verify the picture-locked episode and loudness-normalized stereo mix."""
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent
PROD=ROOT.parent
EPISODE=PROD.parent
OUT=EPISODE/'episode'
OUT.mkdir(exist_ok=True)
CUT=OUT/'5oclock_ep2_the_koban_silent_v1.mp4'
FINAL=OUT/'5oclock_ep2_the_koban_v1.mp4'
STEMS=ROOT/'stems'
TRACK=OUT/'5oclock_ep2_the_koban_mix_v1.wav'
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
        ver=2 if number in ('04','08') else 1
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
def normalize():
    original=STEMS/'premaster.wav'
    first=measure(original)
    filter='loudnorm=I=-15:TP=-1.55:LRA=11:linear=true'
    for key,label in [('measured_I','input_i'),('measured_TP','input_tp'),('measured_LRA','input_lra'),('measured_thresh','input_thresh'),('offset','target_offset')]:
        filter+=f':{key}={first[label]}'
    run(['ffmpeg','-n','-v','error','-i',str(original),'-af',filter,'-ar','48000','-c:a','pcm_s24le',str(TRACK)])
    return measure(TRACK)
def finish():
    loud=normalize() if not TRACK.exists() else measure(TRACK)
    assert -16<=float(loud['input_i'])<=-14, loud
    assert float(loud['input_tp'])<=-1.0,loud
    if not FINAL.exists():
        run(['ffmpeg','-n','-v','error','-i',str(CUT),'-i',str(TRACK),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','256k','-t','63','-movflags','+faststart',str(FINAL)])
    final=video(FINAL,1512,True)
    loud_final=measure(FINAL)
    assert -16<=float(loud_final['input_i'])<=-14,loud_final
    assert float(loud_final['input_tp'])<=-1.0,loud_final
    (OUT/'MASTER_QA.json').write_text(json.dumps({'picture':final,'mix_wav':loud,'final_aac':loud_final},indent=2))
    print('Final episode:',FINAL)
    print('AAC',loud_final['input_i'],'LUFS,',loud_final['input_tp'],'dBTP.')
if __name__=='__main__':
    if sys.argv[1]=='picture':build_picture()
    elif sys.argv[1]=='finish':finish()


