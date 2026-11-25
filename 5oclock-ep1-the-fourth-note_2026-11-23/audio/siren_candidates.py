"""Siren candidates for Sam to listen to (Ep1 v3 note: "the siren sound can be a lot better"). Each file = the town's THREE-NOTE
five o'clock call (the series pitches 66, 70, 73), ~8 s, designed a different way. Original designs over CC0 recordings
(recordings/openverse, LICENSES.txt). Writes audio/siren_candidates/*.wav. usage: python -E -s siren_candidates.py"""
import numpy as np
from pathlib import Path
from lib_mix import read, take, band, filter_, peak, clip_fade, stretch, wav, rate
from thriller import siren, hills, rec, mtof, OV, _ease

OUT = Path(__file__).resolve().parent / 'siren_candidates'; OUT.mkdir(exist_ok=True)
NOTES = (66 - 12, 70 - 12, 73 - 12); T = (0.4, 1.9, 3.4)                           # three calls, 1.5 s apart
L = int(9.0 * rate)


def put(buf, a, t, g=1.0):
    k = int(t * rate)
    if k < 0: a = a[-k:]; k = 0
    n = min(len(a), len(buf) - k)
    if n > 0: buf[k:k + n] += a[:n] * g


def sub(t0, dur=1.2, f=42):
    t = np.arange(int(dur * rate)) / rate; s = np.sin(2 * np.pi * f * t * (1 - 0.25 * t / dur)) * np.exp(-t / 0.35)
    return np.stack([s, s], 1).astype(np.float32)


def save(name, buf):
    buf = buf / (np.max(np.abs(buf)) + 1e-9) * 0.89; wav(OUT / f'{name}.wav', buf.astype(np.float32)); print('wrote', name)


# A: what v3 has now (for comparison)
st = read(Path(__file__).resolve().parent / 'stems' / 'thriller.wav'); save('A_v3_current', st[int(18.8 * rate):int(27.8 * rate)].copy())

# B: a REAL air-raid siren, re-pitched onto the three notes, off the hills (a machine, not a voice)
b = np.zeros((L, 2), np.float32); src = rec('siren_airraid', 0.0, 5.0, 120, 7000)
for i, (t, m) in enumerate(zip(T, NOTES)):
    a = stretch(src, 2 ** ((61 - m) / 12)); a = a[:int((1.4 if i < 2 else 3.2) * rate)]
    a = clip_fade(a, .08, .5 if i == 2 else .2); put(b, hills(a, lp=2600), t, 0.9); put(b, sub(t), t, 0.5)
save('B_real_airraid_pitched', b)

# C: GIANT - an octave lower, slow wind-up, heavy drive, the last note falls two octaves like something dying
c = np.zeros((L, 2), np.float32)
for i, (t, m) in enumerate(zip(T, NOTES)):
    last = i == 2
    s = siren(mtof(m - 12), 3.8 if last else 1.4, up=0.55, down=3.0 if last else 0.35, drop=0.25 if last else 0.92, voice='aa', drive=9.0, seed=30 + i)
    put(c, hills(s, taps=((0.55, 0.55), (1.2, 0.38), (2.1, 0.24), (3.2, 0.14)), lp=2200), t - 0.15, 1.0); put(c, sub(t, 1.6, 36), t, 0.8)
save('C_giant_dying', c)

# D: GHOST CHOIR - three sung siren voices per note (aa / oo / ee, detuned), no harsh drive, a long hall, breath underneath
d = np.zeros((L, 2), np.float32)
for i, (t, m) in enumerate(zip(T, NOTES)):
    for j, (v, cents) in enumerate((('aa', 0), ('oo', -14), ('ee', 11))):
        s = siren(mtof(m + cents / 100.0), 2.6 if i == 2 else 1.5, up=0.35, down=0.6, drop=0.86, voice=v, drive=1.6, seed=40 + 3 * i + j)
        put(d, hills(s, taps=((0.3, 0.6), (0.8, 0.45), (1.5, 0.3), (2.4, 0.2)), lp=3000), t + 0.03 * j, 0.55)
put(d, rec('breath_scared', 0.2, 6.0, 300, 9000), 0.2, 0.25)
save('D_ghost_choir', d)

# E: BROKEN LOUDSPEAKER - the cute town chime played through a dying PA: bit-crush, drop-outs, tape wobble, feedback squeal
from mix_ep1 import MAR, note
e = np.zeros((L, 2), np.float32); r = np.random.default_rng(5)
for i, (t, m) in enumerate(zip(T, (66, 70, 73))):
    a = band(note(MAR, m, .48, 1.3), 500, 3200); n = len(a); tt = np.arange(n) / rate
    a = np.interp(np.arange(n) * (1 - 0.03 * np.sin(2 * np.pi * 0.9 * tt) - 0.06 * tt / tt[-1] * (i == 2)), np.arange(n), a[:, 0])
    a = np.round(a * 9) / 9; a = np.tanh(4 * a); mask = (r.random(n // 600 + 1) > 0.12).repeat(600)[:n]; a *= mask
    put(e, hills(np.stack([a, a], 1).astype(np.float32), lp=2400), t, 0.8)
fb = np.sin(2 * np.pi * np.cumsum(np.linspace(2400, 3900, int(1.6 * rate))) / rate) * np.linspace(0, 1, int(1.6 * rate)) ** 3
put(e, np.stack([fb, fb], 1).astype(np.float32), 5.6, 0.18); put(e, rec('screech_muffled', 0, 2.5, 200, 8000), 6.9, 0.5)
save('E_broken_loudspeaker', e)

# F: REVERSED - each note is sucked in backwards, then hits; the tail is a metal screech
f_ = np.zeros((L, 2), np.float32)
for i, (t, m) in enumerate(zip([x + 1.0 for x in T], NOTES)):
    s = siren(mtof(m), 1.3, up=0.2, down=0.3, drop=0.9, voice='oo', drive=4.0, seed=60 + i)
    rv = hills(s, lp=3000)[::-1][-int(1.2 * rate):] * np.linspace(0, 1, int(1.2 * rate))[:, None] ** 2
    put(f_, rv, t - 1.2, 0.8); put(f_, s, t, 0.7); put(f_, sub(t), t, 0.6)
put(f_, rec('screech_metal', 7.6, 9.6, 300, 10000), 3.7, 0.45)
save('F_reversed_suck_in', f_)

# G: HAND-CRANK - a real mechanical hand-cranked siren, slowed 30 % (deeper, laboured), three wind-ups, a sub under each
g = np.zeros((L, 2), np.float32); hc = rec('siren_handcrank', 2.0, 9.0, 60, 9000); hc = stretch(hc, 1.42)
for i, t in enumerate(T):
    seg = clip_fade(hc[int(i * 2.0 * rate):int((i * 2.0 + (1.6 if i < 2 else 3.4)) * rate)], .1, .5)
    put(g, hills(seg, lp=2800), t, 0.9); put(g, sub(t, 1.4, 40), t, 0.5)
save('G_handcrank_slowed', g)

# H: CREATURE PA - B (real siren) and C (giant voice) together: a machine that has a throat
save('H_machine_with_a_throat', b / (np.max(np.abs(b)) + 1e-9) * 0.7 + c / (np.max(np.abs(c)) + 1e-9) * 0.6)
