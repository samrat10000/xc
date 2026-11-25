# twin heavy machine guns on the front fork ends (exec'd from build_a; uses its globals)
M_GUN = pbr('Gun steel parkerized', '#2b2d2c', .45, .8)
M_BRASS = pbr('Cartridge brass', '#b08a3e', .3, 1)
M_TIP = pbr('Bullet copper tip', '#8a4a2a', .35, 1)
M_CANOD = pbr('Ammo can olive drab', '#4d5233', .6, .2)
GN = grp('13 • Twin fork-mounted heavy guns')
Xq = Matrix.Rotation(math.pi / 2, 4, 'Y')
def bar(bm, p0, p1, r, segs=16):
    p0, p1 = V(p0), V(p1); cyl(bm, (p0 + p1) / 2, p1 - p0, r, (p1 - p0).length, segs)
def gun(side):
    p, nrm, nm = hit((FX + .15, .76 * side, 4), (0, 0, -1)); print('gun base', p, nm, flush=True)
    if p is None: return
    g = bmesh.new(); bl = bmesh.new(); can = bmesh.new(); amm = bmesh.new(); tips = bmesh.new()
    b0 = p.copy()
    # pintle: bolted base plate, post, cradle yoke
    box(g, b0 + V((0, 0, .015)), (.30, .22, .03), bev=.008)
    for dx in (-.11, .11):
        for dy in (-.075, .075): hexbolt(g, b0 + V((dx, dy, .03)), (0, 0, 1), .014, .012)
    bar(g, b0 + V((0, 0, .03)), b0 + V((0, 0, .22)), .045, 20)
    cyl(g, b0 + V((0, 0, .2)), (0, 0, 1), .07, .04, 20)
    zc = b0.z + .36; c = V((b0.x, b0.y, zc))
    for s in (-1, 1):  # yoke arms + trunnion pins
        box(g, V((b0.x, b0.y + s * .14, b0.z + .28)), (.1, .025, .2), bev=.006)
        cyl(g, V((b0.x, b0.y + s * .158, zc)), (0, 1, 0), .028, .02, 14)
    box(g, V((b0.x, b0.y, b0.z + .2)), (.1, .3, .03), bev=.006)
    # receiver
    rx0, rx1 = b0.x + .42, b0.x - .30
    box(g, V(((rx0 + rx1) / 2, b0.y, zc)), (rx0 - rx1, .2, .22), bev=.012)
    box(g, V(((rx0 + rx1) / 2 + .03, b0.y, zc + .125)), (rx0 - rx1 - .1, .17, .04), bev=.01)          # top cover
    cyl(g, V((rx1 + .06, b0.y, zc + .125)), (0, 1, 0), .02, .19, 12)                                  # cover hinge
    for i in range(9):  # side plate rivets
        x = rx1 + .05 + i * (rx0 - rx1 - .1) / 8
        for s in (-1, 1):
            for dz in (-.07, .07): cyl(g, V((x, b0.y + s * .101, zc + dz)), (0, 1, 0), .008, .006, 8)
    bar(g, V((rx0, b0.y, zc)), V((rx0 + .1, b0.y, zc)), .06, 20)                                       # back buffer
    for s in (-1, 1): bar(g, V((rx0 + .1, b0.y + s * .07, zc - .02)), V((rx0 + .2, b0.y + s * .07, zc - .07)), .02, 10)   # spade grips
    bar(g, V((rx0 + .2, b0.y - .09, zc - .07)), V((rx0 + .2, b0.y + .09, zc - .07)), .028, 12)
    bar(g, V((b0.x + .1, b0.y - side * .1, zc + .02)), V((b0.x + .1, b0.y - side * .2, zc + .02)), .015, 10)  # charging handle (inboard)
    box(g, V((b0.x + .1, b0.y - side * .21, zc + .02)), (.08, .03, .04), bev=.008)
    # barrel group
    bx = rx1
    cyl(g, V((bx - .06, b0.y, zc + .01)), (1, 0, 0), .07, .12, 24)                                    # trunnion block
    bar(g, V((bx - .12, b0.y, zc + .01)), V((bx - 1.35, b0.y, zc + .01)), .036, 20)                   # barrel
    for i in range(14):                                                                                # cooling rings
        x = bx - .17 - i * .04; cyl(g, V((x, b0.y, zc + .01)), (1, 0, 0), .05, .016, 20)
    # perforated jacket: ribs + holes look via spaced bars
    for k in range(10):
        a = 2 * math.pi * k / 10; o = V((0, math.cos(a) * .062, math.sin(a) * .062))
        bar(g, V((bx - .14, b0.y, zc + .01)) + o, V((bx - .72, b0.y, zc + .01)) + o, .011, 6)
    for x in (bx - .14, bx - .43, bx - .72): cyl(g, V((x, b0.y, zc + .01)), (1, 0, 0), .075, .03, 24)
    mx = bx - 1.35
    cyl(g, V((mx - .07, b0.y, zc + .01)), (1, 0, 0), .058, .14, 20)                                   # muzzle brake
    for x in (mx - .03, mx - .075, mx - .12): cyl(bl, V((x, b0.y, zc + .01)), (1, 0, 0), .061, .02, 20)  # dark ports
    cyl(bl, V((mx - .141, b0.y, zc + .01)), (1, 0, 0), .028, .004, 16)                                 # bore
    box(g, V((bx - .9, b0.y, zc + .07)), (.03, .02, .07), bev=.004)                                    # front sight
    box(g, V((rx1 + .12, b0.y, zc + .165)), (.05, .05, .05), bev=.006)                                 # rear sight
    # ammo can on the outboard side + feed chute
    cc = V((b0.x + .04, b0.y + side * .34, zc - .05))
    box(can, cc, (.32, .16, .26), bev=.012)
    box(can, cc + V((0, 0, .14)), (.33, .17, .025), bev=.006)
    bar(can, cc + V((-.08, 0, .16)), cc + V((.08, 0, .16)), .01, 8)
    for x in (-.13, .13): box(g, V((cc.x + x, b0.y + side * .2, zc - .12)), (.03, .16, .02), bev=.004)  # can bracket
    # belt: cartridges along an arc from can top into the feed tray
    path = [cc + V((0, -side * .02, .16)), cc + V((0, -side * .1, .23)), V((b0.x + .04, b0.y + side * .14, zc + .1)), V((b0.x + .04, b0.y + side * .1, zc + .06))]
    pts = []
    for i in range(len(path) - 1):
        for t in np.linspace(0, 1, 6, endpoint=False): pts.append(path[i].lerp(path[i + 1], t))
    pts.append(path[-1])
    for q in pts:
        cs = q + V((.09, 0, 0)); ce = q + V((-.07, 0, 0))
        bar(amm, cs, ce, .013, 8); cyl(tips, ce + V((-.03, 0, 0)), (1, 0, 0), .011, .06, 8, r2=.002)
        box(g, q + V((.03, 0, 0)), (.03, .03, .03), bev=0)                                             # link
    # firing cable back to the cockpit
    tube(bl, [V((rx0 + .05, b0.y - side * .08, zc - .1)), V((rx0 + .2, b0.y - side * .2, zc - .25)), V((rx0 + .6, b0.y - side * .3, b0.z + .05)), V((-.6, .3 * side, 1.3))], .014, 6)
    obj(f"{'Left' if side < 0 else 'Right'} heavy machine gun", g, M_GUN, GN, sharp=30)
    obj(f"{'Left' if side < 0 else 'Right'} gun ports and cable", bl, M_BLK, GN, sharp=30)
    obj(f"{'Left' if side < 0 else 'Right'} ammo can", can, M_CANOD, GN, sharp=30)
    obj(f"{'Left' if side < 0 else 'Right'} belt cartridges", amm, M_BRASS, GN, sharp=0)
    obj(f"{'Left' if side < 0 else 'Right'} belt bullet tips", tips, M_TIP, GN, sharp=0)
for sd in (-1, 1): gun(sd)
print('guns done', flush=True)
