"""Build the v6 picture from reviewed shot versions and frame-accurate editorial trims."""
from pathlib import Path
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

PROJECT=Path(__file__).resolve().parent.parent
OUT=PROJECT/'episode'/'v6'
SHOTS=PROJECT/'shots'
KEEP={
  1:('alarm',1,72), 2:('wrong_room',2,96), 3:('the_crack',1,96),
  4:('mirror_mom',2,96), 5:('the_street',3,96), 6:('the_koban',1,120),
  7:('the_rules',2,128), 8:('mom_calls',2,96), 9:('behind_him',1,96),
  10:('the_window',3,96), 11:('1659',1,96), 12:('the_horns_turn',2,120),
  13:('rule_one',2,120), 14:('the_knock',2,120), 15:('rule_eight',2,96),
}
selection=OUT/'revision_selection.json'
if selection.exists():
    for number,version in json.loads(selection.read_text(encoding='utf-8')).items():
        slug,_,frames=KEEP[int(number)]
        KEEP[int(number)]=(slug,version,frames)
# The source out frame is exclusive. Segment count is independent of shot count.
EDITS=[
 ('01a','L',46,64,'crop=720:1280:330:94,scale=1080:1920,eq=saturation=0.91'),
 ('01b','01',3,33,''),
 ('02','02',0,96,''),
 ('03','03',0,90,''),
 ('04','04',0,96,''),
 ('05a','05',0,42,''),
 ('05b','05',52,96,''),
 ('06','06',0,98,''),
 ('07','07',0,128,''),
 ('08','08',0,70,''),
 ('09','09',34,85,''),
 ('10','10',0,96,''),
 ('11','11',24,79,''),
 ('12','12',0,120,''),
 ('13a','13',0,68,''),
 ('13b','L',77,101,'crop=972:1728:108:56,scale=1080:1920,eq=saturation=0.93:gamma=1.03'),
 ('13c','13',84,120,''),
 ('14','14',0,120,''),
 ('15','15',0,96,''),
]

def run(args):
    done=subprocess.run(args,capture_output=True,text=True)
    if done.returncode:
        raise RuntimeError(done.stderr.strip())
    return done

def count(path):
    out=run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries',
             'stream=nb_read_frames,width,height,r_frame_rate','-of','json',str(path)])
    stream=json.loads(out.stdout)['streams'][0]
    assert (stream['width'],stream['height'],stream['r_frame_rate'])==(1080,1920,'24/1'),(path,stream)
    return int(stream['nb_read_frames'])

def source(name):
    if name=='L':
        return OUT/'listener_ep1_reference.mp4',108
    slug,version,frames=KEEP[int(name)]
    ident=f'{name}_{slug}'
    return SHOTS/ident/f'{ident}_v{version}.mp4',frames

def plan():
    timeline=[]
    position=0
    for label,ident,start,end,grade in EDITS:
        raw,expected=source(ident)
        if end>expected:
            raise ValueError((label,end,expected))
        timeline.append({'id':label,'part_of_shot':int(label[:2]),'asset':str(raw),
                         'source_in':start,'source_out':end,'in_frame':position,
                         'out_frame':position+end-start,'filter':grade})
        position+=end-start
    return timeline

def segment(entry):
    raw=Path(entry['asset'])
    expected=entry['source_out']-entry['source_in']
    if not raw.exists():
        raise FileNotFoundError(raw)
    if not entry['filter'] and entry['source_in']==0 and expected==source(next(v[1] for v in EDITS if v[0]==entry['id']))[1]:
        assert count(raw)==expected,(raw,expected)
        return raw
    initial={'01a':'03_the_crack_v1','01b':'01_alarm_v1','03':'03_the_crack_v1',
             '06':'06_the_koban_v1','08':'08_mom_calls_v2','09':'09_behind_him_v1',
             '11':'11_1659_v1','13b':'listener_ep1_reference'}
    tag=entry['id'] if initial.get(entry['id'])==raw.stem else f"{entry['id']}_{raw.stem}"
    out=OUT/f'{tag}_edit.mp4'
    if not out.is_file():
        start,end=entry['source_in'],entry['source_out']
        pipeline=f'trim=start_frame={start}:end_frame={end},setpts=PTS-STARTPTS'
        if entry['filter']:
            pipeline+=','+entry['filter']
        env=out.with_name(out.stem+'_working.mp4')
        run(['ffmpeg','-y','-v','error','-threads','3','-filter_threads','2','-i',str(raw),'-an','-vf',pipeline,
             '-frames:v',str(expected),'-c:v','libx264','-preset','veryfast','-crf','15','-pix_fmt','yuv420p',
             '-threads','4','-movflags','+faststart',str(env)])
        assert count(env)==expected,(entry,count(env))
        env.rename(out)
    assert count(out)==expected,(entry,expected)
    return out

def main(prepare=False):
    OUT.mkdir(exist_ok=True)
    timeline=plan()
    manifest=OUT/'picture_timeline_v6.json'
    manifest.write_text(json.dumps(timeline,indent=2),encoding='utf-8')
    if prepare:
        # Prepare editorial trims of already approved assets while new pictures render.
        existing=[step for step in timeline if Path(step['asset']).is_file()]
        for step in existing:
            if step['filter'] or step['source_in'] or step['source_out']!=source(next(row[1] for row in EDITS if row[0]==step['id']))[1]:
                segment(step)
        return
    with ThreadPoolExecutor(max_workers=2) as jobs:
        files=list(jobs.map(segment,timeline))
    for entry,path in zip(timeline,files):
        entry['segment']=str(path)
    manifest.write_text(json.dumps(timeline,indent=2),encoding='utf-8')
    concat=OUT/'concat_v6.txt'
    concat.write_text(''.join(f"file '{p.as_posix()}'\n" for p in files),encoding='utf-8')
    cut=OUT/'5oclock_ep2_the_koban_silent_v6.mp4'
    if not cut.exists():
        run(['ffmpeg','-n','-v','error','-f','concat','-safe','0','-i',str(concat),'-map','0:v','-c:v','copy','-an',
             '-movflags','+faststart',str(cut)])
    frames=timeline[-1]['out_frame']
    assert count(cut)==frames,(cut,frames)
    print(f'Picture v6 locked: {frames} frames ({frames/24:.3f} s)',flush=True)

if __name__=='__main__':
    main('--prepare' in sys.argv)

