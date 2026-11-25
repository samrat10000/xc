"""5 O'CLOCK series theme "The Fourth Note" (Claude, 2026-11-24). One signature cue for every episode, built only from recorded
instruments (VSCO 2 CE, CC0; samples/ via get_samples.py). Writes ../stems/*.wav (48 kHz stereo) + ../theme_cues.json.

Idea: the Kiriyama chime is three notes, F#-A#-C# (major, innocent, the town). Where the fourth note should come the music turns
minor and a 3+3+2 cello ostinato starts driving. The melody keeps landing on G - one semitone above home (flat 2, Phrygian dread).
Climax: everything hits a G major chord over the F# bass, then a hard cut to silence, and a lone tubular bell rings the 'fourth
note' - G, not the F# you expect. 92 BPM, F# minor. Cues: full (~33 s), intro (5.2 s), bed (ostinato loop, 10.43 s), sting (6 s).
usage: python -I theme.py"""
import json, re, subprocess, functools
from fractions import Fraction
from pathlib import Path
import numpy as np
from scipy import signal

ROOT = Path(__file__).resolve().parents[1]; SM = ROOT / 'samples'; OUT = ROOT / 'stems'; OUT.mkdir(exist_ok=True)
SR = 48000; BPM = 92.0; Q = 60 / BPM; E8 = Q / 2; BAR = 4 * Q
NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


@functools.lru_cache(maxsize=200)
def read(path):
    b = subprocess.check_output(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', str(path), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'])
    return np.frombuffer(b, '<f4').reshape(-1, 2).copy()


def bank(folder, shift):
    """{midi: path}; VSCO strings name notes with C3 = middle C, so their real pitch is name + 12 (measured: check_pitch.py)"""
    out = {}
    for p in sorted((SM / folder).glob('*.wav')):
        m = re.search(r'_([A-G])(#?)(\d)_', p.name + '_')
        if m: out[12 * (int(m.group(3)) + 1) + NAMES[m.group(1)] + (1 if m.group(2) else 0) + shift] = p
    return out


CSPIC, CSUS, CTREM = bank('cello_spic', 12), bank('cello_sus', 12), bank('cello_trem', 12)
VSUS, VTREM, VSPIC = bank('vln_sus', 12), bank('vln_trem', 12), bank('vln_spic', 12)
BASS, HARP = bank('bass_sus', 12), bank('harp', 0)
# tubular bells: names are standard (C4 = 60); measured strike partials 2:3:4 confirm it
TB = {60: SM / 'perc' / 'TB_hit_C4_v4_rr1.wav', 67: SM / 'perc' / 'TB_hit_G4_v4_rr1.wav', 72: SM / 'perc' / 'TB_hit_C5_v4_rr1.wav', 77: SM / 'perc' / 'TB_hit_F5_v3_rr1.wav'}


def bank_std(folder):                                             # marimba/glock: standard names, as in the episode chime
    out = {}
    for p in sorted((SM / folder).glob('*.wav')):
        m = re.search(r'_([A-G])(#?)(\d)[_.]', p.name)
        if m: out[12 * (int(m.group(3)) + 1) + NAMES[m.group(1)] + (1 if m.group(2) else 0)] = p
    return out


MAR, GLK = bank_std('marimba'), bank_std('glock')
P = lambda n: SM / 'perc' / n
T_ = lambda n: SM / 'timp' / n


def resample(a, ratio):
    r = Fraction(ratio).limit_denominator(400)
    return signal.resample_poly(a, r.denominator, r.numerator, axis=0).astype(np.float32)   # ratio > 1 = higher pitch, shorter


def note(bk, midi, dur, rel=0.35, att=0.004, start=0.0):
    key = min(bk, key=lambda k: abs(k - midi)); a = read(bk[key])
    a = a[int(start * SR):]
    a = resample(a, 2 ** ((midi - key) / 12))[: int((dur + rel) * SR)].copy()
    n = len(a); t = np.arange(n) / SR
    env = np.clip(t / max(att, 1e-4), 0, 1) * np.where(t > dur, np.exp(-(t - dur) / max(rel / 3, 0.01)), 1.0)
    return a * env[:, None].astype(np.float32)


def hit(path, gain=1.0, lp=None, hp=None, pitch=0.0):
    a = read(path)
    if pitch: a = resample(a, 2 ** (pitch / 12))
    if lp: a = signal.sosfilt(signal.butter(2, lp, 'lowpass', fs=SR, output='sos'), a, axis=0).astype(np.float32)
    if hp: a = signal.sosfilt(signal.butter(2, hp, 'highpass', fs=SR, output='sos'), a, axis=0).astype(np.float32)
    return a * gain


def place(tr, a, t, g=1.0, pan=0.0):
    k = int(round(t * SR))
    if k < 0: a = a[-k:]; k = 0
    n = min(len(a), len(tr) - k)
    if n <= 0: return
    pv = np.array([min(1, 1 - pan), min(1, 1 + pan)], np.float32)
    tr[k:k + n] += a[:n] * g * pv


def reverb(x, secs=2.6, wet=0.28, pre=0.018):
    rng = np.random.default_rng(5); n = int(secs * SR); t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)).astype(np.float32) * np.exp(-t / (secs / 6.9))[:, None]
    ir = signal.sosfilt(signal.butter(1, 5200, 'lowpass', fs=SR, output='sos'), ir, axis=0)
    ir = np.vstack([np.zeros((int(pre * SR), 2), np.float32), ir]); ir /= np.sqrt((ir ** 2).sum(0))
    w = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return (x * (1 - wet) + w * wet * 1.6).astype(np.float32)


def bar(b, beat=0.0): return (b - 1) * BAR + beat * Q          # bars count from 1


def compose(L):
    S = {k: np.zeros((int(L * SR), 2), np.float32) for k in ('bells', 'strings', 'ostinato', 'perc', 'low')}
    # --- bars 1-2: the chime (three notes, the fourth missing); the drone and a cymbal swell rise out of the gap
    for i, m in enumerate((66, 70, 73)):
        place(S['bells'], note(TB, m, 3.2, 1.4), 0.15 + i * 0.98, 0.55, -0.2 + 0.2 * i)
        place(S['bells'], note(HARP, m + 12, 0.6, 1.6), 0.15 + i * 0.98, 0.20, 0.25 - 0.2 * i)
        place(S['bells'], note(MAR, m, 0.48, 1.3), 0.15 + i * 0.98, 0.42, -0.18 + 0.12 * i)          # the town chime itself
        place(S['bells'], note(GLK, m + 12, 0.22, 1.17), 0.15 + i * 0.98, 0.15, -0.18 + 0.12 * i)
    place(S['low'], note(BASS, 42, 4.0, 1.0, att=1.6), 1.6, 0.40)                          # F#2 contrabass drone
    place(S['low'], note(CSUS, 30 + 12, 3.0, 0.8, att=1.2), 2.4, 0.18)
    cr = hit(P('susCymb1-cresc-Median_v1.wav'), hp=300); place(S['perc'], cr, bar(3) - len(cr) / SR + 0.05, 0.35)
    # --- bars 3-10: the ostinato, 3+3+2 eighths, accents on 0/3/6; roots F# F# D E | F# F# D C#
    roots = {3: 42, 4: 42, 5: 38, 6: 40, 7: 42, 8: 42, 9: 38, 10: 37}
    for b, rt in roots.items():
        for e in range(8):
            acc = e in (0, 3, 6); g = (0.95 if acc else 0.42) * (1.0 if b < 7 else 1.15)
            m = rt + (12 if e in (5, 7) and b >= 7 else 0)                              # octave leaps once the melody is in
            place(S['ostinato'], note(CSPIC, m, 0.16, 0.12), bar(b) + e * E8, g * 0.55, -0.15)
            if b >= 5: place(S['ostinato'], note(VSPIC, m + 24, 0.12, 0.10), bar(b) + e * E8 + 0.006, g * 0.22, 0.30)
        place(S['perc'], hit(P('BDrumNewhit_v7_rr%d_Sum.wav' % (1 + b % 2)), lp=900), bar(b), 0.55)
        place(S['perc'], hit(T_('Timpani2_Hit_v4_rr1_Sum.wav'), lp=1800), bar(b) + 3 * E8, 0.45)
        if b >= 7: place(S['perc'], hit(T_('Timpani4_Hit_v3_rr1_Sum.wav'), lp=1800), bar(b) + 6 * E8, 0.38)
        place(S['low'], note(BASS, rt, BAR - 0.05, 0.3, att=0.03), bar(b), 0.30)
    for b, m in ((3, 73), (4, 73), (5, 74), (6, 76)):                                       # violins tremolo: tension rising
        place(S['strings'], note(VTREM, m, BAR, 0.4, att=0.9 if b == 3 else 0.05), bar(b), 0.16 + 0.03 * (b - 3), 0.1)
    for b in (10,):
        for k in range(4): place(S['perc'], hit(T_('Timpani5_Hit_v4_rr1_Sum.wav'), lp=1800), bar(b) + k * Q, 0.30 + 0.08 * k)
    cr = hit(P('susCymb1-cresc-Long_v1.wav'), hp=250); place(S['perc'], cr, bar(11) - len(cr) / SR + 0.03, 0.40)
    # --- bars 7-10: the theme. F#5 A5 C#6 | G5 (the wrong note) F#5 | E5 F#5 A5 | G#5 G5 C#5
    mel = [(7, 0, 78, 2), (7, 2, 81, 1), (7, 3, 85, 1), (8, 0, 79, 3), (8, 3, 78, 1),
           (9, 0, 76, 1), (9, 1, 78, 1), (9, 2, 81, 2), (10, 0, 80, 1), (10, 1, 79, 1), (10, 2, 73, 2)]
    for b, bt, m, d in mel:
        t = bar(b, bt); dur = d * Q - 0.03
        place(S['strings'], note(VSUS, m, dur, 0.5, att=0.05), t, 0.42, 0.12)
        place(S['strings'], note(CSUS, m - 24, dur, 0.5, att=0.06), t, 0.30, -0.18)
        place(S['bells'], note(HARP, m - 12, 0.3, 1.2), t, 0.16, 0.3)
        if bt == 0: place(S['bells'], note(TB, m - 12, 2.0, 1.0), t, 0.22, -0.25)
    # --- bar 11: the hit - G major over the F# bass, everything at once; then a hard cut
    T = bar(11); HOLD = 1.45
    for m, g, bk in ((30, 0.55, BASS), (42, 0.45, CSUS), (49, 0.35, CSUS), (79, 0.40, VSUS), (83, 0.36, VSUS), (86, 0.30, VSUS), (67, 0.32, VSUS)):
        place(S['strings'], note(bk, m, HOLD, 0.06, att=0.012), T, g)
    for p_, g, lp in (('gongHit_fff.wav', 0.75, None), ('BDrumNewhit_v7_rr1_Sum.wav', 0.9, 900), ('../timp/Timpani1_Hit_v3_rr1_Sum.wav', 0.7, 2000),
                      ('cymbal-crash1_ff_rr1.wav', 0.45, None), ('Anvil_Hit1_v3_Sum.wav', 0.22, None)):
        a = hit(P(p_), lp=lp)[: int((HOLD + 0.06) * SR)]
        a[-int(0.06 * SR):] *= np.linspace(1, 0, int(0.06 * SR))[:, None]; place(S['perc'], a, T, g)
    place(S['bells'], note(TB, 66, HOLD, 0.06), T, 0.35)
    # --- bar 12: silence, then the fourth note - G - alone, ringing into nothing
    TE = T + HOLD + 0.62
    place(S['bells'], note(TB, 67, 4.5, 2.5), TE, 0.75)                     # G4 bell at its own pitch: the clean strike note
    place(S['bells'], note(HARP, 91, 0.5, 3.0), TE + 0.004, 0.12, 0.3)
    place(S['bells'], note(MAR, 79, 0.48, 1.6), TE, 0.40); place(S['bells'], note(GLK, 91, 0.22, 1.4), TE, 0.14)
    place(S['low'], hit(P('gongHit_f.wav'), lp=420), TE, 0.25)
    return S, dict(bpm=BPM, bar=BAR, intro=(0, bar(3)), bed=(bar(3), bar(7)), theme=(bar(7), bar(11)), hit=T, cut=T + HOLD, fourth_note=TE)


def master(S):
    wet = {'bells': 0.42, 'strings': 0.32, 'ostinato': 0.16, 'perc': 0.20, 'low': 0.14}
    mix = sum(reverb(S[k], 2.8 if k == 'bells' else 2.2, w) for k, w in wet.items())
    mix = mix / (np.abs(mix).max() + 1e-9) * 0.89
    return mix.astype(np.float32), {k: reverb(S[k], 2.6, wet[k]) for k in S}


def wav(path, a):
    import wave
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((np.clip(a, -1, 1) * 32767).astype('<i2').tobytes())


def main():
    L = bar(13) + 5.5
    S, cues = compose(L); mix, stems = master(S)
    end = int((cues['fourth_note'] + 6.5) * SR); mix = mix[:end]
    c0, c1 = int((cues['cut'] + 0.01) * SR), int((cues['fourth_note'] - 0.004) * SR); fd = int(0.045 * SR)
    gate = np.ones(len(mix), np.float32); gate[c0:c0 + fd] = np.linspace(1, 0, fd); gate[c0 + fd:c1] = 0.0   # the hard cut: true silence
    mix = mix * gate[:, None]
    for k in stems: stems[k][:len(gate)] *= gate[:, None]
    wav(OUT / 'theme_full.wav', mix)
    for k, a in stems.items(): wav(OUT / f'stem_{k}.wav', a[:end] / (np.abs(mix).max() + 1e-9) * 0.89)
    cut = lambda a, b: mix[int(a * SR):int(b * SR)]
    wav(OUT / 'theme_intro.wav', cut(0, cues['bed'][0] + 1.2))
    bed = cut(*cues['bed']); xf = int(0.08 * SR); bed[:xf] *= np.linspace(0, 1, xf)[:, None]; wav(OUT / 'theme_bed_loop.wav', bed)
    wav(OUT / 'theme_sting.wav', cut(cues['hit'] - 0.05, cues['fourth_note'] + 6.0))
    rms = 20 * np.log10(np.sqrt((mix ** 2).mean()) + 1e-9)
    (ROOT / 'theme_cues.json').write_text(json.dumps(dict(cues={k: (list(v) if isinstance(v, tuple) else v) for k, v in cues.items()},
        length=len(mix) / SR, rms_db=round(float(rms), 1)), indent=2), encoding='utf-8')
    print('theme %.1f s, rms %.1f dB' % (len(mix) / SR, rms), cues)


if __name__ == '__main__':
    main()
