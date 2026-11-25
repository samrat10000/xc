"""v2 fix for the shop-window flicker (Sam: 'mirror behind grandma stutters', 'mirror should be totally reflective').
1. The holdout glass sat on the exact plane of the shop body's front face (y = WY): EEVEE z-fought, so the window
   switched between reflection and plaster frame to frame. Glass now 12 mm in front of the wall.
2. The reflection test used 4 projected corners and switched off as soon as one corner went behind the lens, while the
   glass still filled the frame (08 f17-25). Now the quad is clipped at the near plane before projecting.
Run: python -I patch_glass_v2.py  (idempotent; refuses if a target text is missing)"""
import ast
from pathlib import Path

EP = Path(__file__).resolve().parents[3] / 'shots'
HELPER = '''

def glass_proj(near=0.05):
    """the shop-window quad clipped at the camera's near plane, projected to (u, v); returns (poly, visible)"""
    pts = [ROAD.matrix_world @ c for c in GLASS_CORNERS]
    zs = [world_to_camera_view(sc, cam, p_).z for p_ in pts]
    out_ = []
    for i_ in range(4):
        a_, b_, za, zb = pts[i_], pts[(i_ + 1) % 4], zs[i_], zs[(i_ + 1) % 4]
        if za > near: out_.append(a_)
        if (za > near) != (zb > near): out_.append(a_ + (b_ - a_) * ((za - near) / (za - zb)))
    poly = [proj(p_)[:2] for p_ in out_]
    vis_ = len(poly) >= 3 and max(u_ for u_, v_ in poly) > 0 and min(u_ for u_, v_ in poly) < 1 \\
        and max(v_ for u_, v_ in poly) > 0 and min(v_ for u_, v_ in poly) < 1
    return poly, vis_
'''
PROJ = "def proj(pw):\n    v = world_to_camera_view(sc, cam, pw); return (v.x, 1 - v.y, v.z)\n"
OLD_GLASS = "vs = [bm.verts.new(v) for v in ((GL0, WY, GZ0), (GL1, WY, GZ0), (GL1, WY, GZ1), (GL0, WY, GZ1))]"
NEW_GLASS = "vs = [bm.verts.new(v) for v in ((GL0, WY - 0.012, GZ0), (GL1, WY - 0.012, GZ0), (GL1, WY - 0.012, GZ1), (GL0, WY - 0.012, GZ1))]"
OLD_CORN = "GLASS_CORNERS = [Vector((GL0, WY, GZ0)), Vector((GL1, WY, GZ0)), Vector((GL1, WY, GZ1)), Vector((GL0, WY, GZ1))]"
NEW_CORN = OLD_CORN.replace('WY,', 'WY - 0.012,')
VIS = ("    gc = [proj(ROAD.matrix_world @ c) for c in GLASS_CORNERS]\n"
       "    vis = all(z_ > 0 for u_, v_, z_ in gc) and (any(0 <= u_ <= 1 and 0 <= v_ <= 1 for u_, v_, z_ in gc) or (min(u_ for u_, v_, z_ in gc) < 0 < max(u_ for u_, v_, z_ in gc)))\n")
NEWVIS = "    gpoly, vis = glass_proj()\n"
META_OLD = "glass=[(u_, v_) for u_, v_, z_ in gc]"
META_NEW = "glass=gpoly"

jobs = {EP / '04_ride/src/build_s04.py': [(PROJ, PROJ + HELPER, 'glass_proj('), (OLD_GLASS, NEW_GLASS, NEW_GLASS), (OLD_CORN, NEW_CORN, NEW_CORN)]}
for s in ('05_ritual/src/build_s05.py', '08_frozen/src/build_s08.py', '10_eyes/src/build_s10.py', '16_welcome/src/build_s16.py'):
    jobs[EP / s] = [(VIS, NEWVIS, NEWVIS), (META_OLD, META_NEW, META_NEW)]
for p, reps in jobs.items():
    t = p.read_text(encoding='utf-8')
    for old, new, done in reps:
        if done in t and old not in t: continue                               # already patched
        if t.count(old) != 1: raise SystemExit(f'MISSING/AMBIGUOUS in {p.name}: {old[:60]!r} x{t.count(old)}')
        t = t.replace(old, new)
    ast.parse(t); p.write_text(t, encoding='utf-8'); print('ok', p.name)
