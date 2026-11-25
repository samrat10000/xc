# 060_garage: dead quiet garage, tube lights clunk on one by one (each adds to the hum), drips, his steps, the keys

import subprocess, numpy as np, os
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(S, '..', '..'); X = f'{R}/sfx7'; SR = 48000; DUR = 4.0; L = int(DUR * SR)
def ld(f, ss=0, t=None, af=None):
    cmd = ['ffmpeg', '-v', 'quiet', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', f] + (['-af', af] if af else []) + ['-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
out = np.zeros(L, np.float32)
def put(a, t, g, env=None):
    i = int(t * SR); a = a[:max(0, L - i)] * g
    if env is not None: a = a * env(np.arange(len(a)) / SR + t)
    out[i:i + len(a)] += a
def rms(a): return float(np.sqrt(np.mean(a * a)) + 1e-9)
for k, f_on in enumerate((10, 22, 34, 46)):
    cl = ld(f'{X}/buzz/0_fdee707b.mp3', .95 if k % 2 == 0 else 2.05, .7); put(cl / rms(cl), f_on / 24 - .1, .1 * (1 - .12 * k))
hum = ld(f'{X}/buzz/2_d8e0bafe.mp3', 2, 4.0)
put(hum / rms(hum), 0, .02, lambda t: sum((t > f / 24).astype(float) for f in (10, 22, 34, 46)) / 4)
rng = np.random.default_rng(6)
for tt in (.3, 1.4, 2.2, 3.3):                       # drips somewhere in the dark
    d = (np.sin(2 * np.pi * rng.uniform(1300, 1900) * np.arange(int(.05 * SR)) / SR) * np.exp(-np.arange(int(.05 * SR)) / (.008 * SR))).astype(np.float32)
    put(d, tt, .02)
for k, (f, pk) in enumerate(zip((62, 70, 77, 84, 91), (1.5, 2.1, 2.7, 3.3, 3.9))):
    st = ld(f'{X}/shoe/0_8897b20d.mp3', pk - .06, .4); st *= np.linspace(1, 0, len(st)) ** .5; put(st / rms(st), f / 24, .06)
ky = ld(f'{X}/keys/390324.mp3', .6, 1.2); put(ky / rms(ky), 80 / 24, .03)
tmp = os.path.join(S, '_060.f32'); out.tofile(tmp)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', tmp, '-af', 'aecho=0.8:0.5:90|170:0.3|0.18,alimiter=limit=0.89,loudnorm=I=-20:TP=-2',
                '-ar', '48000', '-ac', '2', os.path.join(S, '060_snd.wav')], check=True)
os.remove(tmp); print('ok')
