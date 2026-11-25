"""5 O'CLOCK Ep1 score: real recorded samples only (VSCO-2 CE: Ivy Audio pipe organ, strings, marimba, glock,
timpani, gong). Sampler = pitch-shift by resampling + envelopes. Original composition in A minor -> F major."""
import numpy as np, subprocess, glob, re, os, functools, json, sys
SR = 48000
V = '/root/snd/vsco'


@functools.lru_cache(None)
def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def hps(x):
    m = x.mean(1)
    st = int(.25 * SR)
    seg = m[st:st + int(1.2 * SR)]
    if len(seg) < 4096:
        seg = m[:int(1.0 * SR)]
    N = 8 * len(seg)
    sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), N)); fr = np.fft.rfftfreq(N, 1 / SR)
    h = sp.copy()
    for k in (2, 3, 4):
        d = sp[::k]; h[:len(d)] *= d
    msk = (fr > 25) & (fr < 2500)
    f = fr[np.argmax(h * msk)]
    return 69 + 12 * np.log2(f / 440)


def bank(files, name_to_midi):
    out = []
    for f in files:
        n = name_to_midi(os.path.basename(f))
        if n is None:
            continue
        out.append((n, f))
    return sorted(out)


def organ_bank(kind, loud):
    if loud:
        fs = glob.glob(f'{V}/Keys/Organ/Loud/Rode_{"Man3Open" if kind == "man" else "Pedal"}_*.wav')
        return bank(fs, lambda b: 35 + int(re.findall(r'_(\d+)\.wav', b)[0]))
    fs = glob.glob(f'{V}/Keys/Organ/Quiet/NT5_{"Man3Quiet" if kind == "man" else "PedalQuiet"}_*_rr1.wav')
    off = 86 if kind == 'man' else 28
    return bank(fs, lambda b: int(re.findall(r'_(\d+)_rr1', b)[0]) - off)


def named_bank(pattern):
    fs = glob.glob(pattern)
    def nm(b):
        m = re.search(r'_([A-G])(#|s)?(\d)', b)
        if not m:
            return None
        n = 12 * (int(m.group(3)) + 1) + NOTE[m.group(1)] + (1 if m.group(2) else 0)
        # verify octave by pitch detection
        try:
            d = hps(load(os.path.join(os.path.dirname(pattern), b)))
            k = round((d - n) / 12)
            if abs(d - (n + 12 * k)) < .8 and k != 0:
                n += 12 * k
        except Exception:
            pass
        return n
    return bank(fs, nm)


def pick(bk, midi):
    n, f = min(bk, key=lambda x: (abs(x[0] - midi), x[0] < midi))
    return n, f


def shift(x, semis):
    if abs(semis) < 1e-3:
        return x
    r = 2 ** (semis / 12)
    n = int(len(x) / r)
    idx = np.arange(n) * r
    i0 = idx.astype(int); fr = (idx - i0)[:, None]
    i1 = np.minimum(i0 + 1, len(x) - 1)
    return x[i0] * (1 - fr) + x[i1] * fr


class Mix:
    def __init__(self, dur):
        self.y = np.zeros((int(dur * SR), 2), np.float32)

    def add(self, x, t, g=1.0):
        a = int(t * SR)
        if a >= len(self.y):
            return
        x = x[:len(self.y) - a]
        self.y[a:a + len(x)] += x * g


def note(bk, midi, dur, att=.08, rel=.8, start_off=0.0, detune=0.0):
    n, f = pick(bk, midi)
    x = load(f)
    x = shift(x, midi - n + detune)
    s = int(start_off * SR)
    x = x[s:]
    L = int((dur + rel) * SR)
    if len(x) < L:
        x = np.concatenate([x, np.zeros((L - len(x), 2), np.float32)])
    x = x[:L].copy()
    env = np.ones(L, np.float32)
    na = max(1, int(att * SR)); env[:na] = np.linspace(0, 1, na) ** 1.5
    nd = int(dur * SR); nr = L - nd
    if nr > 0:
        env[nd:] = np.exp(-np.linspace(0, 6, nr))
    return x * env[:, None]


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros_like(x); s = np.zeros(x.shape[1], np.float32)
    # vectorised via scipy if present
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x, axis=0).astype(np.float32)


def bandpass(x, lo, hi, order=4):
    from scipy.signal import butter, sosfilt
    sos = butter(order, [lo, hi], btype='band', fs=SR, output='sos')
    return sosfilt(sos, x, axis=0).astype(np.float32)


def hp(x, fc, order=2):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x, axis=0).astype(np.float32)


def lp(x, fc, order=2):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x, axis=0).astype(np.float32)


def reverb(x, secs=3.5, wet=.3, seed=0, pre=.02):
    """convolution with a decaying-noise IR (a room/hall model applied to the real samples)"""
    from scipy.signal import fftconvolve
    r = np.random.default_rng(seed)
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = r.normal(0, 1, (n, 2)).astype(np.float32) * np.exp(-t * 6.9 / secs)[:, None]
    ir = lp(ir, 6000)
    ir[:int(pre * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum(0, keepdims=True))
    y = np.stack([fftconvolve(x[:, i], ir[:, i])[:len(x)] for i in range(2)], 1)
    return x * (1 - wet) + y * wet * 1.0


def pa_speaker(x):
    """outdoor town loudspeaker: horn band-limit, mild saturation, mountain echoes"""
    y = bandpass(x, 420, 4200)
    y = np.tanh(y * 2.2) / 2.2
    out = y.copy()
    for d, g in ((.42, .32), (.86, .16), (1.5, .08)):
        k = int(d * SR)
        e = np.zeros_like(y); e[k:] = lp(y, 2500)[:-k]
        out += e * g
    return out


def fade(x, a, b):
    n = len(x)
    e = np.ones(n, np.float32)
    na, nb = int(a * SR), int(b * SR)
    if na: e[:na] = np.linspace(0, 1, na)
    if nb: e[-nb:] = np.linspace(1, 0, nb)
    return x * e[:, None]


def automation(n, pts):
    t = np.arange(n) / SR
    tt, vv = zip(*pts)
    return np.interp(t, tt, vv).astype(np.float32)[:, None]


def addv(*xs):
    n = max(len(x) for x in xs)
    y = np.zeros((n, 2), np.float32)
    for x in xs:
        y[:len(x)] += x
    return y
