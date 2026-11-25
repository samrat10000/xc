# 001_ring sound: quiet penthouse (rain on the glass, fridge hum, a far siren), then the phone rings and buzzes on the wood at 0.33 s
import subprocess, numpy as np, os
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(S, '..', '..'); SR = 48000; DUR = float(os.environ.get('DUR', '4.0'))
def ld(f, ss=0, t=None):
    cmd = ['ffmpeg', '-v', 'quiet', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
L = int(DUR * SR); buses = {k: np.zeros(L, np.float32) for k in ('amb', 'ring', 'vib')}
def put(b, a, t, g):
    i = int(t * SR); a = a[:max(0, L - i)]; buses[b][i:i + len(a)] += a * g
def rms(a): return float(np.sqrt(np.mean(a * a)) + 1e-9)
T0 = float(os.environ.get('T0', '.33')); OFF = float(os.environ.get('OFF', '0')); STOP = float(os.environ.get('STOP', '99'))
def cutoff(a, t0):   # the ring stops dead when he answers (8 ms fade)
    n = int((STOP - t0) * SR)
    if 0 < n < len(a): k = int(.008 * SR); a = a.copy(); a[n:n + k] *= np.linspace(1, 0, len(a[n:n + k])); a[n + k:] = 0
    return a
rain = ld(f'{R}/sfx7/rainglass/3_c0f69197.mp3', 5, DUR); put('amb', rain / rms(rain), 0, .035)
fr = ld(f'{R}/sfx7/fridge/0_e7ba27fc.mp3', 2, DUR); put('amb', fr / rms(fr), 0, .02)
si = ld(f'{R}/sfx7/siren/0_ead5a45b.mp3', 60, DUR); put('amb', si / rms(si), 0, .025)
rg = ld(f'{R}/sfx7/ring/3_0af307fc.mp3', OFF); put('ring', cutoff(rg / rms(ld(f'{R}/sfx7/ring/3_0af307fc.mp3')), T0), T0, .09 * float(os.environ.get('RINGG', '1')))
vb0 = ld(f'{R}/sfx7/vib/0_c9ed7654.mp3', .45 - .02); vb = vb0[int(OFF * SR):]; put('vib', cutoff(vb / rms(vb0), T0), T0, .12 * float(os.environ.get('VIBG', '1')))
buses['vo'] = np.zeros(L, np.float32)
for it in filter(None, os.environ.get('VO', '').split(',')):   # VO="file@time@gain,..."  (files in ep1/vo)
    fn, t_, g_ = it.split('@'); v_ = ld(f'{R}/ep1/vo/{fn}'); put('vo', v_ / rms(v_), float(t_), float(g_))
buses['ph'] = np.zeros(L, np.float32); buses['fx'] = np.zeros(L, np.float32)
for it in filter(None, os.environ.get('PH', '').split(',')):   # voice heard through the phone speaker
    fn, t_, g_ = it.split('@'); v_ = ld(f'{R}/ep1/vo/{fn}'); put('ph', v_ / rms(v_), float(t_), float(g_))
for it in filter(None, os.environ.get('FX', '').split(',')):   # FX="sfx7/x.mp3:ss@time@gain"
    fn, t_, g_ = it.split('@'); fn, ss_ = (fn.split(':') + ['0'])[:2]; v_ = ld(f'{R}/{fn}', float(ss_)); put('fx', v_ / rms(v_[:SR * 2]), float(t_), float(g_))
paths = {}
for k, a in buses.items(): paths[k] = os.path.join(S, f'_{k}.f32'); a.tofile(paths[k])
fc = ('[1]highpass=f=300,lowpass=f=7000,aecho=0.8:0.4:35|70:0.18|0.1[r];[2]lowpass=f=5000[v];'
      '[3]aecho=0.8:0.3:25:0.12[d];[4]highpass=f=350,lowpass=f=3400,acrusher=bits=10:mix=.25,aecho=0.8:0.3:12:0.1[p];[0][r][v][d][p][5]amix=inputs=6:normalize=0,alimiter=limit=0.89,loudnorm=I=-20:TP=-2[o]')
args = ['ffmpeg', '-y', '-v', 'error']
for k in ('amb', 'ring', 'vib', 'vo', 'ph', 'fx'): args += ['-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', paths[k]]
out = os.path.join(S, os.environ.get('OUT', '001_snd.wav'))
subprocess.run(args + ['-filter_complex', fc, '-map', '[o]', '-t', str(DUR), '-ar', '48000', out], check=True)
for p in paths.values(): os.remove(p)
print('ok', out)
