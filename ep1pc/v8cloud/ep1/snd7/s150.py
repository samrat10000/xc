# 150_stalker_scream: it stares, mouth hanging, wet breath; head snaps to the sky with the lightning and screams
import subprocess, numpy as np, os
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(S, '..', '..'); X = f'{R}/music/sfx'; SR = 48000; DUR = 2.25; L = int(DUR * SR)
def ld(f, ss=0, t=None):
    cmd = ['ffmpeg', '-v', 'quiet', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
def rms(a): return float(np.sqrt(np.mean(a * a)) + 1e-9)
def ldf(f, ss, t, af):
    cmd = ['ffmpeg', '-v', 'quiet', '-ss', str(ss), '-t', str(t), '-i', f, '-af', af, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
out = np.zeros(L, np.float32)
def put(a, t, g, fade=0.):
    a = a / rms(a); i = int(t * SR); a = a[:max(0, L - i)].copy()
    if fade: k = int(fade * SR); a[-k:] *= np.linspace(1, 0, min(k, len(a)))
    out[i:i + len(a)] += a * g
put(ld(f'{X}/rain_city_1.wav', 3, DUR), 0, .06)
put(ldf(f'{X}/wet_gurgle_1.wav', 0, 1.2, 'asetrate=48000*0.85,aresample=48000'), 0, .08, .3)
put(ld(f'{X}/thunder_1.wav', 0, 1.0), 1.2, .2, .4)
put(ldf(f'{X}/stalker_screech_0.wav', 0, 1.1, 'asetrate=48000*0.9,aresample=48000,aecho=0.8:0.5:90:0.3'), 1.3, .34, .35)
put(ldf(f'{X}/stalker_screech_0.wav', 0, 1.0, 'asetrate=48000*0.55,aresample=48000,lowpass=f=400'), 1.3, .15, .35)

p = os.path.join(S, '_150.f32'); out.tofile(p)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', p, '-af', 'highpass=f=30,alimiter=limit=0.89,loudnorm=I=-18:TP=-1.5,apad', '-t', str(DUR), '-ar', '48000', os.path.join(S, '150_snd.wav')], check=True)
os.remove(p); print('ok')
