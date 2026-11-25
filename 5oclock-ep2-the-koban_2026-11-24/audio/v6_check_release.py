"""Check the v6 master and produce a contact sheet from its decoded timeline."""
from pathlib import Path
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import re

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from revision_cut_v6 import OUT, count, run
from revision_mix_v6 import MASTER, WAVE, CUT, PROJECT
import assemble_episode as metrics

def frame_hashes(path,selector=None):
    cmd=['ffmpeg','-hide_banner','-v','error','-threads','3','-i',str(path),'-an']
    if selector:
        cmd+=['-vf',selector,'-fps_mode','passthrough']
    cmd+=['-f','framemd5','-']
    return [x.rsplit(',',1)[1].strip() for x in run(cmd).stdout.splitlines() if not x.startswith('#')]

def motion_metrics(path,segments):
    width,height=135,240
    raw=subprocess.check_output(['ffmpeg','-v','error','-threads','3','-i',str(path),
                                 '-an','-vf',f'scale={width}:{height}:flags=area',
                                 '-pix_fmt','gray','-f','rawvideo','-threads','2','-'])
    frames=np.frombuffer(raw,np.uint8).reshape((-1,height,width))
    assert len(frames)==segments[-1]['out_frame']
    results={}
    for row in segments:
        shot=row['shot']
        clip=frames[row['in_frame']:row['out_frame']].astype(np.int16)
        changes=np.abs(np.diff(clip,axis=0)).mean(axis=(1,2))
        if shot==14:
            changes=changes[:-7]
        results.setdefault(shot,[]).extend(changes)
    return [{'shot':shot,'pixel_change_mean':round(float(np.mean(changes)),3),
             'low_motion_pct':round(float(np.mean(np.array(changes)<.25))*100,1),
             'pairs':len(changes)} for shot,changes in results.items()]

def verify():
    steps=json.loads((OUT/'picture_timeline_v6.json').read_text())
    sounds=json.loads((OUT/'audio_timeline_v6.json').read_text())
    duration=steps[-1]['out_frame']/24
    assert len(sounds['dialogue'])==7
    assert all(v['tempo']==1 for v in sounds['dialogue'])
    assert all(abs((v['end']-v['start'])-v['source_trimmed_seconds'])<.001 for v in sounds['dialogue'])
    assert all(0<=v['start']<v['end']<=duration for v in sounds['dialogue'])
    assert count(CUT)==count(MASTER)==steps[-1]['out_frame']
    authored_end=next(r['in_frame'] for r in steps if r['id']=='15')
    target=(authored_end-7,authored_end)
    cmd=['ffmpeg','-hide_banner','-nostats','-threads','4','-i',str(MASTER),
         '-an','-vf','scale=135:240,blackdetect=d=0:pix_th=0.03:pic_th=0.995','-f','null','-']
    black=re.findall(r'black_start:([\d.]+) black_end:([\d.]+)',run(cmd).stderr)
    span=[(round(float(a)*24),round(float(b)*24)) for a,b in black]
    assert span==[target],(span,target)
    ids_by_frame={i for row in steps for i in (row['in_frame'],row['out_frame']-1)}
    expr='+'.join(f'eq(n,{i})' for i in sorted(ids_by_frame))
    actual=dict(zip(sorted(ids_by_frame),frame_hashes(MASTER,f"select='{expr}'")))
    def compare(row):
        frames=row['out_frame']-row['in_frame']
        boundaries=frame_hashes(row['segment'],f"select='eq(n,0)+eq(n,{frames-1})'")
        expected=[actual[row['in_frame']],actual[row['out_frame']-1]]
        assert boundaries==expected,(row['id'],row['segment'])
        return row['id']
    with ThreadPoolExecutor(max_workers=3) as pool:
        verified=list(pool.map(compare,steps))
    print(f'Verified {len(verified)} segment boundaries, {int(duration*24)} frames and authored black only.',flush=True)
    audio=metrics.measure(MASTER)
    gap_start,gap_end=sounds['theme_silence']
    silence=subprocess.check_output(['ffmpeg','-v','error','-ss',str(gap_start+.09),
                                     '-i',str(MASTER),'-t',str(gap_end-gap_start-.18),
                                     '-map','0:a:0','-c:a','pcm_f32le','-f','f32le','-'])
    values=np.frombuffer(silence,np.float32)
    assert len(values)>0
    gap_peak=float(abs(values).max())
    assert gap_peak<.001,gap_peak
    # Extract the timeline pictures at phone size.
    w,h=144,256
    raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(MASTER),'-an','-vf',
                                 f'scale={w}:{h}:flags=area','-pix_fmt','rgb24','-f','rawvideo','-threads','2','-'])
    pictures=np.frombuffer(raw,np.uint8).reshape((-1,h,w,3))
    font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',14)
    tile=Image.new('RGB',(6*w,((len(steps)+5)//6)*(h+25)),'#211e2a')
    d=ImageDraw.Draw(tile)
    for i,row in enumerate(steps):
        at=(row['in_frame']+row['out_frame'])//2
        x=(i%6)*w;y=(i//6)*(h+25)
        tile.paste(Image.fromarray(pictures[at]),(x,y+25))
        d.text((x+3,y+3),f"{row['id']}  {at/24:05.2f}s",font=font,fill='white')
    tile.save(OUT/'contact_v6.jpg',quality=93)
    before=json.loads((PROJECT/'episode'/'picture_timeline.json').read_text())
    after=[{**r,'shot':r['part_of_shot']} for r in steps]
    comparison={'method':'Within-segment mean absolute grayscale delta, 135x240; low motion below 0.25/255. Excludes the authored blackout.',
                'v5':motion_metrics(MASTER.with_name('5oclock_ep2_the_koban_v5.mp4'),before),
                'v6':motion_metrics(MASTER,after)}
    (OUT/'MOTION_QA_V6.json').write_text(json.dumps(comparison,indent=2),encoding='utf-8')
    report={'frames':len(pictures),'duration':duration,'black_span_frames':span,
            'boundary_matches':verified,'voice_count':len(sounds['dialogue']),
            'audio':audio,'theme_gap_seconds':gap_end-gap_start,'theme_gap_decoded_peak':gap_peak}
    (OUT/'RELEASE_QA_V6.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(f"Final AAC {audio['input_i']} LUFS, {audio['input_tp']} dBTP, {audio['input_lra']} LU range.",flush=True)

if __name__=='__main__':
    verify()
