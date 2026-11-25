"""Procedural creature animation on the MakeHuman rig (rest = the character's baked pose).
Signs (bone-local X): upperleg +X swings forward, lowerleg +X bends knee, upperarm +X forward,
head/neck +X nods down, spine +X bends forward, jaw +X opens."""
import math, random
import bpy
from mathutils import Vector, Euler

TAU = 2 * math.pi

def _pb(rig, n):
    pb = rig.pose.bones.get(n)
    if pb: pb.rotation_mode = 'XYZ'
    return pb

class Noise:
    """smooth 1-D value noise"""
    def __init__(s, seed): r = random.Random(seed); s.v = [r.uniform(-1, 1) for _ in range(512)]
    def __call__(s, t):
        i = math.floor(t); f = t - i; f = f * f * (3 - 2 * f)
        return s.v[i % 512] * (1 - f) + s.v[(i + 1) % 512] * f

def _key(rig, f, rots):
    for n, r in rots.items():
        pb = _pb(rig, n)
        if not pb: continue
        pb.rotation_euler = Euler([math.radians(a) for a in r], 'XYZ')
        pb.keyframe_insert('rotation_euler', frame=f)

def _move(root, f, base, fwd, dist, bob=0., sway=0., yaw=0.):
    """root empty: travel along its facing (-Y local) plus bob/sway"""
    rz = root.rotation_euler.z
    d = Vector((math.sin(rz), -math.cos(rz), 0)) * 0 + (Matrix_z(rz) @ Vector((0, -1, 0)))
    side = Matrix_z(rz) @ Vector((1, 0, 0))
    root.location = base + d * dist + side * sway + Vector((0, 0, bob))
    root.keyframe_insert('location', frame=f)

def Matrix_z(a):
    from mathutils import Matrix
    return Matrix.Rotation(a, 3, 'Z')

def shamble(rig, root, f0, f1, fps=24, speed=.55, period=1.35, phase=0., limp=.35, seed=1, arms='dangle', drag=True):
    """infected stagger-walk: uneven stride, dragging limp leg, lolling head, twitches"""
    n = Noise(seed); r = random.Random(seed); base = root.location.copy()
    lean = r.uniform(6, 16); headroll = r.uniform(-12, 12)
    dist = 0.
    for f in range(f0, f1 + 1):
        t = (f - f0) / fps; ph = TAU * t / period + phase
        # limp: the bad leg's swing is shorter and slower
        sL, sR = math.sin(ph), math.sin(ph + math.pi)
        aL = 26 * (1 - limp) if drag else 26; aR = 30
        kneeL = 38 * max(0, math.sin(ph + math.pi / 2)) * (1 - limp * .7) + 6
        kneeR = 44 * max(0, math.sin(ph + 1.5 * math.pi)) + 6
        tw = n(t * 3.1) * 10 * (abs(n(t * .7 + 30)) > .55)          # occasional twitch
        rot = {
            'upperleg01.L': (aL * sL, 0, 0), 'upperleg01.R': (aR * sR, 0, 0),
            'lowerleg01.L': (kneeL, 0, 0), 'lowerleg01.R': (kneeR, 0, 0),
            'foot.L': (-10 * sL - (8 if drag else 0), 0, 0), 'foot.R': (-12 * sR, 0, 0),
            'spine05': (lean * .3, 3 * math.sin(ph), 5 * math.sin(ph)),
            'spine03': (lean * .4 + 2 * math.sin(2 * ph), 4 * math.sin(ph + .5), -6 * math.sin(ph)),
            'spine01': (lean * .3, 0, -4 * math.sin(ph)),
            'neck01': (6 + 5 * n(t * 1.3 + 7), 0, 6 * n(t * 1.1 + 3)),
            'head': (8 + 10 * n(t * 1.7) + tw, headroll * .5 + 8 * n(t * .9 + 11), 10 * n(t * 1.2 + 5)),
            'jaw': (6 + 6 * abs(n(t * 2.3 + 2)), 0, 0),
        }
        if arms == 'dangle':
            rot['upperarm01.L'] = (-10 * sL + 6 * n(t * 2 + 1), 0, 4 * math.sin(ph))
            rot['upperarm01.R'] = (-10 * sR + 6 * n(t * 2 + 9), 0, -4 * math.sin(ph))
            rot['lowerarm01.L'] = (8 + 8 * abs(math.sin(ph)), 0, 0); rot['lowerarm01.R'] = (8 + 8 * abs(math.sin(ph + 1)), 0, 0)
        elif arms == 'reach':
            rot['upperarm01.L'] = (55 + 8 * n(t * 2), 0, -6); rot['upperarm01.R'] = (48 + 8 * n(t * 2 + 4), 0, 6)
            rot['lowerarm01.L'] = (20 + 10 * n(t * 3), 0, 0); rot['lowerarm01.R'] = (26 + 10 * n(t * 3 + 2), 0, 0)
        for fn in ('finger2-1', 'finger3-1', 'finger4-1'):
            for sd in ('.L', '.R'): rot[fn + sd] = (20 + 15 * n(t * 2.5 + hash(fn + sd) % 50), 0, 0)
        _key(rig, f, rot)
        # forward travel: faster while the good leg pushes
        dist += speed / fps * (1 + .45 * math.sin(ph + .4))
        if root is not None:
            _move(root, f, base, None, dist, bob=-.035 * abs(math.cos(ph)), sway=.025 * math.sin(ph))

def sprint(rig, root, f0, f1, fps=24, speed=5.5, period=.62, phase=0., seed=2):
    n = Noise(seed); base = root.location.copy(); dist = 0.
    for f in range(f0, f1 + 1):
        t = (f - f0) / fps; ph = TAU * t / period + phase
        sL, sR = math.sin(ph), math.sin(ph + math.pi)
        rot = {
            'upperleg01.L': (48 * sL + 12, 0, 0), 'upperleg01.R': (48 * sR + 12, 0, 0),
            'lowerleg01.L': (70 * max(0, math.sin(ph + 1.9)) + 10, 0, 0), 'lowerleg01.R': (70 * max(0, math.sin(ph + 1.9 + math.pi)) + 10, 0, 0),
            'foot.L': (-20 * sL, 0, 0), 'foot.R': (-20 * sR, 0, 0),
            'spine03': (14, 0, 8 * math.sin(ph)), 'spine01': (8, 0, -6 * math.sin(ph)),
            'upperarm01.L': (-50 * sL, 0, 0), 'upperarm01.R': (-50 * sR, 0, 0),
            'lowerarm01.L': (60, 0, 0), 'lowerarm01.R': (60, 0, 0),
            'head': (-8 + 6 * n(t * 3), 0, 5 * n(t * 2)), 'jaw': (14 + 8 * abs(n(t * 4)), 0, 0),
        }
        _key(rig, f, rot)
        dist += speed / fps
        _move(root, f, base, None, dist, bob=.05 * abs(math.sin(ph)) - .04)

def crawl(rig, root, f0, f1, fps=24, speed=.35, period=1.6, seed=3):
    """arm-over-arm drag: reach, plant, pull; body lurches forward on each pull"""
    n = Noise(seed); base = root.location.copy(); dist = 0.
    for f in range(f0, f1 + 1):
        t = (f - f0) / fps; ph = TAU * t / period
        sL, sR = math.sin(ph), math.sin(ph + math.pi)
        rot = {
            'upperarm01.L': (30 * sL, 0, 10 * max(0, sL)), 'upperarm01.R': (30 * sR, 0, -10 * max(0, sR)),
            'lowerarm01.L': (35 * max(0, -sL) + 10, 0, 0), 'lowerarm01.R': (35 * max(0, -sR) + 10, 0, 0),
            'clavicle.L': (0, 0, 8 * sL), 'clavicle.R': (0, 0, -8 * sR),
            'spine05': (0, 0, 7 * sL), 'spine03': (0, 0, -6 * sL), 'spine01': (0, 4 * sL, 0),
            'neck01': (-8 + 6 * n(t), 0, 6 * sL), 'head': (-10 + 12 * n(t * 1.3), 0, 10 * n(t * .8 + 4)),
            'jaw': (10 + 14 * abs(n(t * 2.1)), 0, 0),
            'upperleg01.R': (6 * sR, 0, 0), 'lowerleg01.R': (10 + 8 * abs(sR), 0, 0),
        }
        for fn in ('finger2-1', 'finger3-1', 'finger4-1', 'finger5-1'):
            rot[fn + '.L'] = (40 * max(0, -sL) + 10, 0, 0); rot[fn + '.R'] = (40 * max(0, -sR) + 10, 0, 0)
        _key(rig, f, rot)
        dist += speed / fps * (1.6 * max(0, -math.cos(ph * 2)) ** 1.5 + .1)     # lurch on each pull
        _move(root, f, base, None, dist, bob=.012 * math.sin(2 * ph))

def scream(rig, f0, f1, fps=24, f_scream=30, seed=4, amp=1.):
    """stillness, a twitch, then the head snaps back and the jaw drops; whole body trembles"""
    n = Noise(seed)
    for f in range(f0, f1 + 1):
        t = (f - f0) / fps; k = max(0., min(1., (f - f_scream) / 5.))          # snap in 5 frames
        k = k * k * (3 - 2 * k); tr = k * 1.6
        pre = 6 * n(t * 6) * (f < f_scream)
        rot = {
            'head': (-34 * k * amp + pre + tr * n(t * 30), tr * n(t * 27 + 3), tr * n(t * 25 + 8)),
            'neck01': (-14 * k * amp, 0, 0), 'neck02': (-10 * k * amp, 0, 0),
            'jaw': (6 + 30 * k * max(amp, .6) + 3 * k * n(t * 20), 0, 0),
            'spine05': (-10 * k * amp, 0, 0), 'spine03': (-6 * k * amp, 0, 0),
            'upperarm01.L': (-12 * k + tr * 2 * n(t * 22), 0, -18 * k), 'upperarm01.R': (-12 * k + tr * 2 * n(t * 21 + 5), 0, 18 * k),
            'lowerarm01.L': (14 * k, 0, 0), 'lowerarm01.R': (14 * k, 0, 0),
        }
        for fn in ('finger1-1', 'finger2-1', 'finger3-1', 'finger4-1', 'finger5-1'):
            for sd in ('.L', '.R'): rot[fn + sd] = (-20 * k + 8 * k * n(t * 18 + len(fn)), 0, 0)
        _key(rig, f, rot)

def idle(rig, f0, f1, fps=24, seed=5, amp=1.):
    """standing infected: breathing, head lolls, fingers twitch, weight shift"""
    n = Noise(seed)
    for f in range(f0, f1 + 1):
        t = (f - f0) / fps
        rot = {
            'spine03': (3 * amp * math.sin(TAU * t / 3.2), 2 * amp * n(t * .5), 3 * amp * n(t * .4 + 2)),
            'head': (6 * amp * n(t * .9), 10 * amp * n(t * .6 + 4), 12 * amp * n(t * .7 + 9)),
            'neck01': (4 * amp * n(t * .8 + 1), 0, 0),
            'jaw': (5 + 6 * abs(n(t * 1.5 + 6)), 0, 0),
            'upperarm01.L': (5 * n(t * 1.2 + 2), 0, 3 * n(t + 1)), 'upperarm01.R': (5 * n(t * 1.1 + 7), 0, 3 * n(t + 5)),
            'upperleg01.L': (2 * n(t * .4), 0, 0), 'upperleg01.R': (2 * n(t * .4 + 3), 0, 0),
        }
        _key(rig, f, rot)

def stomp(rig, root, f0, f1, fps=24, speed=.9, period=1.7, seed=6):
    """the Brute: slow, heavy, shoulders rolling, club arm swinging wide"""
    n = Noise(seed); base = root.location.copy(); dist = 0.
    for f in range(f0, f1 + 1):
        t = (f - f0) / fps; ph = TAU * t / period
        sL, sR = math.sin(ph), math.sin(ph + math.pi)
        rot = {
            'upperleg01.L': (24 * sL, 0, -4), 'upperleg01.R': (24 * sR, 0, 4),
            'lowerleg01.L': (30 * max(0, math.sin(ph + 1.6)) + 8, 0, 0), 'lowerleg01.R': (30 * max(0, math.sin(ph + 1.6 + math.pi)) + 8, 0, 0),
            'spine03': (10, 4 * sL, 10 * sL), 'spine05': (6, 0, 8 * sL), 'spine01': (4, 0, -6 * sL),
            'clavicle.L': (0, 0, 8 * sL), 'clavicle.R': (0, 0, -10 * sR),
            'upperarm01.L': (-14 * sL, 0, 6), 'upperarm01.R': (-22 * sR + 6 * n(t), 0, -10),
            'lowerarm01.L': (18, 0, 0), 'lowerarm01.R': (12 + 8 * abs(sR), 0, 0),
            'head': (-6 + 5 * n(t), 0, 8 * n(t * .7)), 'neck01': (-6, 0, 0), 'jaw': (8 + 10 * abs(n(t * 2)), 0, 0),
        }
        _key(rig, f, rot)
        dist += speed / fps * (1 + .6 * math.sin(2 * ph))
        _move(root, f, base, None, dist, bob=-.06 * abs(math.cos(ph)), sway=.05 * math.sin(ph))
