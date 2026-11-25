"""5 O'CLOCK Ep1 "The Fourth Note" - score, chime, foley and dialogue on the picture-locked 63 s cut. No generated music: recorded
Salamander Grand Piano (CC BY 3.0, A. Holm), VSCO 2 CE marimba/glock (CC0), CC0 foley. Helpers reused from Codex's Ep2 mixer (lib_mix.py).
Dialogue: named ElevenLabs takes from VOICE_SCRIPT.md when present (N1_takeA.mp3 ...); otherwise the mix is scored without voices.
usage: python mix_ep1.py   -> stems/*.wav, premaster.wav, audio_timeline.json"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib_mix as M
from lib_mix import place, echo, note, band, filter_, peak, clip_fade, read, take, curve, wav, rate, length

ROOT = Path(__file__).resolve().parent; REC = ROOT / 'recordings'; OUT = ROOT / 'stems'; OUT.mkdir(exist_ok=True)
# (role, prefix, start, deadline, text) - times from story/5 O'CLOCK Episode 1.html; deadlines = before the next beat
# v2 (real takes): deadlines widened to each take's native length - no line is sped up more than ~5 % (Codex Ep2 lesson:
# a squeezed narrator reads as fast-forward). The next spoken beat is the real limit, not the shot cut.
LINES = [('Narrator', 'N1', 0.4, 5.9, "Every town in Japan plays a song at five o'clock. Ours has four notes."),
         ('Narrator', 'N2', 6.3, 11.6, 'It has played every day since 1964. Nobody ever asked why.'),
         ('Grandma', 'G1', 14.2, 15.6, 'Ears. Quickly.'),
         ('Sam', 'S1', 29.8, 31.9, '...Hello?'),
         ('Grandma', 'G2', 32.4, 34.9, "Don't look at the mirror, Sam."),
         ('Sam', 'S2', 42.45, 44.2, "That's not me."),
         ('Mirror-Sam', 'M1', 44.5, 46.0, 'Your turn.'),
         ('Narrator', 'N3', 49.0, 52.8, 'The fourth note was never ours to play.'),
         ('Town', 'T1', 54.0, 55.9, 'Okaeri, Sam.'),
         ('Sam', 'S3', 57.2, 58.8, 'Mom...?'),
         ('Narrator', 'N4', 59.45, 62.75, 'Rule seven. Never finish the song.')]


def take_file(prefix):
    for L in 'ABCDEFGHIJ':
        p = ROOT / f'{prefix}_take{L}.mp3'
        if p.is_file() and p.stat().st_size: return p
    return None


def voices():
    track = np.zeros((length, 2), np.float32); events = []; missing = []
    for role, prefix, t, dl, words in LINES:
        if role == 'Town':                                                  # unison: every take layered, 10-40 ms offsets
            takes = [ROOT / f'T1_take{L}.mp3' for L in 'ABCDEFGHIJ' if (ROOT / f'T1_take{L}.mp3').is_file()]
            if not takes: missing.append(prefix); continue
            mix_ = None
            for i, p in enumerate(takes):
                a = M.trim(read(p).mean(axis=1)); a = np.pad(a, (int(rate * 0.012 * i), 0))
                mix_ = a if mix_ is None else np.pad(mix_, (0, max(0, len(a) - len(mix_))))[:max(len(a), len(mix_))] + np.pad(a, (0, max(0, len(mix_) - len(a))))
            a = M.compress_to_fit(mix_ / len(takes) ** 0.5, round((dl - t) * rate), 99)
            a = peak(M.norm(clip_fade(band(a, 110, 6500), .02, .08), -20), -6); place(track, a, t)
            events.append(dict(role=role, start=t, end=round(t + len(a) / rate, 3), deadline=dl, text=words, takes=len(takes))); continue
        p = take_file(prefix)
        if p is None: missing.append(prefix); continue
        a = M.trim(read(p).mean(axis=1))
        if role == 'Mirror-Sam': a = M.stretch(a, 2 ** (.5 / 12))        # half a semitone lower, drier, closer
        a = M.compress_to_fit(a, round((dl - t - (0.25 if role == 'Mirror-Sam' else 0)) * rate), len(events) + 1)
        a = band(a, 70, 7800); a = a + band(a, 150, 250) * .25
        if role == 'Grandma': a = band(a, 160, 6000)
        a = peak(M.norm(clip_fade(a, .010, .045), -20 if role == 'Narrator' else -19), -5)
        t0 = t - (0.25 if role == 'Mirror-Sam' else 0)                    # half a beat early
        place(track, a, t0); events.append(dict(role=role, start=t0, end=round(t0 + len(a) / rate, 3), deadline=dl, text=words, take=p.name))
    return track, events, missing


PIANO = {45: 'A2v6', 48: 'C3v6', 54: 'F#3v6', 57: 'A3v6', 60: 'C4v6', 63: 'D#4v6', 66: 'F#4v6', 69: 'A4v6', 72: 'C5v6'}


def score():
    out = np.zeros((length, 2), np.float32)
    # 65 BPM, 3-5 note figures, breaths where only the ring remains; total drop at the dead battery (28.5-31.5)
    phrases = [(0.9, [(57, 0), (63, .55), (66, 1.2)], 1.0), (3.9, [(54, 0), (60, .5), (63, 1.0)], 1.0),
               (6.9, [(45, 0), (57, .5), (60, 1.1), (66, 2.3)], 1.0), (10.2, [(48, 0), (60, .45), (63, 1.0)], .95),
               (13.4, [(54, 0), (63, .5)], .8), (16.9, [(57, 0), (60, .5)], .8),
               (22.0, [(45, 0), (54, .6)], .9), (24.4, [(69, 0), (72, .7), (66, 1.6), (69, 2.6)], .75),
               (31.6, [(42, 0)], .9), (33.5, [(45, 0), (57, .8)], .9), (35.2, [(48, 0), (63, .5), (66, 1.2)], .9),
               (38.6, [(45, 0), (60, .4), (63, .9)], .9), (42.2, [(54, 0), (57, .6)], .8),
               (48.6, [(42, 0), (54, 0), (57, .4), (61, .8), (66, 1.2), (69, 2.0), (73, 2.8)], 1.45),
               (53.2, [(57, 0), (61, .5), (64, 1.0)], .9), (56.2, [(45, 0), (57, .5), (60, 1.6)], .95),
               (59.2, [(42, 0), (54, .5), (57, 1.0), (61, 1.6)], 1.15)]
    phrases = [p for p in phrases if not (37.5 < p[0] < 49.5)]                 # v2: the series theme owns 38-50 s
    for start, mel, vol in phrases:
        for j, (midi, off) in enumerate(mel):
            v = (.139 if j % 3 == 0 else .107) * vol * (.87 if midi < 50 else 1)
            a = filter_(note(PIANO, midi, .72 if midi <= 48 else .37, 2.73, True), 5100, 'lowpass')
            place(out, echo(a, 2.4, .33), start + off, v, (-.13 if j % 2 else .10))
    for start, key in ((8.3, 45), (15.5, 48), (22.0, 42), (36.0, 45), (51.0, 45), (60.4, 42)):   # held low bed
        a = filter_(note(PIANO, key, 1.4, 3.8, True), 700, 'lowpass'); place(out, echo(a, 1.8, .31), start, .09)
    return out


MAR = {53: REC / 'marimba' / 'Marimba_hit_Outrigger_F3_loud_01.wav', 60: REC / 'marimba' / 'Marimba_hit_Outrigger_C4_loud_01.wav',
       71: REC / 'marimba' / 'Marimba_hit_Outrigger_B4_loud_01.wav', 77: REC / 'marimba' / 'Marimba_hit_Outrigger_F5_loud_01.wav',
       84: REC / 'marimba' / 'Marimba_hit_Outrigger_C6_loud_01.wav'}
GLOCK = {72: REC / 'glock' / 'glock_medium_C5.wav'}
for k, n in ((67, 'G4'), (79, 'G5'), (84, 'C6'), (91, 'G6'), (96, 'C7')):
    p = REC / 'glock' / f'glock_medium_{n}.wav'
    if p.is_file(): GLOCK[k] = p
CHIME = (66, 70, 73, 78)                                                      # the series' four-note pitch sequence


def chime_note(track, m, t, gain, pan, inside=False):
    a = band(note(MAR, m, .48, 1.3), 290, 3550) * .8; b = band(note(GLOCK, m + 12, .22, 1.17), 400, 5000) * .28
    n = max(len(a), len(b)); s = np.pad(a, ((0, n - len(a)), (0, 0))) + np.pad(b, ((0, n - len(b)), (0, 0)))
    if inside: s = band(s, 500, 2600) * 1.3                                  # from inside the mirrors: thin, boxed
    else: s = echo(s, 1.65, .30)                                             # the loudspeakers: mountain echo
    place(track, s, t, gain, pan)


def fx_and_chime():
    fx = np.zeros((length, 2), np.float32); ch = np.zeros_like(fx)

    def add(name, t, s, e, g, p=0, lo=55, hi=8000):
        a = take(read(REC / (name + '.mp3')), s, e)
        if len(a): place(fx, peak(clip_fade(band(a, lo, hi), .012, .06), -4), t, g, p)
    room = filter_(read(REC / 'wind.mp3', 13), 1000, 'lowpass')
    for t in (0, 7, 14, 21, 32, 39, 46, 53, 59):                             # the dusk wind bed (gone during the dead-battery silence)
        if 26 < t < 31.5: continue
        place(fx, peak(clip_fade(room[:rate * 9], .41, 1.18), -5), t, .06, -.07)
    for t in (14.6, 14.95, 15.3, 15.62): add('steps', t, 1.01, 1.4, .14, .1, 70, 6000)        # 05b the kids stop running
    add('hinge', 16.25, .14, 1.0, .12, .15, 100, 5000); add('door', 16.9, 0, .6, .30, .1, 46, 6200)   # 05c the shutter comes down
    add('buzz', 17.72, .26, .6, .18, -.05, 80, 3100)                         # 06 the tap on the phone
    add('hinge', 30.2, .89, 1.5, .10, -.1, 1200, 6000)                       # 09 the brake squeal, the only sound in the silence
    add('steps', 30.55, 1.32, 1.6, .10, 0, 70, 5000)                         # 09 his foot comes down
    add('paper', 59.9, 2.1, 3.75, .10, .05, 680, 7100)                       # 18 the ink writing itself
    for i, t in enumerate((19.21, 20.21, 21.21)): chime_note(ch, CHIME[i], t, .14, -.18 + i * .12)   # v3: a ghost under the sirens (thriller.py); 07: three notes = three rings
    chime_note(ch, CHIME[3], 46.62, .22, 0, inside=True)                    # 14: the fourth note, from inside the mirrors
    for i, t in enumerate((61.3, 61.75, 62.2)): chime_note(ch, CHIME[i], t, .10, -.1 + i * .1)   # 18: three notes, then nothing
    return fx, ch


THEME = Path(__file__).resolve().parents[2] / 'SERIES_THEME'
T_HIT = 48.50                                                                 # the cut to shot 15 (frame 1164): the Listener


def theme():
    """the series theme (xc/SERIES_THEME): its ostinato bed (no melody: lines stay clear) builds under 12-14 and lands its next
    downbeat on the cut to the Listener; the hit, 0.5 s, then true silence; N3 speaks into it; the wrong bell (G) rings under N3."""
    out = np.zeros((length, 2), np.float32)
    cues = json.loads((THEME / 'theme_cues.json').read_text())['cues']
    bed = sum(read(THEME / 'stems' / f'stem_{k}.wav') for k in ('ostinato', 'low', 'perc'))
    b0, b1 = cues['bed']; seg = bed[round(b0 * rate):round(b1 * rate)].copy()
    fi = round(1.2 * rate); seg[:fi] *= np.linspace(0, 1, fi)[:, None] ** 2                 # creeps in
    place(out, seg, T_HIT - (b1 - b0), 0.80)
    full = read(THEME / 'stems' / 'theme_full.wav')
    hit = full[round(cues['hit'] * rate):round((cues['hit'] + 0.50) * rate)].copy(); hit[-round(.04 * rate):] *= np.linspace(1, 0, round(.04 * rate))[:, None]
    place(out, hit, T_HIT, 0.48)
    bell = full[round((cues['fourth_note'] - 0.005) * rate):]
    place(out, bell, T_HIT + 0.50 + 0.62, 0.9)
    return out


def main():
    voice, events, missing = voices(); music = score() + theme(); fx, ch = fx_and_chime()
    import thriller; thr = thriller.render()                                     # v3: the horror-siren design
    duck = np.ones(length, np.float32)
    for e in events:
        s0 = max(0, round((e['start'] - .17) * rate)); e1 = min(length, round((e['end'] + .26) * rate))
        duck[s0:e1] = np.minimum(duck[s0:e1], np.interp(np.arange(s0, e1), [s0, round(e['start'] * rate), round(e['end'] * rate), e1 - 1], [1, .36, .35, 1]))
    musical = curve([(0, 1), (28.3, 1), (28.55, 0), (31.4, 0), (31.7, .9), (48.4, 1), (48.6, 1.25), (48.98, 1.25), (49.3, .35), (49.615, .35),   # v4: no dead cut
                    
                     (49.62, 1.1), (53, 1), (62.6, .9), (63, 0)])
    gap = curve([(0, 1), (48.98, 1), (49.0, 0), (49.62, 0), (50.4, 1), (63, 1)])
    thr_gap = curve([(0, 1), (63, 1)])                                                   # v4: the Listener's tail runs through the hush          # the hard cut: true silence but the voice
    duck_t = np.where((np.arange(length) / rate > 49.0) & (np.arange(length) / rate < 53.5), np.maximum(duck, .62), duck)   # the bell stays under N3
    mix = music * (duck_t * musical)[:, None] + fx * ((.65 + .35 * duck) * gap)[:, None] + ch * gap[:, None] + thr * (thr_gap * (.55 + .45 * duck))[:, None] + voice
    lim = np.max(np.abs(mix)); mix = mix * (.96 / lim if lim > .96 else 1)
    for n, a in (('dialogue', voice), ('piano', music), ('foley', fx), ('chime', ch), ('thriller', thr), ('premaster', mix)): wav(OUT / f'{n}.wav', a)
    assert np.isfinite(mix).all() and all(e['start'] < e['end'] <= e['deadline'] + 0.01 for e in events)
    (ROOT / 'audio_timeline.json').write_text(json.dumps(dict(duration=63, dialogue=events, missing_takes=missing,
        chime=dict(notes=CHIME, times=[19.21, 20.21, 21.21, 46.62, 61.3, 61.75, 62.2])), indent=2), encoding='utf-8')
    print('missing takes:', missing or 'none', '| events:', len(events))


if __name__ == '__main__':
    main()

