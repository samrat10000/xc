"""Ep1 real-recording sound bed (Freesound via Openverse, CC0/CC-BY). Full 16 s timeline."""
from music import *
DUR = 16.0
m = Mix(DUR)


def seg(f, a, b):
    x = load(f)
    return x[int(a * SR):int(b * SR)].copy()


def far(x, fc=2500, semis=0.0, rv=.35):
    x = shift(x, semis) if semis else x
    return reverb(lp(hp(x, 180), fc), 2.2, rv, 7)


wire = hp(lp(seg('wires/4_bd334702.mp3', 30, 47), 3200), 60)
wire = wire / (np.sqrt((wire ** 2).mean()) + 1e-9) * 10 ** (-32 / 20)
town = hp(lp(seg('street/2_71757b71.mp3', 20, 32), 1300), 90)
town = town / (np.sqrt((town ** 2).mean()) + 1e-9) * 10 ** (-38 / 20)
n = len(m.y)
w_env = automation(n, [(0, 0), (.25, 1), (9.8, 1), (10.2, .75), (13.0, .7), (14.0, 0), (16, 0)])
t_env = automation(n, [(0, 0), (.25, 1), (9.4, 1), (10.05, 0), (16, 0)])
m.add(fade(wire[:n], .2, .2) * w_env[:len(wire[:n])], 0)
m.add(fade(town[:int(10.2 * SR)], .2, .3) * t_env[:int(10.2 * SR)], 0)
# crows: caw pair far off (pitched down toward the deeper Japanese jungle crow)
m.add(far(seg('crows/0_cb745265.mp3', .7, 2.1), 2200, -3), 1.1, .07)
# take-off: flock bed + nearer caws when the chime starts (002 begins at 3.0; first note 3.55)
flock = seg('crows/5_ac24889d.mp3', 10, 13)
flock = hp(flock, 250) / (np.sqrt((flock ** 2).mean()) + 1e-9) * 10 ** (-27 / 20)
m.add(fade(flock, .15, 1.2), 3.6, 1.0)
m.add(far(seg('crows/0_cb745265.mp3', 6.3, 8.1), 3500, -2, .2), 3.75, .12)
y = m.y
pk = np.abs(y).max()
import wave
y16 = (np.clip(y, -1, 1) * 32767).astype('<i2')
with wave.open('sfx.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y16.tobytes())
print('sfx peak', pk)
