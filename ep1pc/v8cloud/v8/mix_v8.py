# Ep1 v8 full-timeline sound mix. NO background music, only real recordings, plus ONE music piece (v5 score ending) from 135 to the black.
# Buses: amb (beds), fx, vo (on-screen Sam), ph (Akash through the phone), narr (Sam to the audience, dry + upfront), mus.
# Narration ducks everything else ~10 dB; on-screen lines duck beds ~6 dB. Master -14 LUFS / -1.5 dBTP.
import subprocess, numpy as np, os, json, sys
SR = 48000; H = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(H)
T = f'{H}/tsfx'; X = f'{H}/xsfx'; S7 = f'{R}/sfx7'; SN = f'{R}/ep1/snd7'; VO = f'{H}/vot'; SC = f'{H}/snd'
MUS = '/mnt/project-files/reels/series/ep1/music-v5.mp4'
if not os.path.exists(MUS): MUS = f'{R}/music/music-v5.mp4'      # portable copy (xc\\ep1pc\\v8cloud\\music)
FPS = 24
SHOTS = [('000', 168), ('001', 95), ('002', 47), ('003', 83), ('004', 174), ('004w', 60), ('005', 92), ('006', 96), ('007', 48), ('030', 72),
         ('040', 443), ('050', 120), ('055', 70), ('060', 96), ('070', 84), ('080', 36), ('090', 84), ('095', 60), ('100', 36), ('110', 60),
         ('120', 36), ('125', 144), ('130', 72), ('135', 60), ('140', 48), ('150', 60), ('152', 36), ('155', 36), ('160', 252), ('165', 36)]
ST = {}; t = 0.
for n, f in SHOTS: ST[n] = t; t += f / FPS
DUR = t; L = int(DUR * SR) + SR
_DUR = {}
def fdur(f):
    if f not in _DUR: _DUR[f] = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f], capture_output=True, text=True).stdout or 0)
    return _DUR[f]
def ld(f, ss=0, d=None, rate=None):
    fd = fdur(f); need = (d or 0) / (rate or 1)
    if fd and ss + need > fd: ss = max(0., (ss % max(fd - need, .01)) if fd > need else 0.)   # long beds: wrap the offset inside the file
    af = [] if not rate else ['-af', f'asetrate={int(SR * rate)},aresample={SR}']
    cmd = ['ffmpeg', '-v', 'quiet', '-ss', str(ss)] + (['-t', str(d / (rate or 1))] if d else []) + ['-i', f, '-ac', '1', '-ar', str(SR)] + af + ['-f', 'f32le', '-']
    a = np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).copy()
    if not len(a): print('EMPTY', f, file=sys.stderr)
    return a
def rms(a): return float(np.sqrt(np.mean(a * a)) + 1e-9)
def db(x): return 10 ** (x / 20)
B = {k: np.zeros(L, np.float32) for k in ('amb', 'fx', 'vo', 'car', 'ph', 'narr', 'mus', 'keep')}
def put(bus, shot, at, f, g_db, ss=0, d=None, fi=.01, fo=.05, rate=None, norm='rms'):
    a = ld(f, ss, d, rate)
    if not len(a): return
    if norm == 'rms': a = a / rms(a) * .1           # every source to -20 dBFS RMS, then the gain says where it sits
    elif norm == 'peak': a = a / (np.abs(a).max() + 1e-9) * .5
    n = len(a); ki, ko = int(fi * SR), int(fo * SR)
    if ki: a[:min(ki, n)] *= np.linspace(0, 1, min(ki, n))
    if ko: a[-min(ko, n):] *= np.linspace(1, 0, min(ko, n))
    i = int((ST[shot] + at) * SR); a = a[:max(0, L - i)]
    B[bus][i:i + len(a)] += a * db(g_db)
def bed(shot, f, g_db, ss=0, d=None, at=0., fi=.3, fo=.3):     # a bed for the whole shot (or d seconds)
    d = d or (dict(SHOTS)[shot] / FPS - at); put('amb', shot, at, f, g_db, ss, d, fi, fo)
def keep(shot, f, g_db=0, d=None):                              # an approved v7 per-shot mix, as it was
    a = ld(f, 0, d or dict(SHOTS)[shot] / FPS); i = int(ST[shot] * SR); B['keep'][i:i + len(a)] += a * db(g_db)

# ---------------- 000 hook (7 s): the hidden long lens on the rooftop. Narration to the audience.
bed('000', f'{T}/rain_7.mp3', -10, ss=20)
put('amb', '000', 0, f'{T}/siren_8.mp3', -20, ss=40, d=7, fi=1, fo=1)
put('narr', '000', .15, f'{VO}/h1_nyc_t1.wav', 0)
put('narr', '000', 3.45, f'{VO}/h2_boom_t1.wav', 0)                      # "Then..." / "boom" lands at 5.33 s = picture blast f128
BOOM = 5.33
put('fx', '000', BOOM - .02, f'{T}/subdrop_4.mp3', 4, fo=1.5)
put('fx', '000', BOOM, f'{T}/boom_2.mp3', 0, fo=1.0)
put('fx', '000', BOOM + .05, f'{T}/hit_6.mp3', -2, fo=1.0)
put('fx', '000', BOOM + .25, f'{S7}/rattle/' + sorted(os.listdir(f'{S7}/rattle'))[0], -8, d=1.6, fo=.6)
put('fx', '000', BOOM + .35, f'{T}/debris2_2.mp3', -12, fo=.8)
put('amb', '000', BOOM + .5, f'{X}/alarm2.mp3', -14, ss=1, d=1.7, fi=.4)
put('narr', '000', 5.75, f'{VO}/h3_slept_t1.wav', 0)                     # "And I slept through it." ends on the cut to 001

# ---------------- 001 / 002: approved v7 sound (rain, fridge, ring, buzz)
keep('001', f'{SN}/001_snd.wav'); keep('002', f'{SN}/002_snd.wav')
# ---------------- 003: he answers. No narration under the call.
d3 = 83 / FPS
bed('003', f'{S7}/rainglass/3_c0f69197.mp3', -15, ss=9); bed('003', f'{S7}/fridge/0_e7ba27fc.mp3', -20, ss=4)
put('vo', '003', .12, f'{VO}/003_groggy_t1.wav', 0)                      # "Akash? It's like four in the--"
put('ph', '003', 2.72, f'{VO}/003_akash_look_t1.wav', 0)                 # "Sam! Are you seeing this? Look outside. Look outside!" (runs into 004)
# ---------------- 004: he walks to the glass, the tower erupts at 4.8 s
bed('004', f'{S7}/rainglass/3_c0f69197.mp3', -15, ss=12); bed('004', f'{S7}/fridge/0_e7ba27fc.mp3', -22, ss=8, d=4.8)
B4 = 4.8
put('fx', '004', B4, f'{T}/boom_2.mp3', 2, fo=1.2); put('fx', '004', B4 - .02, f'{T}/subdrop_4.mp3', 3, fo=1.5)
put('fx', '004', B4 + .08, f'{S7}/rattle/' + sorted(os.listdir(f'{S7}/rattle'))[0], -4, d=2.0, fo=.6)
put('fx', '004', B4 + .15, f'{T}/glass_2.mp3', -14, d=1.2, fo=.6)
put('amb', '004', B4 + .6, f'{X}/alarm.mp3', -12, d=1.8, fi=.2)
put('amb', '004', B4 + .9, f'{X}/alarm2.mp3', -14, ss=3, d=4, fi=.3)
# ---------------- 004w: the watcher again (outside: rain, the alarms, far sirens)
bed('004w', f'{T}/rain_7.mp3', -10, ss=60); bed('004w', f'{X}/alarm2.mp3', -16, ss=6); bed('004w', f'{T}/siren_8.mp3', -16, ss=80)
# ---------------- 005: approved v7 call drop ("Don't take the bridge, they closed the--", broken words, dead line)
keep('005', f'{SN}/005_snd.wav')
# ---------------- 006: the Screamer stands still, the push-in, THE v5 scream (restored) with a street echo
bed('006', f'{T}/rain_7.mp3', -12, ss=90); bed('006', f'{X}/alarm2.mp3', -20, ss=9)
SCR = 2.45
for k_, g_ in (('vox', 2), ('hit', -2), ('amb', -6)): put('fx', '006', SCR, f'{SC}/scream_v5_{k_}.wav', g_, fo=.3, norm=None)
put('fx', '006', SCR + .32, f'{SC}/scream_v5_vox.wav', -16, fo=.6, norm=None)     # the scream back off the far towers
# ---------------- 007: ripped off the tripod, keys, chain, deadbolt
bed('007', f'{S7}/rainglass/3_c0f69197.mp3', -18, ss=20)
put('fx', '007', 0, f'{S7}/camhandle/' + sorted(os.listdir(f'{S7}/camhandle'))[0], -8, d=.8)
put('fx', '007', .35, f'{X}/keys.mp3', -6, d=1.2)
put('fx', '007', 1.25, f'{X}/chain.mp3', -8, d=.6); put('fx', '007', 1.6, f'{X}/deadbolt.mp3', -6, ss=.1, d=.5)
put('vo', '007', .05, f'{VO}/007_keys_t1.wav', -1, fo=.12)
# ---------------- 030: approved corridor picture, re-voiced (male take) and the sob removed
keep('030', f'{SN}/030_snd_v8.wav')
# ---------------- 040: approved stairwell sound, then the continued take (vault, two flights, LOBBY door)
keep('040', f'{SN}/c40_snd.wav', d=311 / FPS)
t40 = 311 / FPS
put('fx', '040', t40, f'{X}/stairs.mp3', -4, d=5.0, fi=.05, fo=.3)
bed('040', f'{S7}/stairamb/' + sorted(os.listdir(f'{S7}/stairamb'))[0], -14, at=t40 - .2)
put('fx', '040', t40 + 1.1, f'{T}/hit_5.mp3', -14, d=.5)                 # the landing thump after the vault
put('fx', '040', t40 + 2.6, f'{T}/static_5.mp3', -16, ss=2, d=.35)       # camcorder glitch
put('fx', '040', 443 / FPS - .3, f'{X}/pushbar.mp3', -4)                 # the LOBBY door
# ---------------- 050: the lobby (continuous POV): the horde slaps the glass, turn to B1 PARKING
bed('050', f'{S7}/horde/' + sorted(os.listdir(f'{S7}/horde'))[0], -10)
for k_, tt in enumerate((.9, 1.3, 1.6, 2.2, 2.5, 3.1)):
    put('fx', '050', tt, f'{S7}/glassknock/' + sorted(os.listdir(f'{S7}/glassknock'))[k_ % len(os.listdir(f'{S7}/glassknock'))], -6 - k_ % 3 * 2, d=.4)
put('fx', '050', 3.3, f'{X}/stairs.mp3', -8, ss=1.0, d=1.7)
# ---------------- 055: down the service flight, the B1 door bar, into the dark garage
put('fx', '055', 0, f'{X}/stairs.mp3', -6, ss=2.2, d=1.8)
put('fx', '055', 1.85, f'{X}/pushbar.mp3', -2)
bed('055', f'{S7}/stairamb/' + sorted(os.listdir(f'{S7}/stairamb'))[0], -18)
# ---------------- 060: approved garage sound
keep('060', f'{SN}/060_snd.wav')
# ---------------- 070: in the car (over his shoulder): rain on the roof, "Please start. Please.", the starter cranks
bed('070', f'{T}/rainroof_4.mp3', -12, ss=30)
put('fx', '070', 0, f'{X}/door.mp3', -4)
put('vo', '070', .55, f'{VO}/070_please_t1.wav', 0)
CR = 64 / FPS
put('car', '070', CR, f'{X}/start.mp3', 0, ss=.2, d=(84 - 64) / FPS + 1.5, fo=.4, norm='peak')   # crank -> catch (lands in 080)
# ---------------- 080: ignition: catch + two revs (real recordings), idle under
bed('080', f'{T}/rainroof_4.mp3', -14, ss=40)
put('car', '080', .15, f'{T}/rev_4.mp3', -3, ss=.85, d=1.6, norm='peak', fo=.3)
# ---------------- 090: up the ramp, through the half-open gate, into the rain
put('car', '090', 0, f'{T}/rev2_9.mp3', -6, ss=2, d=3.5, norm='peak', fo=.4)
put('fx', '090', .25, f'{T}/drift_1.mp3', -8, d=1.4, fo=.4)
put('fx', '090', 1.15, f'{T}/ping_0.mp3', -10, ss=.0, d=.7)              # the gate scrapes the roof
put('fx', '090', 1.7, f'{T}/splash_0.mp3', -6, d=1.0)
bed('090', f'{T}/rain_7.mp3', -12, ss=120, at=1.4)
# ---------------- 095: the hidden camera from a dark window: the car fishtails past below. Narration.
bed('095', f'{T}/rain_7.mp3', -9, ss=140)
put('car', '095', 0, f'{T}/passby_1.mp3', -6, ss=6.4, d=2.6, norm='peak', fi=.3, fo=.6)
put('narr', '090', 3.0, f'{VO}/095_akashsaid_t1.wav', 0)                  # "Akash said don't take the bridge. ... The bridge was the only way out."
# ---------------- 100 / 110 / 120: re-sounded with the teaser's real tyre, pass-by, drift recordings
put('car', '100', 0, f'{T}/passby_1.mp3', -2, ss=7.1, d=1.5, norm='peak'); put('fx', '100', .3, f'{T}/splash_0.mp3', -6, d=1.0)
bed('110', f'{T}/rain_7.mp3', -12, ss=160); put('car', '110', 0, f'{T}/rev2_0.mp3', -4, ss=1, d=2.5, norm='peak', fo=.3)
put('fx', '110', .4, f'{S7}/runwood/' + sorted(os.listdir(f'{S7}/runwood'))[0], -12, d=1.6)
put('fx', '110', 1.4, f'{T}/splash_0.mp3', -8, d=1.0)
put('car', '120', 0, f'{T}/drift_6.mp3', 0, ss=7.3, d=1.6, norm='peak', fo=.3)
# ---------------- 125: the Brute: stomps, roar, the brakes, "Nope...", charge, J-turn, the hit, roar, "Bridge it is."
bed('125', f'{T}/rain_7.mp3', -12, ss=180)
put('car', '125', 0, f'{X}/idle.mp3', -10, ss=2, d=6, fi=.1, fo=.5)
for tt in (.15, .75, 1.3): put('fx', '125', tt, f'{T}/boom2_7.mp3', -10, d=.6, rate=.8)
put('fx', '125', .85, f'{T}/drift2_9.mp3', -4, ss=4.5, d=1.4, fo=.3)         # brakes hard + skid
put('fx', '125', 1.5, f'{T}/roar_5.mp3', 0, d=2.0, rate=.82, fo=.5); put('fx', '125', 1.52, f'{T}/bear_6.mp3', -6, d=2.0, rate=.9, fo=.5)
put('vo', '125', 1.7, f'{VO}/125_nope_t1.wav', 0)
for tt in np.arange(2.4, 3.6, .2): put('fx', '125', float(tt), f'{T}/boom2_7.mp3', -8, d=.4, rate=.75)   # the charge
put('car', '125', 2.5, f'{T}/rev2_9.mp3', -4, ss=4, d=1.2, norm='peak')                                  # reverse, J-turn
put('fx', '125', 2.9, f'{T}/drift_1.mp3', -6, d=1.2)
HIT = 86 / FPS
put('fx', '125', HIT, f'{T}/hit_5.mp3', 2); put('fx', '125', HIT + .02, f'{T}/glass_2.mp3', -8, d=1.0); put('fx', '125', HIT, f'{T}/boom2_7.mp3', -2, d=.8)
put('car', '125', HIT + .3, f'{T}/rev2_0.mp3', -2, ss=.5, d=2.4, norm='peak', fo=.5)
put('fx', '125', 106 / FPS - .1, f'{T}/lion_5.mp3', -2, rate=.78, fo=.6)
put('vo', '125', 5.0, f'{VO}/125_bridge_t1.wav', -1)
# ---------------- 130: the overpass: the car rolls in and STOPS. Idle, wipers, rain on the roof.
bed('130', f'{T}/rainroof_4.mp3', -14, ss=60); put('car', '130', 0, f'{X}/idle.mp3', -8, ss=5, d=3.0)
put('fx', '130', 1.7, f'{T}/wiper_2.mp3', -14, d=1.3)
# ---------------- 135 -> 155: the Stalker. Real sounds drop to near silence; the ONE music piece (v5 ending) carries it.
bed('135', f'{T}/rainroof_4.mp3', -22, ss=70, d=2.5); put('car', '135', 0, f'{X}/idle.mp3', -16, ss=8, d=2.5, fo=1.0)
put('fx', '135', .3, f'{X}/heart.mp3', -6, d=2.2)
put('fx', '140', .0, f'{T}/whoosh_0.mp3', -8); put('fx', '140', .45, f'{X}/bone.mp3', -8, d=1.2)
SCR2 = 30 / FPS
put('fx', '150', SCR2, f'{T}/elk_0.mp3', 2, ss=3.2, d=1.0, rate=.7, fo=.3); put('fx', '150', SCR2, f'{T}/tiger_3.mp3', -2, ss=1.0, d=1.2, rate=.75, fo=.4)
put('fx', '150', SCR2 - .03, f'{T}/thunder_5.mp3', -4, d=1.2); put('fx', '150', 52 / FPS, f'{T}/boom2_7.mp3', -4, d=.6)
put('fx', '152', 19 / FPS, f'{T}/hit_6.mp3', -4, fo=.8)                    # it lands
M0 = ST['135']; DROP = ST['152'] + 19 / FPS; MHIT = 30.7                   # the score's hit lands on the drop
a = ld(MUS, MHIT - (DROP - M0), ST['160'] - M0); a = a / (np.abs(a).max() + 1e-9) * .5
n = len(a); a[:int(1.2 * SR)] *= np.linspace(0, 1, int(1.2 * SR)); fo_ = int(1.5 * SR); a[-fo_:] *= np.linspace(1, 0, fo_) ** 2
B['mus'][int(M0 * SR):int(M0 * SR) + n] += a * db(-4)
# ---------------- 160: approved ending (dashcam, empty seat, buzz x2, Akash voicemail, click, dead line)
keep('160', f'{SN}/160_snd.wav')
# ---------------- 165: the hidden camcorder's viewfinder, REC blinks, tape stop
bed('165', f'{T}/rain_7.mp3', -14, ss=200, d=.8)
put('fx', '165', .55, f'{T}/tapestop_1.mp3', -6, d=.9, fo=.1)

# ---------------- processing + ducking
def save(a, p): a.astype('<f4').tofile(p)
def ff(inp, af, out):
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', inp, '-af', af, '-f', 'f32le', out], check=True)
    return np.fromfile(out, '<f4')[:L]
proc = {'narr': 'highpass=f=70,equalizer=f=180:t=q:w=1:g=2,equalizer=f=3000:t=q:w=1.2:g=2.5,acompressor=threshold=-24dB:ratio=3:attack=8:release=120:makeup=3',
        'vo': 'highpass=f=90,acompressor=threshold=-24dB:ratio=2.5:makeup=2,aecho=0.9:0.95:22:0.12',
        'ph': 'highpass=f=350,lowpass=f=3400,acrusher=bits=10:mix=.25,acompressor=threshold=-26dB:ratio=4:makeup=4,aecho=0.9:0.95:12:0.1',
        'car': 'lowpass=f=9000', 'fx': 'anull', 'amb': 'anull', 'mus': 'anull', 'keep': 'anull'}
P = {}
for k, a in B.items():
    TMP = os.environ.get('TMP', '/tmp'); save(a, f'{TMP}/_{k}.f32'); P[k] = ff(f'{TMP}/_{k}.f32', proc[k], f'{TMP}/_{k}o.f32')
def env(a, att=.03, rel=.35):
    w = int(.01 * SR); e = np.sqrt(np.convolve(a * a, np.ones(w) / w, 'same')); o = np.zeros_like(e); g = 0.
    ka, kr = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR))
    for i in range(0, len(e), 48):                     # 1 ms control rate
        x = e[i]; g = ka * g + (1 - ka) * x if x > g else kr * g + (1 - kr) * x; o[i:i + 48] = g
    return o
en = env(P['narr']); ev = env(P['vo'] + P['ph'])
dn = np.clip(en / .02, 0, 1); dv = np.clip(ev / .02, 0, 1)
duck_all = db(-10) ** dn                               # narration: everything else -10 dB
duck_bed = db(-6) ** dv                                # on-screen lines: beds/fx -6 dB
# scene dynamics (T: the apartment is quiet, the stairs build, the chase and the Brute are loud, the bridge drops before the music):
# each shot's non-dialogue bed is set by its MEDIAN 100 ms level (transients like the booms keep their punch), lines stay fixed.
TGT = {'000': -32, '001': -33, '002': -33, '003': -34, '004': -32, '004w': -31, '005': -31, '006': -29, '007': -29, '030': -28, '040': -24,
       '050': -24, '055': -26, '060': -26, '070': -28, '080': -23, '090': -20, '095': -25, '100': -20, '110': -21, '120': -19, '125': -20,
       '130': -29, '135': -33, '140': -30, '150': -22, '152': -24, '155': -30, '160': -30, '165': -32}
bedsum = P['amb'] + P['fx'] + P['car']
KEEPG = {'001': -5, '002': -5, '005': -2, '030': -1, '040': 0, '060': 0, '160': -1}   # approved v7 mixes (they carry their own lines): fixed trims only
MAXG = {'150': 4, '135': 0}
kcurve = np.ones(L, np.float32)
gcurve = np.ones(L, np.float32); w_ = int(.1 * SR)
for n_, f_ in SHOTS:
    i0 = int(ST[n_] * SR); i1 = i0 + int(f_ / FPS * SR); x_ = bedsum[i0:i1]
    lv = [np.sqrt(np.mean(x_[j:j + w_] ** 2)) + 1e-9 for j in range(0, len(x_) - w_, w_)]
    med = 20 * np.log10(np.median(lv)) if lv else -60
    g_ = float(np.clip(TGT[n_] - med, -14, MAXG.get(n_, 14))); gcurve[i0:i1] = db(g_); kcurve[i0:i1] = db(KEEPG.get(n_, g_))
    if os.environ.get('STEMS'): print('SCENE', n_, round(med, 1), '->', TGT[n_], 'gain', round(g_, 1))
k_ = int(.25 * SR); cs_ = np.concatenate([[0.], np.cumsum(gcurve, dtype=np.float64)]); ix_ = np.arange(L); lo_ = np.clip(ix_ - k_ // 2, 0, L); hi_ = np.clip(ix_ + k_ // 2, 0, L)
gcurve = ((cs_[hi_] - cs_[lo_]) / np.maximum(hi_ - lo_, 1)).astype(np.float32)
kcurve = ((np.concatenate([[0.], np.cumsum(kcurve, dtype=np.float64)])[hi_] - np.concatenate([[0.], np.cumsum(kcurve, dtype=np.float64)])[lo_]) / np.maximum(hi_ - lo_, 1)).astype(np.float32)
for kk in ('amb', 'fx', 'car'): P[kk] = P[kk] * gcurve
P['keep'] = P['keep'] * kcurve
mix = P['narr'] + (P['vo'] + P['ph']) * duck_all + (P['amb'] + P['fx'] + P['car'] + P['keep'] + P['mus'] * db(-3) ** dn) * duck_all * duck_bed
mix = mix[:int(DUR * SR)]
if os.environ.get('STEMS'):
    for k_, a_ in P.items():
        for n_, _f in SHOTS:
            i0 = int(ST[n_] * SR); i1 = i0 + int(_f / FPS * SR); x_ = a_[i0:i1]
            r_ = 20 * np.log10(np.sqrt(np.mean(x_ * x_)) + 1e-9)
            if r_ > -60: print('STEM', k_, n_, round(r_, 1))
save(mix, f'{TMP}/_mix.f32')
out = os.environ.get('OUT', f'{H}/ep1_v8_mix.wav')
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', f'{TMP}/_mix.f32', '-af',
                'anull', '-ar', '48000', '-ac', '2', out], check=True)
json.dump({n: round(ST[n], 3) for n, _ in SHOTS} | {'_dur': round(DUR, 3)}, open(f'{H}/v8_timeline.json', 'w'), indent=1)
print('ok', out, round(DUR, 2), 's')
