"""Estimate the fundamental of sample files (harmonic product spectrum) vs the note in their name. usage: python -I check_pitch.py <files...>"""
import re, sys, wave
import numpy as np

NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def load(p):
    with wave.open(p) as w:
        n, ch, sw, sr = w.getnframes(), w.getnchannels(), w.getsampwidth(), w.getframerate()
        b = w.readframes(n)
    if sw == 3:
        a = np.frombuffer(b, np.uint8).reshape(-1, 3); a = (a[:, 0].astype(np.int32) | (a[:, 1].astype(np.int32) << 8) | (a[:, 2].astype(np.int32) << 16))
        a = np.where(a >= 1 << 23, a - (1 << 24), a).astype(np.float32) / (1 << 23)
    else: a = np.frombuffer(b, '<i2').astype(np.float32) / 32768
    return a.reshape(-1, ch).mean(1), sr


for p in sys.argv[1:]:
    a, sr = load(p); k = np.argmax(np.abs(a)); seg = a[k + int(.08 * sr): k + int(.08 * sr) + 16384]
    sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), 65536)); hps = sp.copy()
    for h in (2, 3): hps[: len(sp) // h] *= sp[::h][: len(sp) // h]
    f = np.argmax(hps[int(25 * 65536 / sr): int(2000 * 65536 / sr)]) + int(25 * 65536 / sr); f0 = f * sr / 65536
    midi = 69 + 12 * np.log2(f0 / 440)
    m = re.search(r'_([A-G])(#?)(\d)', p.replace('\\', '/').split('/')[-1]); nm = None
    if m: nm = 12 * (int(m.group(3)) + 1) + NAMES[m.group(1)] + (1 if m.group(2) else 0)
    print('%-34s f0 %7.1f Hz  midi %5.1f  name-midi %s' % (p.replace('\\', '/').split('/')[-1], f0, midi, nm))
