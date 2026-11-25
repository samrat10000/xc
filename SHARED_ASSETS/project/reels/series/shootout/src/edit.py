"""Assemble The 43rd Round: shot frames -> 24 fps 1080x1920 graded timeline. usage: python3 edit.py SRC_DIR OUT.mp4 [audio.wav]"""
import os, sys, subprocess, glob, shutil
SRC, OUT = sys.argv[1], sys.argv[2]; AUD = sys.argv[3] if len(sys.argv) > 3 else None
# (shot, first frame, last frame) in render frames; 720 frames total incl. black
EDL = [(1, 1, 60), (2, 1, 60), (3, 3, 62), (4, 1, 96), (5, 1, 96), (6, 1, 48), (7, 1, 60), (8, 1, 60), (9, 1, 72), (10, 1, 48), (11, 1, 46)]
BLACK = 720 - sum(b - a + 1 for _, a, b in EDL)
tmp = '/home/user/w/out/edit_tmp'; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
k = 0; black = None
for s, a, b in EDL:
    have = sorted(int(os.path.basename(p)[1:5]) for p in glob.glob(f'{SRC}/s{s:02d}/f*.png') + glob.glob(f'{SRC}/s{s}/f*.png'))
    d = f'{SRC}/s{s}' if os.path.isdir(f'{SRC}/s{s}') else f'{SRC}/s{s:02d}'
    for f in range(a, b + 1):
        prev = [h for h in have if h <= f] or have[:1]
        src = f'{d}/f{prev[-1]:04d}.png'
        os.symlink(src, f'{tmp}/{k:05d}.png'); k += 1
black_n = BLACK
print('frames', k, 'black', black_n)
font = '/home/user/w/fonts/oswald.ttf'
vf = ("scale=1080:1920:flags=lanczos,"
      "eq=contrast=1.04:saturation=1.05,"
      "vignette=angle=0.5,"
      "noise=alls=7:allf=t,"
      f"drawtext=fontfile={font}:text='SHE BROUGHT 42 ROUNDS.':fontsize=58:fontcolor=0xE9E1CF:x=(w-text_w)/2:y=h*0.17:"
      "shadowcolor=black@0.8:shadowx=0:shadowy=3:enable='lt(t,1.6)':alpha='if(lt(t,1.2),1,(1.6-t)/0.4)',"
      f"tpad=stop={black_n}:color=black")
cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-framerate', '24', '-i', f'{tmp}/%05d.png']
if AUD: cmd += ['-i', AUD]
cmd += ['-vf', vf, '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p']
if AUD: cmd += ['-c:a', 'aac', '-b:a', '256k', '-shortest']
cmd += ['-t', '30', OUT]
subprocess.run(cmd, check=True); print('wrote', OUT)
