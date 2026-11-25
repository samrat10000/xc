import subprocess, os
from PIL import Image
ed = r'C:\Users\cross\Downloads\xc\5oclock-ep1-the-fourth-note_2026-11-23\edit'; out = r'C:\Users\cross\Downloads\xc\5oclock-ep1-the-fourth-note_2026-11-23\edit\5oclock_ep1_v2_silent.mp4'; starts = [0, 72, 144, 228, 324, 408, 456, 564, 684, 756, 840, 924, 1008, 1080, 1164, 1272, 1344, 1416, 1512]
sh = Image.new('RGB', (9 * 160, 2 * 284))
for i in range(18):
    m = (starts[i] + starts[i + 1]) // 2; p = os.path.join(ed, 'tmp_%02d.png' % i)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', out, '-vf', 'select=eq(n\\,%d)' % m, '-vframes', '1', p])
    sh.paste(Image.open(p).resize((160, 284)), ((i % 9) * 160, (i // 9) * 284)); os.remove(p)
sh.save(os.path.join(ed, 'storyboard_check_v2.png'))