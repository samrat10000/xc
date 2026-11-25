"""Transcribe the mixed release locally and compare it to the selected locked takes."""
from pathlib import Path
import json
import re
import sys

from faster_whisper import WhisperModel
import numpy as np
import subprocess

from revision_mix_v6 import MASTER, OUT

def plain(text):
    cleaned=re.sub(r'[^a-z0-9 ]','',' '.join(text.lower().split()))
    return cleaned.replace('11','eleven').replace('8','eight')

def main(model_path):
    events=json.loads((OUT/'audio_timeline_v6.json').read_text())['dialogue']
    model=WhisperModel(model_path,device='cpu',compute_type='int8',cpu_threads=6,local_files_only=True)
    result=[]
    for line in events:
        start=line['start']-.08
        length=(line['end']-start)+.065
        raw=subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(MASTER),
            '-t',str(length),'-vn','-ac','1','-ar','16000','-f','f32le','-'])
        pcm=np.pad(np.frombuffer(raw,'<f4'),(2400,4000))
        segments,_=model.transcribe(pcm,language='en',beam_size=4,condition_on_previous_text=False)
        actual=' '.join(s.text.strip() for s in segments).strip()
        verdict=plain(actual)==plain(line['text'])
        result.append({'id':line['id'],'script':line['text'],'transcription':actual,'match':verdict})
        print(line['id'],actual,verdict,flush=True)
    (OUT/'DIALOGUE_QA_V6.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    assert all(v['match'] for v in result),[v for v in result if not v['match']]

if __name__=='__main__':
    main(sys.argv[1])
