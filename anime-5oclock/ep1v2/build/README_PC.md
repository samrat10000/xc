# 5 O'CLOCK Ep1 v2: build on the PC (all steps local)
Python 3.11+: pip install pycairo numpy scipy pillow . ffmpeg on PATH.
Assets:
- git clone --depth 1 --filter=blob:none --sparse https://github.com/sgossner/VSCO-2-CE vsco ; cd vsco ; git sparse-checkout set Percussion/Marimba Percussion/Glock
- python of.py "crows=crows cawing" "wires=wind power lines hum"   (into ./snd: run from a folder named snd, or move the folders into snd/)
Timeline (21.0 s, 24 fps):
| shot | frames | how |
|---|---|---|
| 001_mirror | 120 (5.0 s) | python render.py shot001 120 fr001 |
| 002_speaker | 84 (3.5 s) | python render.py shot002 84 fr002 |
| 003_sam | 84 (3.5 s) | toon alpha frames (Blender, 72) + hold last 12 -> python comp003.py <alpha_dir> fr003 |
| 004_street | 108 (4.5 s) | python render.py shot004 108 fr004 |
| 005_answer | 108 (4.5 s) | set NOTE_T=1.9, BLACK_T=2.6 then python render.py shot005 108 fr005 |
Each: ffmpeg -framerate 24 -i frNNN/%04d.png -c:v libx264 -crf 18 -pix_fmt yuv420p NNN_name_v2_silent.mp4
Sound: python mix_v2.py <flow_take.mp3> <ep1v2/audio dir> mix_v2.wav ; then loudnorm I=-15 TP=-1.5.
Per-shot clips = cut the mixed wav at 0/5.0/8.5/12.0/16.5/21.0 s and mux with each shot. Send each to Sam separately (shot by shot), then the full cut.
