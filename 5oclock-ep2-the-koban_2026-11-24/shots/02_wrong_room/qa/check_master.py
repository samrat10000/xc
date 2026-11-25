from pathlib import Path
from PIL import Image
import json, math, numpy as np

qa=Path(r'C:/Users/cross/Downloads/xc/anime-5oclock/ep2_codex/02_wrong_room/qa')
data=json.loads((qa/'v1_cel'/'frame_meta.json').read_text())
samples=[data[str(f)] for f in range(1,97)]
assert len(data)==96
for a,b in zip(samples[::2],samples[1::2]):
    assert math.dist(a['support_wrist'],b['support_wrist'])<1e-6
wrist_max=max(e for f in samples for e in f['wrist_error_m'])
anchor=samples[0]['support_wrist']
drift=max(math.dist(f['support_wrist'],anchor) for f in samples)
assert wrist_max<.02
assert drift<.001
phone=np.array([f['screen'] for f in samples[72:]])
assert phone.min()>0 and phone.max()<1
face_part=(np.array([f['head'] for f in samples[:72]]))*np.array([1080,1920])
assert 0<face_part[:,0].min()<face_part[:,0].max()<1080
assert face_part[:,1].max()<1920*.85
for i in range(1,97):
    with Image.open(qa/'v1_frames'/f'{i:03d}.png') as img:
        assert img.mode=='RGB' and img.size==(1080,1920),str(i)
        img.verify()
print(f"Wrist target error <= {wrist_max*1000:.6f} mm. Planted wrist drift <= {drift*1000:.6f} mm.")
print(f"Phone glass screen bounds {phone[:,:,0].min():.3f}–{phone[:,:,0].max():.3f} x, {phone[:,:,1].min():.3f}–{phone[:,:,1].max():.3f} y.")
print("96 intact RGB frames at 1080 × 1920. Head stays within frame in the entire room move.")

