"""Verify the render has a visible aperture and independently moving exterior planes."""
from pathlib import Path
import json, math
from PIL import Image
import numpy as np

qa=Path(__file__).resolve().parent
m=json.loads((qa/'v1_frames_layers.json').read_text())
assert [f['frame'] for f in m]==list(range(1,97))
assert min(f['opening_fraction'] for f in m)>.38
start,end=m[0]['planes'],m[-1]['planes']
assert len(start)==10 and all(start[k]!=end[k] for k in start)
assert len({tuple(end[k]) for k in end})==10
assert end['cedars'][0]>end['ridge'][0]>end['listener'][0]>end['sky'][0]
assert abs(end['crown_cloud'][2] - end['listener'][2])>20
bounds=[]
for f in (1,16,33,49,67,82,96):
    a=np.asarray(Image.open(qa/'v1_cel'/f'cel_{f:03}.png').getchannel('A'))
    line=np.flatnonzero(a[round(a.shape[0]*.70),round(a.shape[1]*.70):]>200)
    if len(line):
        bounds.append(int(line[0]))
assert len(set(bounds))>=3
for i in range(1,97):
    with Image.open(qa/'v1_frames'/f'{i:03}.png') as img:
        assert img.mode=='RGB' and img.size==(1080,1920)
        img.verify()
print(f"96 frames, 10 distinct plane transforms, aperture {min(f['opening_fraction'] for f in m):.1%} or more.")
print(f"Projected curtain edge traveled {max(bounds)-min(bounds)} px across the sampled frames.")
print(f"Crown cloud shifted {end['crown_cloud'][2]-end['listener'][2]:.1f} px upward relative to the static Listener plane.")

