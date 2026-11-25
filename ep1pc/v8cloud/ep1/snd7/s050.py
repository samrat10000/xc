# 050_lobby: steps on marble, the horde moaning through the glass (swells when the camera reaches the glass), rain, the palm SLAP on the glass, backing off

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
feet = [1, 10, 19, 28, 38, 52, 60, 68, 77, 86, 96]; peaks = [1.5, 2.1, 2.7, 3.3, 3.9, 4.5, 5.0, 5.7, 6.4, 2.7, 3.3]
for k, (f, pk) in enumerate(zip(feet, peaks)):
    st = ld(f'{X}/shoe/0_8897b20d.mp3', pk - .06, .4); st *= np.linspace(1, 0, len(st)) ** .5
    put(st / rms(st), f / 24 - .02, .05 * (1.15 if k % 2 else .9))
glass_env = lambda t: np.interp(t, [0, 1.2, 2.0, 2.4, 3.2, 4.0], [.35, .55, 1.0, 1.0, .6, .45])
hd = ld(f'{X}/horde/235797.mp3', 8, 4.0, 'lowpass=f=1400,highpass=f=90'); put(hd / rms(hd), 0, .05, glass_env)          # heard through the glass: low-passed
sh = ld(f'{X}/horde/189230.mp3', 3, 4.0, 'lowpass=f=1800'); put(sh / rms(sh), 0, .03, glass_env)
rn = ld(f'{X}/rainglass/3_c0f69197.mp3', 9, 4.0); put(rn / rms(rn), 0, .03)
sl = ld(f'{X}/glassknock/483499.mp3', .22, .4, 'asetrate=48000*0.62,aresample=48000,lowpass=f=2500'); put(sl / rms(sl), 58 / 24 - .01, .32)
th = ld(f'{X}/boom/1_2de491df.mp3', 0, .6, 'lowpass=f=200'); put(th / rms(th), 58 / 24, .06)
ra = ld(f'{X}/rattle/' + sorted(os.listdir(f'{X}/rattle'))[0], 0, .8); put(ra / rms(ra), 58 / 24 + .03, .04)
tmp = os.path.join(S, '_050.f32'); out.tofile(tmp)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', tmp, '-af', 'aecho=0.8:0.4:60|120:0.2|0.12,alimiter=limit=0.89,loudnorm=I=-19:TP=-1.5',
                '-ar', '48000', '-ac', '2', os.path.join(S, '050_snd.wav')], check=True)
os.remove(tmp); print('ok')
