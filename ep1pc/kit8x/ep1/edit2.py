"""Episode 1 v2 edit: 21 cuts + end card. Grade, lens FX (halation, anamorphic streaks, chromatic edges),
upscale, titles, synthesized sound design, mux. usage: python3 edit2.py [out.mp4]; LIMIT=frames for previews."""
import os, sys, glob, subprocess, math, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUTMP4 = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'out', 'ep1_v2.mp4')
FPS, W, H, SR = 24, 1080, 1920, 48000
SH = os.path.join(HERE, 'out')
# (key, folder, first source frame, length)
CUT = [('c1', 'shots/s1', 1, 60), ('c2', 'cuts/c02', 1, 36), ('c3', 'cuts/c03', 1, 48), ('c4', 'cuts/c04', 1, 24),
       ('c5', 'cuts/c05', 1, 36), ('c6', 'cuts/c06', 1, 36), ('c7', 'cuts/c07', 1, 24), ('c8', 'cuts/c08', 1, 60),
       ('c9', 'cuts/c09', 1, 36), ('c10', 'cuts/c10', 1, 36), ('c11', 'cuts/c11', 1, 36), ('c12', 'cuts/c12', 1, 36),
       ('c13', 'cuts/c13', 1, 60), ('c14', 'cuts/c14', 1, 24), ('c15', 'cuts/c15', 1, 36), ('c16', 'cuts/c16', 1, 36),
       ('c17', 'cuts/c17', 1, 60), ('c18', 'cuts/c18', 1, 24), ('c19', 'cuts/c19', 1, 24), ('c20', 'cuts/c20', 1, 72),
       ('c21', 'cuts/c21', 1, 36), ('end', None, 1, 66)]
START = {}; t = 0
for k, _, _, n in CUT: START[k] = t; t += n
TOTAL = t
FD = '/usr/share/fonts/opentype/inter/'
F_MONO = '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Light.ttf'
def font(name, size): return ImageFont.truetype(name, size)
S = START
TITLES = [
    (0, 56, '3:12 AM', F_MONO, 150, 470, 6, 0, 10),
    (12, 56, 'THE NIGHT THE CITY STOPPED', FD + 'InterDisplay-Light.otf', 40, 650, 10, 8, 10),
    (S['c10'] + 14, S['c10'] + 36, 'NOT EVERYONE RAN.', FD + 'InterDisplay-Light.otf', 46, 520, 12, 4, 6),
    (S['c12'] + 2, S['c13'] + 30, 'NIGHT TERROR', FD + 'InterDisplay-Black.otf', 132, 470, 14, 3, 10),
    (S['c12'] + 8, S['c13'] + 30, 'D E A D   R O A D S', FD + 'InterDisplay-Light.otf', 52, 640, 8, 5, 10),
    (S['end'] + 4, S['end'] + 66, 'EPISODE 2', FD + 'InterDisplay-Black.otf', 96, 760, 12, 6, 0),
    (S['end'] + 14, S['end'] + 66, "FOLLOW SO YOU DON'T MISS IT", FD + 'InterDisplay-Light.otf', 38, 900, 8, 6, 0),
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


# ------------------------------------------------------------------ grade + lens
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = np.clip(1 - .38 * (((xx - W / 2) / (W * .62)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2), .45, 1)[..., None]

def lens(img):
    a = np.asarray(img).astype(np.float32) / 255
    lum = a.max(2)
    # halation: blurred highlights bleed warm-red into the surround
    hi = Image.fromarray((np.clip((lum - .86) / .14, 0, 1) * 255).astype(np.uint8))
    hb = np.asarray(hi.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    a = a + hb[..., None] * np.array([.30, .10, .05]) * .35
    # anamorphic streak: very bright points smear horizontally in blue
    vh = Image.fromarray((np.clip((lum - .96) / .04, 0, 1) * 255).astype(np.uint8))
    st = np.asarray(vh.resize((W // 24, H // 2), Image.BOX).resize((W, H), Image.BILINEAR)).astype(np.float32) / 255
    a = a + st[..., None] * np.array([.10, .22, .45]) * .5
    a = a * VIG
    lm = a.mean(2, keepdims=True)
    a = a + (1 - lm) * np.array([-.012, .004, .018]) + lm * np.array([.015, .004, -.012])
    a = np.clip(a, 0, 1) ** 1.04
    im = Image.fromarray((a * 255 + .5).astype(np.uint8))
    # chromatic edges: red slightly larger, blue slightly smaller than green
    r, g, b = im.split()
    def sc(ch, k):
        w2, h2 = int(W * k), int(H * k); c = ch.resize((w2, h2), Image.BILINEAR)
        x0, y0 = (w2 - W) // 2, (h2 - H) // 2
        return c.crop((x0, y0, x0 + W, y0 + H)) if k > 1 else ch
    r = sc(r, 1.0025)
    b2 = b.resize((int(W * .9975), int(H * .9975)), Image.BILINEAR); bb = Image.new('L', (W, H)); bb.paste(b2, ((W - b2.width) // 2, (H - b2.height) // 2)); b = ImageChops.lighter(bb, ImageChops.multiply(b, Image.new('L', (W, H), 0))) if False else bb
    return Image.merge('RGB', (r, g, b))

def src_frame(folder, i):
    d = os.path.join(SH, folder); p = os.path.join(d, f'f{i:04d}.png')
    if not os.path.exists(p):
        fs = sorted(glob.glob(os.path.join(d, 'f*.png')))
        if not fs: return None
        nums = [int(os.path.basename(f)[1:5]) for f in fs]; p = fs[int(np.argmin([abs(n - i) for n in nums]))]
    return Image.open(p).convert('RGB').resize((W, H), Image.LANCZOS)

# ------------------------------------------------------------------ audio
N = int(TOTAL / FPS * SR) + SR
rng = np.random.default_rng(7)
def sec(fr): return fr / FPS
def idx(t): return int(t * SR)
def noise(n): return rng.standard_normal(n).astype(np.float32)
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


T = lambda k, f=0: sec(START[k] + f)

def thunder(t, g=1.):
    put(fft_filter(noise(idx(.25)), lo=800) * env_adsr(idx(.25), .001, .05, 6), t, .8 * g)
    put(fft_filter(noise(idx(3.5)), hi=180) * env_adsr(idx(3.5), .06, 1.2, 2.5), t, 1.6 * g)
def thump(t, g=1., f=48):
    put(sine(f, 6000) * env_adsr(6000, .004, .09, 4), t, g)
def splash(t, g=.5, pan=0.):
    nn = idx(.35); put(fft_filter(noise(nn), lo=500, hi=7000) * env_adsr(nn, .005, .12, 3), t, g, pan)
def whoosh(t, dur=.45, g=.5, pan=0.):
    nw = idx(dur); put(fft_filter(noise(nw), lo=300, hi=3000) * np.sin(np.linspace(0, np.pi, nw)) ** 3, t, g, pan)
def growl(t, dur=1.8, f=70, g=.3, pan=0.):
    n_ = idx(dur); x = fft_filter(saw(f + 8 * np.sin(np.linspace(0, 9, n_)), n_) + noise(n_) * .5, lo=150, hi=900) * env_adsr(n_, .3, .8, 2)
    put(x, t, g, pan)
def moan(t, g=.22, pan=0.):
    nn = idx(rng.uniform(1.6, 3.0)); f = rng.uniform(85, 150) * (1 - .15 * np.linspace(0, 1, nn))
    m = saw(f, nn) + noise(nn) * .3; m = bandpass(m, rng.uniform(450, 700), 2.5) + bandpass(m, rng.uniform(900, 1200), 4) * .5
    put(reverb(m * np.sin(np.linspace(0, np.pi, nn)) ** 1.5, 1.8, .4), t, g, pan)
def engine(rpm, n):
    f = rpm / 60 * 3
    base = saw(f, n) * .6 + saw(f * .5, n) * .4 + sine(f * 2, n) * .2
    rough = fft_filter(noise(n), hi=600) * .6
    return np.tanh(fft_filter(base + rough * (.5 + .5 * base), hi=1800) * 2.5) * .5
def braam(t, g=.9):
    nb = idx(3.5); tb = np.arange(nb) / SR
    br = sum(saw(f, nb) for f in (55, 55.4, 82.5, 110, 110.6)) / 4
    br = fft_filter(br, hi=900) * np.minimum(1, tb / .02) * np.exp(-tb * .9)
    put(reverb(np.tanh(br * 2) * .7, 2.8, .35), t, g)

# rain bed, muffled inside the garage
rain = fft_filter(noise(N), lo=400, hi=9000) * .05 + fft_filter(noise(N), lo=2500, hi=14000) * .03
for k in range(int(N / SR * 30)):
    i = rng.integers(0, N - 2000); rain[i:i + 1500] += bandpass(noise(1500), rng.uniform(1500, 5000), 8) * env_adsr(1500, .001, .02) * rng.uniform(.05, .2)
g = np.ones(N, np.float32); a, b = idx(T('c10')), idx(T('c12'))
g[a:b] = .18; g[a - 1200:a] = np.linspace(1, .18, 1200); g[b:b + 2400] = np.linspace(.18, 1, 2400)
put(rain * g, 0, 1.0, -.15); put(fft_filter(noise(N), lo=400, hi=9000) * .05 * g, 0, 1.0, .15)
n_ = idx(T('c10')); dr = fft_filter(saw(41.2, n_) * .5 + saw(41.5, n_) * .5, hi=180) * np.linspace(.3, 1, n_) ** 1.5; put(dr, 0, .45)
hit = np.tanh((sine(38, idx(4)) * 1.2 + fft_filter(noise(idx(4)), hi=400) * .5) * env_adsr(idx(4), .002, 1.6, 2) * 2)
put(reverb(hit, 3.0, .45), 0.0, .55)
for k in range(3): put(bandpass(noise(800), 3200, 10) * env_adsr(800, .001, .01), .15 + k * .8, .35)
# crawler
splash(T('c2', 20), .9); thump(T('c2', 20), .6, 60)
for k in range(5): thump(T('c2') + .2 + k * .7, .8); thump(T('c2') + .4 + k * .7, .55)
for k in range(3):
    nn = idx(.6); put(bandpass(noise(nn), 900, 2) * np.sin(np.linspace(0, np.pi, nn)) ** 2, T('c3') + .2 + k * .65, .35, -.3)
growl(T('c4'), 1.2, 70, .35)
# screamer
thunder(T('c5', 16)); thunder(T('c6', 10), .7); thunder(T('c6', 26), .8)
ns = idx(2.2); tt = np.arange(ns) / SR
f0 = 620 + 380 * np.minimum(1, tt / .25) + 40 * np.sin(2 * np.pi * 7 * tt)
srcv = saw(f0, ns) + saw(f0 * 1.007, ns) * .7 + noise(ns) * .6
vox = bandpass(srcv, 950, 3) + bandpass(srcv, 1500, 4) * .7 + bandpass(srcv, 3100, 5) * .5
vox = np.tanh(vox * np.minimum(1, tt / .05) * np.exp(-np.maximum(0, tt - 1.6) * 4) * 3) * .5
put(reverb(vox, 2.5, .45), T('c6', 8), .32, .1)
# horde
whoosh(T('c7'), .3, .7)
for k in range(16): moan(T('c7') + rng.uniform(0, 4.5), .2, rng.uniform(-.8, .8))
for k in range(10): splash(T('c9') + .1 + k * .14 + rng.uniform(0, .05), .25, rng.uniform(-.6, .6))
# garage
nn = idx(sec(72)); put(fft_filter((sine(120, nn) * .3 + saw(120, nn) * .05) * .6, hi=2000), T('c10'), .12)
put(fft_filter(noise(idx(.15)), lo=200, hi=2500) * env_adsr(idx(.15), .001, .04), T('c10', 10), .9); braam(T('c10', 11))
ne = idx(sec(36 + 25)); rpm = np.concatenate([np.linspace(300, 2800, idx(.6)), np.linspace(2800, 1100, ne - idx(.6))])
put(engine(rpm, ne), T('c10', 11), .55)
# chase
nc = idx(T('c16') - T('c12')); rpm = 3500 + 2600 * np.linspace(0, 1, nc) ** .7 + 300 * np.sin(np.linspace(0, 11, nc))
put(engine(rpm, nc), T('c12'), .7)
splash(T('c12', 8), 1.0, .4); splash(T('c12', 20), .7, .4)
for k in range(8): whoosh(T('c13') + .2 + k * .3, .4, .45, rng.choice([-.7, .7]))
growl(T('c14'), .9, 110, .4, -.6); whoosh(T('c15', 4), .8, .5)
for k in range(int((T('c16') - T('c12')) / .5)): put(sine(52, idx(.7)) * env_adsr(idx(.7), .002, .18, 3), T('c12') + k * .5, .9)
ns = idx(1.0); put(bandpass(noise(ns), 2400, 3) * (1 + .5 * np.sin(np.linspace(0, 90, ns))) * env_adsr(ns, .03, .55, 1.2), T('c16'), .95, .3)
put(fft_filter(noise(idx(.3)), hi=300) * env_adsr(idx(.3), .001, .08), T('c16', 20), 1.0)
ne = idx(T('c20') - T('c16', 20)); put(engine(np.linspace(1500, 900, ne), ne), T('c16', 20), .3, .3)
# brute
for f in (20, 45): put(fft_filter(noise(idx(.4)), hi=140) * env_adsr(idx(.4), .002, .12, 3), T('c17', f), 1.6)
growl(T('c17', 30), 1.5, 50, .4)
ng = idx(1.6); gr = fft_filter(saw(46 + 10 * np.sin(np.linspace(0, 15, ng)), ng) * (1 + noise(ng) * .6), hi=700)
put(reverb(np.tanh(gr * 3) * env_adsr(ng, .05, 1.0, 1.5), 2.0, .35), T('c18', 6), .8)
ne = idx(1.0); put(engine(np.concatenate([np.linspace(1100, 5200, idx(.35)), np.linspace(5200, 2500, ne - idx(.35))]), ne), T('c19', 7), .8)
# stalker
nr = idx(T('end') - T('c20')); tr = np.arange(nr) / SR; u = tr / tr[-1]; nz = noise(nr)
ris = (fft_filter(nz, lo=300, hi=900) * (1 - u) + fft_filter(nz, lo=1500, hi=8000) * u) * u ** 2 * .5 + saw(110 * 2 ** (u * 1.5), nr) * .08 * u ** 2
put(ris, T('c20'), .7)
thunder(T('c20', 40)); thunder(T('c20', 46), .7); thunder(T('c21', 12), .8)
for k in range(6): put(bandpass(noise(900), 1800, 6) * env_adsr(900, .001, .01), T('c21') + .2 + k * .17, .4)
put(reverb(hit, 3.5, .4), T('end'), .7)

mix = np.stack([L_, R_], 1); mix = np.tanh(mix * 1.1) * .9; mix /= max(1e-6, np.abs(mix).max()) / .89
mix[:idx(.05)] *= np.linspace(0, 1, idx(.05))[:, None]
wav = os.path.join(HERE, 'out', 'ep1_v2.wav')
with wave.open(wav, 'wb') as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR); wf.writeframes((mix[:idx(TOTAL / FPS)] * 32767).astype(np.int16).tobytes())
print('audio ok', TOTAL, 'frames', TOTAL / FPS, 's')
if os.environ.get('AUDIO_ONLY'): sys.exit(0)

# ------------------------------------------------------------------ video
ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                       '-i', wav, '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '256k',
                       '-movflags', '+faststart', '-shortest', OUTMP4], stdin=subprocess.PIPE)
LIMIT = int(os.environ.get('LIMIT', TOTAL)); ONLY = os.environ.get('ONLY')
gf = 0
for key_, folder, s0, n in CUT:
    for i in range(n):
        if gf >= LIMIT: break
        if ONLY and key_ not in ONLY.split(','): gf += 1; continue
        if folder is None:
            img = Image.new('RGB', (W, H), (4, 4, 6))
        else:
            img = src_frame(folder, s0 + i) or Image.new('RGB', (W, H))
            img = lens(img)
            if i < 2 and key_ not in ('c1',): img = Image.blend(img, Image.new('RGB', (W, H), (0, 0, 0)), [.35, 0][i])
            if key_ == 'c21' and i > n - 8: img = Image.blend(img, Image.new('RGB', (W, H), (0, 0, 0)), (i - (n - 8)) / 8)
        img = img.convert('RGBA')
        for (a0, b0, txt, fp, sz, y, tr_, fi, fo) in TITLES:
            if a0 <= gf < b0:
                al = 1.
                if fi: al = min(al, (gf - a0) / fi)
                if fo: al = min(al, (b0 - gf) / fo)
                draw_tracked(img, txt, fp, sz, y, tr_, max(0, min(1, al)))
        ff.stdin.write(img.convert('RGB').tobytes()); gf += 1
ff.stdin.close(); ff.wait()
print('video ok', OUTMP4, gf, 'frames')
