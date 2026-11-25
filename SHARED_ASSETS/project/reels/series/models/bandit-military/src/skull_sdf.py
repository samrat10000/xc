"""Cow skull as an SDF -> marching cubes. Local axes: X depth (front face = -X), Y lateral, Z up, origin at the poll.
Writes skull.npz (verts, faces, cols) and skull_front.npz (depth/mask for stencil art)."""
import numpy as np, sys
from skimage.measure import marching_cubes
from scipy.ndimage import gaussian_filter, map_coordinates
out = sys.argv[1]
H = float(sys.argv[2]) if len(sys.argv) > 2 else .0025
rng = np.random.default_rng(11)
TAB = rng.random(1 << 20).astype(np.float32)
def vnoise(p, s, off=0.):
    q = p * s + off
    i = np.floor(q).astype(np.int64); f = q - i; f = f * f * (3 - 2 * f)
    def h(dx, dy, dz):
        return TAB[(((i[..., 0] + dx) * 73856093) ^ ((i[..., 1] + dy) * 19349663) ^ ((i[..., 2] + dz) * 83492791)) & ((1 << 20) - 1)]
    x0 = h(0,0,0) * (1 - f[...,0]) + h(1,0,0) * f[...,0]; x1 = h(0,1,0) * (1 - f[...,0]) + h(1,1,0) * f[...,0]
    x2 = h(0,0,1) * (1 - f[...,0]) + h(1,0,1) * f[...,0]; x3 = h(0,1,1) * (1 - f[...,0]) + h(1,1,1) * f[...,0]
    y0 = x0 * (1 - f[...,1]) + x1 * f[...,1]; y1 = x2 * (1 - f[...,1]) + x3 * f[...,1]
    return (y0 * (1 - f[...,2]) + y1 * f[...,2]) * 2 - 1
def fbm(p, s, oct=4, off=0.):
    a, t, n = 1., 0., 0.
    for k in range(oct):
        t += a * vnoise(p, s * 2 ** k, off + k * 17.3); n += a; a *= .5
    return t / n
def V(*a): return np.array(a, np.float32)
def length(v): return np.sqrt((v * v).sum(-1))
def ell(p, c, r):  # approx ellipsoid sdf
    q = (p - c) / r; k0 = length(q); k1 = length(q / r)
    return k0 * (k0 - 1) / np.maximum(k1, 1e-6)
def cap(p, a, b, ra, rb=None):
    rb = ra if rb is None else rb
    pa = p - a; ba = b - a; t = np.clip((pa * ba).sum(-1) / (ba @ ba), 0, 1)
    return length(pa - ba * t[..., None]) - (ra + (rb - ra) * t)
def rbox(p, c, hs, r):
    q = np.abs(p - c) - (hs - r)
    return length(np.maximum(q, 0)) + np.minimum(q.max(-1), 0) - r
def torus(p, c, n, R, r):
    n = n / np.linalg.norm(n); d = p - c; h = d @ n
    rad = length(d - h[..., None] * n)
    return np.sqrt((rad - R) ** 2 + h ** 2) - r
def smin(a, b, k):
    h = np.clip(.5 + .5 * (b - a) / k, 0, 1); return b * (1 - h) + a * h - k * h * (1 - h)
def ssub(a, b, k):  # a minus b
    return -smin(-a, b, k)
def polyline_dist(p, pts):
    d = np.full(p.shape[:-1], 1e9, np.float32)
    for a, b in zip(pts[:-1], pts[1:]):
        d = np.minimum(d, cap(p, V(*a), V(*b), 0.))
    return d

BULLET = V(-.012, .055, -.175)
ON = V(-.72, .62, .1); ON = ON / np.linalg.norm(ON); OC = V(.02, .168, -.285)
def sdf(p):
    y = p[..., 1]; ay = np.abs(y); pm = p.copy(); pm[..., 1] = ay  # mirrored
    z = p[..., 2]
    ZP = [-.75, -.62, -.45, -.30, -.20, -.04, .02]
    WP = [.040, .052, .075, .100, .122, .140, .130]
    DP = [.030, .036, .045, .060, .066, .062, .04]
    CP = [.028, .03, .036, .046, .055, .062, .065]
    hw = np.interp(z, ZP, WP); hd = np.interp(z, ZP, DP); cx = np.interp(z, ZP, CP)
    hd = hd * (1 - .25 * (ay / np.maximum(hw, 1e-3)) ** 2)      # rounded cross-section
    qx = np.abs(p[..., 0] - cx) - hd; qy = ay - hw
    face = np.sqrt(np.maximum(qx, 0) ** 2 + np.maximum(qy, 0) ** 2) + np.minimum(np.maximum(qx, qy), 0)
    face = np.maximum(face - .02, np.maximum(z - .0, -.76 - z))
    d = face
    d = smin(d, cap(pm, V(.065, 0, -.04), V(.075, .17, -.035), .058, .05), .06)            # poll
    d = smin(d, ell(p, V(.07, 0, .0), V(.05, .075, .045)), .03)                     # intercornual bump
    d = smin(d, cap(pm, V(.075, .14, -.03), V(.085, .245, -.005), .048, .036), .03) # horn cores
    d = smin(d, ell(pm, V(.06, .14, -.28), V(.065, .065, .075)), .04)               # orbit mass
    d = smin(d, torus(pm, OC, ON, .054, .02), .035)
    d = smin(d, cap(pm, V(.0, .09, -.225), V(.02, .19, -.235), .02, .016), .03)       # brow ridge                                 # orbit rims
    d = smin(d, cap(pm, V(-.012, .03, -.30), V(-.004, .022, -.625), .019, .013), .02)   # nasal bones
    d = smin(d, cap(pm, V(.03, .1, -.37), V(.03, .075, -.5), .022, .014), .03)          # facial tuberosity
    d = ssub(d, ell(pm, V(-.01, .118, -.46), V(.045, .035, .09)), .02)                  # sunken cheeks
    # premaxilla prongs
    d = smin(d, cap(pm, V(.03, .036, -.64), V(.012, .022, -.785), .016, .01), .02)
    # cavities
    d = ssub(d, ell(p, V(.005, 0, -.675), V(.07, .036, .075)) + .01 * fbm(p, 30, 2, 4.), .012)                    # nasal aperture
    d = ssub(d, cap(pm, OC + ON * .03, OC - ON * .07, .044, .036), .008)                  # eye sockets (deep)
    d = ssub(d, ell(p, V(-.03, -.0, -.30), V(.02, .05, .07)), .03)                       # forehead dish between orbits
    d = np.maximum(d, p[..., 0] - .14)                                                  # flat back
    # bullet hole + broken orbit rim chunk
    bh = cap(p, BULLET + V(-.05, 0, 0), BULLET + V(.2, 0, 0), .011)
    d = np.maximum(d, -bh)
    chip = length(p - V(-.005, -.19, -.24)) - (.03 + .012 * fbm(p, 60))
    d = np.maximum(d, -chip)
    # sutures & cracks (shallow grooves)
    sut = polyline_dist(p, [(-.03, 0, -.03), (-.03, .008, -.07), (-.03, -.006, -.11), (-.03, .007, -.15), (-.03, -.005, -.2), (-.03, .006, -.25), (-.03, 0, -.3)])
    sut = np.minimum(sut, polyline_dist(p, [(-.02, -.15, -.07), (-.03, -.1, -.08), (-.03, -.05, -.065), (-.03, 0, -.08), (-.03, .05, -.066), (-.03, .1, -.08), (-.02, .15, -.07)]))
    # radial cracks from bullet hole
    ang = np.arctan2(p[..., 2] - BULLET[2], p[..., 1] - BULLET[1]); rr = np.sqrt((p[..., 1] - BULLET[1]) ** 2 + (p[..., 2] - BULLET[2]) ** 2)
    rad = np.abs(np.sin(ang * 3.5 + 6 * fbm(p, 9, 2))) * rr
    radc = np.where(rr < .11, rad, 1.)
    n1 = np.abs(fbm(p, 11, 3, 5.)); n2 = np.abs(fbm(p, 23, 2, 9.))
    crack = np.clip(1 - n1 / .035, 0, 1) * (fbm(p, 4, 2, 3.) > .1) + np.clip(1 - n2 / .03, 0, 1) * .5
    groove = .0035 * np.clip(1 - sut / .0035, 0, 1) + .004 * np.clip(1 - radc / .004, 0, 1) + .0025 * crack
    d = d + groove
    d = d + .0016 * fbm(p, 70, 3, 2.) + .0008 * fbm(p, 220, 2, 8.)    # pitted bone
    return d, crack, sut, radc

lo = V(-.07, -.31, -.81); hi = V(.16, .31, .08)
ax = [np.arange(lo[i], hi[i], H, dtype=np.float32) for i in range(3)]
X, Y, Z = np.meshgrid(*ax, indexing='ij')
P = np.stack([X, Y, Z], -1)
vol = np.empty(X.shape, np.float32)
for i in range(0, X.shape[0], 8):
    vol[i:i + 8] = sdf(P[i:i + 8])[0]
print('grid', vol.shape, flush=True)
verts, faces, nrm, _ = marching_cubes(vol, 0., spacing=(H, H, H))
verts = verts + lo
print('mc', len(verts), len(faces), flush=True)
blur = gaussian_filter(vol, 5)
idx = ((verts - lo) / H).T
cav = map_coordinates(blur, idx, order=1) - map_coordinates(vol, idx, order=1)   # >0 concave
d, crack, sut, radc = sdf(verts.astype(np.float32))
def lin(h): c = np.array([int(h[i:i+2], 16) / 255 for i in (1, 3, 5)]); return np.where(c <= .04045, c / 12.92, ((c + .055) / 1.055) ** 2.4)
ivory, pale, brown, dirt, blood, old = lin('#b9aa86'), lin('#d6cbb0'), lin('#7a5d3e'), lin('#3d2e20'), lin('#4a0a08'), lin('#2a0805')
v = verts
var = fbm(v, 9, 3, 1.)[:, None]
col = ivory * (1 - .5 * np.clip(var, 0, 1)) + pale * .5 * np.clip(var, 0, 1)
stain = np.clip(fbm(v, 5, 4, 4.) * 1.6 + .1, 0, 1)[:, None]
col = col * (1 - .55 * stain) + lin('#8f7652') * .55 * stain
sock = np.clip(1 - (cap(np.stack([v[:,0], np.abs(v[:,1]), v[:,2]],-1).astype(np.float32), OC + ON * .0, OC - ON * .1, .05, .04)) / .015, 0, 1)
cv = np.clip(np.maximum(cav / .004, sock), 0, 1)[:, None]
col = col * (1 - .85 * cv) + lin('#1e150e') * .85 * cv
nas = np.clip(1 - (ell(v.astype(np.float32), V(.005, 0, -.675), V(.07, .036, .075))) / .02, 0, 1)[:, None]
col = col * (1 - .85 * nas) + lin('#1e150e') * .85 * nas
grv = np.clip(np.maximum(crack, np.clip(1 - sut / .004, 0, 1)), 0, 1)[:, None]
grv = np.maximum(grv, np.clip(1 - radc / .005, 0, 1)[:, None])
col = col * (1 - .8 * grv) + dirt * .8 * grv
low = np.clip((-v[:, 2] - .55) / .25, 0, 1)[:, None]                 # soot/road grime toward the snout tip
col = col * (1 - .55 * low) + brown * .55 * low
sp = np.clip((fbm(v, 14, 3, 21.) - .15) * 3, 0, 1)[:, None] * .6
col = col * (1 - sp) + lin('#5e4a33') * sp
# blood: around bullet hole and drips running down the face, plus tears from the orbits
def drips(cy, cz, w0, ln, seed, n=5):
    m = np.zeros(len(v), np.float32)
    r = np.random.default_rng(seed)
    for k in range(n):
        y0 = cy + r.uniform(-w0, w0); L = ln * r.uniform(.35, 1.)
        dz = cz - v[:, 2]
        wig = .004 * np.sin(dz * 60 + k) + .003 * fbm(v, 30, 2, k * 3.)
        w = .007 * (1 - .6 * np.clip(dz / L, 0, 1)) + .002
        on = np.clip((w - np.abs(v[:, 1] - y0 - wig)) / .003, 0, 1) * (dz > 0) * np.clip((L - dz) / .01, 0, 1) * (v[:, 0] < .05)
        bead = np.clip((.009 - np.sqrt((dz - L) ** 2 + (v[:, 1] - y0 - wig) ** 2)) / .003, 0, 1) * (v[:, 0] < .05)
        m = np.maximum(m, np.maximum(on, bead))
    return m
bl = np.clip(1 - (np.sqrt((v[:, 1] - BULLET[1]) ** 2 + (v[:, 2] - BULLET[2]) ** 2) - .012) / .03, 0, 1) * (v[:, 0] < .03)
bl = np.maximum(bl, drips(BULLET[1], BULLET[2], .018, .34, 3, 4))
for s in (1, -1):
    bl = np.maximum(bl, .85 * drips(s * .14, -.31, .025, .22, 7 + s, 3))
bl = bl * (.75 + .25 * (fbm(v, 40, 2, 6.) > -.2))
bt = np.clip(fbm(v, 25, 2, 12.) * .5 + .5, 0, 1)[:, None]
bcol = blood * bt + old * (1 - bt)
col = col * (1 - bl[:, None]) + bcol * bl[:, None]
np.savez_compressed(out, verts=verts.astype(np.float32), faces=faces.astype(np.int32), cols=col.astype(np.float32),
                    rough=(.62 + .25 * cv[:, 0] - .3 * bl).astype(np.float32))
# front orthographic depth for stencil art (looking along +X)
occ = vol < 0
first = np.where(occ.any(0), occ.argmax(0), -1)
np.savez_compressed(out.replace('.npz', '_front.npz'), depth=first, H=H, lo=lo, cav=(blur - vol)[0:1].astype(np.float32))
print('saved', flush=True)
