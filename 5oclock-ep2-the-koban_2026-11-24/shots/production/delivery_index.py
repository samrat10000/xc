"""Index the verified reel, shot masters, reference stills, and recording materials."""
from pathlib import Path
import json
import sys

project=Path(__file__).resolve().parents[2]
shots=project/'shots'
out=project/'episode'
timing=json.loads((out/'picture_timeline.json').read_text(encoding='utf-8'))
takes=json.loads((project/'audio'/'audio_timeline.json').read_text(encoding='utf-8'))
pending=bool(takes['missing_takes'])
version=int(sys.argv[1]) if len(sys.argv)>1 else 3
label=f'score_only_v{version}' if pending else f'v{version}'
title='Scored cut' if pending else 'Full reel'
master=out/f'5oclock_ep2_the_koban_{label}.mp4'
assert master.is_file() and (out/(master.stem+'_picture_QA.json')).is_file()
titles=['Alarm','Wrong room','The crack','Mirror-Mom','The street','The koban','The rules',
        'Mom calls','Behind him','The window','16:59','The horns turn','Rule one','The knock','Rule eight']

def time(frame):
    seconds=frame//24
    return f'{seconds//60}:{seconds%60:02d}'

index=['# 5 O’CLOCK Episode 2', '', '## Day 2 · The Koban', '',
       f'[{title}]({master.name}) · [Silent cut](5oclock_ep2_the_koban_silent_v1.mp4) · '
       f'[Stereo WAV](5oclock_ep2_the_koban_mix_{label}.wav)', '',
       '63 seconds · 1080 × 1920 · 24 fps', '',
       'The scored cut contains piano, chime and foley. The ElevenLabs dialogue takes are pending.'
       if pending else 'The stereo mix includes dialogue, piano, chime and foley.', '',
       '| Time | Shot | Full-size PNGs |', '| --- | --- | --- |']
assert len(timing)==len(titles)
for info,name in zip(timing,titles):
    path=shots/info['path']
    frames=sorted(path.parent.glob(path.stem+'_f*.png'))
    assert len(frames)==4,(path,frames)
    stills=' · '.join(f"[{a.stem[-3:]}](../shots/{a.relative_to(shots).as_posix()})" for a in frames)
    period=f"{time(info['in_frame'])}–{time(info['out_frame'])}"
    clip=f"[{info['shot']:02d} {name}](../shots/{info['path']})"
    index.append(f'| {period} | {clip} | {stills} |')
index+=['', '[Voice script](../audio/VOICE_SCRIPT.md) · [Sound sources](../audio/SOURCES.md) · '
        f'[Master verification](MASTER_QA_{label}.json) · [Production log](../PRODUCTION_LOG.md) · '
        '[Motion2d lessons](../MOTION2D_QA_LEARNINGS.md)']
(out/'DELIVERY.md').write_text('\n'.join(index)+'\n',encoding='utf-8')
