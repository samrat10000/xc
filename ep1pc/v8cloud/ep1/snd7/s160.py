# 160_empty_seat: rain blowing in through the open driver door, idling engine, phone buzzing on the seat from 1.0 s, Akash's voicemail through the phone speaker from 3.5 s, then dead line
import subprocess, numpy as np, os
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(S, '..', '..'); SR = 48000; DUR = 10.5; L = int(DUR * SR)
def ld(f, ss=0, t=None):
    cmd = ['ffmpeg', '-v', 'quiet', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
def rms(a): return float(np.sqrt(np.mean(a * a)) + 1e-9)
B = {k: np.zeros(L, np.float32) for k in ('rain', 'idle', 'vib', 'ph')}
def put(b, a, t, g):
    i = int(t * SR); a = a[:max(0, L - i)]; B[b][i:i + len(a)] += a * g
r1 = ld(f'{R}/music/sfx/rain_close_0.wav', 0, DUR); put('rain', r1 / rms(r1), 0, .06)
r2 = ld(f'{R}/sfx7/rainglass/1_971669dc.mp3', 3, DUR); put('rain', r2 / rms(r2), 0, .03)
idl = ld(f'{R}/music/sfx/engine_drive_0.wav', 0, DUR); put('idle', idl / rms(idl), 0, .03)
vb = ld(f'{R}/sfx7/vib/0_c9ed7654.mp3', .43, .75); vb = vb / rms(vb)
k = int(.01 * SR); vb[-k:] *= np.linspace(1, 0, k)
for t in (1.0, 2.25): put('vib', vb, t, .10)          # two buzzes, then it picks up to voicemail
vm = ld(f'{R}/ep1/vo/44.5_akash_voicemail.wav'); put('ph', vm / rms(vm), 3.5, .10)
end = 3.5 + len(vm) / SR; cl = np.zeros(int(.004 * SR), np.float32); cl[0] = .6; cl[1] = -.4; put('ph', cl, min(end + .05, DUR - .1), 1)
P = {}
for k_, a in B.items(): P[k_] = os.path.join(S, f'_{k_}.f32'); a.tofile(P[k_])
fc = ('[0]highpass=f=120,lowpass=f=9000[r];[1]lowpass=f=260[i];[2]lowpass=f=4000,aecho=0.8:0.3:8:0.2[v];'
      '[3]highpass=f=350,lowpass=f=3400,acrusher=bits=10:mix=.25,aecho=0.8:0.3:12:0.1[p];'
      '[r][i][v][p]amix=inputs=4:normalize=0,alimiter=limit=0.89,loudnorm=I=-20:TP=-2[o]')
a = ['ffmpeg', '-y', '-v', 'error']
for k_ in ('rain', 'idle', 'vib', 'ph'): a += ['-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', P[k_]]
subprocess.run(a + ['-filter_complex', fc, '-map', '[o]', '-t', str(DUR), '-ar', '48000', os.path.join(S, '160_snd.wav')], check=True)
for p in P.values(): os.remove(p)
print('ok')
