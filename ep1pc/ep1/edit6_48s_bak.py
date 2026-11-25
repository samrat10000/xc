"""Ep1 v6 picture edit: found-footage / camcorder look. Timeline on the v6 music clock (53 s).
Each entry: (t0, t1, source, f_in, f_out). source = frame dir (f####.png / f_####.png) or .mp4.
Frames are retimed to fill [t0, t1] (nearest frame, never blended). Output: out/v6/ep1_v6_picture.mp4 (+ music if MUSIC set).
env: MUSIC=path.wav  SFX=path.wav  OUT=path"""
import os, glob, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); O = os.path.join(HERE, 'out'); V6 = os.path.join(O, 'v6')
FPS = 24
TL = [
    (0.000, 1.000, 'cuts/c22', 44, 54),          # cold open: the Stalker's lunge (loops with the end)
    (1.000, 5.500, 'v6/wakeup', 1, 108),         # wake-up: phone buzzes, tower erupts
    (5.500, 8.000, 'cuts/c05', 1, 36),           # the Screamer on the rooftop
    (8.000, 10.500, 'cuts_slow/c06', 1, 64),     # the scream
    (10.500, 14.000, 'v6/c30', 1, 84),           # POV down the stairwell, the Crawler on the landing (jolt ~13.2)
    (14.000, 16.500, 'cuts/c08', 1, 60),         # the horde
    (16.500, 19.500, 'v6/c31', 1, 72),           # POV garage run, ignition at 18.9
    (19.500, 20.500, 'cuts/c10', 12, 36),
    (20.500, 22.000, 'cuts/c12', 1, 36),
    (22.000, 24.500, 'cuts/c13', 1, 60),
    (24.500, 25.500, 'cuts/c14', 1, 24),
    (25.500, 28.500, 'cuts/c152', 1, 57),        # burst + boom freeze (26.0)
    (28.500, 31.000, 'cuts/c162', 1, 61),        # skid to a stop (31.0)
    (31.000, 32.800, 'cuts/c17', 1, 45),
    (32.800, 34.300, 'cuts_slow/c18', 1, 38),
    (34.300, 35.800, 'cuts_slow/c19', 1, 31),
    (35.800, 37.600, 'cuts/c20', 31, 72),        # silence under the overpass
    (37.600, 40.000, 'cuts/c22', 1, 54),         # stare -> scream -> lunge (hit 40.0)
    (40.000, 48.000, 'v6/missed', 1, 192),       # phone lights up in the dark: missed call
    (48.000, 53.000, 'v6/missed', 192, 192),     # hold on the dim missed-call card under Akash's voicemail
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
