from music import *

DUR = 16.0
OM, OP = organ_bank('man', False), organ_bank('ped', False)
LM, LP = organ_bank('man', True), organ_bank('ped', True)
MAR = named_bank(f'{V}/Percussion/Marimba/*.wav')
GLK = named_bank(f'{V}/Percussion/Glock/*.wav')
VLN = named_bank(f'{V}/Strings/Violin Section/susVib/*_v1.wav')
VLA = named_bank(f'{V}/Strings/Viola Section/susvib/*v1*.wav')
VC = named_bank(f'{V}/Strings/Cello Section/susvib/*_v1_1.wav')
print('banks', len(OM), len(OP), len(LM), len(LP), len(MAR), len(GLK), len(VLN), len(VLA), len(VC))

org, chime, strings, perc, tick = (Mix(DUR) for _ in range(5))

# --- 0-3.4: quiet organ bed (A minor, open fifth), ticking clock
org.add(note(OP, 45, 3.2, att=1.4, rel=.6), 0.0, .45)
org.add(note(OM, 52, 3.0, att=1.8, rel=.6), 0.1, .22)
org.add(note(OM, 57, 2.9, att=2.0, rel=.6), 0.2, .18)
CLV = sorted(glob.glob(f'{V}/Percussion/Claves1_Hit_v1_rr*_Sum.wav'))
TICK = os.environ.get('TICK')


def tick_at(t, g):
    x = load(CLV[int(t * 10) % len(CLV)])[:int(.25 * SR)]
    x = hp(lp(x, 5200), 900)
    tick.add(x, t, g)


for k, t in enumerate((0.0, 1.0, 2.0, 3.0)):
    tick_at(t, .5)

# --- chime: 3 notes through the town loudspeaker (4th missing)
for t, m in ((3.55, 65), (4.05, 69), (4.55, 72)):
    x = addv(note(MAR, m, .6, att=.002, rel=1.2) * .9, note(GLK, m + 12, .4, att=.002, rel=1.0) * .35)
    chime.add(pa_speaker(x), t, 1.0)

# --- 5.4-6.6: the organ blower breathes in the silence (real wind-supply noise of the organ)
bl = load(f'{V}/Keys/Organ/Rode_Blower.wav')[:int(1.6 * SR)]
org.add(fade(bl, 1.0, .5), 5.3, .5)

# --- 6.5-13: Interstellar-style organ ostinato (original), pulse 0.3 s, ticks join
E8 = .3
prog = [(6.5, 8.9, [57, 60, 64, 60, 57, 60, 64, 69], 45),
        (8.9, 10.7, [53, 57, 60, 57, 53, 57, 60, 65], 41),
        (10.7, 11.9, [48, 52, 55, 52, 60, 55, 64, 60], 36),
        (11.9, 13.0, [55, 59, 62, 59, 55, 59, 62, 67], 43)]
for (a, b, pat, ped) in prog:
    t = a; i = 0
    while t < b - .01:
        u = (t - 6.5) / 6.5
        g = .35 + .5 * u
        org.add(note(OM, pat[i % len(pat)], E8 * .95, att=.03, rel=.35), t, g)
        if t >= 10.0:
            org.add(note(LM, pat[i % len(pat)] + 12, E8 * .9, att=.02, rel=.3), t, .12 + .3 * (t - 10) / 3)
        if i % 2 == 0:
            tick_at(t, .25 + .2 * u)
        t += E8; i += 1
    org.add(note(OP, ped, b - a, att=.5, rel=.5), a, .8)
    if a >= 10.7:
        org.add(note(LP, ped, b - a, att=.3, rel=.4), a, .55)
# strings swell 9.0 -> 13
strings.add(note(VC, 41, 1.8, att=1.2, rel=.6), 8.9, .5)
strings.add(note(VLA, 60, 1.8, att=1.4, rel=.6), 8.95, .35)
strings.add(note(VLN, 69, 1.8, att=1.5, rel=.6), 9.0, .32)
strings.add(note(VC, 48, 1.2, att=.4, rel=.5), 10.7, .6)
strings.add(note(VLA, 64, 1.2, att=.4, rel=.5), 10.7, .45)
strings.add(note(VLN, 72, 1.2, att=.4, rel=.5), 10.7, .45)
strings.add(note(VC, 43, 1.1, att=.3, rel=.5), 11.9, .7)
strings.add(note(VLA, 62, 1.1, att=.3, rel=.5), 11.9, .55)
strings.add(note(VLN, 74, 1.1, att=.3, rel=.5), 11.9, .55)
# timpani roll crescendo into 13
rolls = sorted(glob.glob(f'{V}/Percussion/Timpani/Rolls/*.wav'))
if rolls:
    r = load(rolls[0])[:int(1.6 * SR)]
    r = r * np.linspace(.05, 1, len(r))[:, None]
    perc.add(r, 11.5, .5)

# --- 13-14.2: drop (not a cutout): high violins hold E, low pedal breath
strings.add(note(VLN, 76, 1.3, att=.15, rel=.4), 12.95, .28)
org.add(note(OP, 45, 1.2, att=.2, rel=.3), 13.0, .35)
if rolls:
    r = load(rolls[1 % len(rolls)])[:int(.7 * SR)]
    perc.add(r * np.linspace(0, 1, len(r))[:, None] ** 2, 13.5, .45)

# --- 14.2: the 4th note, from inside the mirror (dry, close) + full organ F major
F = 14.2
x = addv(note(MAR, 77, .8, att=.002, rel=1.6) * .9, note(GLK, 89, .6, att=.002, rel=1.4) * .4)
chime.add(lp(x, 9000), F, 1.15)
for m, g in ((41, .9),):
    org.add(note(LP, m, 1.75, att=.05, rel=1.2), F, g)
    org.add(note(OP, m, 1.75, att=.05, rel=1.2), F, .6)
for m, g in ((53, .5), (57, .45), (60, .45), (65, .4), (69, .38), (72, .3)):
    org.add(note(LM, m, 1.7, att=.06, rel=1.2), F, g)
strings.add(note(VC, 41, 1.7, att=.08, rel=1.0), F, .7)
strings.add(note(VLN, 81, 1.7, att=.1, rel=1.0), F, .4)
gong = f'{V}/Percussion/gongHit_mf.wav'
if os.path.exists(gong):
    perc.add(load(gong), F, .5)
tm = sorted(glob.glob(f'{V}/Percussion/Timpani/Timpani1_Hit_v3_rr1_Sum.wav'))
if tm:
    perc.add(load(tm[0]), F, .7)

# --- mix
mix = (reverb(org.y, 4.0, .35, 1) * 1.0 + reverb(strings.y, 3.5, .4, 2) * .9 + reverb(chime.y, 2.5, .25, 3) * 1.0
       + reverb(perc.y, 3.0, .3, 4) * .9 + reverb(tick.y, 1.2, .15, 5) * .8)
mix = hp(mix, 30)
n = len(mix)
# ending fade 15.2 -> 16.0
mix *= automation(n, [(0, 1), (15.1, 1), (16.0, 0.0)])
mix = np.tanh(mix * 1.2) / 1.2
pk = np.abs(mix).max()
mix = mix / pk * 0.89
import wave
def wav(path, y):
    y16 = (np.clip(y, -1, 1) * 32767).astype('<i2')
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y16.tobytes())
wav('score.wav', mix)
for nm, m in (('stem_org', org.y), ('stem_chime', chime.y)):
    wav(nm + '.wav', m / (np.abs(m).max() + 1e-6) * .8)
print('ok', n / SR)
