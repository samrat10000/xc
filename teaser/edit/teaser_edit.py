"""Night Terror teaser: grade + camcorder treatment + assembly. No text on screen.
python3 teaser_edit.py OUT.mp4 AUDIO.wav  (frame roots in ROOTS, first hit wins)
"""
import os, sys, subprocess, numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, os.environ.get('LOOKDIR', ''))
from look import lens          # Ep1 grade: halation, anamorphic streak, vignette, split tone, chroma edges

W, H, FPS = 1080, 1920, 24
ROOTS = [r for r in os.environ.get('ROOTS', '').split(':') if r]
SEQ = [(901, 24), (902, 36), (903, 41), (904, 34), (905, 29), (906, 14), (907, 10), (908, 19), (909, 19), (910, 48),
       ('black', 14), (911, 139), ('black', 18), (912, 4), ('black', 8)]
VHS = {904, 912}
rng = np.random.default_rng(5)

def frame(cut, i):
    for r in ROOTS:
        p = os.path.join(r, f'c{cut}', f'f{i:04d}.png')
        if os.path.exists(p) and os.path.getsize(p) > 0: return Image.open(p).convert('RGB')
    return None

def grain(a, amt):
    n = rng.normal(0, amt, (H // 2, W // 2, 1)).astype(np.float32)
    n = np.asarray(Image.fromarray(((n[..., 0] * 40 + 128).clip(0, 255)).astype(np.uint8)).resize((W, H), Image.BILINEAR)).astype(np.float32)[..., None]
    return a + (n - 128) / 40 * 255 * amt * (0.6 + 0.4 * (1 - a / 255))

def vhs(a, k=1.0, t=0):
    out = a.copy()
    sh = int(3 * k)
    out[:, sh:, 0] = a[:, :-sh, 0]; out[:, :-sh, 2] = a[:, sh:, 2]          # chroma misregistration
    for _ in range(int(4 * k)):                                              # tracking wobble bands
        y = rng.integers(0, H - 40); h = rng.integers(4, 30); s = rng.integers(-int(10 * k), int(10 * k) + 1)
        out[y:y + h] = np.roll(out[y:y + h], s, 1)
    if rng.random() < .3 * k:                                                # head-switch noise at the bottom
        out[H - 24:] = out[H - 24:] * .6 + rng.integers(40, 200, (24, W, 1))
    im = Image.fromarray(out.clip(0, 255).astype(np.uint8)).resize((W // 2, H), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    b = np.asarray(im).astype(np.float32)
    b[::2] *= .94                                                            # faint scanlines
    lum = b.mean(2, keepdims=True); b = lum + (b - lum) * .82                # tape desaturation
    return b

def build(out_mp4, audio):
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           *(['-i', audio] if audio else []), '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                           *(['-c:a', 'aac', '-b:a', '256k', '-shortest'] if audio else []), '-movflags', '+faststart', out_mp4], stdin=subprocess.PIPE)
    missing = []; last = None
    for item in SEQ:
        cut, n = item
        for i in range(1, n + 1):
            if cut == 'black':
                a = np.zeros((H, W, 3), np.float32)
            else:
                im = frame(cut, i)
                if im is None: missing.append((cut, i)); im = last or Image.new('RGB', (W, H))
                last = im
                im = lens(im.resize((W, H), Image.LANCZOS))
                a = np.asarray(im).astype(np.float32)
                a = grain(a, .022 if cut not in VHS else .035)
                if cut in VHS: a = vhs(a, 1.0 if cut == 904 else 1.8)
                if cut == 911 and i > n - 8:                                   # tape tears to black at the end of the take
                    k = (i - (n - 8)) / 8; a = vhs(a, 1 + 4 * k) * (1 - k * .9)
                if cut == 911 and i == n: a *= 0
            ff.stdin.write(a.clip(0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()
    print('frames', sum(n for _, n in SEQ), 'missing', len(missing), missing[:10])

if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
