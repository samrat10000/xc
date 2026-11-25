"""Ep1 v6 picture edit: found-footage / camcorder look. Timeline on the v6 music clock (52 s).
Each entry: (t0, t1, source, f_in, f_out). source = frame dir (f####.png / f_####.png) or .mp4.
Frames are retimed to fill [t0, t1] (nearest frame, never blended). Output: out/v6/ep1_v6_picture.mp4 (+ music if MUSIC set).
env: MUSIC=path.wav  SFX=path.wav  OUT=path"""
import os, glob, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(HERE, 'out'); V6 = os.path.join(O, 'v6')
FPS = 24
TL = [   # v6b: on the v5 Flow music clock (hits 2.667 eruption, 8.0 scream, 13.333 jolt, 18.667 ignition ... 38.667 lunge), 52 s
    (0.000, 0.500, 'cuts/c22', 46, 54),          # cold open: a flash of the Stalker's lunge
    (0.500, 5.000, 'v6/wakeup', 1, 108),         # phone buzzes 1.75, eruption on the 2.667 hit
    (5.000, 6.167, 'cuts/c04', 1, 24),
    (6.167, 8.000, 'cuts/c05', 1, 36),           # the Screamer on the rooftop
    (8.000, 10.667, 'cuts_slow/c06', 1, 64),     # the scream (call drops)
    (10.667, 13.833, 'v6/c30', 1, 76),           # POV down the stairwell, Crawler jolt on 13.333
    (13.833, 15.833, 'cuts/c08', 1, 48),         # the horde
    (15.833, 18.667, 'v6/c31', 1, 58),           # POV garage run, ignition on 18.667
    (18.667, 19.292, 'cuts/c10', 12, 26),        # headlights
    (19.292, 20.792, 'cuts/c12', 1, 36),
    (20.792, 23.917, 'cuts_slow/c13', 1, 75),
    (23.917, 24.917, 'cuts/c14', 1, 24),
    (24.917, 27.292, 'cuts/c152', 1, 57),        # burst + boom freeze
    (27.292, 29.833, 'cuts/c162', 1, 61),        # skid to a stop
    (29.833, 31.708, 'cuts/c17', 1, 45),
    (31.708, 33.375, 'cuts_slow/c18', 1, 38),
    (33.375, 34.667, 'cuts_slow/c19', 1, 31),
    (34.667, 36.417, 'cuts/c20', 31, 72),        # overpass: "Akash, pick up"
    (36.417, 38.667, 'cuts/c22', 1, 54),         # stare -> scream -> lunge on the hit
    (38.667, 46.667, 'v6/missed', 1, 192),       # phone lights up on the passenger seat: missed call
    (46.667, 52.000, 'v6/missed', 192, 192),     # hold under Akash's voicemail
]

def frames(src):
    p = os.path.join(O, src)
    if p.endswith('.mp4') or os.path.exists(p + '.mp4'):
        mp = p if p.endswith('.mp4') else p + '.mp4'; d = mp[:-4] + '_fr'; os.makedirs(d, exist_ok=True)
        if not glob.glob(d + '/*.png'): subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', mp, d + '/f%04d.png'], check=True)
        p = d
    fs = sorted(glob.glob(p + '/*.png'))
    if not fs: sys.exit(f'missing frames: {src}')
    return fs

def build():
    seq = os.path.join(V6, 'seq'); os.makedirs(seq, exist_ok=True)
    for f in glob.glob(seq + '/*.png'): os.remove(f)
    n = 0
    for t0, t1, src, a, b in TL:
        fs = frames(src); a = max(1, a); b = min(len(fs), b)
        k = round((t1 - t0) * FPS)
        for i in range(k):
            j = a + int((b - a + 1) * i / k); n += 1
            os.symlink(fs[min(j, b) - 1], f'{seq}/s{n:05d}.png')
    return seq, n

# camcorder / phone-footage treatment: soft resolve, chroma offset + bleed, sensor noise, slight gate weave, lifted blacks, vignette
LOOK = ('scale=1080:1920:flags=lanczos,'
        'scale=720:1280:flags=bilinear,scale=1080:1920:flags=bicubic,'
        'rgbashift=rh=2:bh=-2,'
        "crop=1072:1906:4+2*sin(n/9):7+2*sin(n/13+1),scale=1080:1920,"
        'eq=contrast=1.05:saturation=.88:gamma=1.04,'
        'curves=all=0/0.035 0.5/0.5 1/0.96,'
        'noise=c0s=10:c0f=t+u:c1s=6:c1f=t,'
        'vignette=PI/4.6,format=yuv420p')

if __name__ == '__main__':
    seq, n = build()
    out = os.environ.get('OUT', os.path.join(V6, 'ep1_v6.mp4'))
    cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', seq + '/s%05d.png']
    aud = [a for a in (os.environ.get('MUSIC'), os.environ.get('SFX')) if a]
    for a in aud: cmd += ['-i', a]
    cmd += ['-vf', LOOK, '-c:v', 'libx264', '-crf', '17', '-preset', 'slow']
    if len(aud) == 2: cmd += ['-filter_complex', '[1:a][2:a]amix=inputs=2:normalize=0[a]', '-map', '0:v', '-map', '[a]']
    if aud: cmd += ['-c:a', 'aac', '-b:a', '256k', '-shortest']
    subprocess.run(cmd + [out], check=True); print('OUT', out, n, 'frames')
