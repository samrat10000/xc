# Night Terror Ep1 v7 sets. Exec'd inside shots2.py (shares sc, col, K, L, A, V, camera, kick, flicker, _fcurves ...).
# cut40: one-take POV from the dead elevator down a pre-war Manhattan stair hall to the Crawler on the wall.
import numpy as np
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter   # only needed to (re)make textures; the kit ships ep1/tex
except ImportError:
    Image = ImageDraw = ImageFont = ImageFilter = None
from mathutils import Matrix
TEX = os.path.join(HERE, 'tex'); os.makedirs(TEX, exist_ok=True)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def _font(s):
    if ImageFont is None: return None
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/arial.ttf'):
        try: return ImageFont.truetype(p, s)
        except OSError: pass
    return ImageFont.load_default()

# ------------------------------------------------------------------ painted textures (made once, cached in ep1/tex)
def _tex(name, make):
    p = os.path.join(TEX, name)
    if not os.path.exists(p): make(p)
    return bpy.data.images.load(p, check_existing=True)

def _noise2(h, w, sc_, seed):
    r = np.random.default_rng(seed); g = r.random((h // sc_ + 2, w // sc_ + 2)).astype(np.float32)
    im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im).astype(np.float32) / 255

def make_hex(p):
    """white 1-inch hex mosaic with black rosettes and a black border band, dirt and a few broken tiles"""
    W_ = 2048; im = Image.new('RGB', (W_, W_), (150, 146, 138)); d = ImageDraw.Draw(im)
    r = 12.5; w = math.sqrt(3) * r; rng = random.Random(5)
    rows = int(W_ / (1.5 * r)) + 2; cols = int(W_ / w) + 2
    for j in range(rows):
        for i in range(cols):
            cx = i * w + (w / 2 if j % 2 else 0); cy = j * 1.5 * r
            ii, jj = i - (j % 2 == 0) * 0, j
            ros = ((jj % 8) in (3, 4) and (ii % 8) in (3, 4)) or ((jj % 8) == 2 and (ii % 8) == 3) or ((jj % 8) == 5 and (ii % 8) == 3)
            border = (jj % 64) in (60, 61) or (ii % 56) in (52, 53)
            base = 34 if border else rng.randint(196, 222)
            if rng.random() < .004: base = 70                       # cracked / missing tile
            col_ = (base, base - (2 if base > 100 else 0), base - (6 if base > 100 else 0))
            pts = [(cx + (r - 1.6) * math.cos(math.radians(60 * k + 30)), cy + (r - 1.6) * math.sin(math.radians(60 * k + 30))) for k in range(6)]
            d.polygon(pts, fill=col_)
    a = np.asarray(im).astype(np.float32)
    dirt = _noise2(W_, W_, 180, 3) * .55 + _noise2(W_, W_, 40, 4) * .45
    a *= (1 - .32 * np.clip((dirt - .45) / .4, 0, 1))[..., None]
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(p)

def make_smear(p):
    """four-finger blood drag (left to right), thick at the palm, with drips, RGBA"""
    W_, H_ = 1600, 360; a = np.zeros((H_, W_), np.float32); rng = random.Random(9)
    yy, xx = np.mgrid[0:H_, 0:W_].astype(np.float32)
    for k, y0 in enumerate((95, 150, 205, 255)):
        wob = 6 * np.sin(xx / 140 + k) + 4 * np.sin(xx / 47 + 2 * k)
        width = 15 * (1 - xx / W_) ** .6 + 2
        a = np.maximum(a, np.clip(1 - np.abs(yy - y0 - wob - xx * .04) / width, 0, 1) * np.clip(1.25 - xx / W_, 0, 1))
    a = np.maximum(a, np.clip(1 - np.hypot(xx - 110, yy - 175) / 120, 0, 1) * 1.2)         # palm
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    for _ in range(10):
        x = rng.uniform(60, 700); y = rng.uniform(150, 260); L_ = rng.uniform(30, 110)
        d.line([(x, y), (x + rng.uniform(-3, 3), y + L_)], fill=200, width=rng.randint(3, 6))
    al = np.asarray(im.filter(ImageFilter.GaussianBlur(1.6))).astype(np.float32) / 255
    al *= .55 + .45 * _noise2(H_, W_, 12, 2)
    rgb = np.zeros((H_, W_, 3), np.float32); rgb[...] = (70, 6, 8)
    Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8), 'RGBA').save(p)

def make_pool(p):
    S = 768; yy, xx = np.mgrid[0:S, 0:S].astype(np.float32) / S - .5
    ang = np.arctan2(yy, xx); rr = np.hypot(xx, yy)
    edge = .30 + .05 * np.sin(3 * ang + 1) + .03 * np.sin(7 * ang) + .02 * np.sin(13 * ang + 2)
    al = np.clip((edge - rr) / .02, 0, 1)
    rgb = np.zeros((S, S, 3), np.float32); rgb[...] = (38, 3, 4)
    Image.fromarray(np.dstack([rgb, al * 245]).astype(np.uint8), 'RGBA').save(p)

def make_notice(p):
    W_, H_ = 600, 780; im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((20, 40, W_ - 20, H_ - 20), fill=(232, 226, 208, 255))
    d.text((W_ / 2, 120), 'NYC EMERGENCY', font=_font(46), fill=(20, 20, 24), anchor='mm')
    d.text((W_ / 2, 170), 'MANAGEMENT', font=_font(46), fill=(20, 20, 24), anchor='mm')
    d.rectangle((50, 215, W_ - 50, 300), fill=(170, 20, 22))
    d.text((W_ / 2, 258), 'SHELTER IN PLACE', font=_font(44), fill=(250, 245, 240), anchor='mm')
    for i, s in enumerate(['Stay inside. Lock your door.', 'Do NOT use the elevators.', 'Do not open the door to', 'anyone showing symptoms.', 'Await further instructions.']):
        d.text((60, 345 + i * 52), s, font=_font(30), fill=(30, 30, 34))
    for x0 in (30, W_ - 150):                                                   # tape strips
        d.rectangle((x0, 20, x0 + 120, 64), fill=(214, 205, 170, 210))
    a = np.asarray(im).astype(np.float32); n = _noise2(H_, W_, 30, 7)
    a[..., :3] *= (.82 + .18 * n)[..., None]
    Image.fromarray(a.astype(np.uint8), 'RGBA').save(p)

def make_label(text, fg, bg, size=(512, 200), fs=120):
    def mk(p):
        im = Image.new('RGB', size, bg); d = ImageDraw.Draw(im)
        d.text((size[0] / 2, size[1] / 2), text, font=_font(fs), fill=fg, anchor='mm'); im.save(p)
    return mk

def make_flyer(kind):
    def mk(p):
        W_, H_ = 510, 660; im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        paper = (226, 221, 204, 255) if kind != 'laundry' else (238, 214, 120, 255)
        d.rectangle((10, 10, W_ - 10, H_ - 10), fill=paper)
        if kind == 'missing':
            d.text((W_ / 2, 70), 'MISSING', font=_font(78), fill=(150, 18, 18), anchor='mm')
            d.rectangle((95, 125, W_ - 95, 420), fill=(92, 90, 86))
            d.ellipse((190, 165, 320, 300), fill=(150, 146, 138)); d.rectangle((160, 300, 350, 420), fill=(120, 118, 112))
            for i, t_ in enumerate(['HAVE YOU SEEN ME?', 'Maya R., 9 yrs', 'last seen Apt 6B', 'Fri night  CALL 212-555-0148']):
                d.text((W_ / 2, 455 + i * 44), t_, font=_font(30 if i else 34), fill=(25, 25, 28), anchor='mm')
        elif kind == 'laundry':
            d.text((W_ / 2, 110), 'LAUNDRY ROOM', font=_font(52), fill=(20, 20, 20), anchor='mm')
            d.text((W_ / 2, 180), 'CLOSED', font=_font(80), fill=(20, 20, 20), anchor='mm')
            for i, t_ in enumerate(['until further notice', '- Management', '', 'DO NOT GO TO', 'THE BASEMENT']):
                d.text((W_ / 2, 290 + i * 54), t_, font=_font(34), fill=(30, 30, 30), anchor='mm')
        else:
            d.text((W_ / 2, 90), 'TENANT MEETING', font=_font(46), fill=(24, 24, 60), anchor='mm')
            for i, t_ in enumerate(['Lobby, Thursday 8 PM', 'Re: noises in the walls', 'and the smell on 9', 'ALL tenants please attend']):
                d.text((W_ / 2, 190 + i * 60), t_, font=_font(32), fill=(30, 30, 40), anchor='mm')
        d.rectangle((W_ / 2 - 60, 0, W_ / 2 + 60, 36), fill=(214, 205, 170, 220))   # tape
        a = np.asarray(im).astype(np.float32); n_ = _noise2(H_, W_, 25, 11)
        a[..., :3] *= (.7 + .3 * n_)[..., None]
        Image.fromarray(a.astype(np.uint8), 'RGBA').save(p)
    return mk

def make_tag(text, colr, seed):
    """spray-painted word: soft overspray, a hard core and drips"""
    def mk(p):
        W_, H_ = 1400, 520; rng = random.Random(seed)
        base = Image.new('L', (W_, H_), 0); d = ImageDraw.Draw(base)
        d.text((W_ / 2, H_ / 2 - 30), text, font=_font(330), fill=255, anchor='mm')
        base = base.rotate(rng.uniform(-6, 6), resample=Image.BICUBIC)
        a = np.asarray(base).astype(np.float32) / 255
        sh = (12 * np.sin(np.arange(H_) / 37.) + 6 * np.sin(np.arange(H_) / 11.)).astype(int)   # shaky hand
        a = np.stack([np.roll(a[y], sh[y]) for y in range(H_)])
        core = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255
        spray = np.asarray(Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))).astype(np.float32) / 255
        dots = (np.random.default_rng(seed).random((H_, W_)) < spray * .35).astype(np.float32)
        al = np.clip(core * 1.1, 0, 1) * .95 + dots * .5
        dr = Image.fromarray((np.clip(al, 0, 1) * 255).astype(np.uint8)); dd = ImageDraw.Draw(dr)
        ys, xs = np.nonzero(a[:-60] > .5)
        for _ in range(16):
            i = rng.randrange(len(xs)); x, y = xs[i], ys[i]
            if y > H_ * .45: dd.line([(x, y), (x + rng.uniform(-2, 2), y + rng.uniform(40, 150))], fill=230, width=rng.randint(4, 7))
        al = np.asarray(dr.filter(ImageFilter.GaussianBlur(2.2))).astype(np.float32) / 255 * (.55 + .3 * _noise2(H_, W_, 18, seed))
        rgb = np.zeros((H_, W_, 3), np.float32); rgb[...] = colr
        Image.fromarray(np.dstack([rgb, al * 255]).astype(np.uint8), 'RGBA').save(p)
    return mk

def make_claw(p):
    W_, H_ = 900, 500; im = Image.new('L', (W_, H_), 0); d = ImageDraw.Draw(im); rng = random.Random(4)
    for k in range(4):
        x0 = 120 + k * 70 + rng.uniform(-10, 10)
        pts = [(x0 + t * 520 + 30 * math.sin(t * 3 + k), 60 + t * 330 + k * 18) for t in np.linspace(0, 1, 20)]
        for i in range(len(pts) - 1): d.line([pts[i], pts[i + 1]], fill=255, width=int(14 * (1 - i / 22)) + 2)
    al = np.asarray(im.filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
    rgb = np.zeros((H_, W_, 3), np.float32); rgb[...] = (34, 22, 16)
    Image.fromarray(np.dstack([rgb, al * 235]).astype(np.uint8), 'RGBA').save(p)

# ------------------------------------------------------------------ materials
def _bsdf(name):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    return m, nt, nt.nodes, nt.links, nt.nodes['Principled BSDF']

def m_marble(name='Marble'):
    m, nt, n, l, bs = _bsdf(name); co = K.coord(n)
    mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (2.5, 5.0, 2.5); l.new(co, mp.inputs['Vector'])
    vn = n.new('ShaderNodeTexNoise'); vn.inputs['Scale'].default_value = 3.5; vn.inputs['Detail'].default_value = 9; vn.inputs['Distortion'].default_value = 5.5
    l.new(mp.outputs[0], vn.inputs['Vector'])
    vein = n.new('ShaderNodeValToRGB'); cr = vein.color_ramp
    cr.elements[0].position = .493; cr.elements[0].color = (*K.C('#6e6862'), 1); cr.elements[1].position = .5; cr.elements[1].color = (*K.C('#b3ada2'), 1)
    l.new(vn.outputs['Fac'], vein.inputs[0])
    g = K.noise_n(n, l, co, 1.1, 5, .6)
    c = K.mixc(n, l, K.mrange(n, l, g, .45, .75), vein.outputs[0], K.C('#7a6f62'))      # traffic grime
    l.new(c, bs.inputs['Base Color']); l.new(K.mrange(n, l, g, .4, .8, .18, .55), bs.inputs['Roughness'])
    return m

def m_paint(name, col_, under='#5d5246', peel=.63, stain=True):
    """old wall paint: flaking patches show the plaster under, water stains run down"""
    m, nt, n, l, bs = _bsdf(name); co = K.coord(n)
    pn = K.noise_n(n, l, co, 1.6, 3, .5)
    pk = K.mrange(n, l, pn, peel, peel + .015)
    c = K.mixc(n, l, pk, K.C(col_), K.C(under))
    if stain:
        mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (6, 6, .35); l.new(co, mp.inputs['Vector'])
        sn = n.new('ShaderNodeTexNoise'); sn.inputs['Scale'].default_value = 2; sn.inputs['Detail'].default_value = 6; l.new(mp.outputs[0], sn.inputs['Vector'])
        c = K.mixc(n, l, K.math_n(n, l, 'MULTIPLY', K.mrange(n, l, sn.outputs['Fac'], .55, .75), .55), c, K.C('#4a3e2c'))
    fine = K.noise_n(n, l, co, 60, 4, .6)
    c = K.mixc(n, l, K.math_n(n, l, 'MULTIPLY', fine, .18), c, K.C('#2a241e'))
    l.new(c, bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = .78
    bp = n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = .5; bp.inputs['Distance'].default_value = .002
    l.new(K.math_n(n, l, 'ADD', pk, K.math_n(n, l, 'MULTIPLY', fine, .2)), bp.inputs['Height']); l.new(bp.outputs[0], bs.inputs['Normal'])
    return m

def m_iron(name='CastIron'):
    m, nt, n, l, bs = _bsdf(name); co = K.coord(n); r = K.noise_n(n, l, co, 14, 6, .7)
    l.new(K.mixc(n, l, K.mrange(n, l, r, .58, .68), K.C('#1b1d1a'), K.C('#4a2c1a')), bs.inputs['Base Color'])
    bs.inputs['Metallic'].default_value = .75; bs.inputs['Roughness'].default_value = .5; return m

def m_wood(name, col_='#3a2214', rough=.32):
    m, nt, n, l, bs = _bsdf(name); co = K.coord(n)
    wv = n.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value = 9; wv.inputs['Distortion'].default_value = 6; wv.inputs['Detail'].default_value = 4
    l.new(co, wv.inputs['Vector'])
    c = K.mixc(n, l, K.mrange(n, l, wv.outputs['Fac'], .2, .9), K.C(col_), K.C('#1c0f08'))
    l.new(c, bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = rough; bs.inputs['Coat Weight'].default_value = .3
    return m

def m_brass(name='Brass'):
    m, nt, n, l, bs = _bsdf(name); co = K.coord(n); r = K.noise_n(n, l, co, 9, 6, .65)
    l.new(K.mixc(n, l, K.mrange(n, l, r, .45, .7), K.C('#a8823e'), K.C('#3c3120')), bs.inputs['Base Color'])
    bs.inputs['Metallic'].default_value = 1; l.new(K.mrange(n, l, r, 0, 1, .22, .55), bs.inputs['Roughness']); return m

def m_img(name, img, alpha=False, rough=.6, emit=0., proj='UV'):
    m, nt, n, l, bs = _bsdf(name); t = n.new('ShaderNodeTexImage'); t.image = img
    l.new(t.outputs['Color'], bs.inputs['Base Color']); bs.inputs['Roughness'].default_value = rough
    if alpha:
        l.new(t.outputs['Alpha'], bs.inputs['Alpha'])
        try: m.surface_render_method = 'DITHERED'
        except Exception: pass
    if emit:
        l.new(t.outputs['Color'], bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = emit
    return m, t

def m_tile(img):
    m, t = m_img('HexTile', img, rough=.35)
    n = m.node_tree.nodes; l = m.node_tree.links
    co = K.coord(n); mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1 / 2.8, 1 / 2.8, 1); l.new(co, mp.inputs['Vector'])
    l.new(mp.outputs[0], t.inputs['Vector'])
    bs = n['Principled BSDF']; bp = n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = .35
    gm = n.new('ShaderNodeRGBToBW'); l.new(t.outputs['Color'], gm.inputs[0]); l.new(gm.outputs[0], bp.inputs['Height']); l.new(bp.outputs[0], bs.inputs['Normal'])
    return m

def m_static(name='TVStatic', strength=2.5):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; n = nt.nodes; l = nt.links
    for x in list(n): n.remove(x)
    out = n.new('ShaderNodeOutputMaterial'); em = n.new('ShaderNodeEmission'); em.inputs['Strength'].default_value = strength
    nz = n.new('ShaderNodeTexNoise'); nz.noise_dimensions = '4D'; nz.inputs['Scale'].default_value = 420; nz.inputs['Detail'].default_value = 0
    l.new(K.coord(n), nz.inputs['Vector'])
    fc = nz.inputs['W'].driver_add('default_value'); fc.driver.expression = 'frame*7.13'
    ramp = n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = .38; ramp.color_ramp.elements[0].color = (.02, .02, .03, 1)
    ramp.color_ramp.elements[1].position = .62; ramp.color_ramp.elements[1].color = (*K.C('#dfe9ff'), 1)
    l.new(nz.outputs['Fac'], ramp.inputs[0]); l.new(ramp.outputs[0], em.inputs['Color']); l.new(em.outputs[0], out.inputs[0])
    return m

def m_glass_rain(name='RainGlass'):
    m, nt, n, l, bs = _bsdf(name); co = K.coord(n)
    bs.inputs['Base Color'].default_value = (.6, .65, .7, 1); bs.inputs['Roughness'].default_value = .05
    bs.inputs['Transmission Weight'].default_value = 1; bs.inputs['IOR'].default_value = 1.45
    mp = n.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 1, .18); l.new(co, mp.inputs['Vector'])
    vo = n.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value = 60; l.new(mp.outputs[0], vo.inputs['Vector'])
    # sparse drops only (Sam 2026-11-23: the all-over cell bump read as grainy black dots): bump just inside small cell centres
    lt = n.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = .09; l.new(vo.outputs['Distance'], lt.inputs[0])
    wn = n.new('ShaderNodeTexNoise'); wn.inputs['Scale'].default_value = 3; l.new(co, wn.inputs['Vector'])
    gt = n.new('ShaderNodeMath'); gt.operation = 'GREATER_THAN'; gt.inputs[1].default_value = .55; l.new(wn.outputs['Fac'], gt.inputs[0])
    mu = n.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; l.new(lt.outputs[0], mu.inputs[0]); l.new(gt.outputs[0], mu.inputs[1])
    bp = n.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = .08; bp.inputs['Distance'].default_value = .02
    l.new(mu.outputs[0], bp.inputs['Height']); l.new(bp.outputs[0], bs.inputs['Normal'])
    return m

# ------------------------------------------------------------------ geometry helpers
def bx(name, loc, size, mat, rot=(0, 0, 0), bevel=0., ink=0.):
    o = L.box(name, tuple(loc), tuple(size), col, rot=rot, bevel=bevel); L.apply_transform(o) if rot == (0, 0, 0) else None
    L.setmat(o, mat)
    if ink: L.hull(o, col, ink)
    return o

def slope_box(name, p0, p1, thick, width, mat, x, ink=0.):
    """a slab from p0=(y,z) to p1=(y,z), centred at x, thickness along its normal"""
    y0, z0 = p0; y1, z1 = p1; Ln = math.hypot(y1 - y0, z1 - z0); ang = math.atan2(z1 - z0, y1 - y0)
    return bx(name, (x, (y0 + y1) / 2, (z0 + z1) / 2), (width, Ln, thick), mat, rot=(ang, 0, 0), ink=ink)

def join_ink(objs, name, ink):
    o = L.join(objs, name)
    if ink: L.hull(o, col, ink)
    return o

def baluster(x, y, z0, h, mat):
    k = [0, .04, .07, .12, .2, .32, .45, .55, .66, .78, .9, .95, 1.]
    rr = [.018, .018, .012, .016, .009, .009, .02, .009, .009, .014, .01, .016, .012]
    return L.tube('bal', [V((x, y, z0 + h * t)) for t in k], rr, col, sides=8)

def rail_run(pts, r, mat, ink=.0):
    o = L.tube('rail', [V(p) for p in pts], r, col, sides=12); L.setmat(o, mat)
    if ink: L.hull(o, col, ink)
    return o

def light(kind, loc, energy, col_, size=.1, rot=(0, 0, 0), name='l'):
    ld = bpy.data.lights.new(name, kind); ld.energy = energy; ld.color = K.C(col_)
    if kind == 'AREA': ld.size = size
    else: ld.shadow_soft_size = size
    lo = bpy.data.objects.new(name, ld); col.objects.link(lo); lo.location = loc; lo.rotation_euler = rot
    return ld, lo

def strobe(ld, f0, f1, base, seed=11, on=3, off=(4, 9)):
    rng = random.Random(seed); f = f0
    while f <= f1:
        ld.energy = base; ld.keyframe_insert('energy', frame=f)
        ld.energy = 0; ld.keyframe_insert('energy', frame=f + on)
        f += on + rng.randint(*off)
    for fc in _fcurves(ld.animation_data.action):
        for k in fc.keyframe_points: k.interpolation = 'CONSTANT'

def fire_flicker(ld, f0, f1, base, seed=5):
    nz = A.Noise(seed)
    for f in range(f0, f1 + 1, 2):
        ld.energy = base * (.75 + .35 * nz(f * .21) + .15 * nz(f * .9 + 3)); ld.keyframe_insert('energy', frame=f)

# ------------------------------------------------------------------ the stair hall
H7, N7, RUN7 = 3.4, 10, .27
RISE7 = H7 / 2 / N7; LF7 = RUN7 * N7
XW, YN, YS = 1.3, 1.5, -LF7 - 1.5           # walls
FLA, FLB = .725, -.725                      # flight centre lines (A runs down toward -y, B back toward +y)
WELL = .25

def stairhall(floors=3, labels=('PH', '11', '10')):
    marble = m_marble(); paint = m_paint('WallPaint', '#8a8468', peel=.68); lowpaint = m_paint('WainscotPaint', '#3b4a3a', '#2a2219', .6)
    soffit = m_paint('SoffitPaint', '#8c8771', '#4a4034', .66, stain=True)
    iron = m_iron(); oak = m_wood('Oak'); brass = m_brass(); door_w = m_wood('DoorWood', '#2b170f', .45)
    tile = m_tile(_tex('hex.png', make_hex)); dark = K.concrete('ShaftDark', '#0b0b0c')
    zt, zb = 3.2, -floors * H7 - .3
    # walls: lower wainscot band per floor plus upper paint, ceiling slab on top
    for x in (XW, -XW):
        bx('wall', (x + (.05 if x > 0 else -.05), (YN + YS) / 2, (zt + zb) / 2), (.1, YN - YS + .2, zt - zb), paint)
    bx('wallN', (0, YN + .05, (zt + zb) / 2), (2 * XW + .2, .1, zt - zb), paint)
    bx('wallS', (0, YS - .05, (zt + zb) / 2), (2 * XW + .2, .1, zt - zb), paint)
    bx('ceiling', (0, (YN + YS) / 2, zt + .05), (2 * XW + .2, YN - YS + .2, .1), soffit)
    for k in range(floors):
        z = -k * H7; zm = z - H7 / 2
        bx('landing', (0, YN / 2, z - .08), (2 * XW, YN, .16), tile)
        bx('midland', (0, -LF7 - .75, zm - .08), (2 * XW, 1.5, .16), tile)
        for x in (XW - .005, -XW + .005):                                       # baseboards
            bx('base', (x, YN / 2, z + .08), (.03, YN, .16), door_w); bx('base', (x, -LF7 - .75, zm + .08), (.03, 1.5, .16), door_w)
        # flights
        for (xc, ya, za, dy) in ((FLA, 0., z, -1), (FLB, -LF7, zm, 1)):
            steps = []
            for i in range(N7):
                zt_ = za - RISE7 * (i + 1); y_hi = ya + dy * RUN7 * i; y_lo = ya + dy * RUN7 * (i + 1)
                steps.append(bx('tread', (xc, (y_hi + y_lo) / 2 + dy * -.015, zt_ - .022), (.95, RUN7 + .03, .045), marble))
                steps.append(bx('riser', (xc, y_hi + dy * .01, zt_ + RISE7 / 2), (.95, .02, RISE7), lowpaint))
            L.join(steps, 'flight')
            p_top = (ya, za - .22); p_bot = (ya + dy * LF7, za - H7 / 2 - .22)
            slope_box('soffit', p_top, p_bot, .06, 1.0, soffit, xc)
            sx = xc - math.copysign(.5, xc)                                     # inner stringer at the well
            slope_box('stringer', (ya, za - .02), (ya + dy * LF7, za - H7 / 2 - .02), .3, .035, iron, sx, ink=.003)
            bals = []
            nb = int(LF7 / .135)
            for j in range(nb):
                t = (j + .5) / nb; y = ya + dy * LF7 * t; zz = za - H7 / 2 * t - .02
                bals.append(baluster(sx, y, zz, .9, iron))
            join_ink(bals, 'balusters', .0025); L.setmat(bpy.data.objects[bpy.context.object.name] if False else bals[0], iron)
            rail_run([(sx, ya - dy * .05, za + .9 + .02), (sx, ya + dy * LF7, za - H7 / 2 + .9)], .032, oak, ink=.0025)
            # wall-side dado rail (brass brackets) following the slope
            wx = math.copysign(XW - .04, xc)
            rail_run([(wx, ya, za + .88), (wx, ya + dy * LF7, za - H7 / 2 + .88)], .022, oak)
        # rail wreaths around the well ends
        wr = [(WELL * math.cos(a), -LF7 - WELL * .9 * abs(math.sin(a)) - .0, zm + .9) for a in np.linspace(0, math.pi, 9)]
        rail_run(wr, .032, oak, ink=.0025)
        wr2 = [(-WELL * math.cos(a), WELL * .9 * abs(math.sin(a)), z + .92) for a in np.linspace(0, math.pi, 9)]
        if k > 0: rail_run(wr2, .032, oak, ink=.0025)
        # landing guard balusters along the well ends
        g = [baluster(WELL * math.cos(a), -LF7 - WELL * .9 * abs(math.sin(a)), zm, .9, iron) for a in np.linspace(.2, math.pi - .2, 5)]
        join_ink(g, 'guard', .0025); [L.setmat(o_, iron) for o_ in bpy.data.objects if o_.name.startswith('guard') and 'hull' not in o_.name]
        # newel post at the top of flight A on each floor
        np_ = bx('newel', (WELL, .05, z + .5), (.11, .11, 1.0), oak, bevel=.01, ink=.003)
        L.setmat(L.blob('newel cap', (WELL, .05, z + 1.06), (.07, .07, .06), col), brass)
        # door frames on the north wall: x=+.55 apartment 'C', x=-.55 elevator on PH / apartment 'A' below
        lab = labels[k]
        door(.55, z, ('LOBBY' if lab == 'L' else f'{lab}C') if lab != 'PH' else 'PH-C', door_w, brass, open_=(lab == '11'))
        if k == 0: elevator(-.6, z, brass, dark)
        else: door(-.6, z, f'{lab}A', door_w, brass)
        # EXIT sign above the flight A head, emergency twin light on the west wall
        ex = bx('exit', (FLA, YN - .03, z + 2.45), (.42, .04, .16), m_img('ExitSign', _tex('exit.png', make_label('EXIT', (255, 70, 50), (60, 6, 6))))[0])
        mat_e = ex.data.materials[0]; nds = mat_e.node_tree.nodes; mat_e.node_tree.links.new(nds['Image Texture'].outputs['Color'], nds['Principled BSDF'].inputs['Emission Color']); nds['Principled BSDF'].inputs['Emission Strength'].default_value = 3
        light('POINT', (FLA, YN - .25, z + 2.35), 2.5, '#ff3020', .05, name='exitglow')
        em = bx('emunit', (-XW + .06, .7, z + 2.55), (.08, .34, .14), K.metal('EmBox', '#bdbab0', .5))
        for dy_ in (-.12, .12): L.setmat(L.blob('emhead', (-XW + .13, .7 + dy_, z + 2.5), (.045, .045, .045), col), K.emit('EmLamp', '#fff2d8', 0 if k == 0 else 4))
        if k > 0:
            ld, lo = light('SPOT', (-XW + .2, .7, z + 2.45), 60, '#fff0d6', .03, rot=(math.radians(60), 0, math.radians(-90)), name='emlight')
            ld.spot_size = math.radians(110); ld.spot_blend = .6
            (flicker(ld, 1, 330, 60, seed=k + 3, p_off=.25) if k == 1 else strobe(ld, 1, 330, 140, seed=k))
        # stair window on the south wall of each mid landing: city fire glow, rain on the glass
        window(zm)
    # the open well: you can look straight down past the rails into the dark
    bx('pit', (0, -LF7 / 2, zb + .05), (2 * XW, LF7 + 3, .1), dark)

def door(x, z, label, wood, brass, open_=False):
    fr = [bx('frame', (x - .5, YN - .04, z + 1.08), (.08, .1, 2.16), wood), bx('frame', (x + .5, YN - .04, z + 1.08), (.08, .1, 2.16), wood),
          bx('frame', (x, YN - .04, z + 2.2), (1.08, .1, .1), wood)]
    join_ink(fr, 'doorframe', .003)
    piv = bpy.data.objects.new('door pivot', None); col.objects.link(piv); piv.location = (x - .45, YN - .07, z)
    parts = [bx('door', (x, YN - .07, z + 1.05), (.9, .05, 2.1), wood)]
    for dz in (.55, 1.5):
        parts.append(bx('panel', (x, YN - .1, z + dz), (.62, .02, .7), wood))
    parts.append(bx('knob', (x + .35, YN - .12, z + 1.0), (.05, .05, .05), brass))
    parts.append(bx('peep', (x, YN - .1, z + 1.55), (.03, .03, .03), brass))
    plate = bx('number', (x, YN - .1, z + 1.82), (.22, .01, .1), m_img(f'Num{label}', _tex(f'num_{label}.png', make_label(label, (40, 30, 10), (178, 140, 66), (440, 200), 110)), rough=.3)[0])
    parts.append(plate)
    d_ = L.join(parts, 'door ' + label); L.hull(d_, col, .0025)
    for o_ in (d_, bpy.data.objects.get(d_.name + ' hull')):
        if o_: o_.parent = piv; o_.matrix_parent_inverse = piv.matrix_world.inverted()
    if open_:
        piv.rotation_euler.z = math.radians(-72)
        # the apartment beyond: dark room, a TV hissing static, flicker on the floor and the body
        bx('aptfloor', (x, YN + 1.6, z - .05), (2.6, 3.2, .1), m_wood('AptFloor', '#2a1a10', .5))
        bx('aptback', (x, YN + 3.2, z + 1.4), (2.6, .1, 2.8), m_paint('AptWall', '#565b52'))
        bx('tv', (x + .5, YN + 3.1, z + .9), (.9, .06, .55), m_static())
        tl, to = light('AREA', (x + .5, YN + 3.0, z + .9), 18, '#cfdcff', .9, rot=(math.radians(-90), 0, 0), name='tvlight')
        rng = random.Random(4)
        for f in range(1, 331):
            tl.energy = rng.uniform(8, 28); tl.keyframe_insert('energy', frame=f)
        body = K.char('husk', V((x + .5, YN - .6, z + .14)), 0., col=col)
        body.rotation_euler = (math.radians(-88), 0, math.radians(97))   # lies across the landing, feet in the doorway
        pool = bx('pool', (x + .05, YN - 1.15, z + .003), (.9, .9, .002), m_img('Pool', _tex('pool.png', make_pool), alpha=True, rough=.08)[0])
    return piv

def elevator(x, z, brass, dark):
    fr = [bx('elframe', (x - .58, YN - .05, z + 1.1), (.12, .12, 2.2), brass), bx('elframe', (x + .58, YN - .05, z + 1.1), (.12, .12, 2.2), brass),
          bx('elframe', (x, YN - .05, z + 2.26), (1.28, .12, .14), brass)]
    join_ink(fr, 'elevator frame', .003)
    bx('eldoorL', (x - .27, YN - .06, z + 1.08), (.52, .03, 2.12), brass, ink=.0025)       # left door closed
    bx('eldoorR', (x + .43, YN - .02, z + 1.08), (.52, .03, 2.12), brass, ink=.0025)       # right door jammed half open
    bx('shaft', (x + .16, YN + .9, z - 3), (1.2, 1.6, 12), dark)
    for dx in (-.1, .05, .2):
        L.setmat(L.tube('cable', [V((x + .16 + dx, YN + .7, z + 3)), V((x + .16 + dx, YN + .7, z - 9))], .006, col, sides=6), K.metal('Cable', '#3a3836', .4))
    # art-deco floor dial over the doors, needle stuck between floors
    bx('dial', (x, YN - .06, z + 2.55), (.5, .02, .22), brass, ink=.002)
    bx('needle', (x + .05, YN - .075, z + 2.5), (.012, .01, .16), K.metal('Needle', '#111111', .4), rot=(0, math.radians(-38), 0))
    bx('callplate', (x + .8, YN - .03, z + 1.15), (.1, .02, .22), brass, ink=.002)
    for dz in (1.2, 1.1): L.setmat(L.blob('callbtn', (x + .8, YN - .045, z + dz), (.02, .02, .012), col), K.metal('DeadBtn', '#2a2622', .3))
    # the notice taped next to the call button
    bx('notice', (x + 1.08, YN - .025, z + 1.45), (.3, .005, .39), m_img('Notice', _tex('notice.png', make_notice), alpha=True, rough=.85)[0], rot=(math.radians(90), 0, math.radians(180 + 2)))

def window(zm):
    gl = m_glass_rain(); wood = m_wood('WinFrame', '#2d2018', .5)
    fr = [bx('winframe', (-.55, YS + .05, zm + 1.85), (.08, .12, 1.7), wood), bx('winframe', (.55, YS + .05, zm + 1.85), (.08, .12, 1.7), wood),
          bx('winframe', (0, YS + .05, zm + 2.7), (1.18, .12, .08), wood), bx('winframe', (0, YS + .05, zm + 1.0), (1.18, .16, .06), wood),
          bx('mullion', (0, YS + .05, zm + 1.85), (.04, .08, 1.7), wood)]
    join_ink(fr, 'window frame', .003)
    hole = bx('glass', (0, YS + .03, zm + 1.85), (1.04, .01, 1.62), gl)
    bpy.data.objects['wallS'].hide_render = False
    # outside: the burning city glow (emissive backdrop) + an orange flickering key through the glass
    sky_m = bpy.data.materials.get('CityGlow')
    if not sky_m:
        sky_m, nt, n, l, bs = _bsdf('CityGlow'); co = K.coord(n); g = K.noise_n(n, l, co, .6, 6, .6)
        c = K.mixc(n, l, K.mrange(n, l, g, .4, .75), K.C('#0b1424'), K.C('#c2521c'))
        l.new(c, bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = 1.6; bs.inputs['Base Color'].default_value = (0, 0, 0, 1)
    bx('cityglow', (0, YS - 3.5, zm + 1.8), (8, .1, 6), sky_m)
    ld, lo = light('AREA', (0, YS - 1.2, zm + 2.2), 260, '#ff8a3c', 1.6, rot=(math.radians(-80), 0, 0), name='fireglow')
    fire_flicker(ld, 1, 330, 260, seed=int(-zm * 10))

def wall_decal(name, img, center, size, rot, alpha=True):
    m, t = m_img(name, img, alpha=alpha, rough=.25 if name in ('smear', 'handprint') else .85)
    bpy.ops.mesh.primitive_plane_add(size=1, location=center, rotation=rot); o = bpy.context.object; o.name = name
    o.scale = (size[0], size[1], 1); L.setmat(o, m); return o

def pov_stairs(c, foot, looks, f0, f1, eye=1.6, seed=21):
    """walking/running POV keyed every frame from footfalls [(frame, (x,y,z))] and look targets [(frame, (x,y,z))].
    The eye travels between footfalls, dips on each heel strike and sways toward the planted foot."""
    nz = [A.Noise(seed * 10 + i) for i in range(6)]
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = 6.0
    ff = [p[0] for p in foot]; lf = [p[0] for p in looks]
    def seg(arr, frames, f):
        i = max(0, min(len(arr) - 2, sum(1 for x in frames if x <= f) - 1)); a, b = arr[i], arr[i + 1]
        t = max(0., min(1., (f - a[0]) / max(1, b[0] - a[0]))); return i, a, b, t
    for f in range(f0, f1 + 1):
        i, a, b, t = seg(foot, ff, f)
        s = t * t * (3 - 2 * t)
        p = V(a[1]).lerp(V(b[1]), s)
        dip = -.028 * math.exp(-((t - .08) / .1) ** 2) if b[0] - a[0] < 14 else 0.   # heel strike just after each footfall
        side = (.018 if i % 2 else -.018) * math.sin(math.pi * t)
        dirv = (V(b[1]) - V(a[1])); dirv.z = 0
        sidev = V((-dirv.y, dirv.x, 0)).normalized() if dirv.length > 1e-4 else V((1, 0, 0))
        loc = p + V((0, 0, eye + dip)) + sidev * side
        loc += V((nz[0](f * .17) * .012, nz[1](f * .15) * .012, nz[2](f * .2) * .006))
        j, la, lb, lt = seg(looks, lf, f)
        tgt = V(la[1]).lerp(V(lb[1]), lt * lt * (3 - 2 * lt))
        c.location = loc; aim(c, tgt)
        c.rotation_euler.x += math.radians(nz[3](f * .23) * 1.0 + (1.4 * math.exp(-((t - .1) / .12) ** 2) if b[0] - a[0] < 14 else 0))
        c.rotation_euler.y += math.radians(nz[4](f * .2) * 1.4 + (.8 if i % 2 else -1.2) * math.sin(math.pi * t))
        c.rotation_euler.z += math.radians(nz[5](f * .21) * 1.0)
        c.data.dof.focus_distance = max(.7, min(6, (tgt - loc).length))
        for pth in ('location', 'rotation_euler'): c.keyframe_insert(pth, frame=f)
        c.data.dof.keyframe_insert('focus_distance', frame=f)

def flight_feet(xc, ya, za, dy, f_start, every, side=.11, first=0):
    """one footfall per tread down a flight: returns [(frame, (x,y,z))]"""
    out = []
    for i in range(N7):
        y = ya + dy * RUN7 * (i + .55); z = za - RISE7 * (i + 1)
        out.append((f_start + i * every, (xc + (side if (i + first) % 2 else -side), y, z)))
    return out

def cut40():   # v7 one-take POV: dead elevator -> look down the well -> three flights -> 11C body -> the Crawler on the wall
    nf = 312; K.sky(sc, moon=False, fog=.009)
    stairhall(3)
    # horror dressing
    sm = _tex('smear.png', make_smear)
    wall_decal('smear', sm, (XW - .002, -LF7 * .45, -H7 - .55), (1.5, .34, 1), (math.radians(90) - math.atan2(RISE7, RUN7) * 0 + 0, math.radians(0), math.radians(90)))
    o = bpy.data.objects['smear']; o.rotation_euler = (math.radians(90), math.atan2(H7 / 2, LF7), math.radians(90))
    wall_decal('handprint', sm, (.5, YS + .06, -H7 / 2 + 1.25), (.5, .12, 1), (math.radians(90), 0, 0))
    import math as _m
    E = (_m.radians(90), 0, _m.radians(-90)); Wr = (_m.radians(90), 0, _m.radians(90))
    wall_decal('flyer_missing', _tex('fly_missing.png', make_flyer('missing')), (XW - .004, .9, 1.45), (.34, .44, 1), E)
    wall_decal('flyer_meeting', _tex('fly_meeting.png', make_flyer('meeting')), (XW - .004, .35, -H7 + 1.5), (.32, .41, 1), (E[0], .06, E[2]))
    wall_decal('flyer_laundry', _tex('fly_laundry.png', make_flyer('laundry')), (XW - .004, .55, -2 * H7 + 1.4), (.32, .41, 1), (E[0], -.05, E[2]))
    wall_decal('tag_run', _tex('tag_run.png', make_tag('RUN', (96, 10, 8), 3)), (-XW + .004, -LF7 - .45, -H7 / 2 + 1.5), (1.4, .52, 1), Wr)
    wall_decal('tag_11', _tex('tag_dont.png', make_tag("DON'T", (20, 20, 22), 8)), (XW - .004, -LF7 - .9, -H7 - H7 / 2 + 1.6), (1.2, .45, 1), E)
    wall_decal('claws', _tex('claw.png', make_claw), (-XW + .004, -LF7 + .5, -H7 - H7 / 2 - .2), (.9, .5, 1), (Wr[0], .5, Wr[2]))
    for k_, z_ in enumerate((0., -H7, -2 * H7)):                      # fire hose cabinet on each landing, west wall
        cab = bx('hosecab', (-XW + .09, 1.15, z_ + 1.1), (.18, .5, .7), K.metal('HoseRed', '#7a1410', .45), ink=.003)
        bx('hoseglass', (-XW + .185, 1.15, z_ + 1.12), (.01, .4, .56), m_glass_rain() if k_ else K.metal('HoseGlass', '#1a1c1e', .1))
        L.setmat(L.tube('hose', [V((-XW + .14, 1.15 + .12 * _m.cos(a_), z_ + 1.1 + .2 * _m.sin(a_))) for a_ in np.linspace(0, 6.28, 13)], .03, col, sides=8), K.metal('HoseCanvas', '#b9a77a', .8))
    paper_m, *_ = _bsdf('Paper'); paper_m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*K.C('#bdb7a6'), 1)
    for k_ in range(0):                                    # scattered papers on the 11 landing
        r_ = random.Random(k_); L.setmat(L.box('paper', (r_.uniform(-1.1, 1.1), r_.uniform(.15, 1.3), -H7 + .004), (.21, .29, .002), col, rot=(0, 0, r_.uniform(0, 3))), paper_m)
    # the Crawler: comes UP flight B from the 10th floor on all fours, head first, into the lamp
    zm2 = -H7 - H7 / 2
    slope = math.atan2(H7 / 2, LF7)
    cr = K.char('crawler', V((FLB, -1.0, -2 * H7)), 0., scale=1.1, col=col)
    rig = K.char_rig(cr); A.crawl(rig, cr, 1, nf, speed=0.)
    for f in range(1, nf + 1):
        u = min(1., max(0, f - 240) / 72.); y = .4 - 1.0 * u ** .9          # y along flight B, climbing toward -y
        zf = zm2 - (min(y, 0.) + LF7) / LF7 * H7 / 2
        cr.location = V((FLB + .05 * math.sin(f * .4), y, zf + .05)); cr.rotation_euler = (-slope, 0, 0)
        cr.keyframe_insert('location', frame=f); cr.keyframe_insert('rotation_euler', frame=f)
    c = camera(21); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    tl = phone_light(c, 28); tl.spot_size = math.radians(72); tl.spot_blend = .5
    # footfalls: vestibule -> turn -> flight A (PH) -> mid1 -> flight B -> 11 landing -> flight A -> mid2 (reveal)
    feet = [(1, (-.35, .35, 0)), (30, (-.4, .55, 0)), (40, (-.2, .8, 0)), (50, (.2, .55, 0)), (60, (.6, .2, 0))]
    feet += flight_feet(FLA, 0., 0., -1, 68, 7)
    m1 = -LF7 - .7
    feet += [(140, (.45, m1, -H7 / 2)), (148, (0, m1 - .2, -H7 / 2)), (156, (-.55, m1 + .1, -H7 / 2))]
    feet += flight_feet(FLB, -LF7, -H7 / 2, 1, 162, 7, first=1)
    feet += [(234, (-.6, .45, -H7)), (242, (-.1, .75, -H7)), (250, (.5, .45, -H7))]
    feet += flight_feet(FLA, 0., -H7, -1, 256, 5)
    feet += [(306, (.3, m1, zm2)), (312, (.1, m1 + .25, zm2))]
    looks = [(1, (-.6, YN, 1.2)), (26, (-.4, YN + 1.0, -.6)),                # into the black shaft
             (44, (0, -1.0, -2.5)), (58, (0, -1.4, -7.5)),                  # look down the open well
             (70, (FLA, -2.2, -.9)), (126, (FLA, -LF7 - .6, -H7 / 2 + .9)),
             (138, (.2, YS, -H7 / 2 + 1.7)), (150, (-XW, -LF7 - .45, -H7 / 2 + 1.45)),   # the window glow, the handprint
             (162, (FLB, -1.0, -H7 / 2 - .3)), (214, (FLB, .4, -H7 + 1.0)),
             (226, (.55, YN, -H7 + .45)), (240, (.4, YN - .6, -H7 + .1)),   # 11C: the door, the body
             (252, (FLA, -1.4, -H7 - .2)), (282, (FLA + .5, -2.0, -H7 - .35)),   # the smear trail on the east wall
             (296, (0, -LF7 - .9, zm2 + .3)), (304, (FLB, -LF7 + .5, zm2 - .25)), (312, (FLB, -LF7 + .4, zm2 - .05))]  # whip onto the Crawler
    pov_stairs(c, feet, looks, 1, nf)
    kick(c, [303], 3.2)
    sc.view_settings.exposure = 0.
    return 1, nf

def cut441():   # v8 041: continues 040 from f313 (same take): leap over the Crawler, two more flights, camcorder glitch, LOBBY door (T13.3)   # v7 one-take POV: dead elevator -> look down the well -> three flights -> 11C body -> the Crawler on the wall
    nf = 444; K.sky(sc, moon=False, fog=.009)
    stairhall(5, labels=('PH', '11', '10', '9', 'L'))
    # horror dressing
    sm = _tex('smear.png', make_smear)
    wall_decal('smear', sm, (XW - .002, -LF7 * .45, -H7 - .55), (1.5, .34, 1), (math.radians(90) - math.atan2(RISE7, RUN7) * 0 + 0, math.radians(0), math.radians(90)))
    o = bpy.data.objects['smear']; o.rotation_euler = (math.radians(90), math.atan2(H7 / 2, LF7), math.radians(90))
    wall_decal('handprint', sm, (.5, YS + .06, -H7 / 2 + 1.25), (.5, .12, 1), (math.radians(90), 0, 0))
    import math as _m
    E = (_m.radians(90), 0, _m.radians(-90)); Wr = (_m.radians(90), 0, _m.radians(90))
    wall_decal('flyer_missing', _tex('fly_missing.png', make_flyer('missing')), (XW - .004, .9, 1.45), (.34, .44, 1), E)
    wall_decal('flyer_meeting', _tex('fly_meeting.png', make_flyer('meeting')), (XW - .004, .35, -H7 + 1.5), (.32, .41, 1), (E[0], .06, E[2]))
    wall_decal('flyer_laundry', _tex('fly_laundry.png', make_flyer('laundry')), (XW - .004, .55, -2 * H7 + 1.4), (.32, .41, 1), (E[0], -.05, E[2]))
    wall_decal('tag_run', _tex('tag_run.png', make_tag('RUN', (96, 10, 8), 3)), (-XW + .004, -LF7 - .45, -H7 / 2 + 1.5), (1.4, .52, 1), Wr)
    wall_decal('tag_11', _tex('tag_dont.png', make_tag("DON'T", (20, 20, 22), 8)), (XW - .004, -LF7 - .9, -H7 - H7 / 2 + 1.6), (1.2, .45, 1), E)
    wall_decal('claws', _tex('claw.png', make_claw), (-XW + .004, -LF7 + .5, -H7 - H7 / 2 - .2), (.9, .5, 1), (Wr[0], .5, Wr[2]))
    for k_, z_ in enumerate((0., -H7, -2 * H7)):                      # fire hose cabinet on each landing, west wall
        cab = bx('hosecab', (-XW + .09, 1.15, z_ + 1.1), (.18, .5, .7), K.metal('HoseRed', '#7a1410', .45), ink=.003)
        bx('hoseglass', (-XW + .185, 1.15, z_ + 1.12), (.01, .4, .56), m_glass_rain() if k_ else K.metal('HoseGlass', '#1a1c1e', .1))
        L.setmat(L.tube('hose', [V((-XW + .14, 1.15 + .12 * _m.cos(a_), z_ + 1.1 + .2 * _m.sin(a_))) for a_ in np.linspace(0, 6.28, 13)], .03, col, sides=8), K.metal('HoseCanvas', '#b9a77a', .8))
    paper_m, *_ = _bsdf('Paper'); paper_m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*K.C('#bdb7a6'), 1)
    for k_ in range(0):                                    # scattered papers on the 11 landing
        r_ = random.Random(k_); L.setmat(L.box('paper', (r_.uniform(-1.1, 1.1), r_.uniform(.15, 1.3), -H7 + .004), (.21, .29, .002), col, rot=(0, 0, r_.uniform(0, 3))), paper_m)
    # the Crawler: comes UP flight B from the 10th floor on all fours, head first, into the lamp
    zm2 = -H7 - H7 / 2
    slope = math.atan2(H7 / 2, LF7)
    cr = K.char('crawler', V((FLB, -1.0, -2 * H7)), 0., scale=1.1, col=col)
    rig = K.char_rig(cr); A.crawl(rig, cr, 1, nf, speed=0.)
    for f in range(1, nf + 1):
        u = min(1., max(0, f - 240) / 72.); y = .4 - 1.0 * u ** .9          # y along flight B, climbing toward -y
        zf = zm2 - (min(y, 0.) + LF7) / LF7 * H7 / 2
        cr.location = V((FLB + .05 * math.sin(f * .4), y, zf + .05)); cr.rotation_euler = (-slope, 0, 0)
        cr.keyframe_insert('location', frame=f); cr.keyframe_insert('rotation_euler', frame=f)
    c = camera(21); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    tl = phone_light(c, 28); tl.spot_size = math.radians(72); tl.spot_blend = .5
    # footfalls: vestibule -> turn -> flight A (PH) -> mid1 -> flight B -> 11 landing -> flight A -> mid2 (reveal)
    feet = [(1, (-.35, .35, 0)), (30, (-.4, .55, 0)), (40, (-.2, .8, 0)), (50, (.2, .55, 0)), (60, (.6, .2, 0))]
    feet += flight_feet(FLA, 0., 0., -1, 68, 7)
    m1 = -LF7 - .7
    feet += [(140, (.45, m1, -H7 / 2)), (148, (0, m1 - .2, -H7 / 2)), (156, (-.55, m1 + .1, -H7 / 2))]
    feet += flight_feet(FLB, -LF7, -H7 / 2, 1, 162, 7, first=1)
    feet += [(234, (-.6, .45, -H7)), (242, (-.1, .75, -H7)), (250, (.5, .45, -H7))]
    feet += flight_feet(FLA, 0., -H7, -1, 256, 5)
    feet += [(306, (.3, m1, zm2)), (312, (.1, m1 + .25, zm2))]
    looks = [(1, (-.6, YN, 1.2)), (26, (-.4, YN + 1.0, -.6)),                # into the black shaft
             (44, (0, -1.0, -2.5)), (58, (0, -1.4, -7.5)),                  # look down the open well
             (70, (FLA, -2.2, -.9)), (126, (FLA, -LF7 - .6, -H7 / 2 + .9)),
             (138, (.2, YS, -H7 / 2 + 1.7)), (150, (-XW, -LF7 - .45, -H7 / 2 + 1.45)),   # the window glow, the handprint
             (162, (FLB, -1.0, -H7 / 2 - .3)), (214, (FLB, .4, -H7 + 1.0)),
             (226, (.55, YN, -H7 + .45)), (240, (.4, YN - .6, -H7 + .1)),   # 11C: the door, the body
             (252, (FLA, -1.4, -H7 - .2)), (282, (FLA + .5, -2.0, -H7 - .35)),   # the smear trail on the east wall
             (296, (0, -LF7 - .9, zm2 + .3)), (304, (FLB, -LF7 + .5, zm2 - .25)), (312, (FLB, -LF7 + .4, zm2 - .05))]  # whip onto the Crawler
    z10, zm3, z9, zl = -2 * H7, -2 * H7 - H7 / 2, -3 * H7, -4 * H7
    wall_decal('lobbysign', _tex('lobby.png', make_label('LOBBY', (240, 228, 200), (24, 20, 16))), (.55, YN - .17, zl + 1.55), (-.6, .2, 1), (math.radians(90), 0, math.radians(180)), alpha=False)
    feet += [(318, (.0, m1 + .2, zm2)), (322, (FLB + .1, -LF7 + .1, zm2 - .05))]
    feet += [(326, (FLB + .12, -2.2, zm2 - .3)), (330, (FLB - .08, -1.75, zm2 - .6))]          # down flight B toward it
    feet += [(334, (FLB + .2, -1.3, zm2 - .5)), (344, (.35, .55, z10))]                       # the leap over its back onto the 10 landing
    feet += [(350, (.6, .3, z10)), (354, (.75, .05, z10))]
    feet += flight_feet(FLA, 0., z10, -1, 357, 3)                                             # 10 -> mid3, running
    feet += [(387, (.45, m1, zm3)), (391, (-.1, m1 - .2, zm3)), (395, (-.55, m1 + .1, zm3))]
    feet += flight_feet(FLB, -LF7, zm3, 1, 398, 2, first=1)                                  # mid3 -> 9
    feet += [(418, (-.2, .4, z9)), (419, (.2, -.2, zl)), (430, (.5, .3, zl)), (444, (.55, .95, zl))]   # glitch, then the LOBBY door
    looks += [(320, (FLB, -1.2, zm2 - 1.0)), (332, (FLB, -.6, z10 + .2)), (340, (.2, .8, z10 + .3)),
              (350, (FLA, -.6, z10 - .2)), (360, (FLA, -2.2, zm3 + .6)), (386, (-.2, m1 - .4, zm3 + 1.2)),
              (396, (FLB, -1.0, zm3 - .4)), (414, (.55, YN, z9 + 1.8)), (418, (.55, YN, z9 + 1.7)),
              (419, (.55, YN, zl + 1.7)), (432, (.55, YN, zl + 1.6)), (444, (.6, YN, zl + 1.4))]
    pov_stairs(c, feet, looks, 1, nf)
    kick(c, [303], 3.2); kick(c, [344], 3.0); kick(c, [419], 1.8)
    for f_, e_ in ((1, 28), (411, 28), (412, 0), (414, 14), (415, 0), (418, 0), (419, 28)):      # camcorder lamp dies, sputters, back on (glitch hides 9 -> L)
        tl.energy = e_; tl.keyframe_insert('energy', frame=f_)
    for fc in _fcurves(tl.id_data.animation_data.action if tl.id_data.animation_data else None) if False else []: pass
    lob = light('AREA', (.55, YN + 1.6, zl + 1.6), 400, '#ffb070', 1.0, rot=(math.radians(90), 0, 0), name='lobbyglow')[0]
    sc.view_settings.exposure = 0.
    return 1, nf

def relight_roof(nf, hits, fire_e=2600, src=(4, -12, 18), tgt=(10.2, -20, 31.5)):
    """v7 look on the old v5 roof: kill the flat blue moon wash, light her from the burning street below (slow breathing fire)."""
    for l in bpy.data.lights:
        if l.type == 'AREA' and l.color[2] > l.color[0]: l.energy *= .12
    lightning(moon_obj(), list(hits), base=.05, peak=5.0)
    fire = area(src, tgt, fire_e, 6, '#ff5a1c'); rr = random.Random(41)
    for f in range(0, nf + 7, 6):
        fire.energy = fire_e * rr.uniform(.7, 1.1); fire.keyframe_insert('energy', frame=f)
    me = V(tgt)
    key = area(me + V((-2.2, 2.6, -1.6)), me, fire_e * .12, 1.5, '#ff6a2a')     # fire bounce off the parapet onto her face/front
    rim = area(me + V((2.0, -2.6, .4)), me, fire_e * .14, 1.2, '#ff8a3a')       # a fire behind her: orange rim on hair + shoulders
    for f in range(0, nf + 7, 5):
        u = rr.uniform(.7, 1.1); key.energy = fire_e * .12 * u; key.keyframe_insert('energy', frame=f)
        rim.energy = fire_e * .14 * rr.uniform(.7, 1.1); rim.keyframe_insert('energy', frame=f)
    m = bpy.data.materials.get('Rain')                                          # rain reads by the light it catches, not by glowing
    if m:
        bs = m.node_tree.nodes.get('Principled BSDF')
        if bs: bs.inputs['Emission Strength'].default_value = .02; bs.inputs['Alpha'].default_value = .22
    return fire

def cut6():   # v7 006b CU: head snaps back, the scream; same practical-fire look as 006a
    nf = 36; s = roof_set(nf, (10, 26)); A.scream(K.char_rig(s), 1, nf, f_scream=8, amp=.25)
    relight_roof(nf, (10, 26), fire_e=900)
    h = bone_w(s, 'head', 1)
    c = camera(45)
    shot_cam(c, [(1, h + V((-.95, .75, .6)), h + V((0, 0, .02)), 45, 1.35), (nf, h + V((-.75, .6, .5)), h + V((0, 0, .02)), 52, 1.1)], 1, nf, shake=.01, rshake=.4, seed=6)
    kick(c, [8, 9, 11], 2.2)
    sc.view_settings.exposure = -.2
    c.data.dof.aperture_fstop = 2.0; return 1, nf

def cut41():   # v7 006a: from his window across the street, long lens: the Screamer on the roof slowly turns her head to us
    nf = 60; s = roof_set(nf, (44,)); A.idle(K.char_rig(s), 1, nf, amp=.4)
    for f, yaw in ((1, -40.), (14, -40.), (50, -134.), (nf, -136.)):
        s.rotation_euler = (0, 0, math.radians(yaw)); s.keyframe_insert('rotation_euler', frame=f)
    for fc in _fcurves(s.animation_data.action):
        for k in fc.keyframe_points: k.interpolation = 'BEZIER'
    relight_roof(nf, [44], fire_e=1800)
    c = camera(135)
    shot_cam(c, [(1, (-5.5, -5.0, 33.6), (10.2, -20.0, 31.5), 135, 21.5), (nf, (-5.5, -5.0, 33.5), (10.2, -20.0, 31.6), 150, 21.5)], 1, nf, shake=.012, rshake=.08, seed=41)
    sc.view_settings.exposure = -.2
    c.data.dof.aperture_fstop = 4; return 1, nf

# ------------------------------------------------------------------ 030 corridor
def side_door(y, side, label, wood, brass, ajar=0.):
    """apartment door on a side wall of the corridor (side=+1 east wall, -1 west wall), hinge on its north edge"""
    CW = .95; x = side * (CW - .03)
    fr = [bx('frame', (x, y - .5, 1.08), (.1, .08, 2.16), wood), bx('frame', (x, y + .5, 1.08), (.1, .08, 2.16), wood), bx('frame', (x, y, 2.2), (.1, 1.08, .1), wood)]
    join_ink(fr, 'doorframe', .003)
    piv = bpy.data.objects.new('door pivot', None); col.objects.link(piv); piv.location = (x, y + .45, 0); bpy.context.view_layer.update()
    parts = [bx('door', (x, y, 1.05), (.05, .9, 2.1), wood)]
    for dz in (.55, 1.5): parts.append(bx('panel', (x - side * .03, y, dz), (.02, .62, .7), wood))
    parts.append(bx('knob', (x - side * .05, y - .35, 1.0), (.05, .05, .05), brass))
    parts.append(bx('peep', (x - side * .03, y, 1.55), (.03, .03, .03), brass))
    parts.append(bx('number', (x - side * .03, y, 1.82), (.01, .22, .1), m_img(f'Num{label}', _tex(f'num_{label}.png', make_label(label, (40, 30, 10), (178, 140, 66), (440, 200), 110)), rough=.3)[0]))
    d_ = L.join(parts, 'door ' + label); L.hull(d_, col, .0025)
    for o_ in (d_, bpy.data.objects.get(d_.name + ' hull')):
        if o_: o_.parent = piv; o_.matrix_parent_inverse = piv.matrix_world.inverted()
    piv.rotation_euler.z = math.radians(side * ajar)
    return piv

def cut30():   # v7 030: out of the apartment, down the PH corridor in emergency light, a door ajar with someone sobbing, shoulder the EXIT door
    nf = 72; K.sky(sc, moon=False, fog=.012); CW, LEN, HT = .95, 9.0, 2.8
    paint = m_paint('WallPaint', '#8a8468', peel=.68); lowpaint = m_paint('WainscotPaint', '#3b4a3a', '#2a2219', .6)
    soffit = m_paint('SoffitPaint', '#8c8771', '#4a4034', .66, stain=True)
    oak = m_wood('Oak'); brass = m_brass(); door_w = m_wood('DoorWood', '#2b170f', .45)
    tile = m_tile(_tex('hex.png', make_hex))
    runner, *_ = _bsdf('Runner'); rb = runner.node_tree.nodes['Principled BSDF']; rb.inputs['Base Color'].default_value = (*K.C('#3a1512'), 1); rb.inputs['Roughness'].default_value = .95
    y0, y1 = 1.0, -LEN
    bx('floor', (0, (y0 + y1) / 2, -.05), (2 * CW, y0 - y1, .1), tile)
    bx('runner', (0, (y0 + y1) / 2 + .3, .004), (.9, y0 - y1 - 1.2, .008), runner)
    bx('ceiling', (0, (y0 + y1) / 2, HT + .05), (2 * CW + .2, y0 - y1, .1), soffit)
    def wall_with_holes(name, s, holes):            # side wall in segments, with door openings (y centre, width) and lintels above
        edges = sorted(holes, key=lambda h: -h[0]); ya = y0
        for (yc, w) in edges:
            yb = yc + w / 2
            if ya - yb > .01: bx(name, (s * (CW + .05), (ya + yb) / 2, HT / 2), (.1, ya - yb, HT), paint)
            bx(name + ' lintel', (s * (CW + .05), yc, (2.15 + HT) / 2), (.1, w, HT - 2.15), paint); ya = yc - w / 2
        bx(name, (s * (CW + .05), (ya + y1) / 2, HT / 2), (.1, ya - y1, HT), paint)
    wall_with_holes('wallE', 1, [(.0, .92)]); wall_with_holes('wallW', -1, [(-2.6, .92)])
    for s in (1, -1):
        bx('wainscot', (s * (CW - .01), (y0 + y1) / 2, .5), (.02, y0 - y1, 1.0), lowpaint)
        rail_run([(s * (CW - .03), y0, 1.0), (s * (CW - .03), y1, 1.0)], .02, oak)
        bx('base', (s * (CW - .015), (y0 + y1) / 2, .08), (.03, y0 - y1, .16), door_w)
        bx('crown', (s * (CW - .03), (y0 + y1) / 2, HT - .05), (.06, y0 - y1, .1), soffit)
    bx('wallN', (0, y0 + .05, HT / 2), (2 * CW + .2, .1, HT), paint)
    # doors: his own PH-B behind the camera (open), PH-C ajar on the west wall, PH-D and PH-E shut, the EXIT door at the end
    side_door(.0, 1, 'PH-B', door_w, brass, ajar=80)
    side_door(-2.6, -1, 'PH-C', door_w, brass, ajar=62)
    side_door(-4.8, 1, 'PH-D', door_w, brass); side_door(-6.4, -1, 'PH-E', door_w, brass)
    # PH-C beyond the gap: dark room, a TV hissing static, its flicker spilling into the corridor
    bx('aptfloor', (-CW - 1.6, -2.6, -.05), (3.2, 2.6, .1), m_wood('AptFloor', '#2a1a10', .5))
    bx('aptback', (-CW - 3.2, -2.6, 1.4), (.1, 2.6, 2.8), m_paint('AptWall', '#565b52'))
    bx('tv', (-CW - 3.1, -2.9, .9), (.06, .9, .55), m_static())
    tl, _ = light('AREA', (-CW - 2.95, -2.9, .9), 22, '#cfdcff', .9, rot=(0, math.radians(-90), 0), name='tvlight')
    rng = random.Random(30)
    for f in range(1, nf + 1): tl.energy = rng.uniform(10, 30); tl.keyframe_insert('energy', frame=f)
    # the EXIT door at the far end (steel, push bar, wired glass), red EXIT sign above
    ex_w = K.metal('ExitSteel', '#4a2e26', .5)
    ex_piv = bpy.data.objects.new('exit pivot', None); col.objects.link(ex_piv); ex_piv.location = (-.45, y1 + .06, 0); bpy.context.view_layer.update()
    ex = [bx('exit door', (0, y1 + .06, 1.05), (.92, .05, 2.1), ex_w), bx('pushbar', (0, y1 + .11, 1.0), (.75, .05, .06), K.metal('Bar', '#8a8a86', .3)),
          bx('wired glass', (0, y1 + .09, 1.6), (.3, .01, .4), m_glass_rain())]
    exo = L.join(ex, 'EXIT door'); L.hull(exo, col, .003)
    for o_ in (exo, bpy.data.objects.get(exo.name + ' hull')):
        if o_: o_.parent = ex_piv; o_.matrix_parent_inverse = ex_piv.matrix_world.inverted()
    for f, a_ in ((1, 0), (58, 0), (64, -55), (nf, -70)):                  # he shoulders it open
        ex_piv.rotation_euler.z = math.radians(a_); ex_piv.keyframe_insert('rotation_euler', frame=f)
    for xs, w in ((-(CW + .46) / 2 - .01, CW - .46 + .1), ((CW + .46) / 2 + .01, CW - .46 + .1)):
        bx('wallS', (xs, y1 - .05, HT / 2), (w, .1, HT), paint)
    bx('wallS lintel', (0, y1 - .05, (2.15 + HT) / 2), (.94, .1, HT - 2.15), paint)
    exit_img = _tex('exit.png', make_label('EXIT', (255, 40, 30), (20, 6, 6), (440, 160), 120))
    bx('exit sign', (0, y1 + .12, 2.42), (.42, .04, .16), m_img('ExitSign', exit_img, rough=.4, emit=1.5)[0])
    light('POINT', (0, y1 + .3, 2.3), 2.5, '#ff2a1e', .05, name='exitglow')
    sdark = K.concrete('StairDark', '#1a1918')                                  # beyond the door: the dark stair hall
    bx('stairfloor', (0, y1 - 1.6, -.05), (2.4, 3.0, .1), tile); bx('stairback', (0, y1 - 3.1, 1.4), (2.6, .1, 3.0), sdark)
    for s_ in (1, -1): bx('stairside', (s_ * 1.25, y1 - 1.6, 1.4), (.1, 3.0, 3.0), sdark)
    iron_ = m_iron(); bals_ = [baluster(-.7 + .18 * i, y1 - 1.5, -.05 - .06 * i, .9, iron_) for i in range(9)]
    join_ink(bals_, 'stair balusters', .0025); [L.setmat(o_, iron_) for o_ in bpy.data.objects if o_.name.startswith('stair balusters') and 'hull' not in o_.name]
    rail_run([(-.75, y1 - 1.5, .87), (.85, y1 - 1.5, .38)], .03, oak, ink=.0025)
    ld_, _ = light('POINT', (.6, y1 - 1.9, 2.0), 5, '#ffb070', .1, name='stairglow'); fire_flicker(ld_, 1, nf, 5, seed=31)
    # emergency lights: twin-head battery packs, one dying (strobe), one steady and weak
    for k_, (ey, side, base, dying) in enumerate(((-1.6, 1, 45, False), (-5.6, -1, 60, True))):
        bx('emerg box', (side * (CW - .06), ey, 2.35), (.1, .32, .14), K.metal('EmergBox', '#c9c3b5', .5), ink=.002)
        ld, lo = light('SPOT', (side * (CW - .15), ey, 2.3), base, '#fff1d6', .03, rot=(math.radians(35), side * math.radians(-30), 0), name='emerg')
        ld.spot_size = math.radians(95); ld.spot_blend = .6
        if dying: strobe(ld, 1, nf, base, seed=30 + k_, on=4, off=(2, 7))
    # wall dressing: the tenants' notice, a missing flyer, a bloody hand drag on the east wall near PH-D
    E = (math.radians(90), 0, math.radians(-90)); Wr = (math.radians(90), 0, math.radians(90))
    wall_decal('notice', _tex('notice.png', make_notice), (CW - .004, -7.6, 1.5), (.34, .44, 1), E)
    wall_decal('flyer_missing', _tex('fly_missing.png', make_flyer('missing')), (-CW + .004, -4.0, 1.45), (.32, .41, 1), Wr)
    wall_decal('handprint', _tex('smear.png', make_smear), (CW - .004, -5.6, 1.15), (1.1, .3, 1), (math.radians(90), -.25, math.radians(-90)))
    # the camcorder POV: out of his door, glance into PH-C (sobbing), then hurry to the EXIT door and shoulder it
    c = camera(21); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    tl_ = phone_light(c, 26); tl_.spot_size = math.radians(70); tl_.spot_blend = .5; tl_.color = K.C('#ffe2b8')
    feet = [(1, (.2, .3, 0)), (9, (.05, -.35, 0)), (17, (-.1, -1.05, 0)), (25, (-.15, -1.75, 0)), (34, (-.2, -2.4, 0)),   # slows at the gap
            (42, (-.1, -3.2, 0)), (49, (0, -4.3, 0)), (55, (.05, -5.5, 0)), (61, (0, -6.9, 0)), (nf, (-.05, -7.7, 0))]
    looks = [(1, (.2, -4, 1.3)), (18, (-.6, -3.4, 1.2)), (30, (-2.4, -2.9, .9)),   # drawn to the TV glow in PH-C
             (36, (-2.2, -3.4, 1.0)), (48, (-.6, -5.6, 1.3)), (56, (0, y1, 1.4)), (62, (0, y1, 1.2)), (nf, (-.4, y1 - 2, 1.2))]
    pov_stairs(c, feet, looks, 1, nf)
    kick(c, [59], 2.4)
    sc.view_settings.exposure = .35
    return 1, nf

# ------------------------------------------------------------------ 050 lobby
def cut50():   # v7 050: down into the lobby, the doorman's desk abandoned, the horde floods the avenue outside the glass, a hand slaps it, he backs off to B1 PARKING
    nf = 96; GY = -6.0                                   # the glass storefront line; the avenue runs off toward -y beyond it
    hs = horde_set(nf, n=44, near=GY - 1.2, mode='shamble', face=180)
    rng = random.Random(50)
    for i, d in enumerate(hs[:22]):                      # the far crowd: more of them, packed down the avenue into the fog
        e = dup(d, V((rng.uniform(-6, 6), GY - 36 - rng.uniform(0, 14), 0)), math.radians(180 + rng.uniform(-30, 30)), rng.uniform(.95, 1.05))
        A.shamble(K.char_rig(e), e, 1, nf, speed=rng.uniform(.5, .9), period=rng.uniform(1.1, 1.6), phase=rng.uniform(0, 6.3), limp=.3, seed=100 + i, arms='dangle')
    crowd_m = K.metal('CrowdDark', '#140f0d', .9); fig = []
    for i in range(260):                                 # beyond 50 m: hundreds of swaying silhouettes in the fire haze
        x_, y_ = rng.uniform(-9, 9), GY - 50 - rng.uniform(0, 60); h_ = rng.uniform(1.55, 1.85); lean = rng.uniform(-.25, .25)
        fig.append(L.blob('crowd', (x_, y_, h_ * .55), (.2, .14, h_ * .3), col)); fig.append(L.blob('crowd', (x_ + lean * .3, y_, h_ * .93), (.1, .1, .12), col))
        fig.append(L.blob('crowd', (x_, y_, h_ * .22), (.14, .1, h_ * .24), col))
    cr_ = L.join(fig, 'far crowd'); L.setmat(cr_, crowd_m)
    for f in range(1, nf + 1, 6):
        cr_.location = V((math.sin(f * .3) * .04, 0, 0)); cr_.keyframe_insert('location', frame=f)
    for o_ in [o_ for o_ in bpy.data.objects if o_.name.startswith('rain')]: bpy.data.objects.remove(o_, do_unlink=True)
    rain_here((0, GY - 14, 0), (18, 25, 16), 4000, 1, nf)       # rain only OUTSIDE the glass
    for o_ in bpy.data.objects:                                 # nothing of the street may poke through the lobby
        if o_.type == 'MESH' and o_.name not in ('far crowd',) and not o_.name.startswith(('rain',)):
            bb = [o_.matrix_world @ V(cn) for cn in o_.bound_box]
            if min(v.y for v in bb) > GY + .2 and max(v.z for v in bb) < .3: o_.hide_render = True
    for l in bpy.data.lights:                            # the avenue: a few working street lamps and fire glow, no blue fill
        if l.type == 'AREA' and l.color[2] > l.color[0]: l.energy *= .25
    fire = area((6, GY - 30, 6), (0, GY - 10, 1), 3000, 12, '#ff5a1c'); fire_flicker(fire, 1, nf, 3000, seed=50)
    # the lobby interior
    LW, LD, LH = 4.2, 9.0, 3.6
    marble = m_marble(); paint = m_paint('LobbyPaint', '#7d7462', peel=.7); brass = m_brass(); oak = m_wood('Oak')
    wain = m_wood('LobbyWainscot', '#2a170e', .4)
    for m_ in (marble, paint, wain):                    # Sam 2026-11-23: no speckle/dots. Enlarge every texture pattern 4x so surfaces read smooth
        for nd in m_.node_tree.nodes:
            if nd.type == 'MAPPING': nd.inputs['Scale'].default_value = tuple(v * .25 for v in nd.inputs['Scale'].default_value)
            elif nd.type in ('TEX_NOISE', 'TEX_VORONOI', 'TEX_MUSGRAVE') and nd.inputs.get('Scale'): nd.inputs['Scale'].default_value *= .25
    bx('lobbyfloor', (0, GY + LD / 2 + .06, .03), (2 * LW, LD - .1, .1), marble)
    bx('lobbyceil', (0, GY + LD / 2, LH + .05), (2 * LW, LD, .1), m_paint('LobbyCeil', '#8c8771', '#4a4034', .66))
    for s in (1, -1):
        bx('lobbywall', (s * (LW + .05), GY + LD / 2, LH / 2), (.1, LD, LH), paint)
        bx('lobbywain', (s * (LW - .01), GY + LD / 2, .6), (.02, LD, 1.2), wain)
    bx('lobbyback', (0, GY + LD + .05, LH / 2), (2 * LW, .1, LH), paint)
    gl = m_glass_rain(); fr_ = []
    for x_ in np.linspace(-LW, LW, 7): fr_.append(bx('mullion', (x_, GY, LH / 2), (.07, .1, LH), brass))
    fr_ += [bx('transom', (0, GY, 2.6), (2 * LW, .1, .07), brass), bx('sill', (0, GY, .05), (2 * LW, .12, .1), brass)]
    join_ink(fr_, 'storefront', .003)
    bx('storeglass', (0, GY, LH / 2), (2 * LW, .012, LH), gl)
    bx('door push L', (-.35, GY + .08, 1.05), (.04, .04, .5), brass); bx('door push R', (.35, GY + .08, 1.05), (.04, .04, .5), brass)
    # the doorman's desk: lamp still on, logbook open, the phone off the hook, his chair knocked over
    dk = [bx('desk', (-2.2, GY + 3.2, .55), (2.0, .7, 1.1), oak), bx('desktop', (-2.2, GY + 3.2, 1.12), (2.15, .8, .05), marble)]
    join_ink(dk, 'doorman desk', .003)
    bx('logbook', (-2.5, GY + 3.25, 1.155), (.4, .3, .02), m_wood('Paper2', '#cdc5b0', .9), rot=(0, 0, .2))
    bx('desk phone', (-1.75, GY + 3.3, 1.18), (.22, .18, .08), K.metal('PhoneBlack', '#111111', .4))
    bx('handset', (-1.6, GY + 2.75, .03), (.22, .06, .05), K.metal('PhoneBlack', '#111111', .4), rot=(0, 0, .7))
    L.setmat(L.tube('phone cord', [V((-1.75, GY + 3.3, 1.15)), V((-1.7, GY + 2.88, .9)), V((-1.62, GY + 2.78, .06))], .006, col, sides=5), K.metal('Cord', '#111111', .6))
    bx('chair', (-2.4, GY + 4.0, .25), (.5, .5, .5), oak, rot=(math.radians(84), 0, .4))
    ld_, _ = light('POINT', (-2.7, GY + 3.2, 1.45), 40, '#ffb46a', .05, name='desklamp')
    sh_ = bx('lampshade', (-2.7, GY + 3.2, 1.45), (.22, .22, .16), m_paint('Shade', '#b0884e', '#6a4a22', .7)); sh_.visible_shadow = False
    bx('pool', (-1.0, GY + 2.2, .003), (.8, .9, .002), m_img('Pool', _tex('pool.png', make_pool), alpha=True, rough=.08)[0])
    # B1 PARKING door on the east wall with its sign
    park = _tex('b1park.png', make_label('B1  PARKING  ↓', (230, 220, 200), (24, 28, 34), (640, 160), 92))
    bx('parkdoor', (LW - .03, GY + 6.6, 1.05), (.05, .95, 2.1), K.metal('ParkDoor', '#3a3e42', .5), ink=.003)
    bx('parksign', (LW - .05, GY + 6.6, 2.35), (.02, .8, .2), m_img('ParkSign', park, rough=.4, emit=1.2)[0])
    el, _ = light('SPOT', (LW - .2, GY + 7.6, 3.2), 40, '#fff1d6', .03, rot=(math.radians(30), math.radians(-25), 0), name='emerg'); el.spot_size = math.radians(90)
    strobe(el, 1, nf, 40, seed=51, on=5, off=(2, 6))
    # the one at the glass: lunges and slaps it at f58 (a smeared handprint appears)
    slap = hs[0]; slap.location = V((.5, GY - .55, 0)); slap.rotation_euler = (0, 0, math.radians(180))
    for f, y in ((1, GY - 1.6), (50, GY - .9), (57, GY - .45), (59, GY - .42), (nf, GY - .5)):
        slap.location.y = y; slap.keyframe_insert('location', frame=f)
    hp = wall_decal('handprint', _tex('smear.png', make_smear), (.55, GY - .012, 1.55), (.35, .25, 1), (math.radians(90), 0, 0))
    hp.hide_render = True; hp.keyframe_insert('hide_render', frame=57); hp.hide_render = False; hp.keyframe_insert('hide_render', frame=58)
    # camcorder POV: off the last stair, past the desk, to the glass, tilt up over the crowd, the slap, back off to B1
    c = camera(21); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    tl_ = phone_light(c, 30); tl_.spot_size = math.radians(70); tl_.spot_blend = .5; tl_.color = K.C('#ffe2b8')
    feet = [(1, (2.6, GY + 7.6, 0)), (10, (2.1, GY + 6.6, 0)), (19, (1.5, GY + 5.4, 0)), (28, (1.0, GY + 4.2, 0)), (38, (.6, GY + 3.0, 0)),
            (52, (.4, GY + 2.2, 0)), (60, (.45, GY + 2.15, 0)), (68, (.8, GY + 2.9, 0)), (77, (1.4, GY + 3.7, 0)), (86, (1.9, GY + 4.5, 0)), (nf, (2.1, GY + 4.9, 0))]
    looks = [(1, (0, GY, 1.4)), (16, (-2.2, GY + 3.2, 1.1)), (28, (-1.2, GY, 1.3)),          # the empty desk, then out through the glass
             (40, (0, GY - 12, 1.5)), (52, (0, GY - 30, 7.0)),                               # tilt up: the avenue full of them
             (57, (.5, GY, 1.5)), (64, (.55, GY, 1.5)),                                      # SLAP
             (78, (2.6, GY + 1.0, 1.6)), (nf, (LW, GY + 6.6, 1.5))]                          # backing off, swing onto B1 PARKING
    pov_stairs(c, feet, looks, 1, nf)
    kick(c, [58], 3.0)
    sc.view_settings.exposure = .3
    return 1, nf

# ------------------------------------------------------------------ 060 garage reveal (v5 c11 look Sam loved, headlights OFF per his v5 note)
def cut60():   # tube lights clunk on one by one down the row; the Night Terror appears dark, headlights off; slow push in
    nf = 96; car = garage_set(nf, ign=9999)
    for m_ in bpy.data.materials:                              # headlights stay OFF until the ignition shot
        if m_.name.startswith('HeadGlow') and m_.node_tree.animation_data: m_.node_tree.animation_data_clear()
    for l in bpy.data.lights:
        if l.animation_data and l.name != 'fluo': l.animation_data_clear()
        if l.type == 'SPOT': l.energy = 0
    g = bpy.data.materials.get('HeadGlow')
    if g: g.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0
    steam((2.5, -8), h=1.2, r=2.0, dens=.25, seed=5)
    fo = bpy.data.objects['fluo']; fo.data.animation_data_clear(); fo.data.energy = 0; fo.data.keyframe_insert('energy', frame=1)
    tubes = [(fo.data, 10)]
    for k, (y, f_on) in enumerate(((-8.5, 22), (4.0, 34), (-14.5, 46))):          # more tubes down the row
        K.box('tube', col, (.4, y, 5.85), (.12, 2.6, .06), K.emit(f'Fluo{k}', '#cfe8ff', 25))
        ld = bpy.data.lights.new(f'fluo{k}', 'AREA'); ld.shape = 'RECTANGLE'; ld.size = .2; ld.size_y = 2.6; ld.color = K.C('#cfe8ff')
        lo = bpy.data.objects.new(f'fluo{k}', ld); col.objects.link(lo); lo.location = (.4, y, 5.75); tubes.append((ld, f_on))
    for ld, f_on in tubes:                                     # clunk, two stutters, then it holds (a slow flicker afterwards)
        for f, v in ((1, 0), (f_on - 1, 0), (f_on, 160), (f_on + 1, 0), (f_on + 3, 120), (f_on + 4, 0), (f_on + 6, 160)):
            ld.energy = v; ld.keyframe_insert('energy', frame=f)
        rr = random.Random(f_on)
        for f in range(f_on + 9, nf + 1, 7): ld.energy = 160 * rr.uniform(.85, 1.0); ld.keyframe_insert('energy', frame=f)
        for fc in _fcurves(ld.animation_data.action):
            for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    for nm, f_on in (('Fluo', 10), ('Fluo0', 22), ('Fluo1', 34), ('Fluo2', 46)):   # tube emission follows: dark until its light clunks on
        m_ = bpy.data.materials.get(nm)
        if not m_: continue
        for nd in m_.node_tree.nodes:
            sk = nd.inputs.get('Strength') if nd.type == 'EMISSION' else nd.inputs.get('Emission Strength') if nd.type == 'BSDF_PRINCIPLED' else None
            if sk is None: continue
            for f, v in ((1, 0), (f_on - 1, 0), (f_on, 25), (f_on + 1, 0), (f_on + 3, 18), (f_on + 4, 0), (f_on + 6, 25)):
                sk.default_value = v; sk.keyframe_insert('default_value', frame=f)
            for fc in _fcurves(m_.node_tree.animation_data.action):
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    c = camera(24)
    shot_cam(c, [(1, (3.6, -10.8, 1.1), (.4, -2, .9), 24, 7.5), (nf, (2.6, -8.6, 1.0), (.4, -2, .9), 26, 5.8)], 1, nf, shake=.012, rshake=.3, seed=60)
    sc.view_settings.exposure = .6
    c.data.dof.aperture_fstop = 2.8; return 1, nf

def cut80():   # v7 080 ignition (v5 c10 framing): headlights come on ONCE and stay on (Sam's v5 note: no on/off flicker)
    f0, f1 = cut10(); ign = 11
    g = bpy.data.materials.get('HeadGlow')
    if g:
        g.node_tree.animation_data_clear(); em = g.node_tree.nodes['Principled BSDF'].inputs['Emission Strength']
        for f, v in ((1, 0), (ign - 1, 0), (ign, 30), (f1, 28)): em.default_value = v; em.keyframe_insert('default_value', frame=f)
    for l in bpy.data.lights:
        if l.type == 'SPOT' and l.animation_data and l.name != 'fluo':
            l.animation_data_clear()
            for f, v in ((1, 0), (ign - 1, 0), (ign, 1200), (f1, 1120)): l.energy = v; l.keyframe_insert('energy', frame=f)
            for fc in _fcurves(l.animation_data.action):
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    return f0, f1

# ------------------------------------------------------------------ 070 in the car (camcorder propped on the dash = the dashcam for the rest of the episode)
def cut70():   # the camcorder settles on the dash looking back at the passenger seat; his phone is tossed onto it; engine cranks at the end
    nf = 84; car = garage_set(nf, ign=9999)
    for m_ in bpy.data.materials:
        if m_.name.startswith('HeadGlow') and m_.node_tree.animation_data: m_.node_tree.animation_data_clear()
    g = bpy.data.materials.get('HeadGlow')
    if g: g.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0
    for l in bpy.data.lights:
        if l.animation_data: l.animation_data_clear()
        if l.type == 'SPOT': l.energy = 0
    bpy.data.lights['fluo'].energy = 160
    for k, y in enumerate((-8.5, 4.0, -14.5)):
        K.box('tube', col, (.4, y, 5.85), (.12, 2.6, .06), K.emit(f'Fluo{k}', '#cfe8ff', 25))
        ld = bpy.data.lights.new(f'fluo{k}', 'AREA'); ld.shape = 'RECTANGLE'; ld.size = .2; ld.size_y = 2.6; ld.energy = 160; ld.color = K.C('#cfe8ff')
        lo = bpy.data.objects.new(f'fluo{k}', ld); col.objects.link(lo); lo.location = (.4, y, 5.75)
    O = V((.4, -2, 0))                                                     # car root offset (garage_set puts it here, unrotated)
    dash, _ = light('AREA', O + V((0, -.62, 1.2)), 2.5, '#ff4a3a', .4, rot=(math.radians(-70), 0, 0), name='dashglow')   # red dash instrument spill
    # the phone: tossed in from the driver's side, lands on the passenger cushion, bounces, settles face up
    ph = bx('his phone', (0, 0, 0), (.075, .155, .009), K.metal('PhoneBody', '#0d0d0f', .25), bevel=.003)   # built at the origin so location keys place it
    scr_m, *_ = _bsdf('PhoneScreen70'); sb_ = scr_m.node_tree.nodes['Principled BSDF']
    sb_.inputs['Base Color'].default_value = (.01, .01, .012, 1); sb_.inputs['Roughness'].default_value = .08
    sb_.inputs['Emission Color'].default_value = (.75, .85, 1, 1); sb_.inputs['Emission Strength'].default_value = 0
    scr = bx('his phone screen', (0, 0, .0055), (.068, .145, .003), scr_m)
    scr.parent = ph
    keys_ = [(1, (.45, -.05, 1.9), (0, 0, 0)), (27, (.45, -.05, 1.9), (0, 0, 0)), (31, (.15, .1, 1.35), (1.2, .4, .9)), (36, (-.38, .1, .96), (.25, .2, 1.6)),
             (39, (-.42, .14, 1.02), (-.3, .4, 1.9)), (42, (-.42, .12, .95), (-.15, 0, 2.1)), (nf, (-.42, .12, .95), (-.15, 0, 2.1))]
    for f, p, r in keys_:
        ph.location = O + V(p); ph.rotation_euler = r; ph.keyframe_insert('location', frame=f); ph.keyframe_insert('rotation_euler', frame=f)
    # camcorder on the dash: set down (drop + wobble), then still, engine shudder from the crank at f70
    c = camera(18); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    base = O + V((.06, -.64, 1.31)); tgt = O + V((-.45, .32, .95)); nz = [A.Noise(70 + i) for i in range(4)]
    for f in range(1, nf + 1):
        settle = math.exp(-max(0, f - 1) / 5.) if f < 20 else 0.
        crank = (.0025 if 70 <= f < 76 else .0012 if f >= 76 else 0.)
        c.location = base + V((nz[0](f * .9) * .01 * settle, 0, .03 * settle + nz[1](f * 3.1) * crank))
        aim(c, tgt + V((nz[2](f * .7) * .06 * settle, 0, nz[3](f * .8) * .05 * settle)))
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 1.2; c.data.dof.aperture_fstop = 4
    fill, _ = light('AREA', O + V((-.3, .2, 2.4)), 40, '#bcd6ff', 1.0, rot=(0, 0, 0), name='cabinfill')     # the garage tubes through the glass roof/side windows
    em = sb_.inputs['Emission Strength']
    if em is not None:                                                   # the screen wakes as it lands (lock screen), then dims
        for f, v in ((1, 0), (36, 0), (37, 6.), (62, 6.), (68, .0)): em.default_value = v; em.keyframe_insert('default_value', frame=f)
    pl, _ = light('POINT', O + V((-.42, .12, 1.03)), 0, '#d8e4ff', .03, name='phoneglow')
    for f, v in ((1, 0), (36, 0), (37, .6), (62, .6), (68, 0)): pl.energy = v; pl.keyframe_insert('energy', frame=f)
    sc.view_settings.exposure = 1.1
    return 1, nf

# ------------------------------------------------------------------ 130-150 overpass + Stalker (v5 cuts 20-22 with the teaser's bull-skull Stalker v5, v7 dark look)
def relight_overpass():
    for l in bpy.data.lights:
        if l.type == 'AREA' and l.color[2] > l.color[0]: l.energy *= .15
        if l.type in ('POINT', 'SPOT') and l.color[0] > 2 * l.color[1]: l.energy *= .25   # the ember eye: a glow in the socket, not a red floodlight
    sc.view_settings.exposure = sc.view_settings.exposure - .9
    w = bpy.context.scene.world
    if w and w.node_tree:
        for nd in w.node_tree.nodes:
            if nd.type == 'BACKGROUND': nd.inputs['Strength'].default_value *= .35
def cut130(): f = cut20(); relight_overpass(); return f
def stalker_cu_light(H=V((.8, -30, 12.4))):
    """teaser look on the Stalker close-ups: fire rim from behind-left, cold rim behind-right, headlight spill from the street below;
    the ember stays a glow inside the sockets (no red flood)"""
    for l in bpy.data.lights:
        if l.type == 'POINT' and l.color[0] > 2 * l.color[1]: l.energy *= .3
    area(H + V((-3.5, -4.0, 2.5)), H, 900, 1.5, '#ff4a1c')
    area(H + V((3.8, -3.5, 1.8)), H, 650, 1.5, '#5a86ff')
    area(H + V((1.0, 6.0, -9.0)), H + V((0, 0, -.3)), 1400, 3, '#d8e2ff')
    for nd in sc.world.node_tree.nodes:          # thin the pink fog wall behind it so the silhouette and skull read
        if nd.bl_idname == 'ShaderNodeVolumeScatter': nd.inputs['Density'].default_value = min(nd.inputs['Density'].default_value, .0008)
def cut140(): f = cut21(); relight_overpass(); stalker_cu_light(); return f
def cut150(): f = cut22(); relight_overpass(); stalker_cu_light(); return f

# ------------------------------------------------------------------ 160 the ending: dashcam still recording, driver's door open, rain blowing in, seat empty, Akash calling
def cut160():
    nf = 252; st = overpass_set(nf, hits=(70, 75, 190))
    st.hide_render = True
    for o_ in st.children_recursive: o_.hide_render = True            # it's gone, and so is he
    O = V((.4, -20.0, 0)); car, parts, glowm, spots = nt_car(tuple(O), 0, lights_on=True)
    for o_ in parts:                                                  # driver's door hangs open: the door skin on the driver side is gone from the frame
        if o_.type == 'MESH' and 'door' in o_.name.lower():
            bb = [o_.matrix_world @ V(cn) for cn in o_.bound_box]
            if sum(v.x for v in bb) / 8 > O.x + .3: o_.hide_render = True
    rain_here(tuple(O + V((2.3, .2, 0))), (1.0, 3.0, 3.0), 900, 1, nf)   # outside the open door only
    fill, _ = light('AREA', O + V((-.2, .2, 2.2)), 18, '#9ab0ff', 1.2, name='cabinfill')
    dash, _ = light('AREA', O + V((0, -.62, 1.2)), 2.5, '#ff4a3a', .4, rot=(math.radians(-70), 0, 0), name='dashglow')
    # the phone on the passenger seat, Akash calling: buzz-rings from f24, then goes to voicemail at f84
    ph = bx('his phone', (0, 0, 0), (.075, .155, .009), K.metal('PhoneBody', '#0d0d0f', .25), bevel=.003)
    img = bpy.data.images.load(os.path.join(HERE, '..', 'pent7', 'phone_screen_akash.png'))
    sm_, tx_ = m_img('AkashScreen', img, rough=.1, emit=.001)
    sb_ = sm_.node_tree.nodes['Principled BSDF']; sb_.inputs['Emission Strength'].default_value = 0
    scr = bx('his phone screen', (0, 0, .0055), (.068, .145, .003), sm_); scr.parent = ph
    home = O + V((-.42, .12, .95))
    for f in range(1, nf + 1):
        buzz = (.0025 * math.sin(f * 2.7)) if (24 <= f < 84 and (f - 24) % 30 < 18) else 0.
        ph.location = home + V((buzz, buzz * .6, 0)); ph.rotation_euler = (-.15, 0, 2.1 + buzz * 3)
        ph.keyframe_insert('location', frame=f); ph.keyframe_insert('rotation_euler', frame=f)
    em = sb_.inputs['Emission Strength']
    for f, v in ((1, 0), (23, 0), (24, 1.3), (nf, 1.3)): em.default_value = v; em.keyframe_insert('default_value', frame=f)
    pl, _ = light('POINT', home + V((0, 0, .08)), 0, '#d8e4ff', .03, name='phoneglow')
    for f, v in ((1, 0), (23, 0), (24, .7), (nf, .7)): pl.energy = v; pl.keyframe_insert('energy', frame=f)
    # the dashcam: same mount as 070, framing both seats; it never moves again (tiny idle vibration, the engine is still running)
    c = camera(16); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    base = O + V((.06, -.64, 1.31)); tgt = O + V((-.18, .4, .8)); nz = A.Noise(160)
    for f in range(1, nf + 1, 2):
        c.location = base + V((0, 0, nz(f * 2.3) * .0008)); aim(c, tgt)
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 1.0; c.data.dof.aperture_fstop = 4
    sc.view_settings.exposure = .9
    return 1, nf

def cut125():   # 125_brute_block: Brute v2 steps into the headlights and roars, the engine growls back, the car swerves past it
    nf = 120; rng, car, parts, br = brute_set(nf)
    for l_ in bpy.data.lights:
        if l_.type == 'AREA' and l_.color[2] > l_.color[0]: l_.energy *= .3     # practical light only: the headlights carry the shot
        if l_.name.startswith('head'): l_.energy = 1800
    br.location = V((-.1, -10.0, 0)); rg = K.char_rig(br)
    A.stomp(rg, br, 1, 26, speed=.8)
    hl_ = bpy.data.lights.new('headwash', 'SPOT'); hl_.energy = 2600; hl_.color = K.C('#fff1d8'); hl_.spot_size = math.radians(40); hl_.spot_blend = .6
    ho_ = bpy.data.objects.new('headwash', hl_); col.objects.link(ho_); ho_.location = (.4, -5.9, .75); aim(ho_, V((-.1, -10, 1.3)))
    for f, v in ((1, 380), (58, 380), (64, 0)): hl_.energy = v; hl_.keyframe_insert('energy', frame=f)
    A.scream(rg, 27, nf, f_scream=34, amp=.9)
    # car: idling, then the rev at f58 (body squats and shudders), then it pulls left and swerves round the Brute
    path = [(1, (.4, -2, 0), 0), (60, (.4, -2.2, 0), 0), (80, (2.3, -7.6, 0), -18), (98, (2.7, -14.5, 0), 5), (nf, (1.0, -24, 0), 12)]
    for f, p, r in path: key(car, f, loc=V(p), rot=(0, 0, math.radians(4 + r)))
    spin_wheels(parts, 60, nf, 23)
    suspension(car, 1, nf, amp=.004, pitch=[(1, 0), (58, 0), (62, 2.6), (68, 1.4), (80, -1.2), (98, 1.0), (nf, 0)])
    c = camera(24)
    shot_cam(c, [(1, (-2.9, 0.4, .75), (-.1, -10, 1.6), 30, 10.8), (56, (-2.8, -.2, .8), (-.1, -10, 1.9), 34, 10),
                 (84, (-2.6, -1.4, .85), (1.4, -9, 1.5), 28, 8), (nf, (-2.4, -2.4, .9), (1.4, -18, 1.4), 24, 14)],
             1, nf, shake=.018, rshake=.35, seed=125)
    kick(c, [34, 36, 60], 1.8); c.data.dof.aperture_fstop = 4.0
    sc.view_settings.exposure = .4
    return 1, nf

# ------------------------------------------------------------------ v8 006: ONE shot. The Screamer stands STILL facing us (no root turn: T13.5),
# the long lens creeps then crash-zooms into her face as she screams. Sound: the v5 scream stem (locked, T13.7).
def cut450():   # v8 050 (T13.3): starts on the stair door into the LOBBY (shoulder push continues 041), then v7 050 shifted +14 f.   v7 050: down into the lobby, the doorman's desk abandoned, the horde floods the avenue outside the glass, a hand slaps it, he backs off to B1 PARKING
    nf = 120; GY = -6.0; O = 14                                   # the glass storefront line; the avenue runs off toward -y beyond it
    hs = horde_set(nf, n=44, near=GY - 1.2, mode='shamble', face=180)
    rng = random.Random(50)
    for i, d in enumerate(hs[:22]):                      # the far crowd: more of them, packed down the avenue into the fog
        e = dup(d, V((rng.uniform(-6, 6), GY - 36 - rng.uniform(0, 14), 0)), math.radians(180 + rng.uniform(-30, 30)), rng.uniform(.95, 1.05))
        A.shamble(K.char_rig(e), e, 1, nf, speed=rng.uniform(.5, .9), period=rng.uniform(1.1, 1.6), phase=rng.uniform(0, 6.3), limp=.3, seed=100 + i, arms='dangle')
    crowd_m = K.metal('CrowdDark', '#140f0d', .9); fig = []
    for i in range(260):                                 # beyond 50 m: hundreds of swaying silhouettes in the fire haze
        x_, y_ = rng.uniform(-9, 9), GY - 50 - rng.uniform(0, 60); h_ = rng.uniform(1.55, 1.85); lean = rng.uniform(-.25, .25)
        fig.append(L.blob('crowd', (x_, y_, h_ * .55), (.2, .14, h_ * .3), col)); fig.append(L.blob('crowd', (x_ + lean * .3, y_, h_ * .93), (.1, .1, .12), col))
        fig.append(L.blob('crowd', (x_, y_, h_ * .22), (.14, .1, h_ * .24), col))
    cr_ = L.join(fig, 'far crowd'); L.setmat(cr_, crowd_m)
    for f in range(1, nf + 1, 6):
        cr_.location = V((math.sin(f * .3) * .04, 0, 0)); cr_.keyframe_insert('location', frame=f)
    for o_ in [o_ for o_ in bpy.data.objects if o_.name.startswith('rain')]: bpy.data.objects.remove(o_, do_unlink=True)
    rain_here((0, GY - 14, 0), (18, 25, 16), 4000, 1, nf)       # rain only OUTSIDE the glass
    for o_ in bpy.data.objects:                                 # nothing of the street may poke through the lobby
        if o_.type == 'MESH' and o_.name not in ('far crowd',) and not o_.name.startswith(('rain',)):
            bb = [o_.matrix_world @ V(cn) for cn in o_.bound_box]
            if min(v.y for v in bb) > GY + .2 and max(v.z for v in bb) < .3: o_.hide_render = True
    for l in bpy.data.lights:                            # the avenue: a few working street lamps and fire glow, no blue fill
        if l.type == 'AREA' and l.color[2] > l.color[0]: l.energy *= .25
    fire = area((6, GY - 30, 6), (0, GY - 10, 1), 3000, 12, '#ff5a1c'); fire_flicker(fire, 1, nf, 3000, seed=50)
    # the lobby interior
    LW, LD, LH = 4.2, 9.0, 3.6
    marble = m_marble(); paint = m_paint('LobbyPaint', '#7d7462', peel=.7); brass = m_brass(); oak = m_wood('Oak')
    wain = m_wood('LobbyWainscot', '#2a170e', .4)
    for m_ in (marble, paint, wain):                    # Sam 2026-11-23: no speckle/dots. Enlarge every texture pattern 4x so surfaces read smooth
        for nd in m_.node_tree.nodes:
            if nd.type == 'MAPPING': nd.inputs['Scale'].default_value = tuple(v * .25 for v in nd.inputs['Scale'].default_value)
            elif nd.type in ('TEX_NOISE', 'TEX_VORONOI', 'TEX_MUSGRAVE') and nd.inputs.get('Scale'): nd.inputs['Scale'].default_value *= .25
    bx('lobbyfloor', (0, GY + LD / 2 + .06, .03), (2 * LW, LD - .1, .1), marble)
    bx('lobbyceil', (0, GY + LD / 2, LH + .05), (2 * LW, LD, .1), m_paint('LobbyCeil', '#8c8771', '#4a4034', .66))
    for s in (1, -1):
        bx('lobbywall', (s * (LW + .05), GY + LD / 2, LH / 2), (.1, LD, LH), paint)
        bx('lobbywain', (s * (LW - .01), GY + LD / 2, .6), (.02, LD, 1.2), wain)
    bx('lobbyback', ((-LW + 2.1) / 2, GY + LD + .05, LH / 2), (LW + 2.1, .1, LH), paint); bx('lobbyback', ((3.1 + LW) / 2, GY + LD + .05, LH / 2), (LW - 3.1, .1, LH), paint)
    bx('lobbyback', (2.6, GY + LD + .05, (2.15 + LH) / 2), (1.0, .1, LH - 2.15), paint)
    # v8: the stair door the take comes through (shouldered open at f2-8, swings into the lobby)
    sw = m_wood('StairDoor', '#2b170f', .45); fr2 = [bx('sdframe', (2.1, GY + LD - .02, 1.08), (.08, .12, 2.16), sw), bx('sdframe', (3.1, GY + LD - .02, 1.08), (.08, .12, 2.16), sw), bx('sdframe', (2.6, GY + LD - .02, 2.18), (1.08, .12, .08), sw)]
    join_ink(fr2, 'stairdoorframe', .003)
    piv2 = bpy.data.objects.new('stairdoor pivot', None); col.objects.link(piv2); piv2.location = (2.15, GY + LD - .02, 0)
    lf2 = [bx('stairdoor', (2.6, GY + LD - .02, 1.05), (.9, .05, 2.1), sw), bx('pushbar', (2.6, GY + LD + .04, 1.0), (.7, .05, .05), brass), bx('sdwin', (2.6, GY + LD + .0, 1.6), (.25, .06, .35), K.metal('WireGlass', '#2a2e30', .2))]
    lf2 = L.join(lf2, 'stair door'); L.hull(lf2, col, .0025)
    for o_ in (lf2, bpy.data.objects.get(lf2.name + ' hull')):
        if o_: o_.parent = piv2; o_.matrix_parent_inverse = piv2.matrix_world.inverted()
    for f_, a_ in ((1, 0), (2, 0), (5, -70), (8, -96), (12, -104)):
        piv2.rotation_euler.z = math.radians(a_); piv2.keyframe_insert('rotation_euler', frame=f_)
    vd = K.concrete('VestDark', '#1a1918'); bx('stairvest', (2.6, GY + LD + 1.2, -.05), (1.8, 2.4, .1), vd); bx('stairvest', (2.6, GY + LD + 2.4, 1.6), (1.8, .1, 3.2), vd)   # the dark landing behind him
    gl = m_glass_rain(); fr_ = []
    for x_ in np.linspace(-LW, LW, 7): fr_.append(bx('mullion', (x_, GY, LH / 2), (.07, .1, LH), brass))
    fr_ += [bx('transom', (0, GY, 2.6), (2 * LW, .1, .07), brass), bx('sill', (0, GY, .05), (2 * LW, .12, .1), brass)]
    join_ink(fr_, 'storefront', .003)
    bx('storeglass', (0, GY, LH / 2), (2 * LW, .012, LH), gl)
    bx('door push L', (-.35, GY + .08, 1.05), (.04, .04, .5), brass); bx('door push R', (.35, GY + .08, 1.05), (.04, .04, .5), brass)
    # the doorman's desk: lamp still on, logbook open, the phone off the hook, his chair knocked over
    dk = [bx('desk', (-2.2, GY + 3.2, .55), (2.0, .7, 1.1), oak), bx('desktop', (-2.2, GY + 3.2, 1.12), (2.15, .8, .05), marble)]
    join_ink(dk, 'doorman desk', .003)
    bx('logbook', (-2.5, GY + 3.25, 1.155), (.4, .3, .02), m_wood('Paper2', '#cdc5b0', .9), rot=(0, 0, .2))
    bx('desk phone', (-1.75, GY + 3.3, 1.18), (.22, .18, .08), K.metal('PhoneBlack', '#111111', .4))
    bx('handset', (-1.6, GY + 2.75, .03), (.22, .06, .05), K.metal('PhoneBlack', '#111111', .4), rot=(0, 0, .7))
    L.setmat(L.tube('phone cord', [V((-1.75, GY + 3.3, 1.15)), V((-1.7, GY + 2.88, .9)), V((-1.62, GY + 2.78, .06))], .006, col, sides=5), K.metal('Cord', '#111111', .6))
    bx('chair', (-2.4, GY + 4.0, .25), (.5, .5, .5), oak, rot=(math.radians(84), 0, .4))
    ld_, _ = light('POINT', (-2.7, GY + 3.2, 1.45), 40, '#ffb46a', .05, name='desklamp')
    sh_ = bx('lampshade', (-2.7, GY + 3.2, 1.45), (.22, .22, .16), m_paint('Shade', '#b0884e', '#6a4a22', .7)); sh_.visible_shadow = False
    bx('pool', (-1.0, GY + 2.2, .003), (.8, .9, .002), m_img('Pool', _tex('pool.png', make_pool), alpha=True, rough=.08)[0])
    # B1 PARKING door on the east wall with its sign
    park = _tex('b1park.png', make_label('B1  PARKING  ↓', (230, 220, 200), (24, 28, 34), (640, 160), 92))
    bx('parkdoor', (LW - .03, GY + 6.6, 1.05), (.05, .95, 2.1), K.metal('ParkDoor', '#3a3e42', .5), ink=.003)
    bx('parksign', (LW - .05, GY + 6.6, 2.35), (.02, .8, .2), m_img('ParkSign', park, rough=.4, emit=1.2)[0])
    el, _ = light('SPOT', (LW - .2, GY + 7.6, 3.2), 40, '#fff1d6', .03, rot=(math.radians(30), math.radians(-25), 0), name='emerg'); el.spot_size = math.radians(90)
    strobe(el, 1, nf, 40, seed=51, on=5, off=(2, 6))
    # the one at the glass: lunges and slaps it at f58 (a smeared handprint appears)
    slap = hs[0]; slap.location = V((.5, GY - .55, 0)); slap.rotation_euler = (0, 0, math.radians(180))
    for f, y in ((1, GY - 1.6), (50 + O, GY - .9), (57 + O, GY - .45), (59 + O, GY - .42), (nf, GY - .5)):
        slap.location.y = y; slap.keyframe_insert('location', frame=f)
    hp = wall_decal('handprint', _tex('smear.png', make_smear), (.55, GY - .012, 1.55), (.35, .25, 1), (math.radians(90), 0, 0))
    hp.hide_render = True; hp.keyframe_insert('hide_render', frame=57 + O); hp.hide_render = False; hp.keyframe_insert('hide_render', frame=58 + O)
    # camcorder POV: off the last stair, past the desk, to the glass, tilt up over the crowd, the slap, back off to B1
    c = camera(21)   # same lens as 041; c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    tl_ = phone_light(c, 30); tl_.spot_size = math.radians(70); tl_.spot_blend = .5; tl_.color = K.C('#ffe2b8')
    feet = [(1, (2.6, GY + 9.7, 0)), (6, (2.6, GY + 9.35, 0)), (11, (2.6, GY + 8.5, 0)), (15, (2.6, GY + 7.6, 0)), (24, (2.1, GY + 6.6, 0)), (33, (1.5, GY + 5.4, 0)), (42, (1.0, GY + 4.2, 0)), (52, (.6, GY + 3.0, 0)),
            (66, (.4, GY + 2.2, 0)), (74, (.45, GY + 2.15, 0)), (82, (.8, GY + 2.9, 0)), (91, (1.4, GY + 3.7, 0)), (100, (1.9, GY + 4.5, 0)), (108, (2.3, GY + 5.1, 0)), (114, (2.9, GY + 5.9, 0)), (nf, (3.45, GY + 6.5, 0))]   # right up to B1 PARKING (055 pushes it)
    looks = [(1, (2.75, GY + LD, 1.35)), (6, (2.2, GY + 3, 1.4)), (15, (0, GY, 1.4)), (30, (-2.2, GY + 3.2, 1.1)), (42, (-1.2, GY, 1.3)),          # the empty desk, then out through the glass
             (54, (0, GY - 12, 1.5)), (66, (0, GY - 30, 7.0)),                               # tilt up: the avenue full of them
             (71, (.5, GY, 1.5)), (78, (.55, GY, 1.5)),                                      # SLAP
             (92, (2.6, GY + 1.0, 1.6)), (106, (LW, GY + 6.6, 1.5)), (nf, (LW, GY + 6.6, 1.3))]                          # backing off, swing onto B1 PARKING
    pov_stairs(c, feet, looks, 1, nf)
    kick(c, [3], 2.4); kick(c, [58 + O], 3.0)
    sc.view_settings.exposure = .3
    return 1, nf

def cut455():   # v8 055 (T13.3): push the B1 PARKING door, run down the service stair, shoulder the garage door, the camcorder lamp dies -> 060 frame 1
    nf = 70; car = garage_set(nf, ign=9999)
    for m_ in bpy.data.materials:                              # the garage is DARK, exactly as 060 frame 1
        if m_.name.startswith('HeadGlow') and m_.node_tree.animation_data: m_.node_tree.animation_data_clear()
    for l in bpy.data.lights:
        if l.animation_data: l.animation_data_clear()
        if l.type == 'SPOT' or l.name == 'fluo': l.energy = 0
    g = bpy.data.materials.get('HeadGlow')
    if g: g.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0
    fm = bpy.data.materials.get('Fluo')
    if fm:
        for nd in fm.node_tree.nodes:
            sk = nd.inputs.get('Strength') if nd.type == 'EMISSION' else nd.inputs.get('Emission Strength') if nd.type == 'BSDF_PRINCIPLED' else None
            if sk is not None: sk.default_value = 0
    steam((2.5, -8), h=1.2, r=2.0, dens=.25, seed=5)
    conc = K.concrete('GarageWall', '#3a3836'); stair_c = K.concrete('StairConc', '#4a4844'); pdoor, _n0, _n1, _n2, _pb = _bsdf('ParkDoorSmooth'); _pb.inputs['Base Color'].default_value = (*K.C('#3a3e42')[:3], 1); _pb.inputs['Roughness'].default_value = .45; _pb.inputs['Metallic'].default_value = .3   # smooth painted steel, no speckle (LOOK 2)
    # cut a door into the east garage wall (x=6) at y=-10.8, the service stair runs outside it
    bpy.data.objects.remove(bpy.data.objects['wallL'], do_unlink=True)
    K.box('wallL', col, (6, (8 + -10.3) / 2, 3), (.2, 18.3, 6), conc); K.box('wallL', col, (6, -11.65, 3), (.2, .7, 6), conc)
    K.box('wallL', col, (6, -10.8, (2.15 + 6) / 2), (.2, 1.0, 6 - 2.15), conc)
    XS = 6.85; YT, ZT = -3.2, 3.0; NS = 11; RUN, RISE = .29, ZT / NS        # the flight: top at y=-3.2 z=3, down toward -y
    steps = []
    for i in range(NS):
        z_ = ZT - RISE * (i + 1); y_ = YT - RUN * (i + .5)
        steps.append(bx('stread', (XS, y_, z_ - .03), (1.3, RUN + .02, .06), stair_c)); steps.append(bx('sriser', (XS, YT - RUN * i, z_ + RISE / 2), (1.3, .02, RISE), stair_c))
    join_ink(steps, 'service flight', .003)
    yb = YT - RUN * NS
    bx('stop landing', (XS, YT + .8, ZT - .08), (1.4, 1.6, .16), stair_c, ink=.003)
    bx('sbot landing', (XS, (yb + -11.7) / 2, -.04), (1.5, yb + 11.7, .08), stair_c)
    for x_ in (6.1, 7.6): bx('swall', (x_, (YT + 1.6 + -11.8) / 2, 3.2), (.12, YT + 1.6 + 11.8, 6.6), stair_c)
    bx('swall', (XS, -11.85, 3.2), (1.6, .12, 6.6), stair_c); bx('swall', (XS, YT + 1.65, 3.2), (1.6, .12, 6.6), stair_c)
    bx('sceil', (XS, (YT + 1.6 + -11.8) / 2, 6.0), (1.6, YT + 1.6 + 11.8, .12), stair_c)
    slope_box('srail', (YT, ZT + .9), (yb, .9), .045, .045, K.metal('RailPaint', '#6a5a1a', .6), XS - .6, ink=.002)
    wall_decal('b1stencil', _tex('b1.png', make_label('B1', (210, 200, 40), (60, 58, 54), (400, 300), 220)), (7.53, -6.0, 2.3), (-.6, .45, 1), (math.radians(90), 0, math.radians(90)), alpha=False)
    wall_decal('pstencil', _tex('parkarrow.png', make_label('P  ↓', (230, 220, 200), (60, 58, 54), (400, 200), 130)), (7.53, -9.5, 1.6), (-.5, .25, 1), (math.radians(90), 0, math.radians(90)), alpha=False)
    wall_decal('sclaw', _tex('claw.png', make_claw), (6.17, -7.6, 1.3), (.5, .5, 1), (math.radians(90), 0, math.radians(-90)))
    cage, _ = light('POINT', (7.4, -7.0, 2.9), 25, '#ffd08a', .05, name='cagebulb')
    L.setmat(L.blob('bulb', (7.45, -7.0, 2.95), (.05, .05, .07), col), K.emit('BulbEm', '#ffd08a', 6))
    flicker(cage, 1, nf, 25, seed=55, p_off=.3)
    # the top door (B1 PARKING, grey metal) is pushed at f1-6, the garage door is shouldered at f46-52
    def leaf(name, hinge, loc, size, a_keys):
        pv = bpy.data.objects.new(name + ' pivot', None); col.objects.link(pv); pv.location = hinge
        lf = bx(name, loc, size, pdoor); L.hull(lf, col, .0025)
        for o_ in (lf, bpy.data.objects.get(lf.name + ' hull')):
            if o_: o_.parent = pv; o_.matrix_parent_inverse = pv.matrix_world.inverted()
        for f_, a_ in a_keys: pv.rotation_euler.z = math.radians(a_); pv.keyframe_insert('rotation_euler', frame=f_)
        return pv
    leaf('topdoor', (7.45, YT + .3, 0), (XS, YT + .3, ZT + 1.05), (.9, .05, 2.1), ((1, 0), (2, 0), (5, 75), (9, 100)))
    bx('topdoorframe', (XS, YT + .3, ZT + 2.2), (1.0, .1, .1), pdoor, ink=.003)
    leaf('garagedoor', (6.0, -10.35, 0), (6.0, -10.8, 1.05), (.05, .9, 2.1), ((1, 0), (45, 0), (48, -70), (53, -98)))
    c = camera(24); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    tl = phone_light(c, 30); tl.spot_size = math.radians(70); tl.spot_blend = .5; tl.color = K.C('#ffe2b8')
    feet = [(1, (XS - .05, YT + 1.1, ZT)), (5, (XS, YT + .55, ZT)), (9, (XS + .1, YT + .05, ZT))]
    for i in range(NS):                                                       # running down, one tread every 3 frames
        feet.append((12 + i * 3, (XS + (.12 if i % 2 else -.12), YT - RUN * (i + .55), ZT - RISE * (i + 1))))
    feet += [(46, (XS, yb - .9, 0)), (50, (6.7, -10.5, 0)), (54, (6.15, -10.8, 0)), (60, (4.8, -10.8, 0)), (nf, (3.6, -10.8, 0))]
    looks = [(1, (XS, YT - 1, ZT + 1.2)), (9, (XS, YT - 2.5, 1.2)), (22, (7.5, -6.0, 2.2)), (32, (XS, yb - 1, .6)),
             (42, (6.0, -10.8, 1.2)), (50, (6.0, -10.8, 1.1)), (56, (2.0, -6, 1.0)), (nf, (.4, -2, .9))]
    pov_stairs(c, feet, looks, 1, nf)
    for f in range(56, nf + 1):                                              # settle into 060's frame-1 camera (low, 24 mm, held)
        t = (f - 56) / (nf - 56); t = t * t * (3 - 2 * t); sc.frame_set(f)
        c.location = c.location.lerp(V((3.6, -10.8, 1.1)), t) if f < nf else V((3.6, -10.8, 1.1))
        if f == nf: aim(c, V((.4, -2, .9)))
        c.keyframe_insert('location', frame=f)
        if f == nf: c.keyframe_insert('rotation_euler', frame=f)
    kick(c, [2], 2.2); kick(c, [47], 2.6)
    for f_, e_ in ((1, 30), (54, 30), (55, 0), (57, 12), (58, 0), (61, 6), (62, 0)):   # the camcorder lamp dies as he enters: dark, like 060 f1
        tl.energy = e_; tl.keyframe_insert('energy', frame=f_)
    for fc in _fcurves(tl.animation_data.action):
        for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
    sc.view_settings.exposure = .6
    c.data.dof.aperture_fstop = 2.8; return 1, nf

def cut470():   # v8 070 (T13.2, teaser windshield approach): no phone toss, no hand. The camcorder is propped on the dash looking OUT through the windshield at the garage door; his voice and the key do the work; the crank shakes the dash.   v7: the camcorder settles on the dash looking back at the passenger seat; his phone is tossed onto it; engine cranks at the end
    nf = 84; car = garage_set(nf, ign=9999)
    for m_ in bpy.data.materials:
        if m_.name.startswith('HeadGlow') and m_.node_tree.animation_data: m_.node_tree.animation_data_clear()
    g = bpy.data.materials.get('HeadGlow')
    if g: g.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value = 0
    for l in bpy.data.lights:
        if l.animation_data: l.animation_data_clear()
        if l.type == 'SPOT': l.energy = 0
    bpy.data.lights['fluo'].energy = 160
    for k, y in enumerate((-8.5, 4.0, -14.5)):
        K.box('tube', col, (.4, y, 5.85), (.12, 2.6, .06), K.emit(f'Fluo{k}', '#cfe8ff', 25))
        ld = bpy.data.lights.new(f'fluo{k}', 'AREA'); ld.shape = 'RECTANGLE'; ld.size = .2; ld.size_y = 2.6; ld.energy = 160; ld.color = K.C('#cfe8ff')
        lo = bpy.data.objects.new(f'fluo{k}', ld); col.objects.link(lo); lo.location = (.4, y, 5.75)
    O = V((.4, -2, 0))                                                     # car root offset (garage_set puts it here, unrotated)
    dash, _ = light('AREA', O + V((0, -.62, 1.2)), 2.5, '#ff4a3a', .4, rot=(math.radians(-70), 0, 0), name='dashglow')   # red dash instrument spill
    # camcorder on the dash: set down (drop + wobble), then still, engine shudder from the crank at f70
    c = camera(18); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    base = O + V((.06, -.64, 1.31)); tgt = O + V((.1, -10.5, 1.15)); nz = [A.Noise(70 + i) for i in range(4)]
    for f in range(1, nf + 1):
        settle = math.exp(-max(0, f - 1) / 5.) if f < 20 else 0.
        crank = (.0035 if 64 <= f < 72 else .0018 if f >= 72 else 0.)
        c.location = base + V((nz[0](f * .9) * .01 * settle, 0, .03 * settle + nz[1](f * 3.1) * crank))
        aim(c, tgt + V((nz[2](f * .7) * .06 * settle, 0, nz[3](f * .8) * .05 * settle)))
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 6.0; c.data.dof.aperture_fstop = 4
    fill, _ = light('AREA', O + V((-.3, .2, 2.4)), 40, '#bcd6ff', 1.0, rot=(0, 0, 0), name='cabinfill')     # the garage tubes through the glass roof/side windows
    sc.view_settings.exposure = 1.1
    return 1, nf

def sam_in_driver_seat(O, nf, keys):
    """append Sam (cast/sam/sam.blend), seat him behind the wheel (car root O, unrotated, front -Y) and key the arms.
    keys: [(frame, right_target_rel, right_turn_deg)]; the left hand stays on the wheel. Face never shown (T: Sam's face)."""
    path = os.path.join(HERE, '..', 'cast', 'sam', 'sam.blend')
    with bpy.data.libraries.load(path) as (src, dst): dst.collections = [n_ for n_ in src.collections if n_ == 'SAM']
    for c_ in dst.collections: sc.collection.children.link(c_)
    rig = [o_ for c_ in dst.collections for o_ in c_.all_objects if o_.type == 'ARMATURE'][0]
    for o_ in [o_ for c_ in dst.collections for o_ in c_.all_objects if o_.type in ('LIGHT', 'CAMERA') or o_.name == 'floor']: bpy.data.objects.remove(o_)
    def aimb(bn, d):
        pb = rig.pose.bones[bn]; bpy.context.view_layer.update()
        M = rig.matrix_world.to_3x3().normalized(); cur = pb.matrix.copy(); cd = (cur.to_3x3() @ V((0, 1, 0))).normalized()
        q = cd.rotation_difference((M.inverted() @ V(d)).normalized())
        pb.matrix = Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ cur.to_3x3().normalized().to_4x4() @ Matrix.Diagonal(cur.to_scale()).to_4x4()
        bpy.context.view_layer.update()
    def ik(s, T, pole):
        bpy.context.view_layer.update(); Wm = rig.matrix_world; pbs = rig.pose.bones
        S_ = Wm @ pbs[f'upperarm01.{s}'].head; k = Wm.to_scale().x
        a_ = (pbs[f'upperarm01.{s}'].bone.length + pbs[f'upperarm02.{s}'].bone.length) * k
        b_ = (pbs[f'lowerarm01.{s}'].bone.length + pbs[f'lowerarm02.{s}'].bone.length) * k
        dv = T - S_; d_ = min(dv.length, a_ + b_ - .01); u = dv.normalized()
        pp = (V(pole) - u * V(pole).dot(u)).normalized()
        al = math.acos(max(-1, min(1, (a_ * a_ + d_ * d_ - b_ * b_) / (2 * a_ * d_))))
        E = S_ + a_ * (u * math.cos(al) + pp * math.sin(al)); ua, la = (E - S_).normalized(), (T - E).normalized()
        for bn in ('upperarm01', 'upperarm02'): aimb(f'{bn}.{s}', tuple(ua))
        for bn in ('lowerarm01', 'lowerarm02'): aimb(f'{bn}.{s}', tuple(la))
        return la
    GL = O + V((.235, -.40, 1.25)); GR = O + V((.565, -.38, 1.25))      # grips on the wheel rim (10 and 2)
    def pose_at(f, RT, turn):
        for pb_ in rig.pose.bones: pb_.matrix_basis = Matrix()
        bpy.context.view_layer.update()
        br = math.sin(f / 24 * 2 * math.pi * .55) * .012                    # fast, scared breathing
        for bn in ('spine05', 'spine04', 'spine03'): aimb(bn, (0, -.42 - br, .9))
        for bn in ('spine02', 'spine01'): aimb(bn, (0, -.18, .98))
        for bn in [b.name for b in rig.pose.bones if b.name.startswith('neck')]: aimb(bn, (0, -.55, .83))
        aimb('head', (0, -.75, .66))                                       # head down toward the column, eyes on the key
        for s, sg in (('L', 1), ('R', -1)):
            for bn in ('upperleg01', 'upperleg02'): aimb(f'{bn}.{s}', (sg * .12, -.84, .5))
            for bn in ('lowerleg01', 'lowerleg02'): aimb(f'{bn}.{s}', (sg * .03, -.28, -1))
            aimb(f'foot.{s}', (sg * .05, -1, -.2))
        la = ik('L', GL, (1, .2, -1)); aimb('wrist.L', tuple((la + V((0, 0, .25))).normalized()))
        la = ik('R', RT, (-1, .2, -1)); w = (la + V((0, 0, .25))).normalized()
        aimb('wrist.R', tuple(w))
        pb = rig.pose.bones['wrist.R']; pb.rotation_mode = 'XYZ'; pb.rotation_euler.y += math.radians(turn)
        for side in ('L', 'R'):
            for fg in range(1, 6):
                for k_ in (1, 2, 3):
                    b = rig.pose.bones.get(f'finger{fg}-{k_}.{side}')
                    if b: b.rotation_mode = 'XYZ'; b.rotation_euler = (math.radians(52 if k_ == 1 else 48), 0, 0)
    # seat him: hips on the cushion (top z .90 rel), back against the shell
    pose_at(1, GR, 0)
    W_ = rig.matrix_world
    hip = (W_ @ rig.pose.bones['upperleg02.L'].head + W_ @ rig.pose.bones['upperleg02.R'].head) / 2
    rig.location += (O + V((.40, .34, .99))) - hip; bpy.context.view_layer.update()
    for f, RT, turn in keys:
        pose_at(f, RT, turn)
        for pb_ in rig.pose.bones:
            pb_.keyframe_insert('rotation_quaternion' if pb_.rotation_mode == 'QUATERNION' else 'rotation_euler', frame=f); pb_.keyframe_insert('location', frame=f)
    return rig, GR

def cut471():   # v8 070 (T13.2): over HIS shoulder from the camcorder wedged on the passenger headrest: hands on the wheel, the right hand goes to the key, "Please start. Please.", it cranks
    f0, nf = cut470()
    O = V((.4, -2, 0)); IGN = O + V((.53, -.58, 1.07))
    R0 = O + V((.565, -.38, 1.25))
    keys = [(1, R0, 0), (10, R0, 0), (20, R0 + V((0, .01, -.01)), 0), (34, R0, 0), (42, R0 + V((-.02, .06, -.06)), 0),
            (50, IGN + V((0, .04, .03)), 0), (56, IGN, 0), (60, IGN, 0), (63, IGN, 55), (nf, IGN, 50)]
    rig, _ = sam_in_driver_seat(O, nf, keys)
    c = camera(22); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    base = O + V((.02, .98, 1.7)); tgt = O + V((.42, -.6, 1.12)); nz = [A.Noise(471 + i) for i in range(4)]
    for f in range(1, nf + 1):
        crank = (.004 if 64 <= f < 72 else .002 if f >= 72 else 0.)
        c.location = base + V((nz[0](f * .4) * .004, nz[1](f * .5) * .003, nz[2](f * .45) * .003 + nz[1](f * 3.1) * crank))
        aim(c, tgt + V((nz[3](f * .35) * .02, 0, nz[2](f * .3) * .015)))
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f)
    kick(c, [64], 1.0)
    c.data.dof.use_dof = True; c.data.dof.focus_distance = 1.25; c.data.dof.aperture_fstop = 4
    tl = phone_light(c, 14); tl.spot_size = math.radians(80); tl.spot_blend = .6; tl.color = K.C('#ffe2b8')   # the camcorder lamp, low so it only rims him
    sc.view_settings.exposure = 1.0
    return 1, nf

def cut490():   # v8 090 gate burst: one take, low road camera. The car tears up the garage ramp under the half-open roll gate, hops the kerb, fishtails left into the rain (T13.3/T13.4: nothing passes through anything)
    nf = 84; rng = base_street(seed=9, length=140, fog=.006, dead=(1, 3), wrecks=False, exposure=1.0)
    for o_ in list(bpy.data.objects):                     # clear the +x block where the garage exit goes
        if o_.type != 'MESH': continue
        bb = [o_.matrix_world @ V(cn) for cn in o_.bound_box]
        if min(v.x for v in bb) > 9.5 and max(v.y for v in bb) > -17 and min(v.y for v in bb) < -3: o_.hide_render = True; o_.hide_viewport = True
    conc = K.concrete('GarageWall', '#3a3836'); brick = K.concrete('ExitBrick', '#4a3a32'); slat_m = K.metal('Door', '#2a2c2e', .55)
    K.box('exitfacade', col, (10.15, -5.0, 6), (.3, 2.0, 12), brick); K.box('exitfacade', col, (10.15, -15.0, 6), (.3, 6.0, 12), brick)
    K.box('exitfacade', col, (10.15, -10, 7.2), (.3, 8.0, 9.6), brick)
    K.box('exitfacade', col, (10.15, -6.6, 1.2), (.3, 1.2, 2.4), brick); K.box('exitfacade', col, (10.15, -13.4, 1.2), (.3, 1.2, 2.4), brick)
    for k in range(5): K.box('gateslat', col, (10.05, -10, 2.32 + k * .26), (.08, 5.8, .22), slat_m)       # roll gate jammed half open
    ang = math.atan2(2.5, 10.)
    rp = bx('ramp', (15.0, -10, -1.3), (10.3, 5.6, .1), conc, rot=(0, ang, 0))
    for s_ in (1, -1): bx('rampwall', (15.0, -10 + s_ * 2.85, 0), (10.4, .12, 5.2), conc)
    bx('rampceil', (15.0, -10, 2.55), (10.4, 5.8, .12), conc)
    tub, _ = light('AREA', (14.0, -10, 2.3), 220, '#cfe8ff', 1.2, rot=(0, 0, 0), name='rampfluo'); flicker(tub, 1, nf, 220, seed=90, p_off=.2)
    K.box('rampfluo', col, (14.0, -10, 2.47), (2.6, .12, .05), K.emit('RampFluoEm', '#cfe8ff', 20))
    car, parts, glowm, spots = nt_car((18, -10, -2.0), math.radians(-90), lights_on=True)
    keys = [(1, (18.0, -10, -2.0), -90, -14), (22, (10.5, -10, -.125), -90, -14), (26, (9.2, -10, .08), -90, -5), (30, (8.0, -10, 0), -90, 3),
            (34, (6.8, -10.2, 0), -88, 0), (50, (3.2, -12.5, 0), -35, 0), (58, (1.2, -15.5, 0), 12, 0), (66, (.6, -19.5, 0), -6, 0),
            (74, (.4, -24.0, 0), 2, 0), (nf, (.4, -30.5, 0), 0, 0)]
    car.rotation_mode = 'XYZ'
    for f, p, yaw, pit in keys:
        car.location = p; car.rotation_euler = (math.radians(pit), 0, math.radians(yaw))
        car.keyframe_insert('location', frame=f); car.keyframe_insert('rotation_euler', frame=f)
    dist = sum((V(b[1]) - V(a[1])).length for a, b in zip(keys, keys[1:]))
    spin_wheels(parts, 1, nf, dist)
    suspension(car, 1, nf, amp=.012, pitch=[(1, 0), (28, 0), (31, 2.5), (36, -1), (40, 0), (54, 0), (58, -1.2), (64, .8), (nf, 0)])
    rain_here((2, -16, 0), (22, 34, 14), 6000, 1, nf)
    lamp_spot((1.5, -13, 7.5), 3500); fire = area((-6, -60, 6), (0, -20, 1), 2600, 10, '#ff5a1c'); fire_flicker(fire, 1, nf, 2600, seed=91)
    c = camera(22); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30
    nz = [A.Noise(490 + i) for i in range(4)]; trail = []
    for f in range(1, nf + 1):
        sc.frame_set(f); trail.append(car.matrix_world.translation.copy())
    for f in range(1, nf + 1):
        u = (f - 1) / (nf - 1); u_ = u * u * (3 - 2 * u)
        loc = V((-1.4, -3.6, .55)).lerp(V((-2.3, -21.0, .75)), u_) + V((nz[0](f * .21) * .03, nz[1](f * .19) * .03, nz[2](f * .3) * .012))
        tg = trail[max(0, f - 4)] + V((0, 0, .9))                       # the aim lags the car by 3 frames (documentary)
        c.location = loc; aim(c, tg); c.rotation_euler.y += math.radians(nz[3](f * .25) * 1.2)
        c.data.dof.focus_distance = max(1.5, (tg - loc).length)
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f); c.data.dof.keyframe_insert('focus_distance', frame=f)
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = 4.0
    kick(c, [30], 1.6); kick(c, [58], 1.0)
    return 1, nf

def load_sam():
    """append Sam's rig (cast/sam/sam.blend). Returns rig, aimb(bone, dir), ik(side, target, pole). Face NEVER shown."""
    path = os.path.join(HERE, '..', 'cast', 'sam', 'sam.blend')
    with bpy.data.libraries.load(path) as (src, dst): dst.collections = [n_ for n_ in src.collections if n_ == 'SAM']
    for c_ in dst.collections: sc.collection.children.link(c_)
    rig = [o_ for c_ in dst.collections for o_ in c_.all_objects if o_.type == 'ARMATURE'][0]
    for o_ in [o_ for c_ in dst.collections for o_ in c_.all_objects if o_.type in ('LIGHT', 'CAMERA') or o_.name == 'floor']: bpy.data.objects.remove(o_)
    def aimb(bn, d):
        pb = rig.pose.bones[bn]; bpy.context.view_layer.update()
        M = rig.matrix_world.to_3x3().normalized(); cur = pb.matrix.copy(); cd = (cur.to_3x3() @ V((0, 1, 0))).normalized()
        q = cd.rotation_difference((M.inverted() @ V(d)).normalized())
        pb.matrix = Matrix.Translation(cur.translation) @ q.to_matrix().to_4x4() @ cur.to_3x3().normalized().to_4x4() @ Matrix.Diagonal(cur.to_scale()).to_4x4()
        bpy.context.view_layer.update()
    def ik(s, T, pole):
        bpy.context.view_layer.update(); Wm = rig.matrix_world; pbs = rig.pose.bones
        S_ = Wm @ pbs[f'upperarm01.{s}'].head; k = Wm.to_scale().x
        a_ = (pbs[f'upperarm01.{s}'].bone.length + pbs[f'upperarm02.{s}'].bone.length) * k
        b_ = (pbs[f'lowerarm01.{s}'].bone.length + pbs[f'lowerarm02.{s}'].bone.length) * k
        dv = T - S_; d_ = min(dv.length, a_ + b_ - .01); u = dv.normalized()
        pp = (V(pole) - u * V(pole).dot(u)).normalized()
        al = math.acos(max(-1, min(1, (a_ * a_ + d_ * d_ - b_ * b_) / (2 * a_ * d_))))
        E = S_ + a_ * (u * math.cos(al) + pp * math.sin(al)); ua, la = (E - S_).normalized(), (T - E).normalized()
        for bn in ('upperarm01', 'upperarm02'): aimb(f'{bn}.{s}', tuple(ua))
        for bn in ('lowerarm01', 'lowerarm02'): aimb(f'{bn}.{s}', tuple(la))
        return la
    return rig, aimb, ik

WIN = V((-6.3, -5.0, 33.6))          # Sam's penthouse window (006 looks out of it at the Screamer roof)
def watcher_set(nf, sam='seated', screamer=False, lightning_at=(9999,)):
    """the street seen from far away + Sam's tower on the -x side with his lit penthouse window (T15.2 hidden watcher)"""
    s = roof_set(nf, lightning_at)
    if not screamer:
        for o_ in [s] + list(s.children_recursive): o_.hide_render = True
    mat = K.facade('SamTower', '#33302c', lit=.22, seed=8.1, brick=False)
    K.box('samtower', col, (-14.3, -5.0, 18.5), (8, 14, 37), mat)
    for yy in (-12.0, 2.0): K.box('samside', col, (-8.3, yy, 18.5), (4.0, .06, 37), mat)
    K.box('samroof', col, (-8.3, -5.0, 37.0), (4.0, 14, .1), K.concrete('Roof', '#2a2928'))
    for zz in [3.4 * k for k in range(1, 11)]: K.box('ledge', col, (-6.25, -5.0, zz), (.12, 14.1, .1), K.concrete('Trim', '#4a4640'))
    # the penthouse: a deep warm room behind a big pane (the room box sits INSIDE the tower volume, cut by hiding the facade face there)
    room = K.concrete('RoomWarm', '#5a4636')
    K.box('pent floor', col, (-8.3, -5.0, 32.35), (4.0, 5.0, .1), room); K.box('pent back', col, (-10.2, -5.0, 34.0), (.1, 5.0, 3.4), room)
    for dy in (-2.5, 2.5): K.box('pent side', col, (-8.3, -5.0 + dy, 34.0), (4.0, .1, 3.4), room)
    K.box('pent ceil', col, (-8.3, -5.0, 35.65), (4.0, 5.0, .1), room)
    hole = [K.box('samfront', col, (-6.28, -5.0 + dy * 4.85, 18.5), (.06, 4.3, 37), mat) for dy in (-1, 1)]
    K.box('samfront', col, (-6.28, -5.0, 16.1), (.06, 5.4, 32.2), mat); K.box('samfront', col, (-6.28, -5.0, 36.4), (.06, 5.4, 1.2), mat)
    for zz in (32.3, 35.7): K.box('mullion', col, (-6.26, -5.0, zz), (.08, 5.4, .08), K.metal('Frame', '#1a1a1a', .5))
    for yy in (-7.6, -5.0, -2.4): K.box('mullion', col, (-6.26, yy, 34.0), (.08, .08, 3.4), K.metal('Frame', '#1a1a1a', .5))
    lamp, _ = light('POINT', (-9.0, -4.0, 34.6), 260, '#ffb46a', .3, name='pent lamp')
    tv, _ = light('AREA', (-9.8, -6.2, 33.4), 90, '#ff7a3a', 1.2, rot=(0, math.radians(90), 0), name='pent firelight')   # the burning city reflected inside
    fire_flicker(tv, 1, nf, 90, seed=40)
    rig, aimb, ik = load_sam()
    for pb_ in rig.pose.bones: pb_.matrix_basis = Matrix()
    bpy.context.view_layer.update()
    rig.rotation_euler.z = math.radians(-90)          # he faces the glass (+x)
    if sam == 'seated':                               # asleep in the armchair (the hook: "and I slept through it")
        for bn in ('spine05', 'spine04', 'spine03'): aimb(bn, (.38, 0, .92))      # he faces -x (back to the glass): the watcher sees the chair back + his hair, never the face
        for bn in ('spine02', 'spine01'): aimb(bn, (.22, 0, .97))
        for bn in [b.name for b in rig.pose.bones if b.name.startswith('neck')]: aimb(bn, (.25, .35, .9))
        aimb('head', (.35, .55, .75))
        for s_, sg in (('L', 1), ('R', -1)):
            for bn in ('upperleg01', 'upperleg02'): aimb(f'{bn}.{s_}', (-1, -sg * .16, .06))
            for bn in ('lowerleg01', 'lowerleg02'): aimb(f'{bn}.{s_}', (-.32, -sg * .06, -1))
            for bn in ('upperarm01', 'upperarm02'): aimb(f'{bn}.{s_}', (-.2, -sg * .28, -1))
            for bn in ('lowerarm01', 'lowerarm02', 'wrist'): aimb(f'{bn}.{s_}', (-1, -sg * .08, -.1))
        K.box('armchair', col, (-8.6, -4.2, 32.65), (.9, .9, .5), K.concrete('ChairDark', '#2a1c14')); K.box('armchair back', col, (-8.02, -4.2, 33.0), (.18, .95, .8), K.concrete('ChairDark', '#2a1c14'))
        bpy.context.view_layer.update(); W_ = rig.matrix_world
        hip = (W_ @ rig.pose.bones['upperleg02.L'].head + W_ @ rig.pose.bones['upperleg02.R'].head) / 2
        rig.location += V((-8.55, -4.2, 32.98)) - hip
        bpy.context.view_layer.update(); print('SAMSEAT hip', tuple(round(v, 2) for v in ((rig.matrix_world @ rig.pose.bones['upperleg02.L'].head))), 'head', tuple(round(v, 2) for v in (rig.matrix_world @ rig.pose.bones['head'].tail)), 'scale', tuple(rig.matrix_world.to_scale()))
    else:                                             # standing at the glass, phone to the ear (004w)
        for s_, sg in (('L', 1), ('R', -1)):
            for bn in ('upperleg01', 'upperleg02', 'lowerleg01', 'lowerleg02'): aimb(f'{bn}.{s_}', (0, sg * .05, -1))
        for bn in ('upperarm01.L', 'upperarm02.L'): aimb(bn, (0, .12, -1))
        for bn in ('lowerarm01.L', 'lowerarm02.L', 'wrist.L'): aimb(bn, (.15, .08, -1))
        bpy.context.view_layer.update(); W_ = rig.matrix_world
        hd = W_ @ rig.pose.bones['head'].head; ik('R', hd + V((.02, -.1, -.03)), (-.6, -1, -.4))
        bpy.context.view_layer.update()
        heel = W_ @ rig.pose.bones['foot.L'].head
        rig.location += V((-6.95, -5.3, 32.42)) - V((heel.x, heel.y, heel.z - .06))
    return rig

def watcher_cam(nf, keys, seed=400, hunt=()):
    """the hidden camcorder: long lens from a far roof. keys [(f, loc, target, lens)], focus on the target with
    hunting [(f0, f1, amount_m)] where the AF breathes and misses before it locks; tiny handheld drift magnified by the lens"""
    c = camera(keys[0][3]); c.data.sensor_fit = 'VERTICAL'; c.data.sensor_height = 30; c.data.clip_end = 2000
    nz = [A.Noise(seed + i) for i in range(5)]; fr = [k[0] for k in keys]
    for f in range(1, nf + 1):
        i = max(0, min(len(keys) - 2, sum(1 for x in fr if x <= f) - 1)); a, b = keys[i], keys[i + 1]
        t = max(0., min(1., (f - a[0]) / max(1, b[0] - a[0]))); t = t * t * (3 - 2 * t)
        loc = V(a[1]).lerp(V(b[1]), t); tg = V(a[2]).lerp(V(b[2]), t); lens = a[3] + (b[3] - a[3]) * t
        c.location = loc; aim(c, tg)
        k_ = 35. / max(lens, 35.)                                          # the longer the lens the smaller the hand drift in degrees, but it still shows
        c.rotation_euler.x += math.radians(nz[0](f * .13) * .9 * k_ + nz[1](f * .9) * .05)
        c.rotation_euler.z += math.radians(nz[2](f * .11) * 1.1 * k_ + nz[3](f * .8) * .05)
        c.data.lens = lens
        fd = (tg - loc).length
        for h0, h1, amt in hunt:
            if h0 <= f <= h1: u = (f - h0) / max(1, h1 - h0); fd += amt * math.sin(u * math.pi * 3) * (1 - u)
        c.data.dof.focus_distance = fd
        c.keyframe_insert('location', frame=f); c.keyframe_insert('rotation_euler', frame=f); c.data.keyframe_insert('lens', frame=f); c.data.dof.keyframe_insert('focus_distance', frame=f)
    c.data.dof.use_dof = True; c.data.dof.aperture_fstop = 5.6
    return c

WPOS = V((36.0, -52.0, 46.0))        # the watcher's roof, far across and down the avenue

def cut400():   # v8 000_hook: the hidden camera on a far roof films the burning skyline, hunts, zooms into his window: he is asleep in the chair. "Then... boom": a tower beyond erupts, flash, the zoom snaps out
    nf = 168; watcher_set(nf, 'seated')
    K.box('watcher parapet', col, (WPOS.x - .6, WPOS.y + .9, WPOS.z - 1.2), (3, .3, 1.0), K.concrete('Parapet', '#2a2826'))   # his own roof edge, out of focus at the bottom
    fb = L.blob('fireball', (-48, -14, 50), (1, 1, 1), col); fb.scale = (.01, .01, .01)
    fm = bpy.data.materials.new('FireballVol'); fm.use_nodes = True; nt_ = fm.node_tree; nn = nt_.nodes; ll = nt_.links
    for x_ in list(nn):
        if x_.type != 'OUTPUT_MATERIAL': nn.remove(x_)
    pv_ = nn.new('ShaderNodeVolumePrincipled'); tx = nn.new('ShaderNodeTexNoise'); tx.inputs['Scale'].default_value = 3.6; tx.inputs['Detail'].default_value = 12; tx.inputs['Roughness'].default_value = .7; tx.inputs['Distortion'].default_value = .9
    cr = nn.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = .5; cr.color_ramp.elements[1].position = .66
    tcn = nn.new('ShaderNodeTexCoord'); gr_ = nn.new('ShaderNodeTexGradient'); gr_.gradient_type = 'SPHERICAL'; ll.new(tcn.outputs['Object'], gr_.inputs['Vector']); ll.new(tcn.outputs['Object'], tx.inputs['Vector'])
    ad_ = nn.new('ShaderNodeMath'); ad_.operation = 'MULTIPLY_ADD'; ll.new(tx.outputs['Fac'], ad_.inputs[0]); ad_.inputs[1].default_value = .7; ll.new(gr_.outputs['Fac'], ad_.inputs[2])
    cr.color_ramp.elements[0].position = .62; cr.color_ramp.elements[1].position = .8
    ll.new(ad_.outputs[0], cr.inputs['Fac']); dm = nn.new('ShaderNodeMath'); dm.operation = 'MULTIPLY'; dm.inputs[1].default_value = .9; ll.new(cr.outputs['Color'], dm.inputs[0]); ll.new(dm.outputs[0], pv_.inputs['Density'])
    pv_.inputs['Color'].default_value = (.02, .015, .012, 1); pv_.inputs['Blackbody Tint'].default_value = (1, .55, .25, 1)
    hc_ = nn.new('ShaderNodeMath'); hc_.operation = 'MULTIPLY'; ll.new(gr_.outputs['Fac'], hc_.inputs[0]); ll.new(tx.outputs['Fac'], hc_.inputs[1])
    cr2 = nn.new('ShaderNodeValToRGB'); cr2.color_ramp.elements[0].position = .24; cr2.color_ramp.elements[1].position = .5; ll.new(hc_.outputs[0], cr2.inputs['Fac'])
    em2 = nn.new('ShaderNodeMath'); em2.operation = 'MULTIPLY'; em2.inputs[1].default_value = 14.0; ll.new(cr2.outputs['Color'], em2.inputs[0]); ll.new(em2.outputs[0], pv_.inputs['Emission Strength']); pv_.inputs['Emission Color'].default_value = (1, .38, .08, 1)
    ll.new(pv_.outputs[0], [x_ for x_ in nn if x_.type == 'OUTPUT_MATERIAL'][0].inputs['Volume']); L.setmat(fb, fm)
    for k_, (fx, fy, fz) in enumerate(((-70, -40, 30), (-55, -95, 26), (-90, -20, 40), (40, -120, 22))):     # the city already burning
        fa = area((fx, fy, fz), (fx + 1, fy + 1, 0), 9000, 14, '#ff5a1c'); fire_flicker(fa, 1, nf, 9000, seed=400 + k_)
        K.box('burning floors', col, (fx, fy, fz - 6), (10, 10, 4), K.emit(f'BurnEm{k_}', '#ff6a22', 6))
    fl, _ = light('POINT', (-48, -14, 52), 0, '#ff8a3a', 4, name='blast')
    for f, s_, e_, le in ((1, .01, 0, 0), (127, .01, 0, 0), (128, 3, 40, 6e4), (132, 6, 30, 3e4), (146, 9, 14, 1.4e4), (nf, 12, 8, 7e3)):
        fb.scale = (s_, s_, s_ * .8); fb.keyframe_insert('scale', frame=f); fl.energy = le; fl.keyframe_insert('energy', frame=f)
        ems = pv_.inputs['Emission Strength']
        if not ems.is_linked: ems.default_value = e_; ems.keyframe_insert('default_value', frame=f)
    tw = V((-8.3, -4.15, 33.45))     # Sam's head and shoulders over the chair back
    rl_, _ = light('POINT', (-9.6, -3.0, 33.9), 90, '#ffc58a', .25, name='reading lamp rim')   # his reading lamp rims his hair and shoulders
    c = watcher_cam(nf, [(1, WPOS, V((-30, -10, 40)), 38), (30, WPOS, V((-20, -6, 38)), 42), (59, WPOS, tw, 180), (102, WPOS, tw, 560),
                         (127, WPOS, tw, 590), (130, WPOS, tw + V((0, 0, .3)), 360), (140, WPOS, V((-38, -12, 46)), 80), (nf, WPOS, V((-44, -13, 48)), 62)],
                    seed=400, hunt=((59, 98, 9.0),))
    kick(c, [128], 2.6); kick(c, [134], 1.2)
    sc.view_settings.exposure = .4
    return 1, nf

def cut404():   # v8 004w_watcher: the same hidden lens, Sam standing at the glass on the phone, slow zoom, focus hunting; we never learn who films
    nf = 60; watcher_set(nf, 'standing', screamer=True)
    tw = WIN + V((-.6, -.3, -.1))
    c = watcher_cam(nf, [(1, WPOS, tw + V((0, 1.5, -1.2)), 240), (24, WPOS, tw, 330), (nf, WPOS, tw + V((0, 0, .1)), 420)], seed=404, hunt=((1, 30, 7.0), (40, 48, 2.0)))
    sc.view_settings.exposure = .4
    return 1, nf

def cut525():   # v8 125: the Brute steps out and roars; the car brakes hard; it CHARGES; reverse + J-turn; its shoulder slams the rear quarter
    # as the car whips round (car kicks, Brute staggers), the car escapes the other way, the Brute roars after it. Collision-checked (T13.4).
    nf = 144; rng, car, parts, br = brute_set(nf)
    for l_ in bpy.data.lights:
        if l_.type == 'AREA' and l_.color[2] > l_.color[0]: l_.energy *= .3
        if l_.name.startswith('head'): l_.energy = 1800
    rg = K.char_rig(br)
    br.location = V((-.1, -10.5, 0)); br.rotation_euler = (0, 0, math.radians(188))
    A.stomp(rg, br, 1, 28, speed=.8)
    A.scream(rg, 29, 56, f_scream=36, amp=.9)
    br.rotation_euler = (0, 0, math.radians(175)); br.keyframe_insert('rotation_euler', frame=56)
    br.rotation_euler = (0, 0, math.radians(188)); br.keyframe_insert('rotation_euler', frame=50)
    A.stomp(rg, br, 57, 86, speed=5.2, period=.95, seed=9)          # the charge
    p86 = br.location.copy()
    for f, d, yaw in ((90, V((-.35, -.55, 0)), 168), (98, V((-.6, -1.0, 0)), 160)):   # the hit knocks it back a stride, it twists
        br.location = p86 + d; br.keyframe_insert('location', frame=f); br.rotation_euler = (0, 0, math.radians(yaw)); br.keyframe_insert('rotation_euler', frame=f)
    A.scream(rg, 99, nf, f_scream=106, amp=1.0)
    # the car: arrives braking hard, stops; reverse; J-turn (nose swings away, rear swings toward it); escape +y
    path = [(1, (.4, 12.0, 0), 4), (22, (.4, -1.4, 0), 4), (28, (.4, -2.0, 0), 4), (58, (.4, -2.0, 0), 4), (72, (.6, -.4, 0), 8),
            (80, (.6, .0, 0), 70), (86, (.42, .05, 0), 150), (90, (.75, .6, 0), 178), (100, (1.1, 4.5, 0), 184), (nf, (.6, 24.0, 0), 182)]
    for f, p, r in path: key(car, f, loc=V(p), rot=(0, 0, math.radians(r)))
    dist = sum((V(b[1]) - V(a[1])).length for a, b in zip(path, path[1:]))
    spin_wheels(parts, 1, nf, dist)
    suspension(car, 1, nf, amp=.006, pitch=[(1, 0), (14, 0), (22, -3.2), (28, 1.4), (34, 0), (58, 0), (60, -1.6), (72, .8), (86, -.5), (87, 2.2), (92, -1.0), (100, 2.0), (110, 0), (nf, 0)])
    # collision check: car as an oriented box, Brute as a capsule; contact only at the hit (<= 15 cm), never through
    worst = []; gaps = []
    for f in range(1, nf + 1):
        sc.frame_set(f); M = car.matrix_world; inv = M.inverted()
        b = inv @ (br.matrix_world.translation + V((0, 0, 1.2)))
        dx = max(0., abs(b.x) - .98); dy = max(0., (b.y - 2.25) if b.y > 0 else (-2.4 - b.y))
        pen = .75 - math.hypot(dx, dy)
        if pen > 0: worst.append((f, round(pen, 2)))
        gaps.append((round(-pen, 2), f))
    print('COLLISION', worst, 'MINGAP', sorted(gaps)[:4], 'BR86', tuple(round(v, 2) for v in p86))
    hl_ = bpy.data.lights.new('headwash', 'SPOT'); hl_.energy = 380; hl_.color = K.C('#fff1d8'); hl_.spot_size = math.radians(40); hl_.spot_blend = .6
    ho_ = bpy.data.objects.new('headwash', hl_); col.objects.link(ho_); ho_.parent = car; ho_.location = (0, -2.3, .75); ho_.rotation_euler = (math.radians(90), 0, 0)
    lamp_spot((-.6, -3.2, 7.2), 6500, '#ffb060', 80); lamp_spot((-3.5, 4.0, 6.8), 1600, '#ffb060', 70, flick=(1, nf))   # two working street lamps light the hit
    fz = area((6, -16, 5), (0, -2, 1), 2200, 6, '#ff5a1c'); fire_flicker(fz, 1, nf, 2200, seed=525)
    c = camera(24)
    shot_cam(c, [(1, (-4.2, 3.2, .9), (.2, -6, 1.5), 26, 9), (28, (-4.2, 3.0, .9), (-.1, -9, 1.9), 30, 10), (56, (-4.1, 2.6, .95), (-.1, -9, 2.0), 34, 9.5),
                 (84, (-4.0, 2.2, 1.0), (.8, -2.0, 1.4), 26, 5.5), (98, (-3.8, 2.4, 1.0), (.8, 3.0, 1.2), 24, 5), (106, (-3.7, 2.2, 1.0), (-1.8, -3.6, 2.0), 30, 6.3), (nf, (-3.4, 1.4, 1.05), (-1.8, -3.7, 2.1), 34, 5.4)],
             1, nf, shake=.02, rshake=.4, seed=525)
    kick(c, [36, 38, 87], 2.0); kick(c, [106], 1.4); c.data.dof.aperture_fstop = 4.0
    sc.view_settings.exposure = .4
    return 1, nf

def cut406():
    nf = 96; s = roof_set(nf, (70,)); rig = K.char_rig(s)
    s.rotation_euler = (0, 0, math.radians(-134))           # already facing his window; never keyed
    A.idle(rig, 1, 58, amp=.35)
    A.scream(rig, 59, nf, f_scream=66, amp=.3)
    relight_roof(nf, [70], fire_e=1800)
    h = bone_w(s, 'head', 1)
    c = camera(135)
    P = (-5.5, -5.0, 33.6)
    # slow creep 135 -> 190 mm (searching), then a crash zoom 190 -> 520 mm over 10 frames as the mouth opens
    shot_cam(c, [(1, P, h + V((0, 0, -.9)), 135, (h - V(P)).length), (52, P, h + V((0, 0, -.35)), 190, (h - V(P)).length),
                 (60, P, h + V((0, 0, .16)), 520, (h - V(P)).length), (nf, P, h + V((0, 0, .2)), 560, (h - V(P)).length)],
             1, nf, shake=.006, rshake=.05, seed=406)
    kick(c, [66, 67, 69], 1.2)
    c.data.dof.aperture_fstop = 4.0; sc.view_settings.exposure = -.1
    return 1, nf

exec(open(os.path.join(HERE, 'v8bridge.py')).read())   # v8: teaser Stalker helpers
