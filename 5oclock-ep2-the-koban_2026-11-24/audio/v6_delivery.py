"""Index reviewed v6 assets and frame-accurate trim decisions."""
from pathlib import Path
import json
import os
from revision_mix_v6 import MASTER, WAVE, CUT
from revision_cut_v6 import OUT

qa=json.loads((OUT/'RELEASE_QA_V6.json').read_text())
timeline=json.loads((OUT/'picture_timeline_v6.json').read_text())
audio=json.loads((OUT/'audio_timeline_v6.json').read_text())
parent=MASTER.parent
labels=['Alarm','Wrong room','The crack','Mirror-Mom','The street','The koban','The rules',
        'Mom calls','Behind him','The window','16:59','The horns turn','Rule one','The knock','Rule eight']
def relative(path):
    assert Path(path).exists(),path
    return Path(os.path.relpath(path,parent)).as_posix()

def t(frame):
    return f'{frame//1440}:{frame/24%60:05.2f}'

result=['# 5 O’CLOCK Episode 2 · The Koban v6','',
        f'[Full reel]({relative(MASTER)}) · [Silent cut]({relative(CUT)}) · [Stereo WAV]({relative(WAVE)}) · '
        '[Timeline contact sheet](v6/contact_v6.jpg)','',
        f"{qa['duration']:.2f} seconds · 1080 × 1920 · 24 fps · 15 story beats",'',
        '## Shot sources','',
        '| Time | Beat | Source clips |', '| --- | --- | --- |']
for i,label in enumerate(labels,1):
    rows=[r for r in timeline if r['part_of_shot']==i]
    assert rows
    links=' · '.join(f"[{row['id']}]({relative(row['segment'])})" for row in rows)
    result.append(f"| {t(rows[0]['in_frame'])}–{t(rows[-1]['out_frame'])} | {i:02d} {label} | {links} |")
result+=['','## Audio','',
         f"The AAC master measures {qa['audio']['input_i']} LUFS, {qa['audio']['input_tp']} dBTP and {qa['audio']['input_lra']} LU loudness range.",
         'The revised cut uses the seven selected ElevenLabs takes without speeding them up, omits the redundant time-jump line, and keeps the four town chime notes.',
         'The encoded score gap was verified at 0.62 seconds. Dialogue checks use local transcription. Human listening is pending.',
         '', '[Revision notes](../V6_REVISION.md) · [Shot verification](v6/RELEASE_QA_V6.json) · '
         '[Dialogue timing](v6/audio_timeline_v6.json) · [Dialogue transcript](v6/DIALOGUE_QA_V6.json) · '
         '[Motion comparison](v6/MOTION_QA_V6.json)']
(parent/'DELIVERY_V6.md').write_text('\n'.join(result)+'\n',encoding='utf-8')

