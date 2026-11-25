"""Humanoid builder on top of castlib: posed skin-modifier skeleton + sculpted head."""
import math, random
from mathutils import Vector, noise
import castlib as L
import bmesh

def V(*a): return Vector(a[0]) if len(a) == 1 else Vector(a)

class Skel:
    def __init__(s): s.j = []; s.e = []; s.names = {}
    def add(s, name, p, r, parent=None):
        s.j.append((tuple(p), (r, r) if not hasattr(r, '__len__') else tuple(r)))
        i = len(s.j) - 1; s.names[name] = i
        if parent is not None: s.e.append((s.names[parent] if isinstance(parent, str) else parent, i))
        return i
    def chain(s, name, pts, radii, parent, mids=1):
        """add points with optional interpolated mid-joints for muscle shape"""
        prev = parent; prevp = Vector(s.j[s.names[parent]][0]) if isinstance(parent, str) else None
        out = []
        for k, (p, r) in enumerate(zip(pts, radii)):
            p = Vector(p)
            if mids and prevp is not None and isinstance(r, tuple) and len(r) == 3:
                pass
            i = s.add(f'{name}{k}', p, r[:2] if hasattr(r, '__len__') else r, prev)
            prev = f'{name}{k}'; prevp = p; out.append(i)
        return out
    def p(s, name): return Vector(s.j[s.names[name]][0])

def hand(sk, side, wrist, palm, curl=.6, spread=1., rng=None, fat=1.):
    """5 fingers from the palm; curl bends them toward the palm normal."""
    rng = rng or random.Random(1)
    wp, pp = sk.p(wrist), sk.p(palm)
    d = (pp - wp).normalized()
    side_v = d.cross(V(0, 0, 1)).normalized() if abs(d.z) < .95 else V(1, 0, 0)
    if side < 0: side_v = -side_v
    palm_n = d.cross(side_v).normalized()
    lens = [.024, .028, .026, .022]
    for f in range(4):
        off = (f - 1.5) * .013 * spread
        base = pp + side_v * off + d * .012
        sk.add(f'{palm}f{f}b', base, .0085 * fat, palm)
        dirv = (d + side_v * (f - 1.5) * .08 * spread).normalized()
        p = base; prev = f'{palm}f{f}b'
        c = curl + rng.uniform(-.25, .25)
        for k in range(3):
            ang = c * (k + 1) * .55
            dirk = (dirv * math.cos(ang) - palm_n * math.sin(ang)).normalized()
            p = p + dirk * lens[f] * (1 - k * .15)
            sk.add(f'{palm}f{f}{k}', p, (.0075 - k * .0012) * fat, prev); prev = f'{palm}f{f}{k}'
    # thumb
    tb = wp.lerp(pp, .5) + side_v * -.02 - palm_n * .008
    sk.add(f'{palm}t0', tb, .011 * fat, wrist)
    tdir = (d * .6 - side_v * .5 - palm_n * .4).normalized()
    p = tb; prev = f'{palm}t0'
    for k in range(2):
        p = p + tdir * .022; tdir = (tdir - palm_n * .3 * curl).normalized()
        sk.add(f'{palm}t{k + 1}', p, .009 * fat - k * .0015, prev); prev = f'{palm}t{k + 1}'

def limb(sk, name, parent, pts, radii, mids=2):
    """chain with interpolated mid joints whose radius bulges (muscle) by radii[i][2] factor"""
    prev = parent; prevp = sk.p(parent); prevr = sk.j[sk.names[parent]][1]
    for k, (p, r) in enumerate(zip(pts, radii)):
        p = Vector(p); rr = r[:2]; bulge = r[2] if len(r) > 2 else 1.0
        for m in range(1, mids + 1):
            t = m / (mids + 1)
            q = prevp.lerp(p, t)
            b = 1 + (bulge - 1) * math.sin(t * math.pi)
            mr = ((prevr[0] + (rr[0] - prevr[0]) * t) * b, (prevr[1] + (rr[1] - prevr[1]) * t) * b)
            sk.add(f'{name}{k}m{m}', q, mr, prev); prev = f'{name}{k}m{m}'
        sk.add(f'{name}{k}', p, rr, prev); prev = f'{name}{k}'; prevp = p; prevr = rr

# ------------------------------------------------------------------ head
def head(name, col, rx=.082, ry=.098, rz=.112, gaunt=1., jaw_open=.6, rot_nose=True, seed=3, zombie=True):
    """sculpted skull-ish head in local space, origin at head centre, faces -Y."""
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=72, radius=1)
    o = L.mesh_obj(name, bm, col)
    def g(p, c, r): return math.exp(-((p - c).length_squared) / (r * r))
    def f(p):
        x, y, z = p.x * rx, p.y * ry, p.z * rz
        q = V(x, y, z)
        # skull: wider at back-top, narrow jaw, flatter face
        if z < 0: q.x *= 1 + z / rz * .28 * (1 if y < 0 else .6)
        if y < 0: q.y *= .93 - .05 * max(0, z / rz)
        if y > 0 and z > -.02: q.y *= 1.06
        if z < -.03 and y > 0: q.y *= .8            # back of the neck taper
        # forehead slope
        q.y += .012 * max(0, z / rz) * (1 if y < 0 else 0)
        n = q.normalized() if q.length else V(0, 0, 1)
        d = 0
        E = [V(.031, -.081, .013), V(-.031, -.081, .013)]
        for e in E:
            d -= .021 * g(q, e, .021) * gaunt          # deep sockets
        d += .009 * g(q, V(0, -.088, .036), .028) * (1 - g(q, V(0, -.09, .02), .012))   # brow ridge
        for sx in (1, -1):
            d += .010 * g(q, V(.048 * sx, -.066, -.012), .016)        # cheekbones
            d -= .016 * gaunt * g(q, V(.05 * sx, -.058, -.048), .022)  # hollow cheeks
            d -= .008 * g(q, V(.07 * sx, -.02, .045), .03)              # temples
            d += .006 * g(q, V(.045 * sx, -.04, -.085), .02)             # jaw angle
        # nose: ridge + tip, half rotted away on +x
        nose = .022 * g(q, V(0, -.095, -.012), .016) + .012 * g(q, V(0, -.092, .008), .011)
        if rot_nose and x > .002: nose *= .25
        d += nose
        # mouth cavity (open jaw): push in a wide oval
        mo = g(V(q.x * .75, q.y, (q.z + .052) * (1.5 - jaw_open * .6)), V(0, -.085, 0), .024)
        d -= .03 * mo * jaw_open
        d += .004 * g(q, V(0, -.09, -.088), .02)      # chin
        # lumpy skin
        d += .0025 * noise.noise(q * 60) + .0012 * noise.noise(q * 160)
        return q + n * d
    L.warp(o, f)
    L.smooth(o)
    return o

def teeth(name, col, cx=0, cy=-.071, cz=-.040, w=.028, n=12, down=False, seed=4, missing=(), mat=None):
    rng = random.Random(seed); objs = []
    for i in range(n):
        if i in missing: continue
        t = i / (n - 1) - .5
        ang = t * 2.2
        x = cx + math.sin(ang) * w; y = cy + (1 - math.cos(ang)) * w * .7
        h = .011 + rng.uniform(-.002, .004) * (1 if abs(t) < .3 else .6)
        o = L.box(f'{name}{i}', (x, y, cz + (-h / 2 if not down else h / 2)), (.0048, .0035, h / 2 * 1.0), col,
                  rot=(rng.uniform(-.25, .25), 0, -ang * .8 + rng.uniform(-.3, .3)), bevel=.0012, segs=2)
        objs.append(o)
    j = L.join(objs, name)
    if mat: L.setmat(j, mat)
    L.smooth(j); return j

def hair(name, col, head_obj, density=.55, seed=7, length=(.02, .05), r=.0016, mask=None, color_mat=None):
    """patchy strands as thin tubes on the scalp (world space)"""
    rng = random.Random(seed); objs = []
    me = head_obj.data; mw = head_obj.matrix_world; nm = mw.to_3x3()
    verts = [v for v in me.vertices]
    bm = bmesh.new()
    for v in verts:
        p = mw @ v.co; n = (nm @ v.normal).normalized()
        lp = v.co
        if lp.z < .01 or (lp.y < -.05 and lp.z < .06): continue        # scalp only
        if rng.random() > density * .12: continue
        if mask and mask(p) <= rng.random(): continue
        ln = rng.uniform(*length)
        d = (n * .6 + V(0, .5, -.6) * .5 + V(rng.uniform(-.3, .3), rng.uniform(-.3, .3), 0)).normalized()
        pts = [p - n * .002]
        for k in range(3):
            d = (d + V(0, .15, -.35)).normalized()
            pts.append(pts[-1] + d * ln / 3)
        rings = []
        for k, q in enumerate(pts):
            rad = r * (1 - k / 3.2)
            dv = (pts[min(k + 1, 3)] - pts[max(k - 1, 0)]).normalized()
            a = dv.cross(V(0, 0, 1)).normalized() if abs(dv.z) < .95 else V(1, 0, 0)
            b = dv.cross(a)
            rings.append([bm.verts.new(q + (a * math.cos(t) + b * math.sin(t)) * rad) for t in (0, 2.09, 4.19)])
        for k in range(3):
            for m in range(3):
                bm.faces.new((rings[k][m], rings[k][(m + 1) % 3], rings[k + 1][(m + 1) % 3], rings[k + 1][m]))
    o = L.mesh_obj(name, bm, col)
    if color_mat: L.setmat(o, color_mat)
    return o
