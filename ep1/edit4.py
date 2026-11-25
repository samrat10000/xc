"""Ep1 v4 (freeze-time shots) picture edit cut to the locked music (v5). Segments are placed on the music clock; speed is derived
so each source range fills its slot (slow-mo < 1 < whip). Frame-blended retiming. usage:
python3 edit3.py audio.wav out.mp4 [END_SECONDS]"""
import os, sys, subprocess, numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from look import lens, src_frame, W, H

FPS = 24
# (start s, end s, folder, first src frame, last src frame)
SEG = [
    (0.000, 2.667, 'shots/s1', 1, 60),
    (2.667, 4.167, 'cuts/c02', 1, 36),
    (4.167, 6.167, 'cuts/c03', 1, 48),
    (6.167, 7.167, 'cuts/c04', 1, 24),
    (7.167, 8.000, 'cuts/c05', 1, 20),
    (8.000, 8.542, 'cuts/c06', 1, 13),       # scream at real speed...
    (8.542, 10.667, 'cuts/c61', 1, 51),      # ...then time FREEZES at its peak: rain hangs, camera arcs around her
    (10.667, 13.333, 'cuts/c08', 1, 60),
    (13.333, 15.833, 'cuts_slow/c09', 1, 57),     # feet in puddles, slow-mo; entered through a whip-blur on the beat
    (15.833, 18.208, 'cuts/c11', 1, 36),     # garage reveal, slow
    (18.208, 19.292, 'cuts/c10', 1, 26),     # headlights ignite exactly on the 18.667 hit (src f11)
    (19.292, 20.792, 'cuts/c12', 1, 36),
    (20.792, 23.917, 'cuts/c13', 1, 60),     # chase tracking, slightly slowed
    (23.917, 24.917, 'cuts/c14', 1, 24),     # runner past the lens
    (24.917, 25.833, 'cuts/c15', 1, 22),     # car bursts out of the fog: real speed...
    (25.833, 27.292, 'cuts/c151', 1, 35),    # ...freeze: car mid-burst, camera sweeps the nose
    (27.292, 28.042, 'cuts/c16', 1, 18),     # skid at real speed...
    (28.042, 29.333, 'cuts/c161', 4, 31),    # ...freeze mid-slide, camera arcs across the front
    (29.333, 29.833, 'cuts/c16', 19, 30),    # time restarts: car slams to a stop on the hit
    (29.833, 31.708, 'cuts/c17', 1, 45),     # Brute over the shoulder
    (31.708, 33.375, 'cuts_slow/c18', 1, 38),     # roar in slow-mo, jaw snap (src f5) on the 32.0 braam
    (33.375, 34.667, 'cuts/c19', 1, 24),     # headlights rev
    (34.667, 37.167, 'cuts/c20', 1, 60),     # Stalker on the overpass
    (37.167, 38.667, 'cuts/c21', 1, 36),     # skull close-up -> cut to black on the lunge hit
    (38.667, 45.5, None, 0, 0),              # black: the theme rings out
]

WHIPS = [(13.333, 1)]          # (time, direction): camera whips sideways, motion-blur smear across the cut
def whip(img, t):
    for tw, dr in WHIPS:
        d = t - tw
        if abs(d) < .13:
            k = 1 - abs(d) / .13; k = k * k * (3 - 2 * k)
            a = np.asarray(img).astype(np.float32)
            sh = int(dr * (-1 if d < 0 else 1) * k * W * .35) * (1 if d < 0 else -1)
            a = np.roll(a, sh, axis=1)
            r = int(6 + 160 * k)                      # horizontal box blur via cumulative sum
            c = np.cumsum(np.pad(a, ((0, 0), (r, r), (0, 0)), mode='edge'), axis=1)
            a = (c[:, 2 * r:] - c[:, :-2 * r]) / (2 * r)
            a = a[:, :W]
            return Image.fromarray(np.clip(a * (1 + .15 * k), 0, 255).astype(np.uint8))
    return img

def frame_at(folder, s):
    if folder is None: return Image.new('RGB', (W, H), (3, 3, 5))
    a = int(np.floor(s)); fr = s - a
    A = src_frame(folder, max(1, a))
    if fr < .08: return A
    B = src_frame(folder, a + 1)
    return Image.blend(A, B, fr) if B is not None else A

from PIL import ImageDraw, ImageFont
_FD = '/tmp/claude-0/-home-user/c4e17d76-c9b0-576e-a5b4-2ffa0e0e7106/scratchpad/ep1/'
def endcard(img, tt):
    a = min(1, max(0, (tt - 2.2) / .8)) * min(1, max(0, (6.2 - tt) / .6))
    if a <= 0: return img
    fp = '/usr/share/fonts/opentype/inter/InterDisplay-Light.otf'
    f = ImageFont.truetype(fp, 40); d = ImageDraw.Draw(img); txt = 'E P I S O D E   2'
    w = d.textlength(txt, font=f); d.text(((W - w) / 2, H * .47), txt, font=f, fill=tuple(int(225 * a) for _ in range(3)))
    return img

if __name__ == '__main__':
    wav, out = sys.argv[1], sys.argv[2]
    END = float(sys.argv[3]) if len(sys.argv) > 3 else SEG[-1][1]
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-i', wav, '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '320k',
                           '-movflags', '+faststart', '-shortest', out], stdin=subprocess.PIPE)
    n = int(round(END * FPS))
    for i in range(n):
        t = (i + .5) / FPS
        seg = [s for s in SEG if s[0] <= t < s[1]] or [SEG[-1]]
        t0, t1, folder, f0, f1 = seg[0]
        u = (t - t0) / (t1 - t0)
        s = f0 + u * (f1 - f0 + 1) - .5
        img = frame_at(folder, min(max(s, f0), f1))
        img = whip(lens(img), t) if folder else img
        if folder is None and os.environ.get('ENDCARD', '1') == '1': img = endcard(img, t - t0)
        if t > END - .6: img = Image.blend(img, Image.new('RGB', (W, H)), (t - (END - .6)) / .6)
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait(); print('ok', out, n)
