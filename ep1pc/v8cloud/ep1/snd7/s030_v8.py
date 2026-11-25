# 030_corridor: hurried steps on tile + runner, a woman sobbing behind PH-C (muffled, peaks as we pass the gap), TV hiss,
# a dying emergency light buzzing, a far siren, then the push-bar clunk and the stairwell opening up
import subprocess, numpy as np, os
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(S, '..', '..'); X = f'{R}/sfx7'; SR = 48000; DUR = 3.2; L = int(DUR * SR)
def ld(f, ss=0, t=None, af=None):
    cmd = ['ffmpeg', '-v', 'quiet', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', f] + (['-af', af] if af else []) + ['-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
out = np.zeros(L, np.float32)
def put(a, t, g, env=None):
    i = int(t * SR); a = a[:max(0, L - i)] * g
    if env is not None: a = a * env(np.arange(len(a)) / SR + t)
    out[i:i + len(a)] += a
def rms(a): return float(np.sqrt(np.mean(a * a)) + 1e-9)
feet = [1, 9, 17, 25, 34, 42, 49, 55, 61, 72]; peaks = [1.5, 2.1, 2.7, 3.3, 3.9, 4.5, 5.0, 5.7, 6.4, 2.7]
for k, (f, pk) in enumerate(zip(feet, peaks)):
    st = ld(f'{X}/shoe/0_8897b20d.mp3', pk - .06, .4, 'lowpass=f=2600' if 1 < k < 8 else None)   # on the runner the heel is duller
    st *= np.linspace(1, 0, len(st)) ** .5
    put(st / rms(st), f / 24 - .02, .05 * (1.15 if k % 2 else .9))
pass_env = lambda t: np.clip(np.interp(t, [0, .55, 1.0, 1.6, 2.3], [.25, .7, 1.0, .6, .15]), 0, 1)
# sob = ld(f'{X}/sob/368388.mp3', 3.05, 2.6, 'lowpass=f=1500,highpass=f=180,aecho=0.8:0.5:18:0.3')
# v8: the sob read as a FEMALE voice in the corridor (Sam 11-24). Removed; Sam's own male line goes on in the episode mix.
hiss = np.random.default_rng(3).normal(0, 1, L).astype(np.float32)
hs = subprocess.run(['ffmpeg', '-v', 'quiet', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', 'bandpass=f=4200:w=3000', '-f', 'f32le', '-'], input=hiss.tobytes(), capture_output=True).stdout
hs = np.frombuffer(hs, np.float32).copy(); put(hs / rms(hs), 0, .006, pass_env)
bz = ld(f'{X}/buzz/2_d8e0bafe.mp3', 2, DUR); put(bz / rms(bz), 0, .012)
si = ld(f'{X}/siren/0_ead5a45b.mp3', 64, DUR, 'lowpass=f=1800'); put(si / rms(si), 0, .02)
pb = ld(f'{X}/pushbar/475312.mp3'); put(pb / rms(pb[:SR // 2]), 58 / 24 - .1, .12)
sa = ld(f'{X}/stairamb/2_2a4e960e.mp3', 4, 1.2); put(sa / rms(sa), 2.45, .03, lambda t: np.clip((t - 2.45) / .3, 0, 1))
tmp = os.path.join(S, '_030.f32'); out.tofile(tmp)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', tmp, '-af', 'aecho=0.8:0.35:40|85:0.18|0.1,alimiter=limit=0.89,loudnorm=I=-20:TP=-2',
                '-ar', '48000', '-ac', '2', os.path.join(S, '030_snd_v8.wav')], check=True)
os.remove(tmp); print('ok')
