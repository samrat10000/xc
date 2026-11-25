"""Numbers-only QA of theme_full.wav (no listening tool): RMS per 0.5 s, the silence after the cut, chroma of the melody bars,
clipping, and a spectrogram PNG. usage: python -I check_theme.py"""
import json, wave
from pathlib import Path
import numpy as np
from scipy import signal
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
with wave.open(str(ROOT / 'stems' / 'theme_full.wav')) as w:
    sr = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), '<i2').reshape(-1, 2).astype(np.float32) / 32768
c = json.loads((ROOT / 'theme_cues.json').read_text())['cues']; m = a.mean(1)
blk = int(0.5 * sr); rms = [20 * np.log10(np.sqrt((m[i:i + blk] ** 2).mean()) + 1e-9) for i in range(0, len(m) - blk, blk)]
print('rms per 0.5 s:', ' '.join('%d' % r for r in rms))
print('peak %.3f  clipped samples %d' % (np.abs(a).max(), int((np.abs(a) > 0.999).sum())))
g = m[int((c['cut'] + 0.12) * sr): int((c['fourth_note'] - 0.02) * sr)]
print('gap after the cut: %.0f dB rms' % (20 * np.log10(np.sqrt((g ** 2).mean()) + 1e-9)))
PC = 'C C# D D# E F F# G G# A A# B'.split()


def chroma(t0, t1):
    x = m[int(t0 * sr): int(t1 * sr)]; f, P = signal.welch(x, sr, nperseg=16384)
    ch = np.zeros(12)
    for fi, p in zip(f, P):
        if 60 < fi < 3000: ch[int(round(12 * np.log2(fi / 440) + 69)) % 12] += p
    ch /= ch.max(); return ' '.join('%s:%.2f' % (PC[i], ch[i]) for i in np.argsort(-ch)[:4])


bar = c['bar']
for name, t0 in (('chime', 0.1), ('bed bar3', c['bed'][0]), ('theme bar7', c['theme'][0]), ('theme bar8 (G)', c['theme'][0] + bar), ('hit', c['hit'] + 0.1), ('fourth note', c['fourth_note'] + 0.1)):
    print('%-16s %s' % (name, chroma(t0, t0 + (2.9 if name == 'chime' else 1.2))))
f, t, S = signal.spectrogram(m, sr, nperseg=4096, noverlap=3072)
S = 10 * np.log10(S[(f > 30) & (f < 6000)] + 1e-12); S = np.clip((S - S.max() + 80) / 80, 0, 1)
Image.fromarray((S[::-1] * 255).astype(np.uint8)).resize((1400, 400)).save(ROOT / 'stems' / 'theme_spectrogram.png')
