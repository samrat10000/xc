"""Verify cut boundaries by comparing decoded frames, and count authored black frames."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT.parent/'episode'
TIMELINE=OUT/'picture_timeline.json'
BLACK_START=55*24+113
BLACK_END=60*24

def decode_hashes(path,frames=None):
    cmd=['ffmpeg','-v','error','-threads','2','-i',str(path),'-map','0:v:0']
    if frames is not None:
        cmd+=['-vf',"select='eq(n,0)+eq(n,{} )'".format(frames-1)]
    cmd+=['-an','-fps_mode','passthrough','-f','framemd5','-']
    data=subprocess.check_output(cmd,text=True)
    return [line.rsplit(',',1)[1].strip() for line in data.splitlines() if line and not line.startswith('#')]

def black_spans(path):
    probe=subprocess.run(['ffmpeg','-hide_banner','-nostats','-threads','2','-i',str(path),
        '-map','0:v:0','-an','-vf','blackdetect=d=0:pix_th=0.03:pic_th=0.995','-f','null','-'],
        check=True,capture_output=True,text=True)
    return [(round(float(a)*24),round(float(b)*24)) for a,b in
            re.findall(r'black_start:([\d.]+) black_end:([\d.]+)',probe.stderr)]

def main():
    master=Path(sys.argv[1]).resolve()
    cuts=json.loads(TIMELINE.read_text(encoding='utf-8'))
    # Decode once to verify sequence and exact frame count after concatenation or remux.
    whole=decode_hashes(master)
    assert len(whole)==1512, len(whole)
    spans=black_spans(master)
    assert spans==[(BLACK_START,BLACK_END)], spans
    def compare(cut):
        start,end=cut['in_frame'],cut['out_frame']
        hashes=decode_hashes(ROOT/cut['path'],end-start)
        assert hashes==[whole[start],whole[end-1]], (cut,hashes)
        return {'shot_number':cut['shot'],'in_frame':start,'out_frame_exclusive':end,
                'first_and_last_frame_match':True}
    with ThreadPoolExecutor(max_workers=3) as worker:
        verified=list(worker.map(compare,cuts))
    repeated=[i for i in range(1,len(whole)) if whole[i]==whole[i-1] and not BLACK_START<i<BLACK_END]
    report={'master':master.name,'video_frames':len(whole),'authored_black_ranges':spans,
            'nonblack_identical_neighbor_frames':repeated,'cut_boundaries':verified}
    (OUT/(master.stem+'_picture_QA.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(f'Picture QA: {len(whole)} decoded frames, {len(verified)} matched cuts, and {BLACK_END-BLACK_START} authored black frames.')
    print(f'{len(repeated)} identical nonblack neighboring frames (animation holds reported for review).')

if __name__=='__main__':
    main()
