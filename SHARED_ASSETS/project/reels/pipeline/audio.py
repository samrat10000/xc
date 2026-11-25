"""Synthesise the whole soundtrack from the mechanism timeline (no samples).
usage: python3 audio.py out.wav"""
import sys, os, wave, math
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import timeline as T

SR = 48000
DUR = T.N / T.FPS
n = int(SR * DUR)
rng = np.random.default_rng(7)
t = np.arange(n) / SR

def env(length, a=0.002, d=0.1):
    x = np.arange(int(length * SR)) / SR
    return np.minimum(1, x / a) * np.exp(-x / d)

def add(buf, sig, at):
    i = int(at * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig)); buf[i:j] += sig[:j - i]

def lp(x, cutoff):
    """one-pole lowpass, cutoff may be array."""
    c = np.broadcast_to(np.asarray(cutoff, float), x.shape)
    a = 1 - np.exp(-2 * np.pi * c / SR)
    y = np.empty_like(x); s = 0.0
    for i in range(len(x)):
        s += a[i] * (x[i] - s); y[i] = s
    return y

# frame -> speed, interpolated per sample
fr = t * T.FPS
spd = np.interp(fr, np.arange(T.N), [T.speed(i) for i in range(T.N)])

# ---------------------------------------------------------------- engine: one bang per power stroke
eng = np.zeros(n); engL = np.zeros(n); engR = np.zeros(n)
crank_s = np.interp(fr, np.arange(T.N + 1), [T.crank(i) for i in range(T.N + 1)])
for c, fire in T.FIRE.items():
    ph = (crank_s - fire) % 720
    idx = np.nonzero(np.diff(ph) < -300)[0] + 1      # wrapped -> fired
    for i in idx:
        s = spd[i]; at = i / SR
        if s > 0.5:
            # real speed: short pulses fuse into a growl
            L = 0.014; x = np.arange(int(L * SR)) / SR
            sig = (np.sin(2 * np.pi * 95 * x) * .6 + rng.standard_normal(len(x)) * .35) * np.exp(-x / .004)
            add(engR if c <= 3 else engL, sig * .55, at)
        else:
            # slow-mo: each bang is a big, pitched-down boom
            L = 1.1; x = np.arange(int(L * SR)) / SR
            f0 = 46 * (1 + 2.5 * np.exp(-x / .03))
            body = np.sin(2 * np.pi * np.cumsum(f0) / SR) * np.exp(-x / .28)
            crack = lp(rng.standard_normal(len(x)), 1800) * np.exp(-x / .05) * 1.4
            rumble = lp(rng.standard_normal(len(x)), 220) * np.exp(-x / .35) * 2.2
            add(engR if c <= 3 else engL, (body * 1.0 + crack + rumble) * .9, at)
            # exhaust puff half a stroke later, intake hiss on the intake stroke (slow-mo only)
            x2 = np.arange(int(.5 * SR)) / SR
            puff = lp(rng.standard_normal(len(x2)), 700) * np.sin(np.pi * np.minimum(1, x2 / .5)) * .35
            add(engR if c <= 3 else engL, puff, at + 180 / (750 / T.SLOW) / T.FPS)
            hiss = rng.standard_normal(len(x2)); hiss = (hiss - lp(hiss, 3000)) * np.sin(np.pi * np.minimum(1, x2 / .5)) * .12
            add(engR if c <= 3 else engL, hiss, at + 360 / (750 / T.SLOW) / T.FPS)
# idle mechanical tick in slow-mo (valvetrain), at every 90 deg of crank
for k in range(int(crank_s[-1] // 90)):
    i = np.searchsorted(crank_s, k * 90.0)
    if i < n and spd[i] < 0.5:
        x = np.arange(int(.03 * SR)) / SR
        add(eng, np.sin(2 * np.pi * 2400 * x) * np.exp(-x / .004) * .06, i / SR)

# ---------------------------------------------------------------- whooshes on speed ramps
def sweep(f0, f1, lo, hi, gain, up):
    a, b = f0 / T.FPS, f1 / T.FPS; m = (t >= a) & (t < b)
    u = (t[m] - a) / (b - a)
    cut = lo + (hi - lo) * (u if up else 1 - u) ** 2
    nz = lp(rng.standard_normal(m.sum()), cut)
    shape = np.sin(np.pi * u) ** 1.5
    out = np.zeros(n); out[m] = nz * shape * gain; return out
fx = sweep(T.C_RAMP[0] - 4, T.C_RAMP[1] + 8, 150, 4000, 1.6, False)
fx += sweep(T.E_RAMP[0], T.E_RAMP[1] + 4, 150, 5000, 1.6, True)
# launch hit
x = np.arange(int(.8 * SR)) / SR
add(fx, (np.sin(2 * np.pi * 50 * x) * np.exp(-x / .25) + lp(rng.standard_normal(len(x)), 900) * np.exp(-x / .12)) * .9,
    T.F_END[0] / T.FPS)

# ---------------------------------------------------------------- pen scratch during ink-in
pen = np.zeros(n)
for k in range(9):
    at = (1 + k * 3.2 + rng.random() * 1.5) / T.FPS; L = .12 + rng.random() * .16
    x = np.arange(int(L * SR)) / SR
    nz = rng.standard_normal(len(x)); nz = nz - lp(nz, 1500); nz = lp(nz, 6000)
    am = np.sin(np.pi * x / L) * (0.6 + 0.4 * np.sin(2 * np.pi * (14 + rng.random() * 8) * x))
    add(pen, nz * am * .35, at)

# ---------------------------------------------------------------- UI blips (caption pops / type-on)
ui = np.zeros(n)
def blip(fr_, f0=1320, L=.045, g=.12):
    x = np.arange(int(L * SR)) / SR
    add(ui, np.sign(np.sin(2 * np.pi * f0 * x)) * np.exp(-x / (L / 3)) * g, fr_ / T.FPS)
cyc = 720 / (750 / T.SLOW); D0 = T.D_SLOW[0]
for fr_ in [2, 19, D0, 164, 245, 245 + 14, T.F_END[0] + 4]:
    blip(fr_, 990, .07, .14); blip(fr_ + 1.5, 1480, .05, .1)
for fr_ in range(3, 14, 2): blip(fr_, 2600, .015, .035)            # type-on ticks
prev = None
for f in range(int(D0), int(D0 + cyc)):
    s = T.stroke(1, f)
    if s != prev: blip(f, 760 + s * 180, .05, .09); prev = s

# ---------------------------------------------------------------- music bed (chiptune), tape-stops with the ramp
BPM = 112; beat = 60 / BPM
mlen = DUR + 4; mt = np.arange(int(mlen * SR)) / SR
mus = np.zeros(len(mt))
roots = [45, 41, 48, 43]                       # A F C G (midi)
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
for b in range(int(mlen / beat)):
    bar = (b // 4) % 4; r = roots[bar]
    for half in (0, .5):
        at = (b + half) * beat; L = beat * .45
        x = np.arange(int(L * SR)) / SR
        note = r if half == 0 else r + 12
        sq = np.sign(np.sin(2 * np.pi * mtof(note) * x)) * np.exp(-x / .12) * .10
        add(mus, sq, at)
    # hats
    x = np.arange(int(.03 * SR)) / SR
    hz = rng.standard_normal(len(x)); hz -= lp(hz, 6000)
    add(mus, hz * np.exp(-x / .008) * .07, (b + .5) * beat)
    if b % 2 == 0:
        x = np.arange(int(.18 * SR)) / SR
        add(mus, np.sin(2 * np.pi * 55 * (1 + 2 * np.exp(-x / .02)) * x) * np.exp(-x / .07) * .25, b * beat)
    # arp lead every other bar
    if bar in (1, 3):
        for k, iv in enumerate([0, 7, 12, 15]):
            at = b * beat + k * beat / 4; L = beat / 4 * .9; x = np.arange(int(L * SR)) / SR
            add(mus, np.sign(np.sin(2 * np.pi * mtof(r + 24 + iv) * x)) * np.exp(-x / .05) * .035, at)
# tape rate: follows speed, but hits zero (stop) during slow-mo, restarts with the ramp-up
rate = np.clip((spd - 0.02) / 0.98, 0, 1) ** .7
tau = np.cumsum(rate) / SR
music = np.interp(tau, mt, mus) * np.clip(rate * 3, 0, 1)
# slow-mo pad: low detuned drone under the bangs
pm = (spd < 0.5).astype(float); pm = lp(pm, 3)
pad = (np.sin(2 * np.pi * 55 * t) + np.sin(2 * np.pi * 55.4 * t) * .8 + np.sin(2 * np.pi * 82.5 * t) * .4) * .05 * pm
music += pad

# riser into the launch + sub drop as slow-mo lands
a0 = T.E_RAMP[0] / T.FPS; a1 = T.F_END[0] / T.FPS; m_ = (t >= a0) & (t < a1); u_ = (t[m_] - a0) / (a1 - a0)
rise = np.zeros(n); rise[m_] = np.sin(2 * np.pi * np.cumsum(200 + 1800 * u_ ** 2) / SR) * u_ ** 2 * .12
rise[m_] += lp(rng.standard_normal(m_.sum()), 500 + 7000 * u_ ** 2) * u_ ** 2 * .5
x = np.arange(int(1.2 * SR)) / SR
add(rise, np.sin(2 * np.pi * np.cumsum(70 * np.exp(-x / .5) + 28) / SR) * np.exp(-x / .5) * .7, T.D_SLOW[0] / T.FPS - .1)
# sidechain: duck music under every bang
duck = np.ones(n)
for c, fire in T.FIRE.items():
    ph = (crank_s - fire) % 720
    for i in np.nonzero(np.diff(ph) < -300)[0] + 1:
        if spd[i] < .5:
            k = np.arange(min(n - i, int(.4 * SR))); duck[i:i + len(k)] = np.minimum(duck[i:i + len(k)], 1 - .7 * np.exp(-k / SR / .15))
mono = fx * .3 + pen + ui + music * .9 * duck + rise
L_ = mono + engL * .8 + engR * .35
R_ = mono + engR * .8 + engL * .35
mix = np.stack([L_, R_], 1)
# gentle bus compression + limiter
mix = np.tanh(mix * 1.3) * .9
mix /= max(1e-6, np.abs(mix).max()) / .89
st = mix
w = wave.open(sys.argv[1], "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype("<i2").tobytes()); w.close()
print("ok", DUR)
