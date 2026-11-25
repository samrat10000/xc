"""Write the per-shot delivery index from the verified timeline and approved files."""
from pathlib import Path
import json

episode=Path(__file__).resolve().parent.parent
out=episode/'episode'
timing=json.loads((out/'picture_timeline.json').read_text(encoding='utf-8'))
master=out/'5oclock_ep2_the_koban_v1.mp4'
assert master.exists() and (out/(master.stem+'_picture_QA.json')).exists()
labels=['Alarm','Wrong room','The crack','Mirror-Mom','The street','The koban','The rules',
        'Mom calls','Behind him','The window','16:59','The horns turn','Rule one','The knock','Rule eight']

def format_frame(number):
    seconds=number//24
    return f'{seconds//60}:{seconds%60:02d}'

output=['# 5 O’CLOCK Episode 2', '', '## Day 2 · The Koban', '',
        '[Watch the complete reel](5oclock_ep2_the_koban_v1.mp4) · '
        '[Silent cut](5oclock_ep2_the_koban_silent_v1.mp4) · '
        '[Stereo WAV](5oclock_ep2_the_koban_mix_v1.wav)', '',
        '63 seconds · 1080 × 1920 · 24 fps · stereo dialogue, piano, chime and foley', '',
        '| Time | Shot | Full-size PNGs |', '| --- | --- | --- |']
for info,label in zip(timing,labels):
    path=episode/info['path']
    images=sorted(path.parent.glob(path.stem+'_f*.png'))
    assert len(images)==4, (path,images)
    time=f"{format_frame(info['in_frame'])}–{format_frame(info['out_frame_exclusive'])}"
    shot=f"[{info['shot']:02d} {label}](../{info['path']})"
    stills=' · '.join(f"[{a.stem[-3:]}](../{a.relative_to(episode).as_posix()})" for a in images)
    output.append(f'| {time} | {shot} | {stills} |')
output+=['', '## Production notes', '',
         'Each shot has a source folder with its build entry point. The shared recipe lives in the production folder.',
         'The call audio uses locally rendered stock voices. The same voice plays Sam and Mirror-Sam.',
         'The reversed clock digits and the brief cut to black before the notebook stinger are deliberate.',
         '', '[Sound sources](../production/audio/SOURCES.md) · '
         '[Picture and sound validation](MASTER_QA.json) · '
         '[Motion2d lessons](../../codex_ep2/MOTION2D_QA_LEARNINGS.md)']
(out/'DELIVERY.md').write_text('\n'.join(output)+'\n',encoding='utf-8')

