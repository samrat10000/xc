"""Deer-style bare skull with branching antlers, built in local space.
Origin at cranium centre, snout toward -Y, top +Z. Returns dict of objects."""
import math, random
import bpy, bmesh
from mathutils import Vector, noise
import castlib as L
V = lambda *a: Vector(a[0] if len(a) == 1 else a)

def _bool(o, cutter, op='DIFFERENCE'):
    m = o.modifiers.new('b', 'BOOLEAN'); m.operation = op; m.object = cutter; m.solver = 'EXACT'
    L.apply_all(o); bpy.data.objects.remove(cutter)

def _remesh(o, vs, smooth_it=3):
    r = o.modifiers.new('rm', 'REMESH'); r.mode = 'VOXEL'; r.voxel_size = vs
    if smooth_it:
        s = o.modifiers.new('sm', 'SMOOTH'); s.factor = .5; s.iterations = smooth_it
    L.apply_all(o)

def branch(name, col, pts, r0, r1, rng, sides=10, wob=.006):
    """smooth tapered tube through pts (Catmull-Rom resampled), gnarled with wobble."""
    P = [V(p) for p in pts]
    out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        for k in range(6):
            t = k / 6
            q = .5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)
            out.append(q)
    out.append(P[-1])
    n = len(out)
    for i in range(1, n - 1):
        out[i] = out[i] + V(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)) * wob * (1 - i / n)
    radii = [r0 + (r1 - r0) * (i / (n - 1)) ** .8 for i in range(n)]
    radii = [r * (1 + .12 * math.sin(i * 1.7)) for i, r in enumerate(radii)]
    return L.tube(name, out, radii, col, sides=sides), out

def build(col, seed=7):
    rng = random.Random(seed)
    parts = []
    parts.append(L.blob('sk cranium', (0, .02, .0), (.064, .078, .058), col))
    parts.append(L.blob('sk occiput', (0, .065, -.012), (.052, .045, .05), col))
    parts.append(L.blob('sk brow', (0, -.035, .022), (.05, .05, .035), col))
    # long tapering snout (top line slopes down to the nose)
    sn = []
    for i in range(9):
        t = i / 8
        sn.append(V(0, -.02 - .25 * t, .012 - .04 * t - .01 * t * t))
    snout = L.tube('sk snout', sn, [.046 - .028 * (i / 8) ** .8 for i in range(9)], col, sides=24)
    for v in snout.data.vertices:
        c = v.co; c.x *= .82; c.z = (c.z - sn[0].z) * .78 + sn[0].z if c.y > -.02 else c.z
    parts.append(snout)
    for sx in (1, -1):
        # zygomatic arch and orbit rims
        parts.append(L.tube(f'sk zyg{sx}', [(.046 * sx, .03, -.02), (.06 * sx, -.02, -.022), (.058 * sx, -.07, -.02), (.04 * sx, -.11, -.025)], [.007, .009, .008, .006], col, sides=10))
        parts.append(L.blob(f'sk orbit{sx}', (.05 * sx, -.056, .014), (.03, .032, .03), col))
        parts.append(L.blob(f'sk maxilla{sx}', (.026 * sx, -.11, -.026), (.02, .065, .019), col))
        # antler pedicles
        parts.append(L.tube(f'sk ped{sx}', [(.026 * sx, .0, .04), (.036 * sx, .012, .066)], [.017, .015], col, sides=12))
    skull = L.join(parts, 'Stalker skull')
    _remesh(skull, .0022, 10)
    # cavities: orbits, nasal aperture, lacrimal pits, temporal fossae
    for sx in (1, -1):
        _bool(skull, L.blob('cut', (.074 * sx, -.064, .018), (.026, .024, .024), col, seg=32, ring=24))
        _bool(skull, L.blob('cut', (.044 * sx, -.095, .0), (.008, .012, .007), col))
        _bool(skull, L.blob('cut', (.07 * sx, .03, .0), (.014, .03, .02), col))
    _bool(skull, L.blob('cut', (0, -.27, -.022), (.017, .06, .014), col, seg=32, ring=24))
    _bool(skull, L.blob('cut', (0, -.21, -.005), (.012, .05, .006), col))        # nasal slit on the bridge
    # bone surface: pitting, sutures
    for v in skull.data.vertices:
        p = v.co
        d = .0007 * noise.noise(p * 140) + .0012 * noise.noise(p * 45)
        d -= .0009 * max(0, 1 - abs(noise.noise(p * 22 + V(3, 1, 0))) * 14)     # suture cracks
        v.co = p + v.normal * d
    L.smooth(skull)

    # lower jaw: two thin mandibles meeting at the chin, hanging slightly open
    jaw_parts = []
    for sx in (1, -1):
        jaw_parts.append(L.tube(f'jaw{sx}', [(.04 * sx, .035, -.01), (.042 * sx, .03, -.06), (.036 * sx, -.02, -.072), (.024 * sx, -.12, -.07), (.008 * sx, -.215, -.066)],
                                [.012, .013, .011, .008, .007], col, sides=12))
    jaw = L.join(jaw_parts, 'Stalker jaw'); _remesh(jaw, .002, 3)
    for v in jaw.data.vertices: v.co += v.normal * .0008 * noise.noise(v.co * 120)
    L.smooth(jaw)

    # teeth: molar rows top and bottom, plus long unnatural fangs
    teeth = []
    for sx in (1, -1):
        for i in range(7):
            y = -.03 - i * .016
            teeth.append(L.box(f't u{sx}{i}', (.027 * sx * (1 - i * .03), y, -.043 - i * .0015), (.006, .012, .012 + rng.uniform(0, .004)), col, bevel=.0015))
            teeth.append(L.box(f't l{sx}{i}', (.025 * sx * (1 - i * .04), y, -.059), (.0055, .011, .011 + rng.uniform(0, .004)), col, bevel=.0015))
        teeth.append(L.tube(f't fang{sx}', [(.017 * sx, -.15, -.045), (.019 * sx, -.155, -.07), (.014 * sx, -.15, -.095)], [.005, .0035, .0005], col, sides=8))
        teeth.append(L.tube(f't fangl{sx}', [(.012 * sx, -.19, -.058), (.014 * sx, -.196, -.04), (.01 * sx, -.19, -.025)], [.004, .003, .0005], col, sides=8))
    teeth = L.join(teeth, 'Stalker teeth')

    # antlers: big gnarled beams with tines, sweeping up, out and back
    ant = []
    for sx in (1, -1):
        p0 = V(.036 * sx, .012, .066)
        beam = [p0, p0 + V(.04 * sx, .04, .07), p0 + V(.12 * sx, .1, .16), p0 + V(.22 * sx, .13, .28), p0 + V(.28 * sx, .09, .42),
                p0 + V(.3 * sx, .02, .54), p0 + V(.27 * sx, -.04, .62)]
        beam = [p0 + (q - p0) * .72 for q in beam]
        o, pts = branch(f'antler{sx}', col, beam, .014, .003, rng, sides=12)
        ant.append(o)
        n = len(pts)
        for frac, d, ln, r in ((.12, V(.03 * sx, -.16, .06), .15, .011), (.3, V(.02 * sx, -.14, .13), .19, .01),
                               (.5, V(-.02 * sx, -.1, .14), .17, .009), (.68, V(.08 * sx, .1, .1), .14, .008), (.82, V(-.05 * sx, -.06, .1), .1, .006)):
            b0 = pts[int(frac * (n - 1))]
            dd = d.normalized() * ln * .7
            tp = [b0, b0 + dd * .35 + V(0, 0, .01), b0 + dd * .7 + V(0, 0, .03), b0 + dd + V(0, 0, .06)]
            t, _ = branch(f'tine{sx}{frac}', col, tp, r * .8, .001, rng, sides=8, wob=.004)
            ant.append(t)
    antlers = L.join(ant, 'Stalker antlers'); _remesh(antlers, .0025, 2)
    for v in antlers.data.vertices:
        p = v.co
        v.co = p + v.normal * (.0012 * noise.noise(p * V(60, 60, 20)) + .0008 * noise.noise(p * 200))
    L.smooth(antlers)
    return {'skull': skull, 'jaw': jaw, 'teeth': teeth, 'antlers': antlers,
            'orbits': [V(.05 * sx, -.056, .014) for sx in (1, -1)]}
