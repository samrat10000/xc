# 140_stalker_cu: rain on the overpass, the lightning crack at f12, bone clicks and a low throat growl
import subprocess, numpy as np, os
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(S, '..', '..'); X = f'{R}/music/sfx'; SR = 48000; DUR = 1.5; L = int(DUR * SR)
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
put(ld(f'{X}/rain_city_1.wav', 1, DUR), 0, .06)
put(ld(f'{X}/thunder_0.wav', 0, 1.5), .48, .22, .4)
put(ld(f'{X}/stalker_click_0.wav', 0, .6), .15, .14, .2)
put(ld(f'{X}/stalker_click_1.wav', 0, .5), .95, .12, .2)
put(ldf(f'{X}/growl_0.wav', 0, 1.4, 'asetrate=48000*0.8,aresample=48000'), .1, .07, .4)

p = os.path.join(S, '_140.f32'); out.tofile(p)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', p, '-af', 'highpass=f=30,alimiter=limit=0.89,loudnorm=I=-18:TP=-1.5,apad', '-t', str(DUR), '-ar', '48000', os.path.join(S, '140_snd.wav')], check=True)
os.remove(p); print('ok')
