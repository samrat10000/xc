"""Siren candidates, round 2 (Sam: "very similar to the siren-head siren"). An ORIGINAL design in that genre - a deafening, distorted
air-raid siren with garbled emergency-radio voice fragments, static and a deep rumble - built only from our CC0 recordings
(recordings/openverse) and our own ElevenLabs takes. No audio from any existing character is used.
Writes audio/siren_candidates/I_*.wav .. L_*.wav. usage: python -E -s siren_candidates2.py"""
import numpy as np
from pathlib import Path
from scipy import signal
from lib_mix import read, take, band, filter_, peak, clip_fade, stretch, wav, rate
from thriller import hills, rec

HERE = Path(__file__).resolve().parent; OUT = HERE / 'siren_candidates'
L = int(10.0 * rate); rng = np.random.default_rng(11)


def put(buf, a, t, g=1.0):
    k = int(t * rate)
    if k < 0: a = a[-k:]; k = 0
    n = min(len(a), len(buf) - k)
    if n > 0: buf[k:k + n] += a[:n] * g


def st(x): return np.stack([x, x], 1).astype(np.float32)


def radio(a, lo=450, hi=2800, crush=7, drive=6.0):
    """through a broken emergency radio: narrow band, bit-crushed, overdriven, with crackle"""
    x = band(a, lo, hi)[:, 0]; x = x / (np.max(np.abs(x)) + 1e-9)
    x = np.round(x * crush) / crush; x = np.tanh(drive * x)
    crack = (rng.random(len(x)) > 0.9985) * rng.uniform(-1, 1, len(x)) * 0.8
    return st(x * 0.8 + crack)


def static(dur, g=0.5):
    n = int(dur * rate); s = band(st(rng.standard_normal(n).astype(np.float32)), 900, 6000)[:, 0]
    gate = (signal.sosfilt(signal.butter(1, 6, fs=rate, output='sos'), rng.random(n)) > 0.5).astype(np.float32)
    return st(s * (0.3 + 0.7 * gate) * g)


def rumble(dur, f=33):
    t = np.arange(int(dur * rate)) / rate
    s = np.sin(2 * np.pi * f * t + 0.6 * np.sin(2 * np.pi * 0.3 * t)) * np.minimum(1, t / 1.2) * np.minimum(1, (dur - t) / 1.0)
    return st(s * 0.9)


def wail(src, s0, dur, semis=-3, drive=5.0):
    """a real siren, lowered, overdriven to the edge of breaking (a loudspeaker pushed past its limit)"""
    a = stretch(rec(src, s0, s0 + dur * 2 ** (semis / 12) + 0.2, 90, 9000), 2 ** (-semis / 12))[:int(dur * rate)]
    x = a / (np.max(np.abs(a)) + 1e-9); x = np.tanh(drive * x) / np.tanh(drive)
    return band(clip_fade(x.astype(np.float32), 0.15, 0.6), 110, 6500)


def voice_bits(n=6, semis=-7):
    """garbled broadcast words: short chops of our own takes (narrator + Mirror-Sam), pitched down, reversed at random"""
    takes = [read(HERE / f) for f in ('N3_takeA.mp3', 'M1_takeA.mp3', 'N1_takeA.mp3') if (HERE / f).exists()]
    out = []
    for i in range(n):
        a = takes[i % len(takes)]; s0 = rng.uniform(0.2, max(0.3, len(a) / rate - 0.8)); seg = a[int(s0 * rate):int((s0 + rng.uniform(0.25, 0.6)) * rate)]
        seg = stretch(seg, 2 ** (-semis / 12))
        if rng.random() < 0.4: seg = seg[::-1]
        out.append(radio(seg))
    return out


def save(name, buf):
    buf = buf / (np.max(np.abs(buf)) + 1e-9) * 0.89; wav(OUT / f'{name}.wav', buf.astype(np.float32)); print('wrote', name)


if __name__ == '__main__':                                                      # importable: thriller.py uses wail/static/rumble
    T = (0.5, 3.4, 6.3)
    # I: the classic genre sound - three long, deafening, distorted wails; static between; rumble under all
    i_ = np.zeros((L, 2), np.float32); put(i_, rumble(9.6), 0.2, 0.5)
    for k, t in enumerate(T):
        put(i_, hills(wail('siren_airraid', 0.5 + 6 * k, 2.6, -3 - 2 * k, 6.0), lp=2600), t, 1.0)
        put(i_, static(0.6, 0.35), t + 2.5, 1.0)
    save('I_broadcast_wail', i_)
    
    # J: wail + a garbled emergency voice between the calls (the speaker is trying to talk)
    j = np.zeros((L, 2), np.float32); put(j, rumble(9.6), 0.2, 0.45); bits = voice_bits(8)
    for k, t in enumerate(T):
        put(j, hills(wail('siren_civildef', 10.8 + 4 * k, 2.3, -4 - k, 7.0), lp=2400), t, 1.0)
        for m in range(2): put(j, bits[2 * k + m], t + 2.35 + 0.4 * m, 0.55)
    put(j, static(9.5, 0.12), 0.2, 1.0)
    save('J_wail_and_broken_voice', j)
    
    # K: two sirens a minor second apart, an octave down: the sound of something huge breathing through loudspeakers
    kk = np.zeros((L, 2), np.float32); put(kk, rumble(9.6, 29), 0.2, 0.6)
    for k, t in enumerate(T):
        a = wail('siren_airraid', 1.0 + 5 * k, 2.7, -12, 4.0); b_ = wail('siren_airraid', 1.3 + 5 * k, 2.7, -11, 4.0)
        put(kk, hills(a * 0.6 + b_ * 0.6, taps=((0.5, 0.5), (1.1, 0.35), (2.0, 0.22)), lp=1800), t, 1.0)
    save('K_two_sirens_an_octave_down', kk)
    
    # L: the full thing for the climax - K's octave-down sirens + I's wail on top + the broken voice + metal screech
    l = np.zeros((L, 2), np.float32); put(l, rumble(9.6, 31), 0.2, 0.55)
    for k, t in enumerate(T):
        put(l, hills(wail('siren_airraid', 0.5 + 6 * k, 2.6, -3, 6.0), lp=2600), t, 0.75)
        put(l, hills(wail('siren_airraid', 1.0 + 5 * k, 2.7, -12, 4.0), lp=1800), t, 0.7)
        put(l, bits[k], t + 2.4, 0.5)
    put(l, rec('screech_metal', 7.6, 9.6, 300, 10000), 8.0, 0.4)
    save('L_climax_everything', l)
