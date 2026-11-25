src=open('survivor.py').read()
def rep(a,b,n=1):
    global src
    assert src.count(a)==n,(a,src.count(a)); src=src.replace(a,b)
rep("""             jacket=('denim', '#3a4a6a'), tee='#141416', pants=('canvas', '#1c1c20'), boots='#141210', iris='#2a1a10', weapon='pipe'),
}[CH]""","""             jacket=('denim', '#3a4a6a'), tee='#141416', pants=('canvas', '#1c1c20'), boots='#141210', iris='#2a1a10', weapon='pipe'),
 'rider': dict(mix={'universal-female-young-averagemuscle-averageweight': 1.0}, skin='#e2bc9c', hair='#ebe6dc', hstyle='bob',
             jacket=('leather', '#9a6236'), tee='#1c1a1a', pants=('leather', '#121214'), boots='#8a5a30', iris='#5a6e80', weapon='pistol'),
}[CH]
RIDER = CH == 'rider'""")
rep("def jk_keep(p): return .86 < p.z","def jk_keep(p): return (1.02 if RIDER else .86) < p.z")
rep("def pants_keep(p): return .1 < p.z < 1.0","def pants_keep(p): return (.70 if RIDER else .1) < p.z < 1.0")
rep("collar = L.tube(f'{CH} collar', col_pts, .009, C, sides=8)","collar = L.tube(f'{CH} collar', col_pts, .02 if RIDER else .009, C, sides=8)")
rep("L_ = {'short': (.035, .06), 'buzz': (.008, .014), 'long': (.25, .42), 'bob': (.12, .17)}[hs]",
    "L_ = {'short': (.035, .06), 'buzz': (.008, .014), 'long': (.25, .42), 'bob': (.07, .19) if RIDER else (.12, .17)}[hs]")
rep("M.C(LOOK['hair']), M.C('#000000'))","M.C(LOOK['hair']), M.C('#8a857c' if RIDER else '#000000'))")
# extra gear block, inserted before the weapon section
GEAR = r'''
extra = []
if RIDER:
    # torn dark tights under the shorts
    def holes(c): return noise.noise(c * 14 + V(3, 1, 2)) > .38 and .2 < c.z < .7
    tights = z.garment('tights', LEGS, keep=lambda p: .1 < p.z < .74, push=.002, thick=.0015, tear=holes)
    # tall boot shafts with a turned cuff
    shafts = z.garment('bootshaft', both('lowerleg01', 'lowerleg02', 'foot'), keep=lambda p: .1 < p.z < .47, push=.012,
                       fold=lambda p: .003 * math.sin(p.z * 90 + 5 * noise.noise(p * 9)) + .006 * L.sm(.42, .47, p.z), thick=.004)
    # gloves, wrist down
    WX = abs(z.j('wrist.L____head').x) - .035
    allb = [vg.name for vg in b.vertex_groups]
    gloves = z.garment('gloves', allb, keep=lambda p: abs(p.x) > WX and p.z > .6, push=.0035, thick=.002)
    # duct-taped knee pad on the left knee
    kn = z.j('lowerleg01.L____head'); hk, nk_ = z.hit(b, kn + V(0, -.4, 0), (0, 1, 0))
    kp = L.blob(f'{CH} kneepad', (hk or kn) + V(0, -.012, 0), (.055, .025, .065), C); z.bind(kp, 'lowerleg01.L')
    tape = L.box(f'{CH} tape', (hk or kn) + V(0, -.035, .01), (.06, .004, .012), C, rot=(0, .25, 0)); z.bind(tape, 'lowerleg01.L')
    # goggles pushed up on the forehead + strap
    gz = EL.z + .058; lenses = []
    for e in (EL, ER):
        h, n = z.hit(b, (e.x * 1.05, -.5, gz), (0, 1, 0))
        if h is None: continue
        rim = L.tube(f'{CH} goggle rim', [h + V(0, .002, 0), h + V(0, -.024, 0)], .023, C, sides=18)
        gl = L.blob(f'{CH} goggle glass', h + V(0, -.026, 0), (.02, .006, .02), C)
        lenses += [rim]; extra.append(gl)
    hc2 = V(HC.x, HC.y + .012, gz)
    ring = []
    for i in range(33):
        a = i / 32 * 2 * math.pi
        h, n = z.hit(b, hc2 + V(math.cos(a) * .35, math.sin(a) * .35, 0), (-math.cos(a), -math.sin(a), 0))
        if h is not None: ring.append(h + V(math.cos(a), math.sin(a), 0) * .02)
    strap = L.tube(f'{CH} goggle strap', ring, .006, C, sides=6)
    goggles = L.join(lenses + [strap], f'{CH} goggles'); z.bind(goggles, 'head')
    glass = L.join(extra, f'{CH} goggle lenses'); z.bind(glass, 'head'); extra = []
    # headset: ear cups + band over the crown
    cups = []
    ey = EL.y + .085
    for sx in (1, -1):
        h, n = z.hit(b, (sx * .4, ey, EL.z - .025), (-sx, 0, 0))
        h = h or V(sx * .075, ey, EL.z - .025)
        cups.append(L.tube(f'{CH} cup', [h + V(sx * .004, 0, 0), h + V(sx * .03, 0, 0)], [.034, .03], C, sides=20))
        cups.append(L.blob(f'{CH} cupcap', h + V(sx * .03, 0, 0), (.006, .026, .026), C))
    band = []
    for i in range(17):
        a = math.pi * i / 16
        dv = V(math.cos(a), 0, math.sin(a))
        h, n = z.hit(b, V(0, ey, EL.z - .02) + dv * .4, -dv)
        if h is not None: band.append(h + dv * .03)
    cups.append(L.tube(f'{CH} band', band, .007, C, sides=8))
    mic = L.tube(f'{CH} mic', [cups[0].location if False else V(.1, ey - .01, EL.z - .04), V(.07, EL.y - .07, EL.z - .085)], .003, C, sides=6)
    headset = L.join(cups + [mic], f'{CH} headset'); z.bind(headset, 'head')
    # bandolier with brass rounds, left shoulder to right hip
    s0 = z.j('shoulder01.L____head'); s1 = z.j('upperleg01.R____head')
    pts = []
    for i in range(15):
        t = i / 14; q = s0.lerp(s1, t) + V(-.02 * t, 0, .03 * (1 - t))
        h, n = z.hit(b, (q.x, -.6, q.z), (0, 1, 0))
        if h is not None: pts.append(h + V(0, -.032, 0))
    bando = L.tube(f'{CH} bandolier', pts, .011, C, sides=6); z.bind(bando, 'spine03')
    shells = []
    for i in range(1, len(pts) - 1, 1):
        d = (pts[i + 1] - pts[i - 1]).normalized()
        shells.append(L.tube(f'{CH} shell', [pts[i] + V(0, -.006, 0) - d.cross(V(0, 1, 0)) * .016, pts[i] + V(0, -.006, 0) + d.cross(V(0, 1, 0)) * .016], .0055, C, sides=8))
    shells = L.join(shells, f'{CH} shells'); z.bind(shells, 'spine03')
    # thigh holster
    th = z.j('upperleg02.R____head')
    h, n = z.hit(b, th + V(-.4, 0, .05), (1, 0, 0))
    hol = L.box(f'{CH} holster', (h or th) + V(-.022, 0, 0), (.02, .055, .1), C, bevel=.006); z.bind(hol, 'upperleg02.R')
    hstrap = L.tube(f'{CH} holster strap', [(h or th) + V(-.03, -.06, .06), (h or th) + V(-.03, .06, .06)], .006, C); z.bind(hstrap, 'upperleg02.R')
'''
rep("# weapon in the right hand\n", GEAR + "# weapon in the right hand\n")
rep("""else:
    weapon = L.tube(f'{CH} weapon', [grip + V(0, 0, .12), grip - V(0, 0, .6)], .015, C, sides=10)""",
"""elif wp == 'pistol':
    slide = L.box(f'{CH} slide', grip - V(0, .05, .045), (.016, .1, .022), C, bevel=.003)
    gp = L.box(f'{CH} grip', grip, (.015, .028, .06), C, rot=(.25, 0, 0), bevel=.004)
    weapon = L.join([slide, gp], f'{CH} weapon'); wmat = M.metal(f'{CH}_Gun', col='#2a2a2c', rust='#4a3a2a')
else:
    weapon = L.tube(f'{CH} weapon', [grip + V(0, 0, .12), grip - V(0, 0, .6)], .015, C, sides=10)""")
MATS = r'''
if RIDER:
    L.setmat(tights, M.canvas(f'{CH}_Tights', '#1e1c1e')); L.setmat(shafts, M.leather(f'{CH}_BootShaft', LOOK['boots']))
    L.setmat(gloves, M.leather(f'{CH}_Gloves', '#1a1614')); L.setmat(kp, M.rubber(f'{CH}_Pad', col='#2a2826'))
    L.setmat(tape, M.canvas(f'{CH}_Tape', '#8a8a86')); L.setmat(goggles, M.leather(f'{CH}_GoggleRim', '#3a2a1e'))
    L.setmat(glass, M.flat(f'{CH}_Lens', '#c76a1e', .05)); L.setmat(headset, M.rubber(f'{CH}_Headset', col='#2c2c2e', tread=False))
    L.setmat(bando, M.leather(f'{CH}_Bando', '#3a2a1e')); L.setmat(shells, M.metal(f'{CH}_Brass', col='#b08a3a', rust='#5a4220'))
    L.setmat(hol, M.leather(f'{CH}_Holster', '#2a1e16')); L.setmat(hstrap, M.leather(f'{CH}_Hstrap', '#2a1e16'))
    L.setmat(collar, M.canvas(f'{CH}_Bandana', '#7a221c'))
'''
rep("for k in ('eyeL', 'eyeR'):\n    o = z.parts[k]; z.subdiv(o, 2)", MATS + "for k in ('eyeL', 'eyeR'):\n    o = z.parts[k]; z.subdiv(o, 2)")
rep("for o in [b, tee, jacket, pants, belt, collar, weapon, cap] + [s for sh in shoes for s in sh[:2]]:",
    "for o in [b, tee, jacket, pants, belt, collar, weapon, cap] + [s for sh in shoes for s in sh[:2]] + ([shafts, gloves, kp, goggles, headset, bando, hol] if RIDER else []):")
open('rider.py','w').write(src)
