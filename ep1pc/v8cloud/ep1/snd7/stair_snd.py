# c40 stairwell sound: real recorded steps on each footfall, room tone, distant sirens through the window,
# emergency-light buzz, Sam's two lines, the Crawler's hiss at the reveal. No score (score starts at the ignition).
import subprocess, numpy as np, random, os
S = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(S, '..', '..'); SR = 48000; FPS = 24; N = 312
def ld(f, ss=0, t=None):
    cmd = ['ffmpeg', '-v', 'quiet', '-ss', str(ss)] + (['-t', str(t)] if t else []) + ['-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
L = int(N / FPS * SR) + SR; mix = {k: np.zeros(L, np.float32) for k in ('steps', 'amb', 'vo', 'fx')}
def put(bus, a, t, g=1.):
    i = int(t * SR); a = a[:max(0, L - i)]; mix[bus][i:i + len(a)] += a * g
def rms(a): return float(np.sqrt(np.mean(a * a)) + 1e-9)
# step one-shots
walk = ld(f'{R}/sfx7/shoe/0_8897b20d.mp3'); run = ld(f'{R}/sfx7/stairs/1_85019719.mp3')
won = [1.56, 2.15, 3.31, 3.94, 4.5, 5.09, 5.7, 6.36]; ron = [.31, .61, .82, 1.02, 1.23, 1.44, 1.64, 1.84, 2.05, 2.25, 2.46, 2.67, 2.87, 3.08, 3.29]
def cut(a, t, d=.28):
    s = a[max(0, int((t - .02) * SR)):int((t + d) * SR)].copy(); f = np.ones(len(s)); k = int(.06 * SR); f[-k:] = np.linspace(1, 0, k); return s * f
wk = [cut(walk, t) for t in won]; rk = [cut(run, t, .2) for t in ron]
wk = [w / rms(w) for w in wk]; rk = [w / rms(w) for w in rk]
def flight(f0, every, n=10): return [f0 + i * every for i in range(n)]
walkf = [30, 40, 50, 60] + flight(68, 7) + [140, 148, 156] + flight(162, 7) + [234, 242, 250]
runf = flight(256, 5) + [306, 312]
rng = random.Random(3)
for f in walkf: put('steps', rng.choice(wk), f / FPS + rng.uniform(-.01, .01), rng.uniform(.75, 1.0))
for f in runf: put('steps', rng.choice(rk), f / FPS, rng.uniform(.9, 1.1))
# room tone + sirens (window) + buzz
amb = ld(f'{R}/sfx7/stairamb/2_2a4e960e.mp3', 20, N / FPS + 1); put('amb', amb / rms(amb), 0, .05)
sir = ld(f'{R}/sfx7/siren/0_ead5a45b.mp3', 30, N / FPS + 1); put('amb', sir / rms(sir), 0, .06)
bz = ld(f'{R}/sfx7/buzz/2_d8e0bafe.mp3', 2, 8); put('amb', bz / rms(bz) * np.linspace(0, 1, len(bz)) ** .5 * np.linspace(1, 0, len(bz)) ** .5, 6.0, .05)
# lines
vo1 = ld(f'{R}/ep1/vo/11.0_sam.wav'); vo2 = ld(f'{R}/ep1/vo/13.2_sam.wav')
put('vo', vo1 / rms(vo1), 172 / FPS, .12); put('vo', vo2 / rms(vo2), 305 / FPS, .16)
# the Crawler: a low wet breath as it rises, then the hiss on the reveal
cb = ld(f'{R}/music/sfx/crawler_breath_0.wav'); put('fx', cb / rms(cb), 268 / FPS, .05)
hs = ld(f'{R}/music/sfx/crawler_hiss_1.wav'); put('fx', hs / rms(hs), 300 / FPS, .14)
out = os.path.join(S, 'c40_snd.wav')
st = {}
for k, a in mix.items():
    p = os.path.join(S, f'_{k}.f32'); a.astype(np.float32).tofile(p); st[k] = p
# stairwell reverb on steps + voice, voice phone-mic presence, mix, limit
fc = ('[0]aecho=0.8:0.6:45|110|190:0.35|0.25|0.18,highpass=f=70[s];[2]aecho=0.8:0.5:60|140:0.2|0.12[v];'
      '[s][1][v][3]amix=inputs=4:normalize=0,alimiter=limit=0.89,loudnorm=I=-18:TP=-2[o]')
args = ['ffmpeg', '-y', '-v', 'error']
for k in ('steps', 'amb', 'vo', 'fx'): args += ['-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', st[k]]
subprocess.run(args + ['-filter_complex', fc, '-map', '[o]', '-t', str(N / FPS), '-ar', '48000', out], check=True)
for p in st.values(): os.remove(p)
print('ok', out)
