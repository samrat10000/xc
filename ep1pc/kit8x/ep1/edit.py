"""Episode 1 edit: grade + upscale shot frames, titles, synthesized sound design, mux to MP4.
usage: python3 edit.py [out.mp4]   (reads out/shots/sN/f####.png; missing frames -> held/black)"""
import os, sys, glob, subprocess, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SH = os.path.join(HERE, 'out', 'shots')
OUTMP4 = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out', 'ep1.mp4')
FPS, W, H, SR = 24, 1080, 1920, 48000
# (shot, frames)
CUT = [(1, 96), (2, 96), (3, 96), (4, 96), (5, 72), (6, 120), (7, 120), (8, 96), (0, 66)]
START = {}; t = 0
for s, n in CUT: START[s] = t; t += n
TOTAL = t
FD = '/usr/share/fonts/opentype/inter/'
F_MONO = '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Light.ttf'
def font(name, size): return ImageFont.truetype(name, size)

# ------------------------------------------------------------------ titles
# (start, end, text, font, size, y, tracking, fade_in, fade_out)
TITLES = [
    (0, 84, '3:12 AM', F_MONO, 150, 470, 6, 0, 10),
    (14, 84, 'THE NIGHT THE CITY STOPPED', FD + 'InterDisplay-Light.otf', 40, 650, 10, 8, 10),
    (START[5] + 4, START[5] + 30, 'NOT EVERYONE RAN.', FD + 'InterDisplay-Light.otf', 46, 520, 12, 6, 6),
    (START[6] + 6, START[6] + 70, 'NIGHT TERROR', FD + 'InterDisplay-Black.otf', 132, 470, 14, 4, 12),
    (START[6] + 14, START[6] + 70, 'D E A D   R O A D S', FD + 'InterDisplay-Light.otf', 52, 640, 8, 6, 12),
    (START[0] + 4, START[0] + 66, 'EPISODE 2', FD + 'InterDisplay-Black.otf', 96, 760, 12, 6, 0),
    (START[0] + 14, START[0] + 66, 'FOLLOW SO YOU DON\'T MISS IT', FD + 'InterDisplay-Light.otf', 38, 900, 8, 6, 0),
]

def draw_tracked(img, text, fpath, size, y, track, alpha):
    if alpha <= 0: return
    f = font(fpath, size)
    widths = [f.getbbox(ch)[2] - f.getbbox(ch)[0] if ch != ' ' else size * .3 for ch in text]
    tw = sum(widths) + track * (len(text) - 1)
    x = (W - 230 * .5 - tw) / 2 + 0     # keep right rail mostly clear
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    cx = x
    for ch, w in zip(text, widths):
        ds.text((cx, y + 4), ch, font=f, fill=(0, 0, 0, int(200 * alpha)))
        d.text((cx, y), ch, font=f, fill=(242, 236, 224, int(255 * alpha)))
        cx += w + track
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    img.alpha_composite(sh); img.alpha_composite(lay)

# ------------------------------------------------------------------ grade
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = 1 - .38 * (((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2)
VIG = np.clip(VIG, .45, 1)[..., None]

def grade(a):
    a = a.astype(np.float32) / 255
    a = a * VIG
    # gentle teal shadows / warm highlights
    lum = a.mean(2, keepdims=True)
    a = a + (1 - lum) * np.array([-.012, .004, .018]) * 1.0 + lum * np.array([.015, .004, -.012])
    a = np.clip(a, 0, 1) ** 1.04
    return (a * 255 + .5).astype(np.uint8)

def shot_frame(s, i):
    p = os.path.join(SH, f's{s}', f'f{i + 1:04d}.png')
    if not os.path.exists(p):
        fs = sorted(glob.glob(os.path.join(SH, f's{s}', 'f*.png')))
        if not fs: return None
        # nearest available frame (previews)
        nums = [int(os.path.basename(f)[1:5]) for f in fs]
        p = fs[int(np.argmin([abs(n - (i + 1)) for n in nums]))]
    return Image.open(p).convert('RGB').resize((W, H), Image.LANCZOS)

# ------------------------------------------------------------------ audio
N = int(TOTAL / FPS * SR) + SR
rng = np.random.default_rng(7)
def sec(fr): return fr / FPS
def idx(t): return int(t * SR)
def noise(n): return rng.standard_normal(n).astype(np.float32)

def onepole_lp(x, fc):
    a = math.exp(-2 * math.pi * fc / SR); y = np.empty_like(x); z = 0.
    for i in range(len(x)): z = (1 - a) * x[i] + a * z; y[i] = z
    return y

def fft_filter(x, lo=None, hi=None, slope=4):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); g = np.ones_like(f)
    if hi: g *= 1 / (1 + (f / hi) ** slope)
    if lo: g *= 1 / (1 + (lo / np.maximum(f, 1)) ** slope)
    return np.fft.irfft(X * g, len(x)).astype(np.float32)

def bandpass(x, fc, q=6): return fft_filter(x, lo=fc / (1 + 1 / q), hi=fc * (1 + 1 / q), slope=6)

def env_adsr(n, a=.01, r=.3, curve=3):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-curve * np.maximum(0, t - a) / max(r, 1e-3))
    return e.astype(np.float32)

L_ = np.zeros(N, np.float32); R_ = np.zeros(N, np.float32)
def put(sig, t, gain=1., pan=0.):
    i = idx(t); j = min(N, i + len(sig)); sig = sig[:j - i] * gain
    L_[i:j] += sig * math.cos((pan + 1) * math.pi / 4) * 1.41; R_[i:j] += sig * math.sin((pan + 1) * math.pi / 4) * 1.41

def saw(f, n, ph=0.):
    if np.isscalar(f): f = np.full(n, f, np.float32)
    p = (np.cumsum(f) / SR + ph) % 1.
    return (2 * p - 1).astype(np.float32)

def sine(f, n):
    if np.isscalar(f): f = np.full(n, f, np.float32)
    return np.sin(2 * np.pi * np.cumsum(f) / SR).astype(np.float32)

def reverb(x, dur=2.4, mix=.35):
    n = int(dur * SR); ir = noise(n) * np.exp(-np.linspace(0, 7, n)).astype(np.float32); ir = fft_filter(ir, hi=5000)
    ir /= np.sqrt((ir ** 2).sum()) + 1e-9
    m = len(x) + n; X = np.fft.rfft(x, m) * np.fft.rfft(ir, m); wet = np.fft.irfft(X, m)[:len(x)].astype(np.float32)
    return x * (1 - mix) + wet * mix * 3

T = lambda s, f=0: sec(START[s] + f)

# rain bed everywhere (muffled in the garage)
rain = fft_filter(noise(N), lo=400, hi=9000) * .05 + fft_filter(noise(N), lo=2500, hi=14000) * .03
drip = np.zeros(N, np.float32)
for k in range(int(N / SR * 30)):
    i = rng.integers(0, N - 2000); d = bandpass(noise(1500), rng.uniform(1500, 5000), 8) * env_adsr(1500, .001, .02)
    drip[i:i + 1500] += d * rng.uniform(.05, .2)
rain = rain + drip
g = np.ones(N, np.float32)
a, b = idx(T(5)), idx(T(6))
g[a:b] = .18
for i0, i1, g0, g1 in ((a - 2400, a, 1, .18), (b, b + 4800, .18, 1)): g[i0:i1] = np.linspace(g0, g1, i1 - i0)
put(rain * g, 0, 1.0, -.15); put(fft_filter(noise(N), lo=400, hi=9000) * .05 * g, 0, 1.0, .15)

# sub drone + slow swell
n = idx(T(5)); dr = (saw(41.2, n) * .5 + saw(41.5, n) * .5); dr = fft_filter(dr, hi=180) * np.linspace(.2, 1, n) ** 1.5
put(dr, 0, .45)

# 3:12 AM tick (clock) on hook
for k in range(4): put(bandpass(noise(800), 3200, 10) * env_adsr(800, .001, .01), .15 + k * 1.0, .35)

# crawler: heartbeat + flesh drag scrapes
for k in range(5):
    tt = T(2) + .3 + k * .78
    hb = sine(48, 6000) * env_adsr(6000, .004, .09, 4); put(hb, tt, .9); put(hb * .7, tt + .2, .7)
for k in range(4):
    nn = int(.6 * SR); sc_ = bandpass(noise(nn), 900, 2) * (np.sin(np.linspace(0, np.pi, nn)) ** 2) * (1 + .6 * np.sin(np.linspace(0, 60, nn)))
    put(sc_, T(2) + .6 + k * .9, .35, -.3)
gr = fft_filter(saw(70 + 8 * np.sin(np.linspace(0, 9, idx(1.8))), idx(1.8)) + noise(idx(1.8)) * .5, lo=150, hi=900) * env_adsr(idx(1.8), .3, .8, 2)
put(gr, T(2, 46), .28, -.2)

# screamer: thunder + scream
for fh, gg in ((22, 1), (30, .7), (70, .9)):
    cr = fft_filter(noise(idx(.25)), lo=800) * env_adsr(idx(.25), .001, .05, 6)
    rb = fft_filter(noise(idx(3.5)), hi=180) * env_adsr(idx(3.5), .06, 1.2, 2.5)
    put(cr, T(3, fh), .8 * gg); put(rb, T(3, fh), 1.6 * gg)
ns = idx(2.6); tt = np.arange(ns) / SR
f0 = 620 + 380 * np.minimum(1, tt / .35) + 40 * np.sin(2 * np.pi * 7 * tt) + 30 * noise(ns) * .3
src = saw(f0, ns) + saw(f0 * 1.007, ns) * .7 + noise(ns) * .6
vox = bandpass(src, 950, 3) * 1.0 + bandpass(src, 1500, 4) * .7 + bandpass(src, 3100, 5) * .5
vox *= np.minimum(1, tt / .08) * np.exp(-np.maximum(0, tt - 1.9) * 4)
vox = np.tanh(vox * 3) * .5
put(reverb(vox, 2.5, .45), T(3, 36), .3, .1)

# horde: many moans
for k in range(14):
    nn = idx(rng.uniform(1.6, 3.2)); f = rng.uniform(85, 150) * (1 - .15 * np.linspace(0, 1, nn))
    m = saw(f, nn) + noise(nn) * .3; m = bandpass(m, rng.uniform(450, 700), 2.5) + bandpass(m, rng.uniform(900, 1200), 4) * .5
    m *= np.sin(np.linspace(0, np.pi, nn)) ** 1.5
    put(reverb(m, 1.8, .4), T(4) + rng.uniform(0, 3.0), .22, rng.uniform(-.8, .8))

# garage: fluorescent hum, ignition, braam
nn = idx(sec(72)); hum = (sine(120, nn) * .3 + saw(120, nn) * .05) * .6; put(fft_filter(hum, hi=2000), T(5), .12)
put(fft_filter(noise(idx(.15)), lo=200, hi=2500) * env_adsr(idx(.15), .001, .04), T(5, 26), .9)   # clunk
nb = idx(3.5); tb = np.arange(nb) / SR
br = sum(saw(f, nb) for f in (55, 55.4, 82.5, 110, 110.6)) / 4
br = fft_filter(br, hi=900) * np.minimum(1, tb / .02) * np.exp(-tb * .9)
put(reverb(np.tanh(br * 2) * .7, 2.8, .35), T(5, 27), .9)

# engine: start + idle in garage, roar through chase, brake at skid
def engine(rpm, n):
    f = rpm / 60 * 3                                     # V6: 3 firing pulses per rev
    base = saw(f, n) * .6 + saw(f * .5, n) * .4 + sine(f * 2, n) * .2
    rough = fft_filter(noise(n), hi=600) * .6
    return np.tanh(fft_filter(base + rough * (.5 + .5 * base), hi=1800) * 2.5) * .5
ne = idx(sec(72 - 34)); rpm = np.concatenate([np.linspace(300, 2800, idx(.6)), np.linspace(2800, 1100, ne - idx(.6))])
put(engine(rpm, ne), T(5, 34), .55)
nc = idx(sec(120)); rpm = 3500 + 2600 * np.linspace(0, 1, nc) ** .7 + 300 * np.sin(np.linspace(0, 11, nc))
put(engine(rpm, nc), T(6), .7)
for k in range(9):                                       # passing-infected whooshes / hits
    nw = idx(.5); w = fft_filter(noise(nw), lo=300, hi=3000) * np.sin(np.linspace(0, np.pi, nw)) ** 3
    put(w, T(6) + .3 + k * .52, .5, rng.choice([-.7, .7]))
    if k in (2, 5, 7): put(fft_filter(noise(idx(.2)), hi=300) * env_adsr(idx(.2), .001, .06), T(6) + .5 + k * .52, 1.0)
for k in range(10):                                      # taiko pulse
    put(sine(52, idx(.7)) * env_adsr(idx(.7), .002, .18, 3), T(6) + k * .5, .9)
ns = idx(1.3); sk = bandpass(noise(ns), 2400, 3) * (1 + .5 * np.sin(np.linspace(0, 90, ns))) * env_adsr(ns, .03, .7, 1.2)
put(sk, T(7, 2), .95, .3)
ne = idx(sec(120 - 26)); put(engine(np.linspace(1500, 900, ne), ne), T(7, 26), .3, .3)
# brute: heavy steps + growl
for k in range(6):
    put(fft_filter(noise(idx(.4)), hi=140) * env_adsr(idx(.4), .002, .12, 3), T(7, 34) + k * .62, 1.5)
ng = idx(2.4); gr = fft_filter(saw(48 + 6 * np.sin(np.linspace(0, 15, ng)), ng) * (1 + noise(ng) * .5), hi=500)
put(np.tanh(gr * 2) * env_adsr(ng, .4, 1.2, 1.5), T(7, 70), .55)

# stalker: rising riser, clicks, stinger + end hit
nr = idx(sec(96)); tr = np.arange(nr) / SR
u = (tr / tr[-1]); nz = noise(nr); ris = (fft_filter(nz, lo=300, hi=900) * (1 - u) + fft_filter(nz, lo=1500, hi=8000) * u) * u ** 2 * .5
ris += saw(110 * 2 ** (tr / tr[-1] * 1.5), nr) * .08 * (tr / tr[-1]) ** 2
put(ris, T(8), .7)
for k in range(6): put(bandpass(noise(900), 1800, 6) * env_adsr(900, .001, .01), T(8) + .8 + k * .21 + (k > 2) * .5, .4)
for fh in (64, 70):
    put(fft_filter(noise(idx(3.0)), hi=180) * env_adsr(idx(3.0), .05, 1.0, 2.5), T(8, fh), 1.2)
hit = np.tanh((sine(38, idx(4)) * 1.2 + fft_filter(noise(idx(4)), hi=400) * .5) * env_adsr(idx(4), .002, 1.6, 2) * 2)
put(reverb(hit, 3.5, .4), T(0), .7)
put(reverb(hit, 3.0, .45), 0.0, .55)

# master: duck rain when big sounds, soft-clip, normalize
mix = np.stack([L_, R_], 1)
mix = np.tanh(mix * 1.1) * .9
mix /= max(1e-6, np.abs(mix).max()) / .89
mix[:idx(.05)] *= np.linspace(0, 1, idx(.05))[:, None]
wav = os.path.join(HERE, 'out', 'ep1.wav')
import wave
with wave.open(wav, 'wb') as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((mix[:idx(TOTAL / FPS)] * 32767).astype(np.int16).tobytes())
print('audio ok')
if os.environ.get('AUDIO_ONLY'): sys.exit(0)

# ------------------------------------------------------------------ video
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-i', wav, '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k',
                       '-movflags', '+faststart', '-shortest', OUTMP4], stdin=subprocess.PIPE)
LIMIT = int(os.environ.get('LIMIT', TOTAL))
gf = 0
for s, n in CUT:
    for i in range(n):
        if gf >= LIMIT: break
        if s == 0:
            img = Image.new('RGB', (W, H), (4, 4, 6))
        else:
            img = shot_frame(s, i) or Image.new('RGB', (W, H))
            img = Image.fromarray(grade(np.asarray(img)))
            if i < 3 and s != 1: img = Image.blend(img, Image.new('RGB', (W, H), (0, 0, 0)), [.5, .25, 0][i])   # tiny dip on cuts
            if s == 8 and i > n - 8: img = Image.blend(img, Image.new('RGB', (W, H), (0, 0, 0)), (i - (n - 8)) / 8)
        img = img.convert('RGBA')
        for (a, b, txt, fp, sz, y, tr, fi, fo) in TITLES:
            if a <= gf < b:
                al = 1.
                if fi: al = min(al, (gf - a) / fi)
                if fo: al = min(al, (b - gf) / fo)
                draw_tracked(img, txt, fp, sz, y, tr, max(0, min(1, al)))
        ff.stdin.write(img.convert('RGB').tobytes()); gf += 1
ff.stdin.close(); ff.wait()
print('video ok', OUTMP4, gf, 'frames')
