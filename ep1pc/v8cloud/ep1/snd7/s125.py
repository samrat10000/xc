# 125_brute_block: rain, heavy Brute footfalls, the roar, the V8 growls back (rev at 2.4 s), tyres bite and the car swerves past
import subprocess, numpy as np, os
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(S, '..', '..'); X = f'{R}/music/sfx'; SR = 48000; DUR = 5.0; L = int(DUR * SR)
def ld(f, ss=0, t=None):
    cmd = ['ffmpeg', '-v', 'quiet', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
def rms(a): return float(np.sqrt(np.mean(a * a)) + 1e-9)
out = np.zeros(L, np.float32)
def put(a, t, g, fade=0.):
    a = a / rms(a); i = int(t * SR); a = a[:max(0, L - i)].copy()
    if fade: k = int(fade * SR); a[-k:] *= np.linspace(1, 0, min(k, len(a)))
    out[i:i + len(a)] += a * g
put(ld(f'{X}/rain_city_0.wav', 2, DUR), 0, .05)
for k, t in enumerate((.15, .85)): put(ld(f'{X}/stomp_{k}.wav', 0, .8), t, .22, .1)
def ldf(f, ss, t, af):
    cmd = ['ffmpeg', '-v', 'quiet', '-ss', str(ss), '-t', str(t), '-i', f, '-af', af, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
# deeper, bigger roar: the sample slowed to 78 percent pitch, a sub layer an octave down, a wet throat growl and a little chest distortion
put(ldf(f'{X}/brute_roar_1.wav', 0, 2.2, 'asetrate=48000*0.78,aresample=48000,acrusher=bits=12:mix=.15'), 1.36, .30, .6)
put(ldf(f'{X}/brute_roar_1.wav', 0, 1.6, 'asetrate=48000*0.5,aresample=48000,lowpass=f=300'), 1.36, .18, .6)
put(ldf(f'{X}/growl_2.wav', 0, 2.0, 'asetrate=48000*0.7,aresample=48000'), 1.30, .12, .5)
put(ld(f'{X}/engine_drive_0.wav', 0, DUR), 0, .05)
put(ld(f'{X}/engine_start_1.wav', 2.6, 2.6), 2.35, .26, .6)
put(ld(f'{X}/exhaust_pop_0.wav', 0, .6), 2.55, .12, .2)
put(ld(f'{X}/tire_spin_1.wav', 0, 2.2), 2.6, .14, .6)
put(ld(f'{X}/whoosh_1.wav', 0, 1.2), 3.4, .16, .4)
put(ld(f'{X}/growl_1.wav', 0, 1.2), 3.6, .12, .5)
p = os.path.join(S, '_125.f32'); out.tofile(p)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', p, '-af', 'highpass=f=30,alimiter=limit=0.89,loudnorm=I=-18:TP=-1.5,apad', '-t', str(DUR), '-ar', '48000', os.path.join(S, '125_snd.wav')], check=True)
os.remove(p); print('ok')
