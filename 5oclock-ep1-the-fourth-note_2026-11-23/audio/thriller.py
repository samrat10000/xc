"""5 O'CLOCK Ep1 v3 - thriller sound design (Sam v2 note: "the three sounds from the siren should be thrilling... like an evil
spirit... make it thriller"). An original design, not any existing character's sound: the town loudspeaker's chime notes
become a living PA siren - a vocal, formant-filtered siren voice that winds up onto each note, distorts through a horn speaker
and echoes off the hills - layered over real CC0 siren / screech / boom recordings from Openverse (recordings/openverse).
render() returns a (length, 2) stem on the 63 s timeline; mix_ep1.py adds it (gated by the hard-cut silence)."""
import numpy as np
from scipy import signal
from pathlib import Path
from lib_mix import read, take, place, band, filter_, peak, clip_fade, rate, length

OV = Path(__file__).resolve().parent / 'recordings' / 'openverse'
mtof = lambda m: 440.0 * 2 ** ((m - 69) / 12)
FORM = {'oo': ((330, 1.0), (760, 0.45), (2500, 0.18)), 'aa': ((720, 1.0), (1150, 0.6), (2600, 0.3)), 'ee': ((300, 0.8), (2250, 0.55), (3000, 0.3))}


def _ease(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)


def siren(f0, dur, up=0.28, down=0.40, drop=0.80, voice='oo', drive=3.0, seed=0):
    """a siren that sings: winds up from 0.62 f0, holds with a slow wobble, groans down to drop*f0; vocal formants; horn; drive"""
    n = int(dur * rate); t = np.arange(n) / rate; r = np.random.default_rng(seed)
    f = f0 * (0.62 + 0.38 * _ease(t / up))
    f *= 1 + 0.007 * np.sin(2 * np.pi * 5.3 * t + r.uniform(0, 6)) + 0.004 * np.sin(2 * np.pi * 0.7 * t)
    f *= 1 - (1 - drop) * _ease((t - (dur - down)) / down)
    out = np.zeros(n, np.float32)
    for mult, g in ((1.0, 1.0), (0.5, 0.40), (1.0065, 0.6), (2.003, 0.25)):      # the note, an octave under, two beating detunes
        ph = 2 * np.pi * np.cumsum(f * mult) / rate
        for k in range(1, 30):
            if k * f0 * mult > 15000: break
            out += (g / k ** 0.85) * np.sin(k * ph).astype(np.float32)
    v = np.zeros_like(out)
    for fc, g in FORM[voice]:                                                     # it sings a vowel: no machine does that
        v += g * signal.sosfilt(signal.butter(2, (fc * 0.8, fc * 1.25), 'bandpass', fs=rate, output='sos'), out)
    v = np.tanh(drive * v / (np.max(np.abs(v)) + 1e-9)) / np.tanh(drive)
    v = band(v, 200, 4300)                                                        # horn loudspeaker
    env = _ease(t / min(up, 0.25)) * (1 - _ease((t - (dur - 0.12)) / 0.12))
    v = v * env
    st = np.stack([v, np.roll(v, int(0.011 * rate))], 1).astype(np.float32)
    return st


def hills(x, taps=((0.42, 0.50), (0.95, 0.33), (1.70, 0.21), (2.60, 0.12)), lp=3200):
    """loudspeaker echo off the hills: each return later, darker, quieter, a little wider"""
    out = np.pad(x, ((0, int(3.2 * rate)), (0, 0)))
    for i, (d, g) in enumerate(taps):
        e = filter_(x, lp / (1.6 ** i), 'lowpass') * g; k = int(d * rate); out[k:k + len(e)] += e[:, ::-1] if i % 2 else e
    return out


def rec(name, s, e, lo=40, hi=12000):
    return clip_fade(band(take(read(OV / f'{name}.mp3'), s, e), lo, hi), .02, .15)


def render():
    out = np.zeros((length, 2), np.float32)
    notes = (66 - 12, 70 - 12, 73 - 12)                                           # the series chime, an octave down: weight
    # --- 07 (19.2-21.2 s): the three notes, sung by the town's loudspeakers ---
    rs = rec('whoosh_back', 0, 1.2, 80, 9000)                                     # air sucked in before the first note
    place(out, peak(rs, -8), 19.21 - len(rs) / rate + 0.03, 0.55)
    # v4 (Sam picked candidate I "broadcast wail"): three deafening, overdriven air-raid wails, each lower; static bursts; a rumble
    from siren_candidates2 import wail, static, rumble
    place(out, peak(rumble(5.4), -4), 18.9, 0.45)
    for i, t in enumerate((19.21, 20.21, 21.21)):
        last = i == 2
        w = wail('siren_airraid', 0.5 + 6 * i, 3.2 if last else 1.15, -3 - 2 * i, 6.0)
        place(out, peak(hills(w, lp=2600), -3), t - 0.04, 0.62, -0.12 + 0.12 * i)
        if not last: place(out, peak(static(0.18, 0.35), -10), t + 0.98, 0.5)
    place(out, peak(static(0.6, 0.35), -8), 24.3, 0.5)                            # the speakers crackle out
    # --- 21.5-28.4: the dread bed under the frozen town, swelling, then CUT at the dead battery (28.45) ---
    bed = rec('drone_dark', 20, 27.5, 30, 6000) * 0.8 + rec('wind_howl', 3, 10.5, 200, 5000) * 0.5
    n = min(len(bed), int((28.45 - 21.0) * rate)); bed = bed[:n] * np.linspace(0.15, 1.0, n)[:, None] ** 1.6
    place(out, peak(bed, -12), 21.0, 1.0)
    # --- 33.5-48.4: the mirror walk: low drone + a heartbeat that speeds up toward the Listener ---
    bed2 = rec('drone_horror', 5, 20.0, 25, 4000)
    n = min(len(bed2), int((48.45 - 33.5) * rate)); bed2 = bed2[:n] * np.linspace(0.25, 1.0, n)[:, None] ** 1.3
    place(out, peak(bed2, -14), 33.5, 1.0)
    t, gap = 41.6, 1.25
    while t < 45.9:
        b = np.sin(2 * np.pi * 52 * np.arange(int(0.22 * rate)) / rate) * np.exp(-np.arange(int(0.22 * rate)) / rate / 0.06)
        b2 = np.concatenate([b, np.zeros(int(0.17 * rate)), b * 0.6])                # lub-dub
        place(out, np.stack([b2, b2], 1).astype(np.float32), t, 0.22 + 0.12 * (t - 41.6) / 4.3)
        t += gap; gap = max(0.78, gap * 0.92)
    # --- 46.6: the fourth note, from INSIDE the mirrors: lower, wrong vowel, reversed swell into it, a breath ---
    s4 = siren(mtof(78 - 24), 1.9, up=0.35, down=1.1, drop=0.7, voice='ee', drive=5.0, seed=4)
    rev = s4[::-1][:int(0.9 * rate)] * np.linspace(0, 1, int(0.9 * rate))[:, None] ** 2
    place(out, peak(rev, -10), 46.62 - 0.9, 0.35)
    place(out, peak(hills(band(s4, 350, 2800), lp=2200), -6), 46.62, 0.45)
    place(out, peak(rec('breath_scared', 0.2, 2.5, 300, 9000), -10), 46.1, 0.22, 0.3)
    # --- 48.5-49.0: the Listener. Every siren at once, an octave below, screaming metal, a boom; then true silence ---
    roar = siren(mtof(42), 0.50, up=0.08, down=0.2, drop=0.85, voice='aa', drive=8.0, seed=9) + 0.6 * siren(mtof(49), 0.50, up=0.06, down=0.2, drop=0.8, voice='ee', drive=8.0, seed=10)
    place(out, peak(roar, -2), 48.50, 0.30)
    from lib_mix import stretch
    beast = stretch(rec('siren_civildef', 10.8, 12.0, 150, 6000), 2.0)[:int(0.5 * rate)]       # a real siren an octave down: a throat
    beast = np.tanh(4 * beast / (np.max(np.abs(beast)) + 1e-9)); beast[-int(.03 * rate):] *= np.linspace(1, 0, int(.03 * rate))[:, None]
    place(out, peak(beast.astype(np.float32), -2), 48.50, 0.50)
    sc_ = stretch(rec('screech_metal', 7.6, 7.95, 300, 12000), 1.45)[:int(0.5 * rate)]
    place(out, peak(sc_, -4), 48.50, 0.30)
    place(out, peak(rec('screech_metal', 7.6, 8.1, 300, 10000), -4), 48.50, 0.35)
    place(out, peak(rec('riser_hit44', 0, 0.5, 25, 8000), -2), 48.50, 0.40)
    # v4 (Sam: "a significant cut of music between 48 and 49 s"): the same broadcast wail as the three notes (it IS the song,
    # grown huge), and it never stops dead - it decays into the hills and a long rumble under the narrator
    w = wail('siren_airraid', 0.5, 4.5, -7, 7.0); n = len(w); env = np.ones(n, np.float32)
    k0 = int(0.5 * rate); env[k0:] = np.exp(-np.arange(n - k0) / rate / 0.9)                  # loud for 0.5 s, then dies away
    place(out, peak(hills(w * env[:, None], taps=((0.6, 0.55), (1.3, 0.4), (2.2, 0.28), (2.9, 0.18)), lp=2000), -2), 48.50, 0.60)
    place(out, peak(rumble(6.0, 30), -4), 48.40, 0.55)
    # --- after the silence (49.62-53): the hand in the sky. A far groan under the narrator, the hills answering ---
    g = siren(mtof(37), 3.6, up=1.2, down=1.8, drop=0.6, voice='oo', drive=2.0, seed=12)
    place(out, peak(hills(filter_(g, 900, 'lowpass'), lp=900), -10), 49.65, 0.35)
    # --- v4 (Sam: "Mirror-Sam should say some chant, some evil mantra, through which the glass cracks"): his own words
    # "Your turn" become the mantra - forward, reversed, an octave down, whispered on top of each other, faster and faster,
    # building from 45.9 s to the crack at 48.5. Heard again, faint, under the town's "Okaeri, Sam" (54-56 s).
    from lib_mix import stretch as _st
    HERE_ = Path(__file__).resolve().parent
    m1 = read(HERE_ / 'M1_takeA.mp3'); nz = np.flatnonzero(np.abs(m1).max(1) > 0.02 * np.abs(m1).max()); m1 = clip_fade(m1[nz[0]:nz[-1]], .01, .05)
    word = band(m1, 120, 7000)
    t, step, k = 45.9, 0.62, 0
    chant = np.zeros((length, 2), np.float32)
    while t < 48.45:
        v = [word, word[::-1], _st(word, 2 ** (7 / 12)), _st(word[::-1], 2 ** (12 / 12))][k % 4]
        place(chant, peak(v, -6), t, 0.18 + 0.30 * (t - 45.9) / 2.55, (-0.3, 0.3)[k % 2])
        t += step; step = max(0.22, step * 0.82); k += 1
    chant = hills(chant[int(45.8 * rate):int(48.6 * rate)], taps=((0.09, 0.5), (0.21, 0.35), (0.37, 0.25)), lp=5000)
    place(out, chant, 45.8, 1.0)
    low = _st(word[::-1], 2.0)                                                     # an octave down, reversed: the town answering
    for j, tt in enumerate((54.2, 55.0)): place(out, peak(filter_(low, 1500, 'lowpass'), -10), tt, 0.20, (-0.4, 0.4)[j])
    # --- 40 s (shot 12 whip to the street): he sees them all frozen - his own unsure "...Hello?" again, smaller ---
    s1 = read(HERE_ / 'S1_takeB.mp3')
    if len(s1): place(out, peak(band(s1, 100, 9000), -3), 39.70, 0.55)
    # --- 18 (61.3-62.2): three notes again, far away now; the third cuts off mid-wind-up. Then nothing. ---
    for i, (t, m) in enumerate(zip((61.3, 61.75, 62.2), notes)):
        s = siren(mtof(m), 0.8, up=0.2, down=0.2, drop=0.95, voice='oo', drive=2.5, seed=20 + i)
        s = filter_(s, 1800, 'lowpass')
        if i == 2: s = s[:int(0.32 * rate)]; s[-200:] *= np.linspace(1, 0, 200)[:, None]
        place(out, peak(hills(s, lp=1500) if i < 2 else s, -10), t, 0.30)
    return out


if __name__ == '__main__':
    from lib_mix import wav
    wav(Path(__file__).resolve().parent / 'stems' / 'thriller.wav', render()); print('thriller stem written')


