"""Shared timeline: 16 s @ 24 fps. Mechanism clock drives HUD, captions and SFX."""
import math
FPS = 24
N = 384
RPM_REAL = 3000.0

# segments (frame numbers, 0-based)
A_INK = (0, 34)        # hook, sketch inks in
B_FILL = (34, 58)      # marker fill + pixel wipe, REAL SPEED
C_RAMP = (58, 82)      # speed ramp down, body ghosts to ink
D_SLOW = (82, 300)     # slow-mo cutaway, 4 strokes + firing order
E_RAMP = (300, 330)    # ramp back up, body re-pixels
F_END = (330, 384)     # real speed, payoff text

SLOW = 84.0

def speed(f):
    """playback speed factor (1 = real time)."""
    def ease(t): return t * t * (3 - 2 * t)
    if f < C_RAMP[0]: return 1.0
    if f < C_RAMP[1]:
        t = ease((f - C_RAMP[0]) / (C_RAMP[1] - C_RAMP[0]))
        return math.exp(math.log(1.0) * (1 - t) + math.log(1 / SLOW) * t)
    if f < E_RAMP[0]: return 1 / SLOW
    if f < E_RAMP[1]:
        t = ease((f - E_RAMP[0]) / (E_RAMP[1] - E_RAMP[0]))
        return math.exp(math.log(1 / SLOW) * (1 - t))
    return 1.0

_cache = {}
def crank(f):
    """crank angle in degrees at frame f (integrated through speed ramps)."""
    if f in _cache: return _cache[f]
    _cache[f] = _raw(f) + _off()
    return _cache[f]

def _raw(f):
    a = 0.0; dpf = RPM_REAL / 60 * 360 / FPS
    for i in range(f): a += dpf * speed(i)
    return a

_o = []
def _off():
    # align so cylinder 1 starts its intake stroke exactly when slow-mo settles
    if not _o: _o.append((360 - _raw(D_SLOW[0])) % 720)
    return _o[0]

def rpm_shown(f):
    return RPM_REAL * speed(f)

def slowmo_label(f):
    s = speed(f)
    if s > 0.98: return "REAL SPEED"
    k = 1 / s
    return ("SLOW-MO 1/%.1f" % k) if k < 3 else ("SLOW-MO 1/%d" % round(k))

# cylinder firing: order 1-4-2-5-3-6, cylinder i fires when cycle angle == FIRE[i]
FIRE = {1: 0, 4: 120, 2: 240, 5: 360, 3: 480, 6: 600}   # V6, even 120 deg firing
CRANK_OFF = {1: 0, 2: 180, 3: 180, 4: 0}   # pin offset per cylinder

def stroke(cyl, f):
    """0 intake,1 compression,2 power,3 exhaust for cylinder."""
    c = (crank(f) - FIRE[cyl] + 720 + 0) % 720
    # power starts at firing (TDC) -> power 0-180, exhaust 180-360, intake 360-540, compression 540-720
    return [2, 3, 0, 1][int(c // 180)]

STROKE_NAME = ["SUCK", "SQUEEZE", "BANG", "BLOW"]
